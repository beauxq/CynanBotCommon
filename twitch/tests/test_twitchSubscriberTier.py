from typing import Optional

try:
    from ..twitchSubscriberTier import TwitchSubscriberTier
except:
    from twitch.twitchSubscriberTier import TwitchSubscriberTier


class TestTwitchSubscriberTier():

    def test_fromStr_with1000String(self):
        result = TwitchSubscriberTier.fromStr('1000')
        assert result is TwitchSubscriberTier.TIER_ONE

    def test_fromStr_with2000String(self):
        result = TwitchSubscriberTier.fromStr('2000')
        assert result is TwitchSubscriberTier.TIER_TWO

    def test_fromStr_with3000String(self):
        result = TwitchSubscriberTier.fromStr('3000')
        assert result is TwitchSubscriberTier.TIER_THREE

    def test_fromStr_withEmptyString(self):
        result: Optional[TwitchSubscriberTier] = None
        exception: Optional[Exception] = None

        try:
            result = TwitchSubscriberTier.fromStr('')
        except Exception as e:
            exception = e

        assert result is None
        assert exception is not None
        assert isinstance(exception, ValueError)

    def test_fromStr_withNone(self):
        result: Optional[TwitchSubscriberTier] = None
        exception: Optional[Exception] = None

        try:
            result = TwitchSubscriberTier.fromStr('')
        except Exception as e:
            exception = e

        assert result is None
        assert exception is not None
        assert isinstance(exception, ValueError)

    def test_fromStr_withWhitespaceString(self):
        result: Optional[TwitchSubscriberTier] = None
        exception: Optional[Exception] = None

        try:
            result = TwitchSubscriberTier.fromStr('')
        except Exception as e:
            exception = e

        assert result is None
        assert exception is not None
        assert isinstance(exception, ValueError)
