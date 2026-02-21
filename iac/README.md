# Terraform ECR Setup

Creates two Amazon ECR repositories:

- `resto/production`
- `resto/ci`

## Usage

```bash
cd iac
terraform init
terraform fmt
terraform validate
terraform plan
terraform apply
```

Optional overrides:

```bash
terraform plan -var='aws_region=us-west-2' -var='image_tag_mutability=IMMUTABLE'
```
