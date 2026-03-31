resource "random_password" "db" {
  length           = 32
  special          = true
  override_special = "!#&*-_=+:?"
}

resource "aws_db_subnet_group" "main" {
  name       = "${local.name}-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id
}

resource "aws_db_instance" "main" {
  identifier        = "${local.name}-postgres"
  engine            = "postgres"
  engine_version    = "17"
  instance_class    = var.db_instance_class
  allocated_storage = 20
  storage_type      = "gp3"

  db_name  = var.db_name
  username = var.db_username
  password = random_password.db.result

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  multi_az                = var.db_multi_az
  backup_retention_period = 7
  deletion_protection     = false # Set to true for production
  skip_final_snapshot     = true

  tags = { Name = "${local.name}-postgres" }
}

# Store the full connection string in Secrets Manager
resource "aws_secretsmanager_secret" "db_connection_string" {
  name                    = "/${var.app_name}/${var.environment}/db-connection-string"
  recovery_window_in_days = 0 # Allow immediate deletion; increase for production
}

resource "aws_secretsmanager_secret_version" "db_connection_string" {
  secret_id     = aws_secretsmanager_secret.db_connection_string.id
  secret_string = "Host=${aws_db_instance.main.address};Port=5432;Database=${var.db_name};Username=${var.db_username};Password='${random_password.db.result}'"
}
