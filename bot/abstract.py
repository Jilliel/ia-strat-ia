from abc import ABC, abstractmethod
from typing import Optional
from enum import Enum

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
    def view(self) -> dict:
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

    def playTurn(self):
        """
        
        """