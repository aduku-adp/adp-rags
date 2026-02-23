variable "eks_cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "adp-rags-eks"
}

variable "eks_cluster_version" {
  description = "EKS cluster Kubernetes version"
  type        = string
  default     = "1.31"
}

variable "eks_node_instance_types" {
  description = "EC2 instance types for EKS managed nodes"
  type        = list(string)
  default     = ["t3.xlarge"]
}

variable "eks_node_desired_size" {
  description = "Desired number of EKS managed nodes"
  type        = number
  default     = 2
}

variable "eks_node_min_size" {
  description = "Minimum number of EKS managed nodes"
  type        = number
  default     = 2
}

variable "eks_node_max_size" {
  description = "Maximum number of EKS managed nodes"
  type        = number
  default     = 2
}
