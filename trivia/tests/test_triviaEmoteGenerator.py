import asyncio
from asyncio import AbstractEventLoop

import pytest

try:
    from ...backgroundTaskHelper import BackgroundTaskHelper
    from ...storage.backingDatabase import BackingDatabase
    from ...storage.backingSqliteDatabase import BackingSqliteDatabase
    from ...timber.timber import Timber
    from ...trivia.triviaEmoteGenerator import TriviaEmoteGenerator
except:
    from backgroundTaskHelper import BackgroundTaskHelper
    from storage.backingDatabase import BackingDatabase
    from storage.backingSqliteDatabase import BackingSqliteDatabase
    from timber.timber import Timber
    from trivia.triviaEmoteGenerator import TriviaEmoteGenerator


class TestTriviaEmoteGenerator():

    eventLoop: AbstractEventLoop = asyncio.get_event_loop()
    backgroundTaskHelper = BackgroundTaskHelper(eventLoop = eventLoop)
    backingDatabase: BackingDatabase = BackingSqliteDatabase(eventLoop = eventLoop)
    timber: Timber = Timber(backgroundTaskHelper = backgroundTaskHelper)
    triviaEmoteGenerator: TriviaEmoteGenerator = TriviaEmoteGenerator(
        backingDatabase = backingDatabase,
        timber = timber
    )

    @pytest.mark.asyncio
    async def test_getRandomEmote(self):
        for _ in range(100):
            result = self.triviaEmoteGenerator.getRandomEmote()
            assert result is not None
            assert isinstance(result, str)
            assert not result.isspace()
            assert len(result) >= 1
            assert result == await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote(result)

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withAbacus(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🧮')
        assert result is not None
        assert result == '🧮'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withAlembic(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('⚗️')
        assert result is not None
        assert result == '⚗️'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withAlien(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('👽')
        assert result is not None
        assert result == '👽'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withAvocado(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🥑')
        assert result is not None
        assert result == '🥑'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withBabyChick(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🐤')
        assert result is not None
        assert result == '🐦'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withBacon(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🥓')
        assert result is not None
        assert result == '🥓'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withBackpack(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🎒')
        assert result is not None
        assert result == '🎒'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withBanana(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🍌')
        assert result is not None
        assert result == '🍌'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withBarChart(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('📊')
        assert result is not None
        assert result == '📊'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withBellPepper(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🫑')
        assert result is not None
        assert result == '🫑'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withBird(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🐦')
        assert result is not None
        assert result == '🐦'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withBlueberry(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🫐')
        assert result is not None
        assert result == '🫐'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withBooks(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('📚')
        assert result is not None
        assert result == '📚'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withBriefcase(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('💼')
        assert result is not None
        assert result == '💼'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withBus(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🚌')
        assert result is not None
        assert result == '🚌'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withCardIndex(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('📇')
        assert result is not None
        assert result == '📇'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withCarrot(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🥕')
        assert result is not None
        assert result == '🥕'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withCheese(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🧀')
        assert result is not None
        assert result == '🧀'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withCherry(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🍒')
        assert result is not None
        assert result == '🍒'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withClipboard(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('📋')
        assert result is not None
        assert result == '📋'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withCow(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🐄')
        assert result is not None
        assert result == '🐄'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withCowFace(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🐮')
        assert result is not None
        assert result == '🐄'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withCrab(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🦀')
        assert result is not None
        assert result == '🦀'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withCrayon(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🖍️')
        assert result is not None
        assert result == '🖍️'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withCurryRice(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🍛')
        assert result is not None
        assert result == '🍛'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withDna(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🧬')
        assert result is not None
        assert result == '🧬'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withDolphin(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🐬')
        assert result is not None
        assert result == '🐬'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withDragon(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🐉')
        assert result is not None
        assert result == '🐉'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withDragonFace(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🐲')
        assert result is not None
        assert result == '🐉'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withDroplet(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('💧')
        assert result is not None
        assert result == '🌊'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withElephant(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🐘')
        assert result is not None
        assert result == '🐘'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withEmptyString(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('')
        assert result is None

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withFaceWithMonocle(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🧐')
        assert result is not None
        assert result == '🧐'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withFireTruck(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🚒')
        assert result is not None
        assert result == '🚒'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withFriedShrimp(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🍤')
        assert result is not None
        assert result == '🦐'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withFrog(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🐸')
        assert result is not None
        assert result == '🐸'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withGhost(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('👻')
        assert result is not None
        assert result == '👻'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withGrapes(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🍇')
        assert result is not None
        assert result == '🍇'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withGreenApple(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🍏')
        assert result is not None
        assert result == '🍏'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withHelicopter(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🚁')
        assert result is not None
        assert result == '🚁'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withHotPepper(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🌶️')
        assert result is not None
        assert result == '🌶️'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withLedger(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('📒')
        assert result is not None
        assert result == '📒'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withLightBulb(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('💡')
        assert result is not None
        assert result == '💡'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withLion(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🦁')
        assert result is not None
        assert result == '🦁'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withMelon(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🍈')
        assert result is not None
        assert result == '🍈'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withMicroscope(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🔬')
        assert result is not None
        assert result == '🔬'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withMonkey(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🐒')
        assert result is not None
        assert result == '🐒'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withMonkeyFace(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🐵')
        assert result is not None
        assert result == '🐒'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withMushroom(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🍄')
        assert result is not None
        assert result == '🍄'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withNerdFace(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🤓')
        assert result is not None
        assert result == '🤓'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withNewLineString(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('\n')
        assert result is None

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withNone(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withNotebook(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('📓')
        assert result is not None
        assert result == '📓'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withOctopus(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🐙')
        assert result is not None
        assert result == '🦑'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withPaperclip(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('📎')
        assert result is not None
        assert result == '📎'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withPear(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🍐')
        assert result is not None
        assert result == '🍐'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withPenguin(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🐧')
        assert result is not None
        assert result == '🐧'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withPig(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🐖')
        assert result is not None
        assert result == '🐖'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withPigFace(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🐷')
        assert result is not None
        assert result == '🐖'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withPineapple(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🍍')
        assert result is not None
        assert result == '🍍'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withPizza(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🍕')
        assert result is not None
        assert result == '🍕'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withPotato(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🥔')
        assert result is not None
        assert result == '🥔'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withRainbow(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🌈')
        assert result is not None
        assert result == '🌈'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withRedApple(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🍎')
        assert result is not None
        assert result == '🍎'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withRiceBall(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🍙')
        assert result is not None
        assert result == '🍙'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withRoastedSweetPotato(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🍠')
        assert result is not None
        assert result == '🍠'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withRobot(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🤖')
        assert result is not None
        assert result == '🤖'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withRocket(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🚀')
        assert result is not None
        assert result == '🚀'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withSchool(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🏫')
        assert result is not None
        assert result == '🏫'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withShrimp(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🦐')
        assert result is not None
        assert result == '🦐'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withSquid(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🦑')
        assert result is not None
        assert result == '🦑'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withStraightRuler(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('📏')
        assert result is not None
        assert result == '📏'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withStrawberry(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🍓')
        assert result is not None
        assert result == '🍓'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withSweatDroplets(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('💦')
        assert result is not None
        assert result == '🌊'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withTangerine(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🍊')
        assert result is not None
        assert result == '🍊'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withTelescope(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🔭')
        assert result is not None
        assert result == '🔭'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withThinkingFace(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🤔')
        assert result is not None
        assert result == '🤔'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withThoughtBalloon(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('💭')
        assert result is not None
        assert result == '💭'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withTiger(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🐅')
        assert result is not None
        assert result == '🐅'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withTigerFace(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🐯')
        assert result is not None
        assert result == '🐅'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withTriangularRuler(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('📐')
        assert result is not None
        assert result == '📐'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withTulip(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🌷')
        assert result is not None
        assert result == '🌷'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withWatermelon(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🍉')
        assert result is not None
        assert result == '🍈'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withWaterWave(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🌊')
        assert result is not None
        assert result == '🌊'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withWhale(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🐋')
        assert result is not None
        assert result == '🐋'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withWhitespaceString(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote(' ')
        assert result is None

    def test_sanity(self):
        assert self.triviaEmoteGenerator is not None
        assert isinstance(self.triviaEmoteGenerator, TriviaEmoteGenerator)
