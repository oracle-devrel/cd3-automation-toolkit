# Steps to Upgrade Your Toolkit (For Existing Customers):

## Upgrade to Release v10.1 from v10
1. Follow the steps in [Launch Docker Container](/cd3_automation_toolkit/documentation/user_guide/Launch_Docker_container.md) to build new image with latest code and launch the container by specifying same path for <directory_in_local_system_where_the_files_must_be_generated> to keep using same outdir.
2. There are minor upgrades to terraform modules. In order to use the latest modules, copy the contents(.tf files and modules directory) from _/cd3user/oci_tools/cd3\_automation\_toolkit/user-scripts/terraform_ <b>to</b> _/cd3user/tenancies/<customer\_name>/terraform\_files/<region\_dir>_.
3. Changes to the CD3 excel sheet templates include correction of the dropdowns for all tabs, few changes in Policies tab wrt policy statements. So users can keep using the v10 templates.
4. The new release supports a separate directory for each service. In order to use this feature for existing customers, execute createTenancy.py using a new outdir with  'outdir_structure_file' parameter set and then run export of the tenanncy into this new outdir using Non Greenfield workflow.

## Upgrade to Release v10 from v9.2.1
1. Follow the steps in [Launch Docker Container](/cd3_automation_toolkit/documentation/user_guide/Launch_Docker_container.md) to build new image with latest code and launch the container by specifying same path for <directory_in_local_system_where_the_files_must_be_generated> to keep using same outdir.
2. Use new excel sheet templates to use OKE and SCH.
3. For existing services, user can continue using existing outdir.

<br><br>
<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/FAQ.md">:arrow_backward: Prev</a> | <a href="/README.md#table-of-contents-bookmark">Next :arrow_forward:</a> |
| :---- | -------: |
