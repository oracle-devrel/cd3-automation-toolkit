# **Connect container to OCI Tenancy - Multiple Prefixes**
---

The toolkit allows independent management of multiple environments using the same container. This enables better resource control and custom configurations for each environment. 


!!! note 

    * With the toolkit release v2024.4.1, the toolkit supports executing createTenancyConfig.py with different values for **prefix** per container when using Jenkins.

<br>

**Use Case**

* Managing Multiple Environments (Prod, Non-Prod etc.,) as separate entities within a single container.


**Steps**

* Edit the **tenancyconfig.properties** file according to <a href="../connect-container-to-oci-tenancy"><u>Connect CD3 Container to OCI</u></a>. Use a unique prefix that differs from the ones used previously. *Eg:  demo_prod,  demo_nonprod.*

!!! tip
    You can copy tenancyconfig.properties file as tenancyconfig_<prefix\>.properties and edit this file instead of directly editing tenancyconfig.properties.<br>
    This will help retain the input properties files used for different executions of the createTenancyConfig.py

* Different values can be specified for other parameters as well. For instance, one prefix can be configured to have **multiple outdir structure** for the generated terraform files, while another prefix can be set with a **single outdir structure**.
* Execute **createTenancyConfig.py** with modified **tenancyconfig.properties** or **tenancyconfig_<prefix\>.properties**.
* After executing **createTenancyConfig.py**, the following screenshots show how the environment specific out directories look like when using the toolkit with CLI and with Jenkins.

<br>

**Multi Prefix with CLI**

In the container, folders named after the specified prefix values will be created under the **/cd3user/tenancies** directory. Each environment specific folder is created with its own unique configuration specified in above steps.

![CLI](../images/multiple-prefixes-cli.jpg)

<br>

**Multi Prefix with Jenkins**

The Jenkins dashboard appears as follows when configured with two prefixes.

![jenkins](../images/multiple-prefixes-jenkins.jpg)


Check <a href=../cd3-jenkins#bootstrapping-of-jenkins-in-the-toolkit> <u>Important Note</u></a> to enable jenkins for multiple prefixes.
