
#CIS Features

Below CIS Features have been included as part of Automation Toolkit. These are not part of CD3 but just included intoSetUpOCI Menu "**CIS Compliance Features**".

1. Create Key/Vault, Object Storage Bucket and enable Logging for write events to bucket:

Below tf files are created
    
| File name | Description|
|---|---|
|cis-osskeyvault-policy.auto.tfvars |TF variables file for allowing object storage service to use keys. This iscreated in Home region directory.|
|cis-keyvault.auto.tfvars |TF variables file for creating the key/vault in the specified compartmentand region. This is created under the specified region directory.|
|cis-oss.auto.tfvars |TF variables file for creating OSS bucket using above key (instead ofOracle Managed Keys). This is also created under specified region directory.|
|cis-oss-logging.auto.tfvars|TF variables file for enabling logging for write events of the abovecreated bucket. This is also created under specified region directory.|
2. Enable Cloud guard

This will enable cloud guard for tenancy from home region, create Oracle Managed detector and responderrecipes. Also creates a target for root compartment with the default Oracle Managed recipes.
Below TF file is created:

| File name | Description|
|---|---|
|cis-cloudguard.auto.tf |vars TF variables file for enabling cloud guard and creating target for rootcompartment. |

3. Enable VCN Flow Logs

This will enable Flow logs for all the subnets mentioned in Subnets' tab of CD3 Excel sheet. Log group foreach VCN is created under the specified compartment and all subnets are added as logs to this log group.

Below TF file is created:

| File name | Description|
|---|---|
|cis-vcnflow-logging.auto.tfvars |TF variables file containing log group for each VCN and logs for eachsubnet in that VCN.|
