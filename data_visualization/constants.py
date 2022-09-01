STOP_SIGNAL = "STOP"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 1024


class ErrorMessageMixin:
    _verbose: bool

    def __init__(self, **kwargs):
        self._verbose = False
        for kw in ["verbose", "debug"]:
            if kw in kwargs and kwargs[kw]:
                self._verbose = True
                break

    def _print_status_message(self, message: str):
        if self._verbose:
            print("[{}] : {}".format(self.__class__.__name__, message))
