resource "aws_cloudwatch_log_group" "this" {
  name              = "/aws/lambda/todo-app-api-logs"
  retention_in_days = 3

  tags = local.common_tags
}
