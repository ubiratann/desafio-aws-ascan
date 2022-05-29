resource "aws_dynamodb_table" "todo" {
  name     = "todo-list"
  hash_key = "id"

  attribute {
    name = "id"
    type = "N"
  }

  attribute {
    name = "description"
    type = "S"
  }

  attribute {
    name = "status"
    type = "N"
  }
}

