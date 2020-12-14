from SetUpOCI_Via_TF.commonTools import *
import shutil
import oci
import os
from oci.resource_manager.models import CreateStackDetails
import base64
from oci.resource_manager.models import CreateZipUploadConfigSourceDetails
from django.http import HttpResponse


class GenerateTerraform():
    def __init__(self, tfForm):
        self.tfForm = tfForm

    def delete_folders(self):
        os.chdir('media')
        user = self.tfForm.Username.replace(' ', '_')
        shutil.rmtree(user + '/confidential', ignore_errors=True)
        shutil.rmtree(user + '/documents', ignore_errors=True)

    def generate_tf(self):
        #try
            user = self.tfForm.Username.replace(' ', '_')
            if self.tfForm.Stack_Name is None:
                self.tfForm.Stack_Name = "CD3aaS_" + user
                self.tfForm.save()
            os.chdir(user)
            os.makedirs("documents", exist_ok=True)
            input_outdir = os.getcwd() + "/documents/" + self.tfForm.Tenancy_Name
            input_config_file = os.getcwd() + "/confidential/" + self.tfForm.Tenancy_Name + "/config"
            os.chdir('..')
            input_key_file = os.getcwd() + "/" + str(self.tfForm.Key_File)
            input_cd3file = os.getcwd() + "/" + str(self.tfForm.CD3_Excel)
            oname = open(input_config_file, "w+")
            tempStr = "[DEFAULT]\ntenancy = " + self.tfForm.Tenancy_OCID + "\nfingerprint = " + self.tfForm.Fingerprint + "\nuser = " + self.tfForm.User_OCID + "\nkey_file = " + input_key_file + "\nregion = " + self.tfForm.Region
            oname.write(tempStr)
            oname.close()
            os.chdir('../SetUpOCI_Via_TF')
            ct = commonTools()
            ct.get_subscribedregions(input_config_file)
            os.chdir('../media/' + user + '/documents/')
            for reg in ct.all_regions:
                if not os.path.exists(input_outdir + "/" + reg):
                    os.makedirs(input_outdir + "/" + reg)
                    file = self.tfForm.Tenancy_Name + "/" + reg + "/provider.tf"
                    oname = open(file, "w+")
                    tempStr = "provider \"oci\" { " + "\n" + "  region = var.region" + "\n" + "}"
                    oname.write(tempStr)
                    oname.close()
                    file = self.tfForm.Tenancy_Name + "/" + reg + "/variables_" + reg + ".tf"
                    oname = open(file, "w+")
                    tempStr = "variable \"tenancy_ocid\" { \n            type = string\n            default = \"" + self.tfForm.Tenancy_OCID + "\" \n}\nvariable \"region\" {\n            type = string\n            default = \"" + ct.region_dict[reg].strip() + "\"\n}"
                    oname.write(tempStr)
                    oname.close()

            os.chdir('../../../SetUpOCI_Via_TF')
            command = "python fetch_compartments_to_variablesTF.py " + input_outdir + " --configFileName " + input_config_file
            exitVal = os.system(command)
            if (exitVal == 1) or (exitVal == 256):
                print("Error encountered. Please try again!!!")
                exit()

            if self.tfForm.IAM:
                os.chdir('Identity/Groups')
                command = 'python create_terraform_groups.py ' + input_cd3file + ' ' + input_outdir + ' ' + self.tfForm.Tenancy_Name + ' --configFileName ' + input_config_file
                os.system(command)
                os.chdir('../Policies')
                command = 'python create_terraform_policies.py ' + input_cd3file + ' ' + input_outdir + ' ' + self.tfForm.Tenancy_Name + ' --configFileName ' + input_config_file
                os.system(command)
                os.chdir("../..")

            if self.tfForm.Network:
                command = 'python create_all_tf_objects.py ' + input_cd3file + ' ' + input_outdir + ' ' + self.tfForm.Tenancy_Name + ' --configFileName ' + input_config_file
                os.chdir('CoreInfra/Networking/BaseNetwork')
                os.system(command)
                os.chdir("../../..")

            os.chdir('../media/' + user + '/documents/')
            shutil.make_archive(self.tfForm.Tenancy_Name, 'zip', self.tfForm.Tenancy_Name)

            if self.tfForm.RM:
                stackdetails = CreateStackDetails()
                zipConfigSource = CreateZipUploadConfigSourceDetails()
                config = oci.config.from_file(file_location=input_config_file)
                ocs_stack = oci.resource_manager.ResourceManagerClient(config)
                #stackdetails.compartment_id = self.tfForm.Tenancy_OCID
                stackdetails.compartment_id = "ocid1.compartment.oc1..aaaaaaaa7jbnffobhy5wkqqhqxxnepoh4z2ylwikr5rg4slidxzec7aijanq"
                stackdetails.description = "OCS CD3 Stack"
                stackdetails.terraform_version = "0.12.x"
                os.chdir(self.tfForm.Tenancy_Name)
                for reg in ct.all_regions:
                    stackdetails.display_name = self.tfForm.Stack_Name + "_" + reg
                    shutil.make_archive(reg, 'zip', reg)
                    with open(reg + ".zip", 'rb') as file:
                        zipContents = file.read()
                        encodedZip = base64.b64encode(zipContents).decode('ascii')
                    zipConfigSource.config_source_type = 'ZIP_UPLOAD'
                    zipConfigSource.zip_file_base64_encoded = encodedZip
                    stackdetails.config_source = zipConfigSource
                    mstack = ocs_stack.create_stack(create_stack_details=stackdetails)
                    stack_ocid = mstack.data.id
                    create_job_details = oci.resource_manager.models.CreateJobDetails()
                    createjoboperationdetails = oci.resource_manager.models.CreateJobOperationDetails()
                    createjoboperationdetails.operation = "PLAN"
                    create_job_details.display_name = self.tfForm.Tenancy_Name + "-" + reg + "-Plan"
                    create_job_details.job_operation_details = createjoboperationdetails
                    create_job_details.operation = "PLAN"
                    create_job_details.stack_id = stack_ocid
                    ocs_stack.create_job(create_job_details)
                os.chdir("..")
            path_to_file = os.path.join(os.getcwd(), self.tfForm.Tenancy_Name + ".zip")
            if os.path.exists(path_to_file):
                with open(path_to_file, 'rb') as fh:
                    response = HttpResponse(fh.read(), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename= %s' % self.tfForm.Tenancy_Name + ".zip"
            os.chdir("../../..")
        #except Exception as e:
         #   print(e)
            #return response
