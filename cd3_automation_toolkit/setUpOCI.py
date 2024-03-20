import argparse
import configparser
import Database
import Identity
import Compute
import ManagementServices
import DeveloperServices
import Security
import cd3Validator
import cd3FirewallValidator
import Storage
import Network
import SDDC
import Governance
from commonTools import *
from collections import namedtuple
import requests
import subprocess
import datetime,glob,os

def show_firewall_options(options, quit=False, menu=False, extra=None, index=0):
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
    a = str(len(options))
    b = 1
    user_input1 = input('Do you wish to run all the above options [1-' + a +'] ("y/n"): ')
    if user_input1 == 'y':
        mylist = []
        a = int(a)
        while b <= a:
            mylist.append(b)
            b += 1
        try:
            return [options[int(choice)-index] for choice in mylist]
        except IndexError as ie:
            print("\nInvalid Option.....Exiting!!")
            exit(1)
        except ValueError as ie:
            print("\nInvalid Input.....Try again!!\n")
            options = show_options(inputs, quit=True, index=index)
            return options
    elif user_input1 == 'n':
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
    else:
        print("\nInvalid choice.....type 'y' or 'n'!!\n")
        exit(0)


def match_options(options, prim_options):
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
            if int(choice)-index < 0 :
                print("\nInvalid Option.....Exiting!!")
                exit(1)
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
            if option.name in ['Security Rules', 'Route Rules', 'DRG Route Rules', 'Network Security Groups','Customer Connectivity','CIS Compliance Checking Script'] and devops:
                with section(option.text):
                    option.callback(*args, **kwargs,sub_options=sub_child_options)
            else:
                with section(option.text):
                    option.callback(*args, **kwargs)

def get_region_list(rm):
    if rm == False:
        if devops:
            input_region_names = ct.reg_filter
        else:
            resource_name = 'OCI resources'
            region_list_str = "\nEnter region (comma separated without spaces if multiple) for which you want to export {}; Identity and Tags will be exported from Home Region.\nPress 'Enter' to export from all the subscribed regions- eg ashburn,phoenix: "
            input_region_names = input(region_list_str.format(resource_name))
    else:
        if devops:
            input_region_names = ct.orm_reg_filter
        else:
            resource_name = 'Terraform Stack'
            region_list_str = "\nEnter region (comma separated without spaces if multiple) for which you want to upload {} - eg ashburn,phoenix,global: "
            input_region_names = input(region_list_str.format(resource_name))

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
def validate_cd3(prim_options=[]):
    options = [
        Option("Validate Compartments", None, None),
        Option("Validate Groups", None, None),
        Option("Validate Policies", None, None),
        Option("Validate Tags", None, None),
        Option("Validate Network(VCNs, SubnetsVLANs, DHCP, DRGs)", None, None),
        Option("Validate DNS", None, None),
        Option("Validate Instances", None, None),
        Option("Validate Block Volumes", None, None),
        Option("Validate FSS", None, None),
        Option("Validate Buckets", None, None)
    ]
    if prim_options:
        if "Validate Networks" in prim_options:
            prim_options[prim_options.index("Validate Networks")] = "Validate Network(VCNs, SubnetsVLANs, DHCP, DRGs)"
        options = match_options(options, prim_options)
    else:
       options = show_options(options, quit=True, menu=False, index=1)
    cd3Validator.validate_cd3(options, inputfile, var_file, prefix, outdir, ct) # config, signer, ct)
    print("Exiting CD3 Validation...")

def validate_firewall_cd3(execute_all=False):
    if not execute_all:
        cd3FirewallValidator.validate_firewall_cd3(inputfile, var_file, prefix, outdir, config, signer, ct)
        print("Exiting CD3 Firewall Validation...")

################## Export Identity ##########################
def export_identityOptions(prim_options=[]):
    options = [Option("Export Compartments/Groups/Policies", export_compartmentPoliciesGroups, 'Exporting Compartments/Groups/Policies'),
               Option("Export Users", export_users, 'Exporting Users'),
               Option("Export Network Sources", export_networkSources, 'Exporting Network Sources')
    ]
    if prim_options :
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, config, signer, ct)
    # Update modified path list
    update_path_list(regions_path=[ct.home_region], service_dirs=[service_dir_identity])


def export_compartmentPoliciesGroups(inputfile, outdir,config, signer, ct):
    compartments = ct.get_compartment_map(var_file, 'Identity Objects')
    Identity.export_identity(inputfile, outdir, service_dir_identity, config, signer, ct, export_compartments=compartments)
    create_identity(prim_options=['Add/Modify/Delete Compartments','Add/Modify/Delete Groups','Add/Modify/Delete Policies'])
    print("\n\nExecute tf_import_commands_identity_nonGF.sh script created under home region directory to synch TF with OCI Identity objects\n")


def export_users(inputfile, outdir,config,signer, ct):
    Identity.Users.export_users(inputfile, outdir, service_dir_identity, config, signer, ct)
    create_identity(prim_options=['Add/Modify/Delete Users'])
    print("\n\nExecute tf_import_commands_users_nonGF.sh script created under home region directory to synch TF with OCI Identity objects\n")


def export_networkSources(inputfile, outdir, config, signer, ct):
    compartments = ct.get_compartment_map(var_file, 'Identity Objects')
    Identity.NetworkSources.export_networkSources(inputfile, outdir, service_dir_identity, config, signer, ct)
    create_identity(prim_options=['Add/Modify/Delete Network Sources'])
    print("\n\nExecute tf_import_commands_networkSources_nonGF.sh script created under home region directory to synch TF with OCI Identity objects\n")

def export_tags(prim_options=[]):
    compartments = ct.get_compartment_map(var_file, 'Tagging Objects')
    Governance.export_tags_nongreenfield(inputfile, outdir, service_dir_tagging, config, signer, ct, export_compartments=compartments)
    create_tags()
    print("\n\nExecute tf_import_commands_tags_nonGF.sh script created under home region directory to synch TF with OCI Tags\n")
    # Update modified path list
    update_path_list(regions_path=[ct.home_region], service_dirs=[service_dir_tagging])


def export_network(prim_options=[]):
    options = [Option("Export all Network Components", export_networking,
                      'Exporting all Network Components'),
               Option("Export Network components for VCNs/DRGs/DRGRouteRulesinOCI Tabs",
                      export_major_objects,
                      'Exporting VCNs, DRGs and DRGRouteRulesinOCI Tabs'),
               Option("Export Network components for DHCP Tab", export_dhcp,
                      'Exporting DHCP Tab'),
               Option("Export Network components for SecRulesinOCI Tab", export_secrules,
                      'Exporting SecRulesinOCI Tab'),
               Option("Export Network components for RouteRulesinOCI Tab", export_routerules,
                      'Exporting RouteRulesinOCI Tab'),
               Option("Export Network components for SubnetsVLANs Tab", export_subnets_vlans,
                      'Exporting SubnetsVLANs Tab'),
               Option("Export Network components for NSGs Tab", export_nsg,
                      'Exporting NSGs Tab')
               ]
    if prim_options :
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, config, signer, ct, export_regions)

    print("=====================================================================================================================")
    print("NOTE: Make sure to execute tf_import_commands_network_major-objects_nonGF.sh before executing the other scripts.")
    print("=====================================================================================================================")

    # Update modified path list
    regions_path = export_regions.copy()
    regions_path.append("global")
    service_dirs = [service_dir_network, service_dir_nsg, service_dir_vlan,'rpc']
    update_path_list(regions_path=regions_path, service_dirs=service_dirs)

def export_networking(inputfile, outdir,config, signer, ct, export_regions):
    service_dirs = []
    service_dir = outdir_struct
    compartments = ct.get_compartment_map(var_file,'Network Objects')
    Network.export_networking(inputfile, outdir, service_dir,config, signer, ct, export_compartments=compartments, export_regions=export_regions)
    options = [ Option(None, Network.create_major_objects, 'Processing VCNs and DRGs Tab'), ]
    execute_options(options, inputfile, outdir, service_dir_network, prefix, ct, non_gf_tenancy)

    options = [ Option(None, Network.create_rpc_resource, 'Processing RPCs in DRGs Tab'),]
    execute_options(options, inputfile, outdir, service_dir_network, prefix, auth_mechanism, config_file_path, ct, non_gf_tenancy)

    options = [
        Option(None, Network.create_terraform_dhcp_options, 'Processing DHCP Tab'),
        Option(None, Network.modify_terraform_secrules, 'Processing SecRulesinOCI Tab'),
        Option(None, Network.modify_terraform_routerules, 'Processing RouteRulesinOCI Tab'),
        Option(None, Network.modify_terraform_drg_routerules, 'Processing DRGRouteRulesinOCI Tab'),
    ]
    execute_options(options, inputfile, outdir, service_dir_network, prefix, ct, non_gf_tenancy)

    options = [
        Option(None, Network.create_terraform_drg_route,'Processing DRGs tab for DRG Route Tables and Route Distribution creation'),
    ]
    execute_options(options, inputfile, outdir, service_dir_network, prefix, ct, non_gf_tenancy,
                    network_connectivity_in_setupoci='', modify_network=False)

    options = [ Option(None, Network.create_terraform_subnet_vlan, 'Processing SubnetsVLANs Tab for Subnets'), ]
    execute_options(options, inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy, network_vlan_in_setupoci='network')

    options = [ Option(None, Network.create_terraform_subnet_vlan, 'Processing SubnetsVLANs Tab for VLANs'), ]
    execute_options(options, inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy, network_vlan_in_setupoci='vlan')

    options = [ Option(None, Network.create_terraform_nsg, 'Processing NSGs Tab'), ]
    execute_options(options, inputfile, outdir, service_dir_nsg, prefix, ct)
    print("\n\nExecute tf_import_commands_network_*_nonGF.sh script created under each region directory to synch TF with OCI Network objects\n")
    for service in [service_dir_network,service_dir_vlan,service_dir_nsg]:
        service_dirs.append(service_dir_network) if service_dir_network not in service_dirs else service_dirs

def export_major_objects(inputfile, outdir, config, signer, ct, export_regions):
    compartments = ct.get_compartment_map(var_file,'VCN Major Objects')
    Network.export_major_objects(inputfile, outdir, service_dir_network, config, signer, ct, export_compartments=compartments, export_regions=export_regions)
    Network.export_drg_routetable(inputfile, outdir, service_dir_network, config, signer, ct, export_compartments=compartments, export_regions=export_regions, _tf_import_cmd=True)
    options = [
        Option(None, Network.create_major_objects, 'Processing VCNs and DRGs Tab'),
    ]
    execute_options(options, inputfile, outdir,service_dir_network, prefix, ct, non_gf_tenancy)

    options = [
        Option(None, Network.create_rpc_resource, 'Processing RPCs in DRGs Tab'),
    ]
    execute_options(options, inputfile, outdir, service_dir_network, prefix, auth_mechanism, config_file_path, ct, non_gf_tenancy)

    options = [
        Option(None, Network.create_terraform_drg_route,'Processing DRGs tab for DRG Route Tables and Route Distribution creation'),
    ]
    execute_options(options, inputfile, outdir, service_dir_network, prefix, ct, non_gf_tenancy,network_connectivity_in_setupoci='', modify_network=False)

    print("\n\nExecute tf_import_commands_network_major-objects_nonGF.sh and tf_import_commands_network_drg_routerules_nonGF.sh scripts created under each region directory to synch TF with OCI Network objects\n")

def export_dhcp(inputfile, outdir,config,signer,ct,export_regions):
    compartments = ct.get_compartment_map(var_file,'DHCP')
    Network.export_dhcp(inputfile, outdir, service_dir_network,config, signer, ct, export_compartments=compartments, export_regions=export_regions)
    options = [
        Option(None, Network.create_terraform_dhcp_options, 'Processing DHCP Tab'),
        ]
    execute_options(options, inputfile, outdir, service_dir_network,prefix, ct, non_gf_tenancy)
    print("\n\nExecute tf_import_commands_network_dhcp_nonGF.sh script created under each region directory to synch TF with OCI Network objects\n")

def export_secrules(inputfile, outdir,config,signer,ct,export_regions):
    compartments = ct.get_compartment_map(var_file,'SecRulesInOCI')
    Network.export_seclist(inputfile, outdir, service_dir_network, config, signer, ct, export_compartments=compartments, export_regions=export_regions, _tf_import_cmd=True)
    options = [
        Option(None, Network.modify_terraform_secrules, 'Processing SecRulesinOCI Tab'),
        ]
    execute_options(options, inputfile, outdir,service_dir_network, prefix, ct, non_gf_tenancy)
    print("\n\nExecute tf_import_commands_network_secrules_nonGF.sh script created under each region directory to synch TF with OCI Network objects\n")

def export_routerules(inputfile, outdir,config,signer,ct,export_regions):
    compartments = ct.get_compartment_map(var_file,'RouteRulesInOCI')
    Network.export_routetable(inputfile, outdir, service_dir_network, config, signer, ct, export_compartments=compartments, export_regions=export_regions, _tf_import_cmd=True)
    options = [
        Option(None, Network.modify_terraform_routerules, 'Processing RouteRulesinOCI Tab'),
        ]
    execute_options(options, inputfile, outdir, service_dir_network,prefix, ct, non_gf_tenancy)
    print("\n\nExecute tf_import_commands_network_routerules_nonGF.sh script created under each region directory to synch TF with OCI Network objects\n")


def export_subnets_vlans(inputfile, outdir,config,signer,ct,export_regions):
    service_dir = outdir_struct
    compartments = ct.get_compartment_map(var_file,'Subnets')
    Network.export_subnets_vlans(inputfile, outdir, service_dir,config, signer, ct, export_compartments=compartments, export_regions=export_regions)
    options = [
        Option(None, Network.create_terraform_subnet_vlan, 'Processing SubnetsVLANs Tab for Subnets'),
    ]
    execute_options(options, inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy,
                    network_vlan_in_setupoci='network')

    options = [
        Option(None, Network.create_terraform_subnet_vlan, 'Processing SubnetsVLANs Tab for VLANs'),
    ]
    execute_options(options, inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy,
                    network_vlan_in_setupoci='vlan')

    print("\n\nExecute tf_import_commands_network_subnets_nonGF.sh script created under each region directory to synch TF with OCI Network objects")
    print("\nExecute tf_import_commands_network_vlans_nonGF.sh script created under each region directory to synch TF with OCI Network objects\n")


def export_nsg(inputfile, outdir,config,signer,ct,export_regions):
    compartments = ct.get_compartment_map(var_file,'NSGs')
    Network.export_nsg(inputfile, outdir,service_dir_nsg, config,signer,ct, export_compartments=compartments, export_regions=export_regions, _tf_import_cmd=True)
    options = [
        Option(None, Network.create_terraform_nsg, 'Processing NSGs Tab'),
        ]
    execute_options(options, inputfile, outdir, service_dir_nsg,prefix, ct)
    print("\n\nExecute tf_import_commands_network_nsg_nonGF.sh script created under each region directory to synch TF with OCI Network objects\n")


def export_firewall_policies(prim_options=[]):
    options = [Option("Export Firewall Policy", export_firewallpolicy,'Exporting Firewall Policy Objects'),
               Option("Export Firewall", export_firewalls,'Exporting Firewalls')]

    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, config, signer, ct, export_regions)
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_firewall])

def export_firewallpolicy(inputfile, outdir, config, signer, ct, export_regions,name_filter=""):
    compartments = ct.get_compartment_map(var_file, 'Firewall Policies')
    filter_str1 = "Enter comma separated list of display name patterns of the Policies or press \"ENTER\" to export all policies:: "
    if not devops:
        policy_name_str = input(filter_str1)
    else:
        policy_name_str = ct.fwl_pol_pattern_filter if ct.fwl_pol_pattern_filter else None

    policies = list(map(lambda x: x.strip(), policy_name_str.split(','))) if policy_name_str else None
    Security.export_firewallpolicy(inputfile, outdir, service_dir_firewall, config,signer,ct, export_compartments=compartments, export_regions=export_regions,export_policies=policies)
    create_firewall_policy(inputfile, outdir, service_dir_firewall, prefix, ct,execute_all=True)
    print("\n\nExecute tf_import_commands_firewallpolicy_nonGF.sh script created under each region directory to synch TF with OCI Firewall policy objects\n")

def export_firewalls(inputfile, outdir, config, signer, ct, export_regions):
    compartments = ct.get_compartment_map(var_file, 'Firewalls')
    Security.export_firewall(inputfile, outdir, service_dir_firewall, config,signer,ct, export_compartments=compartments, export_regions=export_regions)
    create_firewall(inputfile, outdir, service_dir_firewall, prefix, ct)
    print("\n\nExecute tf_import_commands_firewall_nonGF.sh script created under each region directory to synch TF with OCI Firewall policy objects\n")


def export_compute(prim_options=[]):
    options = [Option("Export Dedicated VM Hosts", export_dedicatedvmhosts, 'Exporting Dedicated VM Hosts'),
               Option("Export Instances (excludes instances launched by OKE)", export_instances, 'Exporting Instances')]

    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, config, signer, ct, export_regions)

def export_dedicatedvmhosts(inputfile, outdir, config, signer, ct, export_regions):
    compartments = ct.get_compartment_map(var_file,'Dedicated VM Hosts')
    Compute.export_dedicatedvmhosts(inputfile, outdir, service_dir_dedicated_vm_host, config, signer, ct, export_compartments=compartments, export_regions=export_regions)
    create_dedicatedvmhosts(inputfile, outdir, prefix, ct)
    print("\n\nExecute tf_import_commands_dedicatedvmhosts_nonGF.sh script created under each region directory to synch TF with OCI Dedicated VM Hosts\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_dedicated_vm_host])


def export_instances(inputfile, outdir,config,signer, ct, export_regions):
    compartments = ct.get_compartment_map(var_file,'Instances')
    print("Enter values for below filters to restrict the export for Instances; Press 'Enter' to use empty value for the filter")
    filter_str1 = "Enter comma separated list of display name patterns of the instances: "
    filter_str2 = "Enter comma separated list of ADs of the instances eg AD1,AD2,AD3: "
    if not devops:
        display_name_str = input(filter_str1)
        ad_name_str = input(filter_str2)
    else:
        display_name_str = ct.ins_pattern_filter if ct.ins_pattern_filter else None
        ad_name_str = ct.ins_ad_filter if ct.ins_ad_filter else None

    display_names =  list(map(lambda x: x.strip(), display_name_str.split(','))) if display_name_str else None
    ad_names = list(map(lambda x: x.strip(), ad_name_str.split(','))) if ad_name_str else None

    Compute.export_instances(inputfile, outdir, service_dir_instance,config,signer,ct, export_compartments=compartments, export_regions=export_regions, display_names = display_names, ad_names = ad_names)
    create_instances(inputfile, outdir, service_dir, prefix, ct)
    print("\n\nExecute tf_import_commands_instances_nonGF.sh script created under each region directory to synch TF with OCI Instances\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_instance])


def export_storage(prim_options=[]):
    options = [Option("Export Block Volumes/Block Backup Policy",export_block_volumes,'Exporting Block Volumes'),
               Option("Export File Systems", export_fss, 'Exporting FSS'),
               Option("Export Object Storage Buckets", export_buckets, 'Exporting Object Storage')]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, config, signer, ct, export_regions)

def export_block_volumes(inputfile, outdir,config,signer,ct, export_regions):
    compartments = ct.get_compartment_map(var_file,'Block Volumes')
    print("Enter values for below filters to restrict the export for Block Volumes; Press 'Enter' to use empty value for the filter")
    filter_str1 = "Enter comma separated list of display name patterns of the Block Volumes: "
    filter_str2 = "Enter comma separated list of ADs of the Block Volumes eg AD1,AD2,AD3: "
    if not devops:
        display_name_str = input(filter_str1)
        ad_name_str = input(filter_str2)
    else:
        display_name_str = ct.bv_pattern_filter if ct.bv_pattern_filter else None
        ad_name_str = ct.bv_ad_filter if ct.bv_ad_filter else None

    display_names = list(map(lambda x: x.strip(), display_name_str.split(','))) if display_name_str else None
    ad_names = list(map(lambda x: x.strip(), ad_name_str.split(','))) if ad_name_str else None

    Storage.export_blockvolumes(inputfile, outdir, service_dir_block_volume, config,signer,ct, export_compartments=compartments, export_regions=export_regions, display_names = display_names, ad_names = ad_names)
    Storage.create_terraform_block_volumes(inputfile, outdir, service_dir_block_volume, prefix, ct)
    print(
        "\n\nExecute tf_import_commands_blockvolumes_nonGF.sh script created under each region directory to synch TF with OCI Block Volume Objects\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_block_volume])


def export_fss(inputfile, outdir,config, signer, ct, export_regions):
    compartments = ct.get_compartment_map(var_file,'FSS objects')
    Storage.export_fss(inputfile, outdir, service_dir_fss, config,signer,ct, export_compartments=compartments, export_regions=export_regions)
    Storage.create_terraform_fss(inputfile, outdir, service_dir_fss, prefix, ct)
    print(
        "\n\nExecute tf_import_commands_fss_nonGF.sh script created under each region directory to synch TF with OCI FSS objects\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_fss])


def export_buckets(inputfile, outdir, config, signer, ct, export_regions):
    compartments = ct.get_compartment_map(var_file, 'Buckets')
    Storage.export_buckets(inputfile, outdir, service_dir_object_storage, config,signer,ct, export_compartments=compartments, export_regions=export_regions)
    Storage.create_terraform_oss(inputfile, outdir, service_dir_object_storage, prefix, ct)
    print("\n\nExecute tf_import_commands_buckets_nonGF.sh script created under each region directory to synch TF with OCI Object Storage Buckets\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_object_storage])


def export_loadbalancer(prim_options=[]):
    options = [Option("Export Load Balancers", export_lbr,'Exporting LBR Objects'),
               Option("Export Network Load Balancers", export_nlb,'Exporting NLB Objects')]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, config, signer, ct, export_regions)

def export_lbr(inputfile, outdir,config, signer, ct, export_regions):
    compartments = ct.get_compartment_map(var_file,'LBR objects')
    Network.export_lbr(inputfile, outdir, service_dir_loadbalancer, config,signer,ct, export_compartments=compartments, export_regions=export_regions)
    create_lb(inputfile, outdir, prefix, ct)
    print("\n\nExecute tf_import_commands_lbr_nonGF.sh script created under each region directory to synch TF with OCI LBR objects\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_loadbalancer])


def export_nlb(inputfile, outdir,config,signer, ct, export_regions):
    compartments = ct.get_compartment_map(var_file,'NLB objects')
    Network.export_nlb(inputfile, outdir, service_dir_networkloadbalancer, config,signer,ct, export_compartments=compartments, export_regions=export_regions)
    create_nlb(inputfile, outdir, prefix, ct)
    print("\n\nExecute tf_import_commands_nlb_nonGF.sh script created under each region directory to synch TF with OCI NLB objects\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_networkloadbalancer])


def export_databases(prim_options=[]):
    options = [Option("Export Virtual Machine or Bare Metal DB Systems",export_dbsystems_vm_bm,'Exporting VM and BM DB Systems'),
               Option("Export EXA Infra and EXA VMClusters", export_exa_infra_vmclusters, 'Exporting EXA Infra and EXA VMClusters'),
                Option('Export ADBs', export_adbs, 'Exporting Autonomous Databases')]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, config, signer, ct, export_regions)

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
    create_exa_infra_vmclusters(inputfile, outdir, prefix,ct)
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

def export_management_services(prim_options=[]):
    options = [Option("Export Notifications",export_notifications,'Exporting Notifications'),
               Option("Export Events", export_events,'Exporting Events'),
               Option("Export Alarms", export_alarms, 'Exporting Alarms'),
               Option("Export Service Connectors", export_service_connectors, 'Exporting Service Connectors')]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, service_dir_managementservices, config, signer, ct, export_regions)
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_managementservices])


def export_notifications(inputfile, outdir, service_dir, config, signer, ct, export_regions):
    compartments = ct.get_compartment_map(var_file,'Notifications')
    ManagementServices.export_notifications(inputfile, outdir, service_dir, config,signer,ct, export_compartments=compartments, export_regions=export_regions)
    ManagementServices.create_terraform_notifications(inputfile, outdir, service_dir, prefix, ct)
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

def export_developer_services(prim_options=[]):
    options = [Option("Export OKE cluster and Nodepools", export_oke, 'Exporting OKE'),
               ]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, config, signer, ct, export_regions)

def export_oke(inputfile, outdir, config,signer, ct, export_regions):
    compartments = ct.get_compartment_map(var_file,'OKE')
    DeveloperServices.export_oke(inputfile, outdir, service_dir_oke,config,signer,ct, export_compartments=compartments, export_regions=export_regions)
    DeveloperServices.create_terraform_oke(inputfile, outdir, service_dir_oke,prefix, ct)
    print("\n\nExecute tf_import_commands_oke_nonGF.sh script created under each region directory to synch TF with OKE\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_oke])


def export_sddc(prim_options=[]):
    compartments = ct.get_compartment_map(var_file,'SDDCs')
    SDDC.export_sddc(inputfile, outdir, service_dir_sddc,config,signer,ct, export_compartments=compartments, export_regions=export_regions)
    SDDC.create_terraform_sddc(inputfile, outdir, service_dir_sddc, prefix, ct)
    print("\n\nExecute tf_import_commands_sddcs_nonGF.sh script created under each region directory to synch TF with SDDC\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_sddc])

def export_dns(prim_options=[]):
    options = [Option("Export DNS Views/Zones/Records", export_dns_views_zones_rrsets,
                      'Exporting DNS Views/Zones/Records'),
               Option("Export DNS Resolvers", export_dns_resolvers, 'Exporting DNS Resolvers')
               ]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, service_dir_dns, config, signer, ct, export_regions)
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_dns])


def export_dns_views_zones_rrsets(inputfile, outdir, service_dir, config, signer, ct, export_regions):
    compartments = ct.get_compartment_map(var_file, 'DNS Views ,attached zones and rrsets')
    filter_str1 = "Do you want to export default views/zones/records (y|n), Default is n: "
    if not devops:
        dns_filter = "n" if input(filter_str1).lower() != 'y' else "y"
    else:
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


def cd3_services(prim_options=[]):
    options = [
        Option('Fetch Compartments OCIDs to variables file', fetch_compartments,'Fetch Compartments OCIDs'),
        Option('Fetch Protocols to OCI_Protocols', fetch_protocols, 'Fetch Protocols'),
    ]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, outdir, outdir_struct, ct)

def fetch_protocols(outdir, outdir_struct, ct):
    cd3service.fetch_protocols()

################## Create Functions ##########################
def create_identity(prim_options=[]):
    options = [
        Option('Add/Modify/Delete Compartments', Identity.create_terraform_compartments, 'Processing Compartments Tab'),
        Option('Add/Modify/Delete Groups', Identity.create_terraform_groups, 'Processing Groups Tab'),
        Option('Add/Modify/Delete Policies', Identity.create_terraform_policies, 'Processing Policies Tab'),
        Option('Add/Modify/Delete Users', Identity.Users.create_terraform_users, 'Processing Users Tab'),
        Option('Add/Modify/Delete Network Sources', Identity.NetworkSources.create_terraform_networkSources, 'Processing NetworkSources Tab')
    ]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir,service_dir_identity, prefix, ct)
    # Update modified path list
    update_path_list(regions_path=[ct.home_region], service_dirs=[service_dir_identity])


def create_tags(prim_options=[]):
    options = [Option(None, Governance.create_terraform_tags, 'Processing Tags Tab')]
    execute_options(options, inputfile, outdir, service_dir_tagging, prefix, ct)
    # Update modified path list
    update_path_list(regions_path=[ct.home_region], service_dirs=[service_dir_tagging])


def create_network(execute_all=False,prim_options=[]):
    service_dir = outdir_struct
    options = [
        Option('Create Network', Network.create_all_tf_objects, 'Create All Objects'),
        Option('Modify Network', modify_terraform_network, 'Modifying Network'),
        Option('Security Rules', export_modify_security_rules, 'Security Rules'),
        Option('Route Rules', export_modify_route_rules, 'Route Rules'),
        Option('DRG Route Rules', export_modify_drg_route_rules, 'DRG Route Rules'),
        Option('Network Security Groups', export_modify_nsgs, 'Network Security Groups'),
        Option('Add/Modify/Delete VLANs', create_vlans, 'VLANs'),
        Option('Customer Connectivity', create_drg_connectivity, 'Connectivity')
    ]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        if not execute_all:
            options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy=non_gf_tenancy)
    # Update modified path list
    regions_path = export_regions.copy()
    regions_path.append("global")
    service_dirs = [service_dir_network, service_dir_nsg, service_dir_vlan, 'rpc']
    update_path_list(regions_path=regions_path, service_dirs=service_dirs)

def modify_terraform_network(inputfile, outdir, service_dir,  prefix, ct, non_gf_tenancy):
    Network.create_all_tf_objects(inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy=non_gf_tenancy,  modify_network=True, )

def export_modify_security_rules(inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy,sub_options=[]):
    execute_all = False
    options = [
        Option('Export Security Rules (From OCI into SecRulesinOCI sheet)', export_security_rules, 'Exporting Security Rules in OCI'),
        Option('Add/Modify/Delete Security Rules (Reads SecRulesinOCI sheet)', Network.modify_terraform_secrules, 'Processing SecRulesinOCI Tab'),
    ]
    if sub_options:
        options = match_options(options, sub_options)
    else:
        if not execute_all:
            options = show_options(options, quit=True, menu=True, index=1)

    for option in options:
        options1 = []
        options1.append(option)
        if (option.name == 'Export Security Rules (From OCI into SecRulesinOCI sheet)'):
            execute_options(options1, inputfile, outdir, service_dir_network, config, signer, ct, non_gf_tenancy=non_gf_tenancy)
        elif (option.name == 'Add/Modify/Delete Security Rules (Reads SecRulesinOCI sheet)'):
            execute_options(options1, inputfile, outdir, service_dir_network, prefix, ct, non_gf_tenancy)


def export_security_rules(inputfile, outdir, service_dir, config, signer, ct, non_gf_tenancy):
    compartments = ct.get_compartment_map(var_file, 'OCI Security Rules')
    Network.export_seclist(inputfile, outdir, service_dir, config, signer, ct, export_compartments=compartments, export_regions= export_regions, _tf_import_cmd=False)

def export_modify_route_rules(inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy,sub_options=[]):
    execute_all = False
    options = [
        Option('Export Route Rules (From OCI into RouteRulesinOCI sheet)', export_route_rules, 'Exporting Route Rules in OCI'),
        Option('Add/Modify/Delete Route Rules (Reads RouteRulesinOCI sheet)', Network.modify_terraform_routerules, 'Processing RouteRulesinOCI Tab'),
    ]
    if sub_options:
        options = match_options(options, sub_options)
    else:
        if not execute_all:
            options = show_options(options, quit=True, menu=True, index=1)

    for option in options:
        options1 = []
        options1.append(option)
        if (option.name == 'Export Route Rules (From OCI into RouteRulesinOCI sheet)'):
            execute_options(options1, inputfile, outdir, service_dir_network, config, signer, ct, non_gf_tenancy=non_gf_tenancy)
        elif (option.name == 'Add/Modify/Delete Route Rules (Reads RouteRulesinOCI sheet)'):
            execute_options(options1, inputfile, outdir, service_dir_network, prefix, ct, non_gf_tenancy)


def export_route_rules(inputfile, outdir, service_dir, config, signer, ct, non_gf_tenancy):
    compartments = ct.get_compartment_map(var_file, 'OCI Route Rules')
    Network.export_routetable(inputfile, outdir, service_dir, config, signer, ct, export_compartments=compartments, export_regions= export_regions, _tf_import_cmd=False)

def export_modify_drg_route_rules(inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy,sub_options=[]):
    execute_all = False
    options = [
        Option('Export DRG Route Rules (From OCI into DRGRouteRulesinOCI sheet)', export_drg_route_rules, 'Exporting DRG Route Rules in OCI'),
        Option('Add/Modify/Delete DRG Route Rules (Reads DRGRouteRulesinOCI sheet)', Network.modify_terraform_drg_routerules, 'Processing DRGRouteRulesinOCI Tab'),
    ]
    if sub_options:
        options = match_options(options, sub_options)
    else:
        if not execute_all:
            options = show_options(options, quit=True, menu=True, index=1)

    for option in options:
        options1 = []
        options1.append(option)
        if (option.name == 'Export DRG Route Rules (From OCI into DRGRouteRulesinOCI sheet)'):
            execute_options(options1, inputfile, outdir, service_dir_network, config, signer, ct, non_gf_tenancy=non_gf_tenancy)
        elif (option.name == 'Add/Modify/Delete DRG Route Rules (Reads DRGRouteRulesinOCI sheet)'):
            execute_options(options1, inputfile, outdir, service_dir_network, prefix, ct, non_gf_tenancy)


def export_drg_route_rules(inputfile, outdir, service_dir, config, signer, ct, non_gf_tenancy):
    compartments = ct.get_compartment_map(var_file,'OCI DRG Route Rules')
    Network.export_drg_routetable(inputfile, outdir, service_dir, config, signer, ct, export_compartments=compartments, export_regions= export_regions, _tf_import_cmd=False)


def export_modify_nsgs(inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy,sub_options=[]):
    execute_all = False
    options = [
        Option('Export NSGs (From OCI into NSGs sheet)', export_nsgs, 'Exporting NSGs in OCI'),
        Option('Add/Modify/Delete NSGs (Reads NSGs sheet)', Network.create_terraform_nsg, 'Processing NSGs Tab'),
    ]
    if sub_options:
        options = match_options(options, sub_options)
    else:
        if not execute_all:
            options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, service_dir_nsg, prefix, ct)

def export_nsgs(inputfile, outdir, service_dir, prefix, ct):
    compartments = ct.get_compartment_map(var_file,'OCI NSGs')
    Network.export_nsg(inputfile, outdir, service_dir, config, signer, ct, export_compartments=compartments, export_regions= export_regions, _tf_import_cmd=False)

def create_vlans(inputfile, outdir, service_dir,  prefix,ct, non_gf_tenancy, network_vlan_in_setupoci='vlan'):
    Network.create_terraform_subnet_vlan(inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy=non_gf_tenancy, network_vlan_in_setupoci='vlan',modify_network=True)
    Network.create_terraform_route(inputfile, outdir, service_dir_network, prefix, ct, non_gf_tenancy=non_gf_tenancy, network_vlan_in_setupoci='vlan',modify_network=True)

def create_drg_connectivity(inputfile, outdir, service_dir,  prefix, ct, non_gf_tenancy,network_vlan_in_setupoci='vlan',sub_options=[]):
    execute_all = False
    service_dir = ""

    options = [ Option('Create Remote Peering Connections', create_rpc, 'RPCs'),]
    if sub_options:
        options = match_options(options, sub_options)
    else:
        if not execute_all:
            options = show_options(options, quit=True, menu=True, index=1)

    execute_options(options, inputfile, outdir, service_dir, service_dir_network, prefix, auth_mechanism, config_file_path, ct, non_gf_tenancy=non_gf_tenancy)

def create_rpc(inputfile, outdir, service_dir, service_dir_network, prefix, auth_mechanism, config_file_path, ct, non_gf_tenancy):
    Network.create_rpc_resource(inputfile, outdir, service_dir, prefix, auth_mechanism, config_file_path, ct, non_gf_tenancy=non_gf_tenancy)
    Network.create_terraform_drg_route(inputfile, outdir, service_dir_network, prefix, non_gf_tenancy=non_gf_tenancy, ct=ct, network_connectivity_in_setupoci='connectivity', modify_network=True)

def create_compute(prim_options=[]):
    service_dir = outdir_struct
    options = [
        Option('Add/Modify/Delete Dedicated VM Hosts', create_dedicatedvmhosts, ''),
        Option('Add/Modify/Delete Instances/Boot Backup Policy', create_instances,''),
    ]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, service_dir,prefix, ct)


def create_instances(inputfile, outdir, service_dir, prefix, ct):
    options = [
        Option(None, Compute.create_terraform_instances, 'Processing Instances Tab')
    ]
    execute_options(options, inputfile, outdir, service_dir_instance, prefix, ct)
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_instance])


def create_dedicatedvmhosts(inputfile, outdir, service_dir, prefix, ct):
    options = [Option(None, Compute.create_terraform_dedicatedhosts, 'Processing Dedicated VM Hosts Tab')]
    execute_options(options, inputfile, outdir, service_dir_dedicated_vm_host,prefix, ct)
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_dedicated_vm_host])


def create_storage(execute_all=False,prim_options=[]):
    options = [
        Option('Add/Modify/Delete Block Volumes/Block Backup Policy', create_block_volumes, ''),
        Option('Add/Modify/Delete File Systems', create_fss, ''),
        Option('Add/Modify/Delete Object Storage Buckets', create_buckets, '')
        #Option('Enable Object Storage Buckets Write Logs', create_cis_oss_logs, '')
    ]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    if not execute_all:
        execute_options(options, inputfile, outdir,prefix, ct)

def create_block_volumes(inputfile, outdir, prefix,ct):
    options = [ Option(None, Storage.create_terraform_block_volumes, 'Processing BlockVolumes Tab') ]
    execute_options(options, inputfile, outdir, service_dir_block_volume, prefix, ct)
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_block_volume])


def create_fss(inputfile, outdir, prefix,ct):
    options = [Option(None, Storage.create_terraform_fss, 'Processing FSS Tab')]
    execute_options(options, inputfile, outdir, service_dir_fss, prefix, ct)
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_fss])


def create_buckets(inputfile, outdir, prefix,ct):
    options = [Option(None, Storage.create_terraform_oss, 'Processing Buckets Tab')]
    execute_options(options, inputfile, outdir, service_dir_object_storage, prefix, ct)
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_object_storage])


def create_loadbalancer(execute_all=False,prim_options=[]):
    options = [
        Option('Add/Modify/Delete Load Balancers', create_lb, 'LBaaS'),
        Option('Add/Modify/Delete Network Load Balancers', create_nlb, 'NLB')
        #Option('Enable LBaaS Logs', enable_lb_logs, 'LBaaS Logs')
    ]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    if not execute_all:
        execute_options(options, inputfile, outdir, prefix, ct)

def create_lb(inputfile, outdir, prefix, ct):
    options = [
         Option(None, Network.create_terraform_lbr_hostname_certs, 'Creating LBR'),
         Option(None, Network.create_backendset_backendservers, 'Creating Backend Sets and Backend Servers'),
         Option(None, Network.create_listener, 'Creating Listeners'),
         Option(None, Network.create_path_route_set, 'Creating Path Route Sets'),
         Option(None, Network.create_ruleset, 'Creating Rule Sets'),
    ]
    execute_options(options, inputfile, outdir, service_dir_loadbalancer, prefix, ct)
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_loadbalancer])


def create_nlb(inputfile, outdir, prefix, ct):
    options = [
         Option(None, Network.create_terraform_nlb_listener, 'Creating NLB and Listeners'),
         Option(None, Network.create_nlb_backendset_backendservers, 'Creating NLB Backend Sets and Backend Servers'),
    ]
    execute_options(options, inputfile, outdir, service_dir_networkloadbalancer, prefix, ct)
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_networkloadbalancer])


def create_databases(execute_all=False,prim_options=[]):
    options = [
        Option('Add/Modify/Delete Virtual Machine or Bare Metal DB Systems', create_terraform_dbsystems_vm_bm, 'Processing DBSystems-VM-BM Tab'),
        Option('Add/Modify/Delete EXA Infra and EXA VM Clusters', create_exa_infra_vmclusters, ''),
        Option('Add/Modify/Delete ADBs', create_terraform_adb, 'Processing ADB Tab'),
    ]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        if not execute_all:
            options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, prefix, ct)

def create_terraform_dbsystems_vm_bm(inputfile, outdir, prefix,ct):
    Database.create_terraform_dbsystems_vm_bm(inputfile, outdir, service_dir_dbsystem_vm_bm, prefix, ct)
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_dbsystem_vm_bm])


def create_exa_infra_vmclusters(inputfile, outdir, prefix,ct):
    options = [Option(None, Database.create_terraform_exa_infra, 'Processing Exa-Infra Tab'),
               Option(None, Database.create_terraform_exa_vmclusters, 'Processing Exa-VM-Clusters Tab')]
    execute_options(options, inputfile, outdir, service_dir_database_exacs, prefix, ct)
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_database_exacs])


def create_terraform_adb(inputfile, outdir, prefix,ct):
    Database.create_terraform_dbsystems_vm_bm(inputfile, outdir, service_dir_adb, prefix, ct)
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_adb])


def create_management_services(execute_all=False,prim_options=[]):
    options = [
        Option("Add/Modify/Delete Notifications", ManagementServices.create_terraform_notifications, 'Setting up Notifications'),
        Option("Add/Modify/Delete Events", ManagementServices.create_terraform_events, 'Setting up Events'),
        Option("Add/Modify/Delete Alarms", ManagementServices.create_terraform_alarms, 'Setting up Alarms'),
        Option("Add/Modify/Delete ServiceConnectors", ManagementServices.create_service_connectors,
               'Setting up SCHs'),
    ]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        if not execute_all:
            options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, service_dir_managementservices, prefix, ct)
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_managementservices])


def create_developer_services(execute_all=False,prim_options=[]):
    options = [
        Option("Upload current terraform files/state to Resource Manager", create_rm_stack, 'Creating RM Stack'),
        Option("Add/Modify/Delete OKE Cluster and Nodepools", create_oke, 'Creating OKE cluster and Nodepool')
    ]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        if not execute_all:
            options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, prefix, auth_mechanism, config_file_path,ct)

def create_rm_stack(inputfile, outdir, prefix, auth_mechanism, config_file, ct):
    regions = get_region_list(rm = True)
    DeveloperServices.create_resource_manager(outdir,var_file, outdir_struct, prefix, auth_mechanism, config_file, ct, regions)

def create_oke(inputfile, outdir, prefix, auth_mechanism, config_file, ct):
    DeveloperServices.create_terraform_oke(inputfile, outdir, service_dir_oke, prefix, ct)
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_oke])


def create_sddc(prim_options=[]):
    SDDC.create_terraform_sddc(inputfile, outdir, service_dir_sddc, prefix, ct)
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_sddc])


def create_dns(prim_options=[]):
    options = [
        Option('Add/Modify/Delete DNS Views/Zones/Records', create_terraform_dns,
               'Processing DNS-Views-Zones-Records Tab'),
        Option('Add/Modify/Delete DNS Resolvers', Network.create_terraform_dns_resolvers,
               'Processing DNS-Resolvers Tab')
    ]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, service_dir_dns, prefix, ct)
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_dns])


def create_terraform_dns(inputfile, outdir, service_dir, prefix, ct):
    Network.create_terraform_dns_views(inputfile, outdir, service_dir, prefix, ct)
    Network.create_terraform_dns_zones(inputfile, outdir, service_dir, prefix, ct)
    Network.create_terraform_dns_rrsets(inputfile, outdir, service_dir, prefix, ct)

def create_logging(prim_options=[]):
    options = [
        Option('Enable VCN Flow Logs', create_cis_vcnflow_logs, 'VCN Flow Logs'),
        Option('Enable LBaaS Logs', enable_lb_logs, 'LBaaS Logs'),
        Option('Enable Object Storage Buckets Write Logs', create_cis_oss_logs, 'OSS Write Logs')
    ]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, prefix, ct)

def create_cis_vcnflow_logs(inputfile, outdir,  prefix, ct):
    options = [Option(None, ManagementServices.enable_cis_vcnflow_logging, 'Enabling VCN Flow Logs')]
    execute_options(options, inputfile, outdir, service_dir_network, prefix, ct)
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_network])


def enable_lb_logs(inputfile, outdir, prefix, ct):
    options = [Option(None, ManagementServices.enable_load_balancer_logging, 'Enabling LBaaS Logs')]
    execute_options(options, inputfile, outdir, service_dir_loadbalancer, prefix, ct)
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_loadbalancer])


def create_cis_oss_logs(inputfile, outdir, prefix, ct):
    options = [Option(None, ManagementServices.enable_cis_oss_logging, 'Enabling OSS Write Logs')]
    execute_options(options, inputfile, outdir, service_dir_object_storage, prefix, ct)
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_loadbalancer])


def create_cis_features(prim_options=[]):
    options = [Option('CIS Compliance Checking Script', initiate_cis_scan, 'CIS Compliance Checking'),
               Option("Create Key/Vault", create_cis_keyvault, 'Creating CIS Key/Vault and enable Logging for write events to bucket'),
               Option("Create Default Budget",create_cis_budget,'Create Default Budget'),
               Option("Enable Cloud Guard", enable_cis_cloudguard, 'Enable Cloud Guard'),]

    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, outdir, prefix, config_file_path)

def create_cis_keyvault(*args,**kwargs):
    if not devops:
        region_name = input("Enter region name eg ashburn where you want to create Key/Vault: ")
        comp_name = input("Enter name of compartment as it appears in OCI Console: ")
    else:
        region_name = ct.vault_region
        comp_name = ct.vault_comp
    options = [Option(None, Security.create_cis_keyvault, 'Creating KeyVault')]
    execute_options(options, outdir, service_dir_kms, service_dir_identity,prefix, ct, region_name, comp_name)
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_kms])


def create_cis_budget(*args,**kwargs):
    if not devops:
        amount = input("Enter Monthly Budget Amount (in US$): ")
        threshold = input("Enter Threshold Percentage of Budget: ")
    else:
        amount = ct.budget_amount
        threshold = ct.budget_threshold
    options = [Option(None, Governance.create_cis_budget, 'Creating Budget')]
    execute_options(options, outdir, service_dir_budget, prefix,ct, amount,threshold)
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_budget])


def enable_cis_cloudguard(*args,**kwargs):
    if not devops:
        region = input("Enter Reporting Region for Cloud Guard eg london: ")
    else:
        region = ct.cg_region
    options = [Option(None, Security.enable_cis_cloudguard, 'Enabling Cloud Guard')]
    execute_options(options, outdir, service_dir_cloud_guard, prefix, ct, region)
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_cloud_guard])


def initiate_cis_scan(outdir, prefix, config_file,sub_options=[]):
    options = [
        Option("Download latest compliance checking script", start_cis_download, 'Download CIS script'),
        Option("Execute compliance checking script", start_cis_scan, 'Execute CIS script'),
    ]
    if sub_options:
        options = match_options(options, sub_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, outdir, prefix, config_file)

def start_cis_download(outdir, prefix, config_file):
    print("Downloading the script file as 'cis_reports.py' at location "+os.getcwd())
    resp = requests.get("https://raw.githubusercontent.com/oracle-quickstart/oci-cis-landingzone-quickstart/main/scripts/cis_reports.py")
    resp_contents = resp.text
    with open("cis_reports.py", "w", encoding="utf-8") as fd:
        fd.write(resp_contents)
    print("Download complete!!")

def start_cis_scan(outdir, prefix, config_file):
    cmd = "python cis_reports.py"
    if not devops:
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


def create_validate_firewall_service(execute_all=False,prim_options=[]):
    options = [
        Option('Validate Firewall CD3 Excel', cd3FirewallValidator.validate_firewall_cd3, 'Validate Firewall Excel'),
        Option('Add/Modify/Delete Firewall Policy', create_firewall_policy, 'Add/Modify/Delete Firewall Policy'),
        Option('Add/Modify/Delete Firewall', create_firewall, 'Add/Modify/Delete Firewall'),
        Option('Clone Firewall Policy', clone_firewall_policy, 'Clone the firewall policy'),
        #Option('Delete Firewall Policy', delete_firewall_policy, 'Delete the firewall policy')
    ]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        if not execute_all:
            options = show_options(options, quit=True, menu=True, index=1)
    validation_check = False
    for option in options:
        options1 = []
        if (option.name == 'Validate Firewall CD3 Excel'):
            status = cd3FirewallValidator.validate_firewall_cd3(inputfile, var_file, prefix, outdir, config, signer, ct)
            print("Firewall validator completed with "+ str(status))
        elif(option.name == 'Add/Modify/Delete Firewall Policy' or option.name == 'Add/Modify/Delete Firewall'):
            options1.append(option)
            if not devops and not validation_check:
                run_validator = "Did you run the validation of Firewall cd3 Excel and fixed all Errors(y/n): "
                run_validator_input = input(run_validator)
                if run_validator_input == "n":
                    print("Running Validator for Firewall...\n")
                    status = cd3FirewallValidator.validate_firewall_cd3(inputfile, var_file, prefix, outdir, config, signer, ct)
                    if status == "Error":
                        still_continue = "Do you still want to proceed to generate tfvars (y/n): "
                        still_continue_input = input(still_continue)
                        if still_continue_input == "n":
                            print("Exiting...!")
                            exit(1)
                validation_check = True
                print("Proceeding with tfvars generation...")

            execute_options(options1, inputfile, outdir, service_dir_firewall, prefix, ct,sub_options=sub_child_options)
        else:
            options1.append(option)
            execute_options(options1, inputfile, outdir, service_dir_firewall, config,signer, ct)
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_firewall])


def clone_firewall_policy( inputfile, outdir, service_dir, config, signer, ct):
    filter_str1 = "Enter region of the Firewall Policy to be cloned (eg phoenix): "
    filter_str2 = "Enter names of the source firewall policies(comma separated): "
    filter_str3 = "Enter names for the target firewall policies(comma separated), in the same order as source above, leave empty if you need tool to generate the policy names: "
    filter_str4 = "Clone only if policy is used/attached, y/n, default is y: "
    if not devops:
        region_name_str = input(filter_str1)
        src_policy_str = input(filter_str2)
        target_policy_str = input(filter_str3)
        attached_policy_only = "y" if input(filter_str4).lower() != 'n' else "n"

    else:
        region_name_str = ct.fwl_clone_src_region
        src_policy_str = ct.src_policy_str
        target_policy_str = ct.target_policy_str
        attached_policy_only = None
        if ct.attached_policy_only:
            if ct.attached_policy_only.lower() == "false":
                attached_policy_only = "n"
            if ct.attached_policy_only.lower() == "true":
                attached_policy_only = "y"
        attached_policy_only = attached_policy_only if attached_policy_only else None
    compartments = ct.get_compartment_map(var_file, 'Clone Firewall Policy')

    export_regions = list(map(lambda x: x.strip().lower(), region_name_str.split(','))) if region_name_str else None
    src_policies = list(map(lambda x: x.strip(), src_policy_str.split(','))) if src_policy_str else None
    if src_policies is None:
        print("Source Policies are mandatory for cloning. ")
        exit(1)
    target_policies = list(map(lambda x: x.strip(), target_policy_str.split(','))) if target_policy_str else None
    Security.export_firewallpolicy(inputfile, outdir, service_dir, config, signer, ct,
                                   export_compartments=compartments, export_regions=export_regions,
                                   export_policies=src_policies,target_policies=target_policies,attached_policy_only=attached_policy_only,clone_policy=True)

    #Security.clone_firewallpolicy(inputfile, outdir, service_dir, config, signer, ct, export_compartments=compartments, export_regions=export_regions,  export_firewall=firewall, export_policy=policy)
    print("Proceeding with tfvars generation...")
    create_firewall_policy(inputfile, outdir, service_dir, prefix, ct,execute_all=True)
    #print("\n\nExecute tf_import_commands_Firewallpolicy_nonGF.sh script created under each region directory to synch TF with OCI Firewall policy objects\n")


def delete_firewall_policy(inputfile, outdir, service_dir, config, signer, ct):
    filter_str1 = "Enter region of the Firewall Policy to be deleted (eg phoenix): "
    filter_str2 = "Enter names of the Firewall Policies(comma separated) that need to be deleted: "
    if not devops:
        region_name_str = input(filter_str1)
        firewallpolicy_name_str = input(filter_str2)
    else:
        region_name_str = ct.fwl_region
        firewallpolicy_name_str = ct.fwl_name

    compartments = ct.get_compartment_map(var_file, 'Delete Firewall Policy')

    delete_regions = list(map(lambda x: x.strip().lower(), region_name_str.split(','))) if region_name_str else None
    firewallpolicy = list(map(lambda x: x.strip(), firewallpolicy_name_str.split(','))) if firewallpolicy_name_str else None

    Security.delete_firewallpolicy(inputfile, outdir, service_dir, config, signer, ct,delete_compartments=compartments, delete_regions=delete_regions, delete_policy=firewallpolicy)
    print("Proceeding with tfvars generation...")
    create_firewall_policy(inputfile, outdir, service_dir, prefix, ct,execute_all=True)


def create_firewall_policy(inputfile, outdir, service_dir, prefix, ct,execute_all=False,sub_options=[]):
    options = [
            Option('Add/Modify Policy', Security.firewallpolicy_create, 'Processing Firewall-Policy Tab'),
            Option('Add/Modify Service', Security.fwpolicy_create_service,
                   'Processing Firewall-Policy-Serviceslist Tab'),
            Option('Add/Modify Service-list', Security.fwpolicy_create_servicelist,
                   'Processing Firewall-Policy-Servicelist Tab'),
            Option('Add/Modify Application', Security.fwpolicy_create_apps,
                   'Processing Firewall-Policy-Applicationlist Tab'),
            Option('Add/Modify Application-list', Security.fwpolicy_create_applicationlist,
                   'Processing Firewall-Policy-Applicationlist Tab'),
            Option('Add/Modify Address-list', Security.fwpolicy_create_address,
                   'Processing Firewall-Policy-Address Tab'),
            Option('Add/Modify Url-list', Security.fwpolicy_create_urllist,
                   'Processing Firewall-Policy-Urllist Tab'),
            Option('Add/Modify Security rules', Security.fwpolicy_create_secrules,
                   'Processing Firewall-Policy-Securules Tab'),
            Option('Add/Modify Mapped Secrets', Security.fwpolicy_create_secret,
                   'Processing Firewall-Policy-Secrets Tab'),
            Option('Add/Modify Decryption Rules', Security.fwpolicy_create_decryptrules,
                   'Processing Firewall-Policy-Decrytprofile Tab'),
            Option('Add/Modify Decryption Profile', Security.fwpolicy_create_decryptionprofile,
                   'Processing Firewall-Policy-DecryptRule Tab'),
        ]
    if sub_options and sub_options != ['']:
        options = match_options(options, sub_options)
    else:
        if not execute_all:
            options = show_firewall_options(options, quit=True, menu=True, index=1)

    execute_options(options, inputfile, outdir, service_dir, prefix, ct)


def create_firewall(inputfile, outdir, service_dir, prefix, ct,sub_options=[]):
    Security.fw_create(inputfile, outdir, service_dir, prefix, ct)


#Execution starts here
global devops
global updated_paths
global import_scripts
updated_paths = []
import_scripts = []
exec_start_time = datetime.datetime.now()
parser = argparse.ArgumentParser(description='Sets Up OCI via TF')
parser.add_argument('propsfile', help="Full Path of properties file containing input variables. eg setUpOCI.properties")
parser.add_argument('--main_options', default="")
parser.add_argument('--sub_options', default="")
parser.add_argument('--sub_child_options', default="")
parser.add_argument('--add_filter', default=None)
parser.add_argument('--devops', default=False)
args = parser.parse_args()
setUpOCI_props = configparser.RawConfigParser()
setUpOCI_props.read(args.propsfile)
devops = args.devops
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

## Authenticate Params
ct=None
ct = commonTools()
config,signer = ct.authenticate(auth_mechanism, config_file_path)

if devops:
    # Set Export filters from devops
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
# If single outdir, get service names from /cd3user/oci_tools/cd3_automation_toolkit/user-scripts/.outdir_structure_file.properties
if len(outdir_struct.items())==0:
    single_outdir_config = configparser.RawConfigParser()
    single_outdir_config.read("/cd3user/oci_tools/cd3_automation_toolkit/user-scripts/.outdir_structure_file.properties")
    for item,val in single_outdir_config.items("Default"):
        varname = "service_dir_" + str(item.replace("-", "_")).strip()
        exec(varname + "= \"\"",globals())
# If multiple outdir, get service names from
else:
    for key,value in outdir_struct.items():
        varname = "service_dir_"+str(key.replace("-","_")).strip()
        exec(varname + "= value",globals())

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
    if devops:
        print("Script to Fetch Compartments OCIDs to variables file has not been executed. Running it now.")
        fetch_compartments(outdir, outdir_struct, ct)
    else:
        print("Script to Fetch Compartments OCIDs to variables file has not been executed. Execution of fetch compartments...")
        user_input = input("Do you want to run it now? (y|n), Default is n: ")
        if user_input.lower()!='y':
            user_input = 'n'
        if(user_input.lower() == 'y'):
            fetch_compartments(outdir,outdir_struct, ct)
else:
    print("Make sure to execute the script for 'Fetch Compartments OCIDs to variables file' under 'CD3 Services' menu option atleast once before you continue!")

## Menu Options
if non_gf_tenancy:
    # verify_outdir_is_empty()
    print("\nworkflow_type set to export_resources. Export existing OCI objects and Synch with TF state")
    print("We recommend to not have any existing tfvars/tfstate files for export out directory")
    export_regions = get_region_list(rm=False)
    inputs = [
        Option('Export Identity', export_identityOptions, 'Identity'),
        Option('Export Tags', export_tags, 'Tagging'),
        Option('Export Network', export_network, 'Network'),
        Option('Export OCI Firewall', export_firewall_policies, 'OCI Firewall Policy'),
        Option('Export DNS Management', export_dns, 'DNS Management'),
        Option('Export Compute', export_compute, 'Dedicated VM Hosts and Instances'),
        Option('Export Storage', export_storage, 'Storage'),
        Option('Export Databases', export_databases, 'Databases'),
        Option('Export Load Balancers', export_loadbalancer, 'Load Balancers'),
        Option('Export Management Services', export_management_services, 'Management Services'),
        Option('Export Developer Services', export_developer_services, 'Development Services'),
        Option('Export Software-Defined Data Centers - OCVS', export_sddc, 'OCVS'),
        Option('CD3 Services', cd3_services, 'CD3 Services')

    ]

else:
    inputs = [
        Option('Validate CD3', validate_cd3, 'Validate CD3'),
        Option('Identity', create_identity, 'Identity'),
        Option('Tags', create_tags, 'Tagging'),
        Option('Network', create_network, 'Network'),
        Option('OCI Firewall', create_validate_firewall_service, 'Firewall'),
        Option('DNS Management', create_dns, 'DNS Management'),
        Option('Compute', create_compute, 'Compute'),
        Option('Storage', create_storage, 'Storage'),
        Option('Database', create_databases, 'Databases'),
        Option('Load Balancers', create_loadbalancer, 'Load Balancers'),
        Option('Management Services', create_management_services, 'Management Services'),
        Option('Developer Services', create_developer_services, 'Developer Services'),
        Option('Logging Services', create_logging, 'Logging Services'),
        Option('Software-Defined Data Centers - OCVS', create_sddc, 'Processing SDDC Tabs'),
        Option('CIS Compliance Features', create_cis_features, 'CIS Compliance Features'),
        Option('CD3 Services', cd3_services, 'CD3 Services')
    ]
    export_regions = ct.all_regions

if main_options and args.main_options != "":
    options = match_options(inputs, main_options)
    for option in options:
        with section(option.text, header=True):
            option.callback(prim_options=sub_options)
else:
    print("\nChoose appropriate option from below :\n")
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
# write updated paths to a file
updated_paths_file = f'{outdir}/updated_paths.safe'
with open(updated_paths_file, 'w+') as f:
    for item in updated_paths:
        f.write(str(item).replace('//', '/') + "\n")
f.close()
import_scripts_file = f'{outdir}/import_scripts.safe'
with open(import_scripts_file, 'w+') as f:
    for item in import_scripts:
        f.write(str(item).replace('//', '/') + "\n")
f.close()