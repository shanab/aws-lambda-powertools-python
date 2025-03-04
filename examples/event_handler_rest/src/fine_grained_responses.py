from http import HTTPStatus
from uuid import uuid4

import requests

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import (
    APIGatewayRestResolver,
    Response,
    content_types,
)
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext

tracer = Tracer()
logger = Logger()
app = APIGatewayRestResolver()


@app.get("/todos")
@tracer.capture_method
def get_todos():
    todos: requests.Response = requests.get("https://jsonplaceholder.typicode.com/todos")
    todos.raise_for_status()

    custom_headers = {"X-Transaction-Id": f"{uuid4()}"}

    return Response(
        status_code=HTTPStatus.OK.value,  # 200
        content_type=content_types.APPLICATION_JSON,
        body=todos.json()[:10],
        headers=custom_headers,
    )


# You can continue to use other utilities just as before
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
