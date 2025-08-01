# CD3 Validator Features

With version v9.0 we have introduced validator for Multiple VCN CIDRs in Networking Tab.
CD3 Validator helps you validate the Compartments, Groups, Policies, Network component entries, Instances, Block Volumes, FSS in your CD3 to ensure error free, smooth creation of the resources when Terraform is applied.

- CD3 Validator runs by default when executing the Create Workflow.

- Users can also manually run the`Validate CD3` option from the menu that appears when executing the `setUpOCI.py` script.

- Log file containing CD3 validator checks is generated at: ```/cd3user/tenancies/<prefix>/<prefix>_cd3validator.log```. <br><br>


Below is a list of checks done by the CD3 Validator:

| Tab Name | Validation/Checks |
|----- | --------------- |
| **Identity** | This covers Compartments, Groups, Policies Tabs.<br><ul><li>Checks if the Region column contains Home Region</li><li>Checks for mandatory columns</li></ul> |
| **VCNs** | <ul><li>Checks if the Columns - Region and Compartment have valid entries.</li><li>Checks if the VCN Names are duplicated in Column - VCN Name for the same region.</li><li>Validates the VCN CIDRs (Single and Multiple) - Checks for Overlapping/Duplicate addresses.</li><li>Checks the VCN CIDR ranges for host bits set.</li><li> Checks if the Column - DNS Label has any special characters.</li><li>Checks for NULL Values if any in all the Columns that is Required/Mandatory.</li></ul> |
| **SubnetsVLANs** | <ul><li>Checks if the Columns - Region and Compartment have valid entries.</li><li>Checks if the VCN Names are part of VCN Tab in Column - VCN Name</li><li>Checks if the Column - DNS Label has any special characters or any Duplicate Values</li><li>Validates the Subnet CIDRs - Checks for Overlapping/Duplicate addresses</li><li>Checks the Subnet CIDR ranges for host bits set.</li><li>Checks for NULL Values if any in all the Columns that is Required/Mandatory</li><li>Cross Validates entries in Subnets and DHCP Tabs for Column - DHCP Options</li><li>Checks if Internet Gateways and Service Gateways are set appropriately.</li><li>Cross Validates entries in Subnets and VCNsTabs for Column - Subnet CIDR (Checks if the Subnet CIDR belongs to / falls under the VCN CIDR as mentioned in the Subnet's Tab)</li></ul> |
| **DHCP** | <ul><li>Checks if the Columns - Region and Compartment have valid entries</li><li>Checks if the VCN Names are part of VCN Tab in Column - VCN Name</li><li>Check if there is value for Customer DNS Column if the entered type is 'CustomDNSServer'</li><li>Checks for NULL Values if any in all the Columns that is Required/Mandatory</li></ul> | 
| **DRGs** | <ul><li>Checks if the Columns - Region and Compartment have valid entries</li><li>Checks if DRG Name entered is as per mentioned in VCNs tab</li><li>Checks for the valid format of Attached To column and if it contains VCN Name as mentioned in VCNs Tab.</li><li>Checks for valid format of column 'Import DRG Route Distribution Statements'</li><li>Checks that column 'Import DRG Route Distribution Statements' cannot have any value if colum 'Import DRG Route Distribution' is empty.</li></ul> |
| **Instances** | <ul><li>Checks if the Columns - Region and Compartment have valid entries</li><li>Checks for mandatory columns - Region, Compartment Name, Availability Domain, Display Name, Network Details, SSH Key Var Name, Pub Address, Source Details, Shape</li><li>Checks if Network Details specified is valid</li><li>Checks for valid values for columns - Availability Domain, Fault Domain, Source Details, Shape</li><li>Checks if the NSG names mentioned in NSGs column are part of NSGs tab of the CD3 excel.</li></ul> |
| **Block Volumes** | <ul><li>Checks if the Columns - Region and Compartment have valid entries</li><li>Checks for mandatory columns Block Name, Availability Domain, Attach Type.</li><li>Checks for valid values for columns - Availability Domain, Attach Type, Attached to Instance.</li><li>Checks if AD mentioned in Block Volumes sheet is same as AD mentioned in Instances sheet for the instance to which block volume is to be attached.</li></ul> |
| **FSS** | <ul><li>Checks if the Columns - Region and Compartment have valid entries</li><li>Checks for mandatory columns - Region, Compartment Name, Availability Domain, MountTarget Name, MountTarget SubnetName.</li><li>Checks if Network Details specified is valid</li><li>Checks if the NSG names mentioned in NSGs column are part of NSGs tab of the CD3 excel.</li></ul> |
| **Budgets** | <ul><li>Checks for mandatory columns(Region/Name/Scope/Schedule/Amount) for Budget creation</li><li>Checks for mandatory parameter (Start Date and End Date ) for Single Use Schedule</li><li>Checks for mandatory parameter (Start Day) for MONTH Schedule</li><li>Value format check for "Alert Rules" column</li><li>Value check for email format in "Alert Recipients" column</li><li>Checks if provided region is home region or not</li></ul> |
| **KMS** | <ul><li>Checks if the Columns - Region, Vault Compartment, Key Compartment, Vault display name, Key display name have valid entries</li><li>Checks if valid protection mode, Key algorithm and key length are provided.</li><li>Checks if auto rotation and rotation interval have valid values.</li></ul> |



**Expected ERRORs in the log file:**

* <I>Compartment Network does not exist in OCI.</I>→ This error means that the component is not found in OCI. So, please make sure to create the Compartment "Network" before validating other tabs.

* <I>Either "Region" ashburn is not subscribed to tenancy or toolkit is not yet configured to be used for this region.</I> → If this is a new region subscribed to the tenancy after toolkit was setup initially then Please re run createTenancyConfig.py with same tenancyconfig.properties to configure the toolkit with the new region.


* For policy statements like below:<br>
```
 allow service loganalytics to {BUCKET_READ} in tenancy 
 allow service loganalytics to {EVENTRULE_READ} in tenancy 
 allow DYNAMIC-GROUP logging_analytics_agent to {LOG_ANALYTICS_LOG_GROUP_UPLOAD_LOGS} in tenancy 
```


&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Validator can report below error which can be ignored:<br>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ```2024-04-24 11:50:08,086 - ROW 41 : Invalid verb used in Policy Statement```
