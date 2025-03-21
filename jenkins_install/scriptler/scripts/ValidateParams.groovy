def validate_params(Workflow,MainOptions,SubOptions,SubChildOptions,AdditionalFilters){
    valid_params = "Passed"
    def gf_options_map = [
    "Validate CD3":["Validate Compartments","Validate Groups","Validate Policies","Validate Tags","Validate Budgets","Validate Network(VCNs, SubnetsVLANs, DHCP, DRGs)","Validate DNS","Validate Instances","Validate Block Volumes","Validate FSS","Validate Buckets","Validate KMS"],
    "Identity":["Add/Modify/Delete Compartments", "Add/Modify/Delete Groups","Add/Modify/Delete Policies", "Add/Modify/Delete Users", "Add/Modify/Delete Network Sources"],
    "Governance":["Tags", "Quotas"],
	"Cost Management":["Budgets"],
	"Network":["Create Network", "Modify Network","Security Rules", "Route Rules", "DRG Route Rules", "Network Security Groups", "Add/Modify/Delete VLANs", "Customer Connectivity"],
    "OCI Firewall":["Validate Firewall CD3 Excel", "Add/Modify/Delete Firewall Policy","Add/Modify/Delete Firewall", "Clone Firewall Policy"],
    "DNS Management":["Add/Modify/Delete DNS Views/Zones/Records", "Add/Modify/Delete DNS Resolvers"],
    "Compute":["Add/Modify/Delete Dedicated VM Hosts", "Add/Modify/Delete Instances/Boot Backup Policy"],
    "Storage":["Add/Modify/Delete Block Volumes/Block Backup Policy", "Add/Modify/Delete File Systems", "Add/Modify/Delete Object Storage Buckets"],
    "Database":["Add/Modify/Delete Virtual Machine or Bare Metal DB Systems", "Add/Modify/Delete EXA Infra and EXA VM Clusters", "Add/Modify/Delete ADBs", "Add/Modify/Delete MySQL DBs"],
    "Load Balancers":["Add/Modify/Delete Load Balancers", "Add/Modify/Delete Network Load Balancers"],
    "Management Services":["Add/Modify/Delete Notifications", "Add/Modify/Delete Events", "Add/Modify/Delete Alarms", "Add/Modify/Delete ServiceConnectors"],
    "Developer Services":["Upload current terraform files/state to Resource Manager", "Add/Modify/Delete OKE Cluster and Nodepools"],
	"Security":["Add/Modify/Delete KMS (Keys/Vaults)", "Enable Cloud Guard"],
    "Logging Services":["Enable VCN Flow Logs", "Enable LBaaS Logs", "Enable Object Storage Buckets Logs", "Enable File Storage Logs", "Enable Network Firewall Logs"],
    "CD3 Services":["Fetch Compartments OCIDs to variables file", "Fetch Protocols to OCI_Protocols"],
    "Other OCI Tools":["CIS Compliance Check Script", "ShowOCI Report", "Execute VizOCI", "OCI FSDR"]
    ]
    def non_gf_options_map = [
    "Export Identity":["Export Compartments", "Export Groups", "Export Policies", "Export Users", "Export Network Sources"],
    "Export Governance":["Export Tags", "Export Quotas"],
	"Export Cost Management":["Export Budgets"],
	"Export Network":["Export all Network Components", "Export Network components for VCNs/DRGs/DRGRouteRulesinOCI Tabs", "Export Network components for DHCP Tab", "Export Network components for SecRulesinOCI Tab", "Export Network components for RouteRulesinOCI Tab", "Export Network components for SubnetsVLANs Tab", "Export Network components for NSGs Tab"],
    "Export OCI Firewall":["Export Firewall Policy", "Export Firewall"],  
    "Export DNS Management":["Export DNS Views/Zones/Records", "Export DNS Resolvers"],
    "Export Compute":["Export Dedicated VM Hosts", "Export Instances (excludes instances launched by OKE)"],
    "Export Storage":["Export Block Volumes/Block Backup Policy", "Export File Systems", "Export Object Storage Buckets"],
    "Export Databases":["Export Virtual Machine or Bare Metal DB Systems", "Export EXA Infra and EXA VMClusters", "Export ADBs", "Export MySQL DBs"],
    "Export Load Balancers":["Export Load Balancers", "Export Network Load Balancers"],
    "Export Management Services":["Export Notifications", "Export Events", "Export Alarms", "Export Service Connectors"],
    "Export Developer Services":["Export OKE cluster and Nodepools"],
	"Export Security":["Export KMS (Keys/Vaults)"],
    "CD3 Services":["Fetch Compartments OCIDs to variables file", "Fetch Protocols to OCI_Protocols"]
    ]
    mainoptions_list = MainOptions.split(",")
    suboptions_list = SubOptions.split(",")
    validation_map = [:]
    if (mainoptions_list.size() > 0) {
        for (mitem in MainOptions.split(",")) {
			validation_map[mitem] = "Failed"
            if (mitem.contains("Tag") || mitem.contains("OCVS") ) {
                validation_map[mitem] = "Passed"
                continue
            }
            if (Workflow.toLowerCase().contains("create")){
                for (item in gf_options_map[mitem]) {
                  for (i in item.split(",")){
                  if (i in suboptions_list) {
                        validation_map[mitem] = "Passed"
                        break
                        }
                  }

                }
            }
            else {
                for (item in non_gf_options_map[mitem]) {
                  if (item in suboptions_list) {
						validation_map[mitem] = "Passed"
						break
                    }
                }
            }
        }
      if ('Upload current terraform files/state to Resource Manager' in suboptions_list) {
      	if (AdditionalFilters.split("orm_compartments=\\[,")[1].startsWithAny(",", " ")) {
                println("Failed - RM Stack Compartment")
                valid_params = "Failed"
            }
      }
    } else {
    valid_params = "Failed"
    }
	result_list = []
	validation_map.each { result_list.add(it.value) }
    if ("Failed" in result_list || valid_params == "Failed") {
		valid_params = "Failed"
	}else {
	valid_params = "Passed"
	}
    def failed_map = validation_map.findAll {it.value == 'Failed'}
    return [valid_params,failed_map.keySet() as List]
    }
return this