## Expected Behaviour Of Automation Toolkit

### NOTE:
1. Automation Tool Kit DOES NOT support the creation/export of duplicate resources.
2. DO NOT modify/remove any commented rows or column names. You may re-arrange the columns if needed (except NSGs).
3. A double colon (::) or Semi-Colon (;) has a special meaning in the Tool Kit. Do not use them in the OCI data / values.
4. Do not include any unwanted space in cells you fill in; do not place any empty rows in between.
5. Any entry made/moved post \<END> in any of the tabs of CD3 will not be processed. Any resources created by the automation & then moved after the \<END> will cause the resources to be removed. 
6. The components that get created as part of VCNs Tab (Example: IGW, SGW, LPG, NGW, DRG) will have the same set of Tags attached to them.
7. Automation Tool Kit does not support sharing of Block Volumes.
8. Some points to consider while modifying networking components are:
   - Converting the exported VCN to Hub/Spoke/Peer VCN is not allowed. Route Table rules based on the peering for new LPGs to existing VCNs will not be auto populated. Users are requested to add an entry to the RouteRulesInOCI sheet to support the peering rules.
   - Adding a new VCN as Hub and other new VCNs as Spoke/Peer is allowed. Gateways will be created as specified in VCNs sheet. 
   - Adding new VCNs as None is allowed. Gateways will be created as specified in VCNs sheet.
   - The addition of new Subnets to exported VCNs and new VCNs is allowed.
  
### Terraform Behavior
- Create a Load Balancer with Reserved IP: When you create a LBaaS with reserved ip as "Y" and do a terraform apply, everything will go smooth and be in sync for the first time. If you do a terraform plan immediately (post apply), you will find that the plan changes the private ip of load balancer to null.


  ![image](https://user-images.githubusercontent.com/122371432/214501615-c84d26bb-1227-42b7-bc86-a6f82020aab0.png)

  This is a behaviour of Terraform.  In these scenarios, please add the private ip ocid to the auto.tfvars as shown below before you run a terraform plan again.

  <img src ="https://user-images.githubusercontent.com/122371432/214501874-c27bb4cd-4506-4914-b837-4f30c90309f0.png" width=75% height=75%>

  Once you do the above change, and then execute a terraform plan/apply, you will get the below error and it can be ignored.

  ![image](https://user-images.githubusercontent.com/122371432/214502222-09eb5bb2-4a21-43fa-89b9-6540324c7f75.png)
  
  
- While exporting and synching the tfstate file for LBaaS Objects, the user may be notified that a few components will be modified on apply. In such scenarios, add the attributes that the Terraform notifies to be changed to the appropriate CD3 Tab of Load Balancer and uncomment the parameter from Jinja2 Templates and Terraform (.tf) files. Re-run the export.

- Add a new column - "Freeform Tags" to the CD3 Excel Sheets as per necessity, to export the tags associated with the resource as well. If executed as-is, Terraform may prompt you to modify resources based on Tags.
  
  **Example:**
  
  <img src = "https://user-images.githubusercontent.com/122371432/214502914-61aeb3b6-923a-481e-95a2-f2d5d78e6e45.png" width =50% height=50%>
  
- Toolkit will create TF for only those DRGs which are part of CD3 and skip Route Tables for the DRGs created outside of CD3. This will also synch DRG rules in your tenancy with the terraform state.
  
  > **Note**
  > When there are changes made in the OCI console manually, the above options of export and modify can be helpful to sync up the contents/objects in OCI to TF.

- Match All criteria specified for Route Distribution Statement In DRGs sheet will show below output each time you do terraform plan:

  ![image](https://user-images.githubusercontent.com/122371432/214504858-2c5ba6af-b030-4f72-b6d9-8bc37b5902cf.png)
  
  The service api is designed in such a way that it expects an empty list for match all. And it sends back an empty list in the response every time. Hence this behaviour from terraform side. This can be safely ignored.

- Export process for non greenfield tenancies v6.0 or higher doesn't support OCI objects having duplicate names like for Policies, for VCNs having same names with in a region or subnets having same names within a VCN. You will get output similiar to below when terraform plan is run (Option 3 with non-gf_tenancy set to true)
  
  ***_Error: Duplicate resource "oci_identity_policy" configuration_***
  
- Export process for non greenfield tenancies v6.0 or higher will try to revert SGW for a VCN to point to all services if it was existing for just object storage. You will get output similiar to below when terraform plan is run (Option 3 with non-gf_tenancy set to true).

  ```
  # oci_core_service_gateway.VCN_sgw will be updated in-place

  ~ resource "oci_core_service_gateway" "VCN_sgw" {

        block_traffic  = false

        compartment_id = "ocid1.compartment.oc1..aaaaaaaahsesjfw5hhftccsvndbufdlf5ca2c3q3clyvwg4wngj4ej26i3ya"

        display_name   = "VCN_sgw"
        freeform_tags  = {}

        id             = "ocid1.servicegateway.oc1.iad.aaaaaaaajqtpjqy7ihgikmug5kbz55pztymt7m6t4ijlqek5ujqg3qxeaxma"

        state          = "AVAILABLE"

        time_created   = "2019-03-19 16:46:33.859 +0000 UTC"

        vcn_id         = "ocid1.vcn.oc1.iad.aaaaaaaazjup6ahpesjgrjyaxr2bcnx44tpn3ygvx2tjylytgkub5ikl6rha"


      - services {

          - service_id   = "ocid1.service.oc1.iad.aaaaaaaa74z6sqsezqf6znyomdp5jkvfwb4j2ol33abgosvnhxcqphyl3eaq" -> null

          - service_name = "OCI IAD Object Storage" -> null

        }

      + services {

          + service_id   = "ocid1.service.oc1.iad.aaaaaaaam4zfmy2rjue6fmglumm3czgisxzrnvrwqeodtztg7hwa272mlfna"

          + service_name = (known after apply)

        }

        timeouts {}

    }
  ```
  
### Modification Process
- When there is a change to any of the instance parameters, the volume policy assignment will get recreated. Example: If you want to add a NSG to the instance, you will be notified on a read to the boot volume ocids, modification to the instance and, a create and destruction of the policy assignment. Screenshot below for reference. This behaviour is expected and in order to not have the backup policy recreated, comment the depends_on statement in modules/compute/data.tf at line around 35.

   ![image](https://user-images.githubusercontent.com/122371432/214506185-58c8702f-de87-4fb1-8a29-1a7623b699c4.png)
   
  <br><br>
<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/RestructuringOutDirectory.md">:arrow_backward: Prev</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/FAQ.md">Next :arrow_forward:</a> |
| :---- | -------: |
  
</div>  
