variable "region" {
  type        = string
  description = "AWS region."
}

variable "vpc_cidr" {
  type        = string
  description = "VPC CIDR."
}

variable "app_port" {
  type        = number
  description = "Application port."
  default     = 8080
}

variable "db_port" {
  type        = number
  description = "Database port."
  default     = 5432
}

variable "desired_count" {
  type        = number
  description = "Desired ECS task count."
  default     = 2
}

variable "domain_name" {
  type        = string
  description = "Domain name for TLS."
}

variable "enable_nat" {
  type        = bool
  description = "Enable NAT gateway."
  default     = true
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
