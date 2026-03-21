# ─────────────────────────────────────────────────────────────────
# outputs.tf — Root module outputs
# ─────────────────────────────────────────────────────────────────

output "eks_cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  description = "EKS cluster API endpoint"
  value       = module.eks.cluster_endpoint
  sensitive   = true
}

output "ecr_repository_url" {
  description = "ECR repository URL for Docker images"
  value       = aws_ecr_repository.trading_engine.repository_url
}

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint (host:port)"
  value       = module.rds.rds_endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "ElastiCache Redis primary endpoint"
  value       = module.redis.redis_endpoint
  sensitive   = true
}

output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "kubeconfig_command" {
  description = "Run this to configure kubectl locally"
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${module.eks.cluster_name}"
}
