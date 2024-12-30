variable "lambda_function_name" {
  description = "Name of the Lambda function"
  type        = string
  default     = "notion-counter-service"
}

variable "dynamodb_table_name" {
  description = "Name of the DynamoDB table"
  type        = string
  default     = "notion-counter"
}
