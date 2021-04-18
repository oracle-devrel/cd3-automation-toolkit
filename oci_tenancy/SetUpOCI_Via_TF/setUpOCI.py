import argparse
import configparser
import Database
import Identity
import os
import ResourceManager
import Solutions
import sys
# import fetch_compartments_to_variablesTF as fetch_compartments
from commonTools import *
from collections import namedtuple
from CoreInfra import Networking
from CoreInfra import BlockVolume
from CoreInfra import Compute
from CoreInfra import FileStorage
from Governance import Tagging
from glob import glob
from textwrap import shorten


def show_options(options, quit=False, menu=False, extra=None):
    # Just add whitespace between number and option. It just makes it look better
    number_offset = len(str(len(options))) + 1

    # Iterate over options. Print number and option
    for i, option in enumerate(options, 1):
        print(f'{str(i)+".":<{number_offset}} {option.name}')
    if quit:
        print(f'{"q"+".":<{number_offset}} Press q to quit')
    if menu:
        print(f'{"m"+".":<{number_offset}} Press m to go back to Main Menu')
    if extra:
        print(extra)

    user_input = input('Enter your choice: ')
    user_input = user_input.split(',')
    if 'q' in user_input or 'm' in user_input:
        return user_input
    # Subtract one to account for zero-indexing. The options start at 1
    return [options[int(choice)-1] for choice in user_input]


def execute_options(options, *args, **kwargs):
    global menu, quit
    if 'm' in options or 'q' in options:
        menu = 'm' in options
        quit = 'q' in options
    else:
        for option in options:
            with section(option.text):
                option.callback(*args, **kwargs)


def verify_outdir_is_empty():
    ct = commonTools()
    ct.get_subscribedregions(config)

    print("\nChecking if the specified outdir contains tf files related to the OCI components being exported...")
    tf_list = {}
    for reg in ct.all_regions:
        whitelisted_files = ['provider.tf', f'variables_{reg}.tf']
        terraform_files = glob(f'{outdir}/{reg}/*.tf')
        tf_list[reg] = [file for file in terraform_files if file not in whitelisted_files]

    has_files = False
    for reg in ct.all_regions:
        if len(tf_list[reg]) > 0:
            print(f'{outdir}/{reg} directory under outdir is not empty; contains below tf files {shorten(tf_list[reg].join(","), 40)}')
            has_files = True

    if has_files:
        print("\nMake sure you have clean tfstate file and outdir(other than provider.tf and variables_<region>.tf) for fresh export.")
        print("Existing tf files should not be conflicting with new tf files that are going to be generated with this process.")
        proceed = input("Proceed y/n: ")
        if proceed.lower() != 'y':
            exit_menu("Exiting...")
    else:
        print("None Found. Proceeding to Export...")


def validate_cd3():
    choice = input("Do you want to verify CD3 Network Tabs? Enter y or n: ").lower()
    if choice == 'y':
        print('It will verify tabs: VCNs, DHCP and Subnets in excel sheet\n')
        validated = validate_cd3(inputfile, config)
        if not validated:
            prcd = input('Do you still want to proceed with setUpOCI? Enter y or n: ').lower()
            if (prcd != 'y'):
                exit_menu('Exiting...', exit_code=1)
    elif choice != 'n':
        exit_menu("\nInvalid Input !! Please enter 'y' or 'n'... Exiting!!")


def get_compartment_list(resource_name):
    compartment_list_str = "Enter name of Compartment as it appears in OCI (comma separated without spaces if multiple)for which you want to export {};\nPress 'Enter' to export from all the Compartments: "
    compartments = input(compartment_list_str.format(resource_name))
    return list(map(lambda x: x.strip(), compartments.split(','))) if compartments else []


def export_identity():
    Identity.export_identity(inputfile, outdir, prefix, config)
    create_identity(execute_all=True)
    print("\n\nExecute tf_import_commands_identity_nonGF.sh script created under home region directory to synch TF with OCI Identity objects\n")


def export_networking():
    compartments = get_compartment_list('Network Objects')
    Networking.export_networking(inputfile, outdir, prefix, config=config, compartments=comparments)
    create_networking(execute_all=True)
    print("\n\nExecute tf_import_commands_network_nonGF.sh script created under each region directory to synch TF with OCI Network objects\n")


def export_instances():
    compartments = get_compartment_list('Instances')
    Compute.export_instance(inputfile, outdir, config=config, compartments=compartments)
    create_instances(execute_all=True)
    print("\n\nExecute tf_import_commands_instances_nonGF.sh script created under each region directory to synch TF with OCI Instances\n")


def export_block_volumes():
    compartments = get_compartment_list('Block Volumes')
    BlockVolumes.export_blockvol(inputfile, outdir, config=config, compartments=compartments)
    create_block_volumes()
    print("\n\nExecute tf_import_commands_blockvols_nonGF.sh script created under each region directory to synch TF with OCI Instances\n")


def export_tags():
    Tagging.export_tags(inputfile, outdir, config=config)
    create_tags()
    print("\n\nExecute tf_import_commands_tags_nonGF.sh script created under home region directory to synch TF with OCI Identity objects\n")


def export_fss():
    compartments = get_compartment_list('FSS objects')
    FileStorage.export_fss(inputfile, outdir, config=config, compartments=compartments)
    create_fss()
    print("\n\nExecute tf_import_commands_fss_nonGF.sh script created under each region directory to synch TF with OCI FSS objects\n")


def export_lb():
    compartments = get_compartment_list('LBR objects')
    Networking.export_lbr(inputfile, outdir, config=config, compartments=compartments)
    create_lb()
    print("\n\nExecute tf_import_commands_lbr_nonGF.sh script created under each region directory to synch TF with OCI LBR objects\n")


def export_events_notifications():
    compartments = get_compartment_list('Events and Notifications objects')
    Solutions.export_solutions(inputfile, outdir, config=config, compartments=compartments)
    create_events_notifications(execute_all=True)
    print("\n\nExecute tf_import_commands_solutions_nonGF.sh script created under each region directory to synch TF with OCI Events and Notifications objects\n")


def create_identity(execute_all=False):
    options = [
        Option('Add/Modify/Delete Compartments', Identity.create_terraform_compartments, 'Compartments Tab'),
        Option('Add/Modify/Delete Groups', Identity.create_terraform_groups, 'Group Tab'),
        Option('Add/Modify/Delete Policies', Identity.create_terraform_policies, 'Policies Tab'),
    ]
    if not execute_all:
        options = show_options(options, quit=True, menu=True)
    execute_options(options, inputfile, outdir, prefix, config=config)


def modify_terraform_network(inputfile, outdir, prefix, config):
    Networking.create_all_tf_objects(inputfile, outdir, prefix, config=config, modify_network=True)


def export_terraform_routes_and_secrules(inputfile, outdir, prefix, config):
    compartments = input("Enter name of Compartment as it appears in OCI (comma separated if multiple) for which you want to export rules;\nPress 'Enter' to export from all the Compartments: ")
    compartments = comparments.split(',') if compartments else []
    Networking.export_seclist(inputfile, outdir, prefix, config=config, modify_network=True, network_compartments=compartments)
    Networking.export_routetables(inputfile, outdir, prefix, config=config, modify_network=True, network_compartments=compartments)


def create_networking(execute_all=False):
    options = [
        Option('Create Network - overwrites all TF files; reverts all SecLists and RouteTables to original rules', Networking.create_all_tf_objects, 'Create All Objects'),
        Option('Modify Network - Add/Remove/Modify any network object; updates TF files with changes; this option should be used after modifications have been done to SecRules or RouteRules', modify_terraform_network, 'Modifying Networking'),
        Option('Export existing SecRules and RouteRules to cd3', export_terraform_routes_and_secrules, 'Exporting Rules'),
        Option('Modify SecRules', Networking.modify_terraform_secrules, 'Modifiying Security Rules'),
        Option('Modify RouteRules', Networking.modify_terraform_routerules, 'Modifiying Route Rules'),
        Option('Add/Modify/Delete Network Security Groups', Networking.create_terraform_nsg, 'Processing NSGs Tab'),
    ]
    if not execute_all:
        validate_cd3()
        options = show_options(options, quit=True, menu=True)
    execute_options(options, inputfile, outdir, prefix, config=config)


def create_instances(execute_all=False):
    options = [
        Option('Add/Modify/Delete Dedicated VM Hosts', Compute.create_terraform_dedicatedhosts, 'Processing DedicatedVMHosts Tab'),
        Option('Add/Modify/Delete Instances/Boot Backup Policy', Compute.create_terraform_instances, 'Processing Instances Tab'),
    ]
    if not execute_all:
        options = show_options(options, quit=True, menu=True)
    execute_options(options, inputfile, outdir, config=config)


def create_block_volumes():
    options = [
        Option(None, BlockVolume.create_terraform_block_volumes, 'Processing Block Volume Tab'),
        Option(None, BlockVolume.block_backups_policy, 'Processing Block Volume Policies'),
    ]
    execute_options(options, inputfile, outdir, config=config)


def create_tags():
    options = [Option(None, Tagging.create_namespace_tagkey, 'Processing Tags Tab')]
    execute_options(options, inputfile, outdir, config=config)


def create_fss():
    options = [Option(None, FileStorage.create_terraform_fss, 'Processing FSS Tab')]
    execute_options(options, inputfile, outdir, config=config)


def create_lb():
    options = [
        Option(None, Networking.create_terraform_lbr_hostname_certs, 'Creating LBR'),
        Option(None, Networking.create_backendset_backendservers, 'Creating Backend Sets and Backend Servers'),
        Option(None, Networking.create_listener, 'Creating Listeners'),
        Option(None, Networking.create_path_route_set, 'Creating Pauth Route Sets'),
        Option(None, Networking.create_ruleset, 'Creating Rule Sets'),
    ]
    execute_options(options, inputfile, outdir, config=config)


def create_adw():
    options = [Options(None, Database.create_terraform_adw_atp, 'Processing ADW/ATP Tab')]
    execute_options(options, inputfile, outdir, prefix, config=config)


def create_db(execute_all=False):
    options = [
        Option('Add/Modify/Delete Virtual Machine', Database.create_terraform_database_VM, 'Processing DB_System_VM Tab'),
        Option('Add/Modify/Delete Bare Metal', Database.create_terraform_database_BM, 'Processing DB_System_BM Tab'),
        Option('Add/Modify/Delete ExaData', Database.create_terraform_database_EXA, 'Processing DB_System_EXA Tab'),
    ]
    if not execute_all:
        choices = show_options(options, quit=True, menu=True)
    execute_options(choices, inputfile, outdir, prefix, config=config)


def create_events_notifications(execute_all=False):
    options = [
        Option("Add/Modify/Delete Notifications", Solutions.create_terraform_notifications, 'Setting up Notifications'),
        Option("Add/Modify/Delete Events", Solutions.create_terraform_events, 'Setting up Events'),
    ]
    if not execute_all:
        choices = show_options(options, quit=True, menu=True)
    execute_options(choices, inputfile, outdir, prefix, config=config)


def create_resource_manager():
    options = [Options(None, ResourceManager.create_resource_manager_stack, 'Creating stack')]
    execute_options(options, outdir, prefix, config=config)


parser = argparse.ArgumentParser(description='Sets Up OCI via TF')
parser.add_argument('propsfile', help="Full Path of properties file containing input variables. eg setUpOCI.properties")
args = parser.parse_args()
config = configparser.RawConfigParser()
config.read(args.propsfile)

#Read Config file Variables
try:
    non_gf_tenancy = config.get('Default', 'non_gf_tenancy').strip().lower() == 'true'
    inputfile = config.get('Default','cd3file').strip()
    outdir = config.get('Default', 'outdir').strip()
    prefix = config.get('Default', 'prefix').strip()
    config = config.get('Default', 'config_file').strip() or DEFAULT_LOCATION

    if not outdir:
        exit_menu('input outdir location cannot be left blank. Exiting... ')
    elif not prefix:
        exit_menu('input prefix value cannot be left blank. Exiting... ')
    elif not inputfile:
        exit_menu('input cd3file location cannot be left blank. Exiting... ')
    elif '.xls' not in inputfile:
        exit_menu('valid formats for input cd3file are either .xls or .xlsx')
except Exception as e:
    exit_menu(e + 'Check if input properties exist and try again..exiting...`')

Option = namedtuple('Option', ['name', 'callback', 'text'])
extra = ''

# Pre-work
if not os.path.exists(outdir):
    os.makedirs(outdir)

if non_gf_tenancy:
    inputs = [
        Option('Export Identity', export_identity, 'Identity'),
        Option('Export Networking', export_networking, 'Networking'),
        Option('Export Dedicated VM Hosts/Instances/Boot Backup Policy', export_instances, 'Instances'),
        Option('Export Create and Attach Block Volumes/Block BackUp Policy', export_block_volumes, 'Block Volumes'),
        Option('Export Tags', export_tags, 'Tagging'),
        Option('Export File Storage Service', export_fss, 'FSS'),
        Option('Export Load Balancer Service', export_lb, 'Load Balancers'),
        Option('Export Solutions (Events and Notifications)', export_events_notifications, 'Solutions'),
    ]
    verify_outdir_is_empty()
    fetch_compartments(inputfile, config)
    print("\nnon_gf_tenancy in properties files is set to true..Export existing OCI objects and Synch with TF state")
    print("Process will fetch objects from OCI in the specified compartment from all regions tenancy is subscribed to\n")
else:
    inputs = [
        Option('Identity', create_identity, 'Identity'),
        Option('Networking', create_networking, 'Networking'),
        Option('Dedicated VM Hosts/Instances/Boot Backup Policy', create_instances, 'Instances'),
        Option('Create and Attach Block Volumes/Block BackUp Policy', create_block_volumes, 'Block Volumes'),
        Option('Tags', create_tags, 'Tagging'),
        Option('File Storage Service', create_fss, 'FSS'),
        Option('Load Balancer Service', create_lb, 'Load Balancers'),
        Option('ADW/ATP', create_adw, 'ADW/ATP'),
        Option('Database', create_db, 'Database'),
        Option('Solutions (Events and Notifications)', create_events_notifications, 'Solutions'),
        Option('Upload current terraform files/state to Resource Manager', create_resource_manager, 'Resource Manager'),
    ]

# Run menu
menu = True
while menu:
    options = show_options(inputs, quit=True, extra='\nSee example folder for sample input files\n')
    if 'q' in options:
        exit_menu('Exiting...')
    for option in options:
        menu = False
        with section(option.text, header=True):
            option.callback()
            if menu:
                break
