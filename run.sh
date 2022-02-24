
echo '123456' | sudo -S chmod 777 /dev/ttyUSB1 | sudo -S chmod 777 /dev/ttyUSB2
sudo minicom -D /dev/ttyUSB2 -b 115200 -S cmds.txt <escape.txt  
sudo python3 /home/ficha/arg.py -c 1 > launch_logs.txt

