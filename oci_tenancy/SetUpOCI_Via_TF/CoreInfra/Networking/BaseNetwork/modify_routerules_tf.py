#!/usr/bin/python3

import sys
import argparse
import pandas as pd
import os
sys.path.append(os.getcwd()+"/../../..")
from commonTools import *
from jinja2 import Environment, FileSystemLoader

######
# Takes in input csv or CD3 excel which contains routerules to be updated for the subnet and updates the routes tf file created using BaseNetwork TF generation.
# ######

#Load the template file
file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
routerule = env.get_template('route-rule-template')
defaultrt = env.get_template('default-route-table-template')
routetable = env.get_template('route-table-template')

parser = argparse.ArgumentParser(description="Updates routelist for subnet. It accepts input file which contains new rules to be added to the existing rule list of the subnet.")
parser.add_argument("inputfile", help="Required; Full Path to input route file (either csv or CD3 excel file) containing rules to be updated; See example folder for sample format: add_routes-example.txt")
parser.add_argument("outdir",help="directory path for output tf files ")
parser.add_argument("--configFileName", help="Config file name", required=False)

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()
inputfile = args.inputfile
outdir=args.outdir
if args.configFileName is not None:
    configFileName = args.configFileName
else:
    configFileName=""

ct = commonTools()
ct.get_subscribedregions(configFileName)

data=""
tfStr=''
subnets_done={}
routefile={}
oname = None
default_ruleStr={}
defaultname={}
default_rtables_done={}

#If input is CD3 excel file
if('.xls' in inputfile):
    vcns=parseVCNs(inputfile)

    df = pd.read_excel(inputfile, sheet_name='RouteRulesinOCI', skiprows=1)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    for reg in ct.all_regions:
        if(os.path.exists(outdir + "/" +reg)):
            defaultname[reg] = open(outdir + "/" + reg + "/VCNs_Default_RouteTable.tf", "w")
        default_ruleStr[reg] = ''
        default_rtables_done[reg]=[]
        subnets_done[reg] = []
        # Backup existing seclist files in ash and phx dir
        print("Backing up all existing RT TF files for region " + reg+ " to")
        commonTools.backup_file(outdir + "/" + reg, "_routetable.tf")

    # temporary dictionary1 and dictionary2
    tempStr = {}
    tempdict = {}
    vcn_tf_name = ''
    compartment_tf_name = ''
    obj_tf_name = ''
    display_name=''
    rt_tf_name=''
    dest_objs=[]
    dest_obj=''

    for i in df.index:
        region = str(df.loc[i, 'Region'])
        region = region.strip().lower()
        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        # Check if values are entered for mandatory fields
        if (str(df.loc[i, 'Region']).lower() == 'nan' or str(df.loc[i, 'VCN Name']).lower() == 'nan' or str(df.loc[i, 'Compartment Name']).lower() == 'nan'):
            print("Column Region, VCN Name and Compartment Name cannot be left empty in Instances sheet of CD3..Exiting!")
            exit(1)

        for columnname in dfcolumns:

            # Column value
            columnvalue = str(df[columnname][i]).strip()

            if columnvalue == '1.0' or columnvalue == '0.0':
                if columnvalue == '1.0':
                    columnvalue = "true"
                else:
                    columnvalue = "false"

            if (columnvalue.lower() == 'nan'):
                columnvalue = ""

            if columnname in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if "::" in columnvalue:
                if columnname != 'Compartment Name' and ".Flex" in columnvalue:
                    columnname = commonTools.check_column_headers(columnname)
                    multivalues = columnvalue.split("::")
                    multivalues = [str(part).strip() for part in multivalues if part]
                    tempdict = {columnname: multivalues}

            if columnname == 'Compartment Name':
                compartment_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'compartment_tf_name': compartment_tf_name}

            if columnname == 'VCN Name':
                vcn_name = columnvalue
                display_name = str(df.loc[i,'Route Table Name'])
                # Process only those VCNs which are present in cd3(and have been created via TF)
                if (vcn_name not in vcns.vcn_names):
                    print("skipping route table: " + display_name + " as its VCN is not part of VCNs tab in cd3")
                    continue
                vcn_tf_name = commonTools.check_tf_variable(vcn_name)
                tempdict = {'vcn_tf_name': vcn_tf_name,'rt_display' : display_name}

            #Check this code once
            #if columnname == 'Route Table Name':
                #if columnvalue == '':
                    #continue

            if columnname == 'Route Destination Object':
                dest_objs = columnvalue.strip()
                if dest_objs != '':
                    dest_objs = str(dest_objs).strip().split(":")
                    if (len(dest_objs) == 2):
                        obj_tf_name = vcn_tf_name + "_" + dest_objs[1].strip()
                        obj_tf_name = commonTools.check_tf_variable(obj_tf_name)
                    if ('ngw' in dest_objs[0].lower().strip()):
                        dest_obj = "oci_core_nat_gateway." + obj_tf_name + ".id"
                    elif ('sgw' in dest_objs[0].lower().strip()):
                        dest_obj = "oci_core_service_gateway." + obj_tf_name + ".id"
                    elif ('igw' in dest_objs[0].lower().strip()):
                        dest_obj = "oci_core_internet_gateway." + obj_tf_name + ".id"
                    elif ('lpg' in dest_objs[0].lower().strip()):
                        dest_obj = "oci_core_local_peering_gateway." + obj_tf_name + ".id"
                    elif ('drg' in dest_objs[0].lower().strip()):
                        # dest_obj = "${oci_core_drg." + vcn_tf_name+"_"+obj_tf_name + ".id}"
                        dest_obj = "oci_core_drg." + commonTools.check_tf_variable(dest_objs[1].strip()) + ".id"
                    #        elif ('privateip' in dest_objs[0].lower()):
                    # direct OCID is provided
                    else:
                        dest_obj = "\""+dest_objs[0].strip()+"\""

                    tempdict = {'network_entity_id' : dest_obj}

            destination = str(df.loc[i,'Destination CIDR']).strip()
            description = str(df.loc[i,'Rule Description']).strip()
            tempdict = {'destination' : destination,'description' : description}
            rt_var = vcn_tf_name + "_" + display_name
            rt_tf_name = commonTools.check_tf_variable(rt_var)

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        if("Default Route Table for " in display_name):
            if(rt_tf_name not in default_rtables_done[region]):
                if (len(default_rtables_done[region]) == 0):
                    default_ruleStr[region] = default_ruleStr[region] + defaultrt.render(tempStr)
                    default_rtables_done[region].append(rt_tf_name)
            if(dest_objs[0]!=""):
                default_ruleStr[region]=default_ruleStr[region]+ routerule.render(tempStr)
            continue

        #Process other route tables
        outfile = outdir + "/" + region + "/"+rt_tf_name+"_routetable.tf"
        if(rt_tf_name not in subnets_done[region] or len(subnets_done[region])==0):
            if (tfStr!= ''):
                oname.write(tfStr)
                oname.close()
                tfStr = ''
            oname=open(outfile,'w')
            tfStr= tfStr + routetable.render(tempStr)
            if(dest_objs[0]!=""):
                tfStr=tfStr+ routerule.render(tempStr)
            subnets_done[region].append(rt_tf_name)
        else:
            if (dest_objs[0] != ""):
                tfStr=tfStr+ routerule.render(tempStr)

    if (oname != None):
        oname.write(tfStr)
        oname.close()
    for reg in ct.all_regions:
        if (default_ruleStr[reg] != ''):
            defaultname[reg].write(default_ruleStr[reg])
            defaultname[reg].close()

# If input is a csv file
"""
elif ('.csv' in inputfile):
    fname = open(inputfile, "r")
    # Read the input csv file
    endNames = {'<END>', '<end>', '<End>'}
    all_regions=os.listdir(outdir)
    for reg in all_regions:
        tfStr[reg] = ''
        subnets_done[reg] = []


    for route in fname:
        if (route.strip() in endNames):
            break
        if not route.startswith('#') and route != '\n':
            subnet_name = route.split(",")[0]
            subnet_name=subnet_name.strip()
            dest_cidr = route.split(",")[1]
            dest_cidr=dest_cidr.strip()
            dest_objs = route.split(",")[2]
            dest_objs = dest_objs.strip().split(":")

            if ('ngw' in dest_objs[0].lower()):
                dest_obj = "${oci_core_nat_gateway." + dest_objs[1] + ".id}"
            elif ('sgw' in dest_objs[0].lower()):
                dest_obj = "${oci_core_service_gateway." + dest_objs[1] + ".id}"
            elif ('igw' in dest_objs[0].lower()):
                dest_obj = "${oci_core_internet_gateway." + dest_objs[1] + ".id}"
            elif ('lpg' in dest_objs[0].lower()):
                dest_obj = "${oci_core_local_peering_gateway." + dest_objs[1] + ".id}"
            elif ('drg' in dest_objs[0].lower()):
                dest_obj = "${oci_core_drg." + dest_objs[1] + ".id}"
            else:
                dest_obj = dest_objs[0]
            dest_type = route.split(",")[3]
            dest_type = dest_type.strip()
            region=route.split(",")[4]
            region=region.strip().lower()
            vcn_name = route.split(",")[5]
            vcn_name= vcn_name.strip().lower()

            if region not in all_regions:
                print("Invalid Region")
                continue

            if ('Route Table associated with DRG' in subnet_name):
                drg_name = subnet_name.split('DRG ')[1].strip()
                rt_var = drg_name + "_rt"
            elif ('Default Route Table for' in subnet_name):
                continue;
            elif ('Route Table associated with LPG' in subnet_name):
                lpg_name = subnet_name.split('LPG')
                rt_var = lpg_name[1].strip() + "_rt"
            else:
                rt_var = vcn_name+"_"+subnet_name

            searchString = "##Add More rules for subnet "+rt_var+"##"
            strRule = ""
            strRule = strRule+"""
"""       ##missing content##      """
"""             strRule1 = strRule + "##Add More rules for subnet " +rt_var+"##"

            outfile = outdir + "/" + region + "/" + rt_var + "_routetable.tf"
            commonTools.backup_file(outdir + "/" + region, rt_var + "_routetable.tf")

            # Update file contents
            with open(routefile[region]) as f:
                data = f.read()
            f.close()
            updated_data = re.sub(searchString, strRule1, data)
            with open(routefile[region], 'w') as f:
                f.write(updated_data)
            f.close()
    print("Route Rules added to the file successfully. Please run terraform plan from your outdir to see the changes")

    fname.close()

else:
    print("Invalid input file format; Acceptable formats: .xls, .xlsx, .csv")
"""