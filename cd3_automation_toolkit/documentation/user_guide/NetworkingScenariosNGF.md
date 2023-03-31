# Networking Scenarios

## Non-Greenfield Tenancies (Managing Network for Non Green Field Tenancies)
- [Export Network](#non-greenfield-tenancies)
- [Add a new or modify the existing networking components](#add-a-new-or-modify-the-existing-networking-components)


**NOTE-**
Before you start with Network Export, make sure you have run 'Fetch Compartments OCIDs to variables file'.

### Export Network

Follow the below steps to export the Networking components that includes VCNs, Subnets, DHCP, DRG, Security List, Route Tables, DRG Route Tables, NSGs, etc to CD3 Excel Sheet and create the Terraform state.

1. Use the [CD3-Blank-Template.xlsx](/cd3_automation_toolkit/example) to export the networking resources into the Tabs - VCNs, DRGs, VCN Info, DHCP, Subnets, NSGs, RouteRulesInOCI, SecRulesInOCI,DRGRouteRulesInOCI tabs.
   
2. Execute the _setupOCI.py_ file with _non_gf_tenancy_ parameter value to _true_:
   
   ```python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties```
   
3. Choose one of the below available sub-options from _'Export Network'_ of the main menu. 
   - Export all Network Components
   - Export Network components for VCNs, DRGs and DRGRouteRulesinOCI Tabs
   - Export Network components for DHCP Tab
   - Export Network components for SecRulesinOCI Tab
   - Export Network components for RouteRulesinOCI Tab
   - Export Network components for Subnets Tab
   - Export Network components for NSGs Tab
   
   Once the execution is successful, networking related .tfvars files and .sh files containing import statements will be generated under the folder _/cd3user/tenancies/<customer\_name>/terraform_files/<region_dir>_
    
   Navigate to the above path and execute the terraform commands:<br>
       <br>_terraform init_
       <br>_Execute the shell scirpts of networking components_
       <br>_terraform plan_
       <br>&nbsp;&nbsp;→ Terraform Plan must show that all the components are in sync.
   
This completes the export of Networking components from OCI.

**Sample of CD3 Excel after export:**
<br>(DO NOT Modify the highlighted columns)

VCNs tab:
![image](https://user-images.githubusercontent.com/115973871/214372501-65e68d60-bedd-4df9-bf84-a2316d0f6c62.png)

Subnets tab:
![image](https://user-images.githubusercontent.com/115973871/214372535-69714cbc-1980-4dd5-ae52-e20441903d8a.png)

<br>[Go back to Networking Scenarios](#non-greenfield-tenancies)
### Add a new or modify the existing networking components
1. Export the Networking components by following the steps [above](#1-export-network). (Note that here _non\_gf\_tenancy_ flag is set to true)
2. Follow the [process](/cd3_automation_toolkit/documentation/user_guide/NetworkingScenariosGF.md#modify-network) to add new components such as VCN/DHCP/DRG/IGW/NGW/SGW/LPG/Subnet etc. (Note that here _non\_gf\_tenancy_ flag is set to false)

<br>[Go back to Networking Scenarios](#non-greenfield-tenancies)


<br><br>
<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/NonGreenField.md">:arrow_backward: Prev</a> | <a href="/README.md#table-of-contents-bookmark">Main Menu :arrow_forward:</a> |
| :---- | -------: |
  
</div>
