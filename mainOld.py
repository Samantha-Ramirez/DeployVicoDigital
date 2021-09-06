from flask import Flask

app = Flask(__name__)
PORT = 5000
DEBUG = False

@app.errorhandler(404)
def not_found(error):
    return "Not Found"

@app.route('/', methods=['GET'])
def index():
    return "Hola Mi nombre es Rusell"

if __name__ == '__main__':
    app.run(port = PORT, debug = DEBUG)