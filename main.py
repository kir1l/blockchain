import hashlib
import json
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request

from api import app
# TODO: разобраться с отрицательным балансом, потом доделать gui
if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5000)
