
## Additional CIS Compliance Features

These are some additional "**CIS Compliance Features**" which are not part of CD3 Excel sheet but just included into setUpOCI Menu.

#### **1. Run CIS compliance checker script**

You can choose to run CIS compliance checker script against your tennacy using the Automation Toolkit itself. It also enables you to download the latest script if needed. Folder with name _<customer\_name>\_cis\_report_ gets created under _/cd3user/tenancies/<customer\_name>/_ and it contains all the reports genertaed by the script.
<br>As a best practice, the script should be executed after every deployment in the tenancy. The output report should be analysed to minimise the reported anomalies as per the design requirements.

#### **2. Create Key/Vault:**

Below tf file is created
    
| File name | Description|
|---|---|
|cis-keyvault.auto.tfvars |TF variables file for creating the key/vault in the specified compartment and region. This is created under the specified region directory.|


#### **3. Create Default Budget:**

This option will ask for monthly budget (in US$) and Threshold percentage of Budget and bellow tf files are created:

| File name | Description|
|---|---|
|cis-budget.auto.tfvars |TF variables file for crating budget.|

#### **4. Enable Cloud guard**

This will enable Cloud guard for tenancy from home region, creates Oracle Managed/cloned detector and responder recipes. Creates a target for root compartment with the default/cloned Oracle Managed recipes and attaches the recipes to the target.

Below TF file is created:

| File name | Description|
|---|---|
|cis-cloudguard.auto.tf |vars TF variables file for enabling cloud guard and creating target for root compartment. |

#### **5. Enable VCN Flow Logs**

This will enable Flow logs for all the subnets mentioned in Subnets' tab of CD3 Excel sheet. Log group for each VCN is created under the same compartment as specified for VCN and all subnets are added as logs to this log group.

Below TF file is created:

| File name | Description|
|---|---|
|<customer_name>_vcnflow-logging.auto.tfvars |TF variables file containing log group for each VCN and logs for eachsubnet in that VCN.|
