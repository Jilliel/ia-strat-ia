from abc import ABC, abstractmethod
from typing import Optional
from enum import Enum
import numpy as np

position = tuple[int, int]

class MoveType(Enum):
    """
    Représente les différents types de coup possibles.
    """

    # Gold
    FARM = 0   
    
    # Move
    MOVE_UP = 1
    MOVE_LEFT = 2
    MOVE_DOWN = 3
    MOVE_RIGHT = 4
    
    # Build
    BUILD_CAS = 5
    BUILD_CIT = 6
    BUILD_MIL = 7


class AbstractInterface(ABC):
    """
    Classe abstraite représentant une interface entre le bot et le jeu.
    """
    def __init__(self):
        self.player = None

    @abstractmethod
    def build(self, pos: position, unit: str) -> None:
        """
        Crée une unité.
        """
        pass
    
    @abstractmethod
    def move(self, pos: position, newpos: position, unit: str) -> None:
        """
        Déplace une unité.
        """
        pass
    
    @abstractmethod
    def farm(self, pos: position) -> None:
        """
        Récupère de l'or avec un citoyen.
        """
        pass
    
    @abstractmethod
    def endturn(self) -> None:
        """
        Termine le tour.
        """
        pass

    @abstractmethod
    def getView(self) -> dict:
        """
        Renvoie les informations disponibles.
        """
        pass
    
    def play(self, move: MoveType, pos: position, unit: Optional[str] = None) -> None:
        """
        Joue le coup passé en argument
        """
        y0, x0 = pos
        match move:
            case MoveType.MOVE_DOWN:
                newpos = y0+1, x0
                self.move(pos, newpos, unit)
            case MoveType.MOVE_LEFT:
                newpos = y0, x0-1
                self.move(pos, newpos, unit)
            case MoveType.MOVE_RIGHT:
                newpos = y0, x0+1
                self.move(pos, newpos, unit)
            case MoveType.MOVE_UP:
                newpos = y0-1, x0
                self.move(pos, newpos, unit)
            case MoveType.FARM:
                self.farm(pos)
            case MoveType.BUILD_CAS:
                self.build(pos, 'B')
            case MoveType.BUILD_CIT:
                self.build(pos, 'C')
            case MoveType.BUILD_MIL:
                self.build(pos, 'M')
            case _:
                raise NotImplementedError


class AbstractBot(ABC):
    def __init__(self, interface):
        self.interface: AbstractInterface = interface
        #Board data
        self.width: int = 0
        self.height: int = 0
        self.golds: dict[str: int] = None
        self.mines: dict[position: int] = {}
        #Match data
        self.player: str = ""
        self.winner: str = ""
        #Unit data
        self.militaries: dict = None
        self.buildings: dict = None
        self.citizens: dict = None

    def getCurrentPlayer(self) -> str:
        """
        Renvoie le joueur actuel
        """
        return self.player
    
    def getAdvPlayer(self) -> str:
        """
        Renvoie l'adversaire.
        """
        return 'A' if self.interface.player == 'B' else 'B'
    
    def getOwnPlayer(self) -> str:
        """
        Renvoie le joueur
        """
        return self.interface.player
    
    def reload(self):
        """
        Met à jour les informations du match.
        """
        view = self.interface.getView()
        player = self.getOwnPlayer()
        adversary = self.getAdvPlayer()
        #Match data
        self.player = view['player']
        self.winner = view['winner']
        #Board data
        self.golds = view['gold']
        self.width = view['width']
        self.height = view['height']
        #Unit data
        self.militaries = {'A': np.zeros(shape=(self.height, self.width), dtype=np.uint),
                           'B': np.zeros(shape=(self.height, self.width), dtype=np.uint)}
        self.buildings = {'A': np.zeros(shape=(self.height, self.width), dtype=np.uint),
                          'B': np.zeros(shape=(self.height, self.width), dtype=np.uint)}
        self.citizens = {'A': np.zeros(shape=(self.height, self.width), dtype=np.uint),
                         'B': np.zeros(shape=(self.height, self.width), dtype=np.uint)}
        
        unitmap = view['map']
        for i in range(self.height):
            for j in range(self.width):
                pos = (i, j)
                unitcase = unitmap[i][j]
                if len(unitcase) == 0:
                    continue
                # own units
                self.militaries[player][pos] = unitcase[player]['M']
                self.buildings[player][pos] = unitcase[player]['B']
                self.citizens[player][pos] = unitcase[player]['C']
                # adv units
                self.militaries[adversary][pos] = unitcase[adversary]['M']
                self.buildings[adversary][pos] = unitcase[adversary]['B']
                self.citizens[adversary][pos] = unitcase[adversary]['C']

    @abstractmethod
    def playTurn(self):
        """
        Joue une tour.
        """
        pass

    def playMatch(self) -> None:
        """
        Joue un match
        """
        while self.winner == "":
            self.reload()
            if self.getOwnPlayer() == self.getCurrentPlayer():
                self.playTurn()
        