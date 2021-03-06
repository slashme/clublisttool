#!/usr/bin/python
import psycopg2, sys, os, urllib, json, codecs

try:
    conn = psycopg2.connect("dbname='goclubdb'")
except:
    print "Can't connect"
    sys.exit()
c = conn.cursor()
#FIXME: Need to add handling for club type and status
c.execute("SELECT name, id FROM goclubdb_layer;")
result = c.fetchall()
for layer in sorted(result):
  outfile=codecs.open(layer[0]+"_go_clubs.json",'w', encoding="utf-8")
  c.execute("SELECT name, website, meetplace, meettime, contact, lat, lon, clubtype_id, clubstatus_id FROM goclubdb_club WHERE layer_id = %s;", (layer[1],))
  result = c.fetchall()
  features=[]
  for row in sorted(result):
      if row[7]==7:
          features.append({'geometry': {'type': 'Point', 'coordinates': [row[6],row[5]]}, 'layer': layer[0], 'type': 'Feature', 'properties': {'description': ' , '.join(filter(None,row[1:5])), 'name': row[0], '_storage_options': {'iconClass': 'Ball'}}} )
      elif row[8]==2:
          features.append({'geometry': {'type': 'Point', 'coordinates': [row[6],row[5]]}, 'layer': layer[0], 'type': 'Feature', 'properties': {'description': ' , '.join(filter(None,row[1:5])), 'name': row[0], '_storage_options': {'iconClass': 'Circle'}}} )
      else:
          features.append({'geometry': {'type': 'Point', 'coordinates': [row[6],row[5]]}, 'layer': layer[0], 'type': 'Feature', 'properties': {'description': ' , '.join(filter(None,row[1:5])), 'name': row[0]}})
  result={'type': 'FeatureCollection', 'features': features}
  json.dump(result, outfile, indent=2, ensure_ascii=False, encoding='utf8')
