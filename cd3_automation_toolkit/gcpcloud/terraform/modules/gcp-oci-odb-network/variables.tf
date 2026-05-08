variable "odb_network_project" {
  type    = string
  default = null
}

variable "location" {
  type    = string
  default = null
}

variable "vpc_network_name" {
  type    = string
  default = null
}

variable "odb_network_id" {
  type    = string
  default = null
}

variable "odb_network_gcp_oracle_zone" {
  type    = string
  default = null
}

variable "odb_client_subnet_id" {
  type    = string
  default = null
}

variable "odb_backup_subnet_id" {
  type    = string
  default = null
}

variable "labels" {
  description = "A mapping of tags which should be assigned to the Cloud Exadata Infrastructure."
  type        = map(string)
  default     = null
}

variable "create_odb_network" {
  type    = bool
  default = null
}

variable "create_odb_network_subnets" {
  type    = string
  default = null
}

variable "backup_subnet_cidr" {
  type    = string
  default = null
}

variable "client_subnet_cidr" {
  type    = string
  default = null
}

