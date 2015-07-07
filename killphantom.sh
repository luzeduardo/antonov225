#!/bin/sh

find /proc -maxdepth 1 -user luzeduardo -type d -mmin +3 -exec basename {} \; \
| xargs ps | grep phantomjs | awk '{ print $1 }' | sudo xargs kill

#*/2 * * * * /home/luzeduardo/killphantom.sh
