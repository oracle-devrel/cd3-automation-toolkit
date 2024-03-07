# Provisioning of multiple services together

!!! note
    For any service that needs Network details eg compute, database, loadbalancers etc, terraform-apply pipeline for 'network' needs to be executed prior to launching that service pipeline as explained below.

* Multiple options can be selected simultaneously while creating resources in OCI using setUpOCI pipeline . But if one of the services is dependent upon the availability of another service eg  'Network' (Create Network) and 'Compute' (Add Instances); In such scenarios, terraform-apply pipeline for compute will fail as shown in below screenshot (last stage in the pipeline) -

    ![image](../images/multiservices-1.jpeg)


* Clicking on 'Logs' for Stage: sanjose/compute and clicking on the pipeline will dispay below -

    ![image](../images/multiservices-2.jpeg)

* Clicking on 'Logs' for Stage Terraform Plan displays - 

    ![image](../images/multiservices-3.jpeg)


- This is expected because pipeline for 'compute' expects network to be already existing in OCI to launch a new instance.
- To resolve this, Proceed with terraform-apply pipeline for 'network' and once it is successfuly completed, trigger terraform-apply pipeline for 'compute' manually by clicking on 'Build Now' from left menu.

    ![image](../images/multiservices-4.jpeg)
