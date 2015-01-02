#!/bin/sh
sed s/%SQLGLOBALS%/$(tr -d \\n < sqlconfig.sh)/g < dbfind.m
