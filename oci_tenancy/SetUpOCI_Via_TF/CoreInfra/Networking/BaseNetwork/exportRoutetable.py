#!/usr/bin/python3


import argparse
import sys
import oci
from oci.core.virtual_network_client import VirtualNetworkClient
from oci.identity import IdentityClient
import os
sys.path.append(os.getcwd()+"/../../..")
from commonTools import *

def convertNullToNothing(input):
    EMPTY_STRING = ""
    if input is None:
        return EMPTY_STRING
    else:
        return str(input)

onprem_destinations=[]
igw_destinations=[]
ngw_destinations=[]

global ntk_compartment_ids
ntk_compartment_ids = {}

def get_network_compartment_ids(c_id,c_name):
    compartments = idc.list_compartments(compartment_id=c_id,compartment_id_in_subtree =False)
    for c in compartments.data:
        if c.lifecycle_state =="ACTIVE" :
            if(c_name!="root"):
                name=c_name+"::"+c.name
            else:
                name=c.name
            ntk_compartment_ids[name]=c.id
            #Put individual compartment names also in the dictionary
            if(name!=c.name and c.name not in ntk_compartment_ids.keys()):
                ntk_compartment_ids[c.name]=c.id

            get_network_compartment_ids(c.id,name)

def get_network_entity_name(config,network_identity_id):
    vcn1 = VirtualNetworkClient(config)
    if('internetgateway' in network_identity_id):
        igw=vcn1.get_internet_gateway(network_identity_id)
        network_identity_name = "igw:"+igw.data.display_name
        return  network_identity_name

    elif ('servicegateway' in network_identity_id):
        sgw = vcn1.get_service_gateway(network_identity_id)
        network_identity_name = "sgw:"+sgw.data.display_name
        return network_identity_name


    elif ('natgateway' in network_identity_id):
        ngw = vcn1.get_nat_gateway(network_identity_id)
        network_identity_name = "ngw:"+ngw.data.display_name
        return network_identity_name

    elif ('localpeeringgateway' in network_identity_id):
        lpg = vcn1.get_local_peering_gateway(network_identity_id)
        network_identity_name = "lpg:"+lpg.data.display_name
        return network_identity_name

    elif ('drg' in network_identity_id):
        drg = vcn1.get_drg(network_identity_id)
        network_identity_name = "drg:"+drg.data.display_name
        return network_identity_name

        """
    elif ('privateip' in network_identity_id):
        privateip = vcn1.get_private_ip(network_identity_id)
        network_identity_name = "privateip:"+privateip.data.ip_address
        return network_identity_name
        """
    else:
        return network_identity_id

def print_routetables(routetables,region,vcn_name,comp_name):
    global rows

    for routetable in routetables.data:
        rules = routetable.route_rules
        display_name = routetable.display_name
        dn=display_name
        if (tf_import_cmd == "true"):
            tf_name = vcn_name + "_" + dn
            tf_name = commonTools.check_tf_variable(tf_name)

            if ("Default Route Table for " in dn):
                importCommands[region.lower()].write("\nterraform import oci_core_default_route_table." + tf_name + " " + str(routetable.id))
            else:
                importCommands[region.lower()].write("\nterraform import oci_core_route_table." + tf_name + " " + str(routetable.id))

        if(not rules):
            new_row=(region,comp_name,vcn_name,dn,'','','','')
            rows.append(new_row)

        for rule in rules:
            desc = str(rule.description)
            if (desc == "None"):
                desc = ""

            network_entity_id=rule.network_entity_id
            network_entity_name=get_network_entity_name(config,network_entity_id)
            if ('internetgateway' in network_entity_id):
                if (rule.destination not in igw_destinations):
                    igw_destinations.append(rule.destination)
            elif ('natgateway' in network_entity_id):
                if (rule.destination not in ngw_destinations):
                    ngw_destinations.append(rule.destination)
            elif('drg' in network_entity_id):
                if(rule.destination not in onprem_destinations):
                    onprem_destinations.append(rule.destination)

            new_row=(region,comp_name,vcn_name,dn,rule.destination,str(network_entity_name),str(rule.destination_type),desc)
            rows.append(new_row)
            if(tf_import_cmd=="false"):
                print(dn + "," + str(rule.destination) + "," + str(network_entity_name)+","+ str(rule.destination_type),desc)


parser = argparse.ArgumentParser(description="Export Route Table on OCI to CD3")
parser.add_argument("cd3file", help="path of CD3 excel file to export rules to")
parser.add_argument("--networkCompartment", help="comma seperated Compartments for which to export Networking Objects", required=False)
parser.add_argument("--configFileName", help="Config file name" , required=False)
parser.add_argument("--tf_import_cmd", help="write tf import commands" , required=False)
parser.add_argument("--outdir", help="outdir for TF import commands script" , required=False)

if len(sys.argv) < 2:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()
cd3file=args.cd3file

if('.xls' not in cd3file):
    print("\nAcceptable cd3 format: .xlsx")
    exit()

tf_import_cmd = args.tf_import_cmd
outdir = args.outdir


if args.configFileName is not None:
    configFileName = args.configFileName
    config = oci.config.from_file(file_location=configFileName)
else:
    config = oci.config.from_file()

input_compartment_list = args.networkCompartment
if(input_compartment_list is not None):
    input_compartment_names = input_compartment_list.split(",")
else:
    input_compartment_names = None

if tf_import_cmd is not None:
    tf_import_cmd="true"
    if(outdir is None):
        print("out directory is a mandatory arguement to write tf import commands ")
        exit(1)
else:
    tf_import_cmd = "false"

idc = IdentityClient(config)
ntk_compartment_ids["root"] = config['tenancy']
get_network_compartment_ids(config['tenancy'],"root")
rows=[]
all_regions = []

if(tf_import_cmd=="true"):
    importCommands={}
    regionsubscriptions = idc.list_region_subscriptions(tenancy_id=config['tenancy'])
    for rs in regionsubscriptions.data:
        for k, v in commonTools().region_dict.items():
            if (rs.region_name == v):
                all_regions.append(k)
    for reg in all_regions:
        importCommands[reg] = open(outdir + "/" + reg + "/tf_import_commands_network_nonGF.sh", "a")
        importCommands[reg].write("\n\n######### Writing import for Route Tables #########\n\n")
else:
    vcnInfo = parseVCNInfo(cd3file)
    all_regions=vcnInfo.all_regions

print("\nFetching Route Rules...")

for reg in all_regions:
    config.__setitem__("region", commonTools().region_dict[reg])
    vcn = VirtualNetworkClient(config)
    region = reg.capitalize()
    comp_ocid_done = []
    for ntk_compartment_name in ntk_compartment_ids:
        if ntk_compartment_ids[ntk_compartment_name] not in comp_ocid_done:
            if (input_compartment_names is not None and ntk_compartment_name not in input_compartment_names):
                continue
            comp_ocid_done.append(ntk_compartment_ids[ntk_compartment_name])
            vcns = oci.pagination.list_call_get_all_results(vcn.list_vcns,compartment_id=ntk_compartment_ids[ntk_compartment_name],lifecycle_state="AVAILABLE")
            for v in vcns.data:
                vcn_id = v.id
                vcn_name=v.display_name
                comp_ocid_done_again = []
                for ntk_compartment_name_again in ntk_compartment_ids:
                    if ntk_compartment_ids[ntk_compartment_name_again] not in comp_ocid_done_again:
                        if (input_compartment_names is not None and ntk_compartment_name_again not in input_compartment_names):
                            continue
                        comp_ocid_done_again.append(ntk_compartment_ids[ntk_compartment_name_again])
                        routetables = oci.pagination.list_call_get_all_results(vcn.list_route_tables, compartment_id=ntk_compartment_ids[ntk_compartment_name_again], vcn_id=vcn_id, lifecycle_state='AVAILABLE')
                        print_routetables(routetables,region,vcn_name,ntk_compartment_name_again)

commonTools.write_to_cd3(rows,cd3file,"RouteRulesinOCI")

vcninfo_rows=(onprem_destinations,ngw_destinations,igw_destinations)
commonTools.write_to_cd3(vcninfo_rows,cd3file,"VCN Info")

if (tf_import_cmd == "true"):
    for reg in all_regions:
        importCommands[reg].close()


