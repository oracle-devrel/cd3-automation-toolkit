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


def fetch_compartments(outdir, outdir_struct, config=DEFAULT_LOCATION):
    configFileName = config
    config = oci.config.from_file(config)

    var_files={}
    var_data = {}

    ct = commonTools()
    ct.get_subscribedregions(configFileName)
    home_region = ct.home_region

    print("outdir specified should contain region directories and then variables_<region>.tf file inside the region directories eg /cd3user/tenancies/<customer_tenancy_name>/terraform_files")
    print("Verifying out directory and Taking backup of existing variables files...Please wait...")

    print("\nFetching Compartment Info...Please wait...")
    ct.get_network_compartment_ids(config['tenancy'], "root", configFileName)

    print("\nWriting to variables files...")

    home_region_services = ['identity', 'tagging', 'budget', 'cloud-guard']
    for region in ct.all_regions:
        # Fetch variables file inside region directories - single outdir
        if len(outdir_struct) == 0:
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
    for k,v in ct.ntk_compartment_ids.items():
        k = commonTools.check_tf_variable(k)
        v = "\"" + v + "\""
        compocidsStr = "\t" + k + " = " + v + "\n" + compocidsStr

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
    fetch_comp_file = f'{outdir}/fetchcompinfo.safe'
    with open(fetch_comp_file, 'w+') as f:
        f.write('run_fetch_script=0')
    f.close()


if __name__ == '__main__':
    args = parse_args()
    fetch_compartments(args.outdir, args.config)
