import json
import requests
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    # Extract headers
    notion_token = event['headers'].get('notion-token')
    counter_property = event['headers'].get('counter-property')
    lent_date_property = event['headers'].get('lent-date-property', 'Lent On')
    logger.info(f"Received event: {event}")

    # Check if the event is a clear date event
    if is_date_clear_event(event, lent_date_property):
        logger.info("Date was cleared, skipping processing.")
        return {
            "statusCode": 200,
            "body": json.dumps({"status": "success"})
        }

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

    # Get the updated count
    updated_counter = update_counter(body, counter_property)

    # Update Notion page with the current count
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


def update_counter(body, column_name):
    """
    Update the count value using the existing value in the Notion page. Default to 1 if the value is null.
    """
    existing_count = body["data"]["properties"][column_name]["number"]
    logger.info(f"Existing Count: {existing_count}")

    # Default new_count to 1 for null values
    new_count = 1
    if existing_count:
        new_count = existing_count + 1
    else:
        logger.info("Existing count is null, defaulting to 1.")

    logger.info(f"New Count: {new_count}")
    return new_count


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


def is_date_clear_event(event, lent_date_property) -> bool:
    """
    Check if the event is a clear date event (item returned, start date null)

    :param event:
    :param lent_date_property:
    :return:
    """
    body = json.loads(event['body'])
    lent_on = body['data']['properties'][lent_date_property]
    if not lent_on:
        logger.warning(f"Event does not contain property: {lent_date_property}")
        return True

    if lent_on["date"] is None:
        logger.info(
            f"Event property {lent_date_property} does not contain a date, date was cleared, skipping processing.")
        return True

    return False
