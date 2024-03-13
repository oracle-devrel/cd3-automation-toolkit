List sec_rules = ["<b>SECURITY RULES</b>:disabled","Export Security Rules (From OCI into SecRulesinOCI sheet)", "Add/Modify/Delete Security Rules (Reads SecRulesinOCI sheet)"]
List route_rules = ["<b>ROUTE RULES</b>:disabled","Export Route Rules (From OCI into RouteRulesinOCI sheet)", "Add/Modify/Delete Route Rules (Reads RouteRulesinOCI sheet)"]
List firewall_policy = ["<b>FIREWALL POLICY</b>:disabled","Add/Modify Policy", "Add/Modify Service","Add/Modify Service-list","Add/Modify Application","Add/Modify Application-list","Add/Modify Address-list","Add/Modify Url-list","Add/Modify Security rules","Add/Modify Mapped Secrets","Add/Modify Decryption Rules","Add/Modify Decryption Profile"]
List drg_route_rules = ["<b>DRG ROUTE RULES</b>:disabled","Export DRG Route Rules (From OCI into DRGRouteRulesinOCI sheet)", "Add/Modify/Delete DRG Route Rules (Reads DRGRouteRulesinOCI sheet)"]
List nsg = ["<b>NSGs</b>:disabled","Export NSGs (From OCI into NSGs sheet)", "Add/Modify/Delete NSGs (Reads NSGs sheet)"]
List cis =  ["<b>CIS</b>:disabled","Download latest compliance checking script", "Execute compliance checking script"]
List final_list = []

for (item in SubOptions.split(",")) {
    if (item.equals("Security Rules")){
        final_list += sec_rules
    }
    if (item.equals("Route Rules")){
        final_list += route_rules
    }
    if (item.equals("DRG Route Rules")){
        final_list += drg_route_rules
    }
    if (item.equals("Network Security Groups")){
        final_list += nsg
    }
    if (item.equals("CIS Compliance Checking Script")){
        final_list += cis
    }
      if (item.equals("Add/Modify Firewall Policy")){
        final_list += firewall_policy
    }
}
return final_list