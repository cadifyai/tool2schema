from types import ModuleType
from typing import Callable, Optional

from tool2schema import FindGPTEnabled


def ParseSchema(module: ModuleType, schema: dict) -> Optional[Callable]:
    """
    Given a schema, return the corresponding function from the module. The function
    has to be decorated with `GPTEnabled` for this method to retrieve it.
    :param module: The module where the function is defined.
    :param schema: The schema corresponding to the function.
    :return: The function corresponding to the schema, or None if the function is not found.
    """

    if not (function := schema.get("function", None)):
        return None

    if not (name := function.get("name", None)):
        return None

    for func in FindGPTEnabled(module):
        if func.__name__ == name:
            return func

    return None
