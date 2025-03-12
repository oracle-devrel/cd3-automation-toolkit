List suboptions_list = SubOptions.split(",")
def reg_list = new File("/cd3user/tenancies/${Prefix}/.config_files/regions_file") as String[]
def string_list = reg_list.join(", ")
reg_options = ""
for(item in string_list.split(",")){
  reg_options = reg_options+"<option value=\""+item+"\">"+item+"</option>"
}
def comp_list = new File("/cd3user/tenancies/${Prefix}/.config_files/compartments_file") as String[]
def string_list2 = comp_list.join(", ")
comp_options = ""
for(item in string_list2.split(",")){
  comp_options = comp_options+"<option value=\""+item+"\">"+item+"</option>"
}

html_to_be_rendered = "<table>"
if(Workflow.toLowerCase().contains("export")){
region_filter_option = """
	<tr>
   <td ><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"reg_filter=\"></td>
   <td><label for="value">Select Regions (Optional) :</label></td>
   <td ><select multiple name="value" style="width:150px;">${reg_options} </select></td>
   <td ><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"@\"></td>
   </tr><tr></tr><tr></tr><tr></tr>
	"""
compartment_filter_option = """
	<tr>
    <td ><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"comp_filter=\"></td>
    <td><label for=\"value\">Select Compartments (Optional): </label></td>
    <td ><select multiple name=\"value\">${comp_options}</select></td>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"@\"></td>
    </tr><tr></tr><tr></tr><tr></tr>
	"""
tag_filter_option = """
	<tr>
    <td ><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"tag_filter=[\"></td>
    <td><label for=\"value\">Enter Tags Filter eg TagNameSpace.TagKey1=TagValue1,TagNameSpace.TagKey2=TagValue2 :</label><br></br></td>
    <td><input type=\"text\" name=\"value\">(Leave empty to export all resources)<br></br></td>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td>
    </tr><tr></tr><tr></tr><tr></tr>
	"""
List default_params_set = []
for (item in MainOptions.split(",")) {
  if (item != "Export Identity") {
    html_to_be_rendered = "${html_to_be_rendered} ${region_filter_option} ${compartment_filter_option} ${tag_filter_option}"
    default_params_set = ["region","compartment","tag"]
    break;
  }
}
 if (("Export Groups" in suboptions_list) || ("Export Users" in suboptions_list)) {
	if ("compartment" in default_params_set) {
      		html_to_be_rendered = "${html_to_be_rendered}"
    }else {
        html_to_be_rendered = "${html_to_be_rendered}${compartment_filter_option}"
        default_params_set.add("compartment")
    }
}
}
domain_filter_val = "Unset"
for (item in suboptions_list) {
    if ((item in ["Export Groups","Export Users"]) && (domain_filter_val.equals("Unset"))) {
      	html_to_be_rendered = """
        ${html_to_be_rendered}
    <tr>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"domain_filter=[\"></td>
    <td><label title=\"service1-label\" class=\" \">Enter the ',' separated Identity Domain names to export the resources - NA for IDCS Tenancies : </label></td>
    <td><input type=\"text\" class=\" \" name=\"value\" > (Enter 'all' to export from all domains OR leave it Blank to export from default domain )</br> </td>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td></tr><tr></tr><tr></tr><tr></tr>
      """
      domain_filter_val = "Set"
    }
    if (item.equals("Export Instances (excludes instances launched by OKE)")) {
        html_to_be_rendered = """
        ${html_to_be_rendered}
    <tr>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"ins_pattern_filter=[\"></td>
    <td><label title=\"service1-label\" class=\" \">Display Name Pattern Filter for Compute : </label></td>
    <td><input type=\"text\" class=\" \" name=\"value\" > </br></td>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td>
   </tr><tr></tr><tr></tr><tr></tr>
    <tr>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"ins_ad_filter=[\"></td>
    <td><label title=\"service1-label\" class=\" \">AD filter for Compute : </label></td>
    <td><input type=\"text\" class=\" \" name=\"value\" > (eg AD1,AD2,AD3)</br> </td>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td></tr><tr></tr><tr></tr><tr></tr>
      """
      }
    if (item.equals("Export Firewall Policy")) {
        html_to_be_rendered = """
        ${html_to_be_rendered}
    <tr>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"fwl_pol_pattern_filter=[\"></td>
    <td><label title=\"service1-label\" class=\" \">Display Name Pattern Filter for Firewall Policy : </label></td>
    <td text-align: center><input type=\"text\" class=\" \" name=\"value\" > </br></td>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td>
    </tr><tr></tr><tr></tr><tr></tr>
	 """
      }
	if (item.equals("Clone Firewall Policy")) {
        html_to_be_rendered = """
        ${html_to_be_rendered}
    <tr>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"fwl_clone_src_region=\"></td>
    <td ><label title=\"service1-label\" class=\" \">Select region of the Firewall Policy to be cloned <b> (Mandatory) </b>: </label></td>
	<td ><select name="value">${reg_options} </select></td>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"@\"></td></tr><tr></tr><tr></tr><tr></tr>
    <tr>
	<td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"fwl_clone_comp=\"></td>
    <td><label title=\"service1-label\" class=\" \">Select the compartment of the Firewall Policy to be cloned <b> (Mandatory) </b> : </label></td>
	<td><select name="value">${comp_options}</select></td>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"@\"></td></tr><tr></tr><tr></tr><tr></tr>
    <tr>
	<td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"src_policy_str=[\"></td>
    <td><label title=\"service1-label\" class=\" \">Enter names of the source firewall policies(comma separated) <b> (Mandatory) </b> : </label></td>
	<td><input type=\"text\" class=\" \" name=\"value\" > </br></td>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td></tr><tr></tr><tr></tr><tr></tr>
    <tr>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"target_policy_str=[\"></td>
    <td><label title=\"service1-label\" class=\" \">Enter names for the target firewall policies(comma separated), in the same order as source above:  </label></td>
	<td><input type=\"text\" class=\" \" name=\"value\" > (Leave empty if you need tool to generate the policy names) </br></td>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td></tr><tr></tr><tr></tr><tr></tr>
    <tr>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"attached_policy_only=[\"></td>
    <td><label title=\"service1-label\" class=\" \">Clone attached/used policies only </label></td>
    <td><input name=\"value\"  json=\"service1\" type=\"checkbox\" class=\" \"></td>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td>
    </tr><tr></tr><tr></tr><tr></tr>
	 """
      }
	if (item.equals("Delete Firewall Policy")) {
        html_to_be_rendered = """
        ${html_to_be_rendered}
    <tr>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"fwl_region=\"></td>
    <td><label title=\"service1-label\" class=\" \">Select region of the Firewall Policy to be deleted <b> (Mandatory) </b>: </label></td>
	<td><select name="value">${reg_options} </select></td>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"@\"></td></tr><tr></tr><tr></tr><tr></tr>
    <tr>
	<td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"fwl_del_comp=\"></td>
    <td><label title=\"service1-label\" class=\" \">Select Compartment of the Firewall Policy to be deleted <b> (Mandatory) </b> : </label></td>
	<td><select name="value">${comp_options}</select></td>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"@\"></td></tr><tr></tr><tr></tr><tr></tr>
    <tr>
	<td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"fwl_name=[\"></td>
    <td><label title=\"service1-label\" class=\" \">Enter names of the Firewall Policies(comma separated) that need to be deleted <b> (Mandatory) </b> : </label></td>
	<td><input type=\"text\" class=\" \" name=\"value\" > </br></td>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td></tr><tr></tr><tr></tr><tr></tr>
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
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td></tr><tr></tr><tr></tr><tr></tr>
 <tr>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"bv_ad_filter=[\"></td>
    <td><label title=\"service1-label\" class=\" \">AD filter for Block Volume : </label></td>
    <td><input type=\"text\" class=\" \" name=\"value\" > (eg AD1,AD2,AD3)</br></td>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td></tr><tr></tr><tr></tr><tr></tr>
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
       </tr><tr></tr><tr></tr><tr></tr>
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
      </tr><tr></tr><tr></tr><tr></tr>
<tr>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"orm_compartments=\"></td>
     <td><label title=\"service1-label\" class=\" \">Select compartment name to create RM Stack<b> (Mandatory) </b> : </label></br></td>
         <td><select name="value">${comp_options}</select></td>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"@\"></td>
       </tr><tr></tr><tr></tr><tr></tr>
         """
   }

  if (item.equals('Enable Cloud Guard')){
        html_to_be_rendered = """
        ${html_to_be_rendered}
    <tr>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"cg_region=[\"></td>
    <td><label title=\"service1-label\" class=\" \">Select Reporting Region for Cloud Guard :  </label></td>
    <td><select name="value">${reg_options} </select></td>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td>
    </tr><tr></tr><tr></tr><tr></tr>
         """
   }

    if (item.equals('Execute VizOCI')){
        html_to_be_rendered = """
        ${html_to_be_rendered}
        <tr>
   <td ><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"vizoci_reg_filter=\"></td>
   <td><label for="value">Select Regions (Optional) :</label></td>
   <td ><select multiple name="value" style="width:150px;">${reg_options} </select></td>
   <td ><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"@\"></td>
   </tr><tr></tr><tr></tr><tr></tr>
   <tr>
    <td ><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"vizoci_comp_filter=\"></td>
    <td><label for=\"value\">Select Compartments (Optional): </label></td>
    <td ><select multiple name=\"value\">${comp_options}</select></td>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"@\"></td>
    </tr><tr></tr><tr></tr><tr></tr>

        <tr>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"generate_graphs=[\"></td>
     <td><label title=\"service1-label\" class=\" \">Generate Graphs </label></td>
        <td>
       <input name=\"value\"  json=\"service1\" type=\"checkbox\" class=\" \">
       </td>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td>
       </tr><tr></tr><tr></tr><tr></tr>
         """
   }

}

export_network_rules = "unset"
for (item in SubChildOptions.split(",")) {
  if ((item in ["Export Security Rules (From OCI into SecRulesinOCI sheet)","Export Route Rules (From OCI into RouteRulesinOCI sheet)","Export DRG Route Rules (From OCI into DRGRouteRulesinOCI sheet)","Export NSGs (From OCI into NSGs sheet)"]) && (export_network_rules.equals("unset"))) {
  html_to_be_rendered = """
        ${html_to_be_rendered}
<tr>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"comp_filter=\"></td>
    <td><label title=\"service1-label\" class=\" \">select Compartments to export SECURITY RULES/ROUTE RULES/DRG ROUTE RULES/NSGs : </label></td>
    <td><select multiple name="value">${comp_options}</select></td>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"@\"></td>
    </tr><tr></tr><tr></tr><tr></tr>
<tr>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"tag_filter=\"></td>
    <td><label title=\"service1-label\" class=\" \">Enter Tags Filter eg TagNameSpace.TagKey1=TagValue1,TagNameSpace.TagKey2=TagValue2 : </label></td>
    <td><input type=\"text\" name=\"value\"></td>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td>
    </tr><tr></tr><tr></tr><tr></tr>
         """
   export_network_rules = "set"
  }

	if (item.equals("Export DR Plan")) {
      html_to_be_rendered = """
      ${html_to_be_rendered}

  <tr>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"fsdr_ex_filename=[\"></td>
     <td><label title=\"service1-label\" class=\" \">Excel File Name(without full path) where DR plan will be exported : </label></td>
     <td><input type=\"text\" class=\" \" name=\"value\" > (Default is 'prefix_oci-fsdr-plan.xlsx at /cd3user/tenancies/<prefix>/othertools_files')</br> </td>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td>
       </tr><tr></tr><tr></tr><tr></tr>
  <tr>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"fsdr_ex_sheet=[\"></td>
     <td><label title=\"service1-label\" class=\" \">Sheet Name where DR plan will be exported : </label></td>
         <td><input type=\"text\" class=\" \" name=\"value\" > (Default is 'FSDR-Plan') </br></td>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td>
       </tr><tr></tr><tr></tr><tr></tr>
   <tr>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"fsdr_ex_ocid=[\"></td>
     <td><label title=\"service1-label\" class=\" \">DR Plan OCID which needs to be exported : </label></td>
         <td><input type=\"text\" class=\" \" name=\"value\" > (Mandatory) </br></td>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td>
       </tr><tr></tr><tr></tr><tr></tr>
   """
   }

  if (item.equals("Update DR Plan")) {
      html_to_be_rendered = """
      ${html_to_be_rendered}
  <tr>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"fsdr_up_filename=[\"></td>
    <td><label title=\"service1-label\" class=\" \">Excel File Name(without full path) from where DR plan will be updated : </label></td>
    <td><input type=\"text\" class=\" \" name=\"value\" >  (Default is 'prefix_oci-fsdr-plan.xlsx at /cd3user/tenancies/<prefix>/othertools_files)</br></td>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td></tr><tr></tr><tr></tr><tr></tr>
 <tr>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"fsdr_up_sheet=[\"></td>
    <td><label title=\"service1-label\" class=\" \">Sheet Name from where DR plan will be updated : </label></td>
    <td><input type=\"text\" class=\" \" name=\"value\" > (Default is 'FSDR-Plan' if left empty)</br></td>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td></tr><tr></tr><tr></tr><tr></tr>
  <tr>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"fsdr_up_ocid=[\"></td>
    <td><label title=\"service1-label\" class=\" \">DR Plan OCID which needs to be updated : </label></td>
    <td><input type=\"text\" class=\" \" name=\"value\" > (Mandatory)</br></td>
    <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td></tr><tr></tr><tr></tr><tr></tr>

      """
   }

}

html_to_be_rendered = "${html_to_be_rendered} </table></dev>"
return html_to_be_rendered