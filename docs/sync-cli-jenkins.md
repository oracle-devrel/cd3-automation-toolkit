# Commit Local changes to GIT

!!! note
    It is recommended to stick to using the toolkit either via CLI or via Jenkins.

!!! note
    The below process will push the updated files to the **develop** branch of the GIT Repository. Successful completion of the resource specific terraform-apply pipeline in Jenkins will update to the **main** branch.

There can be scenarios when updating the terraform_files folder manually via CLI is necessary. Below are some examples:

- The setUpOCI script is executed to generate tfvars for some resources via CLI.
- The **variables_<region\>.tf** file is modified to update image OCID or SSH Key for Compute or Database etc.

 Follow below steps to sync local terraform_files folder to OCI DevOps GIT Repo:

**Step 1:**
 ```
   cd /cd3user/tenancies/<prefix>/terraform_files
 ```
**Step 2:**
 ```
   git status
 ```
 Below screenshot shows changes in variables_phoenix.tf file under phoenix/compute folder.
  
<img width="556" alt="Screenshot 2024-01-17 at 9 12 39 PM" src="../images/gitstatus.png">

**Step 3:**
  ```
   git add -A .
  ```
**Step 4:**
  ```
   git commit -m "msg"
  ```
  
<img width="370" alt="Screenshot 2024-01-17 at 9 13 35 PM" src="../images/gitcommit.png">

**Step 5:**
  ```
    git push
  ```
  
<img width="1500" height="300" alt="Screenshot 2024-01-17 at 9 14 24 PM" src="../images/gitpush.png">

