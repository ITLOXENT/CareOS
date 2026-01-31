variable "name" {
  type        = string
  description = "Base name for compute resources."
}

variable "vpc_id" {
  type        = string
  description = "VPC ID."
}

variable "public_subnet_ids" {
  type        = list(string)
  description = "Public subnet IDs for the ALB."
}

variable "private_subnet_ids" {
  type        = list(string)
  description = "Private subnet IDs for ECS tasks."
}

variable "alb_security_group_id" {
  type        = string
  description = "Security group ID for ALB."
}

variable "ecs_security_group_id" {
  type        = string
  description = "Security group ID for ECS tasks."
}

variable "app_port" {
  type        = number
  description = "Application port."
  default     = 8080
}

variable "desired_count" {
  type        = number
  description = "Desired task count."
  default     = 0
}

variable "domain_name" {
  type        = string
  description = "Domain name for TLS certificate."
  default     = "example.com"
}

variable "container_image" {
  type        = string
  description = "Container image for the service."
  default     = "public.ecr.aws/nginx/nginx:stable"
}
