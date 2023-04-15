import locale

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.cuteness.cutenessEntry import CutenessEntry
except:
    import utils
    from cuteness.cutenessEntry import CutenessEntry


class CutenessLeaderboardEntry(CutenessEntry):

    def __init__(
        self,
        cuteness: int,
        rank: int,
        userId: str,
        userName: str
    ):
        super().__init__(
            cuteness = cuteness,
            userId = userId,
            userName = userName
        )

        if not utils.isValidInt(rank):
            raise ValueError(f'rank argument is malformed: \"{rank}\"')
        elif rank < 1 or rank > utils.getLongMaxSafeSize():
            raise ValueError(f'rank argument is out of bounds: {rank}')

        self.__rank: int = rank

    def getRank(self) -> int:
        return self.__rank

    def getRankStr(self) -> str:
        return locale.format_string("%d", self.__rank, grouping = True)
