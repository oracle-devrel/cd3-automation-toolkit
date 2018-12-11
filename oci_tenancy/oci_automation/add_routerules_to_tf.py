#!/bin/python

import sys
import argparse
import shutil
import re
######
# Takes in input csv which contains routerules to be updated for the subnet and updates the routes tf file created using base_tf_creation.
# ######



parser = argparse.ArgumentParser(description="Updates routelist for subnet. It accepts input file which contains new rules to be added to the existing rule list of the subnet.")
parser.add_argument("inputcsv", help="Required; Full Path to input route file containing rules to be updated; See example folder for sample format: add_routes-example.txt")
parser.add_argument("routefile", help= "Required: Full path of routes tf file which will be modified. This should ideally be the tf file which was created using create_all_tf_objects.py script.")

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)


args = parser.parse_args()
routefile = args.routefile
inputcsv = args.inputcsv

# Backup the existing Routes tf file
shutil.copy(routefile, routefile + "_backup")

# Open input CSV file
fname = open(inputcsv, "r")

# Read the input csv file
for route in fname:
    if not route.startswith('#'):
        print "processing : " + route
        subnet_name = route.split(":")[0]
        dest = route.split(":")[1]
        ntk_ent_id = route.split(":")[2]
        dest_type = route.split(":")[3]
        dest_type = dest_type.strip()

        searchString = "##Add More rules for subnet "+subnet_name+"##"

        strRule = ""
        strRule = strRule+"""
            route_rules {
	        destination = \"""" + dest_cidr + """\"
	        network_entity_id = \"""" + dest_obj + """\"
	        destination_type = \"""" + dest_type + """\"
	        }
	        """
        strRule = strRule + "##Add More rules for subnet " +subnet_name+"##"

        # Update file contents
        with open(routefile) as f:
            data = f.read()

        with open(routefile, 'w') as f:
            updated_data = re.sub(searchString, strRule, data)
            f.write(updated_data)

fname.close()
f.close()