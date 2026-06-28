########################################
# Trust Policy
########################################

data "aws_iam_policy_document" "glue_assume_role" {

  statement {
    effect = "Allow"

    actions = [
      "sts:AssumeRole"
    ]

    principals {
      type = "Service"

      identifiers = [
        "glue.amazonaws.com"
      ]
    }
  }
}

########################################
# IAM Role
########################################

resource "aws_iam_role" "glue_role" {

  name = "siwy-service-role"

  assume_role_policy = data.aws_iam_policy_document.glue_assume_role.json

  tags = {
    Project = "crypto"
    Environment = "dev"
  }
}

########################################
# AWS Managed Glue Policy
########################################

resource "aws_iam_role_policy_attachment" "glue_service_role" {

  role = aws_iam_role.glue_role.name

  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

########################################
# S3 Access
########################################

resource "aws_iam_role_policy_attachment" "glue_s3_access" {

  role = aws_iam_role.glue_role.name

  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

########################################
# CloudWatch Logs
########################################

resource "aws_iam_role_policy_attachment" "glue_logs" {

  role = aws_iam_role.glue_role.name

  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}