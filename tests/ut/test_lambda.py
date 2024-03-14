import json
import unittest
from unittest.mock import MagicMock, Mock

from app import lambda_func, BASE_DIR
from app.index.model import IndexResponse

TEST_BASE_DIR = BASE_DIR.replace('/app', '/tests') + '/datasets'


class LambdaTest(unittest.TestCase):

    @unittest.skip("Service mocking is not working in lambda_func")
    def test_something(self):
        mock_cs = Mock()
        mock_cs.search = Mock(return_value=IndexResponse(code=201, message="Created",
                                                         sqs_msg_id=None, detail_error=None, doc_id="1"))
        mock = MagicMock()
        mock.get_os_search_service().return_value = mock_cs

        with open(TEST_BASE_DIR + '/cs_doc.json', 'r') as cs_json:
            data = json.load(cs_json)
        cs_res = lambda_func.process_event(data)
        self.assertIsNotNone(cs_res)


if __name__ == '__main__':
    unittest.main()
