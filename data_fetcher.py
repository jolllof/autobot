#TODO: script should reference keys stored in config.yaml

from binance.client import Client
import os

API_KEY = os.getenv('binance_key')
API_SECRET = os.getenv('binance_secret')

print(f"{API_KEY} -  {API_SECRET}")