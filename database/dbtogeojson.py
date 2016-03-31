import sqlite3, os, urllib, json

conn = sqlite3.connect('clubs.db')
c = conn.cursor()
#FIXME: Need to add handling for club type and status, and not hardcode layer
c.execute('''
SELECT
  name,
  website,
  meetplace,
  meettime,
  contact,
  lat,
  lon,
  layer
FROM 
  clubs 
WHERE layer LIKE "CH"
''')
result = c.fetchall()
c.close()
features=[]
for row in result:
    features.append({'geometry': {'type': 'Point', 'coordinates': [row[6],row[5]]}, 'layer': row[7], 'type': 'Feature', 'properties': {'description': ', '.join(filter(None,row[1:5])), 'name': row[0]}})
result={'type': 'FeatureCollection', 'features': features}
print(json.dumps(result))
