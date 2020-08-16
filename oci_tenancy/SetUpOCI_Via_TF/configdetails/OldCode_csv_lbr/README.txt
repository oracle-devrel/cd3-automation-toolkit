There are two (2) scripts that make up the FSS tools
CreateLBConfFile.py - creates Terraform File for Loadbalancer service based on input CSV file
                          Takes as input: a CSV file with following header
                          [LBName,LBSize,LBSubnet1,LBSubnet2,LB_BES_Name,LBURL,LBHostName,LBListener]
CreateLBBackend.py - creates and add backend servers for the load-balancer
                        Takes as input:
                        --lbbackendfile   : same csv file which is used in CreateLBConfFile.py
                        --excludedServerList : optional argument, a csv files with list of servers which should be excluded,
                            while adding backend servers to load-balancer

Order of operations:
1. Create/update CSV file with the required entries for LB - See  sample_lb_file.csv file for ref.
2. Execute the CreateLBConfFile.py script with required inputs
3. Execute the CreateLBBackend.py script with required inputs
4. Review contents of outputdir directory 'terraformfiles'
5. Add them to the Terraform environment and validate: terraform plan
6. Deploy to the clients OCI environmnet: terraform apply


Example output:
C:\Users\jsaleh\Python\python.exe D:/GitRepo/oci/oci_tenancy/LoadBalancerService/CreateLBConfFile.py
usage: CreateLBConfFile.py [-h] cvsfilename

CSV file name

positional arguments:
  cvsfilename  CSV file with required details with following columns [LBName,L
               BSize,LBSubnet1,LBSubnet2,LB_BES_Name,LBURL,LBHostName,LBListen
               er]

optional arguments:
  -h, --help   show this help message and exit


C:\Users\jsaleh\Python\python.exe D:/GitRepo/oci/oci_tenancy/FileSystemService/CreateLBBackend.py
usage: CreateLBBackend.py [-h] [--lbbackendfile LBBACKENDFILE]
                          [--excludedServerList EXCLUDEDSERVERLIST]

CSV file name

optional arguments:
  -h, --help            show this help message and exit
  --lbbackendfile LBBACKENDFILE
                        CSV file with required details with following columns
                        [LBName,LBSize,LBSubnet1,LBSubnet2,LB_BES_Name,LBURL,L
                        BHostName,LBListener]
  --excludedServerList EXCLUDEDSERVERLIST
                        CSV file with server to be execluded for each
                        backendset
