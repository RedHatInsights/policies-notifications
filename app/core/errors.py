from typing import Set


class BOPException(Exception):
    pass


class BOPInvalidRecipientException(BOPException):
    """Exception raised when BOP returns invalid recipients error

    Attributes:
        invalid_recipients -- list of invalid recipients
    """
    def __init__(self, invalid_recipients: Set[str]):
        self.invalid_recipients = invalid_recipients


class NoTemplateFoundException(Exception):
    pass


class RbacException(Exception):
    pass


class InvalidInputException(Exception):
    pass
