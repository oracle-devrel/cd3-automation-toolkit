#!/bin/bash
#
# This script is used to remount NFS file systems previously mounted. 
# It cen be necessary when NFS share is changed due to failover.
#
Usage() {
        echo "Missing or bad arguments"
        echo 'Usage: nfs-remount.sh nfs-clients-list-file mount-points-list-file'
        echo './nfs-remount.sh /opt/nfsadmin/config/nfs-clients.conf /opt/nfsadmin/config/nfs-mounts.conf'
        exit
}

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



RemountNFS() {
	host=$1
	
	while read mp || [[ -n "$mp" ]]
	do
		if [ "${mp:0:1}" != "#" ]
		then
			ssh -l ${APP_REMOUNT_USER} -i ${PRIVKEY} ${host} sudo umount -f -l ${mp} < /dev/null
			sleep 2s
			ssh -l ${APP_REMOUNT_USER} -i ${PRIVKEY} ${host} sudo mount ${mp} < /dev/null
			[ $? -eq 0 ] && echo "REMOUNTED ${mp} ON HOST $host" || echo "MOUNT POINT $mp ON $host failed"
			
			LogMsg $LOGFILE "Remount attempted on $host for $mp"
		else
			LogMsg $LOGFILE "Skipping mount for $mp on host ${hname}"
		fi
	
	done <${MOUNTS}
}


[ $# != 2 ] && Usage


HOSTS=$1
MOUNTS=$2

STIME=$(date +'%s')
FTIME=$(date --date "@${STIME}" +'%Y%m%d-%H%M%S')

CONFIGFILE=/opt/nfsadmin/config/nfsadmin.conf
LOGFILE=/var/log/nfsadmin/nfs-remount-clients-$HOSTNAME.log


FixACL ${LOGFILE}



if [ -e $CONFIGFILE ] ; then
        source $CONFIGFILE
else
        echo "Config file $CONFIGFILE does not exist, setting default values"
        APP_REMOUNT_USER=rydersvc
	PRIVKEY="/opt/nfsadmin/config/id_rsa"
fi


printf "\n"

LogMsg $LOGFILE "-----------------Remount Started--------------"
while read hname || [[ -n "$hname" ]]
do
	if [ "${hname:0:1}" != "#" ]
	then
		RemountNFS $hname
	else
		LogMsg $LOGFILE "Skipping hostname ${hname}"
	fi
done <${HOSTS}

printf "\n"
echo "check log file $LOGFILE for any skipped locations"

LogMsg $LOGFILE "-----------------Remount Finished--------------"
