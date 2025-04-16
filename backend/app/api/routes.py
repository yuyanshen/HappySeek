from flask import jsonify, request
from . import api

@api.route('/test')
def test():
    return jsonify({'message': 'API is working'})