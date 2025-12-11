from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello World! Flask is working!"

if __name__ == '__main__':
    # When running with the reloader (debug mode), the script is executed twice.
    # Only print the startup message in the reloader child process to avoid duplicates.
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        print("Starting Flask test server...")
    app.run(debug=True, port=5000)
