import uuid
from typing import Dict, Union, List

WineprefixConfigurationObject = Dict[str, Union[Dict, List, str, float, int, bool]]


class WineprefixConfiguration:
    _configuration_object: WineprefixConfigurationObject
    _program_configuration_overrides: WineprefixConfigurationObject

    def __init__(self, configuration_object: WineprefixConfigurationObject):
        self._configuration_object = {
            **configuration_object
        }

        self._program_configuration_overrides = dict()

    @property
    def id(self):
        return self.program_configuration_object.get("id", None) or str(uuid.uuid4())

    @property
    def user_configuration_object(self) -> WineprefixConfigurationObject:
        return {
            **self._configuration_object,
        }

    @property
    def program_configuration_object(self) -> WineprefixConfigurationObject:
        return {
            **self._configuration_object,
            **self._program_configuration_overrides
        }
