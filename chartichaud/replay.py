from flask import Flask
from flask import jsonify
from flask import send_from_directory
import sqlite3

app = Flask(__name__, static_url_path='', static_folder='static')

@app.route('/matchlist')
def listMatches():
    con = sqlite3.connect("matchs.db")
    cursor = con.cursor()
    cursor.execute("SELECT date,playerA,playerB,winner,replay FROM matchs ORDER BY date DESC ;")
    rows = cursor.fetchall()
    out = []
    for row in rows:
        out.append({"date":row[0], "A": row[1], "B": row[2], "winner": row[3], "replay": row[4] })
    return jsonify(out)



@app.route('/match/<path:filename>')
def base_static(filename):
    return send_from_directory(app.root_path + '/match/', filename)

@app.route('/')
def root():
    return app.send_static_file('replay.html')


app.run(host='0.0.0.0', port=7654)
