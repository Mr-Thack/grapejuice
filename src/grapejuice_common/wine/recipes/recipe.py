from abc import ABC
from typing import Callable, Union, List

from grapejuice_common.wine.wineprefix import Wineprefix
from grapejuice_common.wine.wineprefix_hints import WineprefixHint

RecipeIndicator = Callable[[Wineprefix], bool]
RecipeIndicatorList = List[RecipeIndicator]


class Recipe(ABC):
    _indicators: RecipeIndicatorList
    _hint: Union[WineprefixHint, None]

    def __init__(
        self,
        indicators: Union[RecipeIndicatorList, None] = None,
        hint: Union[WineprefixHint, None] = None
    ):
        self._indicators = indicators or []
        self._hint = hint

    def _run_indicators(self, prefix: Wineprefix) -> bool:
        v = True

        for indicator in self._indicators:
            v = v and indicator(prefix)

        return v

    def exists_in(self, prefix: Wineprefix) -> bool:
        return self._run_indicators(prefix)

    @property
    def hint(self) -> Union[WineprefixHint, None]:
        return self._hint

    def make_in(self, prefix: Wineprefix):
        pass
