output "lambda_function_arn" {
  value = module.notion-counter-service.lambda_function_arn
}

output "dynamodb_table_arn" {
  value = aws_dynamodb_table.notion_counter_table.arn
}