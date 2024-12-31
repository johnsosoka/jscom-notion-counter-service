resource "aws_dynamodb_table" "notion_counter_table" {
  name           = var.dynamodb_table_name
  billing_mode   = "PAY_PER_REQUEST" # Cost-effective and scales with usage
  hash_key       = "PageId"

  attribute {
    name = "PageId"
    type = "S"
  }

  tags = {
    project = local.project_name
  }
}