resource "aws_dynamodb_table" "todo" {
  billing_mode = "PAY_PER_REQUEST"
  name         = "todo-list"

  attribute {
    name = "id"
    type = "N"
  }

  attribute {
    name = "status_code"
    type = "N"
  }

  attribute {
    name = "description"
    type = "S"
  }


  global_secondary_index {
    name               = "status_code_index"
    hash_key           = "status_code"
    range_key          = "description"
    write_capacity     = 10
    read_capacity      = 10
    projection_type    = "INCLUDE"
    non_key_attributes = ["id"]
  }
}

