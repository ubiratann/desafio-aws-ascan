resource "aws_cloudwatch_log_group" "this" {
  name              = "/aws/lamda/todo-list-lambda"
  retention_in_days = 3
}
