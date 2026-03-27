# ─────────────────────────────────────────────────────────────────
# Terraform Cloud Backend Configuration
# File: trading-engine/terraform/backend.tf
# ─────────────────────────────────────────────────────────────────
# This tells Terraform to use Terraform Cloud (app.terraform.io)
# as the remote backend — state is stored there, not locally.

terraform {
  cloud {
    organization = "Hemanshu-HCPT" # ← replace with your TFC org

    workspaces {
      name = "trading-engine-sandbox" # ← must match TFC_WORKSPACE secret
    }
  }

  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
  }
}

# ─────────────────────────────────────────────────────────────────
# Variables that the CI/CD pipeline passes to TFC as workspace
# environment variables (set them in TFC UI or via API)
# ─────────────────────────────────────────────────────────────────

variable "aws_region" { type = string }
variable "project_name" { type = string }
variable "environment" { type = string }

variable "vpc_cidr" { type = string }
variable "availability_zones" { type = list(string) }
variable "single_nat_gateway" { type = bool }

variable "eks_cluster_name" { type = string }
variable "eks_cluster_version" { type = string }

variable "node_group_instance_type" { type = string }
variable "node_group_min_size" { type = number }
variable "node_group_max_size" { type = number }
variable "node_group_desired_size" { type = number }

variable "rds_instance_class" { type = string }
variable "rds_engine_version" { type = string }
variable "rds_allocated_storage" { type = number }
variable "rds_max_allocated_storage" { type = number }
variable "rds_multi_az" { type = bool }
variable "rds_skip_final_snapshot" { type = bool }
variable "rds_deletion_protection" { type = bool }
variable "rds_backup_retention_days" { type = number }
variable "rds_db_name" { type = string }

# Sensitive — set as sensitive workspace variables in TFC UI
variable "rds_username" {
  type      = string
  sensitive = true
}
variable "rds_password" {
  type      = string
  sensitive = true
}

variable "redis_node_type" { type = string }
variable "redis_num_cache_nodes" { type = number }
variable "redis_engine_version" { type = string }
variable "redis_parameter_group_name" { type = string }

variable "api_gateway_replicas" { type = number }
variable "celery_worker_replicas" { type = number }

variable "api_gateway_cpu_request" { type = string }
variable "api_gateway_cpu_limit" { type = string }
variable "api_gateway_memory_request" { type = string }
variable "api_gateway_memory_limit" { type = string }

variable "celery_worker_cpu_request" { type = string }
variable "celery_worker_cpu_limit" { type = string }
variable "celery_worker_memory_request" { type = string }
variable "celery_worker_memory_limit" { type = string }

variable "common_tags" { type = map(string) }
