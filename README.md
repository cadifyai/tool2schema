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

# Why tool2schema?

Sometimes you can provide a large language model (LLM) with functions for it to call, but it needs to follow a specific schema. `tool2schema` is a small depedency-free library that converts your functions into that specific schema. So yeah, it's in the name!

# Installation

You can install `tool2schema` using `pip`.

```bash
pip3 install tool2schema
```

# Usage

On all functions that you would like to get the schema for, simply add the `EnableTool` decorator. Then use the return value of `FindToolEnabledSchemas` method directly in your requests to whatever LLM you are using.

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

## OpenAI

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

## Anthropic

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

## Mistral

Currently the same as OpenAI.

# Public API

In this section we describe in more detail how to utilise this library to its fullest extent.

## Configuration

There are a number of setting available for you to tweak.

| Name | Description | Default Value |
|----------|----------|--------------|
|   `ignore_parameters`  |   A list of parameter names to exclude from the schema  |  `[]`
|   `ignore_all_parameters`  |   A boolean value indicating whether to exclude all parameters from the schema. When set to true, `ignore_parameters` and `ignore_parameter_descriptions` will be ignored.  | `False` |
|   `ignore_function_description`  |   A boolean value indicating whether to exclude the function description from the schema.  | `False` |
|   `ignore_parameter_descriptions`  |   A boolean value indicating whether to exclude all parameter descriptions from the schema  | `False` |

### Decorator Configuration

You can provide the `EnableTool` decorator with the settings listed above.

For example, to omit parameters `b` and `c`:

```python
@GPTEnabled(ignore_parameters=["b", "c"])
def my_function(a: int, b: str, c: float):
    # Function code here...
```

### Global Configuration

It is also possible to specify the settings globally, so that they apply to all functions
unless explicitly overridden. It can be done by editing the global configuration as follows:

```python
import tool2schema

# Ignore all parameters named "a" or "b" by default
tool2schema.CONFIG.ignore_parameters = ["a", "b"]
```

## Module Operations

`tool2schema` has methods available to get functions from a module. See below for example usage of each of the public API methods that `tool2schema` exposes.

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

## Function Schema

To get the schema (in JSON format) for a function with the `EnableTool` decorator, either use the methods in the [Method Operations](#module-operations) section, or call the `to_json()` method on the function directly.

```python
@GPTEnabled
def my_function(a: int):
    """
    Example function description.

    :param a: First parameter
    """
    # Function code here...

my_function.to_json()  # <-- returns the function schema
```

**Note**: that the decorator returns a new `ToolEnabled` object with additional attributes, but can be called just like the original function.

## Function Tags

The `EnableTool` decorator also supports the `tags` keyword argument. This allows you to add tags to your function schema.

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

# How it Works

`tool2schema` uses certain features of your function definition to correctly populate the schema.

- Parameter type hints
- Parameter default values
- Docstring with parameter descriptions

The docstring must be using the [Sphinx docstring](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html) format.
**Note**: We use the parameter type hints instead of the docstring for parameter types.

## Supported Parameter Types

Most of the common types are supported. See [type_schema.py](./tool2schema/type_schema.py) for more details.

Any parameter types not supported will be listed as `object` in the schema.

## Enumerations

Enumeration in the schema are listed as strings of the enumeration names rather than the values. This was a design choice we felt made more sense for use with LLMs. We introduce some additional pre-processing to ensure that the enumeration name strings are mapped back to the correct enum value. Therefore, `@EnableTool` decorator allows to invoke the function using the name of the enum member rather than an instance of the class. For example, you may invoke `my_function(1, MyEnum.YES)` as `my_function(1, "YES")`. See the code for more details.

> Enumerations are used to explcitly indicate what values are permitted for the parameter value.

If the enumeration values are not known at the time of defining the function, you can add them later using the `add_enum` method.

```python
@GPTEnabled
def my_function(a: int, b: str):
    """
    Example function description.

    :param a: First parameter
    :param b: Second parameter
    """
    # Function code here...

my_function.schema.add_enum("b", ["yes", "no"])  #  <-- Add enum values for parameter 'b'
```