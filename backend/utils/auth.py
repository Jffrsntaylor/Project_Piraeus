from functools import wraps
from flask import request, jsonify
import os

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_token = request.headers.get('Authorization')
        if auth_token == os.environ.get('API_KEY'):
            return f(*args, **kwargs)
        return jsonify({"error": "Unauthorized"}), 401
    return decorated
