#!/usr/bin/python

#Script to load geojson club data into database

import json, sys, sqlite3

#Load the file given as an argument on the command line
infile=open(sys.argv[1],'r')

#Parse it as json data
clubdata=json.load(infile)

#Open database connection
con = sqlite3.connect(sys.argv[2])

#At the moment, the geojson just has a name and description, with all the information bundled into the description
for club in clubdata['features']:
  try:
    con.execute("INSERT INTO clubs (layer, lon, lat, name, contact) VALUES (?, ?, ?, ?, ?)", ('RU', club['geometry']['coordinates'][0], club['geometry']['coordinates'][1], club['properties']['name'], club['properties']['description'])) #FIXME: currently hard-coded layer info.
  except KeyError:
    pass
con.commit()

