## OCI Resource Manager Upload


Included is an option in setUpOCI Menu to upload the terraform outdir into OCI Resource Manager:

On choosing **"Developer Services"** in the SetUpOCI menu, choose **"Upload current terraform files/state to Resource Manager"** sub-option to upload the terraform outdir into OCI Resource Manager.

When prompted, specify the Region to create/upload the terraform files to Resource Manager Stack. Multiple regions can be specified as comma separated values.

On the next prompt, enter the Compartment where the Stack should be created if it is for the first time. The toolkit will create a Stack for the region specified previously under the specified compartment.

The Stack created will use Terraform 1.0.x. The upload includes terraform.tfstate file as well, if present. This is to sync the OCI Resource Manager Stack to that of your outdir.

The toolkit also creates a rm_ocids.csv file in the outdir which has the information on the Resource Manager stack that is created. The format of the data in rm_ocids.csv is as follows - 

<Compartment_Name>;<Region_in_lowercase>;<Resource_Manager_Name>;<Resource_Manager_OCID>


Example:

<img width="800" alt="image" src="https://user-images.githubusercontent.com/122371432/214032479-a4754a66-dcf9-4540-a627-dcc8393a062b.png">

To use an existing Resource Manager stack, enter the details in the format provided above to your outdir/rm_ocids.csv" file. 


Sample Execution:


<img width="800" height="600" alt="image" src="https://user-images.githubusercontent.com/122371432/214032803-b31feff1-9949-459b-b2f4-4af35421436c.png">


