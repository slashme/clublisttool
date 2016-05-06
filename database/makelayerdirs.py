import urllib, json, os

response = urllib.urlopen("http://goclubdb.herokuapp.com/layers/json")
for i in json.loads(response.read()):
  if not os.path.exists(i['name']):
    try:
      os.makedirs(i['name'])
    except OSError:
      print "Can't create directory %s\n" % i['name']
    else:
      print "Made directory %s\n" % i['name']
