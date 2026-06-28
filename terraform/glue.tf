resource "aws_glue_job" "crypto_ingestion" {

  name     = "crypto-ingestion"
  role_arn = aws_iam_role.glue_role.arn

  command {
    name            = "pythonshell"
    script_location = "s3://siwy-humboligerra2/scripts/crypto_ingestion1.py"
    python_version  = "3.9"
  }

  glue_version = "5.0"

  max_capacity = 0.0625

  timeout    = 60
  max_retries = 0

  default_arguments = {
    "--job-language" = "python"
  }

  execution_property {
    max_concurrent_runs = 1
  }
}