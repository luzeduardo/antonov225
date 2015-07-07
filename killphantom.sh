#!/bin/sh

find /proc -maxdepth 1 -type d -mmin +3 -exec basename {} \; \
| xargs ps | grep phantomjs | awk '{ print $1 }' | sudo xargs kill