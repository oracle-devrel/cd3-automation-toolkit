# Steps to Upgrade Your Toolkit (For Existing Customers using older versions):

1. Follow the steps in [Launch Docker Container](launch-container.md) to build new image with latest code and launch the new container.
2. Use export_resources(Non Greenfield) workflow to export the required OCI services into new excel sheet and the tfvars. Run terraform import commands also.
3. Once terraform is in synch, Switch to create_resources (Greenfield) workflow and use for any future modifications to the infra.
