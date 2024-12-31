module "notion-counter-service" {
  source = "terraform-aws-modules/lambda/aws"

  function_name      = var.lambda_function_name
  description        = "Handles Notion webhook and updates counters in DynamoDB."
  handler            = "counter_service.lambda_handler"
  runtime            = "python3.12"
  source_path        = "../lambda/src"
  attach_policy_json = true
  timeout            = 10

  policy_json = jsonencode({
    Version   = "2012-10-17"
    Statement = [
      # DynamoDB permissions for read/write
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:UpdateItem",
          "dynamodb:PutItem"
        ]
        Resource = aws_dynamodb_table.notion_counter_table.arn
      },
      # Log permissions
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })

  environment_variables = {
    DYNAMODB_TABLE = aws_dynamodb_table.notion_counter_table.name
  }

  tags = {
    project = local.project_name
  }
}