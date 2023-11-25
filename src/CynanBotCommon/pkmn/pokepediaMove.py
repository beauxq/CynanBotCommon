from typing import Dict, List, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.pkmn.pokepediaContestType import PokepediaContestType
    from CynanBotCommon.pkmn.pokepediaDamageClass import PokepediaDamageClass
    from CynanBotCommon.pkmn.pokepediaGeneration import PokepediaGeneration
    from CynanBotCommon.pkmn.pokepediaMachine import PokepediaMachine
    from CynanBotCommon.pkmn.pokepediaMoveGeneration import \
        PokepediaMoveGeneration
except:
    import utils

    from pkmn.pokepediaContestType import PokepediaContestType
    from pkmn.pokepediaDamageClass import PokepediaDamageClass
    from pkmn.pokepediaGeneration import PokepediaGeneration
    from pkmn.pokepediaMachine import PokepediaMachine
    from pkmn.pokepediaMoveGeneration import PokepediaMoveGeneration


class PokepediaMove():

    def __init__(
        self,
        contestType: Optional[PokepediaContestType],
        damageClass: PokepediaDamageClass,
        generationMachines: Optional[Dict[PokepediaGeneration, List[PokepediaMachine]]],
        generationMoves: Dict[PokepediaGeneration, PokepediaMoveGeneration],
        critRate: int,
        drain: int,
        flinchChance: int,
        moveId: int,
        initialGeneration: PokepediaGeneration,
        description: str,
        name: str,
        rawName: str
    ):
        if contestType is not None and not isinstance(contestType, PokepediaContestType):
            raise ValueError(f'contestType argument is malformed: \"{contestType}\"')
        elif not isinstance(damageClass, PokepediaDamageClass):
            raise ValueError(f'damageClass argument is malformed: \"{damageClass}\"')
        elif not utils.hasItems(generationMoves):
            raise ValueError(f'generationMoves argument is malformed: \"{generationMoves}\"')
        elif not utils.isValidInt(critRate):
            raise ValueError(f'critRate argument is malformed: \"{critRate}\"')
        elif not utils.isValidInt(drain):
            raise ValueError(f'drain argument is malformed: \"{drain}\"')
        elif not utils.isValidInt(flinchChance):
            raise ValueError(f'flinchChance argument is malformed: \"{flinchChance}\"')
        elif not utils.isValidInt(moveId):
            raise ValueError(f'moveId argument is malformed: \"{moveId}\"')
        elif not isinstance(initialGeneration, PokepediaGeneration):
            raise ValueError(f'initialGeneration argument is malformed: \"{initialGeneration}\"')
        elif not utils.isValidStr(description):
            raise ValueError(f'description argument is malformed: \"{description}\"')
        elif not utils.isValidStr(name):
            raise ValueError(f'name argument is malformed: \"{name}\"')
        elif not utils.isValidStr(rawName):
            raise ValueError(f'rawName argument is malformed: \"{rawName}\"')

        self.__contestType: Optional[PokepediaContestType] = contestType
        self.__damageClass: PokepediaDamageClass = damageClass
        self.__generationMachines: Optional[Dict[PokepediaGeneration, List[PokepediaMachine]]] = generationMachines
        self.__generationMoves: Dict[PokepediaGeneration, PokepediaMoveGeneration] = generationMoves
        self.__critRate: int = critRate
        self.__drain: int = drain
        self.__flinchChance: int = flinchChance
        self.__moveId: int = moveId
        self.__initialGeneration: PokepediaGeneration = initialGeneration
        self.__description: str = description
        self.__name: str = name
        self.__rawName: str = rawName

    def getContestType(self) -> Optional[PokepediaContestType]:
        return self.__contestType

    def getCritRate(self) -> int:
        return self.__critRate

    def getDamageClass(self) -> PokepediaDamageClass:
        return self.__damageClass

    def getDescription(self) -> str:
        return self.__description

    def getDrain(self) -> int:
        return self.__drain

    def getFlinchChance(self) -> int:
        return self.__flinchChance

    def getGenerationMachines(self) -> Optional[Dict[PokepediaGeneration, List[PokepediaMachine]]]:
        return self.__generationMachines

    def getGenerationMoves(self) -> Dict[PokepediaGeneration, PokepediaMoveGeneration]:
        return self.__generationMoves

    def getInitialGeneration(self) -> PokepediaGeneration:
        return self.__initialGeneration

    def getMoveId(self) -> int:
        return self.__moveId

    def getName(self) -> str:
        return self.__name

    def getRawName(self) -> str:
        return self.__rawName

    def hasContestType(self) -> bool:
        return self.__contestType is not None

    def hasMachines(self) -> bool:
        return utils.hasItems(self.__generationMachines)

    def toStrList(self) -> List[str]:
        strings: List[str] = list()
        strings.append(f'{self.getName()} — {self.getDescription()}')

        for gen in PokepediaGeneration:
            if gen in self.__generationMoves:
                genMove = self.__generationMoves[gen]
                strings.append(genMove.toStr())

        return strings
