variable "name" {
  type        = string
  description = "Base name for network resources."
}

variable "cidr_block" {
  type        = string
  description = "VPC CIDR block."
}

variable "public_subnet_count" {
  type        = number
  description = "Number of public subnets."
  default     = 2
}

variable "private_subnet_count" {
  type        = number
  description = "Number of private subnets."
  default     = 2
}

variable "enable_nat" {
  type        = bool
  description = "Enable a NAT gateway for private subnets."
  default     = true
}
