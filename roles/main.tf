# Criando policy
resource "aws_iam_policy" "policy" {
  name        = "lambda-apigateway-policy"
  description = "Política que autoriza acesso ao DynamoDB, Amazon CloudWatch Logs e execução da Lambda function."

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # Permissões do banco de dados
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
      # Permissões do Cloudwatch logs
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]

        Effect   = "Allow"
        Resource = "*"
        Sid      = ""
      },
      # Permissão de execução
      {
        Action = [
          "sts:AssumeRole"
        ]

        Principal = {
          Service = "lambda.amazonaws.com"
        },

        Effect = "Allow"
        Sid    = ""
      }
    ]
  })
}

# Vinculando policy com role
resource "aws_iam_role" "role" {
  name               = "lambda-apigateway-role"
  assume_role_policy = aws_iam_policy.policy.id
}
