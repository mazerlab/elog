ifeq ($(shell domainname), mlab)
  INSTALLROOT ?= /auto/share
else
  INSTALLROOT ?= /usr/local
endif

MODULES=*.py

test-inplace:
	@sed s^%%LIB%%^$(shell dirname $(shell pwd))^g \
		<elog.template >./elog
	@sed s^%%LIB%%^$(shell dirname $(shell pwd))^g \
		<elogatt.template >./elogatt
	@chmod +x ./dbfind
	@chmod +x ./elog
	@chmod +x ./elogatt

install:
	sudo make install_ install_scripts

install_: 
	rm -rf $(INSTALLROOT)/lib/elog
	mkdir $(INSTALLROOT)/lib/elog
	cp $(MODULES) $(INSTALLROOT)/lib/elog
	sed s^%%LIB%%^$(INSTALLROOT)/lib^g \
		<elog.template >$(INSTALLROOT)/bin/elog 
	chmod a+x $(INSTALLROOT)/bin/elog
	sed s^%%LIB%%^$(INSTALLROOT)/lib^g \
		<elogatt.template >$(INSTALLROOT)/bin/elogatt
	chmod a+x $(INSTALLROOT)/bin/elogatt
	cp dbfind dbfind.m elogatt.m qhistory eloghist $(INSTALLROOT)/pypeextra/
	chmod a+x $(INSTALLROOT)/pypeextra/dbfind
	chmod a+x $(INSTALLROOT)/pypeextra/qhistory
	chmod a+x $(INSTALLROOT)/pypeextra/eloghist
	cp scripts/* $(INSTALLROOT)/pypeextra


install_scripts:
	chmod +x scripts/*
	cp scripts/* $(INSTALLROOT)/pypeextra

# dump live database for testing using 'test-elog'
testdata:
	mysqldump -hsql -umlab -pmlab \
			--add-drop-database --databases mlabdata | \
		sed s/mlabdata/mlabdata_test/g | gzip >testdata.sql.gz
	./test-elog -r


clean:
	/bin/rm -rf *.pyc \#*~ elog elogatt
	svn status

commit:
	svn commit && svn update

schema:
	mysqldump -d -hsql -umlab -pmlab mlabdata
