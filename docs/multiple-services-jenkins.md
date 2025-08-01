# Provisioning of multiple services together

!!! Important
    For services that require network details, such as compute, database, and load balancers, the 'network' apply pipeline must be executed before launching the service pipeline, as explained below.

* Multiple options can be selected simultaneously while creating resources in OCI using setUpOCI pipeline . In scenarios where one service depends on another service's availability, such as 'Network' (Create Network) and 'Compute' (Add Instances), the apply pipeline for compute will fail. Check the below image.


    ![image](../images/multiservices-1.jpg)


* Clicking on 'Logs' for Stage: london/compute and clicking on the pipeline will display below -

    ![image](../images/multiservices-2.jpg)

* Clicking on 'Logs' for Stage Terraform Plan displays - 

    ![image](../images/multiservices-3.jpg)


- This is expected because pipeline for 'compute' expects network to be already existing in OCI to launch a new instance.
- To resolve this, Proceed with apply pipeline for 'network' and once it is successfuly completed, trigger apply pipeline for 'compute' manually by clicking on 'Build Now' from left menu.

    ![image](../images/multiservices-4.jpg)
