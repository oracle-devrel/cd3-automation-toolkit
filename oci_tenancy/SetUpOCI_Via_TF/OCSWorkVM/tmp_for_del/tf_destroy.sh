
#!/bin/bash
cd /root/ocswork/ocic2oci_work
n=0
    until [ $n -ge 5 ]
   do
      terraform destroy -auto-approve && break
      n=$[$n+1]
      sleep 3
   done
