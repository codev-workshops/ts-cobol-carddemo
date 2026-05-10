################################################################################
# CodePipeline – CardDemo CI/CD
#
# Trigger: push to main → Source (GitHub) → Build (CodeBuild) → Deploy (M2)
################################################################################

################################################################################
# CodeBuild Project
################################################################################

resource "aws_codebuild_project" "carddemo_compile" {
  name         = "${var.project_name}-compile"
  description  = "Compile CardDemo COBOL programs and BMS maps for M2 Micro Focus"
  service_role = var.codebuild_role_arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type    = "BUILD_GENERAL1_MEDIUM"
    image           = "aws/codebuild/amazonlinux2-x86_64-standard:5.0"
    type            = "LINUX_CONTAINER"
    privileged_mode = false

    environment_variable {
      name  = "M2_ENVIRONMENT_ID"
      value = var.m2_environment_id
    }

    environment_variable {
      name  = "S3_ARTIFACT_BUCKET"
      value = var.s3_artifact_bucket
    }
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = "infra/cicd/buildspec.yml"
  }

  tags = {
    Project = var.project_name
  }
}

################################################################################
# CodePipeline
################################################################################

resource "aws_codepipeline" "carddemo" {
  name     = "${var.project_name}-pipeline"
  role_arn = aws_iam_role.pipeline.arn

  artifact_store {
    location = var.s3_artifact_bucket
    type     = "S3"
  }

  # Stage 1: Source
  stage {
    name = "Source"

    action {
      name             = "GitHub_Source"
      category         = "Source"
      owner            = "AWS"
      provider         = "CodeStarSourceConnection"
      version          = "1"
      output_artifacts = ["source_output"]

      configuration = {
        ConnectionArn    = var.codestar_connection_arn
        FullRepositoryId = var.github_repo
        BranchName       = "main"
      }
    }
  }

  # Stage 2: Build (compile COBOL + BMS)
  stage {
    name = "Build"

    action {
      name             = "Compile_COBOL"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      version          = "1"
      input_artifacts  = ["source_output"]
      output_artifacts = ["build_output"]

      configuration = {
        ProjectName = aws_codebuild_project.carddemo_compile.name
      }
    }
  }

  # Stage 3: Deploy to M2
  stage {
    name = "Deploy"

    action {
      name            = "Deploy_to_M2"
      category        = "Deploy"
      owner           = "AWS"
      provider        = "S3"
      version         = "1"
      input_artifacts = ["build_output"]

      configuration = {
        BucketName = var.s3_artifact_bucket
        Extract    = "true"
        ObjectKey  = "deployments/latest"
      }
    }
  }

  tags = {
    Project = var.project_name
  }
}

################################################################################
# Pipeline IAM Role
################################################################################

resource "aws_iam_role" "pipeline" {
  name = "${var.project_name}-pipeline-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "codepipeline.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "pipeline" {
  name = "${var.project_name}-pipeline-policy"
  role = aws_iam_role.pipeline.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:GetBucketVersioning"
        ]
        Resource = [
          "arn:aws:s3:::${var.s3_artifact_bucket}",
          "arn:aws:s3:::${var.s3_artifact_bucket}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "codebuild:StartBuild",
          "codebuild:BatchGetBuilds"
        ]
        Resource = aws_codebuild_project.carddemo_compile.arn
      },
      {
        Effect   = "Allow"
        Action   = ["codestar-connections:UseConnection"]
        Resource = var.codestar_connection_arn
      }
    ]
  })
}

################################################################################
# Variables
################################################################################

variable "project_name" {
  type    = string
  default = "carddemo"
}

variable "codebuild_role_arn" {
  description = "IAM role ARN for CodeBuild"
  type        = string
}

variable "m2_environment_id" {
  description = "AWS M2 environment ID"
  type        = string
}

variable "s3_artifact_bucket" {
  description = "S3 bucket for build artifacts"
  type        = string
}

variable "codestar_connection_arn" {
  description = "CodeStar Connections ARN for GitHub"
  type        = string
}

variable "github_repo" {
  description = "GitHub repository (org/repo format)"
  type        = string
  default     = "codev-workshops/aws-mainframe-modernization-carddemo"
}
