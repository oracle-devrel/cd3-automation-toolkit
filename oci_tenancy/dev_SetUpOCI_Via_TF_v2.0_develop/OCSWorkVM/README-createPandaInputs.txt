Readme for "createPandaInputs.py"
This script will take generate the hosts.yml and secrets.yml - one for each host based on the output of the
"opcmigrate" (aka Koala) tool as well as the terraform state file which creates the Panda server.
This is why it is important to have to have all those complete before creating this input. The terraform.tfstate file
is used to get the info of the "ctlsInstance"

opcmigrate discover
opcmigrate instances-export > instance-export.json
opcmigrate report

run the createPandaInputs.py with a command like this:
 ./createPandaInputs.py terraform.tfstate instance-export.json resources-default.json report-606666461-uscom-central-1.xlsx

This will generate the hosts and secret file (one per host)
Copy over the openssh pvt key as required to the Panda host
Copy over the files in tmp to the Panda host.
Setup the files in the /home/opc/ansible directory as required.
You can merge the "instances" if you want to perform multiple instances at one time.

