class IndexException(Exception):

    def __init__(self, code, message, detail_error):
        self.code = code
        self.message = message
        self.detail_error = detail_error

