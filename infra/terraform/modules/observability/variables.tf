variable "name" {
  type        = string
  description = "Base name for observability resources."
}

variable "db_instance_id" {
  type        = string
  description = "RDS instance ID."
}

variable "ecs_cluster_name" {
  type        = string
  description = "ECS cluster name."
}

variable "ecs_service_name" {
  type        = string
  description = "ECS service name."
}
