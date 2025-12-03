import sys
import os
from apig_wsgi import make_lambda_handler
from app import create_app

# Add the root directory to sys.path so we can import 'app'
# This assumes the structure:
# /netlify/functions/api.py
# /app/...
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if root_path not in sys.path:
    sys.path.append(root_path)

app = create_app()

# Configure the handler for AWS Lambda (which Netlify Functions use)
handler = make_lambda_handler(app, binary_support=True)
