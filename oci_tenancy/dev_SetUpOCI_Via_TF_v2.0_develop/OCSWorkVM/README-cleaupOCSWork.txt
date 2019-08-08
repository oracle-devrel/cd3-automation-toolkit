When createOCSWork.py is executed, it updates config file with necessary parameters like compartment OCIDs, VCN OCID etc
and pushes the config file over to the VM.
Apart from updating config file, it also creates config_for_delete file in your current folder in PyCharm. This file contains
OCIDs of the various components created for OCS Work

When cleanOCSWork.py is executed, it will login to the VM, destroy terraform for panda instance created and delete all
components created in OCI for OCS work.

At the end, this script should delete OCI components, empty the config_for_delete file and also remove all OCID parameters
added to config file and revert it back to original.


