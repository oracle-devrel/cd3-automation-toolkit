import time
import os
import sys
import oci
import base64
import shutil
import tempfile
import json
import ast
from django.conf import settings
sys.path.append(os.getcwd() + "/..")
from SetUpOCI_Via_TF.commonTools import *
#from SetUpOCI_Via_TF.OCSWorkVM.createOCSWork import create_compartment
from oci.resource_manager.models import CreateStackDetails
from oci.resource_manager.models import CreateZipUploadConfigSourceDetails
from oci.resource_manager.models import UpdateStackDetails
from oci.resource_manager.models import UpdateZipUploadConfigSourceDetails

def get_keyfile(private_key):
    temp_keyfile = tempfile.NamedTemporaryFile(mode='w+b', suffix=".pem", delete=False)
    try:
        temp_keyfile.write(private_key)
        temp_keyfile.seek(0)
        return temp_keyfile
    except FileNotFoundError:
        print("File not created")


def get_config(stack, temp_keyfile):
    temp_config = tempfile.NamedTemporaryFile(mode='w+t', suffix=".conf", delete=False)
    temp_str = "[DEFAULT]\ntenancy = " + stack.Tenancy_OCID + "\nfingerprint = " + \
               stack.Fingerprint + "\nuser = " + stack.User_OCID + \
               "\nkey_file = " + temp_keyfile.name + "\nregion = " + stack.Region
    try:
        temp_config.write(temp_str)
        temp_config.seek(0)
        return temp_config
    except FileNotFoundError:
        print("File not created")


class GeneratorTF:
    def __init__(self, stack, keyfile):
        self.stack = stack
        self.keyfile = keyfile.read()


    def generate_tf(self):
        #try:
            user = self.stack.Username.replace(' ', '_')
            cwd = os.getcwd()
            input_key_file = get_keyfile(self.keyfile)
            input_config_file = get_config(self.stack, input_key_file)
            cd3file = os.path.join(settings.MEDIA_ROOT, str(self.stack.CD3_Excel))
            out_dir = os.path.join(settings.MEDIA_ROOT,'users', user, 'downloads', self.stack.Stack_Name)

            os.chdir('../SetUpOCI_Via_TF')
            os.makedirs(out_dir, exist_ok=True)
            ct = commonTools()
            ct.get_subscribedregions(input_config_file.name)
            ct.get_network_compartment_ids(self.stack.Tenancy_OCID, "root", input_config_file.name)
            ct.all_regions = list(set(ct.all_regions))
            for reg in ct.all_regions:
                os.makedirs(out_dir + "/" + reg, exist_ok=True)
                file = os.path.join(out_dir, reg, 'provider.tf')
                file_name = open(file, "w+")
                temp_str = "provider \"oci\" { " + "\n" + "  region = var.region" + "\n" + "}"
                file_name.write(temp_str)
                file_name.close()
                temp_name = 'variables_' + reg + '.tf'
                file = os.path.join(out_dir, reg, temp_name)
                file_name = open(file, "w+")
                temp_str = "variable \"tenancy_ocid\" { \n            type = string\n            " \
                           "default = \"" + self.stack.Tenancy_OCID + "\" \n}\nvariable \"region\" " \
                           "{\n            type = string\n            default = \"" + \
                           ct.region_dict[reg].strip() + "\"\n}"
                if self.stack.Instance:
                    temp_str = temp_str + "\nvariable \"" + self.stack.Instance_SSH_Public_Key + "\" " \
                           "{\n            type = string\n            default = \"" + \
                           self.stack.Instance_SSH_Public_Value + "\"\n}"
                file_name.write(temp_str)
                file_name.close()


            if self.stack.Compartment:
                os.chdir('Identity/Compartments')
                command = 'python create_terraform_compartments.py ' + cd3file + ' ' + out_dir + ' ' + self.stack.Stack_Name + " --configFileName " + input_config_file.name
                os.system(command)
                os.chdir("../..")

            if not self.stack.Compartment:
                command = "python fetch_compartments_to_variablesTF.py " + out_dir + " --configFileName " + input_config_file.name
                exitVal = os.system(command)
                if (exitVal == 1) or (exitVal == 256):
                    print("Error encountered. Please try again!!!")
                    exit()

            if self.stack.Groups:
                os.chdir('Identity/Policies')
                command = 'python create_terraform_policies.py ' + cd3file + ' ' + out_dir + ' ' + self.stack.Stack_Name + ' --configFileName ' + input_config_file.name
                os.system(command)
                os.chdir('../Groups')
                command = 'python create_terraform_groups.py ' + cd3file + ' ' + out_dir + ' ' + self.stack.Stack_Name + ' --configFileName ' + input_config_file.name
                os.system(command)
                os.chdir("../..")

            if self.stack.Network:
                os.chdir('CoreInfra/Networking/BaseNetwork')
                if self.stack.Network == 'create_ntk':
                     command = 'python create_all_tf_objects.py ' + cd3file + ' ' + out_dir + ' ' + self.stack.Stack_Name + ' --configFileName ' + input_config_file.name
                     os.system(command)
                if self.stack.Network == 'modify_ntk':
                    command = 'python create_all_tf_objects.py ' + cd3file + ' ' + out_dir + ' ' + self.stack.Stack_Name + ' --configFileName ' + input_config_file.name + ' --modify_network true'
                    os.system(command)
                if self.stack.Network == 'export_secrt':
                    command1 = 'python exportSeclist.py ' + cd3file + ' --configFileName ' + input_config_file.name + " --networkCompartment \"" + self.stack.Export_Compartment_Name + "\""
                    command2 = 'python exportRoutetable.py ' + cd3file + ' --configFileName ' + input_config_file.name + " --networkCompartment \"" + self.stack.Export_Compartment_Name + "\""
                    os.system(command1)
                    os.system(command2)
                if self.stack.Network == 'modify_secrt':
                    command1 = 'python modify_secrules_tf.py ' + cd3file + ' ' + out_dir + ' ' + cd3file + ' --configFileName ' + input_config_file.name
                    command2 = 'python modify_routerules_tf.py ' + cd3file + ' ' + out_dir + ' --configFileName ' + input_config_file.name
                    os.system(command1)
                    os.system(command2)
                os.chdir("../../..")

            if self.stack.NSG:
                command = 'python create_terraform_nsg.py ' + cd3file + ' ' + out_dir + ' --configFileName ' + input_config_file.name
                os.chdir('CoreInfra/Networking/BaseNetwork')
                os.system(command)
                os.chdir("../../..")

            if self.stack.Instance:
                os.chdir('CoreInfra/Compute')
                command1 = 'python create_terraform_instances.py ' + cd3file + ' ' + out_dir + ' --configFileName ' + input_config_file.name
                command2 = 'python boot_backups_policy.py ' + cd3file + ' ' + out_dir + ' --configFileName ' + input_config_file.name
                os.system(command1)
                os.system(command2)
                os.chdir("../..")

            if self.stack.Block_Volume:
                os.chdir('CoreInfra/BlockVolume')
                command1 = 'python create_terraform_block_volumes.py ' + cd3file + ' ' + out_dir  + ' --configFileName ' + input_config_file.name
                command2 = 'python block_backups_policy.py ' + cd3file + ' ' + out_dir + ' --configFileName ' + input_config_file.name
                os.system(command1)
                os.system(command2)
                os.chdir("../..")


            if self.stack.RM:
                #stackdetails = CreateStackDetails()
                #zipConfigSource = CreateZipUploadConfigSourceDetails()
                config = oci.config.from_file(file_location=input_config_file.name)
                ocs_stack = oci.resource_manager.ResourceManagerClient(config)
                #stackdetails.description = "Created using CD3aaS"
                #stackdetails.terraform_version = "0.13.x"
                os.chdir(os.path.join(settings.MEDIA_ROOT, 'users', user, 'downloads', self.stack.Stack_Name))
                #print(ct.all_regions)
                temp = {}
                for reg in ct.all_regions:
                    zip_file = self.stack.Stack_Name + "/" + reg + '.zip'
                    zip_file_path = os.path.join(settings.MEDIA_ROOT, 'users', user, 'downloads', zip_file)
                    if os.path.exists(zip_file_path):
                        os.remove(zip_file_path)
                    shutil.make_archive(reg, 'zip', reg)


                    if not self.stack.Stack_Update:
                        print(self.stack.Stack_Update,"no" )
                        stackdetails = CreateStackDetails()
                        zipConfigSource = CreateZipUploadConfigSourceDetails()
                        stackdetails.description = "Created using CD3aaS"
                        stackdetails.terraform_version = "0.13.x"
                        #compartment_ocid = create_compartment(self.stack.Compartment_Name, "Created using CD3aaS")
                        stackdetails.compartment_id = ct.ntk_compartment_ids[self.stack.Compartment_Name]
                        stackdetails.display_name = "CD3aaS_" + self.stack.Stack_Name + "_" + reg
                        with open(reg + ".zip", 'rb') as file:
                            zipContents = file.read()
                            encodedZip = base64.b64encode(zipContents).decode('ascii')
                        zipConfigSource.config_source_type = 'ZIP_UPLOAD'
                        zipConfigSource.zip_file_base64_encoded = encodedZip
                        stackdetails.config_source = zipConfigSource
                        mstack = ocs_stack.create_stack(create_stack_details=stackdetails)
                        stack_ocid = mstack.data.id
                        temp[reg] = stack_ocid
                        self.stack.Stack_OCID = temp
                        print (temp,"no")

                    if self.stack.Stack_Update:
                        print(self.stack.Stack_Update,"yes")

                        updatestackdetails = UpdateStackDetails()
                        zipConfigSource = UpdateZipUploadConfigSourceDetails()
                        zipConfigSource.config_source_type = 'ZIP_UPLOAD'
                        updatestackdetails.display_name = "CD3aaS_" + self.stack.Stack_Name + "_" + reg
                        with open(reg + ".zip", 'rb') as file:
                            zipContents = file.read()
                            encodedZip = base64.b64encode(zipContents).decode('ascii')
                        zipConfigSource.config_source_type = 'ZIP_UPLOAD'
                        zipConfigSource.zip_file_base64_encoded = encodedZip
                        updatestackdetails.config_source = zipConfigSource
                        updatestackdetails.terraform_version = "0.13.x"
                        updatestackdetails.description = "Created using CD3aaS"
                        print (self.stack.Stack_OCID)
                        temp = self.stack.Stack_OCID
                        temp = ast.literal_eval(temp)
                        print(temp)
                        mstack = ocs_stack.update_stack(stack_id=temp[reg],update_stack_details=updatestackdetails)
                        stack_ocid = mstack.data.id
                        time.sleep(2)

                    create_job_details = oci.resource_manager.models.CreateJobDetails()
                    createjoboperationdetails = oci.resource_manager.models.CreateJobOperationDetails()
                    createjoboperationdetails.operation = "PLAN"
                    create_job_details.display_name = self.stack.Stack_Name + "-" + reg + "-Plan"
                    create_job_details.job_operation_details = createjoboperationdetails
                    create_job_details.operation = "PLAN"
                    # get_stack_response = oci.wait_until(ocs_stack, ocs_stack.get_stack(stack_ocid),'lifecycle_state', 'RUNNING')
                    create_job_details.stack_id = stack_ocid
                    ocs_stack.create_job(create_job_details)
                os.chdir("..")
                    # stackdetails.display_name = "CD3aaS_" + self.stack.Stack_Name + "_" + reg
                    # shutil.make_archive(reg, 'zip', reg)
                    # with open(reg + ".zip", 'rb') as file:
                    #     zipContents = file.read()
                    #     encodedZip = base64.b64encode(zipContents).decode('ascii')
                    # zipConfigSource.config_source_type = 'ZIP_UPLOAD'
                    # zipConfigSource.zip_file_base64_encoded = encodedZip
                    # stackdetails.config_source = zipConfigSource
                        # request = UpdateStackDetails()
                        # request.compartment_id = ct.ntk_compartment_ids[self.stack.Compartment_Name]
                        # # request.display_name = stack_name
                        # # request.description = "OCS CD3 Stack"
                        # request.config_source = zipConfigSource
                        # #request.terraform_version = "0.12.x"
                        # ocs_stack.update_stack(stack_id=stack_ocid, update_stack_details=request)
                    #shutil.rmtree(reg, 'zip', reg)
                #os.chdir("..")


            zip_file = self.stack.Stack_Name + '.zip'
            zip_file_path = os.path.join(settings.MEDIA_ROOT, 'users', user, 'downloads', zip_file)
            if os.path.exists(zip_file_path):
                os.remove(zip_file_path)
            shutil.make_archive(out_dir, 'zip', out_dir)
            self.stack.Terraform_Files = '/users/' +user + '/downloads/' + zip_file
            os.chdir(cwd)
       # except Exception as e:
        #    print(e)
    #finally:
        #os.chdir(cwd)
