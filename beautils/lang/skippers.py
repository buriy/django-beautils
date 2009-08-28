class SkipLine(Exception):
    def __init__(self, message="Skip this row"):
        super(Exception, self).__init__(message)

class SkipFile(Exception):
    def __init__(self, message="Terminate process"):
        super(Exception, self).__init__(message)
