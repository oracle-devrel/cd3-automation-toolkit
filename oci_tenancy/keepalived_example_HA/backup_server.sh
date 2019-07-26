#!/bin/bash
function LogMsg {
	local log=$1
	local msg=$2
	local pid=$$
	local now=$(date +'%s')
	local stamp=$(date --date "@${now}" +'%Y/%m/%d %H:%M:%S')
	echo "${stamp}-${pid}-${msg}" >>$log
}

FixACL (){
	file=$1
	[ ! -e ${file} ] && touch $file
	sudo chmod a+rw $file
	sudo chown nfsadmin:nfsadmin $file
}
LOGFILE=/var/log/nfsadmin/backup_script-${HOSTNAME}.log
FixACL ${LOGFILE}

LogMsg $LOGFILE "-------------Backup Script Execution Start-----------"
#Kill any rsync process in case started as soon as server came up
sudo pkill -9 rsync

LogMsg $LOGFILE "Crontab Status: "

#Stop crond service when NFS01 is running as BACKUP
crontab -r
crontab -l 1>>$LOGFILE 2>&1
sudo systemctl stop crond
sudo systemctl status crond 1>>$LOGFILE 2>&1
LogMsg $LOGFILE "-------------Backup Script Execution Done-----------"
