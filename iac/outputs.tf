output "ecr_repository_urls" {
  description = "Repository URLs keyed by repository name"
  value       = { for name, repo in aws_ecr_repository.repos : name => repo.repository_url }
}

output "ecr_repository_arns" {
  description = "Repository ARNs keyed by repository name"
  value       = { for name, repo in aws_ecr_repository.repos : name => repo.arn }
}
