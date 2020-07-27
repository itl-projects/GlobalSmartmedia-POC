import os
import json

def track(file_name, name, status=None):
	data = {'files': []}
	if os.path.exists(file_name):
		with open(file_name, "r") as f:
			data = json.loads(f.read())
	
	data['files'].append(name)

	with open(file_name, "w+") as f:
		f.write(json.dumps(data))

def track_check(file_name, name):
	if os.path.exists(file_name):
		with open(file_name, "r") as f:
			data = json.loads(f.read())
		if name in data['files']:
			return True
	return False

def track_get_no(file_name):
	if os.path.exists(file_name):
		with open(file_name, "r") as f:
			data = json.loads(f.read())
		return len(data['files'])
	else:
		return 0