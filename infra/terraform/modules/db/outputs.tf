output "db_instance_id" {
  value       = aws_db_instance.db.id
  description = "RDS instance ID."
}

output "db_instance_endpoint" {
  value       = aws_db_instance.db.address
  description = "RDS endpoint address."
}

output "db_secret_arn" {
  value       = aws_secretsmanager_secret.db.arn
  description = "Secrets Manager ARN containing DB credentials."
}
