# Hanabi actions and errors


class HanabiError(Exception):
    """Generic Hanabi event: e.g., invalid actions, play errors, common exceptions."""

    def __init__(self, msg=None, is_game_error=None):
        self.msg = msg
        self.is_game_error = is_game_error


class CardError(HanabiError):
    """A pile is emptied: e.g. no more card in hand."""

    def __init__(self, msg=None):
        if msg is None:
            msg = "No more cards in this stack."
        super().__init__(msg, is_game_error=False)


class EmptyDeck(HanabiError):
    """A deck is finished. Triggers last turn."""

    def __init__(self, msg=None):
        if msg is None:
            msg = "No more cards in deck."
        super().__init__(msg, is_game_error=False)


class InvalidActionError(HanabiError):
    """An invalid Hanabi action. Does not decrement the error counter."""

    def __init__(self, msg=None):
        if msg is None:
            msg = "Invalid Hanabi action."
        super().__init__(msg, is_game_error=False)


class WrongPlayError(HanabiError):
    """A wrong play. Decrements the error counter, however it is a valid action."""

    def __init__(self, msg=None):
        if msg is None:
            msg = "Wrong Hanabi action!"
        super().__init__(msg, is_game_error=True)


class CompletedPile(HanabiError):
    """A pile has been completed."""

    def __init__(self, msg=None):
        if msg is None:
            msg = "A pile has been completed."
        super().__init__(msg, is_game_error=False)
