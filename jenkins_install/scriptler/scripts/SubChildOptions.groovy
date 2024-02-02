List sec_rules = ["<b>SECURITY RULES</b>:disabled","Export Security Rules (From OCI into SecRulesinOCI sheet)", "Add/Modify/Delete Security Rules (Reads SecRulesinOCI sheet)"]
List route_rules = ["<b>ROUTE RULES</b>:disabled","Export Route Rules (From OCI into RouteRulesinOCI sheet)", "Add/Modify/Delete Route Rules (Reads RouteRulesinOCI sheet)"]
List drg_route_rules = ["<b>DRG ROUTE RULES</b>:disabled","Export DRG Route Rules (From OCI into DRGRouteRulesinOCI sheet)", "Add/Modify/Delete DRG Route Rules (Reads DRGRouteRulesinOCI sheet)"]
List nsg = ["<b>NSGs</b>:disabled","Export NSGs (From OCI into NSGs sheet)", "Add/Modify/Delete NSGs (Reads NSGs sheet)"]
List cis =  ["<b>CIS</b>:disabled","CD3 Image already contains the latest CIS compliance checking script available at the time of cd3 image release. Download latest only if new version of the script is available", "Execute compliance checking script"]
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
}
return final_list