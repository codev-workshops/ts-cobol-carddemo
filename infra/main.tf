################################################################################
# CardDemo Phase 0 – AWS Mainframe Modernization Infrastructure
#
# Assumed defaults:
#   Runtime engine : Micro Focus (replatform)
#   Database       : Aurora PostgreSQL
#   VSAM           : Native M2 VSAM (Aurora for reporting)
################################################################################

terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "CardDemo"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

################################################################################
# Data Sources
################################################################################

data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

################################################################################
# VPC – 2 AZs, public + private subnets, NAT gateway
################################################################################

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = { Name = "${var.project_name}-vpc" }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "${var.project_name}-igw" }
}

resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 4, count.index)
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = { Name = "${var.project_name}-public-${count.index}" }
}

resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 4, count.index + 2)
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = { Name = "${var.project_name}-private-${count.index}" }
}

resource "aws_eip" "nat" {
  domain = "vpc"
  tags   = { Name = "${var.project_name}-nat-eip" }
}

resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id

  tags = { Name = "${var.project_name}-nat" }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "${var.project_name}-public-rt" }
}

resource "aws_route" "public_internet" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.main.id
}

resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "${var.project_name}-private-rt" }
}

resource "aws_route" "private_nat" {
  route_table_id         = aws_route_table.private.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.main.id
}

resource "aws_route_table_association" "private" {
  count          = 2
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

################################################################################
# Security Groups
################################################################################

resource "aws_security_group" "m2_runtime" {
  name_prefix = "${var.project_name}-m2-"
  description = "Security group for AWS M2 Micro Focus runtime"
  vpc_id      = aws_vpc.main.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${var.project_name}-m2-sg" }
}

resource "aws_security_group" "aurora" {
  name_prefix = "${var.project_name}-aurora-"
  description = "Security group for Aurora PostgreSQL"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "PostgreSQL from M2 runtime"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.m2_runtime.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${var.project_name}-aurora-sg" }
}

################################################################################
# AWS Mainframe Modernization (M2) Environment – Micro Focus
################################################################################

resource "aws_m2_environment" "carddemo" {
  name          = "${var.project_name}-runtime"
  engine_type   = "microfocus"
  instance_type = var.m2_instance_type

  subnet_ids         = aws_subnet.private[*].id
  security_group_ids = [aws_security_group.m2_runtime.id]

  tags = { Name = "${var.project_name}-m2-env" }
}

################################################################################
# Aurora PostgreSQL – Reporting & Modernized Data Store
################################################################################

resource "aws_db_subnet_group" "aurora" {
  name       = "${var.project_name}-aurora-subnets"
  subnet_ids = aws_subnet.private[*].id

  tags = { Name = "${var.project_name}-aurora-subnet-group" }
}

resource "aws_rds_cluster" "aurora" {
  cluster_identifier = "${var.project_name}-aurora"
  engine             = "aurora-postgresql"
  engine_version     = var.aurora_engine_version
  database_name      = "carddemo"

  master_username                 = "carddemo_admin"
  manage_master_user_password     = true
  master_user_secret_kms_key_id   = aws_kms_key.db_secret.id

  db_subnet_group_name   = aws_db_subnet_group.aurora.name
  vpc_security_group_ids = [aws_security_group.aurora.id]

  storage_encrypted = true
  kms_key_id        = aws_kms_key.aurora.arn

  backup_retention_period = 7
  preferred_backup_window = "03:00-04:00"
  skip_final_snapshot     = var.environment != "prod"

  tags = { Name = "${var.project_name}-aurora-cluster" }
}

resource "aws_rds_cluster_instance" "aurora" {
  count              = 2
  identifier         = "${var.project_name}-aurora-${count.index}"
  cluster_identifier = aws_rds_cluster.aurora.id
  instance_class     = var.aurora_instance_class
  engine             = aws_rds_cluster.aurora.engine
  engine_version     = aws_rds_cluster.aurora.engine_version

  tags = { Name = "${var.project_name}-aurora-instance-${count.index}" }
}

################################################################################
# KMS Keys
################################################################################

resource "aws_kms_key" "aurora" {
  description         = "KMS key for Aurora PostgreSQL encryption at rest"
  enable_key_rotation = true

  tags = { Name = "${var.project_name}-aurora-kms" }
}

resource "aws_kms_key" "db_secret" {
  description         = "KMS key for DB credentials secret"
  enable_key_rotation = true

  tags = { Name = "${var.project_name}-db-secret-kms" }
}

################################################################################
# S3 Bucket – Migration Data (GDG replacement + seed data)
################################################################################

resource "aws_s3_bucket" "migration_data" {
  bucket = "${var.project_name}-migration-data-${data.aws_caller_identity.current.account_id}"

  tags = { Name = "${var.project_name}-migration-data" }
}

resource "aws_s3_bucket_versioning" "migration_data" {
  bucket = aws_s3_bucket.migration_data.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "migration_data" {
  bucket = aws_s3_bucket.migration_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "migration_data" {
  bucket = aws_s3_bucket.migration_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

################################################################################
# IAM Roles
################################################################################

# M2 Execution Role
resource "aws_iam_role" "m2_execution" {
  name = "${var.project_name}-m2-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "m2.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })

  tags = { Name = "${var.project_name}-m2-execution-role" }
}

resource "aws_iam_role_policy" "m2_execution" {
  name = "${var.project_name}-m2-execution-policy"
  role = aws_iam_role.m2_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.migration_data.arn,
          "${aws_s3_bucket.migration_data.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = aws_rds_cluster.aurora.master_user_secret[0].secret_arn
      }
    ]
  })
}

# CodeBuild Role
resource "aws_iam_role" "codebuild" {
  name = "${var.project_name}-codebuild-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "codebuild.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })

  tags = { Name = "${var.project_name}-codebuild-role" }
}

resource "aws_iam_role_policy" "codebuild" {
  name = "${var.project_name}-codebuild-policy"
  role = aws_iam_role.codebuild.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:GetBucketLocation"
        ]
        Resource = [
          aws_s3_bucket.migration_data.arn,
          "${aws_s3_bucket.migration_data.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "m2:*"
        ]
        Resource = aws_m2_environment.carddemo.arn
      }
    ]
  })
}

# Developer Role
resource "aws_iam_role" "developer" {
  name = "${var.project_name}-developer-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root" }
      Action    = "sts:AssumeRole"
      Condition = {
        Bool = { "aws:MultiFactorAuthPresent" = "true" }
      }
    }]
  })

  tags = { Name = "${var.project_name}-developer-role" }
}

resource "aws_iam_role_policy" "developer" {
  name = "${var.project_name}-developer-policy"
  role = aws_iam_role.developer.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "m2:Get*",
          "m2:List*",
          "m2:StartApplication",
          "m2:StopApplication"
        ]
        Resource = aws_m2_environment.carddemo.arn
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.migration_data.arn,
          "${aws_s3_bucket.migration_data.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "rds:Describe*",
          "rds-data:ExecuteStatement",
          "rds-data:BatchExecuteStatement"
        ]
        Resource = aws_rds_cluster.aurora.arn
      },
      {
        Effect = "Allow"
        Action = [
          "logs:GetLogEvents",
          "logs:FilterLogEvents",
          "logs:DescribeLogStreams"
        ]
        Resource = "arn:aws:logs:*:*:log-group:/carddemo/*"
      }
    ]
  })
}

################################################################################
# CloudWatch Log Groups
################################################################################

resource "aws_cloudwatch_log_group" "m2_runtime" {
  name              = "/carddemo/m2-runtime"
  retention_in_days = var.log_retention_days

  tags = { Name = "${var.project_name}-m2-runtime-logs" }
}

resource "aws_cloudwatch_log_group" "batch_execution" {
  name              = "/carddemo/batch-execution"
  retention_in_days = var.log_retention_days

  tags = { Name = "${var.project_name}-batch-execution-logs" }
}

resource "aws_cloudwatch_log_group" "aurora_slow_queries" {
  name              = "/carddemo/aurora-slow-queries"
  retention_in_days = var.log_retention_days

  tags = { Name = "${var.project_name}-aurora-slow-query-logs" }
}
