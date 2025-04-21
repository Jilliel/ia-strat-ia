from abc import ABC, abstractmethod
import scripts.utils as utils
from typing import Optional
from enum import Enum
import numpy as np

position = tuple[int, int]

class MoveType(Enum):
    """
    Représente les différents types de coup possibles.
    """

    # Null
    NULL = 0

    # Gold
    FARM = 1
    
    # Move
    MOVE_UP = 2
    MOVE_LEFT = 3
    MOVE_DOWN = 4
    MOVE_RIGHT = 5

    # Build
    BUILD_CAS = 6
    BUILD_CIT = 7
    BUILD_MIL = 8


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
    
    def play(self, move: MoveType, pos: position, unit: Optional[str]) -> None:
        """
        Joue le coup passé en argument
        """
        y0, x0 = pos
        match move:
            case MoveType.NULL:
                return
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
    def __init__(self, interface: AbstractInterface):
        self.interface: AbstractInterface = interface
        self.ownplayer = self.interface.player
        self.advplayer = 'A' if self.ownplayer == 'B' else 'B'
        #Board data
        self.width: int = 0
        self.height: int = 0
        self.gold: int = 0
        #Match data
        self.current: str = ""
        self.winner: str = ""
        self.farmed: list[position] = []
        #Unit data
        self.mines: np.ndarray = None
        self.militaries: dict[str: np.ndarray] = None
        self.buildings: dict[str: np.ndarray] = None
        self.citizens: dict[str: np.ndarray] = None
        #Global data
        self.costs = {'B': 15, 'M': 10, 'C': 5}

    def play(self, move: MoveType, pos: position, unit: Optional[str] = None) -> None:
        """
        Joue un coup.
        """
        if move == MoveType.FARM:
            self.farmed.append(pos)
        self.interface.play(move, pos, unit)
        self.reloadView()

    def endturn(self) -> None:
        """
        Termine le tour.
        """
        self.interface.endturn()

    def getAvailableMove(self, pos: position, unit: str) -> list[MoveType]:
        """
        Renvoie la liste des coups autorisés pour une unité donnée.
        """
        available = [MoveType.NULL]
        if unit == 'C':
            if self.gold >= self.costs['B'] and self.buildings[self.ownplayer][pos] + self.buildings[self.advplayer][pos] == 0:
                available.append(MoveType.BUILD_CAS)
            if self.mines[pos] > 0 and pos not in self.farmed:
                available.append(MoveType.FARM)

        if unit == 'B':
            if self.gold >= self.costs['C']:
                available.append(MoveType.BUILD_CIT)
            if self.gold >= self.costs['M']:
                available.append(MoveType.BUILD_MIL)

        else:
            y, x = pos
            if y > 0:
                available.append(MoveType.MOVE_UP)
            if y < self.height - 1:
                available.append(MoveType.MOVE_DOWN)
            if x > 0:
                available.append(MoveType.MOVE_LEFT)
            if x < self.width - 1:
                available.append(MoveType.MOVE_RIGHT)
            
        return available
    
    def getUnits(self, player: str, unit: str):
        """
        Renvoie un dictionnaire des unités 
        """
        match unit:
            case 'M':
                map = self.militaries[player] 
                units = utils.nonzero(map)
            case 'B':
                map = self.buildings[player]
                units = utils.nonzero(map)
            case 'C':
                map = self.citizens[player]
                units = utils.nonzero(map)
            case _:
                raise Exception(f"The unit {unit} does not exist.")
        return units

    def reloadView(self) -> None:
        """
        Met à jour les informations du match.
        """
        view = self.interface.getView()
        #Match data
        self.current = view['player']
        self.winner = view['winner']
        #Board data
        self.gold = view['gold'][self.ownplayer]
        self.width = view['width']
        self.height = view['height']
        #Unit data
        self.militaries = {'A': np.zeros(shape=(self.height, self.width), dtype=np.uint),
                           'B': np.zeros(shape=(self.height, self.width), dtype=np.uint)}
        self.buildings = {'A': np.zeros(shape=(self.height, self.width), dtype=np.uint),
                          'B': np.zeros(shape=(self.height, self.width), dtype=np.uint)}
        self.citizens = {'A': np.zeros(shape=(self.height, self.width), dtype=np.uint),
                         'B': np.zeros(shape=(self.height, self.width), dtype=np.uint)}
        self.mines = np.zeros(shape=(self.height, self.width), dtype=np.uint)

        for i in range(self.height):
            for j in range(self.width):
                pos = (i, j)
                unitcase = view['map'][i][j]
                if len(unitcase) == 0:
                    continue

                # gold mine
                if unitcase['G'] > 0 and self.mines[pos] == 0:
                    self.mines[self.height-i-1, self.width-j-1] = unitcase['G']
                self.mines[pos] = unitcase['G']

                # own units
                self.militaries[self.ownplayer][pos] = unitcase[self.ownplayer]['M']
                self.buildings[self.ownplayer][pos] = unitcase[self.ownplayer]['B']
                self.citizens[self.ownplayer][pos] = unitcase[self.ownplayer]['C']
                # adv units
                self.militaries[self.advplayer][pos] = unitcase[self.advplayer]['M']
                self.buildings[self.advplayer][pos] = unitcase[self.advplayer]['B']
                self.citizens[self.advplayer][pos] = unitcase[self.advplayer]['C']

        self.newturn = False

    def startTurn(self) -> None: 
        """
        Commence le tour de jeu.
        """
        self.farmed.clear()

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
            if self.ownplayer == self.current:
                self.startTurn()
                self.playTurn()
                self.endturn()
            self.reloadView()