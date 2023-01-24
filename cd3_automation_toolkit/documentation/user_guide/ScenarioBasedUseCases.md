# Scenario Based UseCases

This page will give you an insight into the usual usecases that can be performed with Automation Toolkit.

## NOTE:

1. Automation Tool Kit DOES NOT support the creation/export of duplicate resources.
2. DO NOT modify/remove any commented rows or column names. You may re-arrange the columns if needed (except NSGs).
3. A double colon (::) or Semi-Colon (;) has a special meaning in the Tool Kit. Do not use them in the OCI data / values.
4. Do not include any unwanted space in cells you fill in; do not place any empty rows in between.
5. To learn about how to add attributes, refer [Support for additional attributes](https://confluence.oraclecorp.com/confluence/display/NAC/Support+for+additional+attributes) (Flat TF Files)
6. Any entry made/moved post \<END> in any of the Tabs, of CD3 will not be processed. Any resources created by the automation & then moved after the \<END> will cause the resources to be removed. 
7. The components that get created as part of VCNs Tab (Example: IGW, SGW, LPG, NGW, DRG) will have the same set of Tags attached to them.
8. Automation Tool Kit does not support sharing of Block Volumes.
9. Detail on the know behaviour of the toolkit can be found at [Known Behaviour Of Automation Toolkit](https://confluence.oraclecorp.com/confluence/display/NAC/Known+Behaviour+Of+Automation+Toolkit)
10. Option to Modify Network - 
  
    Some points to consider while modifying networking components are - 
  
    a. Converting the exported VCN to Hub/Spoke/Peer VCN is not allowed. Route Table rules based on the peering for new LPGs to existing VCNs will not be auto populated. Users are requested to add an entry to the RouteRulesInOCI sheet to support the peering rules.
    
    b. Adding a new VCN as Hub and other new VCNs as Spoke/Peer is allowed. Gateways will be created as specified in VCNs sheet. 
    
    c. Adding new VCNs as None is allowed. Gateways will be created as specified in VCNs sheet.
    
    d. The addition of new Subnets to exported VCNs and new VCNs is allowed.
  
  | Scenarios| Execution Steps  |
  | --- | --- |
  | Validate CD3 | **Steps** <li>Modify the setUpOCI.properties file to set non_gf_tenancy to "false"</li><li>Execute setUpOCI.py and choose the service from the menu options. Choose "Validate CD3"</li><li>Choose the options from sub-menu. Make sure to have created Identity (terraform apply) before you validate Tags, Network, Compute, Storage, Database, LoadBalancers and Management Services</li> **Expected ERROR**: Compartment Network does not exist in OCI.→ These error mean that the component is not found in OCI. So, please make sure to create the Compartment "Network" before validating other tabs. |
| Greenfield - Create new components| **Steps** <li>Modify the setUpOCI.properties file to set non_gf_tenancy to "false".</li><li>Execute setUpOCI.py and choose the service from the menu options.</li> |
| NonGreenfield/Export existing components from tenancy  | **Steps** <li>Modify the setUpOCI.properties file to set non_gf_tenancy to "true".</li><li>Execute setUpOCI.py and choose the service from the menu options.</li> |
| Greenfield - Create Identity components| **Steps** <li>Modify the setUpOCI.properties file to set non_gf_tenancy to "false".</li><li>Execute setUpOCI.py and choose the service from the menu options → Choose "Identity" → Choose "Create Compartments" and "Create Groups"</li><li>Change directory to that of outdir and execute terraform init/plan/apply.</li><li>Change your directory to /cd3user/tenancies/\<prefix>, cat cmds.log. Copy and execute the command for fetch compartments to tf vars.</li><li>Execute setUpOCI.py and choose the service from the menu options →  Choose "Identity" → Choose "Create Policies"</li><li>Execute Terraform Plan and Trerraform Apply in outdir.</li>|
| Use an existing DRG in OCI while creating the network | **Steps** <li>Modify the setUpOCI.properties file to set non_gf_tenancy to "false".</li><li>Execute setUpOCI.py and choose the service from the menu options → Choose "Network" → Choose "Create Network"</li><li>Change directory to that of outdir and execute terraform init </li><li>Import the DRG into your state file. Execute ```terraform import "module.drgs[\"<<drgs terraform variable name>>\"].oci_core_drg.drg" <<drg ocid>>```</li><li> 5.Execute Terraform Plan and Trerraform Apply in outdir. Terraform Plan will indicate to add all the other components except DRG</li> |
| Add a new Network Component - VCN/DHCP/DRG/Subnet| **Steps** <li>Modify the setUpOCI.properties file to set non_gf_tenancy to "false".</li><li>Add the data to the appropriate Excel sheets.</li><li>Execute setUpOCI.py and choose "Network".</li><li>Choose sub-menu → "Modify Network".</li> **Note**: Make sure to export Sec Rules, Route Rules, DRG Route Rules (Option 3,4 of sub-menu) to CD3 Excel Sheet before executing this option.|
| Add a new Compute VM to an existing Infrastructure  (such as Identity, Network) in OCI | **Steps** <li>Modify the setUpOCI.properties file to set non_gf_tenancy to "true".</li><li>Execute setUpOCI.py and choose "Export Network"from the menu options.</li><li>Execute the generated shell script to sync the Terraform with existing network components of OCI.</li><li>Add the new VM details to the Excel sheet.</li><li>Modify the setUpOCI.properties file to set non_gf_tenancy to "false".</li><li>Execute setUpOCI.py and choose "Network" and then "Add/Modify/Delete Instances/Boot Backup Policy" from the menu options.</li><li>Execute Terraform Plan and Trerraform Apply in outdir.</li>|
| To add a new Route Table/Update existing Route Rules/Add new Route Rules/Delete existing Route Rules/Delete existing Route Table/ Add new Security List/ Update existing Security Rule/ Add new Security Rules/Delete existing Security Rules <br/>**Note**: This will create TF for only those Security Lists and Route Tables in VCNs which are part of cd3 and skip any VCNs that have been created outside of cd3 execution. | **Steps** <li>Modify the setUpOCI.properties file to set non_gf_tenancy to "false".</li><li>Add/Update the data to the appropriate Excel sheets.(RouteRulesInOCI, SecRulesInOCI, DRGRouteRulesInOCI).</li><li>Execute setUpOCI.py and choose "Network".</li><li>Choose sub-menu options "Modify SecRules"/ "Modify RouteRules"/ "Modify DRG RouteRules" or a combination of these according to the requirement.</li> |
| Add new components after export of non-greenfield tenancy - For Networking - VCN/DHCP/DRG/IGW/NGW/SGW/LPG/Subnet | **Steps** <li>Modify the setUpOCI.properties file to set non_gf_tenancy to "false".</li><li>Add the data to the appropriate Excel sheets.</li><li>Execute setUpOCI.py and choose "Network".</li><li>Choose sub-menu option  "Modify Network".</li>|
| To Export Instances in batches using different filters | **Steps** <li>Modify the setUpOCI.properties file to set non_gf_tenancy to "true".</li><li>Choose "Export Compute".</li><li>Specify the prefix of the instances to export or specify the AD to export.</li><li>Once the execution completes, take a backup of the files generated for instances in out directory( *_instances.tfvars and tf_import_cmds_instances_nonGF.sh) and a backup of the 'Instances' tab of the Input CD3 Excel Sheet.</li><li>Repeat steps from 1 to 4 to export next set of Instances using another filter.</li><li>Once you export all the required instances using multiple filters, move the files from backup to the out directory and then execute all the shell scripts generated for Instances. Consolidate the data of exported instances from the Excel sheet backups.</li> |

# Sample of CD3 after export:

(DO NOT Modify the highlighted columns)

VCNs tab:

![image](https://user-images.githubusercontent.com/115973871/214372501-65e68d60-bedd-4df9-bf84-a2316d0f6c62.png)

Subnets tab:

![image](https://user-images.githubusercontent.com/115973871/214372535-69714cbc-1980-4dd5-ae52-e20441903d8a.png)


