import inspect
from typing import Any


class BaseParser:
    def attr(self, obj: object, name: str, msg: str = None):
        return self.__test(hasattr(obj, name), msg)

    def inst(self, obj: object, info: Any, msg: str = None):
        return self.__test(isinstance(obj, info), msg)

    def func(self, obj: object, msg: str = None):
        return self.__test(inspect.isfunction(obj), msg)

    def sig(self, obj: Any, args_count: int, msg: str = None):
        parameter_count = len(inspect.signature(obj).parameters)
        return self.__test(parameter_count == args_count, msg)

    def __test(self, cond: bool, msg: str = None):
        if not msg:
            return cond
        assert cond, msg
