import os
import sys
import oci
import base64
import shutil
import tempfile

from django.conf import settings
from django.http import HttpResponse

from .cd3cryto import Cd3Crypto

from SetUpOCI_Via_TF.commonTools import *
from oci.resource_manager.models import CreateStackDetails
from oci.resource_manager.models import CreateZipUploadConfigSourceDetails


# sys.path.insert(0, os.path.join(settings.BASE_DIR, 'SetUpOCI_Via_TF'))
# from commonTools import commonTools


def get_keyfile(private_key):
    temp_keyfile = tempfile.NamedTemporaryFile(mode='w+b', suffix=".pem", delete=False)
    try:
        temp_keyfile.write(private_key.encode('utf-8'))
        temp_keyfile.seek(0)
        # print(temp_keyfile.name)
        # print(temp_keyfile.read().decode('utf-8'))
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
        # print(temp_config.name)
        # print(temp_config.read())
        return temp_config
    except FileNotFoundError:
        print("File not created")


class GeneratorTF:
    def __init__(self, stack):
        self.stack = stack

    # def generate_config(self):
    #     cd3file = self.stack.CD3_Excel.read()
    #     decry = Cd3Crypto(self.stack)
    #     private_key = decry.decrypt_private_key()
    #     temp_keyfile = tempfile.NamedTemporaryFile(mode='w+b', suffix=".pem", delete=False)
    #     temp_config = tempfile.NamedTemporaryFile(mode='w+t', delete=False)
    #     try:
    #         temp_keyfile.write(private_key.encode('utf-8'))
    #         temp_keyfile.seek(0)
    #         # print(temp_keyfile.name)
    #         # print(temp_keyfile.read().decode('utf-8'))
    #         temp_str = "[DEFAULT]\ntenancy = " + self.stack.Tenancy_OCID + "\nfingerprint = " + \
    #                    self.stack.Fingerprint + "\nuser = " + self.stack.User_OCID + \
    #                    "\nkey_file = " + temp_keyfile.name + "\nregion = " + self.stack.Region
    #         temp_config.write(temp_str)
    #         temp_config.seek(0)
    #         print(temp_config.name)
    #         regions = RegionsList(temp_config, self.stack)
    #         regions.get_regions()
    #         print(temp_config.read())
    #     except FileNotFoundError:
    #         print("File not created")
    #     finally:
    #         temp_keyfile.close()

    def generate_tf(self):
        # try
        user = self.stack.Username.replace(' ', '_')
        cwd = os.getcwd()

        decry = Cd3Crypto(self.stack)
        private_key = decry.decrypt_private_key()

        input_key_file = get_keyfile(private_key)
        input_config_file = get_config(self.stack, input_key_file)

        cd3file = os.path.join(settings.MEDIA_ROOT, self.stack.CD3_Excel.name)
        out_dir = os.path.join(settings.MEDIA_ROOT, user, 'downloads', self.stack.Stack_Name)
        os.makedirs(out_dir, exist_ok=True)
        os.chdir(os.path.join(settings.MEDIA_ROOT, user))
        # os.makedirs("downloads", exist_ok=True)
        # out_dir = os.getcwd() + "/downloads/" + self.stack.Stack_Name
        os.chdir('..')
        # cd3file = os.getcwd() + "/" + str(self.stack.CD3_Excel)
        os.chdir('../SetUpOCI_Via_TF')
        ct = commonTools()
        # ct = sys.path.insert(0, os.path.join(settings.BASE_DIR, 'SetUpOCI_Via_TF')).commonTools.commonTools()
        ct.get_subscribedregions(input_config_file.name)
        os.chdir(os.path.join(settings.MEDIA_ROOT, user, 'downloads'))
        print(ct.all_regions)
        for reg in ct.all_regions:
            if not os.path.exists(out_dir + "/" + reg):
                os.makedirs(out_dir + "/" + reg)
                file = self.stack.Stack_Name + "/" + reg + "/provider.tf"
                oname = open(file, "w+")
                tempStr = "provider \"oci\" { " + "\n" + "  region = var.region" + "\n" + "}"
                oname.write(tempStr)
                oname.close()
                file = self.stack.Stack_Name + "/" + reg + "/variables_" + reg + ".tf"
                oname = open(file, "w+")
                tempStr = "variable \"tenancy_ocid\" { \n            type = string\n            default = \"" + self.stack.Tenancy_OCID + "\" \n}\nvariable \"region\" {\n            type = string\n            default = \"" + \
                          ct.region_dict[reg].strip() + "\"\n}"
                oname.write(tempStr)
                oname.close()

        os.chdir('../../../SetUpOCI_Via_TF')
        command = "python fetch_compartments_to_variablesTF.py " + out_dir + " --configFileName " + input_config_file.name
        print(command)
        exitVal = os.system(command)
        if (exitVal == 1) or (exitVal == 256):
            print("Error encountered. Please try again!!!")
            exit()

        if self.stack.IAM:
            os.chdir('Identity/Groups')
            command = 'python create_terraform_groups.py ' + cd3file + ' ' + out_dir + ' ' + self.stack.Tenancy_Name + ' --configFileName ' + input_config_file.name
            os.system(command)
            os.chdir('../Policies')
            command = 'python create_terraform_policies.py ' + cd3file + ' ' + out_dir + ' ' + self.stack.Tenancy_Name + ' --configFileName ' + input_config_file.name
            os.system(command)
            os.chdir("../..")

        if self.stack.Network:
            command = 'python create_all_tf_objects.py ' + cd3file + ' ' + out_dir + ' ' + self.stack.Tenancy_Name + ' --configFileName ' + input_config_file.name
            os.chdir('CoreInfra/Networking/BaseNetwork')
            os.system(command)
            os.chdir("../../..")

        os.chdir('../media/' + user + '/downloads/')
        shutil.make_archive(self.stack.Stack_Name, 'zip', self.stack.Stack_Name)

        if self.stack.RM:
            stackdetails = CreateStackDetails()
            zipConfigSource = CreateZipUploadConfigSourceDetails()
            config = oci.config.from_file(file_location=input_config_file)
            ocs_stack = oci.resource_manager.ResourceManagerClient(config)
            # stackdetails.compartment_id = self.tfForm.Tenancy_OCID
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
        # path_to_file = os.path.join(os.getcwd(), self.stack.Tenancy_Name + ".zip")
        # if os.path.exists(path_to_file):
        #     with open(path_to_file, 'rb') as fh:
        #         response = HttpResponse(fh.read(), content_type='application/zip')
        # response['Content-Disposition'] = 'attachment; filename= %s' % self.stack.Tenancy_Name + ".zip"
        os.chdir("../../..")
        # except Exception as e:
        #   print(e)
        # return response


# class RegionsList:
#     def __init__(self, config, stack):
#         self.config = config
#         self.stack = stack
#
#     def get_regions(self):
#         # print(self.config.read())
#         path = os.path.join(settings.BASE_DIR, 'SetUpOCI_Via_TF')
#
#         print("gong in")
#         # ct = commonTools.get_subscribedregions(self.stack, self.config.name)
#         ct = commonTools
#         ct().get_subscribedregions(input_config_file)
#         for reg in ct.all_regions:
#             if not os.path.exists(settings.MEDIA_ROOT + "/" + reg):
#                 os.makedirs(settings.MEDIA_ROOT + "/" + reg)
#                 file = self.stack.Tenancy_Name + "/" + reg + "/provider.tf"
#                 oname = open(file, "w+")
#                 tempStr = "provider \"oci\" { " + "\n" + "  region = var.region" + "\n" + "}"
#                 oname.write(tempStr)
#                 oname.close()
#                 file = self.stack.Tenancy_Name + "/" + reg + "/variables_" + reg + ".tf"
#                 oname = open(file, "w+")
#                 tempStr = "variable \"tenancy_ocid\" { \n            type = string\n            default = \"" \
#                           + self.stack.Tenancy_OCID + "\" \n}\nvariable \"region\" {\n            " \
#                                                       "type = string\n            default = \"" + \
#                           ct.region_dict[reg].strip() + "\"\n}"
#                 oname.write(tempStr)
#                 oname.close()
