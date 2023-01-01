import random
from typing import Any, Dict, List, Set

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.network.exceptions import GenericNetworkException
    from CynanBotCommon.pkmn.pokepediaElementType import PokepediaElementType
    from CynanBotCommon.pkmn.pokepediaGeneration import PokepediaGeneration
    from CynanBotCommon.pkmn.pokepediaMachineType import PokepediaMachineType
    from CynanBotCommon.pkmn.pokepediaRepository import PokepediaRepository
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.absTriviaQuestionRepository import \
        AbsTriviaQuestionRepository
    from CynanBotCommon.trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from CynanBotCommon.trivia.triviaDifficulty import TriviaDifficulty
    from CynanBotCommon.trivia.triviaEmoteGenerator import TriviaEmoteGenerator
    from CynanBotCommon.trivia.triviaExceptions import (
        GenericTriviaNetworkException, MalformedTriviaJsonException,
        UnsupportedTriviaTypeException)
    from CynanBotCommon.trivia.triviaIdGenerator import TriviaIdGenerator
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
    from CynanBotCommon.trivia.triviaSource import TriviaSource
    from CynanBotCommon.trivia.triviaType import TriviaType
    from CynanBotCommon.trivia.trueFalseTriviaQuestion import \
        TrueFalseTriviaQuestion
except:
    import utils
    from network.exceptions import GenericNetworkException
    from timber.timber import Timber
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.absTriviaQuestionRepository import AbsTriviaQuestionRepository
    from trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from trivia.triviaDifficulty import TriviaDifficulty
    from trivia.triviaEmoteGenerator import TriviaEmoteGenerator
    from trivia.triviaExceptions import (GenericTriviaNetworkException,
                                         MalformedTriviaJsonException,
                                         UnsupportedTriviaTypeException)
    from trivia.triviaIdGenerator import TriviaIdGenerator
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaSource import TriviaSource
    from trivia.triviaType import TriviaType
    from trivia.trueFalseTriviaQuestion import TrueFalseTriviaQuestion

    from pkmn.pokepediaElementType import PokepediaElementType
    from pkmn.pokepediaGeneration import PokepediaGeneration
    from pkmn.pokepediaMachineType import PokepediaMachineType
    from pkmn.pokepediaRepository import PokepediaRepository


class PkmnTriviaQuestionRepository(AbsTriviaQuestionRepository):

    def __init__(
        self,
        pokepediaRepository: PokepediaRepository,
        timber: Timber,
        triviaEmoteGenerator: TriviaEmoteGenerator,
        triviaIdGenerator: TriviaIdGenerator,
        triviaSettingsRepository: TriviaSettingsRepository,
        maxGeneration: PokepediaGeneration = PokepediaGeneration.GENERATION_3
    ):
        super().__init__(triviaSettingsRepository)

        if not isinstance(pokepediaRepository, PokepediaRepository):
            raise ValueError(f'pokepediaRepository argument is malformed: \"{pokepediaRepository}\"')
        elif not isinstance(timber, Timber):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(triviaEmoteGenerator, TriviaEmoteGenerator):
            raise ValueError(f'triviaEmoteGenerator argument is malformed: \"{triviaEmoteGenerator}\"')
        elif not isinstance(triviaIdGenerator, TriviaIdGenerator):
            raise ValueError(f'triviaIdGenerator argument is malformed: \"{triviaIdGenerator}\"')
        elif not isinstance(maxGeneration, PokepediaGeneration):
            raise ValueError(f'maxGeneration argument is malformed: \"{maxGeneration}\"')

        self.__pokepediaRepository: PokepediaRepository = pokepediaRepository
        self.__timber: Timber = timber
        self.__triviaEmoteGenerator: TriviaEmoteGenerator = triviaEmoteGenerator
        self.__triviaIdGenerator: TriviaIdGenerator = triviaIdGenerator
        self.__maxGeneration: PokepediaGeneration = maxGeneration

    async def __createMoveIsAvailableAsTmQuestion(self) -> Dict[str, Any]:
        try:
            move = await self.__pokepediaRepository.fetchRandomMove(
                maxGeneration = self.__maxGeneration
            )
        except GenericNetworkException as e:
            self.__timber.log('PkmnTriviaQuestionRepository', f'Encountered network error when fetching trivia question: {e}', e)
            raise GenericTriviaNetworkException(self.getTriviaSource(), e)

        randomGeneration = await self.__selectRandomGeneration(move.getInitialGeneration())

        moveExistsAsTmInThisGeneration = move.hasMachines() and randomGeneration in move.getGenerationMachines()

        if not moveExistsAsTmInThisGeneration or utils.randomBool():
            # only ask if the move simply exists as a TM in the given generation
            return {
                'correctAnswer': move.hasMachines() and randomGeneration in move.getGenerationMachines(),
                'question': f'In Pokémon {randomGeneration.toLongStr()}, {move.getName()} can be taught via TM.',
                'triviaType': TriviaType.TRUE_FALSE
            }

        machine = move.getGenerationMachines()[randomGeneration][0]
        correctMachineNumber = machine.getMachineNumber()
        machinePrefix = machine.getMachineType().getPrefix()

        falseMachineNumbers = await self.__selectRandomFalseMachineNumbers(
            actualMachineNumber = correctMachineNumber,
            actualMachineType = machine.getMachineType()
        )

        falseMachineNumbersStrs: List[str] = list()
        for falseMachineNumber in falseMachineNumbers:
            falseMachineNumbersStrs.append(f'{machinePrefix}{falseMachineNumber}')

        return {
            'correctAnswer': machine.getMachineName(),
            'incorrectAnswers': falseMachineNumbersStrs,
            'question': f'In Pokémon {randomGeneration.toLongStr()}, {move.getName()} can be taught via which TM?',
            'triviaType': TriviaType.MULTIPLE_CHOICE
        }

    async def __createPokemonTypeQuestion(self) -> Dict[str, Any]:
        try:
            pokemon = await self.__pokepediaRepository.fetchRandomPokemon(
                maxGeneration = self.__maxGeneration
            )
        except GenericNetworkException as e:
            self.__timber.log('PkmnTriviaQuestionRepository', f'Encountered network error when fetching trivia question: {e}', e)
            raise GenericTriviaNetworkException(self.getTriviaSource(), e)

        randomGeneration = await self.__selectRandomGeneration(pokemon.getInitialGeneration())

        correctTypes = pokemon.getCorrespondingGenerationElementTypes(randomGeneration)
        correctType = random.choice(correctTypes)

        falseTypes = await self.__selectRandomFalseTypes(correctTypes)

        falseTypesStrs: List[str] = list()
        for falseType in falseTypes:
            falseTypesStrs.append(falseType.toStr())

        return {
            'correctAnswer': correctType.toStr(),
            'incorrectAnswers': falseTypesStrs,
            'question': f'In Pokémon {randomGeneration.toLongStr()}, {pokemon.getName()} is ONE of the following types?',
            'triviaType': TriviaType.MULTIPLE_CHOICE
        }

    async def fetchTriviaQuestion(self, twitchChannel: str) -> AbsTriviaQuestion:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        self.__timber.log('PkmnTriviaQuestionRepository', f'Fetching trivia question... (twitchChannel={twitchChannel})')

        randomTriviaType = random.randint(0, 1)
        triviaDict: Dict[str, Any] = None

        if randomTriviaType == 0:
            triviaDict = await self.__createMoveIsAvailableAsTmQuestion()
        elif randomTriviaType == 1:
            triviaDict = await self.__createPokemonTypeQuestion()
        else:
            raise ValueError(f'PkmnTriviaQuestionRepository\'s randomTriviaType value is out of bounds: \"{randomTriviaType}\"!')

        if not utils.hasItems(triviaDict):
            raise MalformedTriviaJsonException(f'PkmnTriviaQuestionRepository\'s triviaDict is null/empty: \"{triviaDict}\"!')

        category = 'Pokémon'
        triviaDifficulty = TriviaDifficulty.UNKNOWN
        triviaType: TriviaType = triviaDict['triviaType']
        emote = await self.__triviaEmoteGenerator.getNextEmoteFor(twitchChannel)
        question = utils.getStrFromDict(triviaDict, 'question')

        triviaId = await self.__triviaIdGenerator.generate(
            question = question,
            category = category,
            difficulty = triviaDifficulty.toStr()
        )

        if triviaType is TriviaType.MULTIPLE_CHOICE:
            correctAnswers: List[str] = list()
            correctAnswers.append(utils.getStrFromDict(triviaDict, 'correctAnswer'))
            incorrectAnswers: List[str] = triviaDict['incorrectAnswers']

            multipleChoiceResponses = await self._buildMultipleChoiceResponsesList(
                correctAnswers = correctAnswers,
                multipleChoiceResponses = incorrectAnswers
            )

            return MultipleChoiceTriviaQuestion(
                correctAnswers = correctAnswers,
                multipleChoiceResponses = multipleChoiceResponses,
                category = category,
                categoryId = None,
                emote = emote,
                question = question,
                triviaId = triviaId,
                triviaDifficulty = triviaDifficulty,
                triviaSource = TriviaSource.POKE_API
            )
        elif triviaType is TriviaType.TRUE_FALSE:
            correctAnswers: List[bool] = list()
            correctAnswers.append(utils.getBoolFromDict(triviaDict, 'correctAnswer'))

            return TrueFalseTriviaQuestion(
                correctAnswers = correctAnswers,
                category = category,
                categoryId = None,
                emote = emote,
                question = question,
                triviaId = triviaId,
                triviaDifficulty = triviaDifficulty,
                triviaSource = TriviaSource.POKE_API
            )

        raise UnsupportedTriviaTypeException(f'triviaType \"{triviaType}\" is not supported for Pkmn Trivia: {triviaDict}')

    def getSupportedTriviaTypes(self) -> List[TriviaType]:
        return [ TriviaType.MULTIPLE_CHOICE, TriviaType.TRUE_FALSE ]

    def getTriviaSource(self) -> TriviaSource:
        return TriviaSource.POKE_API

    async def __selectRandomFalseTypes(
        self,
        actualTypes: List[PokepediaElementType]
    ) -> Set[PokepediaElementType]:
        if not utils.hasItems(actualTypes):
            raise ValueError(f'actualTypes argument is malformed: \"{actualTypes}\"')

        allTypes = list(PokepediaElementType)
        falseTypes: Set[PokepediaElementType] = set()

        minResponses = await self._triviaSettingsRepository.getMinMultipleChoiceResponses()
        maxResponses = await self._triviaSettingsRepository.getMaxMultipleChoiceResponses()
        responses = random.randint(minResponses, maxResponses)

        while len(falseTypes) < responses:
            randomType = random.choice(allTypes)

            if randomType not in actualTypes and randomType is not PokepediaElementType.UNKNOWN:
                falseTypes.add(randomType)

        return falseTypes

    async def __selectRandomFalseMachineNumbers(
        self,
        actualMachineNumber: int,
        actualMachineType: PokepediaMachineType
    ) -> Set[int]:
        if not utils.isValidInt(actualMachineNumber):
            raise ValueError(f'actualMachineNumber argument is malformed: \"{actualMachineNumber}\"')
        elif not isinstance(actualMachineType, PokepediaMachineType):
            raise ValueError(f'actualMachineType argument is malformed: \"{actualMachineType}\"')

        falseMachineNumbers: Set[int] = set()

        minResponses = await self._triviaSettingsRepository.getMinMultipleChoiceResponses()
        maxResponses = await self._triviaSettingsRepository.getMaxMultipleChoiceResponses()
        responses = random.randint(minResponses, maxResponses)

        maxMachineNumber: int = None
        if actualMachineType is PokepediaMachineType.HM:
            maxMachineNumber = 12
        elif actualMachineType is PokepediaMachineType.TM:
            maxMachineNumber = 112
        elif actualMachineType is PokepediaMachineType.TR:
            maxMachineNumber = 90
        else:
            raise ValueError(f'Can\'t determine `maxMachineNumber` due to unknown PokepediaMachineType: \"{actualMachineType}\"!')

        while len(falseMachineNumbers) < responses:
            randomInt = random.randint(1, maxMachineNumber)

            if randomInt != actualMachineNumber:
                falseMachineNumbers.add(randomInt)

        return falseMachineNumbers

    async def __selectRandomGeneration(self, initialGeneration: PokepediaGeneration) -> PokepediaGeneration:
        if not isinstance(initialGeneration, PokepediaGeneration):
            raise ValueError(f'initialGeneration argument is malformed: \"{initialGeneration}\"')

        allGenerations = list(PokepediaGeneration)
        indexOfMax = allGenerations.index(self.__maxGeneration)
        indexOfMin = allGenerations.index(initialGeneration)

        if indexOfMax < indexOfMin:
            raise RuntimeError(f'indexOfMax ({indexOfMax}) or indexOfMin ({indexOfMin}) is incompatible with an initial generation of {initialGeneration}! (maxGeneration={self.__maxGeneration}))')

        return allGenerations[random.randint(indexOfMin, indexOfMax)]