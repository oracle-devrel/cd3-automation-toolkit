#!/usr/bin/python3

import sys
from pathlib import Path
import os
import argparse
import logging
import shutil
import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from awscloud.python.awsCommonTools import awsCommonTools, read_aws_auth_properties

def create_region_terraform_files(regions, terraform_root, aws_access_key_id, aws_secret_access_key):

    for region in regions:

        region_dir = os.path.join(terraform_root, region)
        os.makedirs(region_dir, exist_ok=True)

        provider_src = os.path.join(tf_modules_dir, "provider.tf")
        provider_dest = os.path.join(region_dir, "provider.tf")
        shutil.copy(provider_src, provider_dest)

        # Read variables template
        variables_template = os.path.join(tf_modules_dir, "variables_example.tf")

        with open(variables_template, "r") as f:
            variable_data = f.read()

        # Replace placeholders in variables
        variable_data = variable_data.replace("<AWS_REGION>", region)
        variable_data = variable_data.replace("<AWS_ACCESS_KEY>", aws_access_key_id)
        variable_data = variable_data.replace("<AWS_SECRET_KEY>", aws_secret_access_key)

        variable_file = os.path.join(region_dir, f"variable_{region}.tf")

        with open(variable_file, "w") as f:
            f.write(variable_data)


parser = argparse.ArgumentParser(description="Connects Container to AWS")
parser.add_argument("propsfile", help="Path to properties file")
args = parser.parse_args()


current_time = str(datetime.datetime.now())
cloud = "AWS"

# Initialize Toolkit Variables
user_dir = "/cd3user/"+cloud.lower()+"/"
toolkit_dir = os.path.dirname(os.path.abspath(__file__)) + "/.."
tf_modules_dir = toolkit_dir + "/awscloud/terraform"

setupcloud_props_toolkit_file_path = toolkit_dir + "/setUpAWS.properties"

# Read prefix
prefix = None

with open(args.propsfile, "r") as f:
    for line in f:
        if line.strip().startswith("prefix"):
            prefix = line.split("=")[1].strip()

if not prefix:
    print("Invalid Prefix. Please try again......Exiting !!")
    exit(1)

# Prefix safety check
prefixes = []
f = os.path.basename(__file__).rstrip("py") + "safe"
safe_file = user_dir + f

if os.path.exists(safe_file):

    f = open(safe_file, "r")
    safe_file_lines = f.readlines()

    for l in safe_file_lines:
        if "SUCCESS" in l:
            prefixes.append(l.split("\t")[0])


if prefixes != []:
    if prefix in prefixes:

        print("WARNING!!! Container has already been successfully connected to AWS with same prefix.")
        print("Please proceed only if you are re-running the script for new project subscription")

        inp = input("\nDo you want to proceed (y/n):")

        if inp.lower() == "n":
            exit(1)

# Directory structure
prefix_dir = user_dir + "/" + prefix
config_files = prefix_dir + "/.config_files"
terraform_files = prefix_dir + "/terraform_files"

setupcloud_props_file_path = prefix_dir + "/" + prefix + "_setUpAWS.properties"


os.makedirs(prefix_dir, exist_ok=True)
os.makedirs(config_files, exist_ok=True)
os.makedirs(terraform_files, exist_ok=True)

shutil.copy(args.propsfile, config_files + "/" + prefix + "_connectAWS.properties")


# Read AWS Credentials
aws_access_key_id, aws_secret_access_key = read_aws_auth_properties(args.propsfile)

auth = awsCommonTools()

session = auth.authenticate(args.propsfile)

ec2 = session.client("ec2")

response = ec2.describe_regions()
#print(response["Regions"])
regions = [r["RegionName"] for r in response["Regions"]]

# Copy Terraform modules
modules_src = os.path.join(tf_modules_dir, "modules")
modules_dest = os.path.join(terraform_files, "modules")

if os.path.exists(modules_src):

    if not os.path.exists(modules_dest):
        shutil.copytree(modules_src, modules_dest)

# Create region Terraform files
print("terraform_files", terraform_files)

create_region_terraform_files(regions,terraform_files,aws_access_key_id,aws_secret_access_key)

# Generate setUpAWS.properties
print("Creating setUpAWS.properties")
with open(setupcloud_props_toolkit_file_path, 'r') as f:
    data = f.read()

data = data.replace("outdir=", "outdir=" + terraform_files)
data = data.replace("prefix=", "prefix=" + prefix)
data = data.replace("aws_access_key_id=", "aws_access_key_id=" + aws_access_key_id)
data = data.replace("aws_secret_access_key=", "aws_secret_access_key=" + aws_secret_access_key)

with open(setupcloud_props_file_path, "w") as f:
    f.write(data)

# Logging setup

outfile = prefix_dir + '/' + os.path.basename(__file__).rstrip("py") + "out"
print(outfile)
logging.basicConfig(filename=outfile, format='%(message)s', filemode='w', level=logging.INFO)

print("==================================================================================================================================")
print("\nThe toolkit has been setup successfully. !!!\n")

# Write success entry
f = open(safe_file, "a")
data = prefix + "\t" + "SUCCESS\t" + current_time + "\n"
f.write(data)
f.close()

# Logging

logging.info("Prefix Specific Working Directory Path: " + prefix_dir + "\n")

logging.info("\n######################################")
logging.info("Next Steps for using toolkit via CLI")
logging.info("######################################")

logging.info("Modify " + prefix_dir + "/" + prefix + "_setUpAWS.properties with input values for cd3file and workflow_type")
logging.info("cd /cd3user/oci_tools/cd3_automation_toolkit")
logging.info("python setUpCloud.py aws " + prefix_dir + "/" + prefix + "_setUpAWS.properties")

# Print logfile contents
with open(outfile, 'r') as log_file:
    data = log_file.read().rstrip()

print("\nToolkit setup completed successfully")
print(data)

print("===================================================================")