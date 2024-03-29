# Switch between using the toolkit via CLI and Jenkins UI

> **Note -** 
  >***It is recommended to stick to using the toolkit either via CLI or via Jenkins.***

There can be scenarios when you need to update the **terraform_files** folder manually via CLI. Below are some examples:

- You executed setUpOCI script to generate tfvars for some resources via CLI.
- You updated **variables_\<region\>.tf** file to update image OCID or SSH Key for Compute or Database etc.

Please folow below steps to sync local terraform_files folder to OCI DevOps GIT Repo:

- ```cd /cd3user/tenancies/<customer_name>/terraform_files```
- ```git status```
  <br>Below screenshot shows changes in variables_phoenix.tf file under phoenix/compute folder.
  
  <img width="556" alt="Screenshot 2024-01-17 at 9 12 39 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/70213341/e805c930-6aa8-4f16-a65a-e9e8fe1465c4">

- ```git add -A .```

- ```git commit -m "msg"```
  
    <img width="370" alt="Screenshot 2024-01-17 at 9 13 35 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/70213341/96998ed0-c89b-4164-ab9b-d68ecedb9f35">

- ```git push```
  
    <img width="1500" height="300" alt="Screenshot 2024-01-17 at 9 14 24 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/70213341/69ecca46-ff55-4e3f-ad0b-36e18d7347e3">

<br><br>
<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/NonGreenField-Jenkins.md">:arrow_backward: Prev</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/remote_state.md">:arrow_forward: Next</a> |
| :---- | -------: |
  
</div>
