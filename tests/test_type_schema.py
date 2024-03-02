from enum import Enum
from typing import List, Literal, Optional, Type, Union

import pytest
from pydantic import TypeAdapter

from tool2schema.type_schema import TypeSchema

############################################
#  Custom enum class for testing purposes  #
############################################


class CustomEnum(Enum):
    """
    Custom enum for testing purposes.
    """

    YES = 0
    NO = 1
    MAYBE = 2


#########################################
#  Test TypeSchema with multiple types  #
#########################################


@pytest.mark.parametrize(
    "type_object",
    [
        dict,
        int,
        str,
        float,
        List[float],
        Optional[str],
        Union[int, float],
        Literal["a", "b", "c"],
        Union[str, float, None],
        Union[int, list[Literal[1, 2, 3]]],
        List[Optional[Literal["a", "b", "c"]]],
    ],
)
def test_optional_list(type_object: Type):
    adapter = TypeAdapter(type_object)
    assert TypeSchema.create(type_object).to_json() == adapter.json_schema()


################################
#  Test enum encoding/decoding #
################################


def test_union_encode_decode_enum():
    type_schema = TypeSchema.create(Union[int, CustomEnum, float])

    adapter = TypeAdapter(Union[int, Literal["YES", "NO", "MAYBE"], float])
    assert type_schema.to_json() == adapter.json_schema()

    assert type_schema.encode(CustomEnum.YES) == "YES"
    assert type_schema.decode(CustomEnum.YES) == CustomEnum.YES
    assert type_schema.decode("YES") == CustomEnum.YES


def test_list_encode_decode_enum():
    type_schema = TypeSchema.create(List[CustomEnum])

    adapter = TypeAdapter(List[Literal["YES", "NO", "MAYBE"]])
    assert type_schema.to_json() == adapter.json_schema()

    assert type_schema.encode([CustomEnum.YES]) == ["YES"]
    assert type_schema.decode([CustomEnum.YES]) == [CustomEnum.YES]
    assert type_schema.decode(["YES"]) == [CustomEnum.YES]


def test_list_optional_encode_decode_enum():
    type_schema = TypeSchema.create(List[Optional[CustomEnum]])

    adapter = TypeAdapter(List[Optional[Literal["YES", "NO", "MAYBE"]]])
    assert type_schema.to_json() == adapter.json_schema()

    assert type_schema.encode([CustomEnum.YES]) == ["YES"]
    assert type_schema.decode([CustomEnum.YES]) == [CustomEnum.YES]
    assert type_schema.decode(["YES"]) == [CustomEnum.YES]
    assert type_schema.decode([None]) == [None]
