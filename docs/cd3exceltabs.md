# OCI Services currently supported by Automation Toolkit

Click on the links below to know about the specifics of each tab in the Excel templates.

<style>
  h3[id] {
    display: flex;
    align-items: center;
    gap: 20px;
  }

  [data-md-color-scheme="oracle"] h3:target {
    background-color: #90E0D5;       
    border-left: 6px solid #027d6c;  
    padding-left: 16px;
    color: #2D4954;                  
    transition: background-color 0.3s ease, color 0.3s ease;
  }

  [data-md-color-scheme="slate"] h3:target {
    background-color: #2D4954;       
    border-left: 6px solid #90E0D5;  
    padding-left: 16px;
    color: #ffffff;                  
    transition: background-color 0.3s ease, color 0.3s ease;
  }

  h3 img {
    height: 30px;
    width: 30px;
  }
</style>



<div style="display: flex; gap: 100px;">

  <!-- Left Column -->
  <div style="flex: 1; min-width: 300px;">

    <!-- IAM -->
    <h3 id="iamidentity" style="display: flex; align-items: center; gap: 8px;">
      <img src="../images/IAM.png" alt="IAM" style="height: 30px; width: 30px;">  
      <b>IAM / Identity</b> 
    </h3>
    <div style="padding-left: 20px;">
      <ul>
        <li><a href="../tabs#compartments-tab">Compartments</a></li>
        <li><a href="../tabs#groups-tab">Groups / Dynamic Groups</a></li>
        <li><a href="../tabs#policies-tab">Policies</a></li>
        <li><a href="../tabs#users-tab">Users</a></li>
        <li><a href="../tabs#network-sources-tab">Network Sources</a></li>
      </ul>
      <a href="../terraform/identity">🔗 Sample auto.tfvars for Identity components</a>
    </div>

    <h3 id="governance" style="display: flex; align-items: center; gap: 8px;">
      <img src="../images/governance.png" alt="Governance" style="height: 30px; width: 30px;">  
      <b>Governance</b>
    </h3>
    <div style="padding-left: 20px;">
      <ul>
        <li><a href="../tabs#tags-tab">Tags</a></li>
        <li><a href="../tabs#quotas-tab">Quotas</a></li>
      </ul>
      <a href="../terraform/governance/#1-tag-namespaces">🔗 Sample auto.tfvars for Tags</a><br>
      <a href="../terraform/governance/#4-quotas">🔗 Sample auto.tfvars for Quotas</a>
    </div>

    <h3 id="cost-management" style="display: flex; align-items: center; gap: 8px;">
      <img src="../images/cost-management.png" alt="Cost Management" style="height: 30px; width: 30px;">  
      <b>Cost Management</b>
    </h3>
    <div style="padding-left: 20px;">
      <ul>
        <li><a href="../tabs#budgets-tab">Budgets</a></li>
      </ul>
      <a href="../terraform/costmanagement/#budgets">🔗 Sample auto.tfvars for Budgets</a><br>
      <a href="../terraform/costmanagement/#budget-alert-rules">🔗 Sample auto.tfvars for Budget Alert Rules</a>
    </div>

    <h3 id="network" style="display: flex; align-items: center; gap: 8px;">
      <img src="../images/network.png" alt="Network" style="height: 30px; width: 30px;">  
      <b>Network</b>
    </h3>
    <div style="padding-left: 20px;">
      <ul>
        <li><a href="../tabs#a-vcns-tab">VCNs</a></li>
        <li><a href="../tabs#b-drgs-tab">DRGs - Attachments</a></li>
        <li><a href="../tabs#c-vcn-info-tab">VCN Info</a></li>
        <li><a href="../tabs#d-dhcp-tab">DHCP</a></li>
        <li><a href="../tabs#e-subnetsvlans-tab">Subnets / VLANs</a></li>
        <li><a href="../tabs#f-rules">DRG / Route / Sec Rules</a></li>
        <li><a href="../tabs#g-nsgs">NSGs</a></li>
      </ul>
      <a href="../terraform/network">🔗 Sample auto.tfvars for Network components</a>
    </div>

    <h3 id="networkfirewall" style="display: flex; align-items: center; gap: 8px;">
      <img src="../images/firewall.png" alt="Firewall" style="height: 30px; width: 30px;">  
      <b>OCI Network Firewall</b>
    </h3>
    <div style="padding-left: 20px;">
      <ul>
        <li><a href="../tabs#firewall-tabs">Firewall</a></li>
      </ul>
      <a href="../terraform/firewall">🔗 Sample auto.tfvars for Firewall components</a>
    </div>

    <h3 id="monitoring-services" style="display: flex; align-items: center; gap: 8px;">
      <img src="../images/observability.png" alt="Observability Icon" style="height: 30px; width: 30px;">  
      <b>Monitoring Services</b>
    </h3>
    <div style="padding-left: 20px;">
      <ul>
        <li><a href="../tabs#notifications-tab">Notifications</a></li>
        <li><a href="../tabs#events-tab">Events</a></li>
        <li><a href="../tabs#alarms-tab">Alarms</a></li>
        <li><a href="../tabs#serviceconnectors-tab">Service Connectors</a></li>
      </ul>
      <a href="../terraform/managementservices">🔗 Sample auto.tfvars for Alarms, Notifications, Events</a><br>
      <a href="../terraform/sch">🔗 Sample auto.tfvars for Service Connectors</a>
    </div>

    <h3 id="developer-services" style="display: flex; align-items: center; gap: 8px;">
      <img src="../images/oke.png" alt="Observability Icon" style="height: 30px; width: 30px;">  
      <b>Developer Services</b>
    </h3>
    <div style="padding-left: 20px;">
      <ul>
        <li><a href="../resource-manager-upload">Upload to OCI Resource Manager Stack</a></li>
        <li><a href="../tabs#oke-tab">OKE</a></li>
      </ul>
      <a href="../terraform/managementservices">🔗 Sample auto.tfvars for OKE components- Clusters, Nodepools</a><br>
    </div>

    <h3 id="sddcs" style="display: flex; align-items: center; gap: 8px;">
      <img src="../images/infrastructure.png" alt="compute Icon" style="height: 30px; width: 30px;">  
      <b>SDDCs</b>
    </h3>
    <div style="padding-left: 20px;">
      <ul>
        <li><a href="../tabs#sddcs-tab">OCVS</a></li>
      </ul>
      <a href="../terraform/sddc">🔗 Sample auto.tfvars for OCVS</a><br>
    </div>


    <h3 id="private-dns" style="display: flex; align-items: center; gap: 8px;">
      <img src="../images/network.png" alt="Network" style="height: 30px; width: 30px;">  
      <b>Private DNS</b>
    </h3>
    <div style="padding-left: 20px;">
      <ul>
        <li><a href="../tabs#dns-views-zones-records-tab">Views / Zones / Records</a></li>
        <li><a href="../tabs#dns-resolvers-tab">Resolvers</a></li>
      </ul>
      <a href="../terraform/dns">🔗 Sample auto.tfvars for DNS components</a>
    </div>

    <h3 id="load-balancer" style="display: flex; align-items: center; gap: 8px;">
      <img src="../images/loadbalancer.png" alt="Load Balancer" style="height: 30px; width: 30px;">  
      <b>Load Balancer</b>
    </h3>
    <div style="padding-left: 20px;">
      <ul>
        <li><a href="../tabs#lb-hostname-certs-tab">Hostname & Certs</a></li>
        <li><a href="../tabs#lb-backend-set-and-backend-servers-tab">Backends</a></li>
        <li><a href="../tabs#lb-ruleset-tab">Rule Sets</a></li>
        <li><a href="../tabs#lb-path-route-set-tab">Path Routes</a></li>
        <li><a href="../tabs#lb-routing-policy-tab">Routing Policy</a></li>
        <li><a href="../tabs#lb-listeners-tab">Listeners</a></li>
      </ul>
      <a href="../terraform/loadbalancer">🔗 Sample auto.tfvars for Load Balancer components</a>
    </div>

    <h3 id="compute" style="display: flex; align-items: center; gap: 8px;">
      <img src="../images/infrastructure.png" alt="Infrastructure Icon" style="height: 30px; width: 30px;">  
      <b>Compute</b>
    </h3>
    <div style="padding-left: 20px;">
      <ul>
        <li><a href="../tabs#dedicatedvmhosts-tab">Dedicated VM Hosts</a></li>
        <li><a href="../tabs#instances-tab">Instances</a></li>
      </ul>
      <a href="../terraform/compute">🔗 Sample auto.tfvars for Compute</a>
    </div>

    <h3 id="storage" style="display: flex; align-items: center; gap: 8px;">
      <img src="../images/storage.png" alt="storage" style="height: 30px; width: 30px;">  
      <b>Storage</b>
    </h3>
    <div style="padding-left: 20px;">
      <ul>
        <li><a href="../tabs#blockvolumes-tab">Block Volumes</a></li>
        <li><a href="../tabs#fss-tab">File Storage (FSS)</a></li>
        <li><a href="../tabs#buckets-tab">Object Storage Buckets</a></li>
      </ul>
      <a href="../terraform/storage#block-volumes">🔗 Sample auto.tfvars for Block Volumes</a><br>
      <a href="../terraform/storage#fss">🔗 Sample auto.tfvars for File Storage</a><br>
      <a href="../terraform/storage#buckets">🔗 Sample auto.tfvars for Object Buckets</a>
    </div>

    <h3 id="oracle-database" style="display: flex; align-items: center; gap: 8px;">
      <img src="../images/database.png" alt="Database Icon" style="height: 30px; width: 30px;">  
      <b>Oracle Database</b>
    </h3>
    <div style="padding-left: 20px;">
      <ul>
        <li><a href="../tabs#dbsystems-vm-bm-tab">DBSystems - VM/BM</a></li>
        <li><a href="../tabs#exacs">Exadata CS</a></li>
        <li><a href="../tabs#adb-tab">Autonomous DB</a></li>
      </ul>
      <a href="../terraform/adb">🔗 Sample auto.tfvars for ADB</a><br>
      
    </div>

    <h3 id="mysql-database" style="display: flex; align-items: center; gap: 8px;">
      <img src="../images/database.png" alt="Database Icon" style="height: 30px; width: 30px;">  
      <b>MySQL Database</b>
    </h3>
    <div style="padding-left: 20px;">
      <ul>
        <li><a href="../tabs#mysql-tabs">MySQL</a></li>
      </ul>
    </div>


    <h3 id="logging-services" style="display: flex; align-items: center; gap: 8px;">
      <img src="../images/logging.png" alt="Logging" style="height: 30px; width: 30px;">  
      <b>Logging Services</b>
    </h3>
    <div style="padding-left: 20px;">
      <ul>
        <li><a href="../tabs#vcn-flow-logs">VCN Flow Logs</a></li>
        <li><a href="../tabs#lbaas-logs">LBaas Logs</a></li>
        <li><a href="../tabs#oss-logs">OSS Logs</a></li>
        <li><a href="../tabs#fss-logs">FSS Logs</a></li>
        <li><a href="../tabs#firewall-logs">Firewall Logs</a></li>
      </ul>
      <a href="../terraform/logging#vcn-flow-logs">🔗 Sample auto.tfvars for VCN Flow Logs</a><br>
      <a href="../terraform/logging#load-balancer-logs">🔗 Sample auto.tfvars for Load balancer Logs</a><br>
      <a href="../terraform/logging#object-storage-logs">🔗 Sample auto.tfvars for Object storage Logs</a><br>
      <a href="../terraform/logging#nfs-logs">🔗 Sample auto.tfvars for File Storage Logs</a><br>
      <a href="../terraform/logging#firewall-logs">🔗 Sample auto.tfvars for Firewall Logs</a><br>
    </div>


    <h3 id="security" style="display: flex; align-items: center; gap: 8px;">
      <img src="../images/security.png" alt="Security Icon" style="height: 30px; width: 30px;">  
      <b>Security</b>
    </h3>
    <div style="padding-left: 20px;">
      <ul>
        <li><a href="../tabs#kms-tab">KMS</a></li>
        <li><a href="../tabs#cloud-guard">Cloud Guard</a></li>
      </ul>
      <a href="../terraform/security/#1vaults">🔗 Sample auto.tfvars for KMS Vaults</a><br>
       <a href="../terraform/security/#2keys">🔗 Sample auto.tfvars for KMS Keys</a><br>
    </div>


  </div>

</div>

