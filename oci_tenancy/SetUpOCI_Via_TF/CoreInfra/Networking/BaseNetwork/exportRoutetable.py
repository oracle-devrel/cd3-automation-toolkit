#!/usr/bin/python3


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

compartment_ids={}
def get_network_compartment_id(config):#, compartment_name):
    identity = IdentityClient(config)
    comp_list = oci.pagination.list_call_get_all_results(identity.list_compartments,config["tenancy"],compartment_id_in_subtree=True)
    compartment_list = comp_list.data

    #if(compartment_name=='root'):
    for compartment in compartment_list:
        if(compartment.lifecycle_state == 'ACTIVE'):
            compartment_ids[compartment.name]=compartment.id
    return compartment_ids

def get_vcn_id(config,compartment_id,vname):
    vcncient = VirtualNetworkClient(config)
    vcnlist = vcncient.list_vcns(compartment_id=compartment_id,lifecycle_state="AVAILABLE")
    vcn_name = vname.lower()
    for v in vcnlist.data:
        name = v.display_name
        if name.lower() == vcn_name:
            return v.id

def get_vcns(config,compartment_id):
    vcncient = VirtualNetworkClient(config)
    vcnlist = vcncient.list_vcns(compartment_id=compartment_id,lifecycle_state="AVAILABLE")
    return vcnlist

def get_network_entity_name(config,network_identity_id):
    vcn1 = VirtualNetworkClient(config)
    if('internetgateway' in network_identity_id):
        igw=vcn1.get_internet_gateway(network_identity_id)
        network_identity_name = "igw:"+igw.data.display_name
        return  network_identity_name

    if ('servicegateway' in network_identity_id):
        sgw = vcn1.get_service_gateway(network_identity_id)
        network_identity_name = "sgw:"+sgw.data.display_name
        return network_identity_name


    if ('natgateway' in network_identity_id):
        ngw = vcn1.get_nat_gateway(network_identity_id)
        network_identity_name = "ngw:"+ngw.data.display_name
        return network_identity_name

    if ('localpeeringgateway' in network_identity_id):
        lpg = vcn1.get_local_peering_gateway(network_identity_id)
        network_identity_name = "lpg:"+lpg.data.display_name
        return network_identity_name

    if ('drg' in network_identity_id):
        drg = vcn1.get_drg(network_identity_id)
        network_identity_name = "drg:"+drg.data.display_name
        return network_identity_name


def print_routetables(routetables,region,vcn_name,comp_name):

    #oname.write("SubnetName, Destination CIDR, Route Destination Object, Destination Type\n")
    global i
    global df
    for routetable in routetables.data:
        print(routetable.display_name)
        rules = routetable.route_rules
        display_name = routetable.display_name

        # display name contains AD1, AD2 or AD3 and CIDR
        if ('-ad1-10.' in display_name or '-ad2-10.' in display_name or '-ad3-10.' in display_name or '-ad1-172.' in display_name
                or '-ad2-172.' in display_name or '-ad3-172.' in display_name or '-ad1-192.' in display_name or '-ad2-192.' in display_name
                or '-ad3-192.' in display_name):
            dn = display_name.rsplit("-", 2)[0]

        # display name contains CIDR
        elif ('-10.' in display_name or '-172.' in display_name or '192.' in display_name):
            dn = display_name.rsplit("-", 1)[0]
        else:
            dn=display_name

        #dn = routetable.display_name
        if(not rules):
            i=i+1
            print(i)
            new_row = pd.DataFrame({'Region':region,'Compartment Name':comp_name, 'VCN Name':vcn_name, 'SubnetName': dn, 'Destination CIDR': '',
                                    'Route Destination Object': '','Destination Type': ''}, index=[i])
            df = df.append(new_row, ignore_index=True)
        for rule in rules:
            i=i+1
            print(i)
            network_entity_id=rule.network_entity_id
            network_entity_name=get_network_entity_name(config,network_entity_id)


            print(dn + "," + str(rule.destination) + "," + str(network_entity_name)+","+ str(rule.destination_type))
            #oname.write(dn + "," + str(rule.destination) + "," +str(rule.network_entity_id)+","+ str(rule.destination_type)+"\n")
            #new_row = pd.DataFrame({'Region':region,'Compartment Name':comp_name, 'VCN Name':vcn_name,'SubnetName': dn, 'Destination CIDR': str(rule.destination), 'Route Destination Object': str(rule.network_entity_id), 'Destination Type': str(rule.destination_type)}, index=[i])
            new_row = pd.DataFrame(
                {'Region': region, 'Compartment Name': comp_name, 'VCN Name': vcn_name, 'SubnetName': dn,
                 'Destination CIDR': str(rule.destination), 'Route Destination Object': str(network_entity_name),
                 'Destination Type': str(rule.destination_type)}, index=[i])
            df = df.append(new_row, ignore_index=True)

parser = argparse.ArgumentParser(description="Export Route Table on OCI to CD3")
parser.add_argument("cd3file", help="path of CD3 excel file to export rules to")
parser.add_argument("--vcnName", help="VCN from which to export the sec list; Leave blank if need to export from all VCNs", required=False)
parser.add_argument("--networkCompartment", help="Compartment where VCN resides", required=False)
parser.add_argument("--configFileName", help="Config file name" , required=False)



if len(sys.argv) < 2:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()
cd3file=args.cd3file

if('.xls' not in cd3file):
    print("\nAcceptable cd3 format: .xlsx")
    exit()

vcn_name = args.vcnName

if args.configFileName is not None:
    configFileName = args.configFileName
    config = oci.config.from_file(file_location=configFileName)
else:
    config = oci.config.from_file()


ntk_compartment_ids = get_network_compartment_id(config)
df_info = pd.read_excel(cd3file, sheet_name='VCN Info', skiprows=1)
properties = df_info['Property']
values = df_info['Value']
all_regions = str(values[7]).strip()
all_regions = all_regions.split(",")
all_regions = [x.strip().lower() for x in all_regions]

region_dict = {'ashburn':'us-ashburn-1','phoenix':'us-phoenix-1','london':'uk-london-1','frankfurt':'eu-frankfurt-1','toronto':'ca-toronto-1','tokyo':'ap-tokyo-1','seoul':'ap-seoul-1','mumbai':'ap-mumbai-1'}

i=0
df=pd.DataFrame()

if vcn_name is not None:
    ntk_comp_name = args.networkCompartment
    if(ntk_comp_name=='' or ntk_comp_name is None):
        print("\nEnter a valid name for the compartment where VCN resides...")
        exit(1)

    found_region = ''
    for reg in all_regions:
        print("\nSearching for VCN in region..."+reg)
        config.__setitem__("region", region_dict[reg])
        vcn_ocid = get_vcn_id(config,ntk_compartment_ids[ntk_comp_name],vcn_name)

        if(vcn_ocid=='' or vcn_ocid is None):
            print('\nCould not find vcn in compartment '+ntk_comp_name+' in region...'+reg)
        else:
            print("\nFound in Region..."+reg)
            found_region=reg
            break

    config.__setitem__("region", region_dict[found_region])
    vcn = VirtualNetworkClient(config)
    region=found_region.capitalize()

    routetables = vcn.list_route_tables(compartment_id=ntk_compartment_ids[ntk_comp_name], vcn_id=vcn_ocid, lifecycle_state='AVAILABLE')
    print_routetables(routetables,region, vcn_name,ntk_comp_name)
else:
    print("\nFetching Route Rules for all VCNs in tenancy...")
    for reg in all_regions:
        for ntk_compartment_name in ntk_compartment_ids:
            config.__setitem__("region", region_dict[reg])
            vcn = VirtualNetworkClient(config)
            region = reg.capitalize()
            vcns = get_vcns(config,ntk_compartment_ids[ntk_compartment_name])

            for v in vcns.data:
                vcn_id = v.id
                vcn_name=v.display_name
                routetables = vcn.list_route_tables(compartment_id=ntk_compartment_ids[ntk_compartment_name], vcn_id=vcn_id, lifecycle_state='AVAILABLE')
                print_routetables(routetables,region,vcn_name,ntk_compartment_name)


book = load_workbook(cd3file)
if('RouteRulesinOCI' in book.sheetnames):
    book.remove(book['RouteRulesinOCI'])
writer = pd.ExcelWriter(cd3file, engine='openpyxl')
writer.book = book
writer.save()

book = load_workbook(cd3file)
writer = pd.ExcelWriter(cd3file, engine='openpyxl')
writer.book = book
df.to_excel(writer, sheet_name='RouteRulesinOCI', index=False)
writer.save()
