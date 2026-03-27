# modules/rds/outputs.tf
output "rds_endpoint" {
  value     = aws_db_instance.main.endpoint
  sensitive = true
}

output "rds_port" {
  value = aws_db_instance.main.port
}
