# ─────────────────────────────────────────────────────────────────
# modules/redis/main.tf — ElastiCache Redis (Sandbox-Optimised)
# ─────────────────────────────────────────────────────────────────

# ── Subnet Group ─────────────────────────────────────────────────
resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-redis-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = {
    Name = "${var.project_name}-${var.environment}-redis-subnet-group"
  }
}

# ── Security Group ────────────────────────────────────────────────
resource "aws_security_group" "redis" {
  name        = "${var.project_name}-${var.environment}-redis-sg"
  description = "Allow Redis from EKS nodes only"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [var.eks_node_security_group_id]
    description     = "Redis from EKS worker nodes"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-redis-sg"
  }
}

# ── ElastiCache Cluster ───────────────────────────────────────────
resource "aws_elasticache_cluster" "main" {
  cluster_id           = "${var.project_name}-${var.environment}-redis"
  engine               = "redis"
  node_type            = var.redis_node_type
  num_cache_nodes      = var.redis_num_cache_nodes
  engine_version       = var.redis_engine_version
  parameter_group_name = var.redis_parameter_group_name
  port                 = 6379

  subnet_group_name  = aws_elasticache_subnet_group.main.name
  security_group_ids = [aws_security_group.redis.id]

  # Disable automatic failover for sandbox (single node)
  # Automatic backups disabled to save cost
  snapshot_retention_limit = 0

  apply_immediately = true

  tags = {
    Name = "${var.project_name}-${var.environment}-redis"
  }
}
