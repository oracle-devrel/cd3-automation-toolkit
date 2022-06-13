############################
# Variable Block - Load Balancer
# Create Load Balancer Path Route Set
############################

variable "name" {
  type        = string
  description = "The name of the Rule Set."
  default     = null
}

variable "load_balancer_id" {
  type        = string
  description = "The OCID of load balancer"
  default     = null
}

variable "key_name" {
  type    = string
  default = null
}

variable "path_route_sets" {}