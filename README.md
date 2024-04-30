<div align="center">
<img src="media/logo.jpg" height=200>

<h1>
tool2schema
</h1>

Inspired by [janekb04/py2gpt](https://github.com/janekb04/py2gpt) and [fastai/lm-hackers](https://github.com/fastai/lm-hackers)

[![Check Code](https://github.com/cadifyai/tool2schema/actions/workflows/python-package.yml/badge.svg?branch=main)](https://github.com/cadifyai/tool2schema/actions/workflows/python-package.yml)
[![Downloads](https://static.pepy.tech/badge/tool2schema)](https://pepy.tech/project/tool2schema)
![Stars](https://img.shields.io/github/stars/cadifyai/tool2schema)

</div>

## Why tool2schema?

Sometimes you can provide a large language model (LLM) with functions for it to call, but it needs to follow a specific schema. `tool2schema` is a small depedency-free library that converts your functions into that specific schema. So yeah, it's in the name!

## Installation

You can install `tool2schema` using `pip`.

```bash
pip3 install tool2schema
```

## Usage

On all functions that you would like to get the schema for, simply add the `EnableTool` decorator. Then simply use the return value of `FindToolEnabledSchemas` method directly in your requests to whatever LLM you are using.

```python
from tool2schema import EnableTool

@EnableTool
def my_function1(a: int, b: str = "Hello"):
    """
    Example function description.

    :param a: First parameter
    :param b: Second parameter
    """
    # Function code here...
```

**Note**: To understand the appropriate format required for `tool2schema` to generate the appropriate schema, see the ['How it Works' section](#how-it-works).

### OpenAI

```python
import my_tools  # Module with your functions

from openai import OpenAI
from tool2schema import FindToolEnabledSchemas

client = OpenAI()
completion = client.chat.completions.create(
  model="gpt-4-turbo",
  tools=FindToolEnabledSchemas(my_tools)  # <-- As easy as that!
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ]
)
```

<details>
<summary><b>If finetuning an OpenAI model, then the schema is slightly different.</b></summary>

```python
import my_tools  # Module with your functions

from openai import OpenAI
from tool2schema import FindToolEnabledSchemas, SchemaType

client = OpenAI()
completion = client.chat.completions.create(
  model="gpt-4-turbo",
  tools=FindToolEnabledSchemas(my_tools, SchemaType.OPENAI_TUNE)  # <-- As easy as that!
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ]
)
```

</details>

### Anthropic

```python
import my_tools  # Module with your functions

import anthropic
from tool2schema import FindToolEnabledSchemas, SchemaType

client = anthropic.Anthropic()
response = client.beta.tools.messages.create(
    model="claude-3-opus-20240229",
    tools=FindToolEnabledSchemas(my_tools, SchemaType.ANTHROPIC_CLAUDE), # <-- As easy as that!
    messages=[{"role": "user", "content": "What's the weather like in San Francisco?"}],
)
```

### Mistral

Currently the same as OpenAI.

## Public API

You saw the use of `FindToolEnabledSchemas` above. `tool2schema` has other methods available to help manage your functions. See below for example usage of each of the public API methods that `tool2schema` exposes.

<details>
<summary><b>The examples assume the existance of this my_functions module.</b></summary>

```python
from tool2schema import GPTEnabled

@GPTEnabled
def my_function1(a: int, b: str = "Hello"):
    """
    Example function description.

    :param a: First parameter
    :param b: Second parameter
    """
    # Function code here...


@GPTEnabled(tags=["tag1"])
def my_function2(a: int, b: str = "Hello"):
    """
    Example function description.

    :param a: First parameter
    :param b: Second parameter
    """
    # Function code here...
```
</details>

<br>

```python
import my_functions
import tool2schema

# Return all functions with the ToolEnable decorator
functions = tool2schema.FindToolEnabled(my_functions)
schemas = tool2schema.FindToolEnabledSchemas(my_functions)

# Return the function with a ToolEnable decorator and the given name
function = tool2schema.FindToolEnabledByName(my_functions, "my_function1")
schema = tool2schema.FindToolEnabledByNameSchema(my_functions, "my_function1")

# Return all functions with a ToolEnable decorator and the given tag
functions = tool2schema.FindToolEnabledByTag(my_functions, "tag1")
schemas = tool2schema.FindToolEnabledByTagSchemas(my_functions, "tag1")

# Save the schemas of all functions with a ToolEnable decorator to a JSON file
json_path = "path/to/json/file"
tool2schema.SaveToolEnabled(my_functions, json_path)
```

## How it Works

`tool2schema` uses certain features of your function definition to correctly populate the schema.

- Parameter type hints
- Parameter default values
- Docstring with parameter descriptions

The docstring must be of a specific format. An example function is defined below that utilises all of the above features.

```python
def my_function(a: int, b: str = "Hello"):
    """
    Example function description.

    :param a: First parameter
    :param b: Second parameter
    """
```

To get the schema for this function, simply use the `GPTEnabled` decorator. The decorator will return a class with some additional attributes but can still be called as a function.

The schema of the function be accessed using the `schema` attribute.

```python
my_function.schema.to_json()
```

This returns the function schema in JSON format.

### Supported Parameter Types

The following parameter types are supported:

- `int`
- `float`
- `str`
- `bool`
- `list`

Any other parameter types will be listed as `object` in the schema.

### Enumerations

If you want to limit the possible values of a parameter, you can use a `typing.Literal` type hint or a
subclass of `enum.Enum`. For example, using `typing.Literal`:

```python
import typing


@GPTEnabled
def my_function(a: int, b: typing.Literal["yes", "no"]):
    """
    Example function description.

    :param a: First parameter
    :param b: Second parameter
    """
    # Function code here...
```

Equivalent example using `enum.Enum`:

```python
from enum import Enum

class MyEnum(Enum):
    YES = 0
    NO = 1


@GPTEnabled
def my_function(a: int, b: MyEnum):
    """
    Example function description.

    :param a: First parameter
    :param b: Second parameter
    """
    # Function code here...
```

In the case of `Enum` subclasses, note that the schema will include the enumeration names rather than the values.
In the example above, the schema will include `["YES", "NO"]` rather than `[0, 1]`.

The `@GPTEnabled` decorator also allows to invoke the function using the name of the enum member rather than an
instance of the class. For example, you may invoke `my_function(1, MyEnum.YES)` as `my_function(1, "YES")`.

If the enumeration values are not known at the time of defining the function,
you can add them later using the `add_enum` method.

```python
@GPTEnabled
def my_function(a: int, b: str,):
    """
    Example function description.

    :param a: First parameter
    :param b: Second parameter
    """
    # Function code here...

my_function.schema.add_enum("b", ["yes", "no"])
```

### Tags

The `GPTEnabled` decorator also supports the `tags` keyword argument. This allows you to add tags to your function schema.

```python
@GPTEnabled(tags=["tag1", "tag2"])
def my_function(a: int, b: str = "Hello"):
    """
    Example function description.

    :param a: First parameter
    :param b: Second parameter
    """
    # Function code here...
```

The tags can then be accessed using the `tags` attribute.

```python
my_function.tags  # ["tag1", "tag2"]
```

You can check if a function has a certain tag using the `has_tag` method.

```python
my_function.has_tag("tag1")  # True
```

### Disable parts of the schema

You can provide `GPTEnabled` with a number of settings to selectively disable parts of the schema.
For example, to omit certain parameters:

```python
@GPTEnabled(ignore_parameters=["b", "c"])  # b and c will not be included in the schema
def my_function(a: int, b: str, c: float):
    # Function code here...
```

The available settings are:
- `ignore_parameters`: A list of parameter names to exclude from the schema (defaults to `[]`).
- `ignore_all_parameters`: A boolean value indicating whether to exclude all parameters from the schema
  (defaults to `False`). When set to true, all other parameter-related settings (`ignore_parameters` and
  `ignore_parameter_descriptions`) will be ignored.
- `ignore_function_description`: A boolean value indicating whether to exclude the function description from
  the schema (defaults to `False`).
- `ignore_parameter_descriptions`: A boolean value indicating whether to exclude all parameter descriptions
  from the schema (defaults to `False`).

It is also possible to specify the settings globally, so that they apply to all functions
unless explicitly overridden. It can be done by editing the global configuration as follows:

```python
import tool2schema

# Ignore all parameters named "a" or "b" by default
tool2schema.CONFIG.ignore_parameters = ["a", "b"]
```
