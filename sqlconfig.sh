#!/bin/sh

cat <<EOF
HOST='sql';
USER='mlab';
PASS='mlab';
DB='mlabdata';
PORT='3306';
DIR='$1';
EOF


exit 0

####################################################


if [ "$(domainname)" = "mlab" ]; then
    cat <<EOF
HOST='sql';
USER='mlab';
PASS='mlab';
DB='mlabdata';
PORT='3306';
DIR='$1';
EOF
else
    cat <<EOF
HOST='localhost';
USER='root';
PASS='';
DB='mlabdata';
PORT='3306';
DIR='$1';
EOF
fi

