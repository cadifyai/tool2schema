import typing
from enum import Enum

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

    :param a: This is a parameter
    :param b: This is another parameter
    :param c: This is a boolean parameter
    :param d: This is a list parameter
    """
    return a, b, c, d


@GPTEnabled(tags=["test"])
def function_tags(a: int, b: str, c: bool = False, d: list[int] = [1, 2, 3]):
    """
    This is a test function.

    :param a: This is a parameter
    :param b: This is another parameter
    :param c: This is a boolean parameter
    :param d: This is a list parameter
    """
    return a, b, c, d


def function_not_enabled(a: int, b: str) -> None:
    """
    This is a test function.

    :param a: This is a parameter
    :param b: This is another parameter
    """
    pass


@GPTEnabled
def function_literal(a: typing.Literal[0, 1, 2], b: typing.Literal["a", "b", "c"] = "a"):
    """
    This is a test function.

    :param a: This is a parameter
    :param b: This is another parameter
    """
    return a, b


@GPTEnabled
def function_add_enum(a: str):
    """
    This is a test function.

    :param a: This is a parameter
    """
    return a


function_add_enum.schema.add_enum("a", ["YES", "NO", "MAYBE"])


class CustomEnum(Enum):
    """
    Custom enum for testing purposes.
    """

    X = 0
    Y = 1
    Z = 2


@GPTEnabled
def function_enum(a: CustomEnum):
    """
    This is a test function.

    :param a: This is a parameter
    """
    return a


@GPTEnabled
def function_union(a: typing.Optional[bool], b: typing.Union[str, int] = 4):
    """
    This is a test function.

    :param a: This is a parameter
    :param b: This is another parameter
    """
    return a, b
