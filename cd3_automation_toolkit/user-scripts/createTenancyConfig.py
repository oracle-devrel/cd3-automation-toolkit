#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will help in initilizing the docker container; creates config and variables files.
#
# Author: Shruthi Subramanian
#

import glob
import argparse
import logging
import os
import sys
import time
import configparser
import distutils
from distutils import dir_util

sys.path.append(os.getcwd()+"/..")
from commonTools import *

def paginate(operation, *args, **kwargs):
    while True:
        response = operation(*args, **kwargs)
        for value in response.data:
            yield value
        kwargs["page"] = response.next_page
        if not response.has_next_page:
            break

def seek_info():

    parser = argparse.ArgumentParser(description="Creates OCS Work related components")
    parser.add_argument("propsfile", help="Full Path of properties file. eg tenancyconfig.properties")
    args = parser.parse_args()
    config = configparser.RawConfigParser()
    config.read(args.propsfile)

    # 1. Creation of Config File -
    print("=================================================================")
    print("NOTE: Make sure the API Public Key is added to the OCI Console!!!")
    print("=================================================================")

    # Read Config file Variables
    try:
        tenancy = config.get('Default', 'tenancy_ocid').strip()
        if tenancy == "" or tenancy == "\n":
            print("Invalid Tenancy ID. Please try again......Exiting !!")
            exit(1)

        fingerprint = config.get('Default', 'fingerprint').strip()
        if fingerprint == "" or fingerprint == "\n":
            print("Invalid Fingerprint. Please try again......Exiting !!")
            exit(1)

        user = config.get('Default', 'user_ocid').strip()
        if user == "" or user == "\n":
            print("Invalid User ID. Please try again......Exiting !!")
            exit(1)

        prefix = config.get('Default', 'customer_name').strip()
        if prefix == "" or prefix == "\n":
           print("Invalid Prefix. Please try again......Exiting !!")
           exit(1)

        key_path = config.get('Default', 'key_path').strip()

        region = config.get('Default', 'region').strip()
        if (region == '' or key_path == "\n"):
            region = "us-ashburn-1"

        ssh_public_key = config.get('Default', 'ssh_public_key').strip()

    except Exception as e:
        print(e)
        print('Check if input properties exist and try again..exiting...`    ')
        exit()

    # Variables Initialization
    user_dir = "/"+"cd3user"
    customer_tenancy_dir = user_dir +"/tenancies/" + prefix
    terraform_files = customer_tenancy_dir+"/terraform_files/"
    config_file_path = customer_tenancy_dir+"/"+prefix+"_config"
    auto_keys_dir = user_dir+"/tenancies/keys"
    modules_dir = user_dir +"/oci_tools/cd3_automation_toolkit/user-scripts/terraform"
    documentation_dir = user_dir +"/oci_tools/cd3_automation_toolkit/documentation"
    variables_example_file = modules_dir +"/variables_example.tf"
    setupoci_props_file_path = customer_tenancy_dir + "/" + prefix + "_setUpOCI.properties"

    if not os.path.exists(customer_tenancy_dir):
        os.makedirs(customer_tenancy_dir)

    # 1. Move the newly created PEM keys to /cd3user/tenancies/<customer_name>/
    files = glob.glob(auto_keys_dir+"/*")

    # If the private key is empty or if the private key is already present in the tenancy folder; initialize it to the default path;
    if (key_path == '' or key_path == "\n"):
        print("key_path field is empty in tenancyconfig.properties. Defaulting to " + user_dir + "/tenancies/keys/oci_api_private.pem")
        if os.path.exists(auto_keys_dir):
            print("Copying the key files to " + customer_tenancy_dir)
            if files:
                for f in files:
                    if os.path.exists(f):
                        filename = f.split('/')[-1]
                        if os.path.exists(customer_tenancy_dir + "/" + filename):
                            shutil.move(customer_tenancy_dir + "/" + filename,
                                        customer_tenancy_dir + "/" + filename + "_backup")
                        shutil.copyfile(f, customer_tenancy_dir + "/" + filename)
                        key_path = customer_tenancy_dir + "/oci_api_private.pem"
                    else:
                        print("Key files not found. Please make sure to specify the right path in the properties file.....Exiting!!!")
                        exit(0)
        else:
            print("Directory - "+auto_keys_dir+" does not exist. Please make sure to specify the right path in the properties file.....Exiting!!!")
            exit(0)
        shutil.move(auto_keys_dir, auto_keys_dir + "_backup_" + time.strftime("%H%M%S"))

    # If the key - oci_api_private.pem is already present in the tenancy folder
    elif customer_tenancy_dir + '/oci_api_private.pem' in key_path:
        key_path = customer_tenancy_dir + "/oci_api_private.pem"

    # If the private key is elsewhere; move it to the tenancy folder
    elif auto_keys_dir + "/oci_api_private.pem" not in key_path:
        try:
            shutil.move(key_path, customer_tenancy_dir + '/oci_api_private.pem')
        except FileNotFoundError as e:
            print(
                "Key file not found. Please make sure to specify the right path in the properties file.....Exiting!!!")
            exit(0)
        key_path = customer_tenancy_dir + "/oci_api_private.pem"
    else:
        print("\n")
        print("=================================================================")
        print("\"keys\" directory NOT FOUND in " + user_dir + "/tenancies/" + ". \n"
             "Please generate the keys using the command \"python createAPIKey.py\" \n(OR)\nIf the keys already exist:\n- Create a folder named \"keys\" in " + user_dir + "/tenancies/" + "\n- Place the keys with names oci_api_public.pem and oci_api_private.pem respectively\n!! Try Again !!")
        print("=================================================================")
        exit(0)


    if not os.path.exists(terraform_files):
        os.makedirs(terraform_files)

    # 2. Create config file
    print("Creating the Tenancy specific config, terraform provider , variables and properties files.................")
    file = open(config_file_path, "w")
    file.write("[DEFAULT]\n"
               "tenancy = "+tenancy+"\n"
               "fingerprint = "+fingerprint+"\n"
               "user = "+user+"\n"
               "key_file = "+key_path+"\n"
               "region = "+region+"\n")
    file.close()

    # Fetch OCI_regions
    cd3service = cd3Services()
    cd3service.fetch_regions(configFileName=config_file_path)

    # 3. Fetch AD Names -
    print('Fetching AD names from tenancy and writing to config file if it does not exist.............')
    try:
        python_config = oci.config.from_file(file_location=config_file_path)
    except oci.exceptions.InvalidKeyFilePath as e:
        print("\nInvalid key_file path. Please make sure to specify the right path in the properties file.....Exiting!!!")
        exit(0)
    identity_client = oci.identity.IdentityClient(python_config)
    conf_file = open(config_file_path, "a")
    tenancy_id = tenancy
    i = 1
    for ad in paginate(identity_client.list_availability_domains, compartment_id=tenancy_id):
        ad_name = "ad_" + str(i)
        if not ad_name in python_config:
            conf_file.write("ad_" + str(i) + "=" + ad.name + "\n")
        i = i + 1
    conf_file.close()

    ct = commonTools()
    # 4. Generate setUpOCI.properties file
    ct.get_subscribedregions(config_file_path)

    setupoci_props_file = open(setupoci_props_file_path, "w")
    setupoci_props_file.write("[Default]\n"
                              "\n"
                              "#Input variables required to run setUpOCI script\n"
                              "\n"
                              "#path to output directory where terraform file will be generated. eg /cd3user/tenancies/<customer_tenancy_name>/terraform_files when running from OCS VM\n"
                              "outdir="+terraform_files+"\n"
                              "\n"
                              "#prefix for output terraform files eg client name\n"
                              "prefix="+prefix+"\n"
                              "\n"
                              "#input config file for Python API communication with OCI eg example\config; Leave it blank if code is being executed from OCS Work VM\n"
                              "config_file="+config_file_path+"\n"
                              "\n"
                              "#params required if input data format is cd3\n"
                              "#path to cd3 excel eg example\CD3-Flat-template.xlsx\n"
                              "cd3file=\n"
                              "\n"
                              "#Is it Non GreenField tenancy\n"
                              "non_gf_tenancy=false \n""")
    setupoci_props_file.close()

    # 5. Fetch Subscribed regions and create the TF related files
    for region in ct.all_regions:
        linux_image_id = ''
        windows_image_id = ''

        new_config = python_config
        new_config.__setitem__("region", ct.region_dict[region])
        cc = oci.core.ComputeClient(new_config)

        # fetch latest image ocids
        try:
            for image in paginate(cc.list_images, compartment_id=tenancy_id, operating_system='Oracle Linux',
                                  sort_by='TIMECREATED'):
                if ("Gen2-GPU" not in image.display_name):
                    linux_image_id = image.id
                    break
            for image in paginate(cc.list_images, compartment_id=tenancy_id, operating_system='Windows',
                                  sort_by='TIMECREATED'):
                if ("Gen2-GPU" not in image.display_name):
                    windows_image_id= image.id
                    break
        except:
            print("!!! Authorization failed !!! Cannot fetch the list of images available for Windows and Oracle Linux to write to variables.tf file !!!\n"
                  "Please make sure to have Read Access to the Tenancy at the minimum and try again !!!")
            print("Exiting........!!!")
            exit()

        if not os.path.exists(terraform_files+region):
            os.mkdir(terraform_files+region)

        # 6. Read variables.tf from examples folder and copy the variables as string
        with open(variables_example_file, 'r+') as var_eg_file:
            variables_example_file_data = var_eg_file.read().rstrip()

        variables_example_file_data = variables_example_file_data.replace("<TENANCY OCID HERE>", tenancy)
        variables_example_file_data = variables_example_file_data.replace("<USER OCID HERE>", user)
        variables_example_file_data = variables_example_file_data.replace("<SSH KEY FINGERPRINT HERE>", fingerprint)
        variables_example_file_data = variables_example_file_data.replace("<SSH PRIVATE KEY FULL PATH HERE>", key_path)
        variables_example_file_data = variables_example_file_data.replace("<OCI TENANCY REGION HERE eg: us-phoenix-1 or us-ashburn-1>", ct.region_dict[region])
        variables_example_file_data = variables_example_file_data.replace("<SSH PUB KEY STRING HERE>", ssh_public_key)
        if (windows_image_id != ''):
            variables_example_file_data = variables_example_file_data.replace("<LATEST WINDOWS OCID HERE>", windows_image_id)

        if (linux_image_id != ''):
            variables_example_file_data = variables_example_file_data.replace("<LATEST LINUX OCID HERE>", linux_image_id)

        f = open(terraform_files+"/"+region+"/variables_" + region + ".tf", "w+")
        f.write(variables_example_file_data)
        f.close()

        # 7. Copy the terraform modules and variables file to outdir
        distutils.dir_util.copy_tree(modules_dir, terraform_files +"/" + region)

        # 8. Remove the terraform example variable file from outdir
        os.remove(terraform_files +"/" + region + "/variables_example.tf")

        # 9. Copy documentation folder to outdir
        distutils.dir_util.copy_tree(documentation_dir+"/", customer_tenancy_dir+"/documentation")

    # Logging information
    logging.basicConfig(filename=customer_tenancy_dir+'/cmds.log', format='%(message)s', filemode='w', level=logging.INFO)

    print("==================================================================================================================================")
    print("\nThe toolkit has been setup to execute API's successfully. !!!")
    print("Working Directory Path: "+customer_tenancy_dir)
    print("Config File Path: "+ config_file_path )
    print("Path to region based directories, terraform provider and the variables files: " + terraform_files)
    print("\nPlease use "+prefix+"_setUpOCI.properties file at "+customer_tenancy_dir +" to proceed with the execution of the SetUpOCI script !!!!")
    print("Update the path of CD3 Excel input file in "+customer_tenancy_dir + "/" +prefix+"_setUpOCI.properties before executing the next command......")
    print("\nCommands to execute: (Alternately, you may also check the cmds.log in outdir for the same information)")
    logging.info("Commands to execute:")
    print("cd "+user_dir+"/oci_tools/cd3_automation_toolkit/")
    logging.info("cd "+user_dir+"/oci_tools/cd3_automation_toolkit/")
    print("python setUpOCI.py "+customer_tenancy_dir + "/" +prefix+"_setUpOCI.properties")
    logging.info("python setUpOCI.py "+customer_tenancy_dir + "/" +prefix+"_setUpOCI.properties")
    print("==================================================================================================================================")

if __name__ == '__main__':

    # Execution of the code begins here
    seek_info()
