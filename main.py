import hashlib
import json
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request

from api import BlockchainAPI

if __name__ == '__main__':
   blockchain_api = BlockchainAPI()
   blockchain_api.run()
