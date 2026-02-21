variable "aws_region" {
  description = "AWS region where ECR repositories will be created"
  type        = string
  default     = "eu-central-1"
}

variable "image_tag_mutability" {
  description = "Image tag mutability for ECR repositories"
  type        = string
  default     = "MUTABLE"

  validation {
    condition     = contains(["MUTABLE", "IMMUTABLE"], var.image_tag_mutability)
    error_message = "image_tag_mutability must be MUTABLE or IMMUTABLE."
  }
}
