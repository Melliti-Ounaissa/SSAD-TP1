import sys
import os

# Add the current directory (TP1) to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Now you can import flask_app
from backend import flask_app

flask_app.app.run(debug=True, port=5000)