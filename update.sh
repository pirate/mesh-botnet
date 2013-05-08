echo Starting update script in background.

echo Starting update script >../../updatelog.txt

cp * ../../ 2>>../../updatelog.txt >>../../updatelog.txt
rm -Rf ../../code.zip 2>>../../updatelog.txt >>../../updatelog.txt

nohup python ../../irc_bot.py & 
echo Started IRC bot. >>../../updatelog.txt

rm -Rf ../../code 2>>../../updatelog.txt >>../../updatelog.txt

echo Finished update. >>../../updatelog.txt