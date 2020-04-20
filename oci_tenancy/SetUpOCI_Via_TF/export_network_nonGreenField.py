#!/usr/bin/python3


import argparse
import sys
import oci
from oci.core.virtual_network_client import VirtualNetworkClient
from oci.identity import IdentityClient
import os

sys.path.append(os.getcwd() + "/../../..")
from commonTools import *

compartment_ids = {}
importCommands = {}
oci_obj_names = {}


def get_network_compartment_id(config):  # , compartment_name):
    identity = IdentityClient(config)
    comp_list = oci.pagination.list_call_get_all_results(identity.list_compartments, config["tenancy"],
                                                         compartment_id_in_subtree=True)
    compartment_list = comp_list.data

    for compartment in compartment_list:
        if (compartment.lifecycle_state == 'ACTIVE'):
            compartment_ids[compartment.name] = compartment.id
    compartment_ids['root'] = config['tenancy']
    return compartment_ids


def print_nsgsl(region, comp_name, vcn_name, nsg, nsgsl):
    global rows

    tf_name = commonTools.tfname.sub("-", vcn_name + "_" + str(nsg.display_name))
    sportmin = ""
    sportmax = ""
    dportmin = ""
    dportmax = ""
    icmptype = ""
    icmpcode = ""

    if (nsgsl.tcp_options is not None):
        if (nsgsl.tcp_options.source_port_range is not None):
            sportmin = nsgsl.tcp_options.source_port_range.min
            sportmax = nsgsl.tcp_options.source_port_range.max
        if (nsgsl.tcp_options.destination_port_range is not None):
            dportmin = nsgsl.tcp_options.destination_port_range.min
            dportmax = nsgsl.tcp_options.destination_port_range.max
    if (nsgsl.udp_options is not None):
        if (nsgsl.udp_options.source_port_range is not None):
            sportmin = nsgsl.udp_options.source_port_range.min
            sportmax = nsgsl.udp_options.source_port_range.max
        if (nsgsl.udp_options.destination_port_range is not None):
            dportmin = nsgsl.udp_options.destination_port_range.min
            dportmax = nsgsl.udp_options.destination_port_range.max
    if (nsgsl.icmp_options is not None):
        if (nsgsl.icmp_options.type is not None):
            icmptype = nsgsl.icmp_options.type
        if (nsgsl.icmp_options.code is not None):
            icmpcode = nsgsl.icmp_options.code

    protocol = commonTools().protocol_dict[nsgsl.protocol].lower()
    # print (region,comp_name,vcn_name,nsg.display_name, nsgsl.direction, nsgsl.protocol, nsgsl.is_stateless, nsgsl.source_type, nsgsl.source, nsgsl.destination_type, nsgsl.destination,sportmin,sportmax,dportmin,dportmax,icmptype,icmpcode,nsgsl.description)
    new_row = (region, comp_name, vcn_name, nsg.display_name, nsgsl.direction, protocol, nsgsl.is_stateless,
               nsgsl.source_type, nsgsl.source, nsgsl.destination_type, nsgsl.destination, sportmin, sportmax, dportmin,
               dportmax, icmptype, icmpcode, nsgsl.description)
    rows.append(new_row)


#    importCommands[region.lower()].write("\nterraform import oci_core_network_security_group." + str(nsg.display_name) + " "+str(nsg.id))
def print_nsg(region, comp_name, vcn_name, nsg):
    global rows

    tf_name = commonTools.tfname.sub("-", vcn_name + "_" + str(nsg.display_name))
    new_row = (region, comp_name, vcn_name, nsg.display_name, "", "", "", "", "", "", "", "", "", "", "", "", "", "")
    rows.append(new_row)


#  importCommands[region.lower()].write("\nterraform import oci_core_network_security_group." + str(nsg.display_name) + " "+str(nsg.id))

def print_vcns(region, comp_name, vcn, drg_display_name, igw_display_name, ngw_display_name, sgw_display_name,
               lpg_display_names):
    global rows

    # Check to see if DNS is enabled for this VCN
    if (vcn.dns_label is None):
        dns_label = "n"
    else:
        dns_label = vcn.dns_label

    new_row = (
    region, comp_name, vcn.display_name, vcn.cidr_block, drg_display_name, igw_display_name, ngw_display_name,
    sgw_display_name, lpg_display_names, 'exported', dns_label)
    rows.append(new_row)
    tf_name = commonTools.tfname.sub("-", vcn.display_name)
    importCommands[region.lower()].write("\nterraform import oci_core_vcn." + tf_name + " " + str(vcn.id))


def print_dhcp(region, comp_name, vcn_name, dhcp):
    global rows

    tf_name = commonTools.tfname.sub("-", vcn_name + "_" + str(dhcp.display_name))
    # Dont write Default DHCP option to cd3, jst write TF import command

    options = dhcp.options
    server_type = ""
    custom_dns_servers_str = ""
    search_domain_names_str = ""
    for option in options:
        if (option.type == "DomainNameServer"):
            server_type = option.server_type
            custom_dns_servers = option.custom_dns_servers
            for custom_dns_server in custom_dns_servers:
                custom_dns_servers_str = custom_dns_servers_str + "," + custom_dns_server
            if (custom_dns_servers_str != "" and custom_dns_servers_str[0] == ','):
                custom_dns_servers_str = custom_dns_servers_str[1:]
        if (option.type == "SearchDomain"):
            search_domain_names = option.search_domain_names
            search_domain_names_str = search_domain_names[0]

    new_row = (
    region, comp_name, vcn_name, dhcp.display_name, server_type, search_domain_names_str, custom_dns_servers_str)
    rows.append(new_row)
    if ("Default DHCP Options for " in dhcp.display_name):
        importCommands[region.lower()].write(
            "\nterraform import oci_core_default_dhcp_options." + tf_name + " " + str(dhcp.id))
    else:
        importCommands[region.lower()].write("\nterraform import oci_core_dhcp_options." + tf_name + " " + str(dhcp.id))


def print_subnets(region, comp_name, vcn_name, subnet, dhcp_name, rt_name, sl_names, add_def_seclist):
    global rows

    # Get AD
    availability_domain = subnet.availability_domain
    ad = ""
    if (availability_domain == None):
        ad = "Regional"
    elif ("AD-1" in availability_domain):
        ad = "AD1"
    elif ("AD-2" in availability_domain):
        ad = "AD2"
    elif ("AD-3" in availability_domain):
        ad = "AD3"

    # Get public or private
    pvt_pub = subnet.prohibit_public_ip_on_vnic
    access = ""
    if (pvt_pub == True):
        access = "private"
    elif (pvt_pub == False):
        access = "public"

    # Check to see if DNS is enabled for this Subnet
    if (subnet.dns_label is None):
        dns_label = "n"
    else:
        dns_label = subnet.dns_label

    new_row = (
    region, comp_name, vcn_name, subnet.display_name, subnet.cidr_block, ad, access, dhcp_name, rt_name, sl_names,
    add_def_seclist, '-', '-', '-', '-', '-', dns_label)
    rows.append(new_row)
    tf_name = commonTools.tfname.sub("-", vcn_name + "_" + str(subnet.display_name))
    importCommands[region.lower()].write("\nterraform import oci_core_subnet." + tf_name + " " + str(subnet.id))


parser = argparse.ArgumentParser(description="Export Route Table on OCI to CD3")
parser.add_argument("cd3file", help="path of CD3 excel file to export network objects to")
parser.add_argument("outdir", help="path to out directory containing script for TF import commands")
parser.add_argument("--networkCompartment", help="comma seperated Compartments for which to export Networking Objects",
                    required=False)
parser.add_argument("--configFileName", help="Config file name", required=False)

if len(sys.argv) < 3:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()
cd3file = args.cd3file
outdir = args.outdir
input_config_file = args.configFileName
input_compartment_list = args.networkCompartment
if (input_compartment_list is not None):
    input_compartment_names = input_compartment_list.split(",")
else:
    input_compartment_names = None

if ('.xls' not in cd3file):
    print("\nAcceptable cd3 format: .xlsx")
    exit()

if args.configFileName is not None:
    configFileName = args.configFileName
    config = oci.config.from_file(file_location=configFileName)
else:
    config = oci.config.from_file()

ntk_compartment_ids = get_network_compartment_id(config)
# Check Compartments
remove_comps = []
if (input_compartment_names is not None):
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
else:
    print("Fetching for all Compartments...")
print("\nCD3 excel file should not be opened during export process!!!")
print(
    "Tabs- VCNs, VCN Info, Subnets, DHCP, SecRulesinOCI and RouteRulesinOCI would be overwritten during export process!!!\n")

# Fetch Regions
idc = IdentityClient(config)
all_regions = []
regionsubscriptions = idc.list_region_subscriptions(tenancy_id=config['tenancy'])
for rs in regionsubscriptions.data:
    for k, v in commonTools.region_dict.items():
        if (rs.region_name == v):
            all_regions.append(k)

rows = ([], [], [], all_regions)
commonTools.write_to_cd3(rows, cd3file, "VCN Info")

# Create backups
for reg in all_regions:
    if (os.path.exists(outdir + "/" + reg + "/tf_import_commands_network_nonGF.sh")):
        commonTools.backup_file(outdir + "/" + reg, "tf_import_commands_network_nonGF.sh")
    if (os.path.exists(outdir + "/" + reg + "/obj_names.safe")):
        commonTools.backup_file(outdir + "/" + reg, "obj_names.safe")
    importCommands[reg] = open(outdir + "/" + reg + "/tf_import_commands_network_nonGF.sh", "w")
    importCommands[reg].write("#!/bin/bash")
    importCommands[reg].write("\n")
    importCommands[reg].write("terraform init")
    oci_obj_names[reg] = open(outdir + "/" + reg + "/obj_names.safe", "w")

# Fetch VCNs
print("\nFetching VCNs...")
rows = []
for reg in all_regions:
    importCommands[reg].write("\n######### Writing import for VCNs #########\n")
    config.__setitem__("region", commonTools.region_dict[reg])
    vnc = VirtualNetworkClient(config)
    region = reg.capitalize()
    for ntk_compartment_name in ntk_compartment_ids:
        if (input_compartment_names is not None and ntk_compartment_name not in input_compartment_names):
            continue

        vcns = oci.pagination.list_call_get_all_results(vnc.list_vcns,
                                                        compartment_id=ntk_compartment_ids[ntk_compartment_name],
                                                        lifecycle_state="AVAILABLE")
        for vcn in vcns.data:
            vcn_info = vcn
            # Fetch VCN components assuming components are in same comp as VCN
            drg_display_name = "n"
            DRG_Attachments = oci.pagination.list_call_get_all_results(vnc.list_drg_attachments,
                                                                       compartment_id=ntk_compartment_ids[
                                                                           ntk_compartment_name], vcn_id=vcn.id)
            for drg_attachment in DRG_Attachments.data:
                drg_attachment_info = drg_attachment
                drg_attachment_name = drg_attachment_info.display_name
                drg_id = drg_attachment_info.drg_id

                drg_info = vnc.get_drg(drg_id).data
                drg_display_name = drg_info.display_name

                drgattach_route_table_id = drg_attachment_info.route_table_id
                if (drgattach_route_table_id is not None):
                    oci_obj_names[reg].write(
                        "\ndrginfo::::" + vcn_info.display_name + "::::" + drg_display_name + "::::" + vnc.get_route_table(
                            drgattach_route_table_id).data.display_name)
                tf_name = commonTools.tfname.sub("-", drg_display_name)
                importCommands[reg].write("\nterraform import oci_core_drg." + tf_name + " " + drg_info.id)

                tf_name = commonTools.tfname.sub("-", vcn_info.display_name + "_" + drg_attachment_name)
                importCommands[reg].write(
                    "\nterraform import oci_core_drg_attachment." + tf_name + " " + drg_attachment_info.id)
                oci_obj_names[reg].write(
                    "\ndrgattachinfo::::" + vcn_info.display_name + "::::" + drg_display_name + "::::" + drg_attachment_name)

            igw_display_name = "n"
            IGWs = oci.pagination.list_call_get_all_results(vnc.list_internet_gateways,
                                                            compartment_id=ntk_compartment_ids[ntk_compartment_name],
                                                            vcn_id=vcn.id, lifecycle_state="AVAILABLE")
            for igw in IGWs.data:
                igw_info = igw
                igw_display_name = igw_info.display_name
                tf_name = tf_name = commonTools.tfname.sub("-", vcn_info.display_name + "_" + igw_display_name)
                importCommands[reg].write("\nterraform import oci_core_internet_gateway." + tf_name + " " + igw_info.id)

            ngw_display_name = "n"
            NGWs = oci.pagination.list_call_get_all_results(vnc.list_nat_gateways,
                                                            compartment_id=ntk_compartment_ids[ntk_compartment_name],
                                                            vcn_id=vcn.id, lifecycle_state="AVAILABLE")
            for ngw in NGWs.data:
                ngw_info = ngw
                ngw_display_name = ngw_info.display_name
                tf_name = tf_name = commonTools.tfname.sub("-", vcn_info.display_name + "_" + ngw_display_name)
                importCommands[reg].write("\nterraform import oci_core_nat_gateway." + tf_name + " " + ngw_info.id)

            sgw_display_name = "n"
            SGWs = oci.pagination.list_call_get_all_results(vnc.list_service_gateways,
                                                            compartment_id=ntk_compartment_ids[ntk_compartment_name],
                                                            vcn_id=vcn.id, lifecycle_state="AVAILABLE")
            for sgw in SGWs.data:
                sgw_info = sgw
                sgw_display_name = sgw_info.display_name
                tf_name = tf_name = commonTools.tfname.sub("-", vcn_info.display_name + "_" + sgw_display_name)
                importCommands[reg].write("\nterraform import oci_core_service_gateway." + tf_name + " " + sgw_info.id)

            lpg_display_names = ""
            LPGs = oci.pagination.list_call_get_all_results(vnc.list_local_peering_gateways,
                                                            compartment_id=ntk_compartment_ids[ntk_compartment_name],
                                                            vcn_id=vcn.id)
            for lpg in LPGs.data:
                if (lpg.lifecycle_state != "AVAILABLE"):
                    continue
                lpg_info = lpg
                lpg_display_names = lpg_info.display_name + "," + lpg_display_names

                lpg_route_table_id = lpg_info.route_table_id
                if (lpg_route_table_id is not None):
                    oci_obj_names[region.lower()].write(
                        "\nlpginfo::::" + vcn_info.display_name + "::::" + lpg_info.display_name + "::::" + vnc.get_route_table(
                            lpg_route_table_id).data.display_name)

                tf_name = commonTools.tfname.sub("-", vcn_info.display_name + "_" + lpg_info.display_name)
                importCommands[reg].write(
                    "\nterraform import oci_core_local_peering_gateway." + tf_name + " " + lpg_info.id)

            if (lpg_display_names == ""):
                lpg_display_names = "n"
            elif (lpg_display_names[-1] == ','):
                lpg_display_names = lpg_display_names[:-1]

            # Fill VCNs Tab
            print_vcns(region, ntk_compartment_name, vcn_info, drg_display_name, igw_display_name, ngw_display_name,
                       sgw_display_name, lpg_display_names)

commonTools.write_to_cd3(rows, cd3file, "VCNs")
# commonTools.write_to_cd3(df_vcn,cd3file,"VCNs")
print("VCNs exported to CD3\n")

# Fetch NSGs
rows = []
print("\nFetching NSG...")
for reg in all_regions:
    importCommands[reg].write("\n\n######### Writing import for NSG #########\n\n")
    config.__setitem__("region", commonTools.region_dict[reg])
    vnc = VirtualNetworkClient(config)
    region = reg.capitalize()
    for ntk_compartment_name in ntk_compartment_ids:
        vcns = oci.pagination.list_call_get_all_results(vnc.list_vcns,
                                                        compartment_id=ntk_compartment_ids[ntk_compartment_name],
                                                        lifecycle_state="AVAILABLE")
        for vcn in vcns.data:
            vcn_info = vnc.get_vcn(vcn.id).data
            for ntk_compartment_name_again in ntk_compartment_ids:
                if (input_compartment_names is not None and ntk_compartment_name_again not in input_compartment_names):
                    continue
                NSGs = oci.pagination.list_call_get_all_results(vnc.list_network_security_groups,
                                                                compartment_id=ntk_compartment_ids[
                                                                    ntk_compartment_name_again], vcn_id=vcn.id,
                                                                lifecycle_state="AVAILABLE")
                nsglist = [""]
                for nsg in NSGs.data:
                    NSGSLs = vnc.list_network_security_group_security_rules(nsg.id)
                    for nsgsl in NSGSLs.data:
                        nsglist.append(nsg.id)
                        print_nsgsl(region, ntk_compartment_name_again, vcn_info.display_name, nsg, nsgsl)
                    if (nsg.id not in nsglist):
                        print_nsg(region, ntk_compartment_name_again, vcn_info.display_name, nsg)
commonTools.write_to_cd3(rows, cd3file, "NSGs")
print("NSGs exported to CD3\n")

# Fetch DHCP
rows = []
print("\nFetching DHCP...")
for reg in all_regions:
    importCommands[reg].write("\n\n######### Writing import for DHCP #########\n\n")
    config.__setitem__("region", commonTools.region_dict[reg])
    vnc = VirtualNetworkClient(config)
    region = reg.capitalize()
    for ntk_compartment_name in ntk_compartment_ids:
        vcns = oci.pagination.list_call_get_all_results(vnc.list_vcns,
                                                        compartment_id=ntk_compartment_ids[ntk_compartment_name],
                                                        lifecycle_state="AVAILABLE")
        for vcn in vcns.data:
            vcn_info = vnc.get_vcn(vcn.id).data
            for ntk_compartment_name_again in ntk_compartment_ids:
                if (input_compartment_names is not None and ntk_compartment_name_again not in input_compartment_names):
                    continue
                DHCPs = oci.pagination.list_call_get_all_results(vnc.list_dhcp_options,
                                                                 compartment_id=ntk_compartment_ids[
                                                                     ntk_compartment_name_again], vcn_id=vcn.id,
                                                                 lifecycle_state="AVAILABLE")
                for dhcp in DHCPs.data:
                    dhcp_info = dhcp
                    print_dhcp(region, ntk_compartment_name_again, vcn_info.display_name, dhcp_info)

commonTools.write_to_cd3(rows, cd3file, "DHCP")
print("DHCP exported to CD3\n")

# Fetch Subnets
rows = []
print("\nFetching Subnets...")
for reg in all_regions:
    importCommands[reg].write("\n\n######### Writing import for Subnets #########\n\n")
    config.__setitem__("region", commonTools.region_dict[reg])
    vnc = VirtualNetworkClient(config)
    region = reg.capitalize()
    for ntk_compartment_name in ntk_compartment_ids:
        vcns = oci.pagination.list_call_get_all_results(vnc.list_vcns,
                                                        compartment_id=ntk_compartment_ids[ntk_compartment_name],
                                                        lifecycle_state="AVAILABLE")
        for vcn in vcns.data:
            vcn_info = vnc.get_vcn(vcn.id).data
            for ntk_compartment_name_again in ntk_compartment_ids:
                if (input_compartment_names is not None and ntk_compartment_name_again not in input_compartment_names):
                    continue

                Subnets = oci.pagination.list_call_get_all_results(vnc.list_subnets, compartment_id=ntk_compartment_ids[
                    ntk_compartment_name_again], vcn_id=vcn.id, lifecycle_state="AVAILABLE")
                for subnet in Subnets.data:
                    subnet_info = subnet
                    dhcp_id = subnet_info.dhcp_options_id
                    dhcp_name = vnc.get_dhcp_options(dhcp_id).data.display_name
                    if ("Default DHCP Options for " in dhcp_name):
                        dhcp_name = ""

                    rt_id = subnet_info.route_table_id
                    rt_name = vnc.get_route_table(rt_id).data.display_name
                    if ("Default Route Table for " in rt_name):
                        rt_name = "n"

                    sl_ids = subnet_info.security_list_ids
                    sl_names = ""
                    add_def_seclist = 'n'
                    for sl_id in sl_ids:
                        sl_name = vnc.get_security_list(sl_id).data.display_name
                        if ("Default Security List for " in sl_name):
                            add_def_seclist = 'y'
                            continue
                        sl_names = sl_name + "," + sl_names
                    if (sl_names == ""):
                        sl_names = "n"
                    elif (sl_names != "" and sl_names[-1] == ','):
                        sl_names = sl_names[:-1]
                    # Fill Subnets tab
                    print_subnets(region, ntk_compartment_name_again, vcn_info.display_name, subnet_info, dhcp_name,
                                  rt_name, sl_names, add_def_seclist)

commonTools.write_to_cd3(rows, cd3file, "Subnets")
print("Subnets exported to CD3\n")

for reg in all_regions:
    importCommands[reg].close()
    oci_obj_names[reg].close()

# Fetch RouteRules and SecRules
rows = []
os.chdir('CoreInfra/Networking/BaseNetwork')
if (input_compartment_list is None):
    if (input_config_file is None):
        command_sl = 'python exportSeclist.py ' + cd3file + " --tf_import_cmd true --outdir " + outdir
        command_rt = 'python exportRoutetable.py ' + cd3file + " --tf_import_cmd true --outdir " + outdir
    else:
        command_sl = 'python exportSeclist.py ' + cd3file + ' --tf_import_cmd true --outdir ' + outdir + ' --configFileName ' + input_config_file
        command_rt = 'python exportRoutetable.py ' + cd3file + ' --tf_import_cmd true --outdir ' + outdir + ' --configFileName ' + input_config_file
else:
    if (input_config_file is None):
        command_sl = 'python exportSeclist.py ' + cd3file + " --tf_import_cmd true --outdir " + outdir + " --networkCompartment " + input_compartment_list
        command_rt = 'python exportRoutetable.py ' + cd3file + " --tf_import_cmd true --outdir " + outdir + " --networkCompartment " + input_compartment_list
    else:
        command_sl = 'python exportSeclist.py ' + cd3file + ' --tf_import_cmd true --outdir ' + outdir + ' --configFileName ' + input_config_file + " --networkCompartment " + input_compartment_list
        command_rt = 'python exportRoutetable.py ' + cd3file + ' --tf_import_cmd true --outdir ' + outdir + ' --configFileName ' + input_config_file + " --networkCompartment " + input_compartment_list

os.system(command_sl)
print("SecRules exported to CD3\n")

rows = []
os.system(command_rt)
print("RouteRules exported to CD3\n")

os.chdir("../../..")

for reg in all_regions:
    importCommands[reg] = open(outdir + "/" + reg + "/tf_import_commands_network_nonGF.sh", "a")
    importCommands[reg].write("\n\nterraform plan")
    importCommands[reg].write("\n")
    importCommands[reg].close()


