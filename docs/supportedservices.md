<!DOCTYPE html>
<html lang="en">
<head> 
    <title>OCI Services Grid</title>
    <style>
        .grid-container {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            padding: 5px;
        }
        .service-card {
            background-color: #f2f2f2;
            padding: 10px;
            margin-top: 0px;
            border-radius: 8px;
            font-size: 90%;
            transition: transform 0.3s ease;
            display: flex; 
            flex-direction: column; 
        }
        .service-card:hover {
            transform: scale(1.05);
        }
        .card-title {
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
        }
        .card-title h3 {
            color: #000000; 
            font-weight: bold; 
            margin: 0;
            padding-bottom: 8px;
        }
        .description {
            display: none;
            margin-bottom: 20px;
            color: #000000;
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        .service-card p {
            margin: 0;
        }
        .service-card:hover .description {
            display: block;
            opacity: 1;
        }
        img {
            height: 50px; 
            width: 50px; 
            border-radius: 5px 5px 0 0;
        }
    </style>
</head>
<body>
    <div class="grid-container">
        <div class="service-card">
            <div class="card-title">
                <h3>IAM</h3>
                <img src="../images/IAM.png" alt="IAM">
            </div>
            <p><a href="../cd3exceltabs#iamidentity"><b>IAM/Identity</b></a></p>
            <div class="description">
                <p><i>Compartments, Groups, Dynamic Groups, Policies, Users, Network Sources</i></p>
            </div>
        </div>
        <div class="service-card">
            <div class="card-title">
                <h3>Governance</h3>
                <img src="../images/governance.png" alt="Governance"> 
            </div>
            <p><a href="../cd3exceltabs#governance"><b>Tagging</b></a></p>
            <div class="description">
                <p><i>Tags (Namespaces, Tag Keys, Default Tags, Cost Tracking Tags)</i></p>
            </div>
            <p><a href="../cd3exceltabs#governance"><b>Quotas</b></a></p>
            <div class="description">
                <p><i>Quota policies</i></p>
            </div>
        </div>
        <div class="service-card">
            <div class="card-title">
                <h3>Cost Management</h3>
                <img src="../images/cost-management.png" alt="Cost Management"> 
            </div>
            <p><a href="../cd3exceltabs#cost-management"><b>Budgets</b></a></p>
            <div class="description">
                <p><i>Budgets, Budget Alert Rules</i></p>
            </div>
        </div>
        <div class="service-card">
            <div class="card-title">
                <h3>Network and Connectivity</h3>
                <img src="../images/network.png" alt="Network"> 
            </div>
            <p><a href="../cd3exceltabs#network"><b>Network</b></a></p>
            <div class="description">
                <p><i>VCNs, Subnets, VLANs, DRGs, IGWs, NGWs, LPGs, Route Tables, DRG Route, Tables, Security Lists, Network Security Groups, Remote Peering Connections, Application Load Balancers, Network Load Balancers</i></p>
            </div>
            <p><a href="../cd3exceltabs#network-firewall"><b>OCI Network Firewall</b></a></p>
            <div class="description">
                <p><i>OCI Network Firewall and Policy</i></p>
            </div>
            <p><a href="../cd3exceltabs#private-dns"><b>DNS Management</b></a></p>
            <div class="description">
                <p><i>Private DNS - Views, Zones, RRSets/Records and Resolvers</i></p>
            </div>
        </div>
        <div class="service-card">
            <div class="card-title">
                <h3>Infrastructure</h3>
                <img src="../images/infrastructure.png" alt="Infrastructure Icon"> 
            </div>
            <p><a href="../cd3exceltabs#compute"><b>Compute</b></a></p>
            <div class="description">
                <p><i>Instances supporting Market Place Images, Remote Exec, Cloud-Init scripts, Dedicated VM Hosts</i></p>
            </div>
            <p><a href="../cd3exceltabs#storage"><b>Storage</b></a></p>
            <div class="description">
                <p><i>FSS, Block and Boot Volumes, Backup Policies, Object Storage Buckets</i></p>
            </div>
            <p><a href="../cd3exceltabs#database"><b>Database</b></a></p>
            <div class="description">
                <p><i>Exa Infra, ExaCS, DB Systems VM and BM, ATP, ADW, MySQL(DB Systems and configurations)</i></p>
            </div>
            <p><a href="../cd3exceltabs#sddcs-tab"><b>SDDCs</b></a></p>
            <div class="description">
                <p><i>Oracle Cloud VMWare Solutions</i></p>
            </div>
        </div>
        <div class="service-card">
            <div class="card-title">
                <h3>Observability & Management</h3>
                <img src="../images/observability.png" alt="Observability Icon"> 
            </div>
            <p><a href="../cd3exceltabs#monitoring-services"><b>Monitoring</b></a></p>
            <div class="description">
                <p><i>Events, Notifications, Alarms, Service Connector Hub (SCH)</i></p>
            </div>
            <p><a href="../cd3exceltabs#logging-services"><b>Logging Services</b></a></p>
            <div class="description">
                <p><i>VCN Flow Logs, LBaaS access and error Logs, OSS Buckets Logs, Firewall Logs, FSS Logs</i></p>
            </div>
        </div>
        <div class="service-card">
            <div class="card-title">
                <h3>Developer Services</h3>
                <img src="../images/developerservices.png" alt="Developer Services Icon"> 
            </div>
            <p><a href="../cd3exceltabs#developer-services"><b>Developer Services</b></a></p>
            <div class="description">
                <p><i>Upload to Resource Manager, Oracle Kubernetes Engine (OKE)</i></p>
            </div>
        </div>
        <div class="service-card">
            <div class="card-title">
                <h3>Security</h3>
                <img src="../images/security.png" alt="Security Icon"> 
            </div>
            <p><a href="opa-integration.md"><b>Policy Enforcement</b></a></p>
            <div class="description">
                <p><i>OPA - Open Policy Agent</i></p>
            </div>
            <p><a href="../cd3exceltabs#security"><b>KMS</b></a></p>
            <div class="description">
                <p><i>Vaults and Keys</i></p>
            </div>
            <p><a href="../cd3exceltabs#security"><b>Cloud Guard</b></a></p>
            <div class="description">
                <p><i>Cloud Guard</i></p>
            </div>
        </div>
        <div class="service-card">
            <div class="card-title">
                <h3>Other OCI Tools</h3>
                <img src="../images/FSDR.png" alt="Other OCI Tools Icon">
            </div>
            <p><a href="../other-oci-tools#cis-compliance-checker-script"><b>CIS Landing Zone Compliance</b></a></p>
            <div class="description">
                <p><i>Download and Execute CIS Compliance Check Script</i></p>
            </div>
            <p><a href="../other-oci-tools#showoci-script"><b>Show OCI Report</b></a></p>
            <div class="description">
                <p><i>Download and Execute showOCI Script</i></p>
            </div>
            <p><a href="../other-oci-tools#oci-fsdr"><b>OCI FSDR</b></a></p>
            <div class="description">
                <p><i>Export and Update DR Plans</i></p>
            </div>
        </div>
    </div>
</body>
</html>
