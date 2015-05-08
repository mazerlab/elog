#!/bin/sh

cat ./sqlconfig.sh

read -p "  Ok to make database? [must type Y to confirm] " x
if [ "$x" != "Y" ]; then
  echo "aborted"
  exit 1
fi

. ./sqlconfig.sh

mysqladmin -h${HOST} -u${USER} -p${PASS} create ${DB} <<EOF
mysql -h${HOST} -u${USER} -p${PASS} ${DB} <<EOF
Usage: mysqldump [OPTIONS] database [tables]
OR     mysqldump [OPTIONS] --databases [OPTIONS] DB1 [DB2 DB3...]
OR     mysqldump [OPTIONS] --all-databases [OPTIONS]
For more options, use mysqldump --help
EOF
