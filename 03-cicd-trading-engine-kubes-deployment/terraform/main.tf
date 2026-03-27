# ─────────────────────────────────────────────────────────────────
# main.tf — Root module — Trading Engine (Sandbox)
# ─────────────────────────────────────────────────────────────────

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = var.common_tags
  }
}

# ── VPC ──────────────────────────────────────────────────────────
module "vpc" {
  source = "./modules/vpc"

  project_name       = var.project_name
  environment        = var.environment
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
  single_nat_gateway = var.single_nat_gateway
}

# ── EKS ──────────────────────────────────────────────────────────
module "eks" {
  source = "./modules/eks"

  project_name             = var.project_name
  environment              = var.environment
  eks_cluster_name         = var.eks_cluster_name
  eks_cluster_version      = var.eks_cluster_version
  vpc_id                   = module.vpc.vpc_id
  private_subnet_ids       = module.vpc.private_subnet_ids
  node_group_instance_type = var.node_group_instance_type
  node_group_min_size      = var.node_group_min_size
  node_group_max_size      = var.node_group_max_size
  node_group_desired_size  = var.node_group_desired_size
}

# ── RDS PostgreSQL ────────────────────────────────────────────────
module "rds" {
  source = "./modules/rds"

  project_name               = var.project_name
  environment                = var.environment
  vpc_id                     = module.vpc.vpc_id
  private_subnet_ids         = module.vpc.private_subnet_ids
  eks_node_security_group_id = module.eks.node_security_group_id
  rds_instance_class         = var.rds_instance_class
  rds_engine_version         = var.rds_engine_version
  rds_allocated_storage      = var.rds_allocated_storage
  rds_max_allocated_storage  = var.rds_max_allocated_storage
  rds_multi_az               = var.rds_multi_az
  rds_skip_final_snapshot    = var.rds_skip_final_snapshot
  rds_deletion_protection    = var.rds_deletion_protection
  rds_backup_retention_days  = var.rds_backup_retention_days
  rds_db_name                = var.rds_db_name
  rds_username               = var.rds_username
  rds_password               = var.rds_password
}

# ── ElastiCache Redis ─────────────────────────────────────────────
module "redis" {
  source = "./modules/redis"

  project_name               = var.project_name
  environment                = var.environment
  vpc_id                     = module.vpc.vpc_id
  private_subnet_ids         = module.vpc.private_subnet_ids
  eks_node_security_group_id = module.eks.node_security_group_id
  redis_node_type            = var.redis_node_type
  redis_num_cache_nodes      = var.redis_num_cache_nodes
  redis_engine_version       = var.redis_engine_version
  redis_parameter_group_name = var.redis_parameter_group_name
}

# ── ECR Repository ────────────────────────────────────────────────
resource "aws_ecr_repository" "trading_engine" {
  name                 = var.project_name
  image_tag_mutability = "MUTABLE"
  force_delete = true  # <-- deletes ALL images on destroy/repla
  # lifecycle {
  #   prevent_destroy = true
  # } on critical resources like ECR to guard against accidental teardown.
  image_scanning_configuration {
    scan_on_push = true
  }
}

# Lifecycle policy: keep last 10 images, delete older ones
resource "aws_ecr_lifecycle_policy" "trading_engine" {
  repository = aws_ecr_repository.trading_engine.name
  
  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep last 10 images"
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 10
      }
      action = { type = "expire" }
    }]
  })
}

# ── Kubernetes Namespace & ConfigMap ──────────────────────────────
#provider "kubernetes" {
#  host                   = module.eks.cluster_endpoint
#  cluster_ca_certificate = base64decode(module.eks.cluster_ca_certificate)
#  # token                  = module.eks.cluster_token
#}

provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_ca_certificate)
 
  # Use the exec plugin to fetch a fresh token dynamically
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
  }
}

resource "kubernetes_namespace" "trading_engine" {
  metadata {
    name = "trading-engine"
    labels = {
      environment = var.environment
      managed-by  = "terraform"
    }
  }

  depends_on = [module.eks]
}

resource "kubernetes_secret" "app_secrets" {
  metadata {
    name      = "app-secrets"
    namespace = kubernetes_namespace.trading_engine.metadata[0].name
  }

  data = {
    DATABASE_URL = "postgresql://${var.rds_username}:${var.rds_password}@${module.rds.rds_endpoint}/${var.rds_db_name}"
    REDIS_URL    = "redis://${module.redis.redis_endpoint}:6379/0"
  }

  type = "Opaque"
}

resource "kubernetes_config_map" "app_config" {
  metadata {
    name      = "app-config"
    namespace = kubernetes_namespace.trading_engine.metadata[0].name
  }

  data = {
    AWS_REGION         = var.aws_region
    ENVIRONMENT        = var.environment
    LOG_LEVEL          = "INFO"
    CELERY_CONCURRENCY = "2"
  }
}

import {
  to = aws_ecr_repository.trading_engine
  id = "trading-engine"
}
