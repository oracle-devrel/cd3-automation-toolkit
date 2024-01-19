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
import SDDC
import Governance
from commonTools import *
from collections import namedtuple
import requests
import subprocess
import datetime,glob,os


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

def get_region_list(rm):
    if rm == False:
        input_region_names = ct.reg_filter
    else:
        input_region_names = ct.orm_reg_filter
    input_region_names = list(map(lambda x: x.strip(), input_region_names.split(','))) if input_region_names else None
    remove_regions = []
    region_list_fetch = []
    #validate input regions
    if (input_region_names is not None):
        for x in range(0, len(input_region_names)):
            if (input_region_names[x].lower() not in ct.all_regions and input_region_names[x].lower()!='global'):
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
        # include global dir for RM stack upload
        if rm == True:
            region_list_fetch.append('global')
    return region_list_fetch

def update_path_list(regions_path=[],service_dirs=[]):
    # Update modified path list
    for current_dir in service_dirs:
        for reg in regions_path:
            path_value = ((outdir + "/" + reg + "/" + current_dir).rstrip('/')).replace("//","/")
            items = glob.glob(path_value + "/*")
            files = [f for f in items if
                     (os.path.isfile(f) and (datetime.datetime.fromtimestamp(os.path.getmtime(f)) >= exec_start_time))]
            if files:
                if path_value not in updated_paths:
                    updated_paths.append(path_value)
                for script_file in files:
                    if script_file.endswith(".sh") and script_file not in import_scripts:
                        import_scripts.append(script_file)

def fetch_compartments(outdir, outdir_struct, ct):
    var_files={}
    var_data = {}
    home_region = ct.home_region
    print("outdir specified should contain region directories and then variables_<region>.tf file inside the region directories eg /cd3user/tenancies/<customer_tenancy_name>/terraform_files")
    print("Verifying out directory and Taking backup of existing variables files...Please wait...")
    print("\nFetching Compartment Info...Please wait...")
    ct.get_network_compartment_ids(config['tenancy'], "root", config, signer)
    ct.all_regions.append('global')
    print("\nWriting to variables files...")
    home_region_services = ['identity', 'tagging', 'budget']
    for region in ct.all_regions:
        # for global directory
        if region == 'global':
            file = f'{outdir}/{region}/rpc/variables_{region}.tf'
            var_files[region] = file
            try:
                # Read variables file data
                with open(file, 'r') as f:
                    var_data[region] = f.read()
            except FileNotFoundError as e:
                print(f'\nVariables file not found in - {region}.......')
                print("Continuing")

        # Fetch variables file inside region directories - single outdir
        elif len(outdir_struct) == 0:
            file = f'{outdir}/{region}/variables_{region}.tf'
            var_files[region]=file
            try:
                # Read variables file data
                with open(file, 'r') as f:
                    var_data[region] = f.read()
            except FileNotFoundError as e:
                print(f'\nVariables file not found in - {region}.......')
                print("Continuing")

        # Fetch variables file inside service directories - separate outdir
        else:
            for k, v in outdir_struct.items():
                if ((k not in home_region_services) or ((k in home_region_services) and region == home_region)) and v != '':
                    file = f'{outdir}/{region}/{v}/variables_{region}.tf'
                    var_files[region + "-" + v] = file
                    try:
                        # Read variables file data
                        with open(file, 'r') as f:
                            var_data[region + "-" + v] = f.read()
                    except FileNotFoundError as e:
                        print(f'\nVariables file not found in - {region}/{v}/.......')
                        print("Continuing")

    compocidsStr = ''
    for k,v in ct.ntk_compartment_ids.items():
        k = commonTools.check_tf_variable(k)
        v = "\"" + v + "\""
        compocidsStr = "\t" + k + " = " + v + "\n" + compocidsStr
    compocidsStr = "\n" + compocidsStr
    finalCompStr = "#START_compartment_ocids#" + compocidsStr +  "\t#compartment_ocids_END#"
    for k, v in var_data.items():
        var_data[k] = re.sub('#START_compartment_ocids#.*?#compartment_ocids_END#', finalCompStr,
                               var_data[k], flags=re.DOTALL)
        # Write variables file data
        with open(var_files[k], "w") as f:
            # Backup the existing Routes tf file
            file = var_files[k]
            shutil.copy(file, file + "_backup")
            f.write(var_data[k])
    print("\nCompartment info written to all variables files under outdir...\n")
    # update fetchcompinfo.safe
    fetch_comp_file = f'{outdir}/fetchcompinfo.safe'
    with open(fetch_comp_file, 'w+') as f:
        f.write('run_fetch_script=0')
    f.close()
    ct.all_regions = ct.all_regions[:-1]

################## Validate Function #########################
def validate_cd3(options=[]):
    choices = []
    choice_items = []
    for opt in options:
        choice_items = []
        if opt in ['Validate Compartments','Validate Groups','Validate Policies','Validate Tags','Validate Networks','Validate DNS','Validate Instances','Validate Block Volumes','Validate FSS','Validate Buckets']:
            if opt == "Validate Networks":
                opt = "Validate Network(VCNs, SubnetsVLANs, DHCP, DRGs)"
            choice_items.append(opt)
        choices.append(choice_items)
    cd3Validator.validate_cd3(choices,inputfile, var_file, prefix, outdir, ct) # config, signer, ct)
    print("Exiting CD3 Validation...")

################## Export Identity ##########################
def export_identityOptions(options=[]):
    service_dirs = []
    for opt in options:
        if opt == "Export Compartments/Groups/Policies":
            export_compartmentPoliciesGroups(inputfile, outdir, service_dir_identity, config,signer, ct)
            service_dirs = [service_dir_identity]
        elif opt == "Export Users":
            export_users(inputfile, outdir, service_dir_identity, config,signer, ct)
            service_dirs = [service_dir_identity]
        elif opt == "Export Network Sources":
            export_networkSources(inputfile, outdir, service_dir_identity, config,signer, ct)
            service_dirs = [service_dir_identity]
    # Update modified path list
    update_path_list(regions_path=[ct.home_region], service_dirs=service_dirs)


def export_compartmentPoliciesGroups(inputfile, outdir, service_dir, config, signer, ct):
    compartments = ct.get_compartment_map(var_file, 'Identity Objects')
    Identity.export_identity(inputfile, outdir, service_dir, config, signer, ct, export_compartments=compartments)
    create_identity(options=['Add/Modify/Delete Compartments','Add/Modify/Delete Groups','Add/Modify/Delete Policies'])
    print("\n\nExecute tf_import_commands_identity_nonGF.sh script created under home region directory to synch TF with OCI Identity objects\n")


def export_users(inputfile, outdir, service_dir, config,signer, ct):
    Identity.Users.export_users(inputfile, outdir, service_dir, config, signer, ct)
    create_identity(options=['Add/Modify/Delete Users'])
    print("\n\nExecute tf_import_commands_users_nonGF.sh script created under home region directory to synch TF with OCI Identity objects\n")


def export_networkSources(inputfile, outdir, service_dir, config, signer, ct):
    compartments = ct.get_compartment_map(var_file, 'Identity Objects')
    Identity.NetworkSources.export_networkSources(inputfile, outdir, service_dir, config, signer, ct)
    create_identity(options=['Add/Modify/Delete Network Sources'])
    print("\n\nExecute tf_import_commands_networkSources_nonGF.sh script created under home region directory to synch TF with OCI Identity objects\n")


def export_tags(options=[]):
    compartments = ct.get_compartment_map(var_file, 'Tagging Objects')
    Governance.export_tags_nongreenfield(inputfile, outdir, service_dir_tagging, config, signer, ct, export_compartments=compartments)
    create_tags()
    print("\n\nExecute tf_import_commands_tags_nonGF.sh script created under home region directory to synch TF with OCI Tags\n")
    # Update modified path list
    update_path_list(regions_path=[ct.home_region], service_dirs=[service_dir_tagging])


def export_network(options=[]):
    service_dirs = []
    for opt in options:
        if opt == "Export all Network Components":
            export_networking(inputfile, outdir, outdir_struct, config, signer, ct, export_regions)
            service_dirs = [service_dir_network, service_dir_nsg, service_dir_vlan]
        if opt == "Export Network components for VCNs/DRGs/DRGRouteRulesinOCI Tabs":
            export_major_objects(inputfile, outdir, service_dir_network, config, signer, ct, export_regions)
            service_dirs.append(service_dir_network) if service_dir_network not in service_dirs else service_dirs
        if opt == "Export Network components for DHCP Tab":
            export_dhcp(inputfile, outdir, service_dir_network, config, signer, ct, export_regions)
            service_dirs.append(service_dir_network) if service_dir_network not in service_dirs else service_dirs
        if opt == "Export Network components for SecRulesinOCI Tab":
            export_secrules(inputfile, outdir, service_dir_network, config, signer, ct, export_regions)
            service_dirs.append(service_dir_network) if service_dir_network not in service_dirs else service_dirs
        if opt == "Export Network components for RouteRulesinOCI Tab":
            export_routerules(inputfile, outdir, service_dir_network, config, signer, ct, export_regions)
            service_dirs.append(service_dir_network) if service_dir_network not in service_dirs else service_dirs
        if opt == "Export Network components for SubnetsVLANs Tab":
            export_subnets_vlans(inputfile, outdir, outdir_struct, config, signer, ct, export_regions)
            service_dirs.append(service_dir_vlan) if service_dir_vlan not in service_dirs else service_dirs
            service_dirs.append(service_dir_network) if service_dir_network not in service_dirs else service_dirs
        if opt == "Export Network components for NSGs Tab":
            export_nsg(inputfile, outdir, service_dir_nsg, config, signer, ct, export_regions)
            service_dirs.append(service_dir_nsg) if service_dir_nsg not in service_dirs else service_dirs

    print("=====================================================================================================================")
    print("NOTE: Make sure to execute tf_import_commands_network_major-objects_nonGF.sh before executing the other scripts.")
    print("=====================================================================================================================")

    # Update modified path list
    regions_path = export_regions.copy()
    regions_path.append("global")
    service_dirs.append("rpc")
    update_path_list(regions_path=regions_path, service_dirs=service_dirs)


def export_networking(inputfile, outdir, service_dir,config, signer, ct, export_regions):
    compartments = ct.get_compartment_map(var_file,'Network Objects')
    Network.export_networking(inputfile, outdir, service_dir,config, signer, ct, export_compartments=compartments, export_regions=export_regions)
    Network.create_major_objects(inputfile, outdir, service_dir_network, prefix, ct, non_gf_tenancy)
    Network.create_rpc_resource(inputfile, outdir, service_dir_network, prefix, auth_mechanism, config_file_path, ct, non_gf_tenancy)
    Network.create_terraform_dhcp_options(inputfile, outdir, service_dir_network, prefix, ct, non_gf_tenancy)
    Network.modify_terraform_secrules(inputfile, outdir, service_dir_network, prefix, ct, non_gf_tenancy)
    Network.modify_terraform_routerules(inputfile, outdir, service_dir_network, prefix, ct, non_gf_tenancy)
    Network.modify_terraform_drg_routerules(inputfile, outdir, service_dir_network, prefix, ct, non_gf_tenancy)
    Network.create_terraform_drg_route(inputfile, outdir, service_dir_network, prefix, ct, non_gf_tenancy,
                    network_connectivity_in_setupoci='', modify_network=False)
    Network.create_terraform_subnet_vlan(inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy, network_vlan_in_setupoci='network')
    Network.create_terraform_subnet_vlan(inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy, network_vlan_in_setupoci='vlan')
    Network.create_terraform_nsg(inputfile, outdir, service_dir_nsg, prefix, ct)

    print("\n\nExecute tf_import_commands_network_*_nonGF.sh script created under each region directory to synch TF with OCI Network objects\n")


def export_major_objects(inputfile, outdir, service_dir_network, config, signer, ct, export_regions):
    compartments = ct.get_compartment_map(var_file,'VCN Major Objects')
    Network.export_major_objects(inputfile, outdir, service_dir_network, config, signer, ct, export_compartments=compartments, export_regions=export_regions)
    Network.export_drg_routetable(inputfile, outdir, service_dir_network, config, signer, ct, export_compartments=compartments, export_regions=export_regions, _tf_import_cmd=True)
    Network.create_major_objects(inputfile, outdir,service_dir_network, prefix, ct, non_gf_tenancy)
    Network.create_rpc_resource(inputfile, outdir, service_dir_network, prefix, auth_mechanism, config_file_path, ct, non_gf_tenancy)
    Network.create_terraform_drg_route(inputfile, outdir, service_dir_network, prefix, ct, non_gf_tenancy,network_connectivity_in_setupoci='', modify_network=False)
    print("\n\nExecute tf_import_commands_network_major-objects_nonGF.sh and tf_import_commands_network_drg_routerules_nonGF.sh scripts created under each region directory to synch TF with OCI Network objects\n")


def export_dhcp(inputfile, outdir, service_dir_network,config,signer,ct,export_regions):
    compartments = ct.get_compartment_map(var_file,'DHCP')
    Network.export_dhcp(inputfile, outdir, service_dir_network,config, signer, ct, export_compartments=compartments, export_regions=export_regions)
    Network.create_terraform_dhcp_options(inputfile, outdir, service_dir_network,prefix, ct, non_gf_tenancy, ct)
    print("\n\nExecute tf_import_commands_network_dhcp_nonGF.sh script created under each region directory to synch TF with OCI Network objects\n")


def export_secrules(inputfile, outdir, service_dir_network,config,signer,ct,export_regions):
    compartments = ct.get_compartment_map(var_file,'SecRulesInOCI')
    Network.export_seclist(inputfile, outdir, service_dir_network, config, signer, ct, export_compartments=compartments, export_regions=export_regions, _tf_import_cmd=True)
    Network.modify_terraform_secrules(inputfile, outdir,service_dir_network, prefix, ct, non_gf_tenancy)
    print("\n\nExecute tf_import_commands_network_secrules_nonGF.sh script created under each region directory to synch TF with OCI Network objects\n")


def export_routerules(inputfile, outdir, service_dir_network,config,signer,ct,export_regions):
    compartments = ct.get_compartment_map(var_file,'RouteRulesInOCI')
    Network.export_routetable(inputfile, outdir, service_dir_network, config, signer, ct, export_compartments=compartments, export_regions=export_regions, _tf_import_cmd=True)
    Network.modify_terraform_routerules(inputfile, outdir, service_dir_network,prefix, ct, non_gf_tenancy)
    print("\n\nExecute tf_import_commands_network_routerules_nonGF.sh script created under each region directory to synch TF with OCI Network objects\n")


def export_subnets_vlans(inputfile, outdir, service_dir,config,signer,ct,export_regions):
    compartments = ct.get_compartment_map(var_file,'Subnets')
    Network.export_subnets_vlans(inputfile, outdir, service_dir,config, signer, ct, export_compartments=compartments, export_regions=export_regions)
    Network.create_terraform_subnet_vlan(inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy, network_vlan_in_setupoci='network')
    Network.create_terraform_subnet_vlan(inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy, network_vlan_in_setupoci='vlan')
    print("\n\nExecute tf_import_commands_network_subnets_nonGF.sh script created under each region directory to synch TF with OCI Network objects")
    print("\nExecute tf_import_commands_network_vlans_nonGF.sh script created under each region directory to synch TF with OCI Network objects\n")


def export_nsg(inputfile, outdir, service_dir_nsg,config,signer,ct,export_regions):
    compartments = ct.get_compartment_map(var_file,'NSGs')
    Network.export_nsg(inputfile, outdir,service_dir_nsg, config,signer,ct, export_compartments=compartments, export_regions=export_regions, _tf_import_cmd=True)
    Network.create_terraform_nsg(inputfile, outdir, service_dir_nsg,prefix, ct)
    print("\n\nExecute tf_import_commands_network_nsg_nonGF.sh script created under each region directory to synch TF with OCI Network objects\n")


def export_compute(options=[]):
    for opt in options:
        if opt == "Export Dedicated VM Hosts":
            export_dedicatedvmhosts(inputfile, outdir, config, signer, ct, export_regions)
        if opt == "Export Instances (excludes instances launched by OKE)":
            export_instances(inputfile, outdir, config, signer, ct, export_regions)


def export_dedicatedvmhosts(inputfile, outdir, config, signer, ct, export_regions):
    compartments = ct.get_compartment_map(var_file,'Dedicated VM Hosts')
    Compute.export_dedicatedvmhosts(inputfile, outdir, service_dir_dedicated_vm_host, config, signer, ct, export_compartments=compartments, export_regions=export_regions)
    create_dedicatedvmhosts(inputfile, outdir, service_dir_dedicated_vm_host, prefix, ct)
    print("\n\nExecute tf_import_commands_dedicatedvmhosts_nonGF.sh script created under each region directory to synch TF with OCI Dedicated VM Hosts\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_dedicated_vm_host])


def export_instances(inputfile, outdir,config,signer, ct, export_regions):
    compartments = ct.get_compartment_map(var_file,'Instances')
    display_name_str = ct.ins_pattern_filter if ct.ins_pattern_filter else None
    ad_name_str = ct.ins_ad_filter if ct.ins_ad_filter else None
    display_names =  list(map(lambda x: x.strip(), display_name_str.split(','))) if display_name_str else None
    ad_names = list(map(lambda x: x.strip(), ad_name_str.split(','))) if ad_name_str else None
    Compute.export_instances(inputfile, outdir, service_dir_instance,config,signer,ct, export_compartments=compartments, export_regions=export_regions, display_names = display_names, ad_names = ad_names)
    create_instances(inputfile, outdir, service_dir_instance,prefix, ct)
    print("\n\nExecute tf_import_commands_instances_nonGF.sh script created under each region directory to synch TF with OCI Instances\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_instance])


def export_storage(options=[]):
    for opt in options:
        if opt == "Export Block Volumes/Block Backup Policy":
            export_block_volumes(inputfile, outdir, config, signer, ct, export_regions)
        if opt == "Export File Systems":
            export_fss(inputfile, outdir, config, signer, ct, export_regions)
        if opt == "Export Object Storage Buckets":
            export_buckets(inputfile, outdir, config, signer, ct, export_regions)


def export_block_volumes(inputfile, outdir,config,signer,ct, export_regions):
    compartments = ct.get_compartment_map(var_file,'Block Volumes')
    display_name_str = ct.bv_pattern_filter if ct.bv_pattern_filter else None
    ad_name_str = ct.bv_ad_filter if ct.bv_ad_filter else None
    display_names = list(map(lambda x: x.strip(), display_name_str.split(','))) if display_name_str else None
    ad_names = list(map(lambda x: x.strip(), ad_name_str.split(','))) if ad_name_str else None
    Storage.export_blockvolumes(inputfile, outdir, service_dir_block_volume, config,signer,ct, export_compartments=compartments, export_regions=export_regions, display_names = display_names, ad_names = ad_names)
    Storage.create_terraform_block_volumes(inputfile, outdir, service_dir_block_volume, prefix, ct)
    print("\n\nExecute tf_import_commands_blockvolumes_nonGF.sh script created under each region directory to synch TF with OCI Block Volume Objects\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_block_volume])


def export_fss(inputfile, outdir,config, signer, ct, export_regions):
    compartments = ct.get_compartment_map(var_file,'FSS objects')
    Storage.export_fss(inputfile, outdir, service_dir_fss, config,signer,ct, export_compartments=compartments, export_regions=export_regions)
    Storage.create_terraform_fss(inputfile, outdir, service_dir_fss, prefix, ct)
    print("\n\nExecute tf_import_commands_fss_nonGF.sh script created under each region directory to synch TF with OCI FSS objects\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_fss])


def export_buckets(inputfile, outdir, config, signer, ct, export_regions):
    compartments = ct.get_compartment_map(var_file, 'Buckets')
    Storage.export_buckets(inputfile, outdir, service_dir_object_storage, config,signer,ct, export_compartments=compartments, export_regions=export_regions)
    Storage.create_terraform_oss(inputfile, outdir, service_dir_object_storage, prefix, ct)
    print("\n\nExecute tf_import_commands_buckets_nonGF.sh script created under each region directory to synch TF with OCI Object Storage Buckets\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_object_storage])


def export_loadbalancer(options=[]):
    for opt in options:
        if opt == "Export Load Balancers":
            export_lbr(inputfile, outdir, config, signer, ct, export_regions)
        if opt == "Export Network Load Balancers":
            export_nlb(inputfile, outdir, config, signer, ct, export_regions)


def export_lbr(inputfile, outdir,config, signer, ct, export_regions):
    compartments = ct.get_compartment_map(var_file,'LBR objects')
    Network.export_lbr(inputfile, outdir, service_dir_loadbalancer, config,signer,ct, export_compartments=compartments, export_regions=export_regions)
    create_lb(inputfile, outdir,service_dir_loadbalancer, prefix, ct)
    print("\n\nExecute tf_import_commands_lbr_nonGF.sh script created under each region directory to synch TF with OCI LBR objects\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_loadbalancer])


def export_nlb(inputfile, outdir,config,signer, ct, export_regions):
    compartments = ct.get_compartment_map(var_file,'NLB objects')
    Network.export_nlb(inputfile, outdir, service_dir_networkloadbalancer, config,signer,ct, export_compartments=compartments, export_regions=export_regions)
    create_nlb(inputfile, outdir,service_dir_networkloadbalancer, prefix, ct)
    print("\n\nExecute tf_import_commands_nlb_nonGF.sh script created under each region directory to synch TF with OCI NLB objects\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_networkloadbalancer])


def export_databases(options=[]):
    for opt in options:
        if opt == "Export Virtual Machine or Bare Metal DB Systems":
            export_dbsystems_vm_bm(inputfile, outdir, config, signer, ct, export_regions)
        if opt == "Export EXA Infra and EXA VMClusters":
            export_exa_infra_vmclusters(inputfile, outdir, config, signer, ct, export_regions)
        if opt == 'Export ADBs':
            export_adbs(inputfile, outdir, config, signer, ct, export_regions)


def export_dbsystems_vm_bm(inputfile, outdir,config,signer, ct,export_regions):
    compartments = ct.get_compartment_map(var_file,'VM and BM DB Systems')
    Database.export_dbsystems_vm_bm(inputfile, outdir, service_dir_dbsystem_vm_bm, config,signer,ct, export_compartments=compartments, export_regions= export_regions)
    Database.create_terraform_dbsystems_vm_bm(inputfile, outdir, service_dir_dbsystem_vm_bm, prefix, ct)
    print("\n\nExecute tf_import_commands_dbsystems-vm-bm_nonGF.sh script created under each region directory to synch TF with DBSystems\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_dbsystem_vm_bm])


def export_exa_infra_vmclusters(inputfile, outdir,config, signer, ct, export_regions):
    compartments = ct.get_compartment_map(var_file,'EXA Infra and EXA VMClusters')
    Database.export_exa_infra(inputfile, outdir, service_dir_database_exacs, config,signer,ct, export_compartments=compartments, export_regions= export_regions)
    Database.export_exa_vmclusters(inputfile, outdir, service_dir_database_exacs, config,signer,ct, export_compartments=compartments, export_regions= export_regions)
    create_exa_infra_vmclusters(inputfile, outdir, service_dir_database_exacs, prefix,ct)
    print("\n\nExecute tf_import_commands_exa-infra_nonGF.sh and tf_import_commands_exa-vmclusters_nonGF.sh scripts created under each region directory to synch TF with Exa-Infra and Exa-VMClusters\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_database_exacs])


def export_adbs(inputfile, outdir,config, signer, ct, export_regions):
    compartments = ct.get_compartment_map(var_file,'ADBs')
    Database.export_adbs(inputfile, outdir, service_dir_adb, config,signer,ct, export_compartments=compartments, export_regions= export_regions)
    Database.create_terraform_adb(inputfile, outdir, service_dir_adb, prefix, ct)
    print("\n\nExecute tf_import_commands_adb_nonGF.sh script created under each region directory to synch TF with OCI ADBs\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_adb])


def export_management_services(options=[]):
    service_dirs = []
    for opt in options:
        if opt == "Export Notifications":
            export_notifications(inputfile, outdir, service_dir_managementservices, config, signer, ct, export_regions)
            service_dirs = [service_dir_managementservices]
        if opt == "Export Events":
            export_events(inputfile, outdir, service_dir_managementservices, config, signer, ct, export_regions)
            service_dirs = [service_dir_managementservices]
        if opt == "Export Alarms":
            export_alarms(inputfile, outdir, service_dir_managementservices, config, signer, ct, export_regions)
            service_dirs = [service_dir_managementservices]
        if opt == "Export Service Connectors":
            export_service_connectors(inputfile, outdir, service_dir_managementservices, config, signer, ct, export_regions)
            service_dirs = [service_dir_managementservices]
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_managementservices])


def export_notifications(inputfile, outdir, service_dir, config, signer, ct, export_regions):
    compartments = ct.get_compartment_map(var_file,'Notifications')
    ManagementServices.export_notifications(inputfile, outdir, service_dir, config,signer,ct, export_compartments=compartments, export_regions=export_regions)
    ManagementServices.create_terraform_notifications(inputfile, outdir, service_dir, ct)
    print("\n\nExecute tf_import_commands_notifications_nonGF.sh script created under each region directory to synch TF with OCI Notifications\n")


def export_events(inputfile, outdir, service_dir, config, signer, ct, export_regions):
    compartments = ct.get_compartment_map(var_file,'Events')
    ManagementServices.export_events(inputfile, outdir, service_dir, config,signer,ct, export_compartments=compartments, export_regions=export_regions)
    ManagementServices.create_terraform_events(inputfile, outdir, service_dir, prefix, ct)
    print("\n\nExecute tf_import_commands_events_nonGF.sh script created under each region directory to synch TF with OCI Events\n")


def export_alarms(inputfile, outdir, service_dir, config, signer, ct, export_regions):
    compartments = ct.get_compartment_map(var_file,'Alarms')
    ManagementServices.export_alarms(inputfile, outdir, service_dir, config,signer,ct,  export_compartments=compartments, export_regions=export_regions)
    ManagementServices.create_terraform_alarms(inputfile, outdir,service_dir, prefix, ct)
    print("\n\nExecute tf_import_commands_alarms_nonGF.sh script created under each region directory to synch TF with OCI Alarms\n")


def export_service_connectors(inputfile, outdir, service_dir, config, signer, ct, export_regions):
    compartments = ct.get_compartment_map(var_file,'Service Connectors')
    ManagementServices.export_service_connectors(inputfile, outdir, service_dir, config,signer,ct, export_compartments=compartments, export_regions=export_regions)
    ManagementServices.create_service_connectors(inputfile, outdir, service_dir, prefix, ct)
    print("\n\nExecute tf_import_commands_serviceconnectors_nonGF.sh script created under each region directory to synch TF with OCI Service Connectors\n")


def export_developer_services(options=[]):
    for opt in options:
        if opt == "Export OKE cluster and Nodepools":
            export_oke(inputfile, outdir, config, signer, ct, export_regions)


def export_oke(inputfile, outdir, config,signer, ct, export_regions):
    compartments = ct.get_compartment_map(var_file,'OKE')
    DeveloperServices.export_oke(inputfile, outdir, service_dir_oke,config,signer,ct, export_compartments=compartments, export_regions=export_regions)
    DeveloperServices.create_terraform_oke(inputfile, outdir, service_dir_oke,prefix, ct)
    print("\n\nExecute tf_import_commands_oke_nonGF.sh script created under each region directory to synch TF with OKE\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_oke])


def export_sddc():
    compartments = ct.get_compartment_map(var_file,'SDDCs')
    SDDC.export_sddc(inputfile, outdir, service_dir_sddc,config,signer,ct, export_compartments=compartments, export_regions=export_regions)
    SDDC.create_terraform_sddc(inputfile, outdir, service_dir_sddc, prefix, ct)
    print("\n\nExecute tf_import_commands_sddcs_nonGF.sh script created under each region directory to synch TF with SDDC\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_sddc])


def export_dns(options=[]):
    service_dirs = []
    for opt in options:
        if opt == "Export DNS Views/Zones/Records":
            export_dns_views_zones_rrsets(inputfile, outdir, service_dir_dns, config, signer, ct, export_regions)
            service_dirs = [service_dir_dns]
        if opt == "Export DNS Resolvers":
            export_dns_resolvers(inputfile, outdir, service_dir_dns, config, signer, ct, export_regions)
            service_dirs = [service_dir_dns]
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=service_dirs)


def export_dns_views_zones_rrsets(inputfile, outdir, service_dir, config, signer, ct, export_regions):
    compartments = ct.get_compartment_map(var_file, 'DNS Views ,attached zones and rrsets')
    dns_filter = None
    if ct.default_dns:
        if ct.default_dns.lower() == "false":
            dns_filter = "n"
        if ct.default_dns.lower() == "true":
            dns_filter = "y"

    dns_filter = dns_filter if dns_filter else None
    Network.export_dns_views_zones_rrsets(inputfile, outdir, service_dir, config, signer, ct, dns_filter=dns_filter, export_compartments=compartments, export_regions=export_regions)
    create_terraform_dns(inputfile, outdir, service_dir, prefix, ct)

def export_dns_resolvers(inputfile, outdir, service_dir, config, signer, ct, export_regions):
    compartments = ct.get_compartment_map(var_file, 'DNS Resolvers')
    Network.export_dns_resolvers(inputfile, outdir, service_dir, config, signer, ct, export_compartments=compartments, export_regions=export_regions)
    Network.create_terraform_dns_resolvers(inputfile, outdir, service_dir, prefix, ct)


def cd3_services(options=[]):
    for opt in options:
        if opt == 'Fetch Compartments OCIDs to variables file':
            fetch_compartments(outdir, outdir_struct, ct)
        if opt == 'Fetch Protocols to OCI_Protocols':
            fetch_protocols(outdir, outdir_struct, ct)


def fetch_protocols(outdir, outdir_struct, ct):
    cd3service.fetch_protocols()

################## Create Functions ##########################
def create_identity(options=[]):
    service_dirs = []
    for opt in options:
        if opt == 'Add/Modify/Delete Compartments':
            Identity.create_terraform_compartments(inputfile, outdir,service_dir_identity, prefix, ct)
            service_dirs = [service_dir_identity]
        if opt == 'Add/Modify/Delete Groups':
            Identity.create_terraform_groups(inputfile, outdir,service_dir_identity, prefix, ct)
            service_dirs = [service_dir_identity]
        if opt == 'Add/Modify/Delete Policies':
            Identity.create_terraform_policies(inputfile, outdir,service_dir_identity, prefix, ct)
            service_dirs = [service_dir_identity]
        if opt == 'Add/Modify/Delete Users':
            Identity.Users.create_terraform_users(inputfile, outdir,service_dir_identity, prefix, ct)
            service_dirs = [service_dir_identity]
        if opt == 'Add/Modify/Delete Network Sources':
            Identity.NetworkSources.create_terraform_networkSources(inputfile, outdir,service_dir_identity, prefix, ct)
            service_dirs = [service_dir_identity]
    # Update modified path list
    update_path_list(regions_path=[ct.home_region], service_dirs=[service_dir_identity])


def create_tags():
    Governance.create_terraform_tags(inputfile, outdir, service_dir_tagging, prefix, ct)
    # Update modified path list
    update_path_list(regions_path=[ct.home_region], service_dirs=[service_dir_tagging])


def create_network(options=[], sub_options=[]):
    service_dirs = []
    for opt in options:
        if opt == 'Create Network':
            Network.create_all_tf_objects(inputfile, outdir, outdir_struct, prefix, ct, non_gf_tenancy=non_gf_tenancy)
            service_dirs = [service_dir_network, service_dir_nsg, service_dir_vlan]
        if opt == 'Modify Network':
            modify_terraform_network(inputfile, outdir, outdir_struct, prefix, ct, non_gf_tenancy=non_gf_tenancy)
            service_dirs.append(service_dir_network) if service_dir_network not in service_dirs else service_dirs
        if opt == 'Security Rules':
            export_modify_security_rules(sub_options, inputfile, outdir, service_dir_network, prefix, ct, non_gf_tenancy=non_gf_tenancy)
            service_dirs.append(service_dir_network) if service_dir_network not in service_dirs else service_dirs
        if opt == 'Route Rules':
            export_modify_route_rules(sub_options, inputfile, outdir, service_dir_network, prefix, ct, non_gf_tenancy=non_gf_tenancy)
            service_dirs.append(service_dir_network) if service_dir_network not in service_dirs else service_dirs
        if opt == 'DRG Route Rules':
            export_modify_drg_route_rules(sub_options, inputfile, outdir, service_dir_network, prefix, ct, non_gf_tenancy=non_gf_tenancy)
            service_dirs.append(service_dir_network) if service_dir_network not in service_dirs else service_dirs
        if opt == 'Network Security Groups':
            export_modify_nsgs(sub_options, inputfile, outdir, service_dir_nsg, prefix, ct, non_gf_tenancy=non_gf_tenancy)
            service_dirs.append(service_dir_nsg) if service_dir_nsg not in service_dirs else service_dirs
        if opt == 'Add/Modify/Delete VLANs':
            create_vlans(inputfile, outdir, outdir_struct, prefix, ct, non_gf_tenancy=non_gf_tenancy)
            service_dirs.append(service_dir_vlan) if service_dir_vlan not in service_dirs else service_dirs
            service_dirs.append(service_dir_network) if service_dir_network not in service_dirs else service_dirs
        if opt == 'Customer Connectivity':
            create_drg_connectivity(inputfile, outdir, service_dir_network, prefix, ct, non_gf_tenancy=non_gf_tenancy)
            service_dirs.append(service_dir_network) if service_dir_network not in service_dirs else service_dirs
    # Update modified path list
    regions_path = subscribed_regions.copy()
    regions_path.append("global")
    service_dirs.append("rpc")
    update_path_list(regions_path=regions_path, service_dirs=service_dirs)


def modify_terraform_network(inputfile, outdir, service_dir,  prefix, ct, non_gf_tenancy):
    Network.create_all_tf_objects(inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy=non_gf_tenancy,  modify_network=True, )

def export_modify_security_rules(sub_options,inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy):
    for opt in sub_options:
        if opt == 'Export Security Rules (From OCI into SecRulesinOCI sheet)':
            export_security_rules(inputfile, outdir, service_dir, config, signer, ct, non_gf_tenancy=non_gf_tenancy)
        if opt == 'Add/Modify/Delete Security Rules (Reads SecRulesinOCI sheet)':
            Network.modify_terraform_secrules(inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy)

def export_security_rules(inputfile, outdir, service_dir, config, signer, ct, non_gf_tenancy):
    compartments = ct.get_compartment_map(var_file, 'OCI Security Rules')
    Network.export_seclist(inputfile, outdir, service_dir, config, signer, ct, export_compartments=compartments, export_regions= export_regions, _tf_import_cmd=False)

def export_modify_route_rules(sub_options,inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy):
    execute_all = False
    for opt in sub_options:
        if opt == 'Export Route Rules (From OCI into RouteRulesinOCI sheet)':
            export_route_rules(inputfile, outdir, service_dir, config, signer, ct, non_gf_tenancy=non_gf_tenancy)
        if opt == 'Add/Modify/Delete Route Rules (Reads RouteRulesinOCI sheet)':
            Network.modify_terraform_routerules(inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy)


def export_route_rules(inputfile, outdir, service_dir, config, signer, ct, non_gf_tenancy):
    compartments = ct.get_compartment_map(var_file, 'OCI Route Rules')
    Network.export_routetable(inputfile, outdir, service_dir, config, signer, ct, export_compartments=compartments, export_regions= export_regions, _tf_import_cmd=False)

def export_modify_drg_route_rules(sub_options, inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy):
    execute_all = False
    for opt in sub_options:
        if opt == 'Export DRG Route Rules (From OCI into DRGRouteRulesinOCI sheet)':
            export_drg_route_rules(inputfile, outdir, service_dir, config, signer, ct, non_gf_tenancy=non_gf_tenancy)
        if opt == 'Add/Modify/Delete DRG Route Rules (Reads DRGRouteRulesinOCI sheet)':
            Network.modify_terraform_drg_routerules(inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy)


def export_drg_route_rules(inputfile, outdir, service_dir, config, signer, ct, non_gf_tenancy):
    compartments = ct.get_compartment_map(var_file,'OCI DRG Route Rules')
    Network.export_drg_routetable(inputfile, outdir, service_dir, config, signer, ct, export_compartments=compartments, export_regions= export_regions, _tf_import_cmd=False)


def export_modify_nsgs(sub_options, inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy):
    execute_all = False
    for opt in sub_options:
        if opt == 'Export NSGs (From OCI into NSGs sheet)':
            export_nsgs(inputfile, outdir, service_dir, prefix, ct)
        if opt == 'Add/Modify/Delete NSGs (Reads NSGs sheet)':
           Network.create_terraform_nsg(inputfile, outdir, service_dir, prefix, ct)

def export_nsgs(inputfile, outdir, service_dir, prefix, ct):
    compartments = ct.get_compartment_map(var_file,'OCI NSGs')
    Network.export_nsg(inputfile, outdir, service_dir, config, signer, ct, export_compartments=compartments, export_regions= export_regions, _tf_import_cmd=False)

def create_vlans(inputfile, outdir, service_dir,  prefix,ct, non_gf_tenancy, network_vlan_in_setupoci='vlan'):
    Network.create_terraform_subnet_vlan(inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy=non_gf_tenancy, network_vlan_in_setupoci='vlan',modify_network=True)
    Network.create_terraform_route(inputfile, outdir, service_dir_network, prefix, ct, non_gf_tenancy=non_gf_tenancy, network_vlan_in_setupoci='vlan',modify_network=True)

def create_drg_connectivity(inputfile, outdir, service_dir,  prefix, ct, non_gf_tenancy,network_vlan_in_setupoci='vlan'):
    execute_all = False
    create_rpc( inputfile, outdir, service_dir, service_dir, prefix, auth_mechanism, config_file_path, ct, non_gf_tenancy=non_gf_tenancy)

def create_rpc(inputfile, outdir, service_dir, service_dir_network, prefix, auth_mechanism, config_file_path, ct, non_gf_tenancy):
    Network.create_rpc_resource(inputfile, outdir, service_dir, prefix, auth_mechanism, config_file_path, ct, non_gf_tenancy=non_gf_tenancy)
    Network.create_terraform_drg_route(inputfile, outdir, service_dir_network, prefix, non_gf_tenancy=non_gf_tenancy, ct=ct, network_connectivity_in_setupoci='connectivity', modify_network=True)

def create_compute(options=[]):
    service_dirs = []
    for opt in options:
        if opt == 'Add/Modify/Delete Dedicated VM Hosts':
            create_dedicatedvmhosts(inputfile, outdir, service_dir_dedicated_vm_host,prefix, ct)
            service_dirs.append(service_dir_dedicated_vm_host) if service_dir_dedicated_vm_host not in service_dirs else service_dirs

        if opt == 'Add/Modify/Delete Instances/Boot Backup Policy':
            create_instances(inputfile, outdir, service_dir_instance,prefix, ct)
            service_dirs.append(service_dir_instance) if service_dir_instance not in service_dirs else service_dirs
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=service_dirs)


def create_instances(inputfile, outdir, service_dir,prefix,ct):
    Compute.create_terraform_instances(inputfile, outdir, service_dir, prefix, ct)


def create_dedicatedvmhosts(inputfile, outdir, service_dir, prefix,ct):
    Compute.create_terraform_dedicatedhosts(inputfile, outdir, service_dir,prefix, ct)


def create_storage(options=[]):
    service_dirs = []
    for opt in options:
        if opt == 'Add/Modify/Delete Block Volumes/Block Backup Policy':
            Storage.create_terraform_block_volumes(inputfile, outdir, service_dir_block_volume, prefix, ct)
            service_dirs.append(service_dir_block_volume) if service_dir_block_volume not in service_dirs else service_dirs
        if opt == 'Add/Modify/Delete File Systems':
            Storage.create_terraform_fss(inputfile, outdir, service_dir_fss, prefix, ct)
            service_dirs.append(service_dir_fss) if service_dir_fss not in service_dirs else service_dirs
        if opt == 'Add/Modify/Delete Object Storage Buckets':
            Storage.create_terraform_oss( inputfile, outdir, service_dir_object_storage, prefix, ct)
            service_dirs.append(service_dir_object_storage) if service_dir_object_storage not in service_dirs else service_dirs
        #Option('Enable Object Storage Buckets Write Logs', create_cis_oss_logs, '')
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=service_dirs)


def create_loadbalancer(options=[]):
    service_dirs = []
    for opt in options:
        if opt == 'Add/Modify/Delete Load Balancers':
            create_lb(inputfile, outdir,service_dir_loadbalancer, prefix, ct)
            service_dirs.append(service_dir_loadbalancer) if service_dir_loadbalancer not in service_dirs else service_dirs
        if opt == 'Add/Modify/Delete Network Load Balancers':
            create_nlb(inputfile, outdir,service_dir_networkloadbalancer, prefix, ct)
            service_dirs.append(service_dir_networkloadbalancer) if service_dir_networkloadbalancer not in service_dirs else service_dirs
        #Option('Enable LBaaS Logs', enable_lb_logs, 'LBaaS Logs')
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=service_dirs)


def create_lb(inputfile, outdir,service_dir, prefix, ct):
    Network.create_terraform_lbr_hostname_certs(inputfile, outdir, service_dir, prefix, ct)
    Network.create_backendset_backendservers(inputfile, outdir, service_dir, prefix, ct)
    Network.create_listener(inputfile, outdir, service_dir, prefix, ct)
    Network.create_path_route_set(inputfile, outdir, service_dir, prefix, ct)
    Network.create_ruleset(inputfile, outdir, service_dir, prefix, ct)


def create_nlb(inputfile, outdir,service_dir, prefix, ct):
    Network.create_terraform_nlb_listener(inputfile, outdir, service_dir, prefix, ct)
    Network.create_nlb_backendset_backendservers(inputfile, outdir, service_dir, prefix, ct)


def create_databases(options=[]):
    service_dirs = []
    for opt in options:
        if opt == 'Add/Modify/Delete Virtual Machine or Bare Metal DB Systems':
            Database.create_terraform_dbsystems_vm_bm(inputfile, outdir, service_dir_dbsystem_vm_bm, prefix, ct)
            service_dirs.append(service_dir_dbsystem_vm_bm) if service_dir_dbsystem_vm_bm not in service_dirs else service_dirs
        if opt == 'Add/Modify/Delete EXA Infra and EXA VM Clusters':
            create_exa_infra_vmclusters(inputfile, outdir,service_dir_database_exacs, prefix,ct)
            service_dirs.append(service_dir_database_exacs) if service_dir_database_exacs not in service_dirs else service_dirs
        if opt == 'Add/Modify/Delete ADBs':
            Database.create_terraform_adb(inputfile, outdir, service_dir_adb, prefix, ct)
            service_dirs.append(service_dir_adb) if service_dir_adb not in service_dirs else service_dirs
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=service_dirs)

def create_exa_infra_vmclusters(inputfile, outdir,service_dir, prefix,ct):
    Database.create_terraform_exa_infra(inputfile, outdir, service_dir, prefix, ct)
    Database.create_terraform_exa_vmclusters(inputfile, outdir, service_dir, prefix, ct)

def create_management_services(options=[]):
    service_dirs = []
    for opt in options:
        if opt == "Add/Modify/Delete Notifications":
            ManagementServices.create_terraform_notifications(inputfile, outdir, service_dir_managementservices, prefix, ct)
            service_dirs = [service_dir_managementservices]
        if opt == "Add/Modify/Delete Events":
            ManagementServices.create_terraform_events(inputfile, outdir, service_dir_managementservices, prefix, ct)
            service_dirs = [service_dir_managementservices]
        if opt == "Add/Modify/Delete Alarms":
            ManagementServices.create_terraform_alarms(inputfile, outdir, service_dir_managementservices, prefix, ct)
            service_dirs = [service_dir_managementservices]
        if opt == "Add/Modify/Delete ServiceConnectors":
            ManagementServices.create_service_connectors(inputfile, outdir, service_dir_managementservices, prefix, ct)
            service_dirs = [service_dir_managementservices]

    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_managementservices])


def create_developer_services(options=[]):
    for opt in options:
        if opt == "Upload current terraform files/state to Resource Manager":
            create_rm_stack(inputfile, outdir, prefix, auth_mechanism, config_file_path,ct)
        if opt == "Add/Modify/Delete OKE Cluster and Nodepools":
            create_oke(inputfile, outdir, prefix, auth_mechanism, config_file_path,ct)


def create_rm_stack(inputfile, outdir, prefix, auth_mechanism, config_file, ct):
    regions = get_region_list(rm = True)
    DeveloperServices.create_resource_manager(outdir,var_file, outdir_struct, prefix, auth_mechanism, config_file, ct, regions)

def create_oke(inputfile, outdir, prefix, auth_mechanism, config_file, ct):
    DeveloperServices.create_terraform_oke(inputfile, outdir, service_dir_oke, prefix, ct)
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_oke])


def create_sddc():
    SDDC.create_terraform_sddc(inputfile, outdir, service_dir_sddc, prefix, ct)
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_sddc])


def create_dns(options=[]):
    service_dirs = []
    for opt in options:
        if opt == 'Add/Modify/Delete DNS Views/Zones/Records':
            create_terraform_dns(inputfile, outdir, service_dir_dns, prefix, ct)
            service_dirs = [service_dir_dns]
        if opt == 'Add/Modify/Delete DNS Resolvers':
            Network.create_terraform_dns_resolvers(inputfile, outdir, service_dir_dns, prefix, ct)
            service_dirs = [service_dir_dns]
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=service_dirs)


def create_terraform_dns(inputfile, outdir, service_dir, prefix, ct):
    Network.create_terraform_dns_views(inputfile, outdir, service_dir, prefix, ct)
    Network.create_terraform_dns_zones(inputfile, outdir, service_dir, prefix, ct)
    Network.create_terraform_dns_rrsets(inputfile, outdir, service_dir, prefix, ct)

def create_logging(options=[]):
    service_dirs = []
    for opt in options:
        if opt == 'Enable VCN Flow Logs':
            ManagementServices.enable_cis_vcnflow_logging(inputfile, outdir, service_dir_network, prefix, ct)
            service_dirs.append(service_dir_network) if service_dir_network not in service_dirs else service_dirs
        if opt == 'Enable LBaaS Logs':
            ManagementServices.enable_load_balancer_logging(inputfile, outdir, service_dir_loadbalancer, prefix, ct)
            service_dirs.append(service_dir_loadbalancer) if service_dir_loadbalancer not in service_dirs else service_dirs
        if opt == 'Enable Object Storage Buckets Write Logs':
            ManagementServices.enable_cis_oss_logging(inputfile, outdir, service_dir_object_storage, prefix, ct)
            service_dirs.append(service_dir_object_storage) if service_dir_object_storage not in service_dirs else service_dirs

    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=service_dirs)


def create_cis_features(options=[], sub_options=[]):
    service_dirs = []
    for opt in options:
        if opt == 'CIS Compliance Checking Script':
            initiate_cis_scan(sub_options,outdir, prefix, config_file_path)
        if opt == "Create Key/Vault":
            Security.create_cis_keyvault(outdir, service_dir_kms, service_dir_identity, prefix, ct, ct.vault_region,
                                         ct.vault_comp)
            service_dir = ct.vault_region+"/"+service_dir_identity
            service_dirs.append(service_dir) if service_dir not in service_dirs else service_dirs
        if opt == "Create Default Budget":
            Governance.create_cis_budget(outdir, service_dir_budget, prefix, ct, ct.budget_amount, ct.budget_threshold)
            service_dir = ct.home_region + "/" + service_dir_budget
            service_dirs.append(service_dir) if service_dir not in service_dirs else service_dirs
        if opt == "Enable Cloud Guard":
            Security.enable_cis_cloudguard(outdir, service_dir_cloud_guard, prefix, ct, ct.cg_region)
            service_dir = ct.cg_region + "/" + service_dir_cloud_guard
            service_dirs.append(service_dir) if service_dir not in service_dirs else service_dirs

    # Update modified path list
    update_path_list(regions_path=[""], service_dirs=service_dirs)


def initiate_cis_scan(sub_options,outdir, prefix, config_file):
    for opt in sub_options:
        if opt == "CD3 Image already contains the latest CIS compliance checking script available at the time of cd3 image release. Download latest only if new version of the script is available":
            start_cis_download(outdir, prefix, config_file)
        if opt == "Execute compliance checking script":
            start_cis_scan(outdir, prefix, config_file)

def start_cis_download(outdir, prefix, config_file):
    print("Downloading the script file as 'cis_reports.py' at location "+os.getcwd())
    resp = requests.get("https://raw.githubusercontent.com/oracle-quickstart/oci-cis-landingzone-quickstart/main/scripts/cis_reports.py")
    resp_contents = resp.text
    with open("cis_reports.py", "w", encoding="utf-8") as fd:
        fd.write(resp_contents)
    print("Download complete!!")

def start_cis_scan(outdir, prefix, config_file):
    cmd = "python cis_reports.py"
    #user_input = input("Enter command to execute the script. Press Enter to execute {} : ".format(cmd))
    #if user_input!='':
    #    cmd = "{}".format(user_input)
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

    out = ["-c", config_file, '--report-directory', out_rep]
    cmd = cmd +" "+ out[0] + " "+out[1] + " "+ out[2] + " " +out[3]
    split.extend(out)
    print("Executing: "+cmd)
    print("Scan started!")
    execute(split, config_file)

def execute(command,config_file):
    export_cmd_windows = "set OCI_CONFIG_HOME="+config_file
    export_cmd_linux = "export OCI_CONFIG_HOME=" + config_file
    export_cmd = ""
    if "linux" in sys.platform:
        export_cmd = export_cmd_linux
    elif "win" in sys.platform:
        export_cmd = export_cmd_windows

    if export_cmd == "":
        print("Failed to get OS details. Exiting!!")
        exit(1)

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
parser.add_argument('--main_options', default="")
parser.add_argument('--sub_options', default="")
parser.add_argument('--sub_child_options', default="")
parser.add_argument('--add_filter', default=None)
args = parser.parse_args()
setUpOCI_props = configparser.RawConfigParser()
setUpOCI_props.read(args.propsfile)
main_options = args.main_options.split(",")
sub_options = args.sub_options.split(",")
sub_child_options = args.sub_child_options.split(",")

#Read Config file Variables
try:
    workflow_type = setUpOCI_props.get('Default', 'workflow_type').strip().lower()

    if (workflow_type == 'export_resources'):
        non_gf_tenancy = True
    else:
        non_gf_tenancy = False

    inputfile = setUpOCI_props.get('Default','cd3file').strip()
    outdir = setUpOCI_props.get('Default', 'outdir').strip()
    prefix = setUpOCI_props.get('Default', 'prefix').strip()
    auth_mechanism = setUpOCI_props.get('Default', 'auth_mechanism').strip().lower()
    config_file_path = setUpOCI_props.get('Default', 'config_file').strip() or DEFAULT_LOCATION

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
    outdir_structure = setUpOCI_props.get('Default', 'outdir_structure_file').strip()
except Exception as e:
    outdir_structure = ''

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

## Authenticate Params
ct=None
ct = commonTools()
config,signer = ct.authenticate(auth_mechanism, config_file_path)

# Set Export filters
export_filters = args.add_filter.split("@") if args.add_filter else []
ct.get_export_filters(export_filters)

## Fetch OCI_regions
cd3service = cd3Services()
cd3service.fetch_regions(config,signer)

## Check if fetch compartments script needs to be run
run_fetch_script = 0

## Fetch Subscribed Regions
subscribed_regions = ct.get_subscribedregions(config,signer)
home_region = ct.home_region

# Set service directories as per outdir_structure file
# Add service name from outdir_structure_file to dir_services here
dir_services = ["identity","tagging","network","loadbalancer","networkloadbalancer","vlan","nsg","instance",
                "block-volume","dedicated-vm-host","adb","dbsystem-vm-bm","database-exacs","fss","oke","sddc",
                "cloud-guard","managementservices","budget","kms","object-storage","dns"]
if len(outdir_struct.items())==0:
    for item in dir_services:
        varname = "service_dir_" + str(item.replace("-", "_")).strip()
        exec(varname + "= \"\"")
else:
    for key,value in outdir_struct.items():
        varname = "service_dir_"+str(key.replace("-","_")).strip()
        exec(varname + "= value")

var_file = (f'{outdir}/{home_region}/{service_dir_identity}/variables_{home_region}.tf').replace('//','/')

try:
    # read variables file
    with open(var_file, 'r') as f:
        var_data = f.read()
    f.close()
except FileNotFoundError as e:
    exit_menu(f'\nVariables file not found in home region - {home_region}.......Exiting!!!\n')

## Check for the fetch compartment status
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
    print("Script to Fetch Compartments OCIDs to variables file has not been executed. Running it now.")
    fetch_compartments(outdir,outdir_struct, ct)
else:
    print("Make sure to execute the script for 'Fetch Compartments OCIDs to variables file' under 'CD3 Services' menu option at-least once before you continue!")
global updated_paths
global import_scripts
updated_paths = []
import_scripts = []
exec_start_time = datetime.datetime.now()


## Menu Options
if non_gf_tenancy:
    print("\nworkflow_type set to export_resources. Export existing OCI objects and Synch with TF state")
    print("We recommend to not have any existing tfvars/tfstate files for export out directory")
    export_regions = get_region_list(rm=False)
    for option in main_options:
        if option == 'Export Identity':
            export_identityOptions(options=sub_options)
        if option == 'Export Tags':
            export_tags(options=sub_options)
        if option == 'Export Network':
            export_network(options=sub_options)
        if option == 'Export DNS Management':
            export_dns(options=sub_options)
        if option == 'Export Compute':
            export_compute(options=sub_options)
        if option == 'Export Storage':
            export_storage(options=sub_options)
        if option == 'Export Databases':
            export_databases(options=sub_options)
        if option == 'Export Load Balancers':
            export_loadbalancer(options=sub_options)
        if option == 'Export Management Services':
            export_management_services(options=sub_options)
        if option == 'Export Developer Services':
            export_developer_services(options=sub_options)
        if option == 'Export Software-Defined Data Centers - OCVS':
            export_sddc()
        if option == 'CD3 Services':
            cd3_services(options=sub_options)
else:
    export_regions = ct.all_regions
    for option in main_options:
        if option == 'Validate CD3':
            validate_cd3(options=sub_options)
        if option == 'Identity':
            create_identity(options=sub_options)
        if option == 'Tags':
            create_tags()
        if option == 'Network':
            create_network(options=sub_options, sub_options=sub_child_options)
        if option == 'DNS Management':
            create_dns(options=sub_options)
        if option == 'Compute':
            create_compute(options=sub_options)
        if option == 'Storage':
            create_storage(options=sub_options)
        if option == 'Database':
            create_databases(options=sub_options)
        if option == 'Load Balancers':
            create_loadbalancer(options=sub_options)
        if option == 'Management Services':
            create_management_services(options=sub_options)
        if option == 'Developer Services':
            create_developer_services(options=sub_options)
        if option == 'Logging Services':
            create_logging(options=sub_options)
        if option == 'Software-Defined Data Centers - OCVS':
            create_sddc()
        if option == 'CIS Compliance Features':
            create_cis_features(options=sub_options,sub_options=sub_child_options)
        if option == 'CD3 Services':
            cd3_services(options=sub_options)

# write updated paths to a file
updated_paths_file = f'{outdir}/updated_paths.safe'
with open(updated_paths_file, 'w+') as f:
    for item in updated_paths:
        f.write(str(item).replace('//','/')+"\n")
f.close()
import_scripts_file = f'{outdir}/import_scripts.safe'
with open(import_scripts_file, 'w+') as f:
    for item in import_scripts:
        f.write(str(item).replace('//','/')+"\n")
f.close()
