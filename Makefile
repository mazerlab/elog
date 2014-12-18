ifeq ($(shell domainname), mlab)
  INSTALLROOT ?= /auto/share
else
  INSTALLROOT ?= /usr/local
endif

MODULES=*.py

mlab: exe mlabscripts

install: exe

exe: config
	rm -rf $(INSTALLROOT)/lib/elog
	mkdir $(INSTALLROOT)/lib/elog
	cp $(MODULES) $(INSTALLROOT)/lib/elog
	./itemplate $(INSTALLROOT)/lib $(INSTALLROOT)/bin \
		elog elogatt dbfind qhistory
	cp dbfind.m elogatt.m $(INSTALLROOT)/pypeextra/

mlabscripts:
	chmod +x scripts/*
	cp scripts/* $(INSTALLROOT)/pypeextra

# copy live database into for _test for testing with test-elog
testdata:
	./test-elog -r

# make an inplace version of elog for testing..
test: config
	@sed s^%%LIB%%^$(shell dirname $(shell pwd))^g \
		<elog.template >./elog
	@chmod +x ./elog

config:
	./mk_dbfind
	cat sqlconfig.sh >dbsettings.py

clean:
	/bin/rm -rf *.pyc \#*~ elog dbsettings.py dbfind

# This creates the database making script. It should be run on a
# machine in the mazer lab only.. it generates a one-time use script
# that 'make initdb' will use to build an empty database.
dist: 
	./mk_dbmaker.sh

initdb:
	sh ./dbmaker.sh
