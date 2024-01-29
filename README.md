# Fan-Manager
Python Fan Manager for Servers

# Dependancies
ipmitool
python3

# Install
run inclueded install.sh 

This will create the directories
/etc/fan-manager/conf.d/
/etc/fan-manager/bin
/var/log/fan-manager

copy the files into place from the cloned repo

symlink the service file into /etc/systemd/system/ and enable it

Configure via /etc/fan-manager/conf.d/default.conf
then start with
systemctl start fan-manager

# Tested on 
Dell R720, R720XD, R730XD

