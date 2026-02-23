provider "aws" {
  region = var.aws_region
}

locals {
  repositories = toset([
    "resto/production",
    "resto/ci",
  ])
}

resource "aws_ecr_repository" "repos" {
  for_each             = local.repositories
  name                 = each.value
  image_tag_mutability = var.image_tag_mutability

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }
}

resource "aws_s3_bucket" "adp_rags" {
  bucket = "adp-rags"
}
