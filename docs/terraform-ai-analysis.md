# AI Terraform Plan Analyzer

Terraform is widely used to manage infrastructure as code (IaC). Terraform plan outputs can be large and complex, often spanning thousands of lines.<br>

<span style="font-size:1.3em; font-weight:550;">⚠️ The Challenge</span>

Manually reviewing these plans to identify security risks or misconfigurations is time-consuming and prone to human error. 
Even a small oversight such as exposing a resource publicly can lead to serious issues in production environments.

<br>
<span style="font-size:1.3em; font-weight:550;">🎯 The Solution: Automated AI Review</span>

CD3 introduces an AI-assisted analysis step as part of the Jenkins pipeline to help review Terraform plans.<br>

This feature analyzes Terraform plans for potential security risks and best practice violations, helping identify issues early before deployment.

It leverages Oracle Generative AI from configured regions to perform the following:


1. **Parse the plan**  - Understand the infrastructure changes being introduced.

2. **Identify issues**  - Detect misconfigurations such as open network access or insecure settings.

3. **Summarize findings**  - Generate a clear, human-readable report of risks and recommendations.


This feature helps identify common issues early, improving deployment confidence. It acts as a safety check and complements standard review practices.

<br>
<span style="font-size:1.3em; font-weight:550;">💻 Usage</span>

This is an optional feature in the CD3 Jenkins workflow and can be enabled as part of <a href= "../connect-container-to-oci-tenancy">Connect Container to Tenancy </a>configuration
<br>


<b>1.</b> Open the file: `/cd3user/oci_tools/cd3_automation_toolkit/connectOCI.properties` <br>
<b>2.</b> Set the parameter ```enable_terraform_plan_analysis``` to ```yes```, along with other required config details <br>
<b>3.</b> This configuration takes effect when the `connectCloud.py` script is executed (<a href =" ../connect-container-to-oci-tenancy">see Executing connectCloud.py</a>) <br>
<b>4.</b> Once enabled, it runs automatically as part of the Jenkins build.<br>

<b>To view the results:</b><br>
&nbsp;&nbsp;&nbsp; - Open the Jenkins build<br>
&nbsp;&nbsp;&nbsp; - Check the **Console Output**<br>
&nbsp;&nbsp;&nbsp; - Locate the section: **>> Terraform AI Analysis**<br>

<b>The analysis provides:</b><br>
&nbsp;&nbsp;&nbsp; - **Risk level** – Indicates whether changes are low or high risk  
&nbsp;&nbsp;&nbsp; - **Findings** – List of identified issues  
&nbsp;&nbsp;&nbsp; - **Recommendations** – Suggested fixes  
&nbsp;&nbsp;&nbsp; - **Cost estimation** – Approximate cost based on planned resources  
<br>
<b>Disable AI summary</b> <br>

<b>1.</b> Update the parameter `enable_terraform_plan_analysis` from `yes` to `no` in the file `/cd3user/oci_tools/cd3_automation_toolkit/connectOCI.properties`<br>
<b>2.</b> Re-run `connectCloud.py` script (<a href =" ../connect-container-to-oci-tenancy">see Executing connectCloud.py</a>)<br> 
<b>3.</b> Restart Jenkins using: `/usr/share/jenkins/jenkins.sh &`<br>


