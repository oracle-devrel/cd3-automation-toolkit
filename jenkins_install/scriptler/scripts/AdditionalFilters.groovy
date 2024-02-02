html_to_be_rendered = "<table><tr>"

if(Workflow.toLowerCase().contains("export")){

html_to_be_rendered = """
    ${html_to_be_rendered}
    <tr>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"reg_filter=[\"></td>
    <td><label title=\"service1-label\" class=\" \">Region Filter (eg ashburn) : </label></td>
    <td><input type=\"text\" class=\" \" name=\"value\" > </br></td>
    <td>(Leave empty for all subscribed regions) </td>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td>

    </tr>

    <tr>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"comp_filter=[\"></td>
    <td><label title=\"service1-label\" class=\" \">Compartment Filter : </label></td>
    <td><input type=\"text\" class=\" \" name=\"value\" > </br></td>
    <td>(Leave empty to fetch from all compartments)</td>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td>
    </tr>

"""
}
for (item in SubOptions.split(",")) {
    if (item.equals("Export Instances (excludes instances launched by OKE)")) {
        html_to_be_rendered = """
        ${html_to_be_rendered}

       <tr>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"ins_pattern_filter=[\"></td>
    <td><label title=\"service1-label\" class=\" \">Display Name Pattern Filter for Compute : </label></td>
    <td>
    <input type=\"text\" class=\" \" name=\"value\" > </br>
    </td>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td></tr>

     <tr>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"ins_ad_filter=[\"></td>
    <td><label title=\"service1-label\" class=\" \">AD filter for Compute : </label></td>
    <td>
    <input type=\"text\" class=\" \" name=\"value\" > </br>
    </td>
    <td>(eg AD1,AD2,AD3)</td>
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
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"orm_region=[\"></td>
     <td><label title=\"service1-label\" class=\" \">Enter region (comma separated without spaces if multiple) for which you want to upload Terraform Stack - eg ashburn,phoenix,global : </label></td>
     <td><input type=\"text\" class=\" \" name=\"value\" > </br></td>
     <td>(Leave empty for all subscribed regions) </td>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td>

       </tr>
<tr>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"orm_compartments=[\"></td>
     <td><label title=\"service1-label\" class=\" \">Enter compartment name to create RM Stack<b> (Mandatory) </b> : </label></br></td>
         <td><input type=\"text\" class=\" \" name=\"value\" > </br></td>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td>
       </tr>
         """
   }

 if (item.equals('Create Key/Vault')){
        html_to_be_rendered = """
        ${html_to_be_rendered}


<tr>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"vault_region=[\"></td>
     <td><label title=\"service1-label\" class=\" \">Enter region name eg ashburn where you want to create Key/Vault : </label></td>
         <td><input type=\"text\" class=\" \" name=\"value\" > </br></td>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td>
       </tr>
<tr>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"vault_comp=[\"></td>
     <td><label title=\"service1-label\" class=\" \">Enter name of compartment as it appears in OCI Console for Key/Vault: </label></td>
         <td><input type=\"text\" class=\" \" name=\"value\" > </br></td>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td>
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
     <td><label title=\"service1-label\" class=\" \">Enter Reporting Region for Cloud Guard eg london :  </label></td>
         <td><input type=\"text\" class=\" \" name=\"value\" > </br></td>
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
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"comp_filter=[\"></td>
    <td><label title=\"service1-label\" class=\" \">Enter Compartment name to export SECURITY RULES/ROUTE RULES/DRG ROUTE RULES/NSGs : </label></td>
    <td><input type=\"text\" class=\" \" name=\"value\" > </br></td>
    <td>(Leave empty to fetch from all compartments)</td>
   <td><input type=\"hidden\" id=\"sep1\" name=\"value\" value=\"]@\"></td>
    </tr>

         """

	}
  break
}


html_to_be_rendered = "${html_to_be_rendered} </tr></table>"

return html_to_be_rendered