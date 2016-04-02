#!/usr/bin/python
import sqlite3, os, urllib, json, codecs

conn = sqlite3.connect('clubs.db')
c = conn.cursor()
#FIXME: Need to add handling for club type and status
c.execute("SELECT name FROM layers;")
result = c.fetchall()
for layer in result:
  outfile=codecs.open(layer[0]+"_go_clubs.json",'w', encoding="utf-8")
  c.execute('''
  SELECT name, website, meetplace, meettime, contact, lat, lon
  FROM 
    clubs 
  WHERE layer = ?
  ''', (layer[0],))
  result = c.fetchall()
  features=[]
  for row in result:
      features.append({'geometry': {'type': 'Point', 'coordinates': [row[6],row[5]]}, 'layer': layer[0], 'type': 'Feature', 'properties': {'description': ', '.join(filter(None,row[1:5])), 'name': row[0]}})
  result={'type': 'FeatureCollection', 'features': features}
  json.dump(result, outfile, indent=2, ensure_ascii=False)
