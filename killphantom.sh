#!/bin/sh

ps axh -O etimes | grep phantomjs  | awk '{if ($2 >= 120) print $2}' | xargs kill -9
#watch -n 1 'ps -e -o pid,uname,cmd,pmem,pcpu --sort=-pmem,-pcpu | head -15'
#*/2 * * * * /home/luzeduardo/killphantom.sh
