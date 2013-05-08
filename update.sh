#!/bin/bash
cd "$(dirname $BASH_SOURCE)"
echo Starting update script in background.

echo "" >>../../updatelog.txt
date >>../../updatelog.txt
echo Starting update script >>../../updatelog.txt
echo Copying new files into place >>../../updatelog.txt

cp -Rf * ../../ 2>>../../updatelog.txt >>../../updatelog.txt

cd ../../

echo Deleting downloaded source code.zip >> updatelog.txt
rm -Rf code.zip 2>> updatelog.txt >> updatelog.txt

echo Killing running IRC Bot with pid $1 >> updatelog.txt
kill $1
python irc_bot.py > log.txt &
echo Started new IRC bot. >> updatelog.txt

echo Removing downloaded source folder >> updatelog.txt
rm -Rf code 2>>updatelog.txt >>updatelog.txt &
echo Finished update >>updatelog.txt
date >>updatelog.txt
echo "" >>updatelog.txt
echo "--" >>updatelog.txt