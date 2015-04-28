#!/bin/sh
sh ../sqlconfig.sh >/tmp/$$
sed s/%SQLGLOBALS%/$(tr -d \\n < /tmp/$$)/g < dbfind.m
