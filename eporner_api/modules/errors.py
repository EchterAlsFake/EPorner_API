class InvalidURL(Exception):
    def __init__(self, msg):
        super().__init__(msg)
        self.msg = msg


class HTML_IS_DISABLED(Exception):
    def __init__(self, msg):
        super().__init__(msg)
        self.msg = msg


class NotAvailable(Exception):
    def __init__(self, msg):
        super().__init__(msg)
        self.msg = msg


class VideoDisabled(Exception):
    def __init__(self, msg):
        super().__init__(msg)
        self.msg = msg


class InvalidVideo(Exception):
    def __init__(self, msg):
        super().__init__(msg)
        self.msg = msg


class NotFound(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)
        self.msg = msg


class NetworkError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)
        self.msg = msg


class BotDetection(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)
        self.msg = msg


class ProxyError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)
        self.msg = msg


class UnknownNetworkError(Exception):
    def __init__(self, msg):
        super().__init__(msg)
        self.msg = msg


class DownloadFailed(Exception):
    def __init__(self, msg):
        super().__init__(msg)
        self.msg = msg
