resource "aws_dynamodb_table" "todo-app-table" {
  billing_mode = "PAY_PER_REQUEST"
  name         = var.table_name

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
    name            = "status_code_index"
    hash_key        = "status_code"
    range_key       = "description"
    projection_type = "ALL"
  }

  tags = local.common_tags
}

