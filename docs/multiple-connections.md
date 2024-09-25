# **Connect container to OCI Tenancy - Multiple Executions**
---

!!! note 

    * With the toolkit release v2024.4.1, the toolkit supports executing createTenancyConfig.py with different values for **prefix** per container when using Jenkins.


**Use Case**

* You need to manage different environments say Prod, Non Prod etc as different entities.

**Steps**

* Edit tenancyconfig.properties file as per [Connect CD3 Container to OCI](connect-container-to-oci-tenancy.md). Specify different value for prefix than used earlier. Eg demo_prod or demo_nonprod.
* You can chose to specify different values for other parameters also like you can configure one prefix with multiple outdir structure but second prefix with single outdir structure.
* Execute createTenancyConfig.py with modified tenancyconfig.properties.
* Once you execute createTenancyConfig.py, below screenshots show how it looks like when you are using the toolkit with CLI or with Jenkins.

**Multi Prefix Support with CLI**

Folders with names used as prefix values get created under /cd3user/tenancies folder. Each will have its own setup.



**Multi Prefix Support with Jenkins**

The Jenkins dashboard looks as below:

See [important note](cd3-jenkins.md#bootstrapping-of-jenkins-in-the-toolkit) to enable jenkins for multiple prefixes.


