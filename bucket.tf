# Criando bucket
resource "aws_s3_bucket" "bucket" {
  bucket = "ascan-todo-app-repository"
}

# Privando bucket
resource "aws_s3_bucket_acl" "acl" {
  acl    = "private"
  bucket = aws_s3_bucket.bucket.id
}

# Adicionando zip que contém a função lambda ao bucket criado
resource "aws_s3_object" "name" {
  bucket = aws_s3_bucket.bucket.id
  key    = "lambda.zip"
  source = "./lambda.zip"
  etag   = filemd5("./lambda.zip")
}
