resource "aws_dynamodb_table" "todo" {
  billing_mode   = "PROVISIONED"
  hash_key       = "id"
  name           = "todo-list"
  read_capacity  = 20
  write_capacity = 20

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

  global_secondary_index {
    name               = "descriptionIndex"
    hash_key           = "description"
    range_key          = "status"
    write_capacity     = 10
    read_capacity      = 10
    projection_type    = "INCLUDE"
    non_key_attributes = ["id"]
  }
}

