variable "name" {
  type        = string
  description = "Base name for DB resources."
}

variable "subnet_ids" {
  type        = list(string)
  description = "Private subnet IDs for the DB."
}

variable "vpc_security_group_ids" {
  type        = list(string)
  description = "Security group IDs for the DB."
}

variable "db_username" {
  type        = string
  description = "Database username."
  default     = "careos"
}

variable "db_name" {
  type        = string
  description = "Database name."
  default     = "careos"
}

variable "instance_class" {
  type        = string
  description = "RDS instance class."
  default     = "db.t4g.micro"
}

variable "engine_version" {
  type        = string
  description = "Postgres engine version."
  default     = "16.3"
}
