import json

from app import app_settings, get_logger, BASE_DIR
from app.lambda_func import handler

settings = app_settings()

logger = get_logger(name="app.main")

TEST_BASE_DIR = BASE_DIR.replace('/app', '/tests') + '/datasets'

if __name__ == "__main__":
    class Ctx:
        def __init__(self):
            self.aws_request_id = 1


    with open(TEST_BASE_DIR + '/cs_doc_replace.json', 'r') as cs_json:
        data = json.load(cs_json)

    print(handler(data, Ctx()))
