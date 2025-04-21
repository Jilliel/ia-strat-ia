from math import ceil
from flask import Flask
from flask import jsonify
import random
from collections import defaultdict
from flask import send_from_directory
import string
import json
import sys
import os
import sqlite3
import uuid
from copy import deepcopy
import logging
import time
from chartichaud.game import Game

app = Flask(__name__, static_url_path='', static_folder='static')
app.logger.disabled = True
logging.getLogger("werkzeug").disabled=True

#####  AUTH PARAMETERS #####

tokenOf = {}
playerName = {}
startTurn = None
startMatch = time.time()

MAX_TIME = 600
MAX_INIT_TIME = 600

game = Game()
# start a private match without viewers
privateMatch = False
for arg in sys.argv:
    if arg=="private":
        privateMatch = True
        MAX_TIME=15
        print("This is a private match")

def finMatch():
    global tokenOf
    tokenOf = defaultdict(lambda x:"")
    if privateMatch:
        savematch()
        os._exit(0)

        
@app.route('/getToken/<name>')
def getToken(name):
    assert(len(tokenOf) < 2)
    rt = "".join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=8))
    if 'A' in tokenOf:
        player = 'B'
    else:
        player = 'A'
        startTurn = time.time()
    tokenOf[player] = rt
    playerName[player] = name
    return jsonify({'player':player, 'token':rt})

@app.route('/getToken')
def getTokenUnknown():
    return getToken("Unknown")

@app.route('/alive')
def check_alive():
    global startTurn, startMatch
    if startTurn:
        if time.time() - startTurn > MAX_TIME:
            game.forfeit()
            finMatch()
    else:
        if time.time() - startMatch > MAX_INIT_TIME:
            os._exit(0)
    return jsonify({'response':'ok'})

@app.route('/view/<player>/<token>')
def giveView(player,token):
    global tokenOf
    global startTurn
    if (player=="all" and not privateMatch) or game.winner != "":
        return jsonify(game.giveAllView())
    assert(tokenOf[player]==token)
    check_alive()
    return jsonify(game.giveViewPlayer(player))

@app.route('/move/<player>/<kind>/<int:y>/<int:x>/<int:ny>/<int:nx>/<token>')
def move(player,kind,y,x,ny,nx,token):
    global tokenOf
    assert(tokenOf[player]==token)
    assert(player==game.curPlayer)
    return game.move(kind,y,x,ny,nx)

@app.route('/build/<player>/<int:y>/<int:x>/<kind>/<token>')
def build(player,y,x,kind,token):
    global tokenOf
    assert(tokenOf[player]==token)
    assert(player==game.curPlayer)
    return game.build(y,x,kind)

@app.route('/farm/<player>/<int:y>/<int:x>/<token>')
def farm(player,y,x,token):
    global tokenOf
    assert(tokenOf[player]==token)
    assert(player==game.curPlayer)
    return game.farm(y,x)

@app.route('/autofarm/<player>/<token>')
def autofarm(player,token):
    global tokenOf
    assert(tokenOf[player]==token) 
    assert(player==game.curPlayer)
    for y in range(game.MAP_HEIGHT):
        for x in range(game.MAP_WIDTH):
            try:
                game.farm(y,x)
            except:
                pass
    return "ok"

def savematch():
    con = sqlite3.connect("matchs.db")
    cursor = con.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS matchs (id INTEGER PRIMARY KEY AUTOINCREMENT, date real, playerA text, playerB text, winner text, replay text);")
    con.commit()
    matchFilename="match/"+str(uuid.uuid4())+".json"
    winnerName = "No one"
    if game.winner in playerName:
        winnerName = playerName[game.winner] + "("+game.winner+")"
    if 'B' not in playerName:
        playerName['B'] = 'crashed bot'
    cursor.execute("INSERT INTO matchs (date,playerA, playerB, winner, replay) VALUES(datetime('now'),?,?,?,?)", (playerName['A'],playerName['B'],winnerName, matchFilename))
    with open(matchFilename,'w') as f:
        f.write(json.dumps(game.getReplay()))
    con.commit()

@app.route('/endturn/<player>/<token>')
def changeturn(player,token):
    global tokenOf
    global startTurn
    assert(tokenOf[player]==token)
    assert(player==game.curPlayer)
    game.changeturn()
    if game.winner != "":
        finMatch()
    startTurn = time.time()
    return "ok"

@app.route('/getwinner/<player>/<token>')
def getwinner(player, token):
    global tokenOf
    assert(tokenOf[player]==token)
    return jsonify({'winner':game.winner})

@app.route('/')
def root():
    return app.send_static_file('index.html')

def setGameMapdata(mapdata):
    game.mapdata = mapdata

def launchServer(port: int = 8080):
    app.run(port=port, debug=False)

if __name__ == '__main__':
    launchServer()
