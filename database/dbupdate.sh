python dbtogeojson.py
for i in `ls -d [A-Z][A-Z]`
  do mv `printf "$i%s" "_go_clubs.json"` $i
done
