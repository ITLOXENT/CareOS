variable "name" {
  type        = string
  description = "Base name for security resources."
}

variable "vpc_id" {
  type        = string
  description = "VPC ID."
}

variable "app_port" {
  type        = number
  description = "Application port exposed by the service."
  default     = 8080
}

variable "db_port" {
  type        = number
  description = "Database port."
  default     = 5432
}
