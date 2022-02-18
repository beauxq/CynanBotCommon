from datetime import datetime, timezone

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class SimpleDateTime():

    def __init__(
        self,
        useLocalTime: bool = False
    ):
        if not utils.isValidBool(useLocalTime):
            raise ValueError(f'useLocalTime argument is malformed: \"{useLocalTime}\"')

        now: datetime = None
        if useLocalTime:
            now = datetime.now()
        else:
            now = datetime.now(timezone.utc)

        self.__year: str = now.strftime('%Y')
        self.__month: str = now.strftime('%m')
        self.__day: str = now.strftime('%d')
        self.__hour: str = now.strftime('%H')
        self.__minute: str = now.strftime('%M')
        self.__second: str = now.strftime('%S')

    def getDate(self) -> str:
        return f'{self.getYear()}/{self.getMonth()}/{self.getDay()}'

    def getDateAndTime(self) -> str:
        return f'{self.getDate()} {self.getTime()}'

    def getDay(self) -> str:
        return self.__day

    def getHour(self) -> str:
        return self.__hour

    def getMinute(self) -> str:
        return self.__minute

    def getMonth(self) -> str:
        return self.__month

    def getSecond(self) -> str:
        return self.__second

    def getTime(self) -> str:
        return f'{self.getHour()}:{self.getMinute()}:{self.getSecond()}'

    def getYear(self) -> str:
        return self.__year