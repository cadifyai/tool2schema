# flake8: noqa
__version__ = "v2.0.0"

from .config import Config, SchemaType
from .schema import (
    EnableTool,
    FindToolEnabled,
    FindToolEnabledByName,
    FindToolEnabledByNameSchema,
    FindToolEnabledByTag,
    FindToolEnabledByTagSchemas,
    FindToolEnabledSchemas,
    LoadToolEnabled,
    SaveToolEnabled,
)

# Default global configuration
CONFIG = Config()
