import urllib.request
import json
url = "https://raw.githubusercontent.com/rhasspy/piper/master/docs/voices.json"
req = urllib.request.urlopen(url)
data = json.loads(req.read())
voices = [(k, v['name'], v.get('quality', 'unknown')) for k, v in data.items() if 'te_IN' in k]
print("Telugu voices:", voices)
