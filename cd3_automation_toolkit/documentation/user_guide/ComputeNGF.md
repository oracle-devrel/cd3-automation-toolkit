# Managing Compute Instances for Non-Greenfield tenancies

Follow the below steps to export OCI compute Instances to CD3 Excel file and create the terraform state:

1. Use the [CD3-Blank-Template.xlsx](/cd3_automation_toolkit/example) to export existing OCI VM details into the "Instances" sheet.
2. Make sure to export the VCNs and Subnets in which the Instances are present prior to exporting the Instance. This allows to manage the instances at a later point using cd3 and terraform.
3. Execute the _setupOCI.py_ file with _non_gf_tenancy_ parameter value to _true_:
   
   ```python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties```
4. Provide the region from where the Instances have to be exported. Specify comma separated values for multiple regions.
5. From the output menu, select **Option 5: Export Compute >> Option 2: Export Instances**.
6. Enter the compartment to which the Instances belong to. If you have to export Instances from multiple compartments, specify comma separated compartment values.
   For unique compartments, enter the name as it shows on the OCI console. For non-unique compartments, specify the name along with hierarchy in the below format:

        Parent Compartment1 ::  Parent Compartment2 :: ... :: My Compartment
   
7.To export only specific instances, specify the required filter values

     - Enter comma separated list of display name patterns of the instances: 
     - Enter comma separated list of ADs of the instances eg AD1,AD2,AD3: 

8. Upon executing, the "Instances" sheet in input CD3 Excel is populated with the VMs details.
9. The tf_import_commands_instances_nonGF.sh script, tfvars file are generated for the Instances under folder */cd3user/tenancies/<customer_name>/terraform_files/<region_dir>*. If you are using multiple outdirectories, they'll be located under the */cd3user/tenancies/<customer_name>/terraform_files/<region_dir>compute* folder.
10. The associated ssh public keys are placed under variables_<region>.tf under the "instance_ssh_keys" variable.
11. Execute the .sh file ( *sh tf_import_commands_instances_nonGF.sh*) to generate terraform state file.

    


