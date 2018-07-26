ifeq ($(shell domainname), mlab)
  INSTALLROOT ?= /auto/share
  MATLABDIR = $(INSTALLROOT)/pypeextra
else
  INSTALLROOT ?= /usr/local
  MATLABDIR = $(INSTALLROOT)/matlab
endif

MODULES=*.py

install: config tools
	rm -rf $(INSTALLROOT)/lib/elog
	mkdir -p $(INSTALLROOT)/lib/elog
	cp $(MODULES) $(INSTALLROOT)/lib/elog
	./itemplate $(INSTALLROOT)/lib $(INSTALLROOT)/bin elog
	mkdir -p $(MATLABDIR)
	(cd Tools; sh ./mk_dbfind.m.sh > $(MATLABDIR)/dbfind.m; cd ..)

tools:
	cp Tools/elogatt* $(INSTALLROOT)/bin
	cp Tools/dbfind $(INSTALLROOT)/bin

config:
	sh sqlconfig.sh $(INSTALLROOT) >dbsettings.py

createdb:
	sh ./dbmaker.sh

clean:
	/bin/rm -rf *.pyc \#*~ elog dbsettings.py

##############################################################
#
# Everything below here is really for testing or preping for
# a public release.
# 

# copy live database into a _test version for use with test-elog
testdata:
	./test-elog -r

# make an inplace version of elog for use with test-elog or running ./elog
test: config
	@sed s^%%LIB%%^$(shell dirname $(shell pwd))^g \
		<elog.template >./elog
	@chmod +x ./elog

# This creates the database making script. It should be run on a
# machine in the mazer lab only.. it generates a one-time use script
# that 'make initdb' will use to build an empty database.
dist: 
	sh ./mk_dbmaker.sh

###################### mlab only ###############################
# these are custom scripts for the mazer lab that generate on-line
# web-accessible dumps of the logs

mlabscripts:
	chmod +x Tools-mlab/*
	cp -a Tools-mlab/* $(INSTALLROOT)/bin

mlab: install mlabscripts tools

