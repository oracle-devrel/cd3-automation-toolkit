# Support for Additional Attributes

**Follow the below steps to add an attribute that is not present already in your Excel sheet -**

1. Add the attribute name to the CD3 Excel sheet (based on the resource the attribute belongs to) as given in Terraform Official Documentation.
2. Uncomment the attribute in .tf files (terraform modules in outdirectory, if they are commented). 
3. Uncomment the attribute in Jinja template for the resource attribute. <a href="#resource-to-template-mapping"><u>Resource to Jinja template mapping is available here</u></a>.
4. Update the variable file for any additional changes like image ocids, ssh public keys, etc

**Example 1: To add an attribute for Instances - (preserve_boot_volume)**

- Here is the Terraform Hashicorp documentation for instances - <a href="https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/core_instance"><u>https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/core_instance</u></a>
- Add an additional column preserve_boot_volume to the Instances Sheet as shown below. Optionally change the underscores to spaces for better readability.

    <img src = "../images/additionalattr-1.png" width=50% height=50%>


- Uncomment the parameter in **instance.tf** file if not already uncommented.

    <img src = "../images/additionalattr-2.png" width=50% height=50%>

- Uncomment the parameter in **cd3_automation_toolkit\Compute\templates\instance-template** . Any line that is between {# <and> #} are commented in Jinja templates. From the screenshot below we note that the condition for **preserve_boot_volume**  is within the Jinja comments. Copy the highlighted line and place it after/outside line 184 (**#}**) as per below screenshot.

    **Before:**
  
    <img src = "../images/additionalattr-3.png" width=50% height=50%>

    **After:**

    <img src = "../images/additionalattr-4.png" width=50% height=50%>


- Apart from the above changes, optionally, update the **instance_ssh_keys** and **instance_source_ocids** in your variables file before executing the toolkit to generate the auto.tfvars for instances.



**Example 2 : To Add Freeform Tags**

- Automation Tool Kit allows the tagging of resources. To use this option, the user is required to add the below column to the appropriate CD3 sheet.
Ex: To Tag your Instances, Open the ‘Instances’ sheet of your CD3 and add the column **FreeForm Tags** at the end.


!!! Note

    The Tag Values (Default and Freeform Tags) specified will apply to all the resources in the tab.
    Ex: The tags applied to VCNs will not be applied to its objects like IGW, NGW, SGW, LPG, etc
    Empty column values are allowed for FreeForm and Defined Tags; when used it does not attach any tags to the resource. eg: Row 1 in the below example
    Semi Colon is used as Delimiter between multiple tag values (Example as shown below)

- Allowed Values for Tags include the following formats: (**semi-colon** delimited values to be entered)

    **Example:**

    | S.No | Freeform Tags | Defined Tags |
    | --- | --- | --- |
    | 1. | | |
    | 2. | Network=Test1;Network2=Test40 | Operations.CostCenter=01;Users.Name=user01 |
    | 3. | Network=Test2; Network2=Test4 | Application.Env=Dev |
    | 4. | Network= | OS.Version= |
    | 5. | testing | Platform.Usage |

- Export of new attributes is only supported if the attribute name of Terraform documentation matches that of the Python SDK. Export may fail to fetch the data incase there is a mismatch of the variable names.

## Resource to Template Mapping


The following Table maps the Excel Sheet to the Resources to the Templates:

**CD3-CIS-template.xlsx:**

|Tab Name/SetUpOCI Option	|Resource Name(OCI Console)	|Jinja2 Template Path	|Jinja2 Template Name!|
| --- | --- | --- | --- |
|<br>VCNs<br>SubnetsDHCP<br>RouteRulesinOCI<br>SecRulesinOCI<br>NSGs</br></br></br></br></br>| **Networking**: Virtual Cloud Networks | cd3_automation_toolkit\Network\BaseNetwork\templates\ | <br>major-objects-drgs-template<br>major-objects-igws-template<br>major-objects-ngws-template<br>major-objects-lpgs-template<br>major-objects-sgws-template<br>major-objects-vcns-template<br>major-objects-drg-attachments-template<br>major-objects-default-dhcp-template<br>subnet-template<br>custom-dhcp-template<br>drg-data-source-template<br>drg-route-distribution-statement-template<br>drg-route-distribution-template<br>drg-route-rule-template<br>drg-route-table-template<br>default-route-table-template<br>route-rule-template<br>route-table-template<br>default-seclist-template<br>seclist-template<br>sec-rule-template<br>nsg-rule-template<br>nsg-template |
| Tags | Governance: Tag Namespace | cd3_automation_toolkit\Governance\Tagging\templates | <br>tags-namespaces-template<br>tags-keys-template<br>tags-defaults-template</br></br> |
| OSS | Object Storage Bucket | cd3_automation_toolkit\Storage\ObjectStorage\templates | <br>oss-policy-template<br>oss-template</br></br>|
| OKE | Developer Service: Oracle Kubernetes Service | cd3_automation_toolkit\DeveloperServices\OKE\templates\ | <br>cluster-template<br>nodepool-template</br></br> |
| <br>NLB-Listeners<br>NLB-BackendSets-BackendServers</br></br> | Networking: Network Load Balancers | cd3_automation_toolkit\Networking\LoadBalancers\templates\	| <br>nlb-template<br>nlb-backend-set-template<br>nlb-backend-server-template<br>nlb-listener-template<br>nlb-reserved-ips-template |
| Logging | <br>VCN Flow Logs<br>Object Storage Bucket Logs</br></br>| cd3_automation_toolkit\ManagementServices\Logging\templates | logging-template |
| <br>LB-Hostname-Certs<br>BackendSet-BackendServer<br>RuleSet<br>PathRouteSet<br>LB-Listener</br></br> | Networking: Load Balancers | cd3_automation_toolkit\Networking\LoadBalancers\templates\ | <br>lbr-template<br>certificate-template<br>hostname-template<br>cipher-suite-template<br>backend-server-template<br>backend-set-template<br>rule-set-template<br>access-control-rules-template<br>access-method-rules-template<br>http-header-rules-template<br>request-response-header-rules-template<br>uri-redirect-rules-template<br>path-route-set-template<br>path-route-rules-template<br>listener-template<br>lbr-reserved-ips-template</br></br>|
| Key Vault | Key and Vault | cd3_automation_toolkit\Security\KeyVault\templates | <br>keys-template<br>vaults-template</br></br>|
| FSS | File Storage: File Systems | cd3_automation_toolkit\Storage\FileStorage\templates\ | <br>fss-template<br>export-resource-template<br>export-options-template<br>mount-target-template</br></br>|
| <br>DedicatedVMHosts<br>Instances</br></br> | Compute:<br>Dedicated Virtual Machine Hosts<br>Instances</br></br> | cd3_automation_toolkit\Compute\templates\ | <br>dedicatedvmhosts-template<br>instances-template</br></br>|
| <br>Compartments<br>Groups<br>Policies</br></br> | Identity: <br>Compartments<br>Groups<br>Dynamic Groups<br>Policies</br></br></br></br> | <br>cd3_automation_toolkit\Identity\Compartments\templates\ <br> cd3_automation_toolkit\Identity\Groups\templates\ <br> cd3_automation_toolkit\Identity\Policies\templates\ </br></br> | <br>compartments-template<br>groups-template<br>policies-template</br></br> |
| Cloud Guard | Cloud Guard | cd3_automation_toolkit\Security\CloudGuard\templates | <br>cloud-guard-config-template<br>cloud-guard-target-template</br></br>|
| Budgets | Governance: Budgets | cd3_automation_toolkit\Governance\Billing\templates | <br>budget-alert-rule-template<br>budget-template</br></br> |
| BlockVolumes	| Block Storage: Block Volumes	| cd3_automation_toolkit\Storage\BlockVolume\templates\	| blockvolumes-template |
| <br>ADB<br>DBSystems-VM-BM<br>EXA-Infra<br>EXA-VMClusters</br></br> | <br>Autonomous Data Warehouse<br>Autonomous Transaction Processing<br>Bare Metal, VM and Exadata Infra, <br>and Exadata VM Clusters</br></br> | cd3_automation_toolkit\Database\templates\ | <br>adb-template<br>dbsystems-vm-bm-template<br>exa-infra-template<br>exa-vmclusters-template</br></br>|


**CD3-CIS-ManagementServices-template.xlsx**

|Tab Name/SetUpOCI Option	|Resource Name(OCI Console)	|Jinja2 Template Path	|Jinja2 Template Name!|
| --- | --- | --- | --- |
| <br>Notifications<br>Events<br>Alarms<br>ServiceConnectors</br></br> | Application Integration:<br>Notification<br>Events Service<br>Alarms<br>Service Connector Hub</br></br> | <br>cd3_automation_toolkit\ManagementServices\EventsAndNotifications\templates\ <br> cd3_automation_toolkit\ManagementServices\Monitoring\templates\ <br> cd3_automation_toolkit\ManagementServices\ServiceConnectorHub\templates\ </br></br> | <br>actions-template<br>events-template<br>notifications-topics-template<br>notifications-subscriptions-template<br>service-connectors-template</br></br> |




