#!/bin/python


import argparse
import sys
import oci
from oci.core.virtual_network_client import VirtualNetworkClient
from oci.identity import IdentityClient
import pandas as pd
from openpyxl import load_workbook

def convertNullToNothing(input):
    EMPTY_STRING = ""
    if input is None:
        return EMPTY_STRING
    else:
        return str(input)

def get_network_compartment_id(config, compartment_name):
    identity = IdentityClient(config)
    comp_list = oci.pagination.list_call_get_all_results(identity.list_compartments,config["tenancy"],compartment_id_in_subtree=True)
    compartment_list = comp_list.data
    for compartment in compartment_list:
        if compartment.name == compartment_name:
            return compartment.id

def get_vcn_id(config,compartment_id,vname):
    vcncient = VirtualNetworkClient(config)
    vcnlist = vcncient.list_vcns(compartment_id=compartment_id,lifecycle_state="AVAILABLE")
    vcn_name = vname.lower()
    for v in vcnlist.data:
        name = v.display_name
        if name.lower() == vcn_name:
            return vcn.id

def get_vcns(config,compartment_id):
    vcncient = VirtualNetworkClient(config)
    vcnlist = vcncient.list_vcns(compartment_id=compartment_id,lifecycle_state="AVAILABLE")
    return vcnlist

subnets = []
destinations = []
entity_ids = []
dest_types = []
def print_routetables(routetables):

    print ("SubnetName, Destination CIDR, Route Destination Object, Destination Type")
    oname.write("SubnetName, Destination CIDR, Route Destination Object, Destination Type\n")
    for routetable in routetables.data:
        rules = routetable.route_rules
        display_name = routetable.display_name
        dn = ""
        if "10" in display_name:
            dn = display_name.split("10")
            dn = dn[0][:-1]
        else:
            dn = routetable.display_name
        for rule in rules:
            subnets.append(dn)
            destinations.append(str(rule.destination))
            entity_ids.append(str(rule.network_entity_id))
            dest_types.append(str(rule.destination_type))
            print(dn + "," + str(rule.destination) + "," + str(rule.network_entity_id)+","+ str(rule.destination_type))
            oname.write(dn + "," + str(rule.destination) + "," +str(rule.network_entity_id)+","+ str(rule.destination_type)+"\n")
    # Create a Pandas dataframe from some data.
    df1 = pd.DataFrame({'SubnetName': subnets,'Destination CIDR': destinations,'Route Destination Object': entity_ids,'Destination Type': dest_types})

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    #writer = pd.ExcelWriter('pandas_simple.xlsx', engine='xlsxwriter',mode='a')
    #writer = pd.ExcelWriter('pandas_simple.xlsx', mode='a')
    # Convert the dataframe to an XlsxWriter Excel object.

    book = load_workbook('CD3-template.xlsx')
    writer = pd.ExcelWriter('CD3-template.xlsx', engine='openpyxl')
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)

    df1.to_excel(writer, sheet_name='Sheet4', index=False)

    writer.save()
     # Close the Pandas Excel writer and output the Excel file.


parser = argparse.ArgumentParser(description="Export Route Table on OCI to CSV")
parser.add_argument("networkCompartment", help="Compartment where VCN resides")
parser.add_argument("outdir", help="directory path for output csv file ")
parser.add_argument("--vcnName", help="VCN from which to export the sec list", required=False)
parser.add_argument("--configFileName", help="Config file name" , required=False)



if len(sys.argv) < 3:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()
outdir = args.outdir
vcn_name = args.vcnName
ntk_comp_name = args.networkCompartment
if args.configFileName is not None:
    configFileName = args.configFileName
    config = oci.config.from_file(file_location=configFileName)
else:
    config = oci.config.from_file()

ntk_compartment_id = get_network_compartment_id(config, ntk_comp_name)
vcn = VirtualNetworkClient(config)

if(vcn_name is not None):
    outfile = outdir+"/"+ntk_comp_name+"_"+vcn_name+"_RouteRules.csv"
else:
    outfile = outdir+"/"+ntk_comp_name+"_RouteRules.csv"
print("Writing sec rules to "+outfile)
oname = open(outfile,"w")

if vcn_name is not None:
    vcn_ocid = get_vcn_id(config,ntk_compartment_id,vcn_name)
    routetables = vcn.list_route_tables(compartment_id=ntk_compartment_id, vcn_id=vcn_ocid, lifecycle_state='AVAILABLE')
    print_routetables(routetables)
else:
    vcns = get_vcns(config,ntk_compartment_id)
    for v in vcns.data:
        vcn_id = v.id
        routetables = vcn.list_route_tables(compartment_id=ntk_compartment_id, vcn_id=vcn_id, lifecycle_state='AVAILABLE')
        print_routetables(routetables)
oname.close()