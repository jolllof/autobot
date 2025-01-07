import yaml
import requests
import structlog
logger = structlog.get_logger()


def load_from_config(config_path, values):
	with open(config_path, 'r') as file:
		config = yaml.safe_load(file)
		return config.get(values, [])

def get_data(url):
	response = requests.get(url)

	if response.status_code != 200:
		print(f"Error Fetching {url} \n {response}")
		return []
	else:
		return response
	
def flatten_dict(dictionary, dict_name=''):
	flat_dict={}

	if dict_name:
		dictionary = {f'{dict_name}_{key}': value for key, value in dictionary.items()}

	for keys, values in dictionary.items():
		if isinstance(values,dict):
			res=flatten_dict(values, keys)
			flat_dict.update(res)
		else:
			flat_dict[keys]=values

	return flat_dict

def merge_dicts(dict1, dict2):
	return {**dict1, **dict2}

def parse_collections(listofdicts, dict_name=''):
	#flattens any dicts in within dicts by appending inner key name to outer key name
	processedlist=[]
	for dictionary in listofdicts:

		primitive_values={key:value for key, value in dictionary.items() if not (isinstance(value, dict) or isinstance(value, list))}
		list_values={key:value for key, value in dictionary.items() if isinstance(value, list)}
		dict_values={key:value for key, value in dictionary.items() if isinstance(value, dict)}

		if list_values:
			logger.error(f'List Values shouldnt exist in trending data returned by Yahoo Finance. Please Review:{list_values}')
	
		if dict_values:
			flat_dict=flatten_dict(dict_values)
			primitive_values=merge_dicts(primitive_values, flat_dict)
		
		processedlist.append(primitive_values)

	return processedlist