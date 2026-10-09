import json


def lambda_handler(event, context):
    # Each SQS record body is an SNS message, whose "Message" is the EventBridge event.
    for record in event["Records"]:
        sns_message = json.loads(record["body"])
        eventbridge_event = json.loads(sns_message["Message"])
        order = eventbridge_event["detail"]

        print(f"Processing order {order['order_id']} for {order['customer_email']}")
        for item in order["items"]:
            print(f"  reserve stock: {item['quantity']} x {item['name']}")
        print(f"  total charged: ${order['total']}")

    return {"processed": len(event["Records"])}
