import uuid
from dataclasses import asdict
from typing import Dict, Union, List

from grapejuice_common.features.wineprefix_configuration_model import WineprefixConfigurationModel

WineprefixConfigurationObject = Dict[str, Union[Dict, List, str, float, int, bool]]


class WineprefixConfiguration:
    _model: WineprefixConfigurationModel
    _program_configuration_overrides: WineprefixConfigurationObject

    def __init__(self, model: WineprefixConfigurationModel):
        self._model = model

        self._program_configuration_overrides = dict()

    @property
    def id(self):
        return self.program_configuration_object.get("id", None) or str(uuid.uuid4())

    @property
    def user_configuration_object(self) -> WineprefixConfigurationObject:
        return asdict(self._model)

    @property
    def program_configuration_object(self) -> WineprefixConfigurationObject:
        return {
            **self.user_configuration_object,
            **self._program_configuration_overrides
        }
