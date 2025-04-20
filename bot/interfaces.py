from bot.abstract import AbstractInterface
from chartichaud.game import Game

position = tuple[int, int]

class LocalInterface(AbstractInterface):
    """
    Interface locale entre le jeu et le bot.
    """
    def __init__(self, game: Game, player: str, ) -> None:
        super().__init__()
        self.game = game
        self.player = player

    def build(self, pos: position, unit: str) -> None:
        """
        Crée une unité.
        """
        assert self.player == self.game.curPlayer
        self.game.build(*pos, unit)
    
    def move(self, pos: position, newpos: position, unit: str) -> None:
        """
        Déplace une unité.
        """
        assert self.player == self.game.curPlayer
        self.game.move(unit, *pos, *newpos)
    
    def farm(self, pos: position) -> None:
        """
        Récupère de l'or avec un citoyen.
        """
        assert self.player == self.game.curPlayer
        self.game.farm(*pos)

    def getView(self) -> dict:
        """
        Renvoie les informations disponibles.
        """
        return self.game.giveViewPlayer(self.player)
     
    def endturn(self) -> None:
        """
        Termine le tour.
        """
        assert self.player == self.game.curPlayer
        self.game.changeturn()