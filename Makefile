ifeq ($(shell domainname), mlab)
  INSTALLROOT ?= /auto/share
else
  INSTALLROOT ?= /usr/local
endif

MODULES=*.py


test-inplace:
	@sed s^%%LIB%%^$(shell dirname $(shell pwd))^g \
		<elog.template >./elog
	@chmod +x ./elog

install: exe scripts

exe:
	rm -rf $(INSTALLROOT)/lib/elog
	mkdir $(INSTALLROOT)/lib/elog
	cp $(MODULES) $(INSTALLROOT)/lib/elog
	./itemplate $(INSTALLROOT)/lib $(INSTALLROOT)/bin elog elogatt dbfind qhistory eloghist
	cp dbfind.m elogatt.m $(INSTALLROOT)/pypeextra/

scripts:
	chmod +x scripts/*
	cp scripts/* $(INSTALLROOT)/pypeextra

# dump live database for testing using 'test-elog'
testdata:
	mysqldump -hsql -umlab -pmlab --add-drop-database --databases mlabdata \
		| sed s/mlabdata/mlabdata_test/g \
		| gzip >testdata.sql.gz
	./test-elog -r

clean:
	/bin/rm -rf *.pyc \#*~ elog elogatt dbfind

# output of `make schema` can be used to initialize a new database
schema:
	mysqldump -d -hsql -umlab -pmlab mlabdata
