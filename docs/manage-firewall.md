## create_resources (Greenfield) Workflow

Below sub-options appear under _OCI Firewall_ option-

**1. Validate Firewall CD3 Excel** <br>

- This is the validator for all tabs of CD3 Excel sheet for Firewall. It is a comprehensive list of validations performed on firewall tabs. 

- Log file containing CD3 firewall validator checks is generated at: <i>/cd3user/tenancies/<prefix\>/<prefix\>_cd3FirewallValidator.log</i>

**2. Add/Modify/Delete Firewall Policy**<br>

- Reads the Firewall-Policy-* tabs of the excel and generates tfvars.

**3. Add/Modify/Delete Firewall**<br>

- Reads the Firewall tab of the excel and generates tfvars.

!!! Note
      - Specify Subnet Name as ```<subnet-name>::<vcn-name>```. This service does not need Network details to be existing in the excel sheet.

**4. Clone Firewall Policy**<br>

- On choosing this option, specify the region, compartment name and source policy names that need to be cloned.

- The toolkit will export the data from OCI console for each source policy specified and append it to the end of CD3 firewall sheet with a new name.

- It will then generate *.auto.tfvars for this modified excel sheet.
- Execute terraform plan and apply to create the cloned policy in OCI console.



## export_resources (Non-Greenfield) Workflow
- Specify region and compartment to export OCI Network Firewall objects from a tenancy.
- Display name pattern can also be supplied to export firewall policies with a particular pattern in their name.