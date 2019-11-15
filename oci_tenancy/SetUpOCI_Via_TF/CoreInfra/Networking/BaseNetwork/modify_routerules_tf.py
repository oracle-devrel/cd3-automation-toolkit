#!/usr/bin/python3

import sys
import argparse
import shutil
import re
import pandas as pd
import glob
import datetime
import os
######
# Takes in input csv or CD3 excel which contains routerules to be updated for the subnet and updates the routes tf file created using BaseNetwork TF generation.
# ######



parser = argparse.ArgumentParser(description="Updates routelist for subnet. It accepts input file which contains new rules to be added to the existing rule list of the subnet.")
parser.add_argument("inputfile", help="Required; Full Path to input route file (either csv or CD3 excel file) containing rules to be updated; See example folder for sample format: add_routes-example.txt")
parser.add_argument("outdir",help="directory path for output tf files ")
parser.add_argument("--overwrite",help="This will overwrite all sec rules in OCI with whatever is specified in cd3 excel file sheet- SecRulesinOCI (yes or no) ",required=False)


if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)


args = parser.parse_args()
inputfile = args.inputfile
outdir=args.outdir


if args.overwrite is not None:
    overwrite = str(args.overwrite)
else:
    overwrite = "no"

data=""
tfStr=''
subnets_done={}
routefile={}
x = datetime.datetime.now()
date = x.strftime("%f").strip()
cd3_tf_vcns=[]
oname = None

def backup_file(src_dir, pattern,overwrite):
    dest_dir = src_dir + "/backup_RTs_" + date
    for f in os.listdir(src_dir):
        if f.endswith(pattern):
            if not os.path.exists(dest_dir):
                print("\nCreating backup dir "+dest_dir +"\n")
                os.makedirs(dest_dir)

            src = os.path.join(src_dir, f)
            print("backing up ....." +  src)
            dest=os.path.join(dest_dir,f)
            if(overwrite=='yes'):
                shutil.move(src, dest_dir)
            elif(overwrite=='no'):
                shutil.copyfile(src, dest)


#If input is CD3 excel file
if('.xls' in inputfile):
    df_info = pd.read_excel(inputfile, sheet_name='VCN Info', skiprows=1)
    properties = df_info['Property']
    values = df_info['Value']

    all_regions = str(values[7]).strip()
    all_regions = all_regions.split(",")
    all_regions = [x.strip().lower() for x in all_regions]
    """for file in glob.glob(outdir+'/'+reg + '/*routes.tf'):
        routefile[reg] = file
        # Backup the existing Routes tf file
        print("Backing Up "+routefile[reg])
        shutil.copy(routefile[reg], routefile[reg] + "_backup" + date)
    """

    endNames = {'<END>', '<end>', '<End>'}
    NaNstr = 'NaN'

    # Get VCNs in cd3 (created via TF)
    df_vcns = pd.read_excel(args.inputfile, sheet_name='VCNs', skiprows=1)
    for i in df_vcns.index:
        region = df_vcns['Region'][i]
        if (region in endNames):
            break
        cd3_tf_vcns.append(df_vcns['vcn_name'][i])

    if (overwrite == 'yes'):
        print("\nReading RouteRulesinOCI sheet of cd3")
        df = pd.read_excel(inputfile, sheet_name='RouteRulesinOCI')
        df.dropna(how='all')

        for reg in all_regions:
            subnets_done[reg] = []
            # Backup existing seclist files in ash and phx dir
            print("backing up tf files for region " + reg)
            backup_file(outdir + "/" + reg, "_routetable.tf",overwrite)

        for i in df.index:
            region = df.iat[i, 0]
            region = region.strip().lower()
            if region not in all_regions:
                print("Invalid Region; It should be one of the values mentioned in VCN Info tab")
                exit(1)
            comp_name = df.iat[i, 1]
            comp_name = comp_name.strip()
            vcn_name = df.iat[i, 2]
            vcn_name = vcn_name.strip()
            subnet_name = df.iat[i, 3]

            # Process only those VCNs which are present in cd3(and have been created via TF)
            if (vcn_name not in cd3_tf_vcns):
                print("skipping route table: " + subnet_name + " as its VCN is not part of VCNs tab in cd3")
                continue

            if (str(subnet_name).lower() == NaNstr.lower()):
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

            dest_type = df.iat[i, 6]
            if(str(dest_type).lower()=="nan"):
                dest_type=""
            else:
                dest_type = str(dest_type).strip()

            if('Route Table associated with DRG' in subnet_name):
                drg_name = subnet_name.split('DRG ')[1].strip()
                rt_var = drg_name + "_rt"
            elif('Default Route Table for' in subnet_name):
                continue;
            elif('Route Table associated with LPG' in subnet_name):
                lpg_name= subnet_name.split('LPG')
                rt_var = lpg_name[1].strip() + "_rt"
            else:
                rt_var=vcn_name+"_"+subnet_name
            print(rt_var)
            outfile = outdir + "/" + region + "/"+rt_var+"_routetable.tf"

            if(vcn_name+"_"+subnet_name not in subnets_done[region] or len(subnets_done[region])==0):
                if (tfStr!= ''):
                    tfStr = tfStr + """
        }"""
                    oname.write(tfStr)
                    oname.close()
                    tfStr = ''
                oname=open(outfile,'w')

                tfStr= tfStr + """
    resource "oci_core_route_table" \"""" + rt_var + """"{
        compartment_id = "${var.""" + comp_name + """}"
        vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
        display_name = \"""" +subnet_name +  """"
        
        ##Add More rules for subnet """ + rt_var+ """##
        """
                if(dest_cidr!=""):
                    tfStr=tfStr+"""
        
        route_rules {
            
                destination =\"""" + dest_cidr + """\"
                network_entity_id = \"""" + dest_obj + """\"
                destination_type = \"""" + dest_type + """\"
            }
            """
                subnets_done[region].append(vcn_name+"_"+subnet_name)

            else:
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

    elif(overwrite=='no'):
        print("Reading AddRouteRules sheet of cd3")
        df = pd.read_excel(inputfile, sheet_name='AddRouteRules')
        df.dropna(how='all')
        df.drop_duplicates()
        for i in df.index:
            region = df.iat[i, 0]
            region = str(region).lower()

            if (region in endNames):
                break
            if(region==NaNstr.lower() or region=='region'):
                continue
            region=region.strip()

            if region not in all_regions:
                print("Invalid Region; It should be one of the values mentioned in VCN Info tab")
                exit(1)
            comp_name = df.iat[i, 1]
            vcn_name = df.iat[i, 2]
            subnet_name = df.iat[i, 3]
            subnet_name = subnet_name.strip()

            # Process only those VCNs which are present in cd3(and have been created via TF)
            if (vcn_name not in cd3_tf_vcns):
                print("skipping route table: " + subnet_name + " as its VCN is not part of VCNs tab in cd3")
                continue
            dest_cidr = df.iat[i, 4]
            dest_cidr = str(dest_cidr).strip()
            dest_objs = df.iat[i, 5]
            dest_objs = str(dest_objs).strip().split(":")
            if ('ngw' in dest_objs[0].lower()):
                dest_obj = "${oci_core_nat_gateway." + dest_objs[1] + ".id}"

            elif ('sgw' in dest_objs[0].lower()):
                dest_obj = "${oci_core_service_gateway." + dest_objs[1] + ".id}"

            elif ('igw' in dest_objs[0].lower()):
                dest_obj = "${oci_core_internet_gateway." + dest_objs[1] + ".id}"

            elif ('lpg' in dest_objs[0].lower()):
                dest_obj = "${oci_core_local_peering_gateway." + dest_objs[1] + ".id}"
            elif ('drg' in dest_objs[0].lower() and 'ocid1' not in dest_objs[0].lower()):
                dest_obj = "${oci_core_drg." + dest_objs[1] + ".id}"
            else:
                dest_obj = dest_objs[0]

            dest_type = df.iat[i, 6]
            dest_type = str(dest_type).strip()

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

            searchString = "##Add More rules for subnet " + rt_var + "##"
            strRule = ""
            strRule = strRule + """
        route_rules {
            destination = \"""" + dest_cidr + """\"
            network_entity_id = \"""" + dest_obj + """\"
            destination_type = \"""" + dest_type + """\"
        }
        """
            strRule1 = strRule + "##Add More rules for subnet " + rt_var + "##"

            outfile = outdir + "/" + region + "/" + rt_var + "_routetable.tf"
            backup_file(outdir + "/" + region, rt_var + "_routetable.tf", overwrite)

            # Update file contents
            with open(outfile) as f:
                data = f.read()
            f.close()
            updated_data = re.sub(searchString, strRule1, data)
            with open(outfile, 'w') as f:
                f.write(updated_data)
            f.close()
        print("Route Rules added successfully. Please run terraform plan from your outdir to see the changes")

# If input is a csv file
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
                route_rules {
                destination = \"""" + dest_cidr + """\"
                network_entity_id = \"""" + dest_obj + """\"
                destination_type = \"""" + dest_type + """\"
                }
                """
            strRule1 = strRule + "##Add More rules for subnet " +rt_var+"##"

            outfile = outdir + "/" + region + "/" + rt_var + "_routetable.tf"
            backup_file(outdir + "/" + region, rt_var + "_routetable.tf", overwrite)

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
