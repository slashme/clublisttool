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
WHERE layer IS "IT"
''')
result = c.fetchall()
c.close()
for row in result:
    row={'geometry': {'type': 'Point', 'coordinates': [row[6],row[5]]}, 'layer': 'IT', 'type': 'Feature', 'properties': {'description': row[1]+', '+row[2]+', '+row[3]+', '+row[4], 'name': row[0]}}
    print(json.dumps(row))
