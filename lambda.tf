# Criando lambda

data "archive_file" "artifact" {
  output_path = "files/lambda.zip"
  type        = "zip"
  source_file = "src/main.py"
}

resource "aws_lambda_function" "lambda" {

  filename      = data.archive_file.artifact.output_path
  function_name = "todo-app-lambda"
  handler       = "main.handler"
  runtime       = "python3.8"
  role          = aws_iam_role.api_role.arn

  environment {
    variables = {
      "TABLE" = var.table_name
    }
  }

  tags = local.common_tags
}

resource "aws_lambda_permission" "permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda.arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:*/*"
}
