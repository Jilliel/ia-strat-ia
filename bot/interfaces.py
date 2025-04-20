from bot.abstract import AbstractInterface
from chartichaud.game import Game
import requests
import json

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


class APIInterface(AbstractInterface):
    """
    Interface faisant des requêtes avec une API pour
    communiquer avec le serveur distant.
    """
    def __init__(self, host: str, port: str, name: str) -> None:
        super().__init__()
        self.adress = host + ':' + port
        self.session = requests.Session()
        # Creates a player in the distant game
        url = f"{self.adress}/getToken/{name}"
        connexion = json.loads(self.session.get(url))
        # Gets the data
        self.token = connexion['token']
        self.player = connexion['player']

    def push(self, url) -> None:
        """
        Pushes some data with a request to the distant host.
        """
        res = self.session.get(url)
        assert res.status_code == 200

    def pull(self, url) -> None:
        """
        Pulls some data with a request to the distant host.
        """
        res = self.session.get(url)
        assert res.status_code == 200
        return json.loads(res.content)
    
    def build(self, pos: position, unit: str) -> None:
        """
        Crée une unité.
        """
        y, x = pos
        url = f"{self.adress}/build/{self.player}/{y}/{x}/{unit}/{self.token}"
        self.push(url)

    def move(self, pos: position, newpos: position, unit: str) -> None:
        """
        Déplace une unité.
        """
        y0, x0 = pos
        y1, x1 = newpos
        url = f"{self.adress}/move/{self.player}/{unit}/{y0}/{x0}/{y1}/{x1}/{self.token}"
        self.push(url)

    def farm(self, pos: position) -> None:
        """
        Récupère de l'or avec un citoyen.
        """
        y, x = pos
        url = f"{self.adress}/farm/{self.player}/{y}/{x}/{self.token}"
        self.push(url)

    def getView(self) -> dict:
        """
        Renvoie les informations disponibles.
        """
        url = f"{self.adress}/view/{self.player}/{self.token}"
        return self.pull(url)
     
    def endturn(self) -> None:
        """
        Termine le tour.
        """
        url = f"{self.adress}/endturn/{self.player}/{self.token}"
        self.push(url)
