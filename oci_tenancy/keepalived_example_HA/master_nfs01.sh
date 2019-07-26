## This script gets executed automatically whenever this server nfs01 is made as primary server ##

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


CONFIGFILE=/opt/nfsadmin/config/nfsadmin.conf
LOGFILE=/var/log/nfsadmin/master_script-$HOSTNAME.log

FixACL ${LOGFILE}

if [ -e $CONFIGFILE ] ; then
        source $CONFIGFILE
else
        echo "Config file $CONFIGFILE does not exist, setting default values"
        NFS01_VNIC_ID=ocid1.vnic.oc1.iad.abuwcljrvte53pirgsc7skt442nffssspv5ebprlwqeyj7ycru3lfe6ihuzq
        NFS02_VNIC_ID=ocid1.vnic.oc1.iad.abuwcljrg5rvfjboqwqtwbxnr5re3eek76pnsd3cmsytxaxkayrhn4szil6a
	SEC_IP_ADDR=10.218.6.73
fi

LogMsg $LOGFILE "---------Master script execution Start------"
LogMsg $LOGFILE "OCI API Status: "

#unassign private ip from nfs02 vnic
oci network vnic unassign-private-ip --vnic-id $NFS02_VNIC_ID --ip-address $SEC_IP_ADDR --auth instance_principal 1>>$LOGFILE 2>&1
#assign private ip to nfs01 vnic
oci network vnic assign-private-ip --vnic-id $NFS01_VNIC_ID --ip-address $SEC_IP_ADDR --auth instance_principal 1>>$LOGFILE 2>&1

LogMsg $LOGFILE "NFS Remount Status: "
#Remount all mount points on client machines; Apps need to be down before remouting so this is a manual step
/opt/nfsadmin/bin/nfs-remount.sh /opt/nfsadmin/config/nfs-clients.conf /opt/nfsadmin/config/nfs-mounts.conf 1>>$LOGFILE 2>&1

#Delete lock files if any was existing when failover happened
rm -f /var/log/nfsadmin/*.lock

LogMsg $LOGFILE "Crontab Status: "

#Start crontab from MFS01 to NFS02 and to Prod servers in case of switchover
crontab /opt/nfsadmin/config/crontab.nfsadmin 
sleep 2s
crontab -l  1>>$LOGFILE 2>&1


sudo systemctl start crond 
sudo systemctl status crond 1>>$LOGFILE 2>&1

LogMsg $LOGFILE "---------Master script execution Done------"
