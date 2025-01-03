import yaml
import requests

def load_from_config(config_path, values):
	with open(config_path, 'r') as file:
		config = yaml.safe_load(file)
		return config.get(values, [])

def get_data(url):
	response = requests.get(url)

	if response.status_code != 200:
		print(f"Error Fetching {url} \n {response.json()}")
		return []
	else:
		return response.json()