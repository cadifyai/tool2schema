import pytest

from tests import functions
from tool2schema import ParseSchema

####################################################
#  Test schema parsing with the 'functions' module #
####################################################


@pytest.mark.parametrize(
    "function",
    [functions.function, functions.function_no_params, functions.function_tags],
)
def test_union_encode_decode_enum(function):
    assert ParseSchema(functions, function.schema.to_json()) == function
