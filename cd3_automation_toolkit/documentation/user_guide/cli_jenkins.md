# Switch between using the toolkit via CLI and Jenkins UI

> **Note -** 
  >***It is suggested to stick to using the toolkit either via CLI or via Jenkins.***

There can be scenarios when you need to update the terraform_files folder manually via CLI. Below are some examples:

- You executed setUpOCI script to generate tfvars for some resources via CLI.
- You updated variables_<region>.tf file to update OCID or SSH Key for compute or database etc.

Please folow below steps to synch local terrafor_files folder to OCI DevOps GIT Repo:

- ```cd /cd3user/tenancies/<customer_name>/terraform_files```
- ```git status```
<img width="556" alt="Screenshot 2024-01-17 at 9 12 39 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/1a40a5b8-622e-49ef-948d-c516d5e8f712">

- ```git add -A .```

- ```git commit -m "msg"```
<img width="372" alt="Screenshot 2024-01-17 at 9 13 35 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/60e2be71-63c0-4362-a8ce-a02a4fcafe49">

- ```git push```
  <img width="1192" alt="Screenshot 2024-01-17 at 9 14 24 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/08ab71d7-263a-4267-945f-92428741ebb0">

