# modules/rds/variables.tf
variable "project_name"               { type = string }
variable "environment"                { type = string }
variable "vpc_id"                     { type = string }
variable "private_subnet_ids"         { type = list(string) }
variable "eks_node_security_group_id" { type = string }
variable "rds_instance_class"         { type = string }
variable "rds_engine_version"         { type = string }
variable "rds_allocated_storage"      { type = number }
variable "rds_max_allocated_storage"  { type = number }
variable "rds_multi_az"               { type = bool }
variable "rds_skip_final_snapshot"    { type = bool }
variable "rds_deletion_protection"    { type = bool }
variable "rds_backup_retention_days"  { type = number }
variable "rds_db_name"                { type = string }

variable "rds_username" { 
  type      = string  
  sensitive = true 
}

variable "rds_password" { 
  type      = string
  sensitive = true
}
