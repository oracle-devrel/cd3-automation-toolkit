# Provisioning of multiple services together

>***Note - For any service that needs Network details eg compute, database, loadbalancers ets, 'network' pipeline needs to be executed prior to launching that service pipeline.***

You can chose to create multiple OCI resources together by selecting multiple options in setUpOCI pipeline simultaneously. But if one of the services is dependent upon the availability of another service eg You may chose 'Network' (Create Network) and 'Compute' (Add Instances) together. In such scenarios, terraform-apply pipeline for compute will fail as shown in below screenshot (last stage in the pipeline) -

<img width="1216" alt="Screenshot 2024-01-29 at 11 22 53 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/cbd63490-7e4f-49dc-b813-03881a4c6e67">

- Clicking on 'Logs' for Stage: sanjose/compute and clicking on the pipeline will dispay below - 
<img width="927" alt="Screenshot 2024-01-29 at 11 25 24 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/dbdb1be7-bca9-4944-9b3c-987f184b8a95">

- Clicking on 'Logs' for Stage Terraform Plan displays - 

<img width="1497" alt="Screenshot 2024-01-29 at 11 26 41 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/e6b7c60b-256e-40b5-a462-92afd0c9cbf5">

- This is expected because pipleine for 'compute' expects network to be already existing in OCI to launch a new instance.
- To resolve this, Proceed with terraform-apply pipeline for 'network' and once it is successfuly completed, trigger terraform-apply pipeline for 'compute' manually by clicking on 'Build Now' from left menu.

<img width="1223" alt="Screenshot 2024-01-29 at 11 32 13 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/7bd7b4a8-62af-4a98-9250-9d96515cda4d">

- 
- 
<br><br>
<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/GF-Jenkins.md">:arrow_backward: Prev</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/NonGreenField-Jenkins.md">Next :arrow_forward:</a> |
| :---- | -------: |
