# Common Issues faced by Toolkit Users
 
**1. I am getting 'Permission Denied' error while executing any commands inside the container.**
<br> 

When you are running the docker container from a Linux OS, if the outdir is on the root, you may get a permission denied error while executing steps like createAPIKey.py. In such scenarios, please follow the steps given below -
<br><br><u>Error Screenshot:</u>
![image](https://user-images.githubusercontent.com/103508105/215454472-2367c5d5-2dce-4248-a7fd-c57f1104267e.png)
<br><br><u>Solution:</u><br>
Please change:
<br>           - selinux mode from Enforcing to Permissive
<br>           - change the owner of folders in /cd3user/tenancies to that of cd3user. 
Please refer the screenshots below -
![image](https://user-images.githubusercontent.com/103508105/215455637-4bcaac18-269d-4029-b273-2214b719563f.png)
<br>           - Alternately, please attach a data disk and map the container (/cd3user/tenancies) on a folder that is created on the data disk (your local folder).

**2. I used Non-Greenfield workflow to export resources from OCI. I am not able to see all data into my excel sheet.**
<br>
There could be multiple reasons for this: <br>
   - You have to specify all compartment names(comma separated) explicitly from where you want to export the data.<br>
   - There may be some duplicate resource names in OCI. Toolkit does not support creation/export of resources with same names.