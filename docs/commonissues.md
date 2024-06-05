# Common Issues faced by Toolkit Users
 
**1. I am getting 'Permission Denied' error while executing any commands inside the container.**
<br> 

When running the docker container from a Linux OS, if the outdir is on the root, a permission denied error may occur while executing steps like createAPIKey.py. In such scenarios, please follow the steps given below -
<br><br><u>Error Screenshot:</u>

![image](../images/commonissues-1.png)
<br><br><u>Solution:</u><br>
Please change:
<br>           - selinux mode from Enforcing to Permissive
<br>           - change the owner of folders in /cd3user/tenancies to that of cd3user. 
Please refer the screenshots below -
![image](../images/commonissues-2.png)
<br>           - Alternately, please attach a data disk and map the container (/cd3user/tenancies) on a folder that is created on the data disk (your local folder).

**2. I used Export (Non-Greenfield) workflow to export resources from OCI. I am not able to see all data into my excel sheet.**
<br>
There could be multiple reasons for this: <br>
   - You have to specify all compartment names(comma separated) explicitly from where you want to export the data.<br>
   - There may be some duplicate resource names in OCI. Toolkit does not support creation/export of resources with same names.

**3. I get below error while executing terraform pipelines using jenkins.**

```
+ cd /cd3user/tenancies/jenkins_home/jobs/terraform_files/jobs/phoenix/jobs/network/jobs/terraform-apply/workspace/phoenix/network
+ terraform plan -out=tfplan.out
���
��� Error: error loading state: SignatureDoesNotMatch: The secret key required to complete authentication could not be found. The region must be specified if this is not the home region for the tenancy.
��� 	status code: 403, request id: phx-1:JaiPi4IgUOu0YWZE4-kb3TiLr4g7cQnpqvCT1A3Ca_SUn2cRai-yVrmE-osNZVYx, host id: 
```

This gets resolved on its own after sometime.

