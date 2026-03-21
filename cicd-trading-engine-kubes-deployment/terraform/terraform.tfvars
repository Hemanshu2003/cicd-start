# ─────────────────────────────────────────────────────────────────
# terraform.tfvars — Sandbox-Optimised Resource Sizes
# Designed for Pluralsight AWS acloud sandbox (minimal spend)
# ─────────────────────────────────────────────────────────────────

# ── General ──────────────────────────────────────────────────────
aws_region   = "us-east-1" # acloud sandboxes default to us-east-1
project_name = "trading-engine"
environment  = "sandbox"

# ── Networking ───────────────────────────────────────────────────
# Single NAT Gateway saves ~$32/month vs one per AZ
vpc_cidr           = "10.0.0.0/16"
availability_zones = ["us-east-1a", "us-east-1b"] # 2 AZs is enough for sandbox
single_nat_gateway = true                         # ← Cost saver: 1 NAT GW only

# ── EKS Cluster ──────────────────────────────────────────────────
eks_cluster_name    = "trading-engine-sandbox"
eks_cluster_version = "1.31"

# SANDBOX NODE GROUP — absolute minimum
# t3.medium: 2 vCPU / 4 GB RAM  ← smallest that runs EKS system pods + app
# 1 node: fits api-gateway (1 pod) + celery-worker (1 pod) comfortably
node_group_instance_type = "t3.medium"
node_group_min_size      = 1
node_group_max_size      = 2 # Allow scale-out during testing only
node_group_desired_size  = 1 # Default: stay at 1 node to save cost

# ── RDS PostgreSQL ────────────────────────────────────────────────
# db.t3.micro = smallest available, ~$13/month
# single-AZ + no Multi-AZ = sandbox appropriate
rds_instance_class        = "db.t3.micro"
rds_engine_version        = "15"
rds_allocated_storage     = 20    # GB — minimum
rds_max_allocated_storage = 50    # GB — autoscaling cap
rds_multi_az              = false # ← Cost saver: no standby replica
rds_skip_final_snapshot   = true  # ← Sandbox: skip final snapshot on destroy
rds_deletion_protection   = false # ← Sandbox: allow easy teardown
rds_backup_retention_days = 1     # Minimum — 0 disables backups entirely

rds_db_name = "trading_signals"


# ── ElastiCache Redis ─────────────────────────────────────────────
# cache.t3.micro = smallest Redis node, ~$12/month
# single node (no cluster mode, no replica) for sandbox
redis_node_type            = "cache.t3.micro"
redis_num_cache_nodes      = 1 # ← Cost saver: single node, no replica
redis_engine_version       = "7.0"
redis_parameter_group_name = "default.redis7"

# ── Application ───────────────────────────────────────────────────
# Minimal replica counts for sandbox
api_gateway_replicas   = 1
celery_worker_replicas = 1

# Resource requests (guarantee) vs limits (cap) for K8s pods
api_gateway_cpu_request    = "100m"
api_gateway_cpu_limit      = "500m"
api_gateway_memory_request = "128Mi"
api_gateway_memory_limit   = "512Mi"

celery_worker_cpu_request    = "200m"
celery_worker_cpu_limit      = "800m"
celery_worker_memory_request = "256Mi"
celery_worker_memory_limit   = "1Gi"

# ── Tags (applied to all resources) ──────────────────────────────
common_tags = {
  Project     = "trading-engine"
  Environment = "sandbox"
  ManagedBy   = "terraform"
  Owner       = "your-name" # ← update this
  CostCenter  = "pluralsight-sandbox"
}
