class InvalidURL(Exception):
    def __init__(self, msg):
        self.msg = msg


class HTML_IS_DISABLED(Exception):
    def __init__(self, msg):
        self.msg = msg
