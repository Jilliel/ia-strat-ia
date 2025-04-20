from math import ceil
import random
from collections import defaultdict
from copy import deepcopy


class Game:
    def __init__(self):
        self.dirs = [ (1,0),(0,1),(-1,0),(0,-1)]
        self.players = []

        # default game parameters
        self.MAX_NB_ROUNDS = 300
        self.MAP_WIDTH = 16
        self.MAP_HEIGHT = 9
        self.NB_GOLD_SPOTS = 15
        self.price = { 'C':5, 'M':10, 'B':15 } # the self.price of each unit
        self.requires = {'C':'B', 'M': 'B', 'B':'C' } # what do we need to build
        self.opponent = { 'A':'B', 'B':'A' }

        #defines an empty map
        self.mapdata = [ ]
        for y in range(self.MAP_HEIGHT):
            self.mapdata.append([])
            for x in range(self.MAP_WIDTH):
                self.mapdata[-1].append({'G':0,'A':{'C':0,'M':0,'B':0},'B':{'C':0,'M':0,'B':0}})
                
        # initial state
        self.winner = ''
        self.curPlayer = 'A' # initial player
        self.gold = {'A':25,'B':25} # initial gold
        self.mapdata[0][0]['A']['C'] = 3 # initial units of A
        self.mapdata[-1][-1]['B']['C'] = 3 # initial units of B


        #set the initial gold reserves
        for i in range(self.NB_GOLD_SPOTS):
            x = random.randint(0,self.MAP_WIDTH-1)
            y = random.randint(0,self.MAP_HEIGHT-1)
            n = random.randint(1,12)
            self.mapdata[y][x]['G'] += n*n
            self.mapdata[self.MAP_HEIGHT-1-y][self.MAP_WIDTH-1-x]['G'] += n*n

        self.matchData = []
        self.score = {'A': 0, 'B': 0}
        self.curRound = 0

        # initialize moves for the first turn
        self.nbMoves = defaultdict(int)
        self.farmed = set()

    def getVisibility(self,player):
        visible = set()
        for y in range(0,self.MAP_HEIGHT):
            for x in range(0,self.MAP_WIDTH):
                if self.mapdata[y][x][player]['C']+self.mapdata[y][x][player]['M']+self.mapdata[y][x][player]['B']>0:
                    for dx in range(-2,3):
                        for dy in range(-2,3):
                            visible.add((y+dy,x+dx))
        return visible

    def giveAllView(self):
        return {'map':self.mapdata,
                'gold':self.gold,
                'player':self.curPlayer,
                'height':self.MAP_HEIGHT,
                'width':self.MAP_WIDTH,
                'score':self.score,
                'viewA': {str(y)+"_"+str(x):1 for (y,x) in self.getVisibility('A')},
                'viewB': {str(y)+"_"+str(x):1 for (y,x) in self.getVisibility('B')},
                'winner': self.winner}

    def giveViewPlayer(self,player):
        mapView = [ [ {} for x in range(self.MAP_WIDTH)] for y in range(self.MAP_HEIGHT) ]
        visible = self.getVisibility(player)
        if len(visible) == 0:
            self.winner = self.opponent[player]
        for y in range(0,self.MAP_HEIGHT):
            for x in range(0,self.MAP_WIDTH):
                if (y,x) in visible:
                    mapView[y][x] = self.mapdata[y][x]
                    for k in ['C','M','B']:
                        if k+"m" in mapView[y][x][self.curPlayer]:
                            mapView[y][x][self.curPlayer].pop(k+"m")
                        if self.nbMoves[(y,x,self.curPlayer,k)] < mapView[y][x][self.curPlayer][k]:
                            mapView[y][x][self.curPlayer][k+"m"] = True

        data = {'map':mapView,
                'gold':{player: self.gold[player]},
                'player':self.curPlayer,
                'height':self.MAP_HEIGHT,
                'width':self.MAP_WIDTH,
                'score': self.score,
                'winner': self.winner}
        return data
    

    def move(self,kind,y,x,ny,nx):
        assert(abs(x-nx)+abs(y-ny)==1)
        assert( 0 <= nx < self.MAP_WIDTH and 0 <= ny < self.MAP_HEIGHT)
        assert( 0 <= x < self.MAP_WIDTH and 0 <= y < self.MAP_HEIGHT)
        assert(self.mapdata[y][x][self.curPlayer][kind]>0) # useless because of next line ?
        assert(self.nbMoves[(y,x,self.curPlayer,kind)] < self.mapdata[y][x][self.curPlayer][kind])
        self.nbMoves[(ny,nx,self.curPlayer,kind)] += 1
        self.mapdata[y][x][self.curPlayer][kind]-=1
        self.mapdata[ny][nx][self.curPlayer][kind]+=1
        return "ok"


    def build(self,y,x,kind):
        assert( 0 <= x < self.MAP_WIDTH and 0 <= y < self.MAP_HEIGHT)
        assert(kind in self.price)
        assert(self.mapdata[y][x][self.opponent[self.curPlayer]]['B']==0)
        assert(self.mapdata[y][x][self.curPlayer][self.requires[kind]]>0)
        assert(self.nbMoves[(y,x,self.curPlayer,self.requires[kind])] < self.mapdata[y][x][self.curPlayer][self.requires[kind]])
        assert(self.gold[self.curPlayer]>=self.price[kind])
        self.nbMoves[(y,x,self.curPlayer,self.requires[kind])] += 1
        self.nbMoves[(y,x,self.curPlayer,kind)] += 1
        self.mapdata[y][x][self.curPlayer][kind]+=1
        self.gold[self.curPlayer]-=self.price[kind]
        return "ok"

    def forfeit(self):
        if self.winner == '':
            self.winner = self.opponent[self.curPlayer]
    
    def farm(self,y,x):
        assert( 0 <= x < self.MAP_WIDTH and 0 <= y < self.MAP_HEIGHT)
        assert(self.nbMoves[(y,x,self.curPlayer,'C')] < self.mapdata[y][x][self.curPlayer]['C'])
        assert(self.mapdata[y][x]['G']>0)
        assert((y,x) not in self.farmed)
        self.nbMoves[(y,x,self.curPlayer,'C')] += 1
        self.mapdata[y][x]['G'] -= 1
        self.farmed.add((y,x))
        self.gold[self.curPlayer] += 1
        self.score[self.curPlayer] += 1
        return "ok"

    def battle(self,y,x,k,attacker,defender):
        na = self.mapdata[y][x][attacker][k]
        nb = self.mapdata[y][x][defender][k]
        while na>0 and nb>0:
            na-= ceil(nb/2)
            na = max(0, na)
            nb-= ceil(na/2)
            nb = max(0, nb)
        self.mapdata[y][x][attacker][k] = na
        self.mapdata[y][x][defender][k] = nb
                   
    def solveBattles(self,attacker,defender): # combat rules
        for y in range(0,self.MAP_HEIGHT):
            for x in range(0,self.MAP_WIDTH):
                nbDefenderUnitsBefore = self.mapdata[y][x][defender]['B']*self.price['B'] + \
                    self.mapdata[y][x][defender]['M' ]*self.price['M'] + \
                    self.mapdata[y][x][defender]['C']*self.price['C']
                # solve the case of Military vs Military 
                for k in ['M']: # we could do C vs C by adding 'C' here
                    self.battle(y,x,k,attacker,defender)
                for (p,o) in [('A','B'),('B','A')]:
                    # solve the case of Military vs Civil
                    if self.mapdata[y][x][p]['M']>0:
                        self.mapdata[y][x][o]['C']=0
                    # solve the case of remaining Military vs Building
                    if self.mapdata[y][x][p]['M']>0:
                        self.mapdata[y][x][o]['B']=0
                    # we cannot have multiple buildings for a given player
                    # and we cannot have buildings for two different players
                    # as recruiting requires no building
                    self.mapdata[y][x][p]['B'] = min(self.mapdata[y][x][p]['B'],1)
                nbDefenderUnitsAfter  = self.mapdata[y][x][defender]['B']*self.price['B'] + \
                    self.mapdata[y][x][defender]['M' ]*self.price['M'] + \
                    self.mapdata[y][x][defender]['C']*self.price['C']
                self.score[attacker] += nbDefenderUnitsBefore-nbDefenderUnitsAfter


    def getReplay(self):
        return self.matchData

    def changeturn(self):
        # store data for replays
        self.matchData.append({"round":self.curRound,
                               "subround": "beforeBattle",
                               "state":deepcopy(self.giveAllView())})
        # solve battles
        self.solveBattles(self.curPlayer,self.opponent[self.curPlayer])
        # change player
        self.curPlayer=self.opponent[self.curPlayer]
        # check for winner
        for p in ['A', 'B']:
            if len(self.getVisibility(p)) == 0:
                self.winner = self.opponent[p]
        
        if self.winner == '' and self.curRound >= self.MAX_NB_ROUNDS:
            if self.score['A'] == self.score['B']:
                self.winner = 'No one'
            else:
                self.winner = max((self.score['A'],'A'),(self.score['B'],'B'))[1]
        # store again for replays
        self.matchData.append({"round":self.curRound,
                               "subround": "afterBattle",
                               "state":deepcopy(self.giveAllView())})

        # reset data
        self.nbMoves = defaultdict(int)
        self.farmed = set()
        self.curRound +=1

