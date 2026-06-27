module "s3_bucket" {

  source = "terraform-aws-modules/s3-bucket/aws"

  bucket = "siwy-humboligerra"

  acl = "private"

  control_object_ownership = true
  object_ownership         = "ObjectWriter"

  versioning = {
    enabled = true
  }

  tags = {
    Project     = "humboligerrapro"
    Environment = "dev"
    ManagedBy   = "Terraform"
  }
}