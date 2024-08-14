# Open Policy Agent for Terraform

OPA is a powerful policy-as-code framework that enables you to define and enforce policies across your infrastructure-as-code (IaC) deployments. With OPA, you can seamlessly integrate policy checks into your Terraform workflows, ensuring that your infrastructure deployments adhere to your organization's security, compliance, and operational requirements.

By leveraging OPA for Terraform, you can automate policy enforcement, eliminate manual checks, and enforce best practices consistently across your infrastructure-as-code projects. With OPA, you gain enhanced visibility and control over your Terraform deployments, reducing the risk of misconfigurations, security vulnerabilities, and compliance issues. 

As part of CD3, we have meticulously developed an initial set of policies. These policies serve as your initial starting point, ensuring that any Infrastructure-as-Code (IAC) deployments made for Oracle Cloud Infrastructure (OCI) meet the organisation's security and compliance standards.


**Run OPA inside CD3 container**

 1. Open your command line interface inside CD3 container and run OPA. You should see all available options for OPA.

        opa --help
    Currently CD3 container has OPA version 0.55.0 installed.

 2. Generate the terraform/tofu plan output in json format since OPA accepts that format alone for evaluation. Use **tofu** command instead of **terraform** if OpenTofu is configured as the IaC tool.
 
   
         terraform plan -out tfplan.binary
	     terraform show -json tfplan.binary > tfplan.json

 3. Run the terraform plan against all the available OPA rules. It should return an empty array which means the plan has no non-compliant action against CIS benchmarks.

        opa eval -f pretty -b /cd3user/oci_tools/cd3_automation_toolkit/user-scripts/OPA -i tfplan.json data.terraform.deny --fail-defined

    
Alternatively, run the following command to evaluate just a sinle OPA rule say "deny_ingress_for_sl.rego" policy with a pretty output format:

        opa eval -f pretty -d /cd3user/oci_tools/cd3_automation_toolkit/user-scripts/OPA/Networking/oci_deny_ingress_for_sl.rego -i tfplan.json data.terraform.deny

This command will analyze the "tfplan.json" input file against the policy and display the evaluation results with a user-friendly format.

<br><br>
<div align='center'>

 
</div>
