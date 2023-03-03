import argparse
import configparser
import Database
import Identity
import Compute
import ManagementServices
import DeveloperServices
import Security
import cd3Validator
import Storage
import Network
import Governance
from fetch_compartments_to_variablesTF import fetch_compartments
from commonTools import *
from collections import namedtuple
from glob import glob
import requests
import subprocess


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
            with section(option.text):
                option.callback(*args, **kwargs)


def verify_outdir_is_empty():

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
        Option("Validate Tags", None, None),
        Option("Validate Network(VCNs, Subnets, DHCP, DRGs)", None, None),
        Option("Validate Instances", None, None),
        Option("Validate Block Volumes", None, None),
        Option("Validate FSS", None, None),
    ]
    if not execute_all:
        options = show_options(options, quit=True, menu=False, index=1)
    cd3Validator.validate_cd3(inputfile, prefix, outdir, options, config)
    print("Exiting CD3 Validation...")

def get_compartment_list(ntk_compartment_ids,resource_name):
    compartment_list_str = "Enter name of Compartment as it appears in OCI (comma separated without spaces if multiple)for which you want to export {};\nPress 'Enter' to export from all the Compartments: "
    compartments = input(compartment_list_str.format(resource_name))
    input_compartment_names = list(map(lambda x: x.strip(), compartments.split(','))) if compartments else None

    remove_comps = []
    comp_list_fetch = []

    print("\n")
    # Process Compartment Filter
    if input_compartment_names is not None:
        for x in range(0, len(input_compartment_names)):
            if (input_compartment_names[x] not in ntk_compartment_ids.keys()):
                print("Input compartment: " + input_compartment_names[x] + " doesn't exist in OCI")
                remove_comps.append(input_compartment_names[x])

        input_compartment_names = [x for x in input_compartment_names if x not in remove_comps]
        if (len(input_compartment_names) == 0):
            print("None of the input compartments specified exist in OCI..Exiting!!!")
            exit(1)
        else:
            print("Fetching for Compartments... " + str(input_compartment_names))
            comp_list_fetch = input_compartment_names
    else:
        print("Fetching for all Compartments...")
        comp_ocids = []
        for key, val in ntk_compartment_ids.items():
            if val not in comp_ocids:
                comp_ocids.append(val)
                comp_list_fetch.append(key)
    return comp_list_fetch


def get_region_list(rm):
    if rm == False:
        resource_name = 'OCI resources'
        region_list_str = "\nEnter region (comma separated without spaces if multiple) for which you want to export {}; Identity and Tags will be exported from Home Region.\nPress 'Enter' to export from all the subscribed regions- eg ashburn,phoenix: "
    else:
        resource_name = 'Terraform Stack'
        region_list_str = "\nEnter region (comma separated without spaces if multiple) for which you want to upload {} - eg ashburn,phoenix: "

    input_region_names = input(region_list_str.format(resource_name))
    input_region_names = list(map(lambda x: x.strip(), input_region_names.split(','))) if input_region_names else None
    remove_regions = []
    region_list_fetch = []

    #validate input regions
    if (input_region_names is not None):
        for x in range(0, len(input_region_names)):
            if (input_region_names[x].lower() not in ct.all_regions):
                print("Input region: " + input_region_names[x] + " is not subscribed to OCI Tenancy")
                remove_regions.append(input_region_names[x])

        input_region_names = [x.lower() for x in input_region_names if x not in remove_regions]
        if (len(input_region_names) == 0):
            print("None of the input regions specified are subscribed to OCI..Exiting!!!")
            exit(1)
        else:
            print("\nFetching for Regions... " + str(input_region_names))
            region_list_fetch = input_region_names
    else:
        print("Fetching for all Regions OCI tenancy is subscribed to...")
        region_list_fetch = ct.all_regions

    return region_list_fetch


################## Export Functions ##########################
def export_identity():
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['identity']
    else:
        service_dir = ""
    export_compartments = ct.ntk_compartment_ids
    Identity.export_identity(inputfile, outdir, service_dir, _config=config,export_compartments=export_compartments, ct=ct)
    create_identity(execute_all=True)
    print("\n\nExecute tf_import_commands_identity_nonGF.sh script created under home region directory to synch TF with OCI Identity objects\n")

def export_tags():
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['tagging']
    else:
        service_dir = ""
    export_compartments = ct.ntk_compartment_ids
    Governance.export_tags_nongreenfield(inputfile, outdir, service_dir, _config=config, export_compartments=export_compartments,ct=ct)
    create_tags()
    print("\n\nExecute tf_import_commands_tags_nonGF.sh script created under home region directory to synch TF with OCI Tags\n")

def export_network():
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['network']
    else:
        service_dir = ""
    options = [Option("Export all Network Components", export_networking,
                      'Exporting Network Components'),
               Option("Export Network components for VCNs, DRGs and DRGRouteRulesinOCI Tabs", export_major_objects,
                      'Exporting VCNs, DRGs and DRGRouteRulesinOCI Tabs'),
               Option("Export Network components for DHCP Tab", export_dhcp,
                      'Exporting DHCP Tab'),
               Option("Export Network components for SecRulesinOCI Tab", export_secrules,
                      'Exporting SecRulesinOCI Tab'),
               Option("Export Network components for RouteRulesinOCI Tab", export_routerules,
                      'Exporting RouteRulesinOCI Tab'),
               Option("Export Network components for Subnets Tab", export_subnets,
                      'Exporting Subnets Tab'),
               Option("Export Network components for NSGs Tab", export_nsg,
                      'Exporting NSGs Tab')

               ]
    options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, service_dir,prefix, config, export_regions,ct)

    print("=====================================================================================================================")
    print("NOTE: Make sure to execute tf_import_commands_network_major-objects_nonGF.sh before executing the other scripts.")
    print("=====================================================================================================================")


def export_networking(inputfile, outdir, service_dir, prefix,config,export_regions,ct):
    compartments = get_compartment_list(ct.ntk_compartment_ids,'Network Objects')
    Network.export_networking(inputfile, outdir, service_dir,_config=config, export_compartments=compartments, export_regions=export_regions,ct=ct)
    options = [
        Option(None, Network.create_major_objects, 'Processing VCNs and DRGs Tab'),
        Option(None, Network.create_terraform_dhcp_options, 'Processing DHCP Tab'),
        Option(None, Network.create_terraform_subnet, 'Processing Subnets Tab'),
        Option(None, Network.modify_terraform_secrules, 'Processing SecRulesinOCI Tab'),
        Option(None, Network.modify_terraform_routerules, 'Processing RouteRulesinOCI Tab'),
        Option(None, Network.create_terraform_drg_route,
               'Processing DRGs tab for DRG Route Tables and Route Distribution creation'),
        Option(None, Network.modify_terraform_drg_routerules, 'Processing DRGRouteRulesinOCI Tab'),
        Option(None, Network.create_terraform_nsg, 'Processing NSGs Tab'),
    ]
    execute_options(options, inputfile, outdir, service_dir,prefix, non_gf_tenancy, config=config)
    print("\n\nExecute tf_import_commands_network_*_nonGF.sh script created under each region directory to synch TF with OCI Network objects\n")

def export_major_objects(inputfile, outdir, service_dir,prefix,config,export_regions,ct):
    compartments = get_compartment_list(ct.ntk_compartment_ids,'VCN Major Objects')
    Network.export_major_objects(inputfile, outdir, service_dir, _config=config, export_compartments=compartments, export_regions=export_regions,ct=ct)
    Network.export_drg_routetable(inputfile, export_compartments=compartments, export_regions=export_regions, service_dir=service_dir,_config=config, _tf_import_cmd=True, outdir=outdir,ct=ct)
    options = [
        Option(None, Network.create_major_objects, 'Processing VCNs and DRGs Tab'),
        Option(None, Network.create_terraform_drg_route, 'Processing DRGRouteRulesinOCI Tab'),

    ]
    execute_options(options, inputfile, outdir,service_dir, prefix, non_gf_tenancy, config=config)
    print("\n\nExecute tf_import_commands_network_major-objects_nonGF.sh and tf_import_commands_network_drg_routerules_nonGF.sh scripts created under each region directory to synch TF with OCI Network objects\n")

def export_dhcp(inputfile, outdir, service_dir,prefix,config,export_regions,ct):
    compartments = get_compartment_list(ct.ntk_compartment_ids,'DHCP')
    Network.export_dhcp(inputfile, outdir, service_dir,_config=config, export_compartments=compartments, export_regions=export_regions,ct=ct)
    options = [
        Option(None, Network.create_terraform_dhcp_options, 'Processing DHCP Tab'),
        ]
    execute_options(options, inputfile, outdir, service_dir,prefix, non_gf_tenancy, config=config)
    print("\n\nExecute tf_import_commands_network_dhcp_nonGF.sh script created under each region directory to synch TF with OCI Network objects\n")

def export_secrules(inputfile, outdir, service_dir,prefix,config,export_regions,ct):
    compartments = get_compartment_list(ct.ntk_compartment_ids,'SecRulesInOCI')
    Network.export_seclist(inputfile, export_compartments=compartments, export_regions=export_regions, service_dir=service_dir,_config=config, _tf_import_cmd=True, outdir=outdir,ct=ct)
    options = [
        Option(None, Network.modify_terraform_secrules, 'Processing SecRulesinOCI Tab'),
        ]
    execute_options(options, inputfile, outdir,service_dir, prefix, non_gf_tenancy, config=config)
    print("\n\nExecute tf_import_commands_network_secrules_nonGF.sh script created under each region directory to synch TF with OCI Network objects\n")

def export_routerules(inputfile, outdir, service_dir,prefix,config,export_regions,ct):
    compartments = get_compartment_list(ct.ntk_compartment_ids,'RouteRulesInOCI')
    Network.export_routetable(inputfile, export_compartments=compartments, export_regions=export_regions, service_dir=service_dir,_config=config, _tf_import_cmd=True, outdir=outdir,ct=ct)
    options = [
        Option(None, Network.modify_terraform_routerules, 'Processing RouteRulesinOCI Tab'),
        ]
    execute_options(options, inputfile, outdir, service_dir,prefix, non_gf_tenancy, config=config)
    print("\n\nExecute tf_import_commands_network_routerules_nonGF.sh script created under each region directory to synch TF with OCI Network objects\n")


def export_subnets(inputfile, outdir, service_dir,prefix,config,export_regions, ct):
    compartments = get_compartment_list(ct.ntk_compartment_ids,'Subnets')
    Network.export_subnets(inputfile, outdir, service_dir,_config=config, export_compartments=compartments, export_regions=export_regions,ct=ct)
    options = [
        Option(None, Network.create_terraform_subnet, 'Processing Subnets Tab'),
        ]
    execute_options(options, inputfile, outdir, service_dir,prefix, non_gf_tenancy, config=config)
    print("\n\nExecute tf_import_commands_network_subnets_nonGF.sh script created under each region directory to synch TF with OCI Network objects\n")


def export_nsg(inputfile, outdir, prefix,service_dir,config,export_regions,ct):
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['nsg']
    else:
        service_dir = ""

    compartments = get_compartment_list(ct.ntk_compartment_ids,'NSGs')
    Network.export_nsg(inputfile, export_compartments=compartments, export_regions=export_regions, service_dir=service_dir,_config=config, _tf_import_cmd=True, outdir=outdir,ct=ct)
    options = [
        Option(None, Network.create_terraform_nsg, 'Processing NSGs Tab'),
        ]
    execute_options(options, inputfile, outdir, service_dir,prefix, non_gf_tenancy, config=config)
    print("\n\nExecute tf_import_commands_network_nsg_nonGF.sh script created under each region directory to synch TF with OCI Network objects\n")

def export_compute():
    options = [Option("Export Dedicated VM Hosts", export_dedicatedvmhosts, 'Exporting Dedicated VM Hosts'),
               Option("Export Instances (excludes instances launched by OKE)", export_instances, 'Exporting Instances')]

    options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, prefix, config, export_regions, ct)

def export_dedicatedvmhosts(inputfile, outdir, prefix,config, export_regions, ct):
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['dedicated-vm-host']
    else:
        service_dir = ""
    compartments = get_compartment_list(ct.ntk_compartment_ids,'Dedicated VM Hosts')
    Compute.export_dedicatedvmhosts(inputfile, outdir, service_dir, _config=config, export_compartments=compartments, export_regions=export_regions,ct=ct)
    create_dedicatedvmhosts(inputfile, outdir, service_dir, prefix, config)
    print("\n\nExecute tf_import_commands_dedicatedvmhosts_nonGF.sh script created under each region directory to synch TF with OCI Dedicated VM Hosts\n")

def export_instances(inputfile, outdir, prefix,config,export_regions,ct):
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['instance']
    else:
        service_dir = ""
    compartments = get_compartment_list(ct.ntk_compartment_ids,'Instances')
    print("Enter values for below filters to restrict the export for Instances; Press 'Enter' to use empty value for the filter")
    filter_str1 = "Enter comma separated list of display name patterns of the instances: "
    filter_str2 = "Enter comma separated list of ADs of the instances eg AD1,AD2,AD3: "
    display_name_str = input(filter_str1)
    ad_name_str = input(filter_str2)
    display_names =  list(map(lambda x: x.strip(), display_name_str.split(','))) if display_name_str else None
    ad_names = list(map(lambda x: x.strip(), ad_name_str.split(','))) if ad_name_str else None

    Compute.export_instances(inputfile, outdir, service_dir,config=config, export_compartments=compartments, export_regions=export_regions, ct=ct, display_names = display_names, ad_names = ad_names)
    create_instances(inputfile, outdir, service_dir,prefix, config)
    print("\n\nExecute tf_import_commands_instances_nonGF.sh script created under each region directory to synch TF with OCI Instances\n")


def export_storage():
    options = [Option("Export Block Volumes/Block Backup Policy",export_block_volumes,'Exporting Block Volumes'),
               Option("Export File Systems", export_fss, 'Exporting FSS')]

    options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, prefix, config,export_regions,ct)

def export_block_volumes(inputfile, outdir, prefix,config,export_regions,ct):
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['block-volume']
    else:
        service_dir = ""
    compartments = get_compartment_list(ct.ntk_compartment_ids,'Block Volumes')
    print("Enter values for below filters to restrict the export for Block Volumes; Press 'Enter' to use empty value for the filter")
    filter_str1 = "Enter comma separated list of display name patterns of the Block Volumes: "
    filter_str2 = "Enter comma separated list of ADs of the Block Volumes eg AD1,AD2,AD3: "

    display_name_str = input(filter_str1)
    ad_name_str = input(filter_str2)
    display_names = list(map(lambda x: x.strip(), display_name_str.split(','))) if display_name_str else None
    ad_names = list(map(lambda x: x.strip(), ad_name_str.split(','))) if ad_name_str else None

    Storage.export_blockvolumes(inputfile, outdir, service_dir, _config=config, export_compartments=compartments, export_regions=export_regions, display_names = display_names, ad_names = ad_names,ct=ct)
    create_block_volumes(inputfile, outdir, prefix, config=config)
    print("\n\nExecute tf_import_commands_blockvolumes_nonGF.sh script created under each region directory to synch TF with OCI Block Volume Objects\n")


def export_fss(inputfile, outdir, prefix,config,export_regions,ct):
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['fss']
    else:
        service_dir = ""
    compartments = get_compartment_list(ct.ntk_compartment_ids,'FSS objects')
    Storage.export_fss(inputfile, outdir, service_dir, config=config, export_compartments=compartments, export_regions=export_regions,ct=ct)
    create_fss(inputfile, outdir, prefix, config=config)
    print("\n\nExecute tf_import_commands_fss_nonGF.sh script created under each region directory to synch TF with OCI FSS objects\n")


def export_loadbalancer():
    options = [Option("Export Load Balancers", export_lbr,'Exporting LBR Objects'),
               Option("Export Network Load Balancers", export_nlb,'Exporting NLB Objects')]

    options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, prefix, config, export_regions,ct)

def export_lbr(inputfile, outdir, prefix,config,export_regions,ct):
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['loadbalancer']
    else:
        service_dir = ""
    compartments = get_compartment_list(ct.ntk_compartment_ids,'LBR objects')
    Network.export_lbr(inputfile, outdir, service_dir, _config=config, export_compartments=compartments, export_regions=export_regions,ct=ct)
    create_lb(inputfile, outdir, prefix, config=config)
    print("\n\nExecute tf_import_commands_lbr_nonGF.sh script created under each region directory to synch TF with OCI LBR objects\n")

def export_nlb(inputfile, outdir, prefix,config,export_regions,ct):
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['networkloadbalancer']
    else:
        service_dir = ""
    compartments = get_compartment_list(ct.ntk_compartment_ids,'NLB objects')
    Network.export_nlb(inputfile, outdir, service_dir, _config=config, export_compartments=compartments, export_regions=export_regions,ct=ct)
    create_nlb(inputfile, outdir, prefix, config=config)
    print("\n\nExecute tf_import_commands_nlb_nonGF.sh script created under each region directory to synch TF with OCI NLB objects\n")

def export_databases():
    options = [Option("Export Virtual Machine or Bare Metal DB Systems",export_dbsystems_vm_bm,'Exporting VM and BM DB Systems'),
               Option("Export EXA Infra and EXA VMClusters", export_exa_infra_vmclusters, 'Exporting EXA Infra and EXA VMClusters'),
                Option('Export ADBs', export_adbs, 'Exporting Autonomous Databases')]

    options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, prefix, config, export_regions, ct)

def export_dbsystems_vm_bm(inputfile, outdir, prefix,config,export_regions,ct):
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['dbsystem-vm-bm']
    else:
        service_dir = ""
    compartments = get_compartment_list(ct.ntk_compartment_ids,'VM and BM DB Systems')
    Database.export_dbsystems_vm_bm(inputfile, outdir, service_dir, _config=config, export_compartments=compartments, export_regions= export_regions, ct=ct)
    Database.create_terraform_dbsystems_vm_bm(inputfile, outdir, service_dir, prefix, config=config)
    print("\n\nExecute tf_import_commands_dbsystems-vm-bm_nonGF.sh script created under each region directory to synch TF with DBSystems\n")

def export_exa_infra_vmclusters(inputfile, outdir, prefix,config,export_regions,ct):
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['database-exacs']
    else:
        service_dir = ""
    compartments = get_compartment_list(ct.ntk_compartment_ids,'EXA Infra and EXA VMClusters')
    Database.export_exa_infra(inputfile, outdir, service_dir, _config=config, export_compartments=compartments, export_regions= export_regions, ct=ct)
    Database.export_exa_vmclusters(inputfile, outdir, service_dir, _config=config, export_compartments=compartments, export_regions= export_regions, ct=ct)
    create_exa_infra_vmclusters(inputfile, outdir, service_dir, prefix,config=config)
    print("\n\nExecute tf_import_commands_exa-infra_nonGF.sh and tf_import_commands_exa-vmclusters_nonGF.sh scripts created under each region directory to synch TF with Exa-Infra and Exa-VMClusters\n")


def export_adbs(inputfile, outdir, prefix,config,export_regions,ct):
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['adb']
    else:
        service_dir = ""
    compartments = get_compartment_list(ct.ntk_compartment_ids,'ADBs')
    Database.export_adbs(inputfile, outdir, service_dir, _config=config, export_compartments=compartments, export_regions= export_regions, ct=ct)
    Database.create_terraform_adb(inputfile, outdir, service_dir, prefix, config)
    print("\n\nExecute tf_import_commands_adb_nonGF.sh script created under each region directory to synch TF with OCI ADBs\n")

def export_management_services():
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['managementservices']
    else:
        service_dir = ""
    options = [Option("Export Notifications",export_notifications,'Exporting Notifications'),
               Option("Export Events", export_events,'Exporting Events'),
               Option("Export Alarms", export_alarms, 'Exporting Alarms'),
               Option("Export Service Connectors", export_service_connectors, 'Exporting Service Connectors')]

    options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, service_dir, prefix, config, export_regions,ct)

def export_notifications(inputfile, outdir, service_dir, prefix,config, export_regions,ct):
    compartments = get_compartment_list(ct.ntk_compartment_ids,'Notifications')
    ManagementServices.export_notifications(inputfile, outdir, service_dir, _config=config, export_compartments=compartments, export_regions=export_regions,ct=ct)
    ManagementServices.create_terraform_notifications(inputfile, outdir, service_dir, prefix, config=config)
    print("\n\nExecute tf_import_commands_notifications_nonGF.sh script created under each region directory to synch TF with OCI Notifications\n")

def export_events(inputfile, outdir, service_dir, prefix,config, export_regions,ct):
    compartments = get_compartment_list(ct.ntk_compartment_ids,'Events')
    ManagementServices.export_events(inputfile, outdir, service_dir, _config=config, export_compartments=compartments, export_regions=export_regions,ct=ct)
    ManagementServices.create_terraform_events(inputfile, outdir, service_dir, prefix, config=config)
    print("\n\nExecute tf_import_commands_events_nonGF.sh script created under each region directory to synch TF with OCI Events\n")

def export_alarms(inputfile, outdir, service_dir, prefix,config, export_regions, ct):
    compartments = get_compartment_list(ct.ntk_compartment_ids,'Alarms')
    ManagementServices.export_alarms(inputfile, outdir, service_dir, _config=config, export_compartments=compartments, export_regions=export_regions,ct=ct)
    ManagementServices.create_terraform_alarms(inputfile, outdir,service_dir, prefix, config=config)
    print("\n\nExecute tf_import_commands_alarms_nonGF.sh script created under each region directory to synch TF with OCI Alarms\n")

def export_service_connectors(inputfile, outdir, service_dir, prefix, config, export_regions,ct):
    compartments = get_compartment_list(ct.ntk_compartment_ids,'Service Connectors')
    ManagementServices.export_service_connectors(inputfile, outdir, service_dir, _config=config,export_compartments=compartments, export_regions=export_regions,ct=ct)
    ManagementServices.create_service_connectors(inputfile, outdir, service_dir, prefix, config=config)
    print("\n\nExecute tf_import_commands_serviceconnectors_nonGF.sh script created under each region directory to synch TF with OCI Service Connectors\n")

def export_development_services():
    options = [Option("Export OKE cluster and Nodepools", export_oke, 'Exporting OKE'),
               ]
    options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, prefix, config, export_regions,ct)

def export_oke(inputfile, outdir, prefix,config,export_regions,ct):
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['oke']
    else:
        service_dir = ""
    compartments = get_compartment_list(ct.ntk_compartment_ids,'OKE')
    DeveloperServices.export_oke(inputfile, outdir, service_dir,_config=config, export_compartments=compartments, export_regions=export_regions,ct=ct)
    DeveloperServices.create_terraform_oke(inputfile, outdir, service_dir,prefix, config=config)
    print("\n\nExecute tf_import_commands_oke_nonGF.sh script created under each region directory to synch TF with OKE\n")


def cd3_services():

    options = [
        Option('Fetch Compartments OCIDs to variables file', fetch_compartments,'Fetch Compartments OCIDs'),
        Option('Fetch Protocols to OCI_Protocols', fetch_protocols, 'Fetch Protocols'),
    ]
    options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, outdir, outdir_struct, config=config)

def fetch_protocols(outdir, outdir_struct, config):
    cd3service.fetch_protocols()

################## Create Functions ##########################
def create_identity(execute_all=False):
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['identity']
    else:
        service_dir = ""
    options = [
        Option('Add/Modify/Delete Compartments', Identity.create_terraform_compartments, 'Processing Compartments Tab'),
        Option('Add/Modify/Delete Groups', Identity.create_terraform_groups, 'Processing Groups Tab'),
        Option('Add/Modify/Delete Policies', Identity.create_terraform_policies, 'Processing Policies Tab'),
    ]
    if not execute_all:
        options = show_options(options, quit=True, menu=True, index=1)

    execute_options(options, inputfile, outdir,service_dir, prefix, config=config)


def create_network(execute_all=False):
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['network']
    else:
        service_dir = ""

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
    execute_options(options, inputfile, outdir, service_dir, prefix, config=config, non_gf_tenancy=non_gf_tenancy)

def modify_terraform_network(inputfile, outdir, service_dir,  prefix, non_gf_tenancy, config):
    Network.create_all_tf_objects(inputfile, outdir, service_dir, prefix, config=config, non_gf_tenancy=non_gf_tenancy, modify_network=True)

def create_cis_vcnflow_logs(*args,**kwargs):
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['network']
    else:
        service_dir = ""

    options = [Option(None, ManagementServices.enable_cis_vcnflow_logging, 'Enabling VCN Flow Logs')]
    execute_options(options, inputfile, outdir, service_dir, prefix, config=config)

def export_modify_security_rules(inputfile, outdir, service_dir, prefix, non_gf_tenancy, config):
    execute_all = False
    options = [
        Option('Export Security Rules (From OCI into SecRulesinOCI sheet)', export_security_rules, 'Exporting Security Rules in OCI'),
        Option('Add/Modify/Delete Security Rules (Reads SecRulesinOCI sheet)', Network.modify_terraform_secrules, 'Processing SecRulesinOCI Tab'),
    ]
    if not execute_all:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, service_dir, prefix, config=config, non_gf_tenancy=non_gf_tenancy)

def export_security_rules(inputfile, outdir, prefix, service_dir, config, non_gf_tenancy):
    tempconfig = oci.config.from_file(file_location=config)
    ct.get_network_compartment_ids(tempconfig['tenancy'], "root", config)
    compartments = get_compartment_list(ct.ntk_compartment_ids,'OCI Security Rules')
    Network.export_seclist(inputfile, export_compartments=compartments, export_regions= export_regions, service_dir=service_dir, _config=config, _tf_import_cmd=False, outdir=None,ct=ct)

def export_modify_route_rules(inputfile, outdir, service_dir, prefix, non_gf_tenancy, config):
    execute_all = False
    options = [
        Option('Export Route Rules (From OCI into RouteRulesinOCI sheet)', export_route_rules, 'Exporting Route Rules in OCI'),
        Option('Add/Modify/Delete Route Rules (Reads RouteRulesinOCI sheet)', Network.modify_terraform_routerules, 'Processing RouteRulesinOCI Tab'),
    ]
    if not execute_all:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, service_dir, prefix, config=config, non_gf_tenancy=non_gf_tenancy)

def export_route_rules(inputfile, outdir, service_dir, prefix, config, non_gf_tenancy):
    tempconfig = oci.config.from_file(file_location=config)
    ct.get_network_compartment_ids(tempconfig['tenancy'], "root", config)
    compartments = get_compartment_list(ct.ntk_compartment_ids,'OCI Route Rules')
    Network.export_routetable(inputfile, export_compartments=compartments, export_regions= export_regions,service_dir=service_dir, _config=config, _tf_import_cmd=False, outdir=None,ct=ct)

def export_modify_drg_route_rules(inputfile, outdir, service_dir, prefix, non_gf_tenancy, config):
    execute_all = False
    options = [
        Option('Export DRG Route Rules (From OCI into DRGRouteRulesinOCI sheet)', export_drg_route_rules, 'Exporting DRG Route Rules in OCI'),
        Option('Add/Modify/Delete DRG Route Rules (Reads DRGRouteRulesinOCI sheet)', Network.modify_terraform_drg_routerules, 'Processing DRGRouteRulesinOCI Tab'),
    ]
    if not execute_all:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, service_dir, prefix, config=config, non_gf_tenancy=non_gf_tenancy)

def export_drg_route_rules(inputfile, outdir, service_dir, prefix, config, non_gf_tenancy):
    tempconfig = oci.config.from_file(file_location=config)
    ct.get_network_compartment_ids(tempconfig['tenancy'], "root", config)
    compartments = get_compartment_list(ct.ntk_compartment_ids,'OCI DRG Route Rules')
    Network.export_drg_routetable(inputfile, export_compartments=compartments, export_regions= export_regions,service_dir=service_dir, _config=config, _tf_import_cmd=False, outdir=None,ct=ct)


def export_modify_nsgs(inputfile, outdir, service_dir, prefix, non_gf_tenancy, config):
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['nsg']
    else:
        service_dir = ""

    execute_all = False
    options = [
        Option('Export NSGs (From OCI into NSGs sheet)', export_nsgs, 'Exporting NSGs in OCI'),
        Option('Add/Modify/Delete NSGs (Reads NSGs sheet)', Network.create_terraform_nsg, 'Processing NSGs Tab'),
    ]
    if not execute_all:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, service_dir, prefix, config=config, non_gf_tenancy=non_gf_tenancy)

def export_nsgs(inputfile, outdir, service_dir, prefix, config, non_gf_tenancy):
    tempconfig = oci.config.from_file(file_location=config)
    ct.get_network_compartment_ids(tempconfig['tenancy'], "root", config)
    compartments = get_compartment_list(ct.ntk_compartment_ids,'OCI NSGs')
    Network.export_nsg(inputfile, export_compartments=compartments, export_regions= export_regions,service_dir=service_dir, _config=config, _tf_import_cmd=False, outdir=None,ct=ct)


def create_tags():
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['tagging']
    else:
        service_dir = ""
    options = [Option(None, Governance.create_terraform_tags, 'Processing Tags Tab')]
    execute_options(options, inputfile, outdir, service_dir, prefix, config=config)


def create_compute():
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['dedicated-vm-host']
    else:
        service_dir = ""

    options = [
        Option('Add/Modify/Delete Dedicated VM Hosts', Compute.create_terraform_dedicatedhosts, 'Processing Dedicated VM Hosts Tab'),
        Option('Add/Modify/Delete Instances/Boot Backup Policy', create_instances,''),
    ]
    options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, service_dir,prefix,config)

def create_instances(inputfile, outdir, service_dir,prefix,config):
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['instance']
    else:
        service_dir = ""

    options = [
        Option(None, Compute.create_terraform_instances, 'Processing Instances Tab')
    ]
    execute_options(options, inputfile, outdir, service_dir, prefix,config)

def create_dedicatedvmhosts(inputfile, outdir, service_dir, prefix,config):
    options = [Option(None, Compute.create_terraform_dedicatedhosts, 'Processing Dedicated VM Hosts Tab')]
    execute_options(options, inputfile, outdir, service_dir,prefix,config=config)


def create_storage(execute_all=False):
    options = [
        Option('Add/Modify/Delete Block Volumes/Block Backup Policy', create_block_volumes, ''),
        Option('Add/Modify/Delete File Systems', create_fss, '')]
    options = show_options(options, quit=True, menu=True, index=1)
    if not execute_all:
        execute_options(options, inputfile, outdir, prefix, config)

def create_block_volumes(inputfile, outdir, prefix,config):
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['block-volume']
    else:
        service_dir = ""
    options = [
        Option(None, Storage.create_terraform_block_volumes, 'Processing BlockVolumes Tab')
    ]
    execute_options(options, inputfile, outdir, service_dir, prefix, config=config)

def create_fss(inputfile, outdir, prefix,config):
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['fss']
    else:
        service_dir = ""
    options = [Option(None, Storage.create_terraform_fss, 'Processing FSS Tab')]
    execute_options(options, inputfile, outdir, service_dir, prefix, config=config)


def create_loadbalancer(execute_all=False):
    options = [
        Option('Add/Modify/Delete Load Balancers', create_lb, 'LBaaS'),
        Option('Add/Modify/Delete Network Load Balancers', create_nlb, 'NLB'),
        Option('Enable LBaaS Logs', enable_lb_logs, 'LBaaS Logs')]
    options = show_options(options, quit=True, menu=True, index=1)
    if not execute_all:
        execute_options(options, inputfile, outdir, prefix, config)

def create_lb(inputfile, outdir, prefix, config):
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['loadbalancer']
    else:
        service_dir = ""
    options = [
         Option(None, Network.create_terraform_lbr_hostname_certs, 'Creating LBR'),
         Option(None, Network.create_backendset_backendservers, 'Creating Backend Sets and Backend Servers'),
         Option(None, Network.create_listener, 'Creating Listeners'),
         Option(None, Network.create_path_route_set, 'Creating Path Route Sets'),
         Option(None, Network.create_ruleset, 'Creating Rule Sets'),
    ]
    execute_options(options, inputfile, outdir, service_dir, prefix, config=config)

def enable_lb_logs(inputfile, outdir, prefix, config):
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['loadbalancer']
    else:
        service_dir = ""
    options = [Option(None, ManagementServices.enable_load_balancer_logging, 'Enabling LBaaS Logs')]
    execute_options(options, inputfile, outdir, service_dir, prefix, config=config)

def create_nlb(inputfile, outdir, prefix, config):
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['networkloadbalancer']
    else:
        service_dir = ""
    options = [
         Option(None, Network.create_terraform_nlb_listener, 'Creating NLB and Listeners'),
         Option(None, Network.create_nlb_backendset_backendservers, 'Creating NLB Backend Sets and Backend Servers'),
    ]
    execute_options(options, inputfile, outdir, service_dir, prefix, config=config)

def create_databases(execute_all=False):
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['adb']
    else:
        service_dir = ""
    options = [
        Option('Add/Modify/Delete Virtual Machine or Bare Metal DB Systems', create_terraform_dbsystems_vm_bm, 'Processing DBSystems-VM-BM Tab'),
        Option('Add/Modify/Delete EXA Infra and EXA VM Clusters', create_exa_infra_vmclusters, ''),
        Option('Add/Modify/Delete ADBs', Database.create_terraform_adb, 'Processing ADB Tab'),
    ]
    if not execute_all:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, service_dir, prefix, config=config)

def create_terraform_dbsystems_vm_bm(inputfile, outdir,service_dir, prefix,config):
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['dbsystem-vm-bm']
    else:
        service_dir = ""
    Database.create_terraform_dbsystems_vm_bm(inputfile, outdir, service_dir, prefix, config=config)

def create_exa_infra_vmclusters(inputfile, outdir,service_dir, prefix,config):
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['database-exacs']
    else:
        service_dir = ""
    options = [Option(None, Database.create_terraform_exa_infra, 'Processing Exa-Infra Tab'),
               Option(None, Database.create_terraform_exa_vmclusters, 'Processing Exa-VM-Clusters Tab')]
    execute_options(options, inputfile, outdir, service_dir, prefix, config)

def create_management_services(execute_all=False):
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['managementservices']
    else:
        service_dir = ""
    options = [
        Option("Add/Modify/Delete Notifications", ManagementServices.create_terraform_notifications, 'Setting up Notifications'),
        Option("Add/Modify/Delete Events", ManagementServices.create_terraform_events, 'Setting up Events'),
        Option("Add/Modify/Delete Alarms", ManagementServices.create_terraform_alarms, 'Setting up Alarms'),
        Option("Add/Modify/Delete ServiceConnectors", ManagementServices.create_service_connectors,
               'Setting up SCHs'),
    ]
    if not execute_all:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, service_dir, prefix, config=config)


def create_developer_services(execute_all=False):
    options = [
        Option("Upload current terraform files/state to Resource Manager", create_rm_stack, 'Creating RM Stack'),
        Option("Add/Modify/Delete OKE Cluster and Nodepools", create_oke, 'Creating OKE cluster and Nodepool')
    ]
    if not execute_all:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, prefix, config=config)

def create_rm_stack(inputfile, outdir, prefix, config):
    regions = get_region_list(rm = True)
    DeveloperServices.create_resource_manager(outdir, outdir_struct, prefix, regions, config)

def create_oke(inputfile, outdir, prefix, config):
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['oke']
    else:
        service_dir = ""
    DeveloperServices.create_terraform_oke(inputfile, outdir, service_dir, prefix, config)

def create_cis_features():
    options = [Option('CIS Compliance Checking Script', initiate_cis_scan, 'CIS Compliance Checking'),
               Option("Create Key/Vault, Object Storage Bucket and enable Logging for write events to bucket", create_cis_keyvault_oss_log, 'Creating CIS Key/Vault, Object Storage Bucket and enable Logging for write events to bucket'),
               Option("Create Default Budget",create_cis_budget,'Create Default Budget'),
               Option("Enable Cloud Guard", enable_cis_cloudguard, 'Enable Cloud Guard'),]

    options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, outdir, prefix, config)

def create_cis_keyvault_oss_log(*args,**kwargs):
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['kms']
        service_dir_iam = outdir_struct['identity']
    else:
        service_dir = ""
        service_dir_iam= ""

    region_name = input("Enter region name eg ashburn where you want to create OSS Bucket and Key/Vault: ")
    comp_name = input("Enter name of compartment as it appears in OCI Console: ")

    options = [Option(None, Security.create_cis_keyvault, 'Creating KeyVault'),
               Option(None, Storage.create_cis_oss, 'Creating Object Storage Bucket'),
               Option(None, ManagementServices.enable_cis_oss_logging, 'Enabling Logging for write events to bucket')]
    execute_options(options, outdir, service_dir, service_dir_iam,prefix,region_name, comp_name, config=config)

def create_cis_budget(*args,**kwargs):
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['budget']
    else:
        service_dir = ""

    amount = input("Enter Monthly Budget Amount (in US$): ")
    threshold = input("Enter Threshold Percentage of Budget: ")
    options = [Option(None, Governance.create_cis_budget, 'Creating Budget')]
    execute_options(options, outdir, service_dir, prefix,amount,threshold, config=config)

def enable_cis_cloudguard(*args,**kwargs):
    if len(outdir_struct) != 0:
        service_dir = outdir_struct['cloud-guard']
    else:
        service_dir = ""

    options = [Option(None, Security.enable_cis_cloudguard, 'Enabling Cloud Guard')]
    execute_options(options, outdir, service_dir, prefix,config=config)

def initiate_cis_scan(outdir, prefix, config):
    options = [
        Option("CD3 Image already contains the latest CIS compliance checking script available at the time of cd3 image release.\n   Download latest only if new version of the script is available", start_cis_download, 'Download CIS script'),
        Option("Execute compliance checking script", start_cis_scan, 'Execute CIS script'),
    ]
    options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, outdir, prefix, config)

def start_cis_download(outdir, prefix, config):
    print("Downloading the script file as 'cis_reports.py' at location "+os.getcwd())
    resp = requests.get("https://raw.githubusercontent.com/oracle-quickstart/oci-cis-landingzone-quickstart/main/scripts/cis_reports.py")
    resp_contents = resp.text
    with open("cis_reports.py", "w") as fd:
        fd.write(resp_contents)
    print("Download complete!!")

def start_cis_scan(outdir, prefix, config):
    cmd = "python cis_reports.py"
    user_input = input("Enter command to execute the script. Press Enter to execute {} : ".format(cmd))
    if user_input!='':
        cmd = "{}".format(user_input)
    split = str.split(cmd)

    dirname = prefix + "_cis_report"
    resource = "cis_report"
    out_rep = outdir + '/'+ dirname
    #config = "--config "+ config
    commonTools.backup_file(outdir, resource, dirname)

    if not os.path.exists(out_rep):
        os.makedirs(out_rep)
    else:
        commonTools.backup_file(outdir, resource, out_rep)

    out = ["-c", config, '--report-directory', out_rep]
    cmd = cmd +" "+ out[0] + " "+out[1] + " "+ out[2] + " " +out[3]
    split.extend(out)
    print("Executing: "+cmd)
    print("Scan started!")
    execute(split)

def execute(command):
    export_cmd_windows = "set OCI_CONFIG_HOME="+config
    export_cmd_linux = "export OCI_CONFIG_HOME=" + config
    export_cmd = ""
    if "linux" in sys.platform:
        export_cmd = export_cmd_linux
    elif "win" in sys.platform:
        export_cmd = export_cmd_windows

    if export_cmd == "":
        print("Failed to get OS details. Exiting!!")
        exit()

    split_export_cmd = str.split(export_cmd)
    #subprocess.Popen(split_export_cmd, stdout=subprocess.PIPE,bufsize=1)
    popen = subprocess.Popen(command, stdout=subprocess.PIPE,bufsize=1)
    lines_iterator = iter(popen.stdout.readline, b"")
    while popen.poll() is None:
        for line in lines_iterator:
            nline = line.rstrip()
            print(nline.decode("latin"), end="\r\n", flush=True)# yield line


#Execution starts here
parser = argparse.ArgumentParser(description='Sets Up OCI via TF')
parser.add_argument('propsfile', help="Full Path of properties file containing input variables. eg setUpOCI.properties")
args = parser.parse_args()
config1 = configparser.RawConfigParser()
config1.read(args.propsfile)

#Read Config file Variables
try:
    non_gf_tenancy = config1.get('Default', 'non_gf_tenancy').strip().lower() == 'true'
    inputfile = config1.get('Default','cd3file').strip()
    outdir = config1.get('Default', 'outdir').strip()
    prefix = config1.get('Default', 'prefix').strip()
    config = config1.get('Default', 'config_file').strip() or DEFAULT_LOCATION

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

try:
    outdir_structure = config1.get('Default', 'outdir_structure_file').strip()
except Exception as e:
    outdir_structure = ''

Option = namedtuple('Option', ['name', 'callback', 'text'])
extra = ''

# Pre-work
if not os.path.exists(outdir):
    os.makedirs(outdir)

if (outdir_structure == '' or outdir_structure == "\n"):
    outdir_struct = {}

else:
    if os.path.isfile(outdir_structure):
        outdir_config = configparser.RawConfigParser()
        outdir_config.read(outdir_structure)
        outdir_struct = dict(outdir_config.items("Default"))

    else:
        print("Invalid outdir_structure_file. Please provide correct file path. Exiting... ")
        exit(1)

## Fetch OCI_regions
cd3service = cd3Services()
cd3service.fetch_regions(config)

ct=None
ct = commonTools()

## Check if fetch compartments script needs to be run
run_fetch_script = 0

## Fetch Subscribed Regions
ct.get_subscribedregions(config)
home_region = ct.home_region
if len(outdir_struct.items())==0:
    var_file = f'{outdir}/{home_region}/variables_{home_region}.tf'
else:
    identity_dir = outdir_struct['identity']
    var_file = f'{outdir}/{home_region}/{identity_dir}/variables_{home_region}.tf'

try:
    # read variables file
    with open(var_file, 'r') as f:
        var_data = f.read()
    f.close()
except FileNotFoundError as e:
    exit_menu(f'\nVariables file not found in home region - {home_region}.......Exiting!!!\n')

fetchcompinfo_data = "run_fetch_script=0"
try:
    # read fetchcompinfo.safe
    fetch_comp_file = f'{outdir}/fetchcompinfo.safe'
    with open(fetch_comp_file, 'r') as f:
        fetchcompinfo_data = f.read()
    f.close()

except FileNotFoundError as e:
    fetchcompinfo_data = "run_fetch_script=1"
if "# compartment ocids" in var_data or "run_fetch_script=1" in fetchcompinfo_data:
    run_fetch_script = 1

if (run_fetch_script == 1):
    print("Script to Fetch Compartments OCIDs to variables file has not been executed.")
    user_input = input("Do you want to run it now? (y|n):")
    if(user_input.lower() == 'y'):
        fetch_compartments(outdir,outdir_struct, config=config)
else:
    print("Make sure to execute the script for 'Fetch Compartments OCIDs to variables file' under 'CD3 Services' menu option atleast once before you continue!")

service_dir=''
## Menu Options
if non_gf_tenancy:
    inputs = [
        Option('Export Identity', export_identity, 'Identity'),
        Option('Export Tags', export_tags, 'Tagging'),
        Option('Export Network', export_network, 'Network'),
        Option('Export Compute', export_compute, 'Dedicated VM Hosts and Instances'),
        Option('Export Storage', export_storage, 'Storage'),
        Option('Export Databases', export_databases, 'Databases'),
        Option('Export Load Balancers', export_loadbalancer, 'Load Balancers'),
        Option('Export Management Services', export_management_services, 'Management Services'),
        Option('Export Developer Services', export_development_services, 'Development Services'),
        Option('CD3 Services', cd3_services, 'CD3 Services')
    ]

    #verify_outdir_is_empty()
    print("\nnon_gf_tenancy in properties file is set to true..Export existing OCI objects and Synch with TF state")
    print("We recommend to not have any existing tfvars/tfstate files for export out directory")
    export_regions = get_region_list(rm=False)

    ## Fetch Compartments into dict
    tempconfig = oci.config.from_file(file_location=config)
    print("\nFetching compartment details. Please wait...")
    ct.get_network_compartment_ids(tempconfig['tenancy'], "root", config)

    print("\nChoose appropriate option from below for export:\n")

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
        Option('CIS Compliance Features', create_cis_features, 'CIS Compliance Features'),
        Option('CD3 Services', cd3_services,'CD3 Services')
    ]
    export_regions = ct.all_regions

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