#!/usr/bin/expect
    set password Riaan@123456
    cd /root/ocswork/git_ocic2oci
    spawn git pull https://suruchi.singla%40oracle.com@developer.em2.oraclecloud.com/developer14539-usoraocips16001/s/developer14539-usoraocips16001_ocictooci_10075/scm/ocictooci.git
    expect "Password for 'https://suruchi.singla@oracle.com@developer.em2.oraclecloud.com':" {send "$password\r"}
    sleep 20
    expect eof
    