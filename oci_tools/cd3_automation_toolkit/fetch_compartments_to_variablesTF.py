import sys
import argparse
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from commonTools import *

def parse_args():
    parser = argparse.ArgumentParser(description="Fetches Compartment name/ocid info from OCI and pushes to variables.tf file of each region used by TF")
    parser.add_argument('outdir', help='Output directory for creation of TF files')
    parser.add_argument("--config", default=DEFAULT_LOCATION, help="Config file name")
    return parser.parse_args()


def fetch_compartments(outdir, config=DEFAULT_LOCATION):
    configFileName = config
    config = oci.config.from_file(config)

    var_files={}
    var_data = {}
    comp_ocids = []
    comp_tf_name = ''

    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    print("outdir specified should contain region directories and then variables_<region>.tf file inside the region directories eg /cd3user/tenancies/<customer_tenancy_name>/terraform_files")
    print("Verifying out directory and Taking backup of existing variables files...Please wait...")

    for region in ct.all_regions:
        file = f'{outdir}/{region}/variables_{region}.tf'
        var_files[region]=file
        try:
            # Read variables file data
            with open(file, 'r') as f:
                var_data[region] = f.read()
        except FileNotFoundError as e:
            exit_menu(f'\nVariables file not found in region - {region}.......Exiting!!!\n')
        # Backup the existing Routes tf file
        shutil.copy(file, file + "_backup")


    print("Fetching Compartment Info...Please wait...")
    ct.get_network_compartment_ids(config['tenancy'], "root", configFileName)

    compocidsStr = ''
    for k,v in ct.ntk_compartment_ids.items():
        k = commonTools.check_tf_variable(k)
        v = "\"" + v + "\""
        compocidsStr = "\t" + k + " = " + v + "\n" + compocidsStr

    compocidsStr = "\n" + compocidsStr

    finalCompStr = "#START_compartment_ocids#" + compocidsStr +  "\t#compartment_ocids_END#"

    for reg in ct.all_regions:
        var_data[reg] = re.sub('#START_compartment_ocids#.*?#compartment_ocids_END#', finalCompStr,var_data[reg], flags=re.DOTALL)

        # Write variables file data
        with open(var_files[reg], "w") as f:
            f.write(var_data[reg])

        # if ("linux" in sys.platform):
        #     os.system("dos2unix " + var_files[reg])

    print("Compartment info written to all region specific variables files under outdir folder")

if __name__ == '__main__':
    args = parse_args()
    fetch_compartments(args.outdir, args.config)
