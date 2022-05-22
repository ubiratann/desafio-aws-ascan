resource "aws_iam_policy" "policy" {
  name        = "lambda-apigateway-policy"
  description = "Política que autoriza acesso ao DynamoDB e Amazon CloudWatch Logs."

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "dynamodb:DeleteItem",
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:UpdateItem"
        ]

        Effect   = "Allow"
        Resource = "*"
        Sid      = "Stmt1428341300017"
      },
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]

        Effect   = "Allow"
        Resource = "*"
        Sid      = ""
      }
    ]
  })
}

resource "aws_iam_role" "role" {
  name               = "lambda-apigateway-role"
  assume_role_policy = aws_iam_policy.policy.arn
}
