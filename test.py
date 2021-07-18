from json import load

with open('talents.json') as jf:
    json_data = load(jf)

print(json_data['aptekarz']['name'])