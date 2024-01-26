from __future__ import annotations
from tool2schema import GPTEnabled


@GPTEnabled
def function_no_params():
    """
    This is a test function.
    """
    return None


@GPTEnabled
def function(a: int, b: str, c: bool = False, d: list[int] = [1, 2, 3]):
    """
    This is a test function.

    :param a: This is a parameter;
    :param b: This is another parameter;
    :param c: This is a boolean parameter;
    :param d: This is a list parameter;
    """
    return a, b, c, d


@GPTEnabled(tags=["test"])
def function_tags(a: int, b: str, c: bool = False, d: list[int] = [1, 2, 3]):
    """
    This is a test function.

    :param a: This is a parameter;
    :param b: This is another parameter;
    :param c: This is a boolean parameter;
    :param d: This is a list parameter;
    """
    return a, b, c, d


def function_not_enabled(a: int, b: str) -> None:
    """
    This is a test function.

    :param a: This is a parameter;
    :param b: This is another parameter;
    """
    pass
