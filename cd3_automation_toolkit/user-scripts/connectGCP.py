import argparse
import configparser
import datetime
import shutil
import distutils
import os,sys,logging
sys.path.append(os.getcwd()+"/../gcp/python/")
from gcpCommonTools import *



# Execution of code begins here
parser = argparse.ArgumentParser(description="Connects the Container to GCP Tenant")
parser.add_argument("propsfile", help="Full Path of properties file. eg connectGCP.properties")
args = parser.parse_args()
config = configparser.RawConfigParser()
config.read(args.propsfile)

current_time=str(datetime.datetime.now())

# Initialize Toolkit Variables
user_dir = "/cd3user/cloud_accounts/gcp"
user_dir = "/Users/susingla/PyCharmProjects/orahub-develop/cd3user/cloud_accounts/gcp"
auto_keys_dir = user_dir + "/keys"
toolkit_dir = os.path.dirname(os.path.abspath(__file__))+"/.."
tf_modules_dir = toolkit_dir + "/gcp/terraform"
variables_example_file = tf_modules_dir + "/variables_example.tf"
setupcloud_props_toolkit_file_path = toolkit_dir + "/user-scripts/setUpCloud.properties"

cloud="GCP"

prefix = config.get('Default', 'prefix').strip()
if prefix == "" or prefix == "\n":
    print("Invalid Prefix. Please try again......Exiting !!")
    exit(1)

prefixes=[]
f = os.path.basename(__file__).rstrip("py")+".safe"
safe_file = user_dir + f
if os.path.exists(safe_file):
    f=open(safe_file,"r")
    safe_file_lines = f.readlines()
    for l in safe_file_lines:
        if "SUCCESS" in l:
            prefixes.append(l.split("\t")[0])

if prefixes !=[]:
    if prefix in prefixes:
        print("WARNING!!! Container has already been successfuly connected to the GCP with same prefix. Please proceed only if you re-running the script for new project subscription")
        inp = input("\nDo you want to proceed (y/n):")
        if inp.lower()=="n":
            exit(1)

# Initialize Tenancy Variables
prefix_dir = user_dir +"/" + prefix
config_files= prefix_dir +"/.config_files"

terraform_files = prefix_dir + "/terraform_files/"
outdir_safe=terraform_files+"/.safe"
setupcloud_props_file_path = prefix_dir + "/"+prefix+"_setUpCloud.properties"

# Read Config file Variables
try:
    organization_id=''
    config_file=''

    organization_id = config.get('Default', 'organization_id').strip()
    if organization_id == "" or organization_id == "\n":
        print("organization_id cannot be left empty...Exiting !!")
        exit(1)

    config_file = config.get('Default', 'config_file').strip()
    if config_file == "" or config_file == "\n":
        config_file = auto_keys_dir +"/gcp_api_private.json"

    if not os.path.isfile(config_file):
        print("Invalid JSON Key File at " + config_file + ". Please try again......Exiting !!")
        exit(1)


    outdir_structure_file = config.get('Default', 'outdir_structure_file').strip()
    ssh_public_key = config.get('Default', 'ssh_public_key').strip()

except Exception as e:
    print(e)
    print('Check if input properties exist and try again..exiting...')
    exit(1)


if not os.path.exists(prefix_dir):
    os.makedirs(prefix_dir)
if not os.path.exists(config_files):
    os.makedirs(config_files)
if not os.path.exists(outdir_safe):
    os.makedirs(outdir_safe)

# Copy input properties file to customer_tenancy_dir
shutil.copy(args.propsfile,config_files+"/"+prefix+"_"+os.path.basename(args.propsfile))

# 1. Copy outdir_structure_file and config file
# Copy default outdir_structure_file
shutil.copy(toolkit_dir+'/user-scripts/outdir_structure_file.properties', toolkit_dir+'/user-scripts/.outdir_structure_file.properties')

_outdir_structure_file = ''
dir_values = []
if (outdir_structure_file != '' and outdir_structure_file != "\n"):
    if not os.path.isfile(outdir_structure_file):
        print("Invalid outdir_structure_file. Please provide correct file path......Exiting !!")
        exit(1)
    else:
        outdir_config = configparser.RawConfigParser()
        outdir_config.read(outdir_structure_file)
        for key, value in outdir_config.items("Default"):
            if value == '':
                print("Out Directory is missing for one or more parameters, for eg. " + key)
                print("Please check " + outdir_structure_file)
                exit(1)
            if value not in dir_values:
                dir_values.append(str(value))

        _outdir_structure_file = prefix_dir+ "/"+prefix+"_outdir_structure_file.properties"
        #if not os.path.exists(_outdir_structure_file):
        shutil.copyfile(outdir_structure_file, _outdir_structure_file)
    print("\nUsing different directories for GCP services as per the input outdir_structure_file..........")
else:
    print("\nUsing single out directory for resources..........")

filename = os.path.basename(config_file)
_config_file=config_files + "/" + filename
shutil.copy(config_file, _config_file)
os.chmod(_config_file,0o600)


# 2. Authenticate and Get Projects
gct = gcpCommonTools()
credentials = gct.authenticate(config_file)
gct.get_organization_projects(organization_id,credentials)

# 3. Generate setUpCloud.properties file
print("Creating GCP specific setUpCloud.properties.................")
with open(setupcloud_props_toolkit_file_path, 'r+') as setUpCloud_file:
    setupcloud_props_toolkit_file_data = setUpCloud_file.read().rstrip()

setupcloud_props_toolkit_file_data = setupcloud_props_toolkit_file_data.replace("outdir=", "outdir="+terraform_files)
setupcloud_props_toolkit_file_data = setupcloud_props_toolkit_file_data.replace("prefix=", "prefix="+prefix)
setupcloud_props_toolkit_file_data = setupcloud_props_toolkit_file_data.replace("organization_id=", "organization_id=" + organization_id)
setupcloud_props_toolkit_file_data = setupcloud_props_toolkit_file_data.replace("config_file=", "config_file="+_config_file)
setupcloud_props_toolkit_file_data = setupcloud_props_toolkit_file_data.replace("outdir_structure_file=", "outdir_structure_file="+_outdir_structure_file)

f = open(setupcloud_props_file_path, "w+")
f.write(setupcloud_props_toolkit_file_data)
f.close()

# 4.Create the TF related files for each project
if not os.path.exists(terraform_files):
    os.makedirs(terraform_files)


print("Creating GCP specific project directories, terraform provider , variables files.................")
#regions_file_data = ""

# 5. Read variables.tf from examples folder and copy the variables as string
for id,name in gct.projects.items():
    project=id

    with open(variables_example_file, 'r+') as var_eg_file:
        variables_example_file_data = var_eg_file.read().rstrip()

    variables_example_file_data = variables_example_file_data.replace("<PATH TO JSON KEY FILE>", _config_file)
    variables_example_file_data = variables_example_file_data.replace("<PROJECT ID HERE>", project)

    # Rerunning script for any new project subscription. Process only new prohect directories else continue
    if os.path.exists(terraform_files + project):
        continue

    os.mkdir(terraform_files + project)
    f = open(terraform_files + "/" + project + "/variables_" + project + ".tf", "w+")
    f.write(variables_example_file_data)
    f.close()

    # 6. Copy terraform modules and variables file to outdir
    distutils.dir_util.copy_tree(tf_modules_dir, terraform_files + "/" + project)

    # Manage single and multiple outdir
    if (outdir_structure_file == '' or outdir_structure_file == "\n"):
        # remove depends_on for single outdir
        project_dir = terraform_files + "/" + project + "/"
        single_outdir_config = configparser.RawConfigParser()
        outdir_config_file = os.path.dirname(os.path.abspath(__file__)) + "/.outdir_structure_file.properties"

        single_outdir_config.read(outdir_config_file)
        keys = []
        for key, val in single_outdir_config.items("Default"):
            keys.append(key)
        for file in os.listdir(project_dir):
            # name=file.removesuffix(".tf")
            name = file[:-len(".tf")]
            if name in keys:
                file = project_dir + "/" + file
                with open(file, 'r+') as tf_file:
                    module_data = tf_file.read().rstrip()
                    module_data = module_data.replace("# depends_on", "depends_on")
                tf_file.close()
                f = open(file, "w+")
                f.write(module_data)
                f.close()
    else:
        project_dir = terraform_files + "/" + project + "/"
        for service, service_dir in outdir_config.items("Default"):
            service = service.strip().lower()
            service_dir = service_dir.strip()

            # Keep the .tf file in default region directory if directory name is empty
            if service_dir == "" or service_dir == "\n" or service!='instance':
                continue

            project_service_dir=project_dir+service_dir
            if not os.path.exists(project_service_dir):
                os.mkdir(project_service_dir)

            if (service == 'instance'):
                if (os.path.isdir(project_service_dir + '/scripts')):
                    shutil.rmtree(project_service_dir + '/scripts')
                if (os.path.exists(project_dir + 'scripts')):
                    shutil.move(project_dir + 'scripts', project_service_dir + '/')
                with open(project_dir + service + ".tf", 'r+') as tf_file:
                    module_data = tf_file.read().rstrip()
                    module_data = module_data.replace("\"./modules", "\"../modules")

                f = open(project_service_dir + "/" + service + ".tf", "w+")
                f.write(module_data)
                f.close()
                os.remove(project_dir + service + ".tf")

                shutil.copyfile(project_dir + "variables_" + project + ".tf",
                                project_service_dir + "/" + "variables_" + project + ".tf")
                shutil.copyfile(project_dir + "provider.tf", project_service_dir + "/" + "provider.tf")


        os.remove(terraform_files + "/" + project + "/" + "variables_" + project + ".tf")
        os.remove(terraform_files + "/" + project + "/" + "provider.tf")

    # 8. Remove terraform example variable file from outdir
    os.remove(terraform_files + "/" + project + "/variables_example.tf")


# Logging information
f = os.path.basename(__file__).rstrip("py")+".out"
outfile = prefix_dir + "/"+ f
logging.basicConfig(filename=outfile, format='%(message)s', filemode='w', level=logging.INFO)

print("==================================================================================================================================")
print("\nThe toolkit has been setup successfully. !!!\n")
f = open(safe_file, "a")
data="GCP\t"+prefix + "\t" + "SUCCESS\t"+current_time+"\n"
f.write(data)
f.close()

logging.info("Tenant Specific Working Directory Path: "+prefix_dir+"\n")

logging.info("\n######################################")
logging.info("Next Steps for using toolkit via CLI")
logging.info("######################################")
logging.info("Modify "+prefix_dir + "/" +prefix+"_setUpGCP.properties with input values for cd3file and workflow_type")
logging.info("cd "+os.path.dirname(os.path.abspath(__file__)))
logging.info("python setUpGCP.py "+setupcloud_props_file_path)

with open(outfile, 'r') as log_file:
    data = log_file.read().rstrip()
print(data)

print("==================================================================================================================================")












