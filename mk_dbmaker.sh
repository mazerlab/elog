#!/bin/sh

# create dbmaker.sh -- shell script that can be used
# to build an empty 'mlabdata' database schema

cat <<XXX >dbmaker.sh
#!/bin/sh
mysqladmin -hsql -umlab -pmlab create mlabdata <<EOF
mysql -hsql -umlab -pmlab mlabdata <<EOF
XXX

mysqldump -hsql -umlab -pmlab -d mlabdata >>dbmaker.sh

cat <<XXX >>dbmaker.sh
EOF
XXX
