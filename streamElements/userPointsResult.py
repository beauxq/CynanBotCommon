try:
    import CynanBotCommon.utils as utils
except:
    import utils


class UserPointsResult():

    def __init__(
        self,
        jsonResponse
    ):
        # temporary
        self.jsonResponse = jsonResponse
