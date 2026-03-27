# ─────────────────────────────────────────────────────────────────
# modules/rds/main.tf — RDS PostgreSQL (Sandbox-Optimised)
# ─────────────────────────────────────────────────────────────────

# ── Subnet Group ─────────────────────────────────────────────────
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-db-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = {
    Name = "${var.project_name}-${var.environment}-db-subnet-group"
  }
}

# ── Security Group ────────────────────────────────────────────────
resource "aws_security_group" "rds" {
  name        = "${var.project_name}-${var.environment}-rds-sg"
  description = "Allow PostgreSQL from EKS nodes only"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.eks_node_security_group_id]
    description     = "PostgreSQL from EKS nodes"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-rds-sg"
  }
}

# ── Parameter Group ───────────────────────────────────────────────
resource "aws_db_parameter_group" "main" {
  name   = "${var.project_name}-${var.environment}-pg15"
  family = "postgres15"
  
  # Tune for low-memory t3.micro instance
  parameter {
    name  = "shared_buffers"
    value = "32768"   # 32 MB (default is 128 MB — too high for micro)
    apply_method = "pending-reboot"
  }

  parameter {
    name  = "max_connections"
    value = "50"      # Low connection limit for micro
    apply_method = "pending-reboot"
  }

  parameter {
    name  = "log_min_duration_statement"
    value = "1000"    # Log queries > 1s
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-pg-param-group"
  }
}

# ── RDS Instance ──────────────────────────────────────────────────
resource "aws_db_instance" "main" {
  identifier = "${var.project_name}-${var.environment}-db"

  engine         = "postgres"
  engine_version = var.rds_engine_version
  instance_class = var.rds_instance_class

  allocated_storage     = var.rds_allocated_storage
  max_allocated_storage = var.rds_max_allocated_storage
  storage_type          = "gp2"
  storage_encrypted     = true

  db_name  = var.rds_db_name
  username = var.rds_username
  password = var.rds_password

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  parameter_group_name   = aws_db_parameter_group.main.name

  multi_az               = var.rds_multi_az
  publicly_accessible    = false
  skip_final_snapshot    = var.rds_skip_final_snapshot
  deletion_protection    = var.rds_deletion_protection
  backup_retention_period = var.rds_backup_retention_days

  # Performance Insights adds cost — disable for sandbox
  performance_insights_enabled = false

  # Enhanced monitoring adds cost — disable for sandbox
  monitoring_interval = 0

  apply_immediately = true

  tags = {
    Name = "${var.project_name}-${var.environment}-db"
  }
}
