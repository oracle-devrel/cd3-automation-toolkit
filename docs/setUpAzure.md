# **Manage DB@Azure using CD3 Automation Toolkit**
---

**CD3** extends its support to **Oracle DB@Azure**, making it easier to manage Oracle Databases on Azure.

With CD3, users can currently create and manage **ADB@Azure** and **Exadata@Azure**.

!!! info 
    Export is only supported for **ADB@Azure** at the moment.
    <br>Support to Export **Exadata@Azure** will be extended in future releases.

**Prerequisite**

1. Make sure the onboarding of <a href="https://docs.oracle.com/en-us/iaas/Content/database-at-azure/oaaonboard.htm"><u>Oracle AI Database@Azure</u></a>  is completed. 

2. To manage ADB@Azure, users should first complete the steps to <a href="../install-cd3"><u>Install the CD3 toolkit</u></a> and then <a href="../connect-container-to-azure-subscription"><u>Connect the CD3 container to Azure subscription</u></a> 

Once the onboarding is completed and CD3 container is successfully connected to Azure subscription, the Toolkit can be used to execute Create/Export workflows for ADB@Azure and Create workflow for Exadata@Azure.

At present, CD3 for DB@Azure supports only CLI-based operations. Follow the instructions below to get started. 

1.  <a href = "../greenfield-azr-cli"><u>Create DB@Azure</u></a> 
2. <a href = "../nongreenfield-azr-cli"><u>Export DB@Azure</u></a> 


