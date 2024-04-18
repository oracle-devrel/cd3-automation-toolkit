def reg_list = new File("/cd3user/tenancies/${customer_prefix}/.config_files/regions_file") as String[]
def string_list = reg_list.join(", ")
reg_options = ""
for(item in string_list.split(",")){
  reg_options = reg_options+"<option value=\""+item+"\">"+item+"</option>"
}
def comp_list = new File("/cd3user/tenancies/${customer_prefix}/.config_files/compartments_file") as String[]
def string_list2 = comp_list.join(", ")
comp_options = ""
for(item in string_list2.split(",")){
  comp_options = comp_options+"<option value=\""+item+"\">"+item+"</option>"
}

html_to_be_rendered = "<table \"width:200px\"><tr>"
if(Workflow.toLowerCase().contains("export")){

html_to_be_rendered = """
    ${html_to_be_rendered}
    <tr>
   <td ><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"reg_filter=\"></td>
   <td ><label for="value">Select Regions (Optional) :</label></td>
   <td ><select multiple name="value">${reg_options} </select></td>
   <td >(Leave empty to fetch from all regions)</td>
   <td width="1%"><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"@\"></td>
   </tr></table>
    <table style="width:400px">
	<tr>
    <td ><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"comp_filter=\"></td>
    <td ><label for="value">Select Compartments (Optional): </label></td>
    <td ><select multiple name="value">${comp_options}</select></td>
    <td ><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"@\"></td>
    </tr>
    </table><table>
"""
}
for (item in SubOptions.split(",")) {
    if (item.equals("Export Instances (excludes instances launched by OKE)")) {
        html_to_be_rendered = """
        ${html_to_be_rendered}
    <tr>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"ins_pattern_filter=[\"></td>
    <td><label title=\"service1-label\" class=\" \">Display Name Pattern Filter for Compute : </label></td>
    <td><input type=\"text\" class=\" \" name=\"value\" > </br></td>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td>
   </tr>
    <tr>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"ins_ad_filter=[\"></td>
    <td><label title=\"service1-label\" class=\" \">AD filter for Compute : </label></td>
    <td><input type=\"text\" class=\" \" name=\"value\" > </br> </td>
    <td>(eg AD1,AD2,AD3)</td>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td></tr>
      """
      }
    if (item.equals("Export Firewall Policy")) {
        html_to_be_rendered = """
        ${html_to_be_rendered}
    <tr>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"fwl_pol_pattern_filter=[\"></td>
    <td><label title=\"service1-label\" class=\" \">Display Name Pattern Filter for Firewall Policy : </label></td>
    <td><input type=\"text\" class=\" \" name=\"value\" > </br></td>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td>
    </tr>
	 """
      }
	if (item.equals("Clone Firewall Policy")) {
        html_to_be_rendered = """
        ${html_to_be_rendered}
    <tr>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"fwl_clone_src_region=\"></td>
    <td width="40%"><label title=\"service1-label\" class=\" \">Select region of the Firewall Policy to be cloned <b> (Mandatory) </b>: </label></td>
	<td width="40%"><select name="value">${reg_options} </select></td>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"@\"></td></tr>
    <tr>
	<td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"fwl_clone_comp=\"></td>
    <td width="40%"><label title=\"service1-label\" class=\" \">Select the compartment of the Firewall Policy to be cloned <b> (Mandatory) </b> : </label></td>
	<td width="40%"><select name="value">${comp_options}</select></td>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"@\"></td></tr>
    <tr>
	<td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"src_policy_str=[\"></td>
    <td><label title=\"service1-label\" class=\" \">Enter names of the source firewall policies(comma separated) <b> (Mandatory) </b> : </label></td>
	<td><input type=\"text\" class=\" \" name=\"value\" > </br></td>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td></tr>
    <tr>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"target_policy_str=[\"></td>
    <td><label title=\"service1-label\" class=\" \">Enter names for the target firewall policies(comma separated), in the same order as source above, leave empty if you need tool to generate the policy names:  </label></td>
	<td><input type=\"text\" class=\" \" name=\"value\" > </br></td>
    <td>(Leave empty if you need tool to generate the policy names) </td>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td></tr>
    <tr>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"attached_policy_only=[\"></td>
    <td><label title=\"service1-label\" class=\" \">Clone attached/used policies only </label></td>
    <td><input name=\"value\"  json=\"service1\" type=\"checkbox\" class=\" \"></td>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td>
    </tr>
	 """
      }
	if (item.equals("Delete Firewall Policy")) {
        html_to_be_rendered = """
        ${html_to_be_rendered}
    <tr>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"fwl_region=\"></td>
    <td><label title=\"service1-label\" class=\" \">Select region of the Firewall Policy to be deleted <b> (Mandatory) </b>: </label></td>
	<td><select name="value">${reg_options} </select></td>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"@\"></td></tr>
    <tr>
	<td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"fwl_del_comp=\"></td>
    <td><label title=\"service1-label\" class=\" \">Select Compartment of the Firewall Policy to be deleted <b> (Mandatory) </b> : </label></td>
	<td><select name="value">${comp_options}</select></td>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"@\"></td></tr>
    <tr>
	<td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"fwl_name=[\"></td>
    <td><label title=\"service1-label\" class=\" \">Enter names of the Firewall Policies(comma separated) that need to be deleted <b> (Mandatory) </b> : </label></td>
	<td><input type=\"text\" class=\" \" name=\"value\" > </br></td>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td></tr>
	 """
      }
   if (item.equals("Export Block Volumes/Block Backup Policy")) {
      html_to_be_rendered = """
      ${html_to_be_rendered}
       <tr>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"bv_pattern_filter=[\"></td>
    <td><label title=\"service1-label\" class=\" \">Display Name Pattern filter for Block Volume : </label></td>
    <td>
    <input type=\"text\" class=\" \" name=\"value\" > </br>
    </td>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td></tr>
 <tr>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"bv_ad_filter=[\"></td>
    <td><label title=\"service1-label\" class=\" \">AD filter for Block Volume : </label></td>
    <td><input type=\"text\" class=\" \" name=\"value\" > </br></td>
    <td>(eg AD1,AD2,AD3)</td>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td></tr>
      """
   }

   if (item.equals('Export DNS Views/Zones/Records')){
        html_to_be_rendered = """
        ${html_to_be_rendered}

        <tr>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"default_dns=[\"></td>
     <td><label title=\"service1-label\" class=\" \">Export Default views/Zones/Records </label></td>
        <td>
       <input name=\"value\"  json=\"service1\" type=\"checkbox\" class=\" \">

       </td>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td>
       </tr>
         """
   }
 if (item.equals('Upload current terraform files/state to Resource Manager')){
        html_to_be_rendered = """
        ${html_to_be_rendered}

<tr>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"orm_region=\"></td>
     <td><label title=\"service1-label\" class=\" \">Select regions for which you want to upload Terraform Stack  : </label></td>
     <td><select multiple name="value">${reg_options} <option value="global">global</option></select></td>

   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"@\"></td>

       </tr>
<tr>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"orm_compartments=\"></td>
     <td><label title=\"service1-label\" class=\" \">Select compartment name to create RM Stack<b> (Mandatory) </b> : </label></br></td>
         <td><select name="value">${comp_options}</select></td>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"@\"></td>
       </tr>
         """
   }

 if (item.equals('Create Key/Vault')){
        html_to_be_rendered = """
        ${html_to_be_rendered}
<tr>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"vault_region=\"></td>
     <td><label title=\"service1-label\" class=\" \">Select region name where you want to create Key/Vault : </label></td>
         <td><select name="value">${reg_options} </select></td>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"@\"></td>
       </tr>
<tr>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"vault_comp=\"></td>
     <td><label title=\"service1-label\" class=\" \">select compartment for Key/Vault: </label></td>
         <td><select name="value">${comp_options}</select></td>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"@\"></td>
       </tr>
         """
   }
 if (item.equals('Create Default Budget')){
        html_to_be_rendered = """
        ${html_to_be_rendered}
<tr>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"budget_amount=[\"></td>
     <td><label title=\"service1-label\" class=\" \">Enter Monthly Budget Amount (in USD) :  </label></td>
         <td><input type=\"text\" class=\" \" name=\"value\" > </br></td>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td>
       </tr>
<tr>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"budget_threshold=[\"></td>
     <td><label title=\"service1-label\" class=\" \">Enter Threshold Percentage of Budget : </label></td>
         <td><input type=\"text\" class=\" \" name=\"value\" > </br></td>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td>
       </tr>
         """
   }

 if (item.equals('Enable Cloud Guard')){
        html_to_be_rendered = """
        ${html_to_be_rendered}
    <tr>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"cg_region=[\"></td>
    <td><label title=\"service1-label\" class=\" \">select Reporting Region for Cloud Guard :  </label></td>
    <td><select name="value">${reg_options} </select></td>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td>
    </tr>
         """
   }

}

for (item in SubChildOptions.split(",")) {
	if (item in ["Export Security Rules (From OCI into SecRulesinOCI sheet)","Export Route Rules (From OCI into RouteRulesinOCI sheet)","Export DRG Route Rules (From OCI into DRGRouteRulesinOCI sheet)","Export NSGs (From OCI into NSGs sheet)"]) {

	html_to_be_rendered = """
        ${html_to_be_rendered}

<tr>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"comp_filter=\"></td>
    <td><label title=\"service1-label\" class=\" \">select Compartments to export SECURITY RULES/ROUTE RULES/DRG ROUTE RULES/NSGs : </label></td>
    <td><select multiple name="value">${comp_options}</select></td>

   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"@\"></td>
    </tr>
         """
	}
  break
}

html_to_be_rendered = "${html_to_be_rendered} </tr></table>"
return html_to_be_rendered
