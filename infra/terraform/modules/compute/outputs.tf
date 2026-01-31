output "cluster_name" {
  value       = aws_ecs_cluster.this.name
  description = "ECS cluster name."
}

output "service_name" {
  value       = aws_ecs_service.api.name
  description = "ECS service name."
}

output "alb_arn" {
  value       = aws_lb.api.arn
  description = "ALB ARN."
}

output "acm_certificate_arn" {
  value       = aws_acm_certificate.tls.arn
  description = "ACM certificate ARN."
}
