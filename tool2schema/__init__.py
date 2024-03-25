# flake8: noqa
__version__ = "v1.3.0"

from .config import Config
from .schema import (
    FindGPTEnabled,
    FindGPTEnabledByName,
    FindGPTEnabledByTag,
    FindGPTEnabledSchemas,
    GPTEnabled,
    LoadGPTEnabled,
    SaveGPTEnabled,
    SchemaType,
)

# Default global configuration
CONFIG = Config()
