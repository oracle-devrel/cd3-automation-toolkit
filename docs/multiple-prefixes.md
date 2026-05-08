# **Connect container to OCI Tenancy - Multiple Prefixes**
---

<span style="color: teal; font-weight: bold;"> Overview</span>

The CD3 toolkit supports <b>managing multiple OCI environments</b> (such as Production, Development or QA) within a single container by using <b>prefix-based configurations</b>.

Each prefix represents an independent environment, enabling you to isolate resources and outputs, maintain separate configuration files, and run deployments without interference.

<br>

<span style="color: teal; font-weight: bold;"> 📌 Use Cases</span>

This is particularly useful when:

   - Managing Prod and Non-Prod environments within the same container
   - Maintaining separate Terraform outputs for each environment
   - Running parallel or independent deployments

<br>

<span style="color: teal; font-weight: bold;"> 🛠️ Configuration Steps</span>

<b>1. Prepare the properties file:</b>

   &nbsp;&nbsp;&nbsp;Update the <b>connectOCI.properties</b> file as described in <a href="../connect-container-to-oci-tenancy"><u>Connect CD3 Container to OCI</u></a>. <br>

   - Assign a unique prefix for each environment. <br>
      <i>Example:</i> <br>`demo_nonprod`<br> `demo_prod`


<b>2. Customize Environment-Specific Parameters</b>

&nbsp;&nbsp;&nbsp;Each prefix can have its own configuration, such as:

- Different outdir structures
- Separate tenancy details etc., 


<b>3. (Recommended) Use Separate properties Files</b>

 &nbsp;&nbsp;&nbsp;Instead of modifying the same file repeatedly, create environment-specific copies:<br>
   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`connectOCI_demo_prod.properties`<br> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`connectOCI_demo_nonprod.properties` <br>
 
 &nbsp;&nbsp;&nbsp;This helps preserve configuration history and simplify repeated executions.



<b>4. Execute the Script</b>

  - Run connectCloud.py using the appropriate properties file for each prefix.<br>
   <i>Example:</i> <br>
   `python connectCloud.py oci connectOCI_demo_prod.properties` <br>
   `python connectCloud.py oci  connectOCI_demo_nonprod.properties`

<br>



<span style="color: teal; font-weight: bold;"> Multi Prefix with CLI</span>

- The container creates out directories under: `/cd3user/tenancies/`
- Each prefix has its own isolated folder containing Configuration, Generated Terraform files and Environment-specific outputs <br>

    ![CLI](../images/multiple-prefixes-cli.jpg)

<br>


<span style="color: teal; font-weight: bold;"> Multi Prefix with Jenkins</span>

- The Jenkins dashboard appears as follows when configured with two prefixes.

    ![jenkins](../images/multiple-prefixes-jenkins.jpg)



!!! info "Jenkins configuration for new prefix"
      - If connectCloud.py has been run again for a new prefix, then first kill the existing jenkins process and start new after that.
      - Command to get Jenkins process id -  ```ps -ef | grep jenkins```
      - Command to kill - ```kill -9 <process_id>```
      - Start Jenkins using - ```/usr/share/jenkins/jenkins.sh &```