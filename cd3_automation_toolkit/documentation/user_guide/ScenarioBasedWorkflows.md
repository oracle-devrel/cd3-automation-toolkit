# Scenario Based Workflow

This page will give you an insight into the Automation Toolkit Workflows that must be followed for flawless execution and usage of the toolkit.

## NOTE:

1. Automation Tool Kit DOES NOT support the creation/export of duplicate resources.
2. DO NOT modify/remove any commented rows or column names. You may re-arrange the columns if needed (except NSGs).
3. A double colon (::) or Semi-Colon (;) has a special meaning in the Tool Kit. Do not use them in the OCI data / values.
4. Do not include any unwanted space in cells you fill in; do not place any empty rows in between.
5. To learn about how to add attributes, refer Support for additional attributes (Flat TF Files)
6. Any entry made/moved post <END> in any of the Tabs, of CD3 will not be processed. Any resources created by the automation & then moved after the <END> will cause the resources to be removed. 
7. The components that get created as part of VCNs Tab (Example: IGW, SGW, LPG, NGW, DRG) will have the same set of Tags attached to them.
8. Automation Tool Kit does not support sharing of Block Volumes.
9. Detail on the know behaviour of the toolkit can be found at Known Behaviour Of Automation Toolkit
10. Option to Modify Network - 
  
    Some points to consider while modifying networking components are - 
  
    a. Converting the exported VCN to Hub/Spoke/Peer VCN is not allowed. Route Table rules based on the peering for new LPGs to existing VCNs will not be auto populated. Users are requested to add an entry to the RouteRulesInOCI sheet to support the peering rules.
    
    b. Adding a new VCN as Hub and other new VCNs as Spoke/Peer is allowed. Gateways will be created as specified in VCNs sheet. 
    
    c. Adding new VCNs as None is allowed. Gateways will be created as specified in VCNs sheet.
    
    d. The addition of new Subnets to exported VCNs and new VCNs is allowed.
  
  | Scenarios| Execution Steps|
  | ---| --- |
  | Validate CD3 | Steps: 
