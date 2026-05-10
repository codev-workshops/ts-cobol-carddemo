################################################################################
# Outputs
################################################################################

output "vpc_id" {
  description = "VPC identifier"
  value       = aws_vpc.main.id
}

output "private_subnet_ids" {
  description = "Private subnet identifiers"
  value       = aws_subnet.private[*].id
}

output "m2_environment_id" {
  description = "AWS M2 environment identifier"
  value       = aws_m2_environment.carddemo.id
}

output "aurora_cluster_endpoint" {
  description = "Aurora PostgreSQL cluster writer endpoint"
  value       = aws_rds_cluster.aurora.endpoint
}

output "aurora_cluster_reader_endpoint" {
  description = "Aurora PostgreSQL cluster reader endpoint"
  value       = aws_rds_cluster.aurora.reader_endpoint
}

output "aurora_database_name" {
  description = "Aurora database name"
  value       = aws_rds_cluster.aurora.database_name
}

output "aurora_secret_arn" {
  description = "ARN of the Secrets Manager secret holding DB credentials"
  value       = aws_rds_cluster.aurora.master_user_secret[0].secret_arn
}

output "s3_migration_bucket" {
  description = "S3 bucket for migration data"
  value       = aws_s3_bucket.migration_data.id
}

output "m2_execution_role_arn" {
  description = "IAM role ARN for M2 execution"
  value       = aws_iam_role.m2_execution.arn
}

output "codebuild_role_arn" {
  description = "IAM role ARN for CodeBuild"
  value       = aws_iam_role.codebuild.arn
}
