provider "aws" {
  region  = var.region
  profile = "terraform-admin"
}

terraform {
  backend "s3" {
    bucket = "tfstate-050485243139"
    region = "sa-east-1"
    key    = "terraform.tfstate"
  }
}
