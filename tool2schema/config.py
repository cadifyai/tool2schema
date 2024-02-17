from __future__ import annotations

from typing import Optional


class Config:
    """
    Configuration class for tool2schema.
    """

    def __init__(self, parent: Optional[Config] = None, **settings):
        self._parent = parent
        self._settings = settings

    @property
    def ignore_parameters(self) -> list[str]:
        """
        List of parameter names to ignore when creating a schema.
        """
        return self._get_setting(Config.ignore_parameters.fget.__name__, ["self", "args", "kwargs"])

    @ignore_parameters.setter
    def ignore_parameters(self, value: list[str]):
        self._set_setting(Config.ignore_parameters.fget.__name__, value)

    @property
    def ignore_descriptions(self) -> bool:
        """
        When true, omit all descriptions from the schema.
        """
        return self._get_setting(Config.ignore_descriptions.fget.__name__, False)

    @ignore_descriptions.setter
    def ignore_descriptions(self, value: bool):
        self._set_setting(Config.ignore_descriptions.fget.__name__, value)

    @property
    def ignore_all_parameters(self) -> bool:
        """
        When true, omit all parameters from the schema.
        """
        return self._get_setting(Config.ignore_all_parameters.fget.__name__, False)

    @ignore_all_parameters.setter
    def ignore_all_parameters(self, value: bool):
        self._set_setting(Config.ignore_all_parameters.fget.__name__, value)

    def reset_default(self):
        """
        Reset the configuration to the default settings.
        """
        self._settings = {}

    def _get_setting(self, name: str, default):
        """
        Get a setting value from the settings dictionary or the parent configuration.
        If not found, return the default value.

        :param name: Name of the setting
        :param default: Default value, used when the setting is not found in
            the settings dictionary and this configuration has no parent
        :return: The requested setting value
        """
        fallback = default if not self._parent else getattr(self._parent, name)
        return self._settings.get(name, fallback)

    def _set_setting(self, name: str, value):
        """
        Set a setting value in the settings dictionary.

        :param name: Name of the setting
        :param value: Value to set
        """
        self._settings[name] = value
