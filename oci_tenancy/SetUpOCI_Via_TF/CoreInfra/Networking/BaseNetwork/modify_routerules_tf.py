#!/usr/bin/python3

import sys
import argparse
import pandas as pd
import os
sys.path.append(os.getcwd()+"/../../..")
from commonTools import *

######
# Takes in input csv or CD3 excel which contains routerules to be updated for the subnet and updates the routes tf file created using BaseNetwork TF generation.
# ######



parser = argparse.ArgumentParser(description="Updates routelist for subnet. It accepts input file which contains new rules to be added to the existing rule list of the subnet.")
parser.add_argument("inputfile", help="Required; Full Path to input route file (either csv or CD3 excel file) containing rules to be updated; See example folder for sample format: add_routes-example.txt")
parser.add_argument("outdir",help="directory path for output tf files ")


if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)


args = parser.parse_args()
inputfile = args.inputfile
outdir=args.outdir

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
    vcnInfo=parseVCNInfo(inputfile)

    df = pd.read_excel(inputfile, sheet_name='RouteRulesinOCI', skiprows=1)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    for reg in vcnInfo.all_regions:
        if(os.path.exists(outdir + "/" +reg)):
            defaultname[reg] = open(outdir + "/" + reg + "/VCNs_Default_RouteTable.tf", "w")
        default_ruleStr[reg] = ''
        default_rtables_done[reg]=[]
        subnets_done[reg] = []
        # Backup existing seclist files in ash and phx dir
        print("Backing up all existing RT TF files for region " + reg+ " to")
        commonTools.backup_file(outdir + "/" + reg, "_routetable.tf")

    for i in df.index:
        region = df.iat[i, 0]
        region = region.strip().lower()
        if region not in vcnInfo.all_regions:
            print("Invalid Region; It should be one of the values mentioned in VCN Info tab")
            exit(1)
        comp_name = df.iat[i, 1]
        comp_name = comp_name.strip()
        # Added to check if compartment name is compatible with TF variable name syntax
        comp_name = commonTools.check_tf_variable(comp_name)

        vcn_name = df.iat[i, 2]
        vcn_name = vcn_name.strip()
        display_name = df.iat[i, 3]

        # Process only those VCNs which are present in cd3(and have been created via TF)
        if (vcn_name not in vcns.vcn_names):
            print("skipping route table: " + display_name + " as its VCN is not part of VCNs tab in cd3")
            continue
        vcn_tf_name = commonTools.check_tf_variable(vcn_name)

        if (str(display_name).lower() == "nan"):
            continue
        dest_cidr = df.iat[i, 4]
        if(str(dest_cidr).lower()=='nan'):
            dest_cidr=""
        else:
            dest_cidr = str(dest_cidr).strip()

        dest_objs = df.iat[i, 5]
        if(str(dest_objs).lower()=="nan"):
            dest_objs=""

        dest_objs = str(dest_objs).strip().split(":")
        if(len(dest_objs)==2):
            obj_tf_name = vcn_name+"_"+dest_objs[1].strip()
            obj_tf_name=commonTools.check_tf_variable(obj_tf_name)

        if ('ngw' in dest_objs[0].lower().strip()):
            dest_obj = "${oci_core_nat_gateway." + obj_tf_name + ".id}"
        elif ('sgw' in dest_objs[0].lower().strip()):
            dest_obj = "${oci_core_service_gateway." + obj_tf_name+ ".id}"
        elif ('igw' in dest_objs[0].lower().strip()):
            dest_obj = "${oci_core_internet_gateway." + obj_tf_name + ".id}"
        elif ('lpg' in dest_objs[0].lower().strip()):
            dest_obj = "${oci_core_local_peering_gateway." + obj_tf_name + ".id}"
        elif ('drg' in dest_objs[0].lower().strip()):
            #dest_obj = "${oci_core_drg." + vcn_tf_name+"_"+obj_tf_name + ".id}"
            dest_obj = "${oci_core_drg." + commonTools.check_tf_variable(dest_objs[1].strip()) + ".id}"
#        elif ('privateip' in dest_objs[0].lower()):
        #direct OCID is provided
        else:
            dest_obj = dest_objs[0].strip()

        dest_type = df.iat[i, 6]
        if(str(dest_type).lower()=="nan"):
            dest_type=""
        else:
            dest_type = str(dest_type).strip()

        rule_desc = df.iat[i, 7]
        if (str(rule_desc).lower() == "nan"):
            rule_desc = ""
        else:
            rule_desc = str(rule_desc).strip()

        """if('Route Table associated with DRG' in subnet_name):
            drg_name = subnet_name.split('DRG ')[1].strip()
            rt_var = vcn_name+"_"+drg_name + "_rt"
        elif('Default Route Table for' in subnet_name):
            continue;
        elif('Route Table associated with LPG' in subnet_name):
            lpg_name= subnet_name.split('LPG')
            rt_var = vcn_name+"_"+lpg_name[1].strip() + "_rt"
        else:
            rt_var=vcn_name+"_"+subnet_name
        """
        rt_var = vcn_name + "_" + display_name
        rt_tf_name = commonTools.check_tf_variable(rt_var)

        if("Default Route Table for " in display_name):
            if(rt_tf_name not in default_rtables_done[region]):
                if (len(default_rtables_done[region]) != 0):
                    default_ruleStr[region] = default_ruleStr[region] + """
                }"""
                default_ruleStr[region] = default_ruleStr[region] + """
                resource "oci_core_default_route_table" \"""" + rt_tf_name + """" {
                    manage_default_resource_id  = "${oci_core_vcn.""" + vcn_tf_name + """.default_route_table_id}"
                    ##Add More rules for """ + vcn_tf_name + """##
                """
                default_rtables_done[region].append(rt_tf_name)
            if(dest_objs[0]!=""):
                default_ruleStr[region]=default_ruleStr[region]+"""
                    route_rules {
                        destination =\"""" + dest_cidr + """\"
                        description =\"""" + rule_desc + """\"
                        network_entity_id = \"""" + dest_obj + """\"
                        destination_type = \"""" + dest_type + """\"
                    }
                    """
            continue

        #Process other route tables
        outfile = outdir + "/" + region + "/"+rt_tf_name+"_routetable.tf"
        if(rt_tf_name not in subnets_done[region] or len(subnets_done[region])==0):
            if (tfStr!= ''):
                tfStr = tfStr + """
        }"""
                oname.write(tfStr)
                oname.close()
                tfStr = ''
            oname=open(outfile,'w')

            tfStr= tfStr + """
    resource "oci_core_route_table" \"""" + rt_tf_name + """"{
        compartment_id = "${var.""" + comp_name + """}"
        vcn_id = "${oci_core_vcn.""" + vcn_tf_name + """.id}"
        display_name = \"""" +display_name +  """"
        
        ##Add More rules for subnet """ + rt_tf_name+ """##
        """
            if(dest_objs[0]!=""):
                tfStr=tfStr+"""
        route_rules {
                destination =\"""" + dest_cidr + """\"
                network_entity_id = \"""" + dest_obj + """\"
                destination_type = \"""" + dest_type + """\"
            }
            """
            subnets_done[region].append(rt_tf_name)
        else:
            if (dest_objs[0] != ""):
                tfStr=tfStr+"""
            route_rules {
                destination =\"""" + dest_cidr + """\"
                network_entity_id = \"""" + dest_obj + """\"
                destination_type = \"""" + dest_type + """\"
            }
            """

    tfStr = tfStr + """
        }"""
    if (oname != None):
        oname.write(tfStr)
        oname.close()
    for reg in vcnInfo.all_regions:
        if (default_ruleStr[reg] != ''):
            default_ruleStr[reg] = default_ruleStr[reg] + """
        }"""
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