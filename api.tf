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
  api_id                 = aws_apigatewayv2_api.api.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = aws_lambda_function.lambda.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "delete" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "DELETE /v1/todo/{id}"
  target    = "integrations/${aws_apigatewayv2_integration.integration.id}"
}

resource "aws_apigatewayv2_route" "post" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "POST /v1/todo"
  target    = "integrations/${aws_apigatewayv2_integration.integration.id}"
}

resource "aws_apigatewayv2_route" "start_task" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "PUT /v1/todo/start/{id}"
  target    = "integrations/${aws_apigatewayv2_integration.integration.id}"
}

resource "aws_apigatewayv2_route" "stop_task" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "PUT /v1/todo/stop/{id}"
  target    = "integrations/${aws_apigatewayv2_integration.integration.id}"
}

resource "aws_apigatewayv2_route" "finish_task" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "PUT /v1/todo/finish/{id}"
  target    = "integrations/${aws_apigatewayv2_integration.integration.id}"
}

resource "aws_apigatewayv2_route" "update" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "PUT /v1//update/{id}"
  target    = "integrations/${aws_apigatewayv2_integration.integration.id}"
}

resource "aws_apigatewayv2_route" "get" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "GET /v1/todo/{id}"
  target    = "integrations/${aws_apigatewayv2_integration.integration.id}"
}

resource "aws_apigatewayv2_route" "get_all" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "GET /v1/todo/}"
  target    = "integrations/${aws_apigatewayv2_integration.integration.id}"
}
