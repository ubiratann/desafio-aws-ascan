# Criando lambda
resource "aws_lambda_function" "lambda" {

  filename      = "lambda.zip"
  function_name = "todo-list-lambda"
  handler       = "main.handler"
  runtime       = "python3.8"
  role          = aws_iam_role.api_role.arn

  environment {
    variables = {
      "TABLE" = "todo-list"
    }
  }
}

resource "aws_lambda_permission" "permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda.arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:*:${aws_apigatewayv2_api.api.id}/*"
}
