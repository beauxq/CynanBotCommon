from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict

try:
    from CynanBotCommon.trivia.triviaSource import TriviaSource
except:
    from trivia.triviaSource import TriviaSource


class TriviaErrorDict():

    def __init__(self, fallOffTimeDelta: timedelta = timedelta(hours = 1)):
        if fallOffTimeDelta is None:
            raise ValueError(f'fallOffTimeDelta argument is malformed: \"{fallOffTimeDelta}\"')

        self.__fallOffTimeDelta: timedelta = fallOffTimeDelta
        self.__times: Dict[TriviaSource, datetime] = dict()
        self.__values: Dict[TriviaSource, int] = defaultdict(lambda: 0)

    def __delitem__(self, key: TriviaSource):
        raise RuntimeError(f'this method is not supported for TriviaErrorDict')

    def __getitem__(self, key: TriviaSource) -> int:
        if key is None or not isinstance(key, TriviaSource):
            raise ValueError(f'key argument is malformed: \"{key}\"')

        now = datetime.now(timezone.utc)
        lastErrorTime = self.__times.get(key, None)

        if lastErrorTime is not None and now - lastErrorTime <= self.__fallOffTimeDelta:
            return self.__values[key]

        self.__values[key] = 0
        return 0

    def incrementErrorCount(self, key: TriviaSource) -> int:
        if key is None or not isinstance(key, TriviaSource):
            raise ValueError(f'key argument is malformed: \"{key}\"')

        now = datetime.now(timezone.utc)
        lastErrorTime = self.__times.get(key, None)
        self.__times[key] = now
        newErrorCount: int = 0

        if lastErrorTime is not None and now - lastErrorTime <= self.__fallOffTimeDelta:
            newErrorCount = self.__values[key] + 1
            self.__values[key] = newErrorCount
        else:
            newErrorCount = 1
            self.__values[key] = newErrorCount

        return newErrorCount

    def __setitem__(self, key: TriviaSource, value: int):
        raise RuntimeError(f'this method is not supported for TriviaErrorDict')