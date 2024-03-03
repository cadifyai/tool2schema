# flake8: noqa
__version__ = "v1.2.0"

from .config import Config
from .schema import (
    FindGPTEnabled,
    FindGPTEnabledByName,
    FindGPTEnabledByTag,
    FindGPTEnabledSchemas,
    GPTEnabled,
    SaveGPTEnabled,
    SchemaType,
)

# Default global configuration
CONFIG = Config()
