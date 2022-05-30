resource "aws_cloudwatch_log_group" "this" {
  name              = "/aws/lambda/todo-list"
  retention_in_days = 3
}
