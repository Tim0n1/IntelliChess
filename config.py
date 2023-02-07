import json

config = open('config.json', 'r').read()
config = json.loads(config)

res_x = config['video']['resolution'][0]
res_y = config['video']['resolution'][1]
