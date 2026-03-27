# modules/eks/variables.tf
variable "project_name"             { type = string }
variable "environment"              { type = string }
variable "eks_cluster_name"         { type = string }
variable "eks_cluster_version"      { type = string }
variable "vpc_id"                   { type = string }
variable "private_subnet_ids"       { type = list(string) }
variable "node_group_instance_type" { type = string }
variable "node_group_min_size"      { type = number }
variable "node_group_max_size"      { type = number }
variable "node_group_desired_size"  { type = number }
