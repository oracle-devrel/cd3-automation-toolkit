# Exporting Compute Instances from OCI

Follow the below steps to export OCI compute Instances to CD3 Excel file and create the terraform state:

1. Use the [CD3-Blank-Template.xlsx](/cd3_automation_toolkit/example) to export existing OCI VM details into the "Instances" sheet. <br>
<br>
2. Add any additonal attributes (not part of excel sheet already) which needs to be exported as per [this](SupportforAdditionalAttributes.md). <br>
<br>
3. Make sure to export the VCNs and Subnets in which the Instances are present prior to exporting the Instance. <br>
<br>
4. Execute the _setupOCI.py_ file with _non_gf_tenancy_ parameter value to _true_: <br>
   ```python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties``` <br>
<br>   
5. Provide the region from where the Instances have to be exported. Specify comma separated values for multiple regions. <br>
<br>
6. From the output menu, select **Option 5: Export Compute >> Option 2: Export Instances**. <br>
<br>
7. Enter the compartment to which the Instances belong to. If you have to export Instances from multiple compartments, specify comma separated compartment values. <br>
   Specify the compartment name along with hierarchy in the below format:

        Parent Compartment1::Parent Compartment2::MyCompartment <br>
 

8. To export only specific instances, specify the required filter values
     - Enter comma separated list of display name patterns of the instances: 
     - Enter comma separated list of ADs of the instances eg AD1,AD2,AD3: <br>
<br>

9. Upon executing, the "Instances" sheet in input CD3 Excel is populated with the VMs details. <br>
<br>
10. The tf_import_commands_instances_nonGF.sh script, tfvars file are generated for the Instances under folder */cd3user/tenancies/<customer_name>/terraform_files/<region_dir>*. If you are using multiple outdirectories, they'll be located under the */cd3user/tenancies/<customer_name>/terraform_files/<region_dir>compute* folder. <br>
<br>
10. The associated ssh public keys are placed under variables_<region>.tf under the "instance_ssh_keys" variable.  <br>
<br>
11. While export of instances, it will fetch details for only the primary VNIC attached to the instance. <br>
<br>
12. Execute the .sh file ( *sh tf_import_commands_instances_nonGF.sh*) to generate terraform state file. <br>
<br>
13. Please [read](KnownBehaviour.md) the known behaviour of toolkit for export of instances having multiple plugins.

<br><br>
<div align='center'>
</div>


