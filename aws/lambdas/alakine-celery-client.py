import json
import celery

import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handle(event, context):
    logger.info('## ENVIRONMENT VARIABLES')
    logger.info(os.environ)
    logger.info('## EVENT')
    logger.info(event)
    print(json.dumps(event, indent=2))
    # workspace = event["workspace"]

    app = celery.Celery("tasks",
                        # backend="rpc://",
                        # backend="redis://vlad:y2IrK0VAsVMhKZ8LYiY@alakine-dev-001.tёi5yhi.0001.euw3.cache.amazonaws.com:6379/0",
                        # broker="amqps://guest:guest@localhost:5672")
                        broker="amqps://evolzene:nrg-soft552378@b-119055a9-999a-4156-a8fb-6f238a62b780.mq.eu-west-3.amazonaws.com:5671")
    # amqps://evolzene:nrg-soft552378@b-119055a9-999a-4156-a8fb-6f238a62b780.mq.eu-west-3.amazonaws.com:5671
    taskName = event["taskName"]
    carePlanAssignmentId = event["carePlanAssignmentId"]
    widgetId = event["widgetId"]
    taskToken = event["taskToken"]
    workspace = event["workspace"]

    job = app.send_task(taskName, args=[], kwargs={
        "workspace": workspace,
        "care_plan_assignment_id": carePlanAssignmentId,
        "widget_id": widgetId,
        "task_token": taskToken
    })

    return {
        'statusCode': 200,
        'body': json.dumps(f"Step: {taskName} | carePlanAssignmentId: {carePlanAssignmentId}")
    }
