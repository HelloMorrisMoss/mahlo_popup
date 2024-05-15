"""A class of error used to signal the program to restart."""


class RestartError(RuntimeError):
    def __init__(self, message: any = None, *args, **kwargs):
        super().__init__(message, *args, **kwargs)
        self.additional_information = kwargs.get("additional_information")
