try:
    from ...trivia.bannedWords.bannedPhrase import BannedPhrase
    from ...trivia.bannedWords.bannedWordType import BannedWordType
except:
    from trivia.bannedWords.bannedPhrase import BannedPhrase
    from trivia.bannedWords.bannedWordType import BannedWordType


class TestBannedPhrase():

    def test_equals_withDifferentWords(self):
        one = BannedPhrase('cat')
        two = BannedPhrase('dog')
        assert one != two

    def test_equals_withSameWords(self):
        one = BannedPhrase('hello')
        two = BannedPhrase('hello')
        assert one == two

    def test_hash_withDifferentWords(self):
        one = BannedPhrase('cat')
        two = BannedPhrase('dog')
        assert hash(one) != hash(two)

    def test_hash_withSameWords(self):
        one = BannedPhrase('hello')
        two = BannedPhrase('hello')
        assert hash(one) == hash(two)

    def test_getType(self):
        phrase = BannedPhrase('hello')
        assert phrase.getType() is BannedWordType.PHRASE
