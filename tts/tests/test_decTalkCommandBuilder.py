import pytest

try:
    from ...contentScanner.bannedWordsRepository import BannedWordsRepository
    from ...contentScanner.bannedWordsRepositoryInterface import \
        BannedWordsRepositoryInterface
    from ...contentScanner.contentScanner import ContentScanner
    from ...contentScanner.contentScannerInterface import \
        ContentScannerInterface
    from ...emojiHelper.emojiHelper import EmojiHelper
    from ...emojiHelper.emojiHelperInterface import EmojiHelperInterface
    from ...emojiHelper.emojiRepository import EmojiRepository
    from ...emojiHelper.emojiRepositoryInterface import \
        EmojiRepositoryInterface
    from ...storage.jsonStaticReader import JsonStaticReader
    from ...storage.linesStaticReader import LinesStaticReader
    from ...timber.timberInterface import TimberInterface
    from ...timber.timberStub import TimberStub
    from ...tts.ttsSettingsRepository import TtsSettingsRepository
    from ...tts.ttsSettingsRepositoryInterface import \
        TtsSettingsRepositoryInterface
    from ..decTalk.decTalkCommandBuilder import DecTalkCommandBuilder
    from ..ttsCommandBuilderInterface import TtsCommandBuilderInterface
except:
    from contentScanner.bannedWordsRepository import BannedWordsRepository
    from contentScanner.bannedWordsRepositoryInterface import \
        BannedWordsRepositoryInterface
    from contentScanner.contentScanner import ContentScanner
    from contentScanner.contentScannerInterface import ContentScannerInterface
    from emojiHelper.emojiHelper import EmojiHelper
    from emojiHelper.emojiHelperInterface import EmojiHelperInterface
    from emojiHelper.emojiRepository import EmojiRepository
    from emojiHelper.emojiRepositoryInterface import EmojiRepositoryInterface
    from storage.jsonStaticReader import JsonStaticReader
    from storage.linesStaticReader import LinesStaticReader
    from timber.timberInterface import TimberInterface
    from timber.timberStub import TimberStub
    from tts.decTalk.decTalkCommandBuilder import DecTalkCommandBuilder
    from tts.ttsCommandBuilderInterface import TtsCommandBuilderInterface
    from tts.ttsSettingsRepository import TtsSettingsRepository
    from tts.ttsSettingsRepositoryInterface import \
        TtsSettingsRepositoryInterface


class TestDecTalkCommandBuilder():

    timber: TimberInterface = TimberStub()

    bannedWordsRepository: BannedWordsRepositoryInterface = BannedWordsRepository(
        bannedWordsLinesReader = LinesStaticReader(
            lines = [ 'hydroxychloroquine' ]
        ),
        timber = timber
    )

    contentScanner: ContentScannerInterface = ContentScanner(
        bannedWordsRepository = bannedWordsRepository,
        timber = timber
    )

    emojiRepository: EmojiRepositoryInterface = EmojiRepository(
        emojiJsonReader = JsonStaticReader(
            jsonContents = {
                'emojis': [
                    {
                        'code': [
                            "1F600"
                        ],
                        'emoji': '😀',
                        'name': 'grinning face',
                        'category': 'Smileys & Emotion',
                        'subcategory': 'face-smiling',
                        'support': {
                            'apple': True,
                            'google': True,
                            'windows': True
                        }
                    },
                    {
                        'code': [
                            "1F988"
                        ],
                        'emoji': '🦈',
                        'name': 'shark',
                        'category': 'Animals & Nature',
                        'subcategory': 'animal-marine',
                        'support': {
                            'apple': True,
                            'google': True,
                            'windows': True
                        }
                    }
                ]
            }
        ),
        timber = timber
    )

    emojiHelper: EmojiHelperInterface = EmojiHelper(
        emojiRepository = emojiRepository
    )

    ttsSettingsRepository: TtsSettingsRepositoryInterface = TtsSettingsRepository(
        settingsJsonReader = JsonStaticReader(
            jsonContents = {
                'isEnabled': True
            }
        )
    )

    decTalkCommandBuilder: TtsCommandBuilderInterface = DecTalkCommandBuilder(
        contentScanner = contentScanner,
        emojiHelper = emojiHelper,
        timber = timber,
        ttsSettingsRepository = ttsSettingsRepository
    )

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withEmptyString(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('')
        assert result is None

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withBannedWord(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('have you tried hydroxychloroquine?')
        assert result is None

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withCheerText(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('cheer100 hello world')
        assert result == 'hello world'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withCommaPauseInlineCommand(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('hello world [:comma 50]')
        assert result == 'hello world'

        result = await self.decTalkCommandBuilder.buildAndCleanMessage('hello world [:cp 1000,10000] blah')
        assert result == 'hello world blah'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withDangerousCharactersString(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('& cd C:\\ & dir')
        assert result == 'cd C:\\ dir'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withDecTalkFlagsString1(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('-post hello')
        assert result == 'hello'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withDecTalkFlagsString2(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('-pre hello')
        assert result == 'hello'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withDecTalkFlagsString3(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('-l hello')
        assert result == 'hello'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withDecTalkFlagsString4(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('-lw hello')
        assert result == 'hello'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withDecTalkFlagsString5(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('-l[t] hello')
        assert result == 'hello'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withDecTalkFlagsString6(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('-v show version information')
        assert result == 'show version information'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withDecTalkFlagsString7(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('-d userDict')
        assert result == 'userDict'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withDecTalkFlagsString8(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('-lang uk hello world')
        assert result == 'hello world'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withDesignVoiceInlineCommand(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('hello world [:dv] qwerty')
        assert result == 'hello world qwerty'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withDirectoryTraversalString(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('& cd .. & dir')
        assert result == 'cd dir'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withEmojiString(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('shark 🦈 shark 😀 🤔')
        assert result == 'shark shark shark grinning face'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withErrorInlineCommand(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('hello world [:error] qwerty')
        assert result == 'hello world qwerty'

        result = await self.decTalkCommandBuilder.buildAndCleanMessage('azerty   [:erro C:\\log.txt]  qwerty ')
        assert result == 'azerty qwerty'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withExtraneousSpacesString(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('  Hello,    World! ')
        assert result == 'Hello, World!'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withHelloWorldString(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('Hello, World!')
        assert result == 'Hello, World!'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withLogInlineCommand(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('apple [:log] google')
        assert result == 'apple google'

        result = await self.decTalkCommandBuilder.buildAndCleanMessage(' microsoft[:log C:\\log.txt]  twitch ')
        assert result == 'microsoft twitch'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withModeInlineCommand(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('KEKW [:mode 7] LUL')
        assert result == 'KEKW LUL'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withNone(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withPeriodPauseInlineCommand(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('apple [:period] google')
        assert result == 'apple google'

        result = await self.decTalkCommandBuilder.buildAndCleanMessage('oatsngoats[:peri 123]imyt')
        assert result == 'oatsngoats imyt'

        result = await self.decTalkCommandBuilder.buildAndCleanMessage('[:pp]')
        assert result is None

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withPitchInlineCommand(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('[:pitch] hello')
        assert result == 'hello'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withPlayInlineCommand(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('[:play \"C:\\song.wav\"]')
        assert result is None

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withSyncInlineCommand(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('time to [:sync 1] ok')
        assert result == 'time to ok'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withToneInlineCommand(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('this is a tone inline command [:tone]')
        assert result == 'this is a tone inline command'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withUniText(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('hello world uni5')
        assert result == 'hello world'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withWildNestedInlineCommands(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('hello [[[:play \"C:\\song.wav\"]:volume set 10]: dv qwerty] [:pitch 10] world uni5')
        assert result == 'hello world'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withVolumeInlineCommand(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('this is a volume inline command [:vol set 99]')
        assert result == 'this is a volume inline command'

        result = await self.decTalkCommandBuilder.buildAndCleanMessage('[:volume something]1')
        assert result == '1'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withWhitespaceString(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage(' ')
        assert result is None
