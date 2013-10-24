#PYPEDIR=$(shell pypenv --dir)

MODULES=*.py

test-inplace:
	sed s^%%LIB%%^$(shell dirname $(shell pwd))^g \
		<elog.template >./elog
	sed s^%%LIB%%^$(shell dirname $(shell pwd))^g \
		<elogatt.template >./elogatt
	chmod +x ./dbfind
	chmod +x ./elog
	chmod +x ./elogatt

install:
	sudo make install2

install2:
	rm -rf /auto/share/lib/elog
	mkdir /auto/share/lib/elog
	cp $(MODULES) /auto/share/lib/elog
	sed s^%%LIB%%^/auto/share/lib^g \
		<elog.template >/auto/share/bin/elog 
	sed s^%%LIB%%^/auto/share/lib^g \
		<elogatt.template >/auto/share/bin/elogatt
	chmod +x /auto/share/bin/elogatt
	cp dbfind dbfind.m elogatt.m qhistory /auto/share/pypeextra/
	chmod +x /auto/share/pypeextra/dbfind
	chmod +x /auto/share/pypeextra/qhistory

testdata:
	mysqldump -hsql -umlab -pmlab \
			--add-drop-database --databases mlabdata | \
		sed s/mlabdata/mlabdata_test/g | gzip >testdata.sql.gz


clean:
	/bin/rm -rf *.pyc \#*~ elog elogatt
	svn status

commit:
	svn commit && svn update

schema:
	mysqldump -d -hsql -umlab -pmlab mlabdata
