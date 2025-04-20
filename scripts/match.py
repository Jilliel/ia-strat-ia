from bot.interfaces import LocalInterface, APIInterface
from bot.abstract import AbstractBot

from chartichaud.match import launchServer
from chartichaud.game import Game

from threading import Thread
from time import time

class LocalMatch:
    """
    Crée un match en local
    """
    def __init__(self) -> None:
        self.game = Game()
        self.player1: AbstractBot = None
        self.player2: AbstractBot = None
        self.exectime: float = 0

    def bind(self, bot1: AbstractBot, bot2: AbstractBot) -> None:
        """
        Initialise les deux robots et leur interface.
        """
        interface1 = LocalInterface(game=self.game, player='A')
        self.player1 = bot1(interface1)
        interface2 = LocalInterface(game=self.game, player='B')
        self.player2 = bot2(interface2)

    def run(self) -> None:
        """
        Joue le match entre 
        """
        assert self.player1 is not None
        assert self.player2 is not None

        t1 = time()
        while self.game.winner == "":

            self.player1.reloadView()
            self.player1.startTurn()
            self.player1.playTurn()
            self.player1.endturn()

            if self.game.winner != "":
                break
            
            self.player2.reloadView()
            self.player2.startTurn()
            self.player2.playTurn()
            self.player2.endturn()
    
        t2 = time()
        self.exectime = t2-t1

    def results(self) -> None:
        """
        Affiche les données du match.
        """
        winner = self.game.winner
        looser = 'A' if winner == 'B' else 'B'
        scores = self.game.score
        rounds = self.game.curRound
        print(f"Match ended in {rounds} rounds / {self.exectime} seconds.")
        print(f"Player {winner} won the game with {scores[winner]} points.")
        print(f"Player {looser} lost the game with {scores[looser]} points.")


class APIMatch:
    """
    Crée un match via un serveur web.
    """
    def __init__(self, port="8080") -> None:
        self.game = Thread(target=launchServer, args=(port,))
        self.game.daemon = True
        self.game.start()
        self.player1: AbstractBot = None
        self.player2: AbstractBot = None

    def bind(self, bot1: AbstractBot, bot2: AbstractBot) -> None:
        """
        Initialise les deux robots et leur interface.
        """
        interface1 = APIInterface(host='127.0.0.1', port='8080', name="bot1")
        self.player1 = bot1(interface1)
        interface2 = APIInterface(host='127.0.0.1', port='8080', name="bot2")
        self.player2 = bot2(interface2)
    
    def run(self) -> None:
        """
        Joue le match entre 
        """
        thread1 = Thread(target=self.player1.playMatch)
        thread1.daemon = True
        thread2 = Thread(target=self.player2.playMatch)
        thread2.daemon = True

        # Lance les threads
        thread1.start()
        thread2.start()
        
        # Attend que les threads terminent
        thread1.join()
        thread2.join()
