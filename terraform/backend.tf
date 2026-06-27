terraform {
  backend "s3" {
    bucket = "siwybucket"
    key    = "dev/terraform.tfstate"
    region = "us-east-1"
  }
}