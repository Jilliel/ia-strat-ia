from bot.abstract import AbstractBot
from random import choice, shuffle

class RandomBot(AbstractBot):
    def __init__(self, interface):
        super().__init__(interface)

    def playTurn(self):
        """
        Joue le tour.
        """
        
        # On récupère toutes les unités
        allunits = []
        for unit in ('C', 'M', 'B'):
            units = self.getUnits(player=self.ownplayer, unit=unit)
            for pos, value in units.items():
                for _ in range(value):
                    allunits.append((pos, unit))
        shuffle(allunits)

        # On fait agir tout le monde
        while len(allunits) > 0:
            pos, unit = allunits.pop()
            moves = self.getAvailableMove(pos=pos, unit=unit)
            self.play(move=choice(moves),
                      pos=pos,
                      unit=unit)
        
        
