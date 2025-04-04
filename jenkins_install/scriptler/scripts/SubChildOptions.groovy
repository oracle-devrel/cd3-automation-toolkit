List sec_rules = ["<b>SECURITY RULES</b>:disabled","Export Security Rules (From OCI into SecRulesinOCI sheet)", "Add/Modify/Delete Security Rules (Reads SecRulesinOCI sheet)"]
List route_rules = ["<b>ROUTE RULES</b>:disabled","Export Route Rules (From OCI into RouteRulesinOCI sheet)", "Add/Modify/Delete Route Rules (Reads RouteRulesinOCI sheet)"]
List firewall_policy = ["<b>FIREWALL POLICY</b>:disabled","Add/Modify/Delete Policy", "Add/Modify/Delete Service","Add/Modify/Delete Service-list","Add/Modify/Delete Application","Add/Modify/Delete Application-list","Add/Modify/Delete Address-list","Add/Modify/Delete Url-list","Add/Modify/Delete Security rules","Add/Modify/Delete Mapped Secrets","Add/Modify/Delete Decryption Rules","Add/Modify/Delete Decryption Profile","Add/Modify/Delete Tunnel Inspection Rules"]
List drg_route_rules = ["<b>DRG ROUTE RULES</b>:disabled","Export DRG Route Rules (From OCI into DRGRouteRulesinOCI sheet)", "Add/Modify/Delete DRG Route Rules (Reads DRGRouteRulesinOCI sheet)"]
List nsg = ["<b>NSGs</b>:disabled","Export NSGs (From OCI into NSGs sheet)", "Add/Modify/Delete NSGs (Reads NSGs sheet)"]
List cis =  ["<b>CIS</b>:disabled","Download latest compliance checking script", "Execute compliance checking script"]
List showoci =  ["<b>SHOW OCI</b>:disabled","Download Latest ShowOCI Script", "Execute ShowOCI Script"]
List ocifsdr = ["<b>OCI FSDR</b>:disabled","Export DR Plan", "Update DR Plan"]
List customer_connectivity = ["<b>Connectivity</b>:disabled","Create Remote Peering Connections"]
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
    if (item.equals("CIS Compliance Check Script")){
        final_list += cis
    }
    if (item.equals("ShowOCI Report")){
        final_list += showoci
    }
    if (item.equals("OCI FSDR")){
        final_list += ocifsdr
    }
    if (item.equals("Add/Modify/Delete Firewall Policy")){
        final_list += firewall_policy
    }
    if (item.equals("Customer Connectivity")){
        final_list += customer_connectivity
    }
}
return final_list