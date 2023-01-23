## Support for New Region or New Protocol
**Automation Toolkit can support new regions launched by OCI.**<br>
CD3 Automation Toolkit automatically updates the OCI_Region file on every execution.

Alternately, manually edit the file at **/cd3user/oci_tools/cd3_automation_toolkit/OCI_Regions**; add new region in belowformat:
**#Region:Region_Key**<br>
eg<br>
**langley:us-langley-1**

You should use value specified for 'Region' in the CD3 excel sheet. Outdir for terraform will also be created with name as 'Region' from above file

**Automation Toolkit can support new protocols in SecurityLists or NSGs.**<br> 
To update the OCI_Protocols file, Choose the option **"Fetch Protocols to OCI_Protocols"** from **"CD3 Services"** in setUpOCI menu.
Alternately, manually edit the file at /cd3user/oci_tools/cd3_automation_toolkit/OCI_Protocols; add new protocol in below format:

**#protocol number:protocol name**
