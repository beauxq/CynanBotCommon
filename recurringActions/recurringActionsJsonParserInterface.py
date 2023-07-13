from abc import ABC, abstractmethod
from typing import Optional

try:
    from CynanBotCommon.recurringActions.weatherRecurringAction import \
        WeatherRecurringAction
    from CynanBotCommon.recurringActions.wordOfTheDayRecurringAction import \
        WordOfTheDayRecurringAction
except:
    from recurringActions.weatherRecurringAction import WeatherRecurringAction
    from recurringActions.wordOfTheDayRecurringAction import \
        WordOfTheDayRecurringAction


class RecurringActionsJsonParserInterface(ABC):

    @abstractmethod
    async def parseWeather(
        self,
        minutesBetween: Optional[int],
        jsonString: Optional[str]
    ) -> Optional[WeatherRecurringAction]:
        pass

    @abstractmethod
    async def parseWordOfTheDay(
        self,
        jsonString: Optional[str]
    ) -> Optional[WordOfTheDayRecurringAction]:
        pass

    @abstractmethod
    async def weatherToJson(self, weather: WeatherRecurringAction) -> str:
        pass

    @abstractmethod
    async def wordOfTheDayToJson(self, wordOfTheDay: WordOfTheDayRecurringAction) -> str:
        pass
