List validate_cd3 = ["<b>CD3 Validator</b>:disabled","Validate Compartments","Validate Groups","Validate Policies","Validate Tags","Validate Budgets","Validate Network(VCNs, SubnetsVLANs, DHCP, DRGs)","Validate DNS","Validate Instances","Validate Block Volumes","Validate FSS","Validate Buckets","Validate KMS"]
List identity  = ["<b>IDENTITY</b>:disabled","Add/Modify/Delete Compartments", "Add/Modify/Delete Groups","Add/Modify/Delete Policies", "Add/Modify/Delete Users", "Add/Modify/Delete Network Sources"]
List governance  = ["<b>GOVERNANCE</b>:disabled","Tags", "Quotas"]
List cost_management  = ["<b>COST MANAGEMENT</b>:disabled","Budgets"]
List network  = ["<b>NETWORK</b>:disabled","Create Network", "Modify Network","Security Rules", "Route Rules", "DRG Route Rules", "Network Security Groups", "Add/Modify/Delete VLANs", "Customer Connectivity"]
List oci_firewall  = ["<b>OCI FIREWALL</b>:disabled","Validate Firewall CD3 Excel", "Add/Modify/Delete Firewall Policy","Add/Modify/Delete Firewall", "Clone Firewall Policy"]
List dns_management = ["<b>DNS</b>:disabled","Add/Modify/Delete DNS Views/Zones/Records", "Add/Modify/Delete DNS Resolvers"]
List compute  = ["<b>COMPUTE</b>:disabled","Add/Modify/Delete Dedicated VM Hosts", "Add/Modify/Delete Instances/Boot Backup Policy"]
List storage = ["<b>STORAGE</b>:disabled","Add/Modify/Delete Block Volumes/Block Backup Policy", "Add/Modify/Delete File Systems", "Add/Modify/Delete Object Storage Buckets"]
List database = ["<b>DATABASE</b>:disabled","Add/Modify/Delete Virtual Machine or Bare Metal DB Systems", "Add/Modify/Delete EXA Infra and EXA VM Clusters", "Add/Modify/Delete ADBs", "Add/Modify/Delete MySQL DBs"]
List load_balancers = ["<b>LOAD BALANCERS</b>:disabled","Add/Modify/Delete Load Balancers", "Add/Modify/Delete Network Load Balancers"]
List management_services = ["<b>MANAGEMENT SERVICES</b>:disabled","Add/Modify/Delete Notifications", "Add/Modify/Delete Events", "Add/Modify/Delete Alarms", "Add/Modify/Delete ServiceConnectors"]
List developer_services = ["<b>DEVELOPER SERVICES</b>:disabled","Add/Modify/Delete OKE Cluster and Nodepools"]
List security = ["<b>SECURITY</b>:disabled","Add/Modify/Delete KMS (Keys/Vaults)", "Enable Cloud Guard"]
List logging_services = ["<b>LOGGING SERVICES</b>:disabled","Enable VCN Flow Logs", "Enable LBaaS Logs", "Enable Object Storage Buckets Logs", "Enable File Storage Logs", "Enable Network Firewall Logs"]
List cd3_services = ["<b>CD3 SERVICES</b>:disabled","Fetch Compartments OCIDs to variables file", "Fetch Protocols to OCI_Protocols"]
//List utility_services = ["<b>Other OCI Tools</b>:disabled","CIS Compliance Check Script", "ShowOCI Report", "Execute VizOCI", "OCI FSDR"]
List utility_services = ["<b>Other OCI Tools</b>:disabled","CIS Compliance Check Script", "ShowOCI Report", "OCI FSDR"]
List ex_identity = ["<b>IDENTITY</b>:disabled","Export Compartments", "Export Groups", "Export Policies", "Export Users", "Export Network Sources"]
List ex_governance  = ["<b>GOVERNANCE</b>:disabled","Export Tags", "Export Quotas"]
List ex_cost_management  = ["<b>COST MANAGEMENT</b>:disabled","Export Budgets"]
List ex_network = ["<b>NETWORK</b>:disabled","Export all Network Components", "Export Network components for VCNs/DRGs/DRGRouteRulesinOCI Tabs", "Export Network components for DHCP Tab", "Export Network components for SecRulesinOCI Tab", "Export Network components for RouteRulesinOCI Tab", "Export Network components for SubnetsVLANs Tab", "Export Network components for NSGs Tab"]
List ex_firewall = ["<b>OCI FIREWALL</b>:disabled","Export Firewall Policy", "Export Firewall"]
List ex_dns = ["<b>DNS</b>:disabled","Export DNS Views/Zones/Records", "Export DNS Resolvers"]
List ex_compute = ["<b>COMPUTE</b>:disabled","Export Dedicated VM Hosts", "Export Instances (excludes instances launched by OKE)"]
List ex_storage = ["<b>STORAGE</b>:disabled","Export Block Volumes/Block Backup Policy", "Export File Systems", "Export Object Storage Buckets"]
List ex_databases = ["<b>DATABASE</b>:disabled","Export Virtual Machine or Bare Metal DB Systems", "Export EXA Infra and EXA VMClusters", "Export ADBs", "Export MySQL DBs"]
List ex_lb = ["<b>LOAD BALANCERS</b>:disabled","Export Load Balancers", "Export Network Load Balancers"]
List ex_management = ["<b>MANAGEMENT SERVICES</b>:disabled","Export Notifications", "Export Events", "Export Alarms", "Export Service Connectors"]
List ex_developer = ["<b>DEVELOPER SERVICES</b>:disabled","Export OKE cluster and Nodepools"]
List ex_security = ["<b>SECURITY</b>:disabled","Export KMS (Keys/Vaults)"]

List final_list = []
for (item in MainOptions.split(",")) {
if (item.equals("Validate CD3")){
final_list += validate_cd3
}
if (item.equals("Identity")){
final_list += identity
}
if (item.equals("Governance")){
final_list += governance
}
if (item.equals("Cost Management")){
final_list += cost_management
}
if (item.equals("Compute")){
final_list += compute
}
if (item.equals("Network")){
final_list += network
}
if (item.equals("OCI Firewall")){
final_list += oci_firewall
}
if (item.equals("DNS Management")){
final_list += dns_management
}
if (item.equals("Storage")){
final_list += storage
}
if (item.equals("Database")){
final_list += database
}
if (item.equals("Load Balancers")){
final_list += load_balancers
}
if (item.equals("Management Services")){
final_list += management_services
}
if (item.equals("Developer Services")){
final_list += developer_services
}
if (item.equals("Security")){
final_list += security
}
if (item.equals("Logging Services")){
final_list += logging_services
}
if (item.equals("CD3 Services")){
final_list += cd3_services
}
if (item.equals("Other OCI Tools")){
final_list += utility_services
}
if (item.equals("Export Identity")){
final_list += ex_identity
}
if (item.equals("Export Governance")){
final_list += ex_governance
}
if (item.equals("Export Cost Management")){
final_list += ex_cost_management
}
if (item.equals("Export Network")){
final_list += ex_network
}
if (item.equals("Export OCI Firewall")){
final_list += ex_firewall
}
if (item.equals("Export DNS Management")){
final_list += ex_dns
}
if (item.equals("Export Compute")){
final_list += ex_compute
}
if (item.equals("Export Storage")){
final_list += ex_storage
}
if (item.equals("Export Databases")){
final_list += ex_databases
}
if (item.equals("Export Load Balancers")){
final_list += ex_lb
}
if (item.equals("Export Management Services")){
final_list += ex_management
}
if (item.equals("Export Developer Services")){
final_list += ex_developer
}
if (item.equals("Export Security")){
final_list += ex_security
}
}

return final_list