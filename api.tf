resource "aws_apigatewayv2_api" "api" {
  name          = "todo"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "stage" {
  api_id      = aws_apigatewayv2_api.api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_apigatewayv2_integration" "integration" {
  api_id                 = aws_apigatewayv2_api.this.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = aws_lambda_function.todos[each.key].invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "put" {
  for_each = local.lambdas

  api_id    = aws_apigatewayv2_api.api.id
  route_key = "${upper(each.key)} /v1/todos"
  target    = "integrations/${aws_apigatewayv2_integration.todos[each.key].id}"
}

resource "aws_apigatewayv2_route" "post" {

}

resource "aws_apigatewayv2_route" "delete" {

}

resource "aws_apigatewayv2_route" "get" {
  api_id    = aws_apigatewayv2_api.this.id
  route_key = "GET /v1/todos/{todoId}"
  target    = "integrations/${aws_apigatewayv2_integration.todos["get"].id}"
}

