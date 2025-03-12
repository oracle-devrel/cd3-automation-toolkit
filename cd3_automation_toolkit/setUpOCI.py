import argparse
import configparser
import json
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
import CostManagement
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
        pattern1 = re.compile("Enable(.*)Logs")
        pattern2 = re.compile("(.*)DR Plan")
        for option in options:
            if option.name == "Execute All":
                continue
            if option.name in ['Security Rules', 'Route Rules', 'DRG Route Rules', 'Network Security Groups','Customer Connectivity'] and devops:
                with section(option.text):
                    option.callback(*args, **kwargs,sub_options=sub_child_options)
            # Logging function
            elif pattern1.match(str(option.name)) !=None:
                with section(option.text):
                    option.callback(*args, **kwargs, option=option.name)
            elif pattern2.match(str(option.name)) !=None:
                with section(option.text):
                    option.callback(*args, **kwargs, option=option.name)
            else:
                with section(option.text):
                    option.callback(*args, **kwargs)

def get_tags_list(resource_name=[]):
    if devops:
        input_tags_list = ct.tag_filter
    else:
        if resource_name == []:
            resource_name = 'OCI resources'
        tags_list_str = "\nEnter tags (comma separated without spaces if multiple) for {} which you want to export; Press 'Enter' to export all resources - eg TagNameSpace.TagKey1=TagValue1,TagNameSpace.TagKey2=TagValue2 : "
        input_tags_list = input(tags_list_str.format(resource_name))

    input_tags_list = list(map(lambda x: x.strip(), input_tags_list.split(','))) if input_tags_list else []
    return input_tags_list


def get_region_list(rm,vizoci):
    if rm == False and vizoci==False:
        if devops:
            input_region_names = ct.reg_filter
        else:
            resource_name = 'OCI resources'
            region_list_str = "\nEnter region (comma separated without spaces if multiple) for which you want to export {}; Identity and Tags will be exported from Home Region.\nPress 'Enter' to export from all the subscribed regions - eg ashburn,phoenix: "
            input_region_names = input(region_list_str.format(resource_name))
    elif rm == True and vizoci == False:
        if devops:
            input_region_names = ct.orm_reg_filter
        else:
            resource_name = 'Terraform Stack'
            region_list_str = "\nEnter region (comma separated without spaces if multiple) for which you want to upload {} - eg ashburn,phoenix,global: "
            input_region_names = input(region_list_str.format(resource_name))
    elif vizoci == True and rm == False:
        if devops:
            input_region_names = ct.vizoci_reg_filter
        else:
            resource_name = 'VizOCI'
            region_list_str = "\nEnter region (comma separated without spaces if multiple) for which you want to run {} - eg ashburn,phoenix: "
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
            all_items = glob.glob(path_value + "/*")
            items = []
            for f in all_items:
                actual_file = f.split("/")[-1]
                if actual_file.startswith("variables") or actual_file.endswith(".tf_backup"):
                    continue
                items.append(f)
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
    home_region_services = ['identity', 'tagging', 'budget', 'quota']
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
    compartments_file_data = ""
    comp_done = []
    for k,v in ct.ntk_compartment_ids.items():
        if v not in comp_done:
            compartments_file_data += k + "\n"
            comp_done.append(v)
        k = commonTools.check_tf_variable(k)
        v = "\"" + v + "\""
        compocidsStr = "\t" + k + " = " + v + "\n" + compocidsStr

    f = open(outdir + "/../.config_files/compartments_file", "w+")
    f.write(compartments_file_data[:-1])
    f.close()
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
    fetch_comp_file = f'{outdir}/.safe/fetchcompinfo.safe'
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
        Option("Validate Budgets", None, None),
        Option("Validate Network(VCNs, SubnetsVLANs, DHCP, DRGs)", None, None),
        Option("Validate DNS", None, None),
        Option("Validate Instances", None, None),
        Option("Validate Block Volumes", None, None),
        Option("Validate FSS", None, None),
        Option("Validate Buckets", None, None),
        Option("Validate KMS", None, None)
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

################## Export Functions ##########################
def export_all(prim_options=[]):
    print("\n")
    print("Exports all services supported by CD3 except OCI Network Firewall and Management Services.")
    print("All tabs in input excel sheet will get over written.")
    print("\n")
    export_identityOptions(prim_options=["Export Compartments","Export Groups","Export Policies", "Export Users", "Export Network Sources"])
    export_governance(prim_options=["Export Tags","Export Quotas"])
    export_cost_management(prim_options=['Export Budgets'])
    export_network(prim_options=["Export all Network Components"])
    export_dns_management(prim_options=["Export DNS Views/Zones/Records","Export DNS Resolvers"],export_all=True)
    export_compute(prim_options=["Export Dedicated VM Hosts","Export Instances (excludes instances launched by OKE)"],export_all=True)
    export_storage(prim_options=["Export Block Volumes/Block Backup Policy","Export File Systems","Export Object Storage Buckets"],export_all=True)
    export_databases(prim_options=["Export Virtual Machine or Bare Metal DB Systems","Export EXA Infra and EXA VMClusters",'Export ADBs'])
    export_loadbalancer(prim_options=["Export Load Balancers","Export Network Load Balancers"])
    export_developer_services(prim_options=["Export OKE cluster and Nodepools"])
    export_security(prim_options=["Export KMS (Keys/Vaults)"])
    print("-------------------------------------------------Exporting SDDCs  ---------------------------------------------------")
    export_sddc(prim_options=[])

def export_identityOptions(prim_options=[]):
    options = [Option("Export Compartments", export_compartments, 'Exporting Compartments'),
               Option("Export Groups",export_groups, 'Exporting Groups'),
               Option("Export Policies", export_policies, 'Exporting Policies'),
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


def export_compartments(inputfile, outdir,config, signer, ct):
    resource = 'Compartments'
    Identity.export_identity(inputfile, outdir, service_dir_identity,resource, config, signer, ct)
    options = [Option(None, create_compartments, 'Processing Compartments Tab'), ]
    execute_options(options)
    print("\n\nExecute import_commands_compartments.sh script created under home region directory to synch TF with OCI Identity Compartments\n")

def export_policies(inputfile, outdir,config, signer, ct):
    resource = 'IAM Policies'
    #compartments = ct.get_compartment_map(var_file, resource)
    Identity.export_identity(inputfile, outdir, service_dir_identity,resource, config, signer, ct, export_compartments=compartments)
    options = [Option(None, create_policies, 'Processing Policies Tab'), ]
    execute_options(options)
    print("\n\nExecute import_commands_policies.sh script created under home region directory to synch TF with OCI " +resource +"\n")

def export_groups(inputfile, outdir,config, signer, ct):
    resource = 'IAM Groups'
    selected_domains_data = ct.get_identity_domain_data(config, signer, resource,var_file)
    Identity.export_identity(inputfile, outdir, service_dir_identity,resource, config, signer, ct, export_domains=selected_domains_data)
    options = [Option(None, create_groups, 'Processing Groups Tab'), ]
    execute_options(options)
    print("\n\nExecute import_commands_groups.sh script created under home region directory to synch TF with OCI " +resource +"\n")


def export_users(inputfile, outdir,config,signer, ct):
    resource = 'IAM Users'
    # check if tenancy is identity_domain enabled
    selected_domains_data = ct.get_identity_domain_data(config, signer, resource,var_file)
    Identity.Users.export_users(inputfile, outdir, service_dir_identity, config, signer, ct,export_domains=selected_domains_data)
    options = [Option(None, Identity.Users.create_terraform_users, 'Processing Users Tab'), ]
    execute_options(options,inputfile, outdir,service_dir_identity, prefix, ct)
    print("\n\nExecute import_commands_users.sh script created under home region directory to synch TF with OCI " +resource +"\n")


def export_networkSources(inputfile, outdir, config, signer, ct):
    resource = 'Network Sources'
    Identity.NetworkSources.export_networkSources(inputfile, outdir, service_dir_identity, config, signer, ct)
    options = [Option(None, Identity.NetworkSources.create_terraform_networkSources, 'Processing NetworkSources Tab'), ]
    execute_options(options, inputfile, outdir, service_dir_identity, prefix, ct)
    print("\n\nExecute import_commands_networkSources.sh script created under home region directory to synch TF with OCI " +resource +"\n")

def export_governance(prim_options=[]):
    options = [
    Option('Export Tags', export_tags, 'Exporting Tags'),
    Option('Export Quotas', export_quotas, 'Exporting Quotas')]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options)

def export_tags(prim_options=[]):
    #compartments = ct.get_compartment_map(var_file, 'Tagging Objects')
    Governance.export_tags_nongreenfield(inputfile, outdir, service_dir_tagging, config, signer, ct, export_compartments=compartments)
    options = [Option(None, create_tags, 'Processing Tags Tab'), ]
    execute_options(options)
    print("\n\nExecute import_commands_tags.sh script created under home region directory to synch TF with OCI Tags\n")
    # Update modified path list
    update_path_list(regions_path=[ct.home_region], service_dirs=[service_dir_tagging])

def export_quotas(prim_options=[]):
    Governance.export_quotas_nongreenfield(inputfile, outdir, service_dir_quota, config, signer, ct, export_tags=export_tags_list)
    options = [Option(None, create_quotas, 'Processing Quotas Tab'), ]
    execute_options(options)
    print("\n\nExecute import_commands_quotas.sh script created under home region directory to synch TF with OCI Quota\n")
    # Update modified path list
    update_path_list(regions_path=[ct.home_region], service_dirs=[service_dir_quota])


def export_cost_management(prim_options=[]):
    options = [
    Option('Export Budgets', export_budget, 'Exporting Budgets')]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options)

def export_budget(prim_options=[]):
    CostManagement.export_budgets_nongreenfield(inputfile, outdir, service_dir_budget, config, signer, ct,export_regions,export_tags_list)
    options = [Option(None, create_budgets, 'Processing Budgets Tab')]
    execute_options(options)
    print("\n\nExecute import_commands_budgets.sh script created under each region directory to synch TF with OCI Tags\n")
    # Update modified path list
    update_path_list(regions_path=[ct.home_region], service_dirs=[service_dir_budget])

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
    execute_options(options, inputfile, outdir, config, signer, ct, export_regions,export_tags_list)

    print("=====================================================================================================================")
    print("NOTE: Make sure to execute import_commands_network_major-objects.sh before executing the other scripts.")
    print("=====================================================================================================================")

    # Update modified path list
    regions_path = export_regions.copy()
    regions_path.append("global")
    service_dirs = [service_dir_network, service_dir_nsg, service_dir_vlan,'rpc']
    update_path_list(regions_path=regions_path, service_dirs=service_dirs)

def export_networking(inputfile, outdir,config, signer, ct, export_regions,export_tags_list):
    service_dirs = []
    service_dir = outdir_struct
    #compartments = ct.get_compartment_map(var_file,'Network Objects')
    Network.export_networking(inputfile, outdir, service_dir,config, signer, ct, export_compartments=compartments, export_regions=export_regions,export_tags=export_tags_list)
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
    print("\n\nExecute import_commands_network_*.sh script created under each region directory to synch TF with OCI Network objects\n")
    for service in [service_dir_network,service_dir_vlan,service_dir_nsg]:
        service_dirs.append(service_dir_network) if service_dir_network not in service_dirs else service_dirs

def export_major_objects(inputfile, outdir, config, signer, ct, export_regions,export_tags_list):
    #compartments = ct.get_compartment_map(var_file,'VCN Major Objects')
    Network.export_major_objects(inputfile, outdir, service_dir_network, config, signer, ct, export_compartments=compartments, export_regions=export_regions,export_tags=export_tags_list)
    Network.export_drg_routetable(inputfile, outdir, service_dir_network, config, signer, ct, export_compartments=compartments, export_regions=export_regions,export_tags=export_tags_list, _tf_import_cmd=True)
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

    print("\n\nExecute import_commands_network_major-objects.sh and import_commands_network_drg_routerules.sh scripts created under each region directory to synch TF with OCI Network objects\n")

def export_dhcp(inputfile, outdir,config,signer,ct,export_regions,export_tags_list):
    #compartments = ct.get_compartment_map(var_file,'DHCP')
    Network.export_dhcp(inputfile, outdir, service_dir_network,config, signer, ct, export_compartments=compartments, export_regions=export_regions,export_tags=export_tags_list)
    options = [
        Option(None, Network.create_terraform_dhcp_options, 'Processing DHCP Tab'),
        ]
    execute_options(options, inputfile, outdir, service_dir_network,prefix, ct, non_gf_tenancy)
    print("\n\nExecute import_commands_network_dhcp.sh script created under each region directory to synch TF with OCI Network objects\n")

def export_secrules(inputfile, outdir,config,signer,ct,export_regions,export_tags_list):
    #compartments = ct.get_compartment_map(var_file,'SecRulesInOCI')
    Network.export_seclist(inputfile, outdir, service_dir_network, config, signer, ct, export_compartments=compartments, export_regions=export_regions, export_tags=export_tags_list,_tf_import_cmd=True)
    options = [
        Option(None, Network.modify_terraform_secrules, 'Processing SecRulesinOCI Tab'),
        ]
    execute_options(options, inputfile, outdir,service_dir_network, prefix, ct, non_gf_tenancy)
    print("\n\nExecute import_commands_network_secrules.sh script created under each region directory to synch TF with OCI Network objects\n")

def export_routerules(inputfile, outdir,config,signer,ct,export_regions,export_tags_list):
    #compartments = ct.get_compartment_map(var_file,'RouteRulesInOCI')
    Network.export_routetable(inputfile, outdir, service_dir_network, config, signer, ct, export_compartments=compartments, export_regions=export_regions, export_tags=export_tags_list,_tf_import_cmd=True)
    options = [
        Option(None, Network.modify_terraform_routerules, 'Processing RouteRulesinOCI Tab'),
        ]
    execute_options(options, inputfile, outdir, service_dir_network,prefix, ct, non_gf_tenancy)
    print("\n\nExecute import_commands_network_routerules.sh script created under each region directory to synch TF with OCI Network objects\n")


def export_subnets_vlans(inputfile, outdir,config,signer,ct,export_regions,export_tags_list):
    service_dir = outdir_struct
    #compartments = ct.get_compartment_map(var_file,'Subnets')
    Network.export_subnets_vlans(inputfile, outdir, service_dir,config, signer, ct, export_compartments=compartments, export_regions=export_regions,export_tags=export_tags_list)
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

    print("\n\nExecute import_commands_network_subnets.sh script created under each region directory to synch TF with OCI Network objects")
    print("\nExecute import_commands_network_vlans.sh script created under each region directory to synch TF with OCI Network objects\n")


def export_nsg(inputfile, outdir,config,signer,ct,export_regions,export_tags_list):
    #compartments = ct.get_compartment_map(var_file,'NSGs')
    Network.export_nsg(inputfile, outdir,service_dir_nsg, config,signer,ct, export_compartments=compartments, export_regions=export_regions, export_tags=export_tags_list,_tf_import_cmd=True)
    options = [
        Option(None, Network.create_terraform_nsg, 'Processing NSGs Tab'),
        ]
    execute_options(options, inputfile, outdir, service_dir_nsg,prefix, ct)
    print("\n\nExecute import_commands_network_nsg.sh script created under each region directory to synch TF with OCI Network objects\n")


def export_firewall_policies(prim_options=[]):
    options = [Option("Export Firewall Policy", export_firewallpolicy,'Exporting Firewall Policy Objects'),
               Option("Export Firewall", export_firewalls,'Exporting Firewalls')]

    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, config, signer, ct, export_regions,export_tags_list)
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_firewall])

def export_firewallpolicy(inputfile, outdir, config, signer, ct, export_regions,export_tags_list,name_filter=""):
    #compartments = ct.get_compartment_map(var_file, 'Firewall Policies')
    filter_str1 = "Enter comma separated list of display name patterns of the Policies or press \"ENTER\" to export all policies: "
    if not devops:
        policy_name_str = input(filter_str1)
    else:
        policy_name_str = ct.fwl_pol_pattern_filter if ct.fwl_pol_pattern_filter else None

    policies = list(map(lambda x: x.strip(), policy_name_str.split(','))) if policy_name_str else None
    Security.export_firewallpolicy(inputfile, outdir, service_dir_firewall, config,signer,ct, export_compartments=compartments, export_regions=export_regions,export_tags=export_tags_list,export_policies=policies)
    create_firewall_policy(inputfile, outdir, service_dir_firewall, prefix, ct,execute_all=True)
    print("\n\nExecute import_commands_firewallpolicy.sh script created under each region directory to synch TF with OCI Firewall policy objects\n")

def export_firewalls(inputfile, outdir, config, signer, ct, export_regions,export_tags_list):
    #compartments = ct.get_compartment_map(var_file, 'Firewalls')
    Security.export_firewall(inputfile, outdir, service_dir_firewall, config,signer,ct, export_compartments=compartments, export_regions=export_regions, export_tags=export_tags_list)
    create_firewall(inputfile, outdir, service_dir_firewall, prefix, ct)
    print("\n\nExecute import_commands_firewall.sh script created under each region directory to synch TF with OCI Firewall policy objects\n")


def export_compute(prim_options=[],export_all=False):
    options = [Option("Export Dedicated VM Hosts", export_dedicatedvmhosts, 'Exporting Dedicated VM Hosts'),
               Option("Export Instances (excludes instances launched by OKE)", export_instances, 'Exporting Instances')]

    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, config, signer, ct, export_regions,export_tags_list,export_all)

def export_dedicatedvmhosts(inputfile, outdir, config, signer, ct, export_regions,export_tags_list,export_all):
    #compartments = ct.get_compartment_map(var_file,'Dedicated VM Hosts')
    Compute.export_dedicatedvmhosts(inputfile, outdir, service_dir_dedicated_vm_host, config, signer, ct, export_compartments=compartments, export_regions=export_regions, export_tags = export_tags_list)
    #create_compute(prim_options=['Add/Modify/Delete Dedicated VM Hosts'])
    options = [Option(None, create_dedicatedvmhosts, 'Processing Dedicated VM Hosts Tab'),]
    execute_options(options)

    print("\n\nExecute import_commands_dedicatedvmhosts.sh script created under each region directory to synch TF with OCI Dedicated VM Hosts\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_dedicated_vm_host])


def export_instances(inputfile, outdir,config,signer, ct, export_regions,export_tags_list,export_all):
    #compartments = ct.get_compartment_map(var_file,'Instances')
    print("Enter values for below filters to restrict the export for Instances; Press 'Enter' to use empty value for the filter")
    filter_str1 = "Enter comma separated list of display name patterns of the instances: "
    filter_str2 = "Enter comma separated list of ADs of the instances eg AD1,AD2,AD3: "
    if not devops:
        if export_all==True:
            display_name_str=None
            ad_name_str=None
        else:
            display_name_str = input(filter_str1)
            ad_name_str = input(filter_str2)
    else:
        display_name_str = ct.ins_pattern_filter if ct.ins_pattern_filter else None
        ad_name_str = ct.ins_ad_filter if ct.ins_ad_filter else None

    display_names =  list(map(lambda x: x.strip(), display_name_str.split(','))) if display_name_str else None
    ad_names = list(map(lambda x: x.strip(), ad_name_str.split(','))) if ad_name_str else None

    Compute.export_instances(inputfile, outdir, service_dir_instance,config,signer,ct, export_compartments=compartments, export_regions=export_regions, export_tags = export_tags_list, display_names = display_names, ad_names = ad_names)
    options = [Option(None, create_instances, 'Processing Instances Tab'), ]
    execute_options(options)
    print("\n\nExecute import_commands_instances.sh script created under each region directory to synch TF with OCI Instances\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_instance])


def export_storage(prim_options=[],export_all=False):
    options = [Option("Export Block Volumes/Block Backup Policy",export_block_volumes,'Exporting Block Volumes'),
               Option("Export File Systems", export_fss, 'Exporting FSS'),
               Option("Export Object Storage Buckets", export_buckets, 'Exporting Object Storage Buckets')]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, config, signer, ct, export_regions,export_tags_list,export_all)

def export_block_volumes(inputfile, outdir,config,signer,ct, export_regions,export_tags_list,export_all):
    #compartments = ct.get_compartment_map(var_file,'Block Volumes')
    print("Enter values for below filters to restrict the export for Block Volumes; Press 'Enter' to use empty value for the filter")
    filter_str1 = "Enter comma separated list of display name patterns of the Block Volumes: "
    filter_str2 = "Enter comma separated list of ADs of the Block Volumes eg AD1,AD2,AD3: "
    if not devops:
        if export_all==True:
            display_name_str=None
            ad_name_str=None
        else:
            display_name_str = input(filter_str1)
            ad_name_str = input(filter_str2)
    else:
        display_name_str = ct.bv_pattern_filter if ct.bv_pattern_filter else None
        ad_name_str = ct.bv_ad_filter if ct.bv_ad_filter else None

    display_names = list(map(lambda x: x.strip(), display_name_str.split(','))) if display_name_str else None
    ad_names = list(map(lambda x: x.strip(), ad_name_str.split(','))) if ad_name_str else None

    Storage.export_blockvolumes(inputfile, outdir, service_dir_block_volume, config,signer,ct, export_compartments=compartments, export_regions=export_regions, export_tags = export_tags_list, display_names = display_names, ad_names = ad_names)
    options = [Option(None, create_block_volumes, 'Processing BlockVolumes Tab'), ]
    execute_options(options)
    print("\n\nExecute import_commands_blockvolumes.sh script created under each region directory to synch TF with OCI Block Volume Objects\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_block_volume])


def export_fss(inputfile, outdir,config, signer, ct, export_regions,export_tags_list,export_all):
    #compartments = ct.get_compartment_map(var_file,'FSS objects')
    Storage.export_fss(inputfile, outdir, service_dir_fss, config,signer,ct, export_compartments=compartments, export_regions=export_regions,export_tags = export_tags_list)
    options = [Option(None, create_fss, 'Processing FSS Tab'), ]
    execute_options(options)
    print("\n\nExecute import_commands_fss.sh script created under each region directory to synch TF with OCI FSS objects\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_fss])


def export_buckets(inputfile, outdir, config, signer, ct, export_regions,export_tags_list,export_all):
    #compartments = ct.get_compartment_map(var_file, 'Buckets')
    Storage.export_buckets(inputfile, outdir, service_dir_object_storage, config,signer,ct, export_compartments=compartments, export_regions=export_regions,export_tags = export_tags_list)
    options = [Option(None, create_buckets, 'Processing Buckets Tab'), ]
    execute_options(options)
    print("\n\nExecute import_commands_buckets.sh script created under each region directory to synch TF with OCI Object Storage Buckets\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_object_storage])


def export_loadbalancer(prim_options=[]):
    options = [Option("Export Load Balancers", export_lbr,'Exporting LBaaS Objects'),
               Option("Export Network Load Balancers", export_nlb,'Exporting NLB Objects')]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, config, signer, ct, export_regions,export_tags_list)

def export_lbr(inputfile, outdir,config, signer, ct, export_regions,export_tags_list):
    #compartments = ct.get_compartment_map(var_file,'LBR objects')
    Network.export_lbr(inputfile, outdir, service_dir_loadbalancer, config,signer,ct, export_compartments=compartments, export_regions=export_regions,export_tags=export_tags_list)
    options = [Option(None, create_lb, 'Processing LBaaS Tabs'), ]
    execute_options(options)
    print("\n\nExecute import_commands_lbr.sh script created under each region directory to synch TF with OCI LBR objects\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_loadbalancer])


def export_nlb(inputfile, outdir,config,signer, ct, export_regions,export_tags_list):
    #compartments = ct.get_compartment_map(var_file,'NLB objects')
    Network.export_nlb(inputfile, outdir, service_dir_networkloadbalancer, config,signer,ct, export_compartments=compartments, export_regions=export_regions,export_tags=export_tags_list)
    options = [Option(None, create_nlb, 'Processing NLB Tabs'), ]
    execute_options(options)
    print("\n\nExecute import_commands_nlb.sh script created under each region directory to synch TF with OCI NLB objects\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_networkloadbalancer])

def export_security(prim_options=[]):
    options = [Option("Export KMS (Keys/Vaults)", export_kms,'Exporting KMS Objects (Keys/Vaults)')]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, config, signer, ct, export_regions,export_tags_list)

def export_kms(inputfile, outdir, config, signer, ct, export_regions,export_tags_list):
    #compartments = ct.get_compartment_map(var_file, 'KMS')
    Security.export_keyvaults(inputfile, outdir, service_dir_kms, config,signer,ct, export_compartments=compartments, export_regions=export_regions,export_tags=export_tags_list)
    options = [Option(None, create_kms, 'Processing KMS Tab')]
    execute_options(options)
    print("\n\nExecute import_commands_kms.sh script created under each region directory to synch TF with OCI Key Vaults\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_kms])


def export_databases(prim_options=[]):
    options = [Option("Export Virtual Machine or Bare Metal DB Systems",export_dbsystems_vm_bm,'Exporting VM and BM DB Systems'),
               Option("Export EXA Infra and EXA VMClusters", export_exa_infra_vmclusters, 'Exporting EXA Infra and EXA VMClusters'),
                Option('Export ADBs', export_adbs, 'Exporting Autonomous Databases'),
               Option('Export MysqlDBs', export_mysqlDBs, 'Exporting MySql Databases')]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, config, signer, ct, export_regions,export_tags_list)

def export_dbsystems_vm_bm(inputfile, outdir,config,signer, ct,export_regions,export_tags_list):
    #compartments = ct.get_compartment_map(var_file,'VM and BM DB Systems')
    Database.export_dbsystems_vm_bm(inputfile, outdir, service_dir_dbsystem_vm_bm, config,signer,ct, export_compartments=compartments, export_regions= export_regions,export_tags=export_tags_list)
    options = [Option(None, create_dbsystems_vm_bm, 'Processing DBSystems-VM-BM Tab')]
    execute_options(options)
    print("\n\nExecute import_commands_dbsystems-vm-bm.sh script created under each region directory to synch TF with DBSystems\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_dbsystem_vm_bm])


def export_exa_infra_vmclusters(inputfile, outdir,config, signer, ct, export_regions, export_tags_list):
    #compartments = ct.get_compartment_map(var_file,'EXA Infra and EXA VMClusters')
    Database.export_exa_infra(inputfile, outdir, service_dir_database_exacs, config,signer,ct, export_compartments=compartments, export_regions= export_regions,export_tags = export_tags_list)
    Database.export_exa_vmclusters(inputfile, outdir, service_dir_database_exacs, config,signer,ct, export_compartments=compartments, export_regions= export_regions, export_tags=export_tags_list)
    options = [Option(None, create_exa_infra_vmclusters, '')]
    execute_options(options)
    print("\n\nExecute import_commands_exa-infra.sh and import_commands_exa-vmclusters.sh scripts created under each region directory to synch TF with Exa-Infra and Exa-VMClusters\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_database_exacs])


def export_adbs(inputfile, outdir,config, signer, ct, export_regions,export_tags_list):
    #compartments = ct.get_compartment_map(var_file,'ADBs')
    Database.export_adbs(inputfile, outdir, service_dir_adb, config,signer,ct, export_compartments=compartments, export_regions= export_regions, export_tags=export_tags_list)
    options = [Option(None, create_adb, 'Processing ADB Tab')]
    execute_options(options)
    print("\n\nExecute import_commands_adb.sh script created under each region directory to synch TF with OCI ADBs\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_adb])

def export_mysql(inputfile, outdir, config, signer, ct, export_regions):
    compartments = ct.get_compartment_map(var_file, 'mysql-dbsystem')  # Keep using var_file like ADB
    Database.export_mysql(inputfile, outdir, service_dir_mysql_dbsystem, config,signer,ct, export_compartments=compartments, export_regions= export_regions)
    print("\n\nExecute import_commands_mysql-dbsystem.sh script created under each region directory to synch TF with OCI MySQLs\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_mysql_dbsystem])

def export_mysql_configuration(inputfile, outdir, config, signer, ct, export_regions):
    compartments = ct.get_compartment_map(var_file, 'mysql-configuration')  # Keep using var_file like ADB
    Database.export_mysql_configuration(inputfile, outdir, service_dir_mysql_dbsystem, config,signer,ct, export_compartments=compartments, export_regions= export_regions)
    options = [Option(None, Database.create_terraform_mysql_configuration, 'Processing MySQL configuration Tab')]
    execute_options(options, inputfile, outdir, service_dir_mysql_dbsystem, setUpOCI_props.get('Default', 'prefix').strip(), ct)
    print("\n\nExecute import_commands_mysql_configuration.sh script created under each region directory to synch TF with OCI MySQL Configurations\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_mysql_dbsystem])

def export_mysqlDBs(inputfile=None, outdir=None, config=None, signer=None, ct=None, export_regions=None, prim_options=[]):
    options = [Option("Export Mysql DB system", export_mysql,'Exporting Mysql DB system'),
               Option("Export Mysql Configuration", export_mysql_configuration, 'Exporting Mysql Configuration')]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, config, signer, ct, export_regions)

def export_management_services(prim_options=[]):
    options = [Option("Export Notifications",export_notifications,'Exporting Notifications'),
               Option("Export Events", export_events,'Exporting Events'),
               Option("Export Alarms", export_alarms, 'Exporting Alarms'),
               Option("Export Service Connectors", export_service_connectors, 'Exporting Service Connectors')]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, service_dir_managementservices, config, signer, ct, export_regions, export_tags_list)
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_managementservices])


def export_notifications(inputfile, outdir, service_dir, config, signer, ct, export_regions, export_tags_list):
    compartments = ct.get_compartment_map(var_file,'Notifications')
    ManagementServices.export_notifications(inputfile, outdir, service_dir, config,signer,ct, export_compartments=compartments, export_regions=export_regions,export_tags=export_tags_list)
    create_management_services(prim_options=['Add/Modify/Delete Notifications'])
    print("\n\nExecute import_commands_notifications.sh script created under each region directory to synch TF with OCI Notifications\n")

def export_events(inputfile, outdir, service_dir, config, signer, ct, export_regions,export_tags_list):
    #compartments = ct.get_compartment_map(var_file,'Events')
    ManagementServices.export_events(inputfile, outdir, service_dir, config,signer,ct, export_compartments=compartments, export_regions=export_regions, export_tags=export_tags_list)
    create_management_services(prim_options=['Add/Modify/Delete Events'])
    print("\n\nExecute import_commands_events.sh script created under each region directory to synch TF with OCI Events\n")

def export_alarms(inputfile, outdir, service_dir, config, signer, ct, export_regions, export_tags_list):
    #compartments = ct.get_compartment_map(var_file,'Alarms')
    ManagementServices.export_alarms(inputfile, outdir, service_dir, config,signer,ct,  export_compartments=compartments, export_regions=export_regions, export_tags=export_tags_list)
    create_management_services(prim_options=['Add/Modify/Delete Alarms'])
    print("\n\nExecute import_commands_alarms.sh script created under each region directory to synch TF with OCI Alarms\n")

def export_service_connectors(inputfile, outdir, service_dir, config, signer, ct, export_regions,export_tags_list):
    #compartments = ct.get_compartment_map(var_file,'Service Connectors')
    ManagementServices.export_service_connectors(inputfile, outdir, service_dir, config,signer,ct, export_compartments=compartments, export_regions=export_regions,export_tags=export_tags_list)
    create_management_services(prim_options=['Add/Modify/Delete ServiceConnectors'])
    print("\n\nExecute import_commands_serviceconnectors.sh script created under each region directory to synch TF with OCI Service Connectors\n")

def export_developer_services(prim_options=[]):
    options = [Option("Export OKE cluster and Nodepools", export_oke, 'Exporting OKE'),
               ]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, config, signer, ct, export_regions,export_tags_list)

def export_oke(inputfile, outdir, config,signer, ct, export_regions,export_tags_list):
    #compartments = ct.get_compartment_map(var_file,'OKE')
    DeveloperServices.export_oke(inputfile, outdir, service_dir_oke,config,signer,ct, export_compartments=compartments, export_regions=export_regions, export_tags=export_tags_list)
    options = [Option(None, create_oke, 'Processing OKE Tab')]
    execute_options(options,inputfile, outdir, prefix, '', '', ct)
    print("\n\nExecute import_commands_oke.sh script created under each region directory to synch TF with OKE\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_oke])


def export_sddc(prim_options=[]):
    #compartments = ct.get_compartment_map(var_file,'SDDCs')
    SDDC.export_sddc(inputfile, outdir, service_dir_sddc,config,signer,ct, export_compartments=compartments, export_regions=export_regions,export_tags=export_tags_list)
    SDDC.create_terraform_sddc(inputfile, outdir, service_dir_sddc, prefix, ct)
    print("\n\nExecute import_commands_sddcs.sh script created under each region directory to synch TF with SDDC\n")
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_sddc])

def export_dns_management(prim_options=[],export_all=False):
    options = [Option("Export DNS Views/Zones/Records", export_dns_views_zones_rrsets,
                      'Exporting DNS Views/Zones/Records'),
               Option("Export DNS Resolvers", export_dns_resolvers, 'Exporting DNS Resolvers')
               ]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, service_dir_dns, config, signer, ct, export_regions,export_tags_list,export_all)
    # Update modified path list
    update_path_list(regions_path=export_regions, service_dirs=[service_dir_dns])


def export_dns_views_zones_rrsets(inputfile, outdir, service_dir, config, signer, ct, export_regions,export_tags_list,export_all):
    #compartments = ct.get_compartment_map(var_file, 'DNS Views ,attached zones and rrsets')
    filter_str1 = "Do you want to export default views/zones/records (y|n), Default is n: "
    if not devops:
        if export_all==True:
            dns_filter = "n"
        else:
            dns_filter = "n" if input(filter_str1).lower() != 'y' else "y"
    else:
        dns_filter = None
        if ct.default_dns:
            if ct.default_dns.lower() == "false":
                dns_filter = "n"
            if ct.default_dns.lower() == "true":
                dns_filter = "y"
        dns_filter = dns_filter if dns_filter else None
    Network.export_dns_views_zones_rrsets(inputfile, outdir, service_dir, config, signer, ct, dns_filter=dns_filter, export_compartments=compartments, export_regions=export_regions,export_tags=export_tags_list)
    options = [Option(None, create_dns, 'Processing DNS-Views-Zones-Records Tab')]
    execute_options(options)
def export_dns_resolvers(inputfile, outdir, service_dir, config, signer, ct, export_regions, export_tags_list,export_all):
    #compartments = ct.get_compartment_map(var_file, 'DNS Resolvers')
    Network.export_dns_resolvers(inputfile, outdir, service_dir, config, signer, ct, export_compartments=compartments, export_regions=export_regions,export_tags=export_tags_list)
    options = [Option(None, create_dns_resolvers, 'Processing DNS-Resolvers Tab')]
    execute_options(options)

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

def create_compartments():
    errors = False
    if (workflow_type == 'create_resources'):
        choices = [Option("Validate Compartments", None, None)]
        errors = cd3Validator.validate_cd3(choices, inputfile, var_file, prefix, outdir, ct)
    if errors == False:
        Identity.create_terraform_compartments(inputfile, outdir, service_dir_identity, prefix, ct)
        # Update modified path list
        update_path_list(regions_path=[ct.home_region], service_dirs=[service_dir_identity])
    else:
        print("Please correct the errors in CD3 Sheet and try again. Exiting!!!")
        exit(1)

def create_groups():
    errors = False
    if (workflow_type == 'create_resources'):
        choices = [Option("Validate Groups", None, None)]
        errors = cd3Validator.validate_cd3(choices, inputfile, var_file, prefix, outdir, ct)
    if errors == False:
        Identity.create_terraform_groups(inputfile, outdir, service_dir_identity, prefix, ct)
        # Update modified path list
        update_path_list(regions_path=[ct.home_region], service_dirs=[service_dir_identity])
    else:
        print("Please correct the errors in CD3 Sheet and try again. Exiting!!!")
        exit(1)

def create_policies():
    errors = False
    if (workflow_type == 'create_resources'):
        choices = [Option("Validate Policies", None, None)]
        errors = cd3Validator.validate_cd3(choices, inputfile, var_file, prefix, outdir, ct)

    if errors == False:
        Identity.create_terraform_policies(inputfile, outdir, service_dir_identity, prefix, ct)
        # Update modified path list
        update_path_list(regions_path=[ct.home_region], service_dirs=[service_dir_identity])
    else:
        print("Please correct the errors in CD3 Sheet and try again. Exiting!!!")
        exit(1)

def create_users():
    Identity.create_terraform_users(inputfile, outdir, service_dir_identity, prefix, ct)
    # Update modified path list
    update_path_list(regions_path=[ct.home_region], service_dirs=[service_dir_identity])


def create_networksources():
    Identity.NetworkSources.create_terraform_networkSources(inputfile, outdir, service_dir_identity, prefix, ct)
    # Update modified path list
    update_path_list(regions_path=[ct.home_region], service_dirs=[service_dir_identity])


def create_identity(prim_options=[]):
    ct.identity_domain_check(config,signer)
    options = [
        Option('Add/Modify/Delete Compartments', create_compartments, 'Processing Compartments Tab'),
        Option('Add/Modify/Delete Groups', create_groups, 'Processing Groups Tab'),
        Option('Add/Modify/Delete Policies', create_policies, 'Processing Policies Tab'),
        Option('Add/Modify/Delete Users', create_users, 'Processing Users Tab'),
        Option('Add/Modify/Delete Network Sources', create_networksources, 'Processing NetworkSources Tab')
    ]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options)
    # Update modified path list
    #update_path_list(regions_path=[ct.home_region], service_dirs=[service_dir_identity])



def create_governance(prim_options=[]):
    options = [
    Option('Tags', create_tags, 'Processing Tags Tab'),
    Option('Quotas', create_quotas, 'Processing Quotas Tab')]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options)


def create_tags():
    errors = False
    if (workflow_type == 'create_resources'):
        choices = [Option("Validate Tags", None, None)]
        errors = cd3Validator.validate_cd3(choices, inputfile, var_file, prefix, outdir, ct)

    if errors == False:
        Governance.create_terraform_tags(inputfile, outdir, service_dir_tagging, prefix, ct)
        # Update modified path list
        update_path_list(regions_path=[ct.home_region], service_dirs=[service_dir_tagging])
    else:
        print("Please correct the errors in CD3 Sheet and try again. Exiting!!!")
        exit(1)

def create_quotas():
    Governance.create_terraform_quotas(inputfile, outdir, service_dir_quota, prefix, ct)
    # Update modified path list
    update_path_list(regions_path=[ct.home_region], service_dirs=[service_dir_quota])

def create_cost_management(prim_options=[]):
    options = [
    Option('Budgets', create_budgets, 'Processing Budgets Tab')]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options)


def create_budgets():
    errors = True
    if (workflow_type == 'create_resources'):
        choices = [Option("Validate Budgets", None, None)]
        errors = cd3Validator.validate_cd3(choices, inputfile, var_file, prefix, outdir, ct)

    if errors == True:
        CostManagement.create_terraform_budgets(inputfile, outdir, service_dir_budget, prefix, ct)
        # Update modified path list
        update_path_list(regions_path=[ct.home_region], service_dirs=[service_dir_budget])
    else:
        print("Please correct the errors in CD3 Sheet and try again. Exiting!!!")
        exit(1)

def create_network(execute_all=False,prim_options=[]):
    service_dir = outdir_struct
    options = [
            Option('Create Network', create_terraform_network, 'Create All Objects'),
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
    service_dirs = [service_dir_network,service_dir_nsg, service_dir_vlan, 'rpc']
    update_path_list(regions_path=regions_path, service_dirs=service_dirs)
def create_terraform_network(inputfile, outdir, service_dir,  prefix, ct, non_gf_tenancy):
    errors = False
    if (workflow_type == 'create_resources'):
        choices = [Option("Validate Network(VCNs, SubnetsVLANs, DHCP, DRGs)", None, None)]
        errors = cd3Validator.validate_cd3(choices, inputfile, var_file, prefix, outdir, ct)

    if errors == False:
        Network.create_all_tf_objects(inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy=non_gf_tenancy)
    else:
        print("Please correct the errors in CD3 Sheet and try again. Exiting!!!")
        exit(1)


def modify_terraform_network(inputfile, outdir, service_dir,  prefix, ct, non_gf_tenancy):
    errors = False
    if (workflow_type == 'create_resources'):
        choices = [Option("Validate Network(VCNs, SubnetsVLANs, DHCP, DRGs)", None, None)]
        errors = cd3Validator.validate_cd3(choices, inputfile, var_file, prefix, outdir, ct)

    if errors == False:
        Network.create_all_tf_objects(inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy=non_gf_tenancy,  modify_network=True, )
    else:
        print("Please correct the errors in CD3 Sheet and try again. Exiting!!!")
        exit(1)

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
    export_tags_list = get_tags_list('OCI Security Rules')
    Network.export_seclist(inputfile, outdir, service_dir, config, signer, ct, export_compartments=compartments, export_regions= export_regions, export_tags=export_tags_list, _tf_import_cmd=False)

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
    export_tags_list = get_tags_list('OCI Route Rules')
    Network.export_routetable(inputfile, outdir, service_dir, config, signer, ct, export_compartments=compartments, export_regions= export_regions, export_tags=export_tags_list,_tf_import_cmd=False)

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
    export_tags_list = get_tags_list('OCI DRG Route Rules')
    Network.export_drg_routetable(inputfile, outdir, service_dir, config, signer, ct, export_compartments=compartments, export_regions= export_regions, export_tags=export_tags_list,_tf_import_cmd=False)


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
    export_tags_list = get_tags_list('OCI NSGs')
    Network.export_nsg(inputfile, outdir, service_dir, config, signer, ct, export_compartments=compartments, export_regions= export_regions, export_tags=export_tags_list, _tf_import_cmd=False)

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
    options = [
        Option('Add/Modify/Delete Dedicated VM Hosts', create_dedicatedvmhosts, 'Processing Dedicated VM Hosts Tab'),
        Option('Add/Modify/Delete Instances/Boot Backup Policy', create_instances,'Processing Instances Tab'),
    ]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options)


def create_instances():
    errors = False
    if (workflow_type == 'create_resources'):
        choices = [Option("Validate Instances", None, None)]
        errors = cd3Validator.validate_cd3(choices, inputfile, var_file, prefix, outdir, ct)

    if errors == False:
        Compute.create_terraform_instances(inputfile, outdir, service_dir_instance, prefix, ct)
        # Update modified path list
        update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_instance])
    else:
        print("Please correct the errors in CD3 Sheet and try again. Exiting!!!")
        exit(1)

def create_dedicatedvmhosts():
    Compute.create_terraform_dedicatedhosts(inputfile, outdir, service_dir_dedicated_vm_host, prefix, ct)
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_dedicated_vm_host])


def create_storage(execute_all=False,prim_options=[]):
    options = [
        Option('Add/Modify/Delete Block Volumes/Block Backup Policy', create_block_volumes, 'Processing BlockVolumes Tab'),
        Option('Add/Modify/Delete File Systems', create_fss, 'Processing FSS Tab'),
        Option('Add/Modify/Delete Object Storage Buckets', create_buckets, 'Processing Buckets Tab')
        #Option('Enable Object Storage Buckets Write Logs', create_cis_oss_logs, '')
    ]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    if not execute_all:
        execute_options(options)

def create_block_volumes():
    errors = False
    if (workflow_type == 'create_resources'):
        choices = [Option("Validate Block Volumes", None, None)]
        errors = cd3Validator.validate_cd3(choices, inputfile, var_file, prefix, outdir, ct)

    if errors == False:
        Storage.create_terraform_block_volumes(inputfile, outdir, service_dir_block_volume, prefix, ct)
        # Update modified path list
        update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_block_volume])
    else:
        print("Please correct the errors in CD3 Sheet and try again. Exiting!!!")
        exit(1)

def create_fss():
    errors = False
    if (workflow_type == 'create_resources'):
        choices = [Option("Validate FSS", None, None)]
        errors = cd3Validator.validate_cd3(choices, inputfile, var_file, prefix, outdir, ct)

    if errors == False:
        Storage.create_terraform_fss(inputfile, outdir, service_dir_fss, prefix, ct)
        # Update modified path list
        update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_fss])
    else:
        print("Please correct the errors in CD3 Sheet and try again. Exiting!!!")
        exit(1)


def create_buckets():
    errors = False
    if (workflow_type == 'create_resources'):
        choices = [Option("Validate Buckets", None, None)]
        errors = cd3Validator.validate_cd3(choices, inputfile, var_file, prefix, outdir, ct)

    if errors == False:
        Storage.create_terraform_oss(inputfile, outdir, service_dir_object_storage, prefix, ct)
        # Update modified path list
        update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_object_storage])
    else:
        print("Please correct the errors in CD3 Sheet and try again. Exiting!!!")
        exit(1)

def create_loadbalancer(execute_all=False,prim_options=[]):
    options = [
        Option('Add/Modify/Delete Load Balancers', create_lb, 'Processing LBaaS Tabs'),
        Option('Add/Modify/Delete Network Load Balancers', create_nlb, 'Processing NLB Tabs')
        #Option('Enable LBaaS Logs', enable_lb_logs, 'LBaaS Logs')
    ]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    if not execute_all:
        execute_options(options)

def create_lb():
    options = [
         Option(None, Network.create_terraform_lbr_hostname_certs, 'Creating LBR'),
         Option(None, Network.create_backendset_backendservers, 'Creating Backend Sets and Backend Servers'),
         Option(None, Network.create_listener, 'Creating Listeners'),
         Option(None, Network.create_path_route_set, 'Creating Path Route Sets'),
         Option(None, Network.create_ruleset, 'Creating Rule Sets'),
         Option(None, Network.create_lb_routing_policy, 'Creating Routing Policies'),
    ]
    execute_options(options, inputfile, outdir, service_dir_loadbalancer, prefix, ct)
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_loadbalancer])


def create_nlb():
    options = [
         Option(None, Network.create_terraform_nlb_listener, 'Creating NLB and Listeners'),
         Option(None, Network.create_nlb_backendset_backendservers, 'Creating NLB Backend Sets and Backend Servers'),
    ]
    execute_options(options, inputfile, outdir, service_dir_networkloadbalancer, prefix, ct)
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_networkloadbalancer])

def create_databases(execute_all=False,prim_options=[]):
    options = [
        Option('Add/Modify/Delete Virtual Machine or Bare Metal DB Systems', create_dbsystems_vm_bm, 'Processing DBSystems-VM-BM Tab'),
        Option('Add/Modify/Delete EXA Infra and EXA VM Clusters', create_exa_infra_vmclusters, ''),
        Option('Add/Modify/Delete ADBs', create_adb, 'Processing ADB Tab'),
        Option('Add/Modify/Delete MysqlDBs', create_mysql,'Processing Mysql Tab'),
    ]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        if not execute_all:
            options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options)

def create_dbsystems_vm_bm():
    Database.create_terraform_dbsystems_vm_bm(inputfile, outdir, service_dir_dbsystem_vm_bm, prefix, ct)
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_dbsystem_vm_bm])


def create_exa_infra_vmclusters():
    options = [Option(None, Database.create_terraform_exa_infra, 'Processing Exa-Infra Tab'),
               Option(None, Database.create_terraform_exa_vmclusters, 'Processing Exa-VM-Clusters Tab')]
    execute_options(options, inputfile, outdir, service_dir_database_exacs, prefix, ct)
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_database_exacs])


def create_adb():
    Database.create_terraform_adb(inputfile, outdir, service_dir_adb, prefix, ct)
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_adb])

def create_mysql(execute_all=False,prim_options=[]):
    options = [
        Option('Add/Modify/Delete MysqlDBs', Database.create_terraform_mysql, 'Processing MysqlDBs'),
        Option('Add/Modify/Delete Mysql Configuration', Database.create_terraform_mysql_configuration, 'Processing Mysql Configuration'),
    ]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        if not execute_all:
            options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, service_dir_mysql_dbsystem, prefix, ct)
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_mysql_dbsystem])


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
    if tf_or_tofu == 'terraform':
        options = [
            Option("Upload current terraform files/state to Resource Manager", create_rm_stack, 'Creating RM Stack'),
            Option("Add/Modify/Delete OKE Cluster and Nodepools", create_oke, 'Creating OKE cluster and Nodepool')
        ]
    elif tf_or_tofu=='tofu':
        options = [
            Option("Add/Modify/Delete OKE Cluster and Nodepools", create_oke, 'Creating OKE cluster and Nodepool')
        ]

    if prim_options:
        options = match_options(options, prim_options)
    else:
        if not execute_all:
            options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, inputfile, outdir, prefix, auth_mechanism, config_file_path,ct)

def create_rm_stack(inputfile, outdir, prefix, auth_mechanism, config_file, ct):
    regions = get_region_list(rm = True, vizoci = False)
    DeveloperServices.create_resource_manager(outdir,var_file, outdir_struct, prefix, auth_mechanism, config_file, ct, regions)

def create_oke(inputfile, outdir, prefix, dummy1, dummy2, ct):
    DeveloperServices.create_terraform_oke(inputfile, outdir, service_dir_oke, prefix, ct)
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_oke])


def create_sddc(prim_options=[]):
    SDDC.create_terraform_sddc(inputfile, outdir, service_dir_sddc, prefix, ct)
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_sddc])


def create_dns_management(prim_options=[]):
    errors = False
    if (workflow_type == 'create_resources'):
        choices = [Option("Validate DNS", None, None)]
        errors = cd3Validator.validate_cd3(choices, inputfile, var_file, prefix, outdir, ct)

    if errors == False:
        options = [
            Option('Add/Modify/Delete DNS Views/Zones/Records', create_dns,
                   'Processing DNS-Views-Zones-Records Tab'),
            Option('Add/Modify/Delete DNS Resolvers', create_dns_resolvers,
                   'Processing DNS-Resolvers Tab')
        ]
        if prim_options:
            options = match_options(options, prim_options)
        else:
            options = show_options(options, quit=True, menu=True, index=1)
        execute_options(options)
        # Update modified path list
        update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_dns])
    else:
        print("Please correct the errors in CD3 Sheet and try again. Exiting!!!")
        exit(1)


def create_dns():
    Network.create_terraform_dns_views(inputfile, outdir, service_dir_dns, prefix, ct)
    Network.create_terraform_dns_zones(inputfile, outdir, service_dir_dns, prefix, ct)
    Network.create_terraform_dns_rrsets(inputfile, outdir, service_dir_dns, prefix, ct)

def create_dns_resolvers():
    Network.create_terraform_dns_resolvers(inputfile, outdir, service_dir_dns, prefix, ct)

def create_logging(prim_options=[]):
    options = [
        Option('Enable VCN Flow Logs', ManagementServices.enable_service_logging, 'VCN Flow Logs'),
        Option('Enable LBaaS Logs', ManagementServices.enable_service_logging, 'LBaaS Logs'),
        Option('Enable Object Storage Buckets Logs', ManagementServices.enable_service_logging, 'OSS Logs'),
        Option('Enable File Storage Logs', ManagementServices.enable_service_logging, 'File Storage Logs'),
        Option('Enable Network Firewall Logs', ManagementServices.enable_service_logging, 'Network Firewall Logs')
    ]
    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)

    for option in options:
        options1=[]
        if option == "m" or option == 'q':
            service_dir=''
        elif option.name == 'Enable VCN Flow Logs':
            service_dir=service_dir_network
        elif option.name == 'Enable LBaaS Logs':
            service_dir = service_dir_loadbalancer
        elif option.name == 'Enable Object Storage Buckets Logs':
            service_dir = service_dir_object_storage
        elif option.name == 'Enable File Storage Logs':
            service_dir = service_dir_fss
        elif option.name == 'Enable Network Firewall Logs':
            service_dir = service_dir_firewall

        options1.append(option)
        execute_options(options1, inputfile, outdir, prefix, ct, service_dir)
        update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir])

def create_kms():
    errors = False
    if (workflow_type == 'create_resources'):
        choices = [Option("Validate KMS", None, None)]
        errors = cd3Validator.validate_cd3(choices, inputfile, var_file, prefix, outdir, ct)
    if errors == False:
        Security.create_terraform_keyvaults(inputfile, outdir, service_dir_kms, prefix, ct)
        # Update modified path list
        update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_kms])
    else:
        print("Please correct the errors in CD3 Sheet and try again. Exiting!!!")
        exit(1)
def create_security_services(prim_options=[]):
    options = [Option("Add/Modify/Delete KMS (Keys/Vaults)", create_kms, 'Processing KMS Tab'),
               Option("Enable Cloud Guard", enable_cis_cloudguard, 'Enabling Cloud Guard')]

    if prim_options:
        options = match_options(options, prim_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options)
    for option in options:
        if option.name == 'Add/Modify/Delete KMS (Keys/Vaults)':
            update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_kms])


def run_utility(prim_options=[]):
    options = [Option('CIS Compliance Check Script', initiate_cis_scan, 'CIS Compliance Check Script'),
               Option('ShowOCI Report', run_showoci, 'ShowOCI Report'),
               Option('OCI FSDR', run_oci_fsdr, 'OCI FSDR')
    ]
    if prim_options:
        options = match_options(options, prim_options)
        execute_options(options, outdir, prefix, config_file_path,sub_options=sub_child_options)

    else:
        options = show_options(options, quit=True, menu=True, index=1)
        execute_options(options, outdir, prefix, config_file_path)

"""def create_cis_keyvault(*args,**kwargs):

    options = [Option(None, Security.create_cis_keyvault, 'Creating KeyVault')]
    execute_options(options, outdir, service_dir_kms, service_dir_identity,prefix, ct, region_name, comp_name)
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_kms])"""


def enable_cis_cloudguard():
    if not devops:
        region = input("Enter Reporting Region for Cloud Guard eg london: ")
    else:
        region = ct.cg_region
    region = region.lower()
    Security.enable_cis_cloudguard(outdir, service_dir_cloud_guard, prefix, ct, region)
    # Update modified path list
    update_path_list(regions_path=subscribed_regions, service_dirs=[service_dir_cloud_guard])


def initiate_cis_scan(outdir, prefix, config_file,sub_options=[]):
    options = [
        Option("Download latest compliance checking script", start_cis_download, 'Downloading CIS Script'),
        Option("Execute compliance checking script", start_cis_scan, 'Executing CIS Script'),
    ]
    if sub_options:
        options = match_options(options, sub_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, outdir, prefix, config_file)

def start_cis_download(outdir, prefix, config_file):
    current_dir=os.path.dirname(os.path.abspath(__file__))
    print("Downloading the script file as 'cis_reports.py' at location "+current_dir+"/../othertools/")
    resp = requests.get("https://raw.githubusercontent.com/oracle-quickstart/oci-cis-landingzone-quickstart/main/scripts/cis_reports.py")
    resp_contents = resp.text
    with open(current_dir+"/../othertools/cis_reports.py", "w", encoding="utf-8") as fd:
        fd.write(resp_contents)

    #cmdpath = os.path.dirname(os.path.abspath(__file__)) + "/../"
    #shutil.move(os.getcwd()+"/../othertools/cis_reports.py", os.getcwd()+"/../othertools/cis_reports.py")
    print("Download complete!!")

def start_cis_scan(outdir, prefix, config_file):
    cmdpath =  os.path.dirname(os.path.abspath(__file__))+ "/../othertools/"
    cmd = "python "+cmdpath+"cis_reports.py"

    if auth_mechanism == "instance_principal":
        cmd += " -ip"
    elif auth_mechanism == "session_token":
        cmd += " -st"
    else:
        cmd += " -c "+config_file
    if not devops:
        user_input = input("Enter command to execute the script. Press Enter to execute {} : ".format(cmd))
        if user_input!='':
            cmd = "{}".format(user_input)
    split = str.split(cmd)
    dirname = prefix + "_cis_report"
    resource = "cis_report"
    if outdir[len(outdir)-1]=="/":
        outdir=outdir.rsplit("/",2)[0]+"/othertools_files"
    else:
        outdir = outdir.rsplit("/", 1)[0] + "/othertools_files"
    out_rep = outdir + '/'+ dirname
    #config = "--config "+ config

    commonTools.backup_file(outdir, resource, dirname)
    if not os.path.exists(out_rep):
        os.makedirs(out_rep)

    out = ['--report-directory', out_rep]
    cmd = cmd +" "+ out[0] + " "+out[1]
    split.extend(out)
    print("Executing: "+cmd)
    print("Scan started!")
    execute(split, config_file)

def get_latest_showoci(outdir, prefix,config_file):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print("Getting latest showoci report script at location "+current_dir+"/../othertools/")

    cmdpath=os.path.dirname(os.path.abspath(__file__)) + "/../othertools/"
    tag= "oci-python-sdk"

    if (os.path.isdir(cmdpath+tag)):
        shutil.rmtree(cmdpath+tag)
    cmd = "git clone https://github.com/oracle/oci-python-sdk "+cmdpath+tag
    split = str.split(cmd)
    execute(split, config_file)
    #shutil.move("/tmp/oci-python-sdk", cmdpath+tag)
    print("Download complete!!")


def execute_showoci(outdir, prefix, config_file_path):
    cmdpath = os.path.dirname(os.path.abspath(__file__)) + "/../othertools/"
    tag = "oci-python-sdk"
    if not os.path.isfile(cmdpath+tag+"/examples/showoci/showoci.py"):
        get_latest_showoci(outdir, prefix, config_file=config_file_path)
    cmd = "python "+cmdpath+tag+"/examples/showoci/showoci.py -a"

    if auth_mechanism == "instance_principal":
        cmd += " -ip"
    elif auth_mechanism == "session_token":
        cmd += " -is"
    else:
        cmd += " -cf "+config_file_path
    split = str.split(cmd)

    dirname = prefix + "_showoci_report"
    resource = "showoci_report"
    if outdir[len(outdir) - 1] == "/":
        outdir = outdir.rsplit("/", 2)[0] + "/othertools_files"
    else:
        outdir = outdir.rsplit("/", 1)[0] + "/othertools_files"
    out_rep = outdir + '/' + dirname
    # config = "--config "+ config

    commonTools.backup_file(outdir, resource, dirname)
    if not os.path.exists(out_rep):
        os.makedirs(out_rep)
    out_file = out_rep+"/"+prefix
    out = ['-csv', out_file]
    cmd = cmd + " " + out[0] + " " + out[1]
    split.extend(out)
    print("Executing: " + cmd)
    execute(split, config_file_path)



def run_showoci(outdir, prefix, config_file,sub_options=[]):
    options = [
        Option("Download Latest ShowOCI Script", get_latest_showoci, 'Downloading ShowOCI Script'),
        Option("Execute ShowOCI Script", execute_showoci, 'Executing ShowOCI Script'),
    ]
    if sub_options:
        options = match_options(options, sub_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, outdir, prefix, config_file)

def run_vizoci(outdir, prefix, config_file,sub_options=[]):
    cmdpath = os.path.dirname(os.path.abspath(__file__)) + "/../othertools/"
    tag = "vizoci"
    cwd= os.getcwd()
    os.chdir(cmdpath + tag)
    cmd = "python " + "vizoci-gather.py"

    export_regions = get_region_list(rm=False,vizoci=True)
    reg_list = []
    for reg in export_regions:
        reg_list.append(ct.region_dict[reg])

    compartments = ct.get_compartment_map(var_file, 'VizOCI')
    comp_list=[]
    for comp in compartments:
        if '::' in comp:
            comp=comp.replace("::",".")
        comp_list.append("root."+comp)

    filter_str1 = "Do you also want to generate graphs (y/n), Default is n: "

    if not devops:
        graph_gen = "n" if input(filter_str1).lower() != 'y' else "y"
    else:
        graph_gen = None
        if ct.generate_graphs:
            if ct.generate_graphs.lower() == "false":
                graph_gen = "n"
            if ct.generate_graphs.lower() == "true":
                graph_gen = "y"
        graph_gen = graph_gen if graph_gen else None


    dirname = prefix + "_vizoci_report"
    resource = "vizoci_report"
    if outdir[len(outdir) - 1] == "/":
        outdir = outdir.rsplit("/", 2)[0] + "/othertools_files"
    else:
        outdir = outdir.rsplit("/", 1)[0] + "/othertools_files"
    out_rep = outdir + '/' + dirname
    # config = "--config "+ config

    commonTools.backup_file(outdir, resource, dirname)
    if not os.path.exists(out_rep):
        os.makedirs(out_rep)

    config = oci.config.from_file(file_location=config_file_path)
    with open('config/vizociconfig.json', 'r') as json_file:
        json_data = json.load(json_file)

    json_data['vizocidir'] = out_rep
    json_data['home-region'] = ct.region_dict[ct.home_region]
    json_data['tenantocid'] = config['tenancy']
    json_data['regions'] = reg_list
    json_data['compartments'] = comp_list

    if auth_mechanism == 'api_key':
        json_data['ociconfig']['authtype'] = 'APIKEY'
        json_data['ociconfig']['apikeyinfo']['filelocation'] = config_file
    if auth_mechanism == 'instance_principal':
        json_data['ociconfig']['authtype'] = 'INSTANCE'

    with open('config/vizociconfig.json', 'w') as f:
        json.dump(json_data, f, indent=2)

    split = str.split(cmd)
    print("Executing: " + cmd)
    execute(split, config_file_path)

    print("\n\nVizOCI Data Gather Completed.")

    if graph_gen is not None and graph_gen.lower()=='y':
        print("Proceeding with Graph Generation...\n\n")
        cmd = "python " + "vizoci-graph-gen.py"
        split = str.split(cmd)
        print("Executing: " + cmd)
        execute(split, config_file_path)

    os.chdir(cwd)

def export_update_dr_plan(outdir, prefix, config_file_path,option=''):
    print("Use Excel Template oci-fsdr-plan-template.xlsx at /cd3user/oci_tools/othertools/oci-fsdr for the export")
    tag = "oci-fsdr"

    if option.lower().__contains__("export"):
        c="export"
        input1 = "Please enter excel file name where DR plan will be exported; Leave blank to create with name '$prefix_" + tag + "-plan.xlsx at /cd3user/tenancies/<prefix>/othertools_files: ': "
        input2 = "Please enter sheet name in the excel where DR plan will be exported(without spaces); Leave blank to create with name 'FSDR-Plan': "

    elif option.lower().__contains__("update"):
        c="update"
        input1 = "Please enter excel file name from where DR plan will be updated; Leave blank to read file with name '$prefix_" + tag + "-plan.xlsx': "
        input2 = "Please enter sheet name in the excel from where DR plan will be updated(without spaces); Leave blank to read sheet with name 'FSDR-Plan': "

    cmdpath = os.path.dirname(os.path.abspath(__file__))+"/../othertools/"+tag+"/"+c+"_drplan.py"

    if not os.path.isfile(cmdpath):
        print(cmdpath+" doesnt exist. Exiitng!!!")
        exit(1)

    input3 = "Please enter DR Plan OCID which needs to be exported/updated: "


    if not devops:
        filename = input(input1)
        sheetname = input(input2)
        fsdrocid = input(input3)

    else:
        if option.lower().__contains__("export"):
            filename = ct.fsdr_ex_filename
            sheetname = ct.fsdr_ex_sheet
            fsdrocid = ct.fsdr_ex_ocid
        elif option.lower().__contains__("update"):
            filename = ct.fsdr_up_filename
            sheetname = ct.fsdr_up_sheet
            fsdrocid = ct.fsdr_up_ocid


    if filename == '':
        filename = prefix + "_"+tag+"-plan.xlsx"
    if sheetname == '':
        sheetname = 'FSDR-Plan'
    if fsdrocid == '':
        print("OCID cannot be empty. Exiting!!!")
        exit(1)

    # Build command to execute
    if outdir[len(outdir) - 1] == "/":
        outdir = outdir.rsplit("/", 2)[0] + "/othertools_files"
    else:
        outdir = outdir.rsplit("/", 1)[0] + "/othertools_files"
    out_file = outdir + '/' + filename

    cmd = "python "+cmdpath+ " "

    if auth_mechanism == "instance_principal":
        cmd += " -i"
    elif auth_mechanism == "session_token":
        cmd += " -t"

    cmd += " -c "+config_file_path

    cmd += " -o " + fsdrocid + " -s \"" + sheetname + "\" -f " + out_file


    if not os.path.exists(outdir):
        os.makedirs(outdir)
    # Take backup of existing excel sheet
    #if option.lower().__contains__("export"):
    #    commonTools.backup_file(outdir, tag, filename)

    split = str.split(cmd)
    print("Executing: " + cmd)
    execute(split, config_file_path)


def run_oci_fsdr(outdir, prefix, config_file,sub_options=[]):
    options = [
        Option("Export DR Plan", export_update_dr_plan, 'Exporting DR Plan'),
        Option("Update DR Plan", export_update_dr_plan, 'Updating DR Plan'),
    ]
    if sub_options:
        options = match_options(options, sub_options)
    else:
        options = show_options(options, quit=True, menu=True, index=1)
    execute_options(options, outdir, prefix, config_file)

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
        if option not in ['m','q'] and (option.name == 'Validate Firewall CD3 Excel'):
            status = cd3FirewallValidator.validate_firewall_cd3(inputfile, var_file, prefix, outdir, config, signer, ct)
            print("Firewall validator completed with "+ str(status))
        elif option not in ['m','q'] and (option.name == 'Add/Modify/Delete Firewall Policy' or option.name == 'Add/Modify/Delete Firewall'):
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
    #print("\n\nExecute import_commands_Firewallpolicy.sh script created under each region directory to synch TF with OCI Firewall policy objects\n")


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
            Option('Execute All', None, 'Processing all tabs related to Firewall-Policy'),
            Option('Add/Modify/Delete Policy', Security.firewallpolicy_create, 'Processing Firewall-Policy Tab'),
            Option('Add/Modify/Delete Service', Security.fwpolicy_create_service,
                   'Processing Firewall-Policy-ServicesList Tab'),
            Option('Add/Modify/Delete Service-list', Security.fwpolicy_create_servicelist,
                   'Processing Firewall-Policy-ServiceList Tab'),
            Option('Add/Modify/Delete Application', Security.fwpolicy_create_apps,
                   'Processing Firewall-Policy-ApplicationList Tab'),
            Option('Add/Modify/Delete Application-list', Security.fwpolicy_create_applicationlist,
                   'Processing Firewall-Policy-ApplicationList Tab'),
            Option('Add/Modify/Delete Address-list', Security.fwpolicy_create_address,
                   'Processing Firewall-Policy-AddressList Tab'),
            Option('Add/Modify/Delete Url-list', Security.fwpolicy_create_urllist,
                   'Processing Firewall-Policy-UrlList Tab'),
            Option('Add/Modify/Delete Security rules', Security.fwpolicy_create_secrules,
                   'Processing Firewall-Policy-SecRule Tab'),
            Option('Add/Modify/Delete Mapped Secrets', Security.fwpolicy_create_secret,
                   'Processing Firewall-Policy-Secret Tab'),
            Option('Add/Modify/Delete Decryption Rules', Security.fwpolicy_create_decryptrules,
                   'Processing Firewall-Policy-DecryptRule Tab'),
            Option('Add/Modify/Delete Decryption Profile', Security.fwpolicy_create_decryptionprofile,
                   'Processing Firewall-Policy-Decryption Tab'),
            Option('Add/Modify/Delete Tunnel Inspection Rules', Security.fwpolicy_create_tunnelinspect,
               'Processing Firewall-Policy-TunnelInspect Tab'),
        ]
    if sub_options and sub_options != ['']:
        options = match_options(options, sub_options)
    else:
        if not execute_all:
            options = show_options(options, quit=True, menu=True, index=1)

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
    tf_or_tofu = setUpOCI_props.get('Default', 'tf_or_tofu').strip().lower()
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
ct.setInputParameters(prefix,outdir,inputfile,tf_or_tofu)

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

# Check for new region subscriptions
region_dir_list =[]
for name in os.listdir(outdir):
    if os.path.isdir(os.path.join(outdir,name)):
        region_dir_list.append(name)

region_dir_not_configured = list(set(ct.all_regions).difference(region_dir_list))

if region_dir_not_configured!=[]:
    #None of the subscribed regions dir exist. Looks like user has not executed createTenancyConfig.py even once
    if list(set(ct.all_regions).difference(region_dir_not_configured)) == []:
        print("Make sure that CD3 container has been connected to the tenancy using createTenancyConfig.py script.")
        print("Follow the documentation link: https://oracle-devrel.github.io/cd3-automation-toolkit/latest/install-cd3/")
        print("Exiting!!!")
        exit(0)

    #New region subscription
    else:
        print("WARNING!!!!!!!!")
        print("Regions "+str(region_dir_not_configured) + " are subscribed to the tenancy but not yet configured with CD3 Automation Toolkit.")
        print("Re-run createTenancyConfig.py with same tenancyconfig.properties used for prefix '"+ prefix+"' to configure new regions with the toolkit.")
        print("Till then OCI resources can not be managed through terraform for them.\n\n")
        ct.all_regions = list(set(ct.all_regions).difference(region_dir_not_configured))

home_region = ct.home_region

## Fetch Region ADs
ct.get_region_ad_dict(config,signer)

# Set service directories as per outdir_structure file
# If single outdir, get service names from /cd3user/oci_tools/cd3_automation_toolkit/user-scripts/.outdir_structure_file.properties
if len(outdir_struct.items())==0:
    single_outdir_config = configparser.RawConfigParser()
    outdir_config_file = os.path.dirname(os.path.abspath(__file__))+"/user-scripts/.outdir_structure_file.properties"
    single_outdir_config.read(outdir_config_file)
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
    fetch_comp_file = f'{outdir}/.safe/fetchcompinfo.safe'
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
    export_regions = get_region_list(rm=False,vizoci=False)
    export_tags_list = get_tags_list()
    compartments = ct.get_compartment_map(var_file, "OCI Resources")
    inputs = [
        Option("Export All OCI Resources", export_all, "OCI Resources"),
        Option('Export Identity', export_identityOptions, 'Identity'),
        Option('Export Governance', export_governance, 'Governance'),
        Option('Export Cost Management', export_cost_management, 'Cost Management'),
        Option('Export Network', export_network, 'Network'),
        Option('Export OCI Firewall', export_firewall_policies, 'OCI Firewall Policy'),
        Option('Export DNS Management', export_dns_management, 'DNS Management'),
        Option('Export Compute', export_compute, 'Compute'),
        Option('Export Storage', export_storage, 'Storage'),
        Option('Export Databases', export_databases, 'Databases'),
        Option('Export Load Balancers', export_loadbalancer, 'Load Balancers'),
        Option('Export Management Services', export_management_services, 'Management Services'),
        Option('Export Developer Services', export_developer_services, 'Development Services'),
        Option('Export Security', export_security, 'Security'),
        Option('Export Software-Defined Data Centers - OCVS', export_sddc, 'OCVS'),
        Option('CD3 Services', cd3_services, 'CD3 Services')

    ]

else:
    inputs = [
        Option('Validate CD3', validate_cd3, 'Validate CD3'),
        Option('Identity', create_identity, 'Identity'),
        Option('Governance', create_governance, 'Governance'),
        Option('Cost Management', create_cost_management, 'Cost Management'),
        Option('Network', create_network, 'Network'),
        Option('OCI Firewall', create_validate_firewall_service, 'Firewall'),
        Option('DNS Management', create_dns_management, 'DNS Management'),
        Option('Compute', create_compute, 'Compute'),
        Option('Storage', create_storage, 'Storage'),
        Option('Database', create_databases, 'Databases'),
        Option('Load Balancers', create_loadbalancer, 'Load Balancers'),
        Option('Management Services', create_management_services, 'Management Services'),
        Option('Developer Services', create_developer_services, 'Developer Services'),
        Option('Security', create_security_services, 'Security Services'),
        Option('Logging Services', create_logging, 'Logging Services'),
        Option('Software-Defined Data Centers - OCVS', create_sddc, 'Processing SDDC Tabs'),
        Option('CD3 Services', cd3_services, 'CD3 Services'),
        Option('Other OCI Tools', run_utility,'Other OCI Tools')
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
            options = show_options(inputs, quit=True, index=0)
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