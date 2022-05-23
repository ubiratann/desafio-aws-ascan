resource "aws_api_gateway_rest_api" "api" {
  name = "todoAppRest"
}

resource "aws_api_gateway_resource" "resource" {
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.api.id
  path_part   = ""
}

resource "aws_api_gateway_method" "method" {

}
