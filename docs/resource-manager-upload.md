# OCI Resource Manager Upload


On choosing **"Developer Services"** in the SetUpOCI menu, choose **"Upload current terraform files/state to Resource Manager"** sub-option to upload the terraform outdir into OCI Resource Manager.

This option will upload the created Terraform files & the tfstate (if present) to the OCI Resource Manager.

When prompted, specify the Region to create/upload the terraform files to Resource Manager Stack. Multiple regions can be specified as comma separated values. Specify 'global' to upload RPC related components which reside in 'global' directory.

On the next prompt, enter the Compartment where the Stack should be created if it is for the first time. The toolkit will create a Stack for the region specified previously under the specified compartment. For global resources, stack will be created in the home region.

The Stack created will use Terraform 1.5.x. The upload includes terraform.tfstate file as well, if present. This is to sync the OCI Resource Manager Stack to that of your outdir.

The toolkit also creates a rm_ocids.csv file in the outdir/<region_dir\> which has the information on the Resource Manager stack that is created. The format of the data in ***rm_ocids.csv*** is as follows - 



Example:

<kbd>
<img width="800" alt="image" src="../images/RMupload-1.png">
</kbd>

The toolkit will use an existing Resource Manager stack when data is present in the above format in ```outdir/<region_dir>/rm_ocids.csv``` file. 

Sample Execution:

<kbd>
<img width="800" height="100" alt="image" src="../images/RMupload-2.png">
</kbd><br><br>



!!! IMPORTANT 
    - <b>Upload current terraform files/state to Resource Manager</b> under <b>Developer Services</b> is not enabled if OpenTofu is configured for the prefix during <a href="../connect-container-to-oci-tenancy"><u>Connecting CD3 Container to Tenancy</u></a>.<br>
    - If remote state is being used and try to upload the stack to OCI Resource Manager using <b>Upload current terraform files/state to Resource Manager</b> under <b>Developer Services</b>, then running terraform plan/apply from OCI Resource Manager will not work and show below error:

         <img width="597" alt="Screenshot 2024-01-17 at 11 38 54 PM" src="../images/RMupload-3.png">

          Remove backend.tf from the directory, bring the remote state into local and then re-upload the stack.


