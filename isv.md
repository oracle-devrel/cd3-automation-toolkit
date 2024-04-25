<h2> Export and Replicate OCI Infrastructure across tenancies </h2>

To create an identical copy of existing infrastructure in a target tenancy or compartment, follow the below steps:

Set Up two CD3 containers and connect them to Source Tenancy and Target Tenancy each using steps mentioned in https://oracle-devrel.github.io/cd3-automation-toolkit/install-cd3/. 

>Note: - Same process should be used to replicate Infra resources from one Compartment to another in the same Tenancy.

**Method 1: Using the Excel sheet of source tenancy**

<h5> Identity Components </h5>

- Execute the toolkit to export Identity Components (Compartments, Groups, Policies, Users, Network Sources) from source tenancy. 
- There is no need to execute the generated shell script containing the terraform import commands.
- In the exported Excel file, make appropriate changes to Identity tabs to match region name or other parameters for the new tenancy.
- Execute the toolkit for Create Workflow using above Excel sheet in target tenancy container. Choose 'Identity' in main options and required sub-options.
- Execute terraform init, plan and apply from 'identity' service directory of home region in target tenancy container. This will create identity components in target OCI console.

<h5> Network Components </h5>

- Execute the toolkit to export all Network Components (Option - 'Export all Network Components' under 'Network') from source tenancy. It will export the data into Excel template networking tabs and also create obj_names.safe file in 'network' service directory of each region.
- There is no need to execute the generated shell script containing the terraform import commands.
- In the exported Excel file, make appropriate changes if any (eg Region name, VCN name or CIDR block etc) to Network tabs.
  Eg: If VCN name needs to be changed for target tenancy, it has to be changed in 'VCN Name' column of VCNs, SubentsVLANs, DHCP, SecRulesinOCI, RouteRulesinOCI tabs and 'Attached To' column of DRGs tab.
- Move obj_names.safe from source region's 'network' directory  to target region's 'network' directory. If any changes are done to VCN name/DRG name/DRG RT name attached to VCN in the Excel, make sure to update corresponding obj_names.safe file as well.
- In the target tenancy container, execute the toolkit for Create Workflow using above Excel sheet. Choose 'Network' in main options and then 'Create Network', 'Security Rules', 'Route Rules', 'DRG Route Rules' from sub-options. Choose 'Customer Connectivity' also in case there are RPCs which need to be established. <br> Choose 'Add/Modify/Delete Security Rules (Reads SecRulesinOCI sheet)', 'Add/Modify/Delete Route Rules (Reads RouteRulesinOCI sheet)', 'Add/Modify/Delete DRG Route Rules (Reads DRGRouteRulesinOCI sheet)', 'Create Remote Peering Connections' from sub-options.
- Execute terraform init, plan and apply from 'network' service directory of each region in target tenancy container. This will create networking components in target OCI console.
- Execute terraform init, plan and apply from 'global/rpc' service directory in target tenancy container. This will create RPCs between regions in target OCI console.

- If the source tenancy contains NSGs or VLANs and need to be replicated to target tenancy, then re run the toolkit in target tenancy and choose 'Network' in main options and then 'Network Security Groups' and 'Add/Modify/Delete VLANs' from sub-options. Choose 'Add/Modify/Delete NSGs (Reads NSGs sheet)' from the sub-options.
- Execute terraform init, plan and apply from 'nsg' and 'vlan' service directories of each region in target tenancy container. This will create NSGs and VLANs in target OCI console.

<h5> Use the same process to replicate any other CD3 supported resources in OCI </h5>

**Method 2: Using the terraform code of source tenancy**
<h5> All OCI Components </h5>

- Execute the toolkit to export Identity Components(Compartments, Groups, Policies, Users, Network Sources) from source tenancy. 
- There is no need to execute the generated shell script containing the terraform import commands.
- Copy the generated *.auto.tfvars from 'identity' service folder of home region in source tenancy container.
- Paste the files to 'identity' service folder of home region in target tenancy container.
- Make appropriate changes in tfvars like name changes.
- Execute terraform init, plan and apply. This will create networking components in target OCI console.
- Execute the toolkit to export the created components from target tenancy. This step is needed to get the target tenancy data into Excel sheet.

