data "aws_caller_identity" "current" {}

resource "aws_s3_bucket" "remote-state-bucket" {
  bucket = "tfstate-${data.aws_caller_identity.current.account_id}"

  tags = local.common_tags
}

resource "aws_s3_bucket_versioning" "remote-state-bucket-versioning" {
  bucket = aws_s3_bucket.remote-state-bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_acl" "acl" {
  bucket = aws_s3_bucket.remote-state-bucket.id
  acl    = "private"
}
