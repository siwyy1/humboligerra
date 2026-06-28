terraform {
  backend "s3" {
    bucket = "siwybucket2"
    key    = "dev/terraform.tfstate"
    region = "eu-central-1"
  }
}