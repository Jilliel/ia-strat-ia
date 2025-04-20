from bot.abstract import AbstractBot
from random import choice

class RandomBot(AbstractBot):
    def __init__(self, interface):
        super().__init__(interface)

    def playTurn(self):
        """
        Joue le tour.
        """
        