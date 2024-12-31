resource "aws_apigatewayv2_integration" "notion_counter_integration" {
  api_id             = local.api_gateway_id
  integration_type   = "AWS_PROXY"
  integration_uri    = module.notion-counter-service.lambda_function_arn
  integration_method = "ANY"
  passthrough_behavior = "WHEN_NO_MATCH"
}

resource "aws_apigatewayv2_route" "notion_counter_route" {
  api_id    = local.api_gateway_id
  route_key = "POST /v1/notion/counter"
  target    = "integrations/${aws_apigatewayv2_integration.notion_counter_integration.id}"
}

resource "aws_lambda_permission" "notion_counter_api_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = module.notion-counter-service.lambda_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${local.execution_arn}/*"
}