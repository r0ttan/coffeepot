from flask import Flask, jsonify
import time

app = Flask(__name__)

present = time.time() + 3600
coftime = {'fresh': '{0:.2f}'.format(present), 'empty': True}


@app.route('/')
def index():
    return "Check how long since coffe was fresh made at the office"

@app.route('/api/v1.0/')
def checkcoffetime():
    return jsonify(coftime)

@app.route('/api/v1.0/set/')
def madecoffee():
    coftime['fresh'] = '{0:.2f}'.format(time.time() + 3600)
    coftime['empty'] = False
    return jsonify(coftime)

@app.route('/api/v1.0/empty/')
def empty():
    coftime['fresh'] = '{0:.2f}'.format(time.time() + 3600)
    coftime['empty'] = True
    return jsonify(coftime)

if __name__ == '__main__':
    app.run(debug=False)
