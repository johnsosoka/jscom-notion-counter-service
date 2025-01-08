# jscom-notion-counter-service

Simple API that provides a serverless mechanism to iterate on a number in a Notion page. This service was created to 
count the number of times an item in a Notion database was lent out. However, it can be used to iterate on any number in 
a Notion page when any given action occurs.

## Architecture

A webhook is received through api-gateway, which triggers a lambda function that increments a number in a Notion page. 
The notion token is provided in the webhook header along with an additional header describing the column name to increment.

## Usage

* Configure a Notion integration token & share the page you want to increment with the integration. 
* Create a new webhook for a given action (Lent on Date field changes)
* Destination URL is https://api.johnsosoka.com/v1/notion/counter
* Add the following headers:
  * `notion-token` - Notion integration token
  * `column-name` - Column name to increment
  * `lent-date-property` - Service will optionally filter date change events where the date was cleared. When a date is cleared, the service skips iterating on the property.



