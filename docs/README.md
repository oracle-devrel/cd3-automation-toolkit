# **Getting Started** 
---

<style>
    .grid.cards {
        border-top-color: #5c926c;
        border-radius: 0.5rem;
    }
    .md-typeset a {
    color: #20827bff !important;  
    text-decoration: underline;
    text-decoration-thickness: 0.5px;;
    font-weight: 600 !important;
    transition: color 0.25s ease-in-out; 
}

.md-typeset a:hover {
    color: teal !important;  
    text-decoration-thickness: 2px;
}

</style>

<div class="grid cards" style="border-top-color: #5c926c; border-radius: 1.5rem;" markdown>


-   :material-clock-fast:{ .lg .middle } __Overview__

    ---
    - [What is CD3](cd3-overview.md)<br>
    - [CD3 Workflows](cd3workflows.md)<br>
    - [Architecture](architecture.md)<br>
    - [Services Supported](supportedservices.md)<br>
    - [Excel Templates](excel-templates.md)<br>
    - [AI Analysis](terraform-ai-analysis.md)<br>

-   :material-hammer-screwdriver:{ .lg .middle } __Installing CD3__

    ---
    - [Prerequisites](prerequisites.md)<br>
    - [Launch the container](launch-container.md)<br>
        - [Launch Resource Manager Stack](launch-from-rmstack.md)<br>
        - [Launch from Local Desktop](launch-from-local.md)<br>
    - [Upgrade CD3](upgrade-toolkit.md)<br>



-   :material-monitor-screenshot:{ .lg .middle } __Connect to Cloud__

    ---
    - [Connect CD3 Container to OCI](connect-container-to-oci-tenancy.md)<br>
    - [Connect CD3 Container to Azure](connect-container-to-azure-subscription.md)<br>



-   :material-monitor-screenshot:{ .lg .middle } __Manage OCI__

    ---
    - [Manage OCI with CLI](cd3-cli.md)<br>
        - [Create Resources in OCI using CLI](greenfield-cli.md)<br>
        - [OPA integration](opa-integration.md)<br>
        - [Export Resources from OCI using CLI](nongreenfield-cli.md)<br>
    - [Manage OCI with Jenkins](cd3-jenkins.md)<br>
        - [Jenkins Overview](jenkinsintro.md)<br>
        - [Create Resources in OCI using Jenkins](greenfield-jenkins.md)<br>
        - [Provision multiple Services Together](multiple-services-jenkins.md)<br>
        - [Export Resources from OCI using Jenkins](nongreenfield-jenkins.md)<br>
        - [Commit Local changes to GIT](sync-cli-jenkins.md)<br>  
    - [Must Read](must-read.md)<br>
        - [Manage Network](manage-network.md)<br>
        - [Manage Compute](manage-compute.md)<br>
        - [Manage OCI Network Firewall](manage-firewall.md)<br>



-   :material-monitor-screenshot:{ .lg .middle } __Manage Azure__

    ---
    - [Manage Azure](setUpAzure.md)<br>
    - [Manage Azure with CLI](cd3-azr-cli.md)<br>
        - [Create Resources in Azure](greenfield-azr-cli.md)<br>
        - [Export Resources from Azure](nongreenfield-azr-cli.md)<br>
    

    
<!-- 
-   :material-lightbulb-auto:{ .lg .middle } __Read More for OCI__

    ---
    - [Manage Network](manage-network.md)<br>
    - [Manage Compute](manage-compute.md)<br>
    - [Manage OCI Network Firewall](manage-firewall.md)<br>
     -->

-   :material-feather:{ .lg .middle } __Additional Features__

    ---
    - [Grouping generated TF files](group-tf-files.md)<br>
    - [Remote Management of Terraform State](remotestate.md)<br>
    - [OCI Resource Manager Upload](resource-manager-upload.md)<br>
    - [Support for Additional Attrs](additional-attributes.md)<br>
    - [CD3 Validator](cd3validator.md)<br>
    - [Migrate jobs to user's Jenkins](jobs-migration.md)<br>
   

-  :material-information:{ .lg .middle } __Troubleshooting__

    ---
    - [Expected Behaviour](knownbehaviour.md)<br>
    - [Common Issues](commonissues.md)<br>
    - [FAQs](faq.md)<br>

-  :material-school:{ .lg .middle } __External References__

    ---
    - [Learning Videos](learningvideos.md)<br>
    - [Tutorials](tutorials.md)<br>
</div>