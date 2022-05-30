import argparse
import Database
import Identity
import Compute
import ManagementServices
import DeveloperServices
import cd3Validator
import Storage
import Network
import Governance
from fetch_compartments_to_variablesTF import fetch_compartments
from commonTools import *
from collections import namedtuple
from glob import glob
from Security.CloudGuard import *
from Security.KeyVault import *
from Storage.ObjectStorage import *


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
        return [options[int(choice)-index] for choice in user_input]
    except IndexError as ie:
        print("Invalid Choice.....Exiting!!")
        exit(1)


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
        terraform_files = glob(f'{outdir}/{reg}/*.auto.tfvars')
        tf_list[reg] = [file for file in terraform_files]


    has_files = False
    for reg in ct.all_regions:
        if len(tf_list[reg]) > 0:
            print(f'{outdir}/{reg} directory under outdir is not empty; contains below tf files.')
            for files in tf_list[reg]:
                print(files)
            has_files = True

    if has_files:
        print("\nMake sure you have clean tfstate file and outdir(other than provider.tf and variables_<region>.tf) for fresh export.")
        print("Existing tf files should not be conflicting with new tf files that are going to be generated with this process.")
        proceed = input("Proceed y/n: ")
        if proceed.lower() != 'y':
            exit_menu("Exiting...")
    else:
        print("None Found. Proceeding to Export...")


def validate_cd3(execute_all=False):
    options = [
        Option("Validate Compartments", None, None),
        Option("Validate Groups", None, None),
        Option("Validate Policies", None, None),
        Option("Validate Network(VCNs, Subnets, DHCP, DRGs)", None, None),
        Option("Validate Instances", None, None),
        Option("Validate Block Volumes", None, None),
    ]
    if not execute_all:
        options = show_options(options, quit=True, menu=False, index=1)
    cd3Validator.validate_cd3(inputfile, prefix,outdir, options, config)
    print("Exiting CD3 Validation...")

def get_compartment_list(resource_name):
    compartment_list_str = "Enter name of Compartment as it appears in OCI (comma separated without spaces if multiple)for which you want to export {};\nPress 'Enter' to export from all the Compartments: "
    compartments = input(compartment_list_str.format(resource_name))
    return list(map(lambda x: x.strip(), compartments.split(','))) if compartments else None

################## Export Functions ##########################
def export_identity():
    Identity.export_identity(inputfile, outdir, _config=config)
    create_identity(execute_all=True)
    print("\n\nExecute tf_import_commands_identity_nonGF.sh script created under home region directory to synch TF with OCI Identity objects\n")


def export_network():
    compartments = get_compartment_list('Network Objects')
    Network.export_networking(inputfile, outdir, _config=config, network_compartments=compartments)
    options = [
        Option(None, Network.create_major_objects, 'Processing VCNs and DRGs Tab'),
        Option(None, Network.create_terraform_dhcp_options, 'Processing DHCP Tab'),
        Option(None, Network.create_terraform_subnet, 'Processing Subnets Tab'),
        Option(None, Network.modify_terraform_secrules, 'Processing SecRulesinOCI Tab'),
        Option(None, Network.modify_terraform_routerules, 'Processing RouteRulesinOCI Tab'),
        Option(None, Network.create_terraform_drg_route, 'Processing DRGs tab for DRG Route Tables and Route Distribution creation'),
        Option(None, Network.modify_terraform_drg_routerules, 'Processing DRGRouteRulesinOCI Tab'),
        Option(None, Network.create_terraform_nsg, 'Processing NSGs Tab'),
    ]
    execute_options(options, inputfile, outdir, prefix, non_gf_tenancy, config=config)
    print("\n\nExecute tf_import_commands_network_nonGF.sh script created under each region directory to synch TF with OCI Network objects\n")


def export_tags():
    Governance.export_tags_nongreenfield(inputfile, outdir, _config=config, network_compartments=None)
    create_tags()
    print("\n\nExecute tf_import_commands_tags_nonGF.sh script created under home region directory to synch TF with OCI Tags\n")


def export_compute():
    options = [Option("Export Dedicated VM Hosts", export_dedicatedvmhosts, 'Exporting Dedicated VM Hosts'),
               Option("Export Instances", export_instances, 'Exporting Instances')]

    options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, prefix, config)

def export_dedicatedvmhosts(inputfile, outdir, prefix,config):
    compartments = get_compartment_list('Dedicated VM Hosts')
    Compute.export_dedicatedvmhosts(inputfile, outdir, _config=config, network_compartments=compartments)
    create_dedicatedvmhosts(inputfile, outdir, prefix, config)
    print("\n\nExecute tf_import_commands_dedicatedvmhosts_nonGF.sh script created under each region directory to synch TF with OCI Dedicated VM Hosts\n")

def export_instances(inputfile, outdir, prefix,config):
    compartments = get_compartment_list('Instances')
    print("Enter values for below filters to restrict the export for Instances; Press 'Enter' to use empty value for the filter")
    filter_str1 = "Enter comma separated list of display name patterns of the instances: "
    filter_str2 = "Enter comma separated list of ADs of the instances eg AD1,AD2,AD3: "
    display_name_str = input(filter_str1)
    ad_name_str = input(filter_str2)
    display_names =  list(map(lambda x: x.strip(), display_name_str.split(','))) if display_name_str else None
    ad_names = list(map(lambda x: x.strip(), ad_name_str.split(','))) if ad_name_str else None

    Compute.export_instances(inputfile, outdir, config=config, network_compartments=compartments, display_names = display_names, ad_names = ad_names)
    create_instances(inputfile, outdir, prefix, config)
    print("\n\nExecute tf_import_commands_instances_nonGF.sh script created under each region directory to synch TF with OCI Instances\n")


def export_storage():
    options = [Option("Export Block Volumes/Block Backup Policy",export_block_volumes,'Exporting Block Volumes'),
               Option("Export File Systems", export_fss, 'Exporting FSS')]

    options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, prefix, config)

def export_block_volumes(inputfile, outdir, prefix,config):
    compartments = get_compartment_list('Block Volumes')
    print("Enter values for below filters to restrict the export for Block Volumes; Press 'Enter' to use empty value for the filter")
    filter_str1 = "Enter comma separated list of display name patterns of the Block Volumes: "
    filter_str2 = "Enter comma separated list of ADs of the Block Volumes eg AD1,AD2,AD3: "

    display_name_str = input(filter_str1)
    ad_name_str = input(filter_str2)
    display_names = list(map(lambda x: x.strip(), display_name_str.split(','))) if display_name_str else None
    ad_names = list(map(lambda x: x.strip(), ad_name_str.split(','))) if ad_name_str else None

    Storage.export_blockvolumes(inputfile, outdir, _config=config, network_compartments=compartments, display_names = display_names, ad_names = ad_names)
    create_block_volumes(inputfile, outdir, prefix, config=config)
    print("\n\nExecute tf_import_commands_blockvolumes_nonGF.sh script created under each region directory to synch TF with OCI Block Volume Objects\n")


def export_fss(inputfile, outdir, prefix,config):
    compartments = get_compartment_list('FSS objects')
    Storage.export_fss(inputfile, outdir, config=config, network_compartments=compartments)
    create_fss(inputfile, outdir, prefix, config=config)
    print("\n\nExecute tf_import_commands_fss_nonGF.sh script created under each region directory to synch TF with OCI FSS objects\n")


def export_lb():
    compartments = get_compartment_list('LBR objects')
    Network.export_lbr(inputfile, outdir, _config=config, network_compartments=compartments)
    create_lb(inputfile, outdir, prefix, config=config)
    print("\n\nExecute tf_import_commands_lbr_nonGF.sh script created under each region directory to synch TF with OCI LBR objects\n")


def export_databases():
    options = [Option("Export Virtual Machine or Bare Metal DB Systems",export_dbsystems_vm_bm,'Exporting VM and BM DB Systems'),
               Option("Export EXA Infra and EXA VMClusters", export_exa_infra_vmclusters, 'Exporting EXA Infra and EXA VMClusters')]

    options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, prefix, config)

def export_dbsystems_vm_bm(inputfile, outdir, prefix,config):
    compartments = get_compartment_list('VM and BM DB Systems')
    Database.export_dbsystems_vm_bm(inputfile, outdir, _config=config, network_compartments=compartments)
    Database.create_terraform_dbsystems_vm_bm(inputfile, outdir, prefix, config=config)
    print("\n\nExecute tf_import_commands_dbsystems-vm-bm_nonGF.sh script created under each region directory to synch TF with DBSystems\n")

def export_exa_infra_vmclusters(inputfile, outdir, prefix,config):
    compartments = get_compartment_list('EXA Infra and EXA VMClusters')
    Database.export_exa_infra(inputfile, outdir, _config=config, network_compartments=compartments)
    Database.export_exa_vmclusters(inputfile, outdir, _config=config, network_compartments=compartments)
    create_exa_infra_vmclusters(inputfile, outdir, prefix,config=config)
    print("\n\nExecute tf_import_commands_exa-infra_nonGF.sh and tf_import_commands_exa-vmclusters_nonGF.sh scripts created under each region directory to synch TF with Exa-Infra and Exa-VMClusters\n")


def export_management_services():
    options = [Option("Export Notifications",export_notifications,'Exporting Notifications'),
               Option("Export Events", export_events,'Exporting Events'),
               Option("Export Alarms", export_alarms, 'Exporting Alarms')]

    options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, prefix, config)

def export_notifications(inputfile, outdir, prefix,config):
    compartments = get_compartment_list('Notifications')
    ManagementServices.export_notifications(inputfile, outdir, _config=config, network_compartments=compartments)
    ManagementServices.create_terraform_notifications(inputfile, outdir, prefix, config=config)
    print("\n\nExecute tf_import_commands_notifications_nonGF.sh script created under each region directory to synch TF with OCI Notifications\n")

def export_events(inputfile, outdir, prefix,config):
    compartments = get_compartment_list('Events')
    ManagementServices.export_events(inputfile, outdir, _config=config, network_compartments=compartments)
    ManagementServices.create_terraform_events(inputfile, outdir, prefix, config=config)
    print("\n\nExecute tf_import_commands_events_nonGF.sh script created under each region directory to synch TF with OCI Events\n")

def export_alarms(inputfile, outdir, prefix,config):
    compartments = get_compartment_list('Alarms')
    ManagementServices.export_alarms(inputfile, outdir, _config=config, network_compartments=compartments)
    ManagementServices.create_terraform_alarms(inputfile, outdir, prefix,config=config)
    print("\n\nExecute tf_import_commands_alarms_nonGF.sh script created under each region directory to synch TF with OCI Alarms\n")

################## Create Functions ##########################
def create_identity(execute_all=False):
    options = [
        Option('Add/Modify/Delete Compartments', Identity.create_terraform_compartments, 'Processing Compartments Tab'),
        Option('Add/Modify/Delete Groups', Identity.create_terraform_groups, 'Processing Groups Tab'),
        Option('Add/Modify/Delete Policies', Identity.create_terraform_policies, 'Processing Policies Tab'),
    ]
    if not execute_all:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, prefix, config=config)


def create_network(execute_all=False):
    options = [
        Option('Create Network - overwrites all TF files; reverts all SecLists and RouteTables to original rules', Network.create_all_tf_objects, 'Create All Objects'),
        Option('Modify Network - It will read VCNs, DRGs, Subnets and DHCP sheets and update the TF', modify_terraform_network, 'Modifying Network'),
        Option('Enable VCN Flow Logs', create_cis_vcnflow_logs, 'VCN Flow Logs'),
        Option('Security Rules', export_modify_security_rules, 'Security Rules'),
        Option('Route Rules', export_modify_route_rules, 'Route Rules'),
        Option('DRG Route Rules', export_modify_drg_route_rules, 'DRG Route Rules'),
        Option('Network Security Groups', export_modify_nsgs, 'Network Security Groups')
    ]
    if not execute_all:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, prefix, config=config, non_gf_tenancy=non_gf_tenancy)

def modify_terraform_network(inputfile, outdir, prefix, non_gf_tenancy, config):
    Network.create_all_tf_objects(inputfile, outdir, prefix, config=config, non_gf_tenancy=non_gf_tenancy, modify_network=True)

def create_cis_vcnflow_logs(*args,**kwargs):
    options = [Option(None, ManagementServices.enable_cis_vcnflow_logging, 'Enabling VCN Flow Logs')]
    execute_options(options, inputfile, outdir, prefix, config=config)

def export_modify_security_rules(inputfile, outdir, prefix, non_gf_tenancy, config):
    execute_all = False
    options = [
        Option('Export Security Rules in OCI', export_security_rules, 'Exporting Security Rules in OCI'),
        Option('Add/Modify/Delete Security Rules', Network.modify_terraform_secrules, 'Processing SecRulesinOCI Tab'),
    ]
    if not execute_all:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, prefix, config=config, non_gf_tenancy=non_gf_tenancy)

def export_security_rules(inputfile, outdir, prefix, config, non_gf_tenancy):
    compartments = get_compartment_list('OCI Security Rules')
    Network.export_seclist(inputfile, network_compartments=compartments, _config=config, _tf_import_cmd=False, outdir=None)

def export_modify_route_rules(inputfile, outdir, prefix, non_gf_tenancy, config):
    execute_all = False
    options = [
        Option('Export Route Rules in OCI', export_route_rules, 'Exporting Route Rules in OCI'),
        Option('Add/Modify/Delete Route Rules', Network.modify_terraform_routerules, 'Processing RouteRulesinOCI Tab'),
    ]
    if not execute_all:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, prefix, config=config, non_gf_tenancy=non_gf_tenancy)

def export_route_rules(inputfile, outdir, prefix, config, non_gf_tenancy):
    compartments = get_compartment_list('OCI Route Rules')
    Network.export_routetable(inputfile, network_compartments=compartments, _config=config, _tf_import_cmd=False, outdir=None)

def export_modify_drg_route_rules(inputfile, outdir, prefix, non_gf_tenancy, config):
    execute_all = False
    options = [
        Option('Export DRG Route Rules in OCI', export_drg_route_rules, 'Exporting DRG Route Rules in OCI'),
        Option('Add/Modify/Delete DRG Route Rules', Network.modify_terraform_drg_routerules, 'Processing DRGRouteRulesinOCI Tab'),
    ]
    if not execute_all:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, prefix, config=config, non_gf_tenancy=non_gf_tenancy)

def export_drg_route_rules(inputfile, outdir, prefix, config, non_gf_tenancy):
    compartments = get_compartment_list('OCI DRG Route Rules')
    Network.export_drg_routetable(inputfile, network_compartments=compartments, _config=config, _tf_import_cmd=False,outdir=None)

def export_modify_nsgs(inputfile, outdir, prefix, non_gf_tenancy, config):
    execute_all = False
    options = [
        Option('Export NSGs in OCI', export_nsgs, 'Exporting NSGs in OCI'),
        Option('Add/Modify/Delete NSGs', Network.create_terraform_nsg, 'Processing NSGs Tab'),
    ]
    if not execute_all:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, prefix, config=config, non_gf_tenancy=non_gf_tenancy)

def export_nsgs(inputfile, outdir, prefix, config, non_gf_tenancy):
    compartments = get_compartment_list('OCI NSGs')
    Network.export_nsg(inputfile, network_compartments=compartments, _config=config, _tf_import_cmd=False, outdir=None)


def create_tags():
    options = [Option(None, Governance.create_terraform_tags, 'Processing Tags Tab')]
    execute_options(options, inputfile, outdir, prefix,config=config)


def create_compute():
    options = [
        Option('Add/Modify/Delete Dedicated VM Hosts', Compute.create_terraform_dedicatedhosts, 'Processing Dedicated VM Hosts Tab'),
        Option('Add/Modify/Delete Instances/Boot Backup Policy', create_instances,''),
    ]
    options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, prefix,config)

def create_instances(inputfile, outdir, prefix,config):
    options = [
        Option(None, Compute.create_terraform_instances, 'Processing Instances Tab')
    ]
    execute_options(options, inputfile, outdir, prefix,config)

def create_dedicatedvmhosts(inputfile, outdir, prefix,config):
    options = [Option(None, Compute.create_terraform_dedicatedhosts, 'Processing Dedicated VM Hosts Tab')]
    execute_options(options, inputfile, outdir, prefix,config=config)


def create_storage(execute_all=False):
    options = [
        Option('Add/Modify/Delete Block Volumes/Block Backup Policy', create_block_volumes, ''),
        Option('Add/Modify/Delete File Systems', create_fss, '')]
    options = show_options(options, quit=True, menu=True, index=1)
    if not execute_all:
        execute_options(options, inputfile, outdir, prefix, config)

def create_block_volumes(inputfile, outdir, prefix,config):
    options = [
        Option(None, Storage.create_terraform_block_volumes, 'Processing BlockVolumes Tab')
    ]
    execute_options(options, inputfile, outdir, prefix,config=config)

def create_fss(inputfile, outdir, prefix,config):
    options = [Option(None, Storage.create_terraform_fss, 'Processing FSS Tab')]
    execute_options(options, inputfile, outdir, prefix,config=config)


def create_loadbalancer(execute_all=False):
    options = [
        Option('Add/Modify/Delete Load Balancers', create_lb, 'LBaaS'),
        Option('Enable LBaaS Logs', enable_lb_logs, 'LBaaS Logs')]
    options = show_options(options, quit=True, menu=True, index=1)
    if not execute_all:
        execute_options(options, inputfile, outdir, prefix, config)

def create_lb(inputfile, outdir, prefix, config):
    options = [
         Option(None, Network.create_terraform_lbr_hostname_certs, 'Creating LBR'),
         Option(None, Network.create_backendset_backendservers, 'Creating Backend Sets and Backend Servers'),
         Option(None, Network.create_listener, 'Creating Listeners'),
         Option(None, Network.create_path_route_set, 'Creating Path Route Sets'),
         Option(None, Network.create_ruleset, 'Creating Rule Sets'),
    ]
    execute_options(options, inputfile, outdir, prefix, config=config)

def enable_lb_logs(inputfile, outdir, prefix, config):
    options = [Option(None, ManagementServices.enable_load_balancer_logging, 'Enabling LBaaS Logs')]
    execute_options(options, inputfile, outdir, prefix, config=config)

def create_databases(execute_all=False):
    options = [
        Option('Add/Modify/Delete Virtual Machine or Bare Metal DB Systems', Database.create_terraform_dbsystems_vm_bm, 'Processing DBSystems-VM-BM Tab'),
        Option('Add/Modify/Delete EXA Infra and EXA VM Cluster', create_exa_infra_vmclusters, ''),
        Option('Add/Modify/Delete ADW/ATP', Database.create_terraform_adw_atp, 'Processing ADW/ATP Tab'),
    ]
    if not execute_all:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, prefix, config=config)

def create_exa_infra_vmclusters(inputfile, outdir, prefix,config):
    options = [Option(None, Database.create_terraform_exa_infra, 'Processing Exa-Infra Tab'),
    Option(None, Database.create_terraform_exa_vmclusters, 'Processing Exa-VM-Clusters Tab')]
    execute_options(options, inputfile, outdir, prefix, config)


def create_management_services(execute_all=False):
    options = [
        Option("Add/Modify/Delete Notifications", ManagementServices.create_terraform_notifications, 'Setting up Notifications'),
        Option("Add/Modify/Delete Events", ManagementServices.create_terraform_events, 'Setting up Events'),
        Option("Add/Modify/Delete Alarms", ManagementServices.create_terraform_alarms, 'Setting up Alarms'),
    ]
    if not execute_all:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, prefix, config=config)


def create_developer_services(execute_all=False):
    options = [
        Option("Upload current terraform files/state to Resource Manager", DeveloperServices.create_resource_manager, 'Creating RM Stack')]
    if not execute_all:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, outdir, prefix, config=config)


def create_cis_features(execute_all=False):
    options = [Option("Create Key/Vault, Object Storage Bucket and enable Logging for write events to bucket", create_cis_keyvault_oss_log, 'Creating CIS Key/Vault, Object Storage Bucket and enable Logging for write events to bucket'),
               Option("Create Default Budget",create_cis_budget,'Creating Default Budget'),
               Option("Enable Cloud Guard", enable_cis_cloudguard, 'Enable Cloud Guard'),]

    if not execute_all:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, outdir, prefix, config=config)

def create_cis_keyvault_oss_log(*args,**kwargs):
    region_name = input("Enter region name eg ashburn where you want to create OSS Bucket and Key/Vault: ")
    comp_name = input("Enter name of compartment as it appears in OCI Console: ")

    options = [Option(None, create_cis_keyvault, 'Creating KeyVault'),
               Option(None, create_cis_oss, 'Creating Object Storage Bucket'),
               Option(None, ManagementServices.enable_cis_oss_logging, 'Enabling Logging for write events to bucket')]
    execute_options(options, outdir, prefix,region_name, comp_name, config=config)

def create_cis_budget(*args,**kwargs):
    amount = input("Enter Monthly Budget Amount (in US$): ")
    threshold = input("Enter Threshold Percentage of Budget: ")
    options = [Option(None, Governance.create_cis_budget, 'Creating Budget')]
    execute_options(options, outdir, prefix,amount,threshold, config=config)

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
        Option('Export Tags', export_tags, 'Tagging'),
        Option('Export Network', export_network, 'Network'),
        Option('Export Compute', export_compute, 'Dedicated VM Hosts and Instances'),
        Option('Export Storage', export_storage, 'Storage'),
        Option('Export Databases', export_databases, 'Databases'),
        Option('Export Load Balancers', export_lb, 'Load Balancers'),
        Option('Export Management Services', export_management_services, 'Management Services'),
    ]

    verify_outdir_is_empty()
    fetch_compartments(outdir, config)
    print("\nnon_gf_tenancy in properties files is set to true..Export existing OCI objects and Synch with TF state")
    print("Process will fetch objects from OCI in the specified compartment from all regions tenancy is subscribed to\n")
else:
    inputs = [
        Option('Validate CD3', validate_cd3, 'Validate CD3'),
        Option('Identity', create_identity, 'Identity'),
        Option('Tags', create_tags, 'Tagging'),
        Option('Network', create_network, 'Network'),
        Option('Compute', create_compute, 'Compute'),
        Option('Storage', create_storage, 'Storage'),
        Option('Database', create_databases, 'Databases'),
        Option('Load Balancers', create_loadbalancer, 'Load Balancers'),
        Option('Management Services', create_management_services, 'Management Services'),
        Option('Developer Services', create_developer_services, 'Developer Services'),
        Option('Enable OCI CIS Compliant Features (Key/Vault, OSS, Budget, Cloud-Guard)', create_cis_features, 'CIS Compliant Features'),

    ]

# Run menu
menu = True
while menu:
    if non_gf_tenancy:
        options = show_options(inputs, quit=True, index=1)
    else:
        options = show_options(inputs, quit=True, extra='\nSee example folder for sample input files\n', index=0)
    if 'q' in options:
        exit_menu('Exiting...')
    for option in options:
        menu = False
        with section(option.text, header=True):
            option.callback()
            if menu:
                break