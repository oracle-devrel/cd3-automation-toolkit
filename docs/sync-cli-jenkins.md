# Commit Local changes to GIT

!!! Tip "Best Practice"
    It is recommended to stick to using the toolkit either via CLI or via Jenkins.

!!! info "Git push workflow"
    The below process will push the updated terraform files to the **develop** branch of the GIT Repository. Successful completion of the resource specific terraform-apply pipeline in Jenkins will update to the **main** branch.

There can be scenarios when updating the terraform_files folder manually via CLI is necessary. Below are some examples:

- The setUpOCI script is executed to generate tfvars for some resources via CLI.
- The `variables_<region>.tf` file is modified to update image OCID or SSH Key for Compute or Database etc.

 Follow below steps to sync local `terraform_files` folder to OCI DevOps GIT Repo:


<span style="color: teal; font-weight: bold;">Step 1:</span>
 ```
   cd /cd3user/tenancies/<prefix>/terraform_files
 ```

<span style="color: teal; font-weight: bold;">Step 2:</span>

 ```
   git status
 ```

 Below screenshot shows changes in `variables_phoenix.tf` file under `phoenix/compute` folder.
  
<img width="556" alt="Screenshot 2024-01-17 at 9 12 39 PM" src="../images/gitstatus.png">


<span style="color: teal; font-weight: bold;">Step 3:</span>
  ```
   git add -A .
  ```

<span style="color: teal; font-weight: bold;">Step 4:</span>

  ```
   git commit -m "msg"
  ```
  
<img width="370" alt="Screenshot 2024-01-17 at 9 13 35 PM" src="../images/gitcommit.png">


<span style="color: teal; font-weight: bold;">Step 5:</span>
  ```
    git push
  ```
  
<img width="1500" height="300" alt="Screenshot 2024-01-17 at 9 14 24 PM" src="../images/gitpush.png">

