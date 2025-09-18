import argparse
import configparser
from collections import namedtuple
import datetime,os
import sys
sys.path.append(os.getcwd())
sys.path.append(os.getcwd()+"/..")
from azurecloud.python import *
from common.python import *


def match_options(options, prim_options):
    print("match_options")
    user_input = ""
    # Iterate over options. Print number and option
    for i, option in enumerate(options, 1):
        if option.name in prim_options:
            user_input += "," + str(i)
    user_input = user_input.split(',')[1:]
    try:
        return [options[int(choice) - 1] for choice in user_input]
    except IndexError as ie:
        print("\nInvalid Option.....Exiting!!")
        exit(1)


def show_options(options, quit=False, menu=False, extra=None, index=0):
    # Just add whitespace between number and option. It just makes it look better
    number_offset = len(str(len(options))) + 1
    # Iterate over options. Print number and option
    for i, option in enumerate(options, index):
        print(f'{str(i)+".":<{number_offset}} {option.name}')
    if quit:
        print(f'{"q"+".":<{number_offset}} Press q to quit')
    if menu:
        print(f'{"m"+".":<{number_offset}} Press m to go back to Main Menu')
    if extra:
        print(extra)
    user_input = input('Enter your choice (specify comma separated to choose multiple choices): ')
    user_input = user_input.split(',')
    if 'q' in user_input or 'm' in user_input:
        return user_input
    # Subtract one to account for zero-indexing. The options start at 1
    # #return [options[int(choice)-1] for choice in user_input]

    try:
        for choice in user_input:
            if int(choice) - index < 0:
                print("\nInvalid Option.....Exiting!!")
                exit(1)
            elif options[int(choice) - index].name == "Execute All":
                options.pop(0)
                return options
    except ValueError as ie:
        print("\nInvalid Input.....Try again!!\n")
        options = show_options(inputs, quit=True, index=index)
        return options

    try:
        return [options[int(choice)-index] for choice in user_input]
    except IndexError as ie:
        print("\nInvalid Option.....Exiting!!")
        exit(1)
    except ValueError as ie:
        print("\nInvalid Input.....Try again!!\n")
        options = show_options(inputs, quit=True, index=index)
        return options

def execute_options(options, *args, **kwargs):
    global menu, quit
    if 'm' in options or 'q' in options:
        menu = 'm' in options
        quit = 'q' in options
    else:
        for option in options:
            if option.name == "Execute All":
                continue
            else:
                with section(option.text):
                    option.callback(*args, **kwargs)


def create_adb_azure():
    create_terraform_adb_azure(inputfile, outdir, prefix)

def create_exa_azure():
    create_terraform_exa_infra_azure(inputfile, outdir, prefix)
    create_terraform_exa_vmclusters_azure(inputfile, outdir, prefix)


def create_db_at_azure(execute_all=False):
    options = [
        Option('Add/Modify/Delete ADB @Azure', create_adb_azure, 'Processing ADB-Azure Tab'),
        Option('Add/Modify/Delete Exa @Azure', create_exa_azure, 'Processing Exa-Azure Tabs')
        # Option('Enable LBaaS Logs', enable_lb_logs, 'LBaaS Logs')
    ]
    options = show_options(options, quit=True, menu=True, index=1)
    if not execute_all:
        execute_options(options)

'''
def export_az_adb():
    export_az_oci_adb(inputfile, outdir, credentials)
'''
def export_az_oci_exa():
    export_az_oci_adb(inputfile, outdir, credentials)

def export_db_at_azure(execute_all=False):
    options = [
        Option('Export ADB @Azure', export_adb_azure, 'Exporting ADB-Azure'),
        # Option('Export Exa @Azure', export_az_oci_exa, 'Processing Exa-Azure')
    ]
    options = show_options(options, quit=True, menu=True, index=1)
    if not execute_all:
        execute_options(options,inputfile, outdir, credentials)

    create_terraform_adb_azure(inputfile, outdir, prefix)


#Execution starts here
global devops
global updated_paths
global import_scripts
updated_paths = []
import_scripts = []
# Opt-in to IMDS lookup
exec_start_time = datetime.datetime.now()
parser = argparse.ArgumentParser(description='Sets Up OCI via TF')
parser.add_argument('propsfile', help="Full Path of properties file containing input variables. eg setUpAzure.properties")
#parser.add_argument('--main_options', default="")
#parser.add_argument('--sub_options', default="")
#parser.add_argument('--sub_child_options', default="")
#parser.add_argument('--add_filter', default=None)
#parser.add_argument('--devops', default=False)
args = parser.parse_args()
setUpAz_props = configparser.RawConfigParser()
setUpAz_props.read(args.propsfile)
#devops = args.devops
#main_options = args.main_options.split(",")
#sub_options = args.sub_options.split(",")
#sub_child_options = args.sub_child_options.split(",")

#Read Config file Variables
try:
    workflow_type = setUpAz_props.get('Default', 'workflow_type').strip().lower()

    if (workflow_type == 'export_resources'):
        non_gf_tenancy = True
    else:
        non_gf_tenancy = False

    inputfile = setUpAz_props.get('Default','cd3file').strip()
    outdir = setUpAz_props.get('Default', 'outdir').strip()
    prefix = setUpAz_props.get('Default', 'prefix').strip()
    tf_or_tofu = "terraform"

    if not outdir:
        exit_menu('input outdir location cannot be left blank. Exiting... ')
    elif not prefix:
        exit_menu('input prefix value cannot be left blank. Exiting... ')
    elif not inputfile:
        exit_menu('input cd3file location cannot be left blank. Exiting... ')
    elif '.xls' not in inputfile:
        exit_menu('valid formats for input cd3file are either .xls or .xlsx')
except Exception as e:
    exit_menu(str(e) + ". Check input properties file and try again. Exiting... ")



Option = namedtuple('Option', ['name', 'callback', 'text'])
extra = ''

# Pre-work
if not os.path.exists(outdir):
    os.makedirs(outdir)


#if devops:
    # Set Export filters from devops
    #export_filters = args.add_filter.split("@") if args.add_filter else []
    #ct.get_export_filters(export_filters)

## Menu Options
if non_gf_tenancy:

    ct = azrCommonTools()
    credentials = ct.authenticate(args.propsfile)

    # verify_outdir_is_empty()
    print("\nworkflow_type set to export_resources. Export existing Azure objects and Synch with TF state")
    print("We recommend to not have any existing tfvars/tfstate files for export out directory")
    #export_regions = get_region_list(rm=False,vizoci=False)
    #compartments = ct.get_compartment_map(var_file, "OCI Resources")
    #export_tags_list = get_tags_list()

    inputs = [
        Option("Export DB @Azure", export_db_at_azure, "Export DB @Azure"),

    ]

else:
    inputs = [
        Option('Create DB @Azure', create_db_at_azure, 'Create DB @Azure'),

    ]
'''
if main_options and args.main_options != "":
    options = match_options(inputs, main_options)
    for option in options:
        with section(option.text, header=True):
            option.callback(prim_options=sub_options)
else:
'''
if True:
    print("\nChoose appropriate option from below :\n")
    # Run menu
    menu = True
    while menu:
        if non_gf_tenancy:
            options = show_options(inputs, quit=True, index=1)
        else:
            options = show_options(inputs, quit=True, extra='\nSee example folder for sample input files\n', index=1)
        if 'q' in options:
            exit_menu('Exiting...')
        for option in options:
            menu = False
            with section(option.text, header=True):
                option.callback()
                if menu:
                    break
# write updated paths to a file
'''
updated_paths_file = f'{outdir}/.safe/updated_paths.safe'
with open(updated_paths_file, 'w+') as f:
    for item in updated_paths:
        f.write(str(item).replace('//', '/') + "\n")
f.close()
import_scripts_file = f'{outdir}/.safe/import_scripts.safe'
with open(import_scripts_file, 'w+') as f:
    for item in import_scripts:
        f.write(str(item).replace('//', '/') + "\n")
f.close()
'''