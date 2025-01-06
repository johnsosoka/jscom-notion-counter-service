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
  tags = {
    project = local.project_name
  }
}