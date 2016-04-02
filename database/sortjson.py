#!/usr/bin/python

#Script to sort umap geojson data for clearer diff

import json, sys

#Process each file given as an argument on the command line
for i in sys.argv[1:]:
  infile=open(i,'r')
  outfile=open("sorted."+i,'w')
  #Parse it as json data
  dicti=json.load(infile)
  #Write sorted data to outfile
  for j in sorted(dicti['features']):
    outfile.write(str(j)+'\n')
