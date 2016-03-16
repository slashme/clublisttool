#!/usr/bin/python
import sys
import xml.etree.ElementTree as ET

#from http://stackoverflow.com/questions/7684333/converting-xml-to-dictionary-using-elementtree
from collections import defaultdict

def etree_to_dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.iteritems():
                dd[k].append(v)
        d = {t.tag: {k:v[0] if len(v) == 1 else v for k, v in dd.iteritems()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.iteritems())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
              d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d

outfile=open(sys.argv[1]+'.geojson','w')
tree = ET.parse(sys.argv[1])
root=tree.getroot()
for i in root:
  j=(etree_to_dict(i))
  outfile.write(str(j)+'\n')
