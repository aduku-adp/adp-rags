output "ecr_repository_urls" {
  description = "Repository URLs keyed by repository name"
  value       = { for name, repo in aws_ecr_repository.repos : name => repo.repository_url }
}

output "ecr_repository_arns" {
  description = "Repository ARNs keyed by repository name"
  value       = { for name, repo in aws_ecr_repository.repos : name => repo.arn }
}

output "s3_bucket_name" {
  description = "S3 bucket name for ADP RAG artifacts"
  value       = aws_s3_bucket.adp_rags.bucket
}

output "s3_bucket_arn" {
  description = "S3 bucket ARN for ADP RAG artifacts"
  value       = aws_s3_bucket.adp_rags.arn
}
