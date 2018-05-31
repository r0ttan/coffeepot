from flask import Flask, jsonify, request, make_response, url_for, abort, render_template
import time, hashlib, sqlite3, json, re

app = Flask(__name__)

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify( { 'error': 'Bum request' } ), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)

def make_public_brewer(brewer):
    new_brewer = {}
    new_brewer['uri'] = url_for('checkcoffeetime', brewid = brewer[0], _external = True)
    new_brewer['coffeetime'] = brewer[1]
    return new_brewer

@app.route('/')
def index():
    return "Check how long since coffe was fresh made at the office"

@app.route('/api/v1.2/coffeetime/<string:brewid>', methods = ['GET','POST'])
def checkcoffeetime(brewid):
    con, c = dbconcurs()
    c.execute('SELECT offj FROM coffeetable WHERE brid = ?', (brewid,))
    coftime = json.loads(c.fetchall()[0][0])
    con.commit()
    con.close
    brewer = [brewid, coftime]
    return jsonify(make_public_brewer(brewer))

@app.route('/api/v1.2/set/<string:brewid>', methods = ['GET', 'POST'])
def madecoffee(brewid):
    con, c = dbconcurs()
    c.execute('SELECT offj FROM coffeetable WHERE brid = ?', (brewid,))
    coftime = json.loads(c.fetchall()[0][0])
    brewname = [k for k in coftime.keys()][0]
    coftime[brewname]['fresh'] = time.time() + 3600
    coftime[brewname]['empty'] = False
    c.execute('''UPDATE coffeetable SET offj = ? WHERE brid = ?''', (json.dumps(coftime),brewid))
    con.commit()
    con.close()
    brewer = [brewid, coftime]
    return jsonify(make_public_brewer(brewer)) #jsonify(brewid,coftime)

@app.route('/api/v1.2/empty/<string:brewid>', methods = ['GET', 'POST'])
def empty(brewid):
    con, c = dbconcurs()
    c.execute('SELECT offj FROM coffeetable WHERE brid = ?', (brewid,))
    coftime = json.loads(c.fetchall()[0][0])
    brewname = [k for k in coftime.keys()][0]
    coftime[brewname]['empty'] = True
    coftime[brewname]['fresh'] = ""
    c.execute('''UPDATE coffeetable SET offj = ? WHERE brid = ?''', (json.dumps(coftime),brewid))
    con.commit()
    con.close()
    brewer = [brewid, coftime]
    return jsonify(make_public_brewer(brewer))

@app.route('/api/v1.2/hookup', methods = ['POST'])
def regbrew():
    if not request.json:
        abort(400)
    else:
        newbrew = request.get_json()
        apikey = ['uri','coffeetime','nolollipop']
        for ap in apikey:
            if not ap in newbrew.keys():
                nogo('Request missing key')
    lollipop = hashlib.sha224(newbrew['nolollipop'].encode()).hexdigest()
    if newbrew['uri'] == "" and lollipop == '_f_ff_:¯\_(ツ)_/¯':
        coftime = newbrew['coffeetime']
        brid = make_id('waka')
        brewer = [brid, coftime]
        con, c = dbconcurs()
        c.execute('''INSERT INTO coffeetable VALUES(?, ?)''', (brid,json.dumps(coftime)))
        con.commit()
        con.close()
    else:
        nogo('uri present or secret fail')
    return jsonify(make_public_brewer(brewer))

@app.route('/api/v1.2/search/<string:searchn>', methods = ['GET'])
def listpots(searchn):
    con, c = dbconcurs()
    c.execute('SELECT * FROM coffeetable')
    coftime = c.fetchall()
    brewkeys = [bk[1] for bk in coftime]
    con.commit()
    con.close
    bks = []
    for b in brewkeys:
        for bk in json.loads(b).keys():
            if re.search(searchn, bk, re.IGNORECASE):
                bks.append(bk)
    outlist = []
    for c in coftime:
        if list(json.loads(c[1]))[0] in bks:
            outlist.append((c[0], list(json.loads(c[1]))[0]))
    return jsonify(outlist)

@app.route('/coffeetime/')
def coffepot():
    con, c = dbconcurs()
    c.execute('SELECT offj FROM coffeetable')
    brewkeys = [json.loads(k[0]) for k in c.fetchall()]
    pres = []
    for b in brewkeys:
        for bk in b.keys():
            print("Key:", bk, "Val:", b[bk])
            if b[bk]['fresh'] != "":
                status = {'fresh': (float(time.time() + 3600) - float(b[bk]['fresh']))/60, 'empty':b[bk]['empty']}
            else:
                status = {'fresh': "", 'empty':b[bk]['empty']}
            pres.append({'name':bk, 'status':status})
    return render_template('freshc.html', out=pres)

def nogo(reason):
    abort(400)

def make_id(salt):
    hst = "{}{}".format(salt, time.time())
    return hashlib.sha224(hst.encode()).hexdigest()

def dbconcurs():
    conn = sqlite3.connect('coffeepot.db')
    return conn, conn.cursor()

if __name__ == '__main__':
    app.run(debug=False)
