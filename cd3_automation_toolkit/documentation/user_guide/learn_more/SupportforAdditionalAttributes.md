# Support for Additional Attributes

**Follow the below steps to add an attribute that is not present already in your Excel sheet -**

1. Add the attribute name to the CD3 Excel sheet (based on the resource the attribute belongs to) as given in Terraform Official Documentation.
2. Uncomment the attribute in .tf files (terraform modules in outdirectory, if they are commented). 
3. Uncomment the attribute in Jinja template for the resource attribute. (Resource to Jinja template mapping is available here)
4. Update the variable file for any additional changes like image ocids, ssh public keys, etc

**Example 1: To add an attribute for Instances - (preserve_boot_volume)**

<li>Here is the Terraform Hashicorp documentation for instances - https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/core_instance </li>
<li>Add an additional column preserve_boot_volume to the Instances Sheet as shown below. Optionally change the underscores to spaces for better readability.
</li>

![image](https://user-images.githubusercontent.com/115973871/215402830-d7856e2d-0bd9-43b9-94bd-df039a90b942.png)

<li>Uncomment the parameter in **instances.tf** file as shown below.</li>

![image](https://user-images.githubusercontent.com/115973871/215402973-72857dbd-5efd-40d9-8a7f-3541eb85af66.png)

<li>Uncomment the parameter in **cd3_automation_toolkit\Compute\templates\instance-template** . Any line that is between {# <and> #} are commented in Jinja templates. From the screenshot below we note that the condition for **preserve_boot_volume**  is within the Jinja comments. Copy the highlighted line and place it after/outside line 184 (**#}**) as per below screenshot.</li>

**Before**
  
![image](https://user-images.githubusercontent.com/115973871/215403279-c28634cb-58de-4e72-bfe3-1941b7c28d69.png)

**After**

![image](https://user-images.githubusercontent.com/115973871/215403345-fa24edf5-73d5-4417-ae71-9df216ec95bb.png)

<li>Apart from the above changes, optionally, update the **instance_ssh_keys** and **instance_source_ocids** in your variables file before executing the toolkit to generate the auto.tfvars for instances.</li>


**Exemple 2 : To Add Freeform Tags**

Automation Tool Kit allows the tagging of resources. To use this option, the user is required to add the below column to the appropriate CD3 sheet.
Ex: To Tag your Instances, Open the ‘Instances’ sheet of your CD3 and add the below column at the end.
<li>FreeForm Tags</li>

    Note

    The Tag Values (Default and Freeform Tags) specified will apply to all the resources in the tab.
    Ex: The tags applied to VCNs will not be applied to its objects like IGW, NGW, SGW, LPG, etc
    Empty column values are allowed for FreeForm and Defined Tags; when used it does not attach any tags to the resource. eg: Row 1 in the below example
    Semi Colon is used as Delimiter between multiple tag values (Example as shown below)

Allowed Values for Tags include the following formats: (**Semi-colon** delimited values to be entered)

**Example:**

| S.No | Freeform Tags | Defined Tags |
| --- | --- | --- |
| 1. | | |
| 2. | Network=Test1;Network2=Test40 | Operations.CostCenter=01;Users.Name=user01 |
| 3. | Network=Test2; Network2=Test4 | Application.Env=Dev |
| 4. | Network= | OS.Version= |
| 5. | testing | Platform.Usage |

    Export of new attributes is only supported if the attribute name of Terraform documentation matches that of the Python SDK. Export may fail to fetch the data incase there is a mismatch of the variable names.

## Resource to Template Mapping -

**Added New options for CIS compliance.**

The following Table maps the Excel Sheet to the Resources to the Templates:

**CD3-CIS-template.xlsx:**

|Tab Name/SetUpOCI Option	|Resource Name(OCI Console)	|Jinja2 Template Path	|Jinja2 Template Name!|
| --- | --- | --- | --- |
|<br>VCNs<br>SubnetsDHCP<br>RouteRulesinOCI<br>SecRulesinOCI<br>NSGs</br></br></br></br></br>| **Networking**: Virtual Cloud Networks | cd3_automation_toolkit\Network\BaseNetwork\templates\ | <br>major-objects-drgs-template<br>major-objects-igws-template<br>major-objects-ngws-template<br>major-objects-lpgs-template<br>major-objects-sgws-template<br>major-objects-vcns-template<br>major-objects-drg-attachments-template<br>major-objects-default-dhcp-template<br>subnet-template<br>custom-dhcp-template<br>drg-data-source-template<br>drg-route-distribution-statement-template<br>drg-route-distribution-template<br>drg-route-rule-template<br>drg-route-table-template<br>default-route-table-template<br>route-rule-template<br>route-table-template<br>default-seclist-template<br>seclist-template<br>sec-rule-template<br>nsg-rule-template<br>nsg-template</br></br></br></br></br></br></br></br></br></br></br></br></br></br></br></br></br></br></br></br></br></br></br> |
| Tags | Governance: Tag Namespace | cd3_automation_toolkit\Governance\Tagging\templates | <br>tags-namespaces-template<br>tags-keys-template<br>tags-defaults-template</br></br></br> |
| OSS | Object Storage Bucket | cd3_automation_toolkit\Storage\ObjectStorage\templates | <br>oss-policy-template<br>oss-template</br></br>|
| OKE | Developer Service: Oracle Kubernetes Service | cd3_automation_toolkit\DeveloperServices\OKE\templates\ | <br>cluster-template<br>nodepool-template</br></br> |
| <br>NLB-Listeners<br>NLB-BackendSets-BackendServers</br></br> | Networking: Network Load Balancers | cd3_automation_toolkit\Networking\LoadBalancers\templates\	| <br>nlb-template<br>nlb-backend-set-template<br>nlb-backend-server-template<br>nlb-listener-template<br>nlb-reserved-ips-template</br></br></br></br></br> |
| Logging | <br>VCN Flow Logs<br>Object Storage Bucket Logs</br></br>| cd3_automation_toolkit\ManagementServices\Logging\templates | logging-template |
| ||||





