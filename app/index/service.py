import logging
import uuid

from opensearchpy import OpenSearch

from app.exception.indexexception import IndexException
from app.index.model import IndexResponse


class CSIndexingService:
    __index_name__ = "charging_stations"

    """
    Charging Station document indexing service class implementation.
    """

    def __init__(self, os_client: OpenSearch, logger: logging.Logger):
        self.os_client = os_client
        self.logger = logger

    async def index(self, doc: str, doc_id: str = None) -> IndexResponse:
        """
        Method to index the document on OpenSearch.
        :param doc: document body as string.
        :param doc_id: document identifier in case of replace operation.
        :return: Index Response.
        """
        doc_id = doc_id if doc_id else uuid.uuid4()
        try:
            response = self.os_client.index(
                index=CSIndexingService.__index_name__,
                body=doc,
                id=doc_id,
                refresh=True
            )
        except Exception as e:
            raise IndexException(code=500, message="Internal Server error while indexing",
                                 detail_error=str(e))
        return IndexResponse(code=200, doc_id=response["_id"], message=response["result"])
