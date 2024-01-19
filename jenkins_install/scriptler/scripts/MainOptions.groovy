if (Workflow.toLowerCase().contains("create")){
return[
"Validate CD3",
"Identity",
"Tags",
"Network",
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
"CD3 Services"
]
}
else if(Workflow.toLowerCase().contains("export")) {
return[
"Export Identity",
"Export Tags",
"Export Network",
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