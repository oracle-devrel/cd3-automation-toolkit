if (Workflow.toLowerCase().contains("create")){
return[
"Validate CD3",
"Identity",
"Governance",
"Cost Management",
"Network",
"OCI Firewall",
"DNS Management",
"Compute",
"Storage",
"Database",
"Load Balancers",
"Management Services",
"Developer Services",
"Logging Services",
"Software-Defined Data Centers - OCVS",
"CIS Compliance Features",
"CD3 Services",
"3rd Party Services"
]
}
else if(Workflow.toLowerCase().contains("export")) {
return[
"Export Identity",
"Export Governance",
"Export Cost Management",
"Export Network",
"Export OCI Firewall",
"Export DNS Management",
"Export Compute",
"Export Storage",
"Export Databases",
"Export Load Balancers",
"Export Management Services",
"Export Developer Services",
"Export Software-Defined Data Centers - OCVS",
"CD3 Services"
]
}
else {
return["Please select a Workflow:disabled"]
}