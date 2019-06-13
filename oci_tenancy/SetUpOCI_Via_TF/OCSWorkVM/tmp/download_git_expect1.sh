#!/usr/bin/expect
    set password Riaan@123456
    cd /root/ocswork/git_oci
    spawn git pull  https://suruchi.singla%40oracle.com@developer.em2.oraclecloud.com/developer14539-usoraocips16001/s/developer14539-usoraocips16001_oci_9900/scm/oci.git
    expect "Password for 'https://suruchi.singla@oracle.com@developer.em2.oraclecloud.com':" {send "$password\r"}
    sleep 20
    expect eof
    