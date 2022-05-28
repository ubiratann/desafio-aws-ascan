# Criando lambda
resource "aws_lambda_function" "lambda" {
  filename      = "lambda.zip"
  function_name = "TodoAppLambda"
  handler       = "main.handler"
  runtime       = "python3.8"
  role          = aws_iam_role.role.arn
  environment {
    variables = {
      "TODO_LIST_TABLE" = "todo-app"
    }
  }
}
