for i in `ls -d [A-Z][A-Z]`
  do curl -H "Accept: application/json" https://goclubdb.herokuapp.com/clubs/$i/json > `printf "$i/$i%s" "_go_clubs.json"`
done
