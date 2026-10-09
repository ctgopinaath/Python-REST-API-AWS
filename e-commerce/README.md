# E-Commerce Orders — FastAPI + Lambda + API Gateway + EventBridge + SNS + SQS

A small **event-driven** shop. Placing an order returns right away. The rest of the work happens in the background through events.

---

## How It Works

```
curl POST /orders
     |
     v
API Gateway (HTTP API)
     |
     v
Lambda: ecommerce-orders-api   (FastAPI app, run by Mangum)
     |  put_events  "OrderPlaced"
     v
EventBridge bus: ecommerce-orders-bus
     |  rule: source=ecommerce.orders, detail-type=OrderPlaced
     v
SNS topic: ecommerce-order-notifications ──> Email (optional)
     |
     v
SQS queue: ecommerce-order-processing  (failed messages -> DLQ after 3 tries)
     |
     v
Lambda: ecommerce-order-worker   (reserves stock -> prints to CloudWatch Logs)
```

| Service | Role in this demo |
|---------|-------------------|
| **FastAPI** | Defines the REST endpoints and validates requests (Pydantic) |
| **Lambda** | Runs the API and the background worker. No servers to manage |
| **API Gateway** | Public HTTPS URL. Sends every route to the FastAPI Lambda |
| **EventBridge** | Event bus. Rules decide who receives which event |
| **SNS** | Pub/sub. Sends one message to many subscribers (queue + email) |
| **SQS** | Buffers messages so the worker can process them at its own pace and retry |

---

## Folder Structure

```
e-commerce/
├── template.yaml        # AWS SAM — defines every AWS resource
├── api/
│   ├── app.py           # FastAPI app + Mangum Lambda handler
│   └── requirements.txt
└── worker/
    └── handler.py       # SQS consumer Lambda
```

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/products` | List products |
| GET | `/products/{id}` | Get one product |
| POST | `/orders` | Place an order → publishes `OrderPlaced` event |
| GET | `/orders/{order_id}` | Get an order |

> Orders are kept **in memory**, so `GET /orders/{id}` only works while the same Lambda container is warm. That keeps the demo simple. Use DynamoDB for real storage.

---

## Option 1 — Run Locally (FastAPI only)

If `EVENT_BUS_NAME` is not set, the app skips EventBridge and only prints the event.

```bash
cd e-commerce/api
pip install -r requirements.txt boto3 uvicorn
uvicorn app:app --reload
```

Open the Swagger UI at `http://127.0.0.1:8000/docs`

```bash
curl http://127.0.0.1:8000/products

curl -X POST http://127.0.0.1:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"customer_email": "sam@example.com", "items": [{"product_id": 1, "quantity": 1}, {"product_id": 3, "quantity": 2}]}'
```

---

## Option 2 — Deploy to AWS

### Prerequisites

- AWS CLI configured (`aws configure`)
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)

### Deploy

```bash
cd e-commerce
sam build --use-container
sam deploy --guided
```

> `--use-container` builds inside a Docker image that matches the Lambda runtime (Python 3.13), so Docker must be running. If you have Python 3.13 installed locally, a plain `sam build` also works.

Answer the prompts:
- Stack name: `ecommerce-demo`
- `NotificationEmail`: your email, or leave it blank
- `OrdersApiFunction has no authentication. Is this okay?` → **y**

When the deploy finishes, copy **ApiUrl** from the Outputs.
If you entered an email, click the **confirm subscription** link that AWS sends you.

### Test

```bash
API=https://abc123.execute-api.us-east-1.amazonaws.com

curl $API/products

curl -X POST $API/orders \
  -H "Content-Type: application/json" \
  -d '{"customer_email": "sam@example.com", "items": [{"product_id": 2, "quantity": 1}]}'
```

### Watch the event flow through

```bash
# Worker logs — shows "Processing order ..." a few seconds after the POST
sam logs -n OrderWorkerFunction --stack-name ecommerce-demo --tail

# API logs
sam logs -n OrdersApiFunction --stack-name ecommerce-demo --tail
```

You can also send an event straight to the bus, without the API:

```bash
aws events put-events --entries '[{
  "EventBusName": "ecommerce-orders-bus",
  "Source": "ecommerce.orders",
  "DetailType": "OrderPlaced",
  "Detail": "{\"order_id\":\"test-1\",\"customer_email\":\"a@b.com\",\"items\":[{\"name\":\"Mouse\",\"quantity\":1}],\"total\":29.99}"
}]'
```

### Clean Up

```bash
sam delete --stack-name ecommerce-demo
```

---

## Why Events Instead of Calling the Worker Directly?

| Direct call | Event-driven (this demo) |
|-------------|--------------------------|
| The API waits for stock, email, and so on to finish | The API returns as soon as the event is published |
| If the worker fails, the order request fails | SQS retries. Failed messages go to the DLQ |
| A new consumer means changing the API code | Add another SNS subscriber or EventBridge rule. The API code stays the same |
