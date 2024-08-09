# Networking Scenarios 

   - [Export Network](#export-network)
   - [Add a new or modify the existing networking components](#add-a-new-or-modify-the-existing-networking-components)


!!! note
      Before starting with Network Export, make sure to run 'Fetch Compartments OCIDs to variables file'.

### Export Network

Follow the below steps to export the Networking components that includes VCNs, Subnets, DHCP, DRG, Security List, Route Tables, DRG Route Tables, NSGs, etc to CD3 Excel Sheet and create the Terraform state.

1. Use the [CD3-Blank-Template.xlsx](https://github.com/oracle-devrel/cd3-automation-toolkit/blob/main/cd3_automation_toolkit/example) to export the networking resources into the Tabs - VCNs, DRGs, VCN Info, DHCP, Subnets, NSGs, RouteRulesInOCI, SecRulesInOCI,DRGRouteRulesInOCI tabs. <br>
 
2. Execute the _setupOCI.py_ file with _workflow_type_ parameter value to _export_resources_: 
   ```
   python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties
   ``` 

3. Choose one of the below available sub-options from _'Export Network'_ of the main menu. 
      - Export all Network Components
      - Export Network components for VCNs, DRGs and DRGRouteRulesinOCI Tabs
      - Export Network components for DHCP Tab
      - Export Network components for SecRulesinOCI Tab
      - Export Network components for RouteRulesinOCI Tab
      - Export Network components for SubnetsVLANs Tab
      - Export Network components for NSGs Tab
   
     Once the execution is successful, networking related .tfvars files and .sh files containing import statements will be generated under the folder ```/cd3user/tenancies/<customer_name>/terraform_files/<region_dir>/<service_dir>```
   
     Also,The RPC related .tfvars and .sh files containing import statements will be generated in global directory which is inside the ```/cd3user/tenancies/<customer_name>/terraform_files/``` folder. 

!!! note
       The **oci_core_drg_attachment_management** for RPC resources will be shown as created at the end of import process, but it doesn't actually create any resources and can be safely ignored.

<img width="870" alt="rpc" src="../images/clinetworkexport-1.png">
    
   Navigate to the above path and execute the terraform commands:
       ```
		terraform init
       ```
       ```
		terraform plan
       ```
       ```
		terraform apply
       ```
   → Terraform Plan must show that all the components are in sync.
   
This completes the export of Networking components from OCI.

**Sample of CD3 Excel after export:**
<br>(DO NOT Modify the highlighted columns)

(Showing old images below)
<br>VCNs tab:
![image](../images/clinetworkexport-2.png)

Subnets tab:
![image](../images/clinetworkexport-3.png)


<br>[Go back to Networking Scenarios](#networking-scenarios)
### Add a new or modify the existing networking components
1. Export the Networking components by following the steps [above](#export-network). (Note that here _workflow_type_ flag is set to export_resources)
2. Follow the [process](createnetwork-cli.md#modify-network) to add new components such as VCN/DHCP/DRG/IGW/NGW/SGW/LPG/Subnet etc. (Note that here _workflow_type_ flag is set to create_resources)

