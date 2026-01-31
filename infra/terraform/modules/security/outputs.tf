output "alb_security_group_id" {
  value       = aws_security_group.alb.id
  description = "ALB security group ID."
}

output "ecs_security_group_id" {
  value       = aws_security_group.ecs.id
  description = "ECS security group ID."
}

output "rds_security_group_id" {
  value       = aws_security_group.rds.id
  description = "RDS security group ID."
}
