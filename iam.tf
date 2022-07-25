data "aws_iam_policy_document" "assume-role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "todo-app-role" {
  name               = "todo-app-role"
  assume_role_policy = data.aws_iam_policy_document.assume-role.json

  tags = local.common_tags
}

data "aws_iam_policy_document" "todo-app-policy" {

  statement {
    sid       = "AllowCreatingLogGroups"
    effect    = "Allow"
    resources = ["arn:aws:logs:*:*:*"]
    actions   = ["logs:CreateLogGroup"]
  }

  statement {
    sid       = "AllowWritingLogs"
    effect    = "Allow"
    resources = ["arn:aws:logs:*:*:log-group:/aws/lambda/*:*"]

    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
  }

  statement {
    effect = "Allow"
    resources = [
      "arn:aws:dynamodb:${var.region}:*:table/${var.table_name}",
      "arn:aws:dynamodb:${var.region}:*:table/${var.table_name}/index/*"
    ]
    actions = [
      "dynamodb:PutItem",
      "dynamodb:DescribeTable",
      "dynamodb:DeleteItem",
      "dynamodb:GetItem",
      "dynamodb:Scan",
      "dynamodb:Query",
      "dynamodb:UpdateItem"
    ]
  }

  statement {
    effect    = "Allow"
    resources = ["*"]
    actions = [
      "dynamodb:ListTables",
      "ssm:DescribeParameters",
      "xray:PutTraceSegments"
    ]
  }
}

resource "aws_iam_policy" "iam_policy" {
  name   = "todo-app-policy"
  policy = data.aws_iam_policy_document.todo-app-policy.json

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "attachment" {
  policy_arn = aws_iam_policy.iam_policy.arn
  role       = aws_iam_role.todo-app-role.name
}
