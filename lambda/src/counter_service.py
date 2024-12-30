import boto3
import json
import requests
import os
import logging

dynamodb = boto3.client('dynamodb')
DYNAMODB_TABLE = os.environ.get("DYNAMODB_TABLE")

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    # Extract headers
    notion_token = event['headers'].get('notion-token')
    counter_property = event['headers'].get('counter-property')

    body = None
    page_id = None

    if not notion_token or not counter_property:
        error_message = "Missing required headers: notion-token and counter-property"
        logger.error(error_message)
        return {
            "statusCode": 400,
            "body": json.dumps({"error": error_message})
        }

    # Parse webhook payload
    try:
        body = json.loads(event['body'])
        page_id = body["data"]["id"]
    except (KeyError, json.JSONDecodeError) as e:
        error_message = f"Invalid payload: {str(e)}"
        logger.error(error_message)
        return {
            "statusCode": 400,
            "body": json.dumps({"error": error_message})
        }

    # Update DynamoDB counter and get the new value
    try:
        updated_counter = update_counter(page_id)
    except Exception as e:
        error_message = f"DynamoDB update failed: {str(e)}"
        logger.error(error_message)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": error_message})
        }

    # Update Notion page with the current counter-value
    try:
        update_notion_page(notion_token, page_id, counter_property, updated_counter)
    except Exception as e:
        error_message = f"Notion API update failed: {str(e)}"
        logger.error(error_message)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": error_message})
        }

    return {
        "statusCode": 200,
        "body": json.dumps({"status": "success"})
    }


def update_counter(page_id):
    """
    Update the counter_value for the given page ID in DynamoDB.
    If the entry is new, initialize the counter_value at 0 and increment by 1.
    """
    try:
        response = dynamodb.update_item(
            TableName=DYNAMODB_TABLE,
            Key={'PageId': {'S': page_id}},
            UpdateExpression="SET counter_value = if_not_exists(counter_value, :start) + :inc",
            ExpressionAttributeValues={
                ':start': {'N': '0'},
                ':inc': {'N': '1'}
            },
            ReturnValues="UPDATED_NEW"
        )
        logger.info(f"DynamoDB update response: {response}")
        # Extract the updated counter_value
        updated_count = int(response['Attributes']['counter_value']['N'])
        return updated_count
    except Exception as e:
        logger.error(f"Error updating DynamoDB: {str(e)}")
        raise


def update_notion_page(notion_token, page_id, counter_property, updated_counter):
    """
    Update the Notion page with the given ID and counter-property.
    """
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"  # Hardcoded version
    }
    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {"properties": {counter_property: {"number": updated_counter}}}

    try:
        response = requests.patch(url, headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(f"Notion API error: {response.status_code} {response.text}")

        logger.info("Notion page updated successfully.")
    except Exception as e:
        logger.error(f"Error updating Notion page: {str(e)}")
        raise
