import json
import os
import time
import uuid

import boto3

table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])

# Load the quiz page once when the Lambda container starts
with open(os.path.join(os.path.dirname(__file__), "index.html"), encoding="utf-8") as f:
    PAGE = f.read()


def json_response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def lambda_handler(event, context):
    http = event.get("requestContext", {}).get("http", {})
    method = http.get("method", "")
    path = event.get("rawPath", "/")

    # GET /scores -> top 10
    if path == "/scores" and method == "GET":
        items = table.scan().get("Items", [])
        items.sort(key=lambda x: (-int(x["score"]), int(x["timestamp"])))
        return json_response(200, [{"name": i["name"], "score": int(i["score"])} for i in items[:10]])

    # POST /scores -> save one score
    if path == "/scores" and method == "POST":
        try:
            data = json.loads(event.get("body") or "{}")
            name = str(data.get("name", "")).strip()[:30]
            score = int(data.get("score", -1))
        except (ValueError, TypeError):
            return json_response(400, {"error": "Invalid request"})
        if not name or not 0 <= score <= 5:
            return json_response(400, {"error": "Name and a score from 0 to 5 are required"})
        table.put_item(Item={
            "id": str(uuid.uuid4()),
            "name": name,
            "score": score,
            "timestamp": int(time.time()),
        })
        return json_response(201, {"message": "Score saved"})

    # Everything else GET -> the quiz page
    if method == "GET":
        return {"statusCode": 200, "headers": {"Content-Type": "text/html; charset=utf-8"}, "body": PAGE}

    return json_response(405, {"error": "Method not allowed"})
