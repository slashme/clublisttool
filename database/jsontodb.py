#!/usr/bin/python

#Script to load geojson club data into database

import json, sys, sqlite3

#Load the file given as an argument on the command line
infile=open(sys.argv[1],'r')

#Parse it as json data
clubdata=json.load(infile)

#Open database connection
con = sqlite3.connect('test.db')

#At the moment, the geojson just has a single text field, instead of name and description in most cases.
for club in clubdata['features']:
  try:
    con.execute("INSERT INTO clubs (layer, lon, lat, name) VALUES (?, ?, ?, ?)", (club['layer'], club['geometry']['coordinates'][0], club['geometry']['coordinates'][1], club['properties']['description']))
    #Write it to the database.
  except KeyError:
    pass
con.commit()

