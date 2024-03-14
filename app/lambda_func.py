import asyncio
import json
import pprint

from app import get_os_search_service
from app.dependencies import inject_logger
from app.exception.indexexception import IndexException
from app.index.model import IndexResponse

logger = inject_logger(name="app.lambda_func")


class LambdaError(object):

    def __init__(self, code, message, detail_error=None):
        self.code = code
        self.message = message
        self.detail_error = detail_error


def handler(event, context):
    """
    Lambda Handler function trigger when SQS message is available, the event is SQS event payload.
    :param context: Lambda runtime context.
    :param event: SQS Event records.
        {
          "Records": [
            {
              "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
              "receiptHandle": "AQEBwJnKyrHigUMZj6rYigCgxlaS3SLy0a...",
              "body": "{\"station_id\":\"11\",\"vendor_id\":\"chargemod\",\"address_line\":\"Bangalore, Varthur Rd Vill Sidapur\",\"available_chargers\":[{\"charger_point_type\":\"AC\",\"connectors\":[{\"connector_point_id\":1,\"relay_number\":111,\"status\":1,\"tariff\":125}],\"id\":1,\"power_capacity\":\"240VAC, 15A\"}],\"country\":\"india\",\"distance_unit\":null,\"is_ocpp\":false,\"geo_address\":[12.942873468781595,77.72697865942747],\"name\":\"Harikrishna Fuel Station (Bharat Petroleum)\",\"postal_code\":\"560087\",\"qr_code\":\"CM-S00115-4RXJJRGTXU\",\"rating\":{\"1\":0,\"2\":0,\"3\":0,\"4\":0,\"5\":0,\"avg_rating\":0},\"state\":\"Karnataka\",\"station_status\":\"not_connected\",\"station_time\":{\"end_time\":\"11:59 PM\",\"start_time\":\"12:00 AM\"},\"total_connectors_available\":0,\"town\":\"Bangalore\"}",
              "attributes": {
                "ApproximateReceiveCount": "1",
                "SentTimestamp": "1545082649183",
                "SenderId": "AIDAIENQZJOLO23YVJ4VO",
                "ApproximateFirstReceiveTimestamp": "1545082649185"
              },
              "messageAttributes": {},
              "md5OfBody": "098f6bcd4621d373cade4e832627b4f6",
              "eventSource": "aws:sqs",
              "eventSourceARN": "arn:aws:sqs:us-east-2:123456789012:my-queue",
              "awsRegion": "us-east-2"
            }
          ]
        }
    :return: IndexResponse
    """
    logger.info("Lambda Request ID: %s", context.aws_request_id)
    logger.info("Event data: %s", str(event))
    return process_event(event)


def process_event(event) -> str:
    cs_resp = []
    if event["Records"] is None:
        return json.dumps(LambdaError(code=500, message="Invalid Event payload"))
    for record in event["Records"]:
        message_id = record["messageId"]
        doc = record["body"]
        try:
            if doc:
                doc_json = json.loads(doc)
                _id = None
                if "uid" in doc_json:
                    _id = doc_json.pop("uid")
                    logger.info("Indexing Charge Station document with id: %s", _id)
                index_res = asyncio.run(get_os_search_service().index(doc=json.dumps(doc_json), doc_id=_id))
                cs_resp.append(IndexResponse(code=index_res.code, sqs_msg_id=message_id, doc_id=index_res.id,
                                             message=index_res.message))
            else:
                cs_resp.append(IndexResponse(code=400, sqs_msg_id=message_id, doc_id=None,
                                             message="Body is empty, hence skipping from index."))
        except IndexException as ie:
            logger.error(ie)
            cs_resp.append(IndexResponse(code=ie.code, sqs_msg_id=message_id, doc_id=None, message=ie.message,
                                         detail_error=ie.detail_error))
        except Exception as e:
            logger.error(e)
            cs_resp.append(IndexResponse(code=500, sqs_msg_id=message_id, doc_id=None, message=str(e)))

    return json.dumps(cs_resp, default=lambda o: o.__dict__)
