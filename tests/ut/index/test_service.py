import asyncio
import logging
import unittest
from unittest.mock import MagicMock

from app import BASE_DIR, CSIndexingService

logger = logging.getLogger("test_service")

TEST_BASE_DIR = BASE_DIR.replace('/app', '/tests') + '/datasets'


class ServiceTestSuite(unittest.TestCase):

    def test_index(self):
        ind_res = {"_index": "charging_stations", "_type": "_doc", "_id": "ROreJoMBZrhZq16vMVmy", "_version": 1,
                   "result": "created", "_shards": {"total": 3, "successful": 1, "failed": 0},
                   "_seq_no": 6,
                   "_primary_term": 1
                   }

        mock_os_client = MagicMock()
        mock_os_client.index.return_value = ind_res
        cs = CSIndexingService(os_client=mock_os_client, logger=logger)
        cs_res = asyncio.run(cs.index(doc="{\"_id\": 1}", doc_id=None))
        self.assertIsNotNone(cs_res)
        self.assertEqual(201, cs_res.code)
        self.assertEqual("created", cs_res.message)

    def test_index_replace(self):
        ind_res = {"_index": "charging_stations", "_type": "_doc", "_id": "ROreJoMBZrhZq16vMVmy", "_version": 1,
                   "result": "updated", "_shards": {"total": 3, "successful": 1, "failed": 0},
                   "_seq_no": 6,
                   "_primary_term": 1
                   }
        mock_os_client = MagicMock()
        mock_os_client.index.return_value = ind_res
        cs = CSIndexingService(os_client=mock_os_client, logger=logger)
        cs_res = asyncio.run(cs.index(doc="{\"_id\": 1}", doc_id="1234545"))
        self.assertIsNotNone(cs_res)
        self.assertEqual(201, cs_res.code)
        self.assertEqual("updated", cs_res.message)

    def test_index_exception(self):
        mock_os_client = MagicMock()
        mock_os_client.index.side_effect = Exception("Fake Error")
        cs = CSIndexingService(os_client=mock_os_client, logger=logger)
        try:
            asyncio.run(cs.index(doc="{\"_id\": 1}", doc_id="1234545"))
        except Exception as e:
            self.assertIsNotNone(e)


if __name__ == '__main__':
    """
    Run this with command 
    $export ACTIVE_ENVIRONMENT=test 
    $python -m unittest discover -s tests
    """
    unittest.main()
