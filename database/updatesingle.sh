python ./makelayerdirs.py
curl -H "Accept: application/json" https://goclubdb.herokuapp.com/clubs/$1/json > `printf "$1/$1%s" "_go_clubs.json"`
