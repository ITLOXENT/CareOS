resource "aws_kms_key" "db" {
  description             = "${var.name} RDS encryption key"
  deletion_window_in_days = 30
  enable_key_rotation     = true
}

resource "aws_kms_alias" "db" {
  name          = "alias/${var.name}-rds"
  target_key_id = aws_kms_key.db.key_id
}

resource "aws_db_subnet_group" "db" {
  name       = "${var.name}-db-subnet-group"
  subnet_ids = var.subnet_ids
}

resource "random_password" "db" {
  length  = 24
  special = true
}

resource "aws_secretsmanager_secret" "db" {
  name                    = "${var.name}/db"
  recovery_window_in_days = 7
  kms_key_id              = aws_kms_key.db.arn
}

resource "aws_secretsmanager_secret_version" "db" {
  secret_id     = aws_secretsmanager_secret.db.id
  secret_string = jsonencode({ username = var.db_username, password = random_password.db.result })
}

resource "aws_db_instance" "db" {
  identifier              = "${var.name}-db"
  engine                  = "postgres"
  engine_version          = var.engine_version
  instance_class          = var.instance_class
  db_name                 = var.db_name
  username                = var.db_username
  password                = random_password.db.result
  allocated_storage       = 20
  storage_encrypted       = true
  kms_key_id              = aws_kms_key.db.arn
  backup_retention_period = 7
  deletion_protection     = true
  skip_final_snapshot     = false
  publicly_accessible     = false
  db_subnet_group_name    = aws_db_subnet_group.db.name
  vpc_security_group_ids  = var.vpc_security_group_ids
  apply_immediately       = true
}
