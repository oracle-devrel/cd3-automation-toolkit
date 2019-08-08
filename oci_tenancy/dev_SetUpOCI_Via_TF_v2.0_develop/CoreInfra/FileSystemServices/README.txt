There are two (2) scripts that make up the FSS tools
CreateFSS-MTConfFile.py - creates the the FSS Mount Target Terraform File
                          Takes as input: a properties file and entry to use out of that properties file to create the
                          FSS Mount Target
CreateFSSConfFile.py - creates the FSS Terraform Files
                        Takes as input: the same properties file used in CreateFSS-MTConfFile.py, a CSV file with entries for each FSS to create
                        - one per line/row, and entry to use out of the properties file to create the FSS Mount Target

Order of operations:
1. Create/update properties file with the required entries for FSS - See example of oci-tf-fss.properties file for examples of required entries
2. Execute the CreateFSS-MTConfFile.py script with rquired inputs
3. Execute the CreateFSSConfFile.py script with required inputs
4. Review contents of outputdir directory
5. Add them to the Terraform environment and validate: terraform plan
6. Deploy to the clients OCI environmnet: terraform apply


Example output:
C:\Users\jsaleh\Python\python.exe D:/GitRepo/oci/oci_tenancy/FileSystemService/CreateFSS-MTConfFile.py
usage: CreateFSS-MTConfFile.py [-h] [--properties PROPERTIES] [--fss FSS]

Creates the FSS Mount Target File in defined output directory defined in
propoerties file.

optional arguments:
  -h, --help            show this help message and exit
  --properties PROPERTIES
                        Properties File to use. Must have a [FSS] section
  --fss FSS             From Properties File, which Mount Target to create
                        [FSS#]. Must have a [FSS#] section where # is the
                        number of FSS to create


C:\Users\jsaleh\Python\python.exe D:/GitRepo/oci/oci_tenancy/FileSystemService/CreateFSSConfFile.py
usage: CreateFSSConfFile.py [-h] [--properties PROPERTIES]
                            [--csvfilename CSVFILENAME] [--fss FSS]

FSS Input File in CSV Format

optional arguments:
  -h, --help            show this help message and exit
  --properties PROPERTIES
                        Properties File to use. Must have a [FSS] section
  --csvfilename CSVFILENAME
                        FSS CSV file with required details with following colu
                        mns:Name,AD[1,2,3],path,sourceCIDR,access[READ_ONLY,RE
                        AD_WRITE],GID,UID,IDSquash[NONE,ALL,ROOT],require_ps_p
                        ort[true,false]
  --fss FSS             From Properties File, which Mount Target to use when
                        creating FSS

