import unittest
import sys
import os

# Print current working directory and Python path for debugging
print("Current working directory:", os.getcwd())
print("Python path:", sys.path)

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)
print("Updated Python path:", sys.path)

# Print contents of the backend directory
backend_dir = os.path.join(project_root, 'backend')
print("Contents of backend directory:")
for root, dirs, files in os.walk(backend_dir):
    level = root.replace(backend_dir, '').count(os.sep)
    indent = ' ' * 4 * (level)
    print('{}{}/'.format(indent, os.path.basename(root)))
    subindent = ' ' * 4 * (level + 1)
    for f in files:
        print('{}{}'.format(subindent, f))

# Discover and run tests
loader = unittest.TestLoader()
start_dir = os.path.join(project_root, 'backend', 'tests')
suite = loader.discover(start_dir, pattern="test_*.py")

runner = unittest.TextTestRunner()
result = runner.run(suite)

# Exit with non-zero status if there were failures
sys.exit(not result.wasSuccessful())
