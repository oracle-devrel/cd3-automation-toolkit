Customer acknowledges that the software script(s) are not a
generally available standard Oracle Corp product and that it is a
fundamental condition of supply of the software script(s) to
Customer that Customer accepts the same "as is" and without
warranty of any kind.  No support services of any kind are
available for the software script(s) and Oracle Corp does not represent
to Customer that:

 (i)   operation of any of the software script(s) shall be
       uninterrupted or error free, or

 (ii)  functions contained in the software script(s) shall operate
       in the combinations which may be selected for use by
       Customer or meet Customer's requirements, or

 (iii) that upgraded versions of the software script(s) will be
       issued.

This tool is intended to provide a report of specified OCI objects in
the tenancy.  It requires OCI CLI and the oci cli user config file.
Note: It is recommended that the oci cli user have read only policy for tenancy.

The current version of the tool is Version:  2.1
It was developed using OCI CLI Version 2.4.40 on a Oracle Linux 7.4 Compute Instance.
Python version: Python 2.7.5

The current version of the tool provides information for the following OCI Objects:

A. OCI Environment Tenancy and Region
B. Compute Instances
C. Compute Boot Volumes (associated with compute instances and unassociated)
D. Compute Block Volumes (attached to compute instances and unattached)
E. File System Service
F. Object Storage Service
G. Load Balancer Service
H. DBSys/DB Service
I. Network VCN, Subnets

Valid Options to run the report are:

-c run report and get configs for OCI Compute Instances (and Boot, Block Volumes)
-d run report and get configs for OCI Database Systems
-n run report and get configs for select OCI Network Objects
-s run report and get configs for select OCI Storage Objects (Object, FSS)
-a run report and get configs for OCI Objects in Tenancy
-h print Usage Message for current options

Outputs from the tool is in the form of:

 1. A simple OCI summary report which can be utilized to review objects
    within compartments in the tenancy and across regions.

 2. Object configuration mapping files whose contents, once validated,
    can be used to perform management, queries, obj metadata backup, or updates on those objects.
    Examples include dumping configuration output for an object, 
    performing backups on boot, block volumes or FSS snapshots.
