import os
import sys

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from backend.app import app
from backend.utils.config import config

if __name__ == '__main__':
    app.run(debug=config.DEBUG)
