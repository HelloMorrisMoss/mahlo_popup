"""A class of error used to signal the program to restart."""


class RestartError(RuntimeError):
    def __init__(self, message: any = None):
        super().__init__(message)
