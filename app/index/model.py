class IndexResponse(object):

    def __init__(self, code, doc_id, message, detail_error=None, sqs_msg_id=None):
        self.code = code
        self.sqs_msg_id = sqs_msg_id
        self.id = doc_id
        self.message = message
        self.detail_error = detail_error
