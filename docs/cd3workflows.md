 **CD3 Toolkit Process**

<img width="1200" height="1000" alt="CD3 Toolkit Process" src="../images/CD3-Process.png">
<br>

**The CD3 toolkit supports 2 workflows:**<br>

|🛠️ Workflow | 💡 When to Use | 📌 Highlevel Steps | ✅ Output  |
|----------|-------------|-------|--------|
|  **Create & Manage(Greenfield)** | When setting up a **new OCI tenancy** or creating **new resources** | 1. Fill resource details in the CD3 Excel file  <br> 2. Run the toolkit with `workflow_type = create_resources` <br> 3. Verify the terraform plan & Execute `terraform apply` to create resources <br><br>Detailed steps in [this document](./greenfield-cli.md) |  📦 `.tfvars` files for the resources |
|  **Export & Manage (Non-Greenfield)** | Managing **existing OCI resources** not initially created with CD3 | 1. Use Blank CD3 template as input <br> 2. Run the toolkit with `workflow_type = export_resources`   <br> 3. Run generated terraform import shell scripts to update Terraform state <br> 4. Switch to `create_resources` flow to create/update resources<br><br>Detailed steps in [this document](./nongreenfield-cli.md) |    📝 Excel File with exported resource data <br> + 📦 `.tfvars` files for the resources <br> + 🧾 shell scripts with terraform import commands  |



!!! Info
	CD3 Automation toolkit can be used either via CLI or Jenkins.
  
	📖 Detailed documentation and videos are provided for both options. Check the top panel for navigation.



