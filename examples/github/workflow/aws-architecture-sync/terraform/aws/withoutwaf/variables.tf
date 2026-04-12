variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "eu-west-2"
}

variable "app_name" {
  description = "Application name used as a prefix for all resources"
  type        = string
  default     = "dms"
}

variable "environment" {
  description = "Deployment environment (e.g. production, staging)"
  type        = string
  default     = "production"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

# --- Database ---

variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "dms"
}

variable "db_username" {
  description = "PostgreSQL master username"
  type        = string
  default     = "dms"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t4g.micro"
}

variable "db_multi_az" {
  description = "Enable RDS Multi-AZ for high availability"
  type        = bool
  default     = false
}

# --- ECS ---

variable "api_image" {
  description = "Fully-qualified ECR image URI for the API (e.g. 123456789.dkr.ecr.eu-west-2.amazonaws.com/dms-api:latest)"
  type        = string
  default     = ""
}

variable "frontend_image" {
  description = "Fully-qualified ECR image URI for the frontend"
  type        = string
  default     = ""
}

variable "api_cpu" {
  description = "CPU units for the API Fargate task (1 vCPU = 1024)"
  type        = number
  default     = 512
}

variable "api_memory" {
  description = "Memory (MB) for the API Fargate task"
  type        = number
  default     = 1024
}

variable "frontend_cpu" {
  description = "CPU units for the frontend Fargate task"
  type        = number
  default     = 256
}

variable "frontend_memory" {
  description = "Memory (MB) for the frontend Fargate task"
  type        = number
  default     = 512
}
