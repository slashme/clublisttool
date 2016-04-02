#!/usr/bin/python

#Script to sort umap geojson data for clearer diff

import json, sys, codecs

#Process each file given as an argument on the command line
for i in sys.argv[1:]:
  infile=open(i,'r')
  outfile=codecs.open("sorted."+i,'w', encoding="utf-8")
  #Parse it as json data
  dicti=json.loads(infile.read().decode("utf-8-sig"))
  #Write sorted data to outfile
  json.dump(dicti, outfile, indent=2, sort_keys=True, ensure_ascii=False)
