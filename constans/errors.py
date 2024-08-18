from enum import Enum, auto


class Errors(Enum):
    UnknownError = auto()
    OpenaiAPIConnectionError = auto()
    HttpxReadTimeout = auto()
    Duckduckgo_searchExceptionsTimeoutException = auto()

    @classmethod
    def value_of(cls, target_value):
        for e in Errors:
            if e.value == target_value:
                return e
        return Errors.UnknownError