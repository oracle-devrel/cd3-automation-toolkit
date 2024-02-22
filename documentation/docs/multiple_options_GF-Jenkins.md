# Provisioning of multiple services together

>***Note - For any service that needs Network details eg compute, database, loadbalancers ets, 'network' pipeline needs to be executed prior to launching that service pipeline.***

* Multiple options can be selected simultaneously while creating resources in OCI using setUpOCI pipeline . But if one of the services is dependent upon the availability of another service eg  'Network' (Create Network) and 'Compute' (Add Instances); In such scenarios, terraform-apply pipeline for compute will fail as shown in below screenshot (last stage in the pipeline) -
 ![tuxpi com 1706871371](https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/959dea07-b569-4908-967c-d4d1efbafe04)
<br>

<br>* Clicking on 'Logs' for Stage: sanjose/compute and clicking on the pipeline will dispay below -

> ![tuxpi com 1706871675](https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/65536e92-6612-4c6e-9d79-4a347a5cee9a)
<br>

<br>* Clicking on 'Logs' for Stage Terraform Plan displays - 

> ![tuxpi com 1706871787](https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/711e1687-690f-4cbd-8abc-3fd4da108f9f)

- This is expected because pipeline for 'compute' expects network to be already existing in OCI to launch a new instance.
- To resolve this, Proceed with terraform-apply pipeline for 'network' and once it is successfuly completed, trigger terraform-apply pipeline for 'compute' manually by clicking on 'Build Now' from left menu.

> ![tuxpi com 1706871906](https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/c3b7adb9-183b-4b79-bf9e-d492b3a5f7aa)
