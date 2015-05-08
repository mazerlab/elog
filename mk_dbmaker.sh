#!/bin/sh

if [ `domainname` != mlab ]; then
  echo "This should only be run in the mazer lab!"
  exit 1
fi

# create dbmaker.sh -- shell script that can be used
# to build an empty 'mlabdata' database schema

. ./sqlconfig.sh

cat <<XXX >dbmaker.sh
#!/bin/sh

cat ./sqlconfig.sh

read -p "  Ok to make database? [must type Y to confirm] " x
if [ "\$x" != "Y" ]; then
  echo "aborted"
  exit 1
fi

. ./sqlconfig.sh

mysqladmin -h\${HOST} -u\${USER} -p\${PASS} create \${DB} <<EOF
mysql -h\${HOST} -u\${USER} -p\${PASS} \${DB} <<EOF
XXX

mysqldump -h${HOST} -u${USER} -p${PASS} -d ${DB} >>dbmaker.sh

cat <<XXX >>dbmaker.sh
EOF
XXX
