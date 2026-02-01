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

variable "sentry_dsn" {
  type        = string
  description = "Sentry DSN."
  default     = ""
}

variable "sentry_environment" {
  type        = string
  description = "Sentry environment."
  default     = "prod"
}

variable "sentry_release" {
  type        = string
  description = "Sentry release."
  default     = ""
}

variable "sentry_traces_sample_rate" {
  type        = number
  description = "Sentry traces sample rate."
  default     = 0.1
}

variable "sentry_send_default_pii" {
  type        = bool
  description = "Enable Sentry default PII."
  default     = false
}
