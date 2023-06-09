## OCI Resource Manager Upload


This option will upload the created Terraform files & the tfstate (if present) to the OCI Resource Manager.

On choosing **"Developer Services"** in the SetUpOCI menu, choose **"Upload current terraform files/state to Resource Manager"** sub-option to upload the terraform outdir into OCI Resource Manager.

When prompted, specify the Region to create/upload the terraform files to Resource Manager Stack. Multiple regions can be specified as comma separated values. Specify 'global' to upload RPC related components which reside in 'global' directory.

On the next prompt, enter the Compartment where the Stack should be created if it is for the first time. The toolkit will create a Stack for the region specified previously under the specified compartment. For global resources, stack will be created in the home region.

The Stack created will use Terraform 1.0.x. The upload includes terraform.tfstate file as well, if present. This is to sync the OCI Resource Manager Stack to that of your outdir.

The toolkit also creates a rm_ocids.csv file in the outdir/<region_dir> which has the information on the Resource Manager stack that is created. The format of the data in ***rm_ocids.csv*** is as follows - 

***_<Region_in_lowercase>;<Compartment_Name>;<Resource_Manager_Name>;<Resource_Manager_OCID>_***

Example:

<kbd>
<img width="800" alt="image" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/e95572de-2cb0-46f9-ae26-21391c9fee8b">
</kbd>

To use an existing Resource Manager stack, enter the details in the format provided above into your _outdir/<region_dir>/rm_ocids.csv_" file. 


Sample Execution:

<kbd>
<img width="800" height="600" alt="image" src="(https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/e3d7417e-ce1c-464a-8a1d-5cdfd7862835))">
</kbd>
