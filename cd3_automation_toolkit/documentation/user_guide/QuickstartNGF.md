## Quick start - Export Identity (Non Greenfield Workflow)
Once the Docker container has been launched and connected to the OCI Tenancy, follow the below steps to quickly export Identity components from OCI.

1. Use the excel [CD3-Blank-template](/cd3_automation_toolkit/example) and place it at the location _/cd3user/tenancies/<customer\_name>/_ which is also mapped to your local directory.

2. Edit the _setUpOCI.properties_ at location:_/cd3user/tenancies /<customer\_name>/<customer\_name>\_setUpOCI.properties_ with appropriate values. 
   - Update the _cd3file_ parameter to specify the CD3 excel sheet path.
   - Set the _non_gf_tenancy_ parameter value to _true_. (for Non Greenfield Workflow.)
     
     <blockquote>For more information on types of Workflows, refer to <a href = /cd3_automation_toolkit/documentation/user_guide/Workflows.md> Automation Toolkit Workflows</a></blockquote>

3. Change Directory to 'cd3_automation_toolkit' :
    ```cd /cd3user/oci_tools/cd3_automation_toolkit/```
    
   and execute the _setupOCI.py_ file:
   
   ```python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties```
 4. Choose option 'Export Identity' from the displayed menu. Once the execution is successful, you will see:
      <ul>
      <li><b>Filled in tabs</b>-<i>Compartments, Groups, Polecies of Excel sheet</i></li>
      <li><i>tf_import_commands_identity.sh</i></li>
      <li><i><customer_name>_compartments.auto.tfvars, <customer_name>_groups.auto.tfvars, <customer_name>_policies.auto.tfvars</i></li>
      </ul>
   
 5. Execute _tf\_import\_commands\_identity.sh_ to start importing the identity components into tfstate file.
 6. Repeat the above process (except Step 5) to export other components from OCI.

    
<br><br>
<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/QuickstartGF.md">:arrow_backward: Prev</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/Recommendations.md">Next :arrow_forward:</a> |
| :---- | -------: |
  
</div>
