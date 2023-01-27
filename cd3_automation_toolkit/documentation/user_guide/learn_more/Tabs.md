## Compartments
Use this Tab to create compartments in the OCI tenancy. On choosing "Identity" in the SetUpOCI menu will allow to create compartments in the OCI tenancy.

Output terraform file generated:  \<outdir>/\<region>/\<prefix>_compartments.auto.tfvars where \<region> directory is the home region.

Once terraform apply is done, you can view the resources under Identity -> Compartments in OCI console.

On re-running the same option you will find the previously existing files being backed up under directory →   \<outdir>/\<region>/backup_compartments/\<Date>-\<Month>-\<Time>.

**Notes:**

Automation Tool Kit generates the TF Configuration files for all the compartments in the tenancy. If some compartment was already existing in OCI then on Terraform Apply, the user will see logs which indicate creation of that compartment - this can be ignored as Terraform will only modify the existing Compartments (with additional information, if there are any eg description) and not create a new/duplicate one.
If you have been given admin access to only one compartment in a tenancy (rather than full admin access) - then you should create the sub-compartments from OCI console, run fetch_compartments_to_variablesTF.py script and then proceed with execution of further objects.

## Groups

Use this Tab to create compartments in the OCI tenancy. On choosing "Identity" in the SetUpOCI menu will allow to create groups in the OCI tenancy.

Automation toolkit supports creation and export of Dynamic Groups as well.
  
Output terraform file generated:  \<outdir>/\<region>/\<prefix>_groups.auto.tfvars under where \<region> directory is the home region.

Once terraform apply is done, you can view the resources under Identity -> Groups in OCI console.

On re-running the same option you will find the previously existing files being backed up under directory →   \<outdir>/\<region>/backup_groups/\<Date>-\<Month>-\<Time>.

## Policies

Use this Tab to create compartments in the OCI tenancy. On choosing "Identity" in the SetUpOCI menu will allow to create policies in the OCI tenancy.

Output terraform files generated: \<outdir>/\<region>/\<prefix>_policies.auto.tfvars where \<region> directory is the home region.

Once terraform apply is done, you can view the resources under Identity -> Policies in OCI console.

On re-running the same option you will find the previously existing files being backed up under directory →   \<outdir>/\<region>/backup_policies/\<Date>-\<Month>-\<Time>.

## Tags Tab

Use this Tab to create tags - Namespaces, Key-Value pairs, Default and Cost Tracking Tags. On choosing "Tags" in the SetUpOCI menu will allow to create Tags in the OCI tenancy.
  
Once this is complete you will find the generated output terraform files in location :

---> \<outdir>/\<region>/\<prefix>_tags-defaults.auto.tfvars 

---> \<outdir>/\<region>/\<prefix>_tags-namespaces.auto.tfvars 

---> \<outdir>/\<region>/\<prefix>_tags-keys.auto.tfvars  

under \<region> directory.

Once terraform apply is done, you can view the resources under Governance -> Tag Namespaces for the region.

On re-running the same option you will find the previously existing files being backed up under directory →   \<outdir>/\<region>/backup_Tagging/\<Date>-\<Month>-\<Time>.

## Create Network

**Pre-requisite:**

Run the script **fetch_compartments_to_variablesTF.py**
Execute CD3 Validator, to avoid any errors during the creation of VCN objects. (Check out Support for CD3 Validator for the details)

Fetch Compartments to Varaibles TF file:

This script will fetch OCIDs of all compartments that exist in the tenancy and place them in variables_<region>.tf directory.

Command used to execute from OCSWork VM: (Fetch Compartments) - python fetch_compartments_to_variablesTF.py /cd3user/tenancies/<customer_name>/terraform_files

For other workstations - example: laptop, specify the path of 'outdir' and path of 'config' file for Python OCI - python fetch_compartments_to_variablesTF.py <path to outdir> --configFileName <path to config file>

To create network objects like VCN, subnets etc in OCI; VCNs, VCN Info, Subnets and DHCP tabs of CD3 are required to be configured.
