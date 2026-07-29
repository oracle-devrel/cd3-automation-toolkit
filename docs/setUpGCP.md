# **Manage DB@GCP using CD3 Automation Toolkit**
---

**CD3** extends its support to **Oracle DB@GCP**, making it easier to manage Oracle Databases on GCP.

With CD3, users can currently create and manage **ADB@GCP** and **Exadata@GCP**. 


!!! info 
    Export is only supported for **ADB@GCP** at the moment.
    <br>Support to Export **Exadata@GCP** will be extended in future releases. 

**Prerequisite**

1. Make sure the onboarding of <a href="https://docs.oracle.com/en-us/iaas/Content/database-at-gcp/onboard.htm"><u>Oracle AI Database@GCP</u></a>  is completed. 

2. To manage ADB@GCP, users should first complete the steps to <a href="../install-cd3"><u>Install the CD3 toolkit</u></a> and then <a href="../connect-container-to-gcp-account"><u>Connect the CD3 container to GCP account</u></a> 

Once the onboarding is completed and CD3 container is successfully connected to GCP account, the Toolkit can be used to execute Create/Export workflows for ADB@GCP and Create workflow for Exadata@GCP.

At present, CD3 for DB@GCP supports only CLI-based operations. Follow the instructions below to get started. 

1.  <a href = "../greenfield-gcp-cli"><u>Create DB@GCP</u></a> 
2.  <a href = "../nongreenfield-gcp-cli"><u>Export DB@GCP</u></a> 
