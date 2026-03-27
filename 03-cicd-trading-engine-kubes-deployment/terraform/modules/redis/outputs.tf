# modules/redis/outputs.tf
output "redis_endpoint" {
  value     = aws_elasticache_cluster.main.cache_nodes[0].address
  sensitive = true
}

output "redis_port" {
  value = aws_elasticache_cluster.main.port
}
