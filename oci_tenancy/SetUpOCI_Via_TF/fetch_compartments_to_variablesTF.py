import sys
import argparse
from jinja2 import Environment, FileSystemLoader
from commonTools import *

#Load the template file
file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader,keep_trailing_newline=True)
template = env.get_template('variables-template')

def paginate(operation, *args, **kwargs):
    while True:
        response = operation(*args, **kwargs)
        for value in response.data:
            yield value
        kwargs["page"] = response.next_page
        if not response.has_next_page:
            break


def parse_args():
    parser = argparse.ArgumentParser(description="Fetches Compartment name/ocid info from OCI and pushes to variables.tf file of each region used by TF")
    parser.add_argument("outdir", help="Path  to outdir(on OCSVM: /root/ocswork/terraform_files) containing region directories having variables_<region>.tf file that will be used by TerraForm to communicate with OCI")
    parser.add_argument("--config", default=DEFAULT_LOCATION, help="Config file name")
    return parser.parse_args()


def fetch_compartments(outdir, config=DEFAULT_LOCATION):
    configFileName = config
    config = oci.config.from_file(config)

    tempStr = {}
    var_files={}
    var_data={}

    print("outdir specified should contain region directories and then variables_<region>.tf file inside the region directories eg /root/ocswork/terraform_files")

    ct = commonTools()
    ct.get_subscribedregions(configFileName)
    ct.get_network_compartment_ids(config['tenancy'], "root", configFileName)

    for region in ct.all_regions:
        file = f'{outdir}/{region}/variables_{region}.tf'
        var_files[region]=file
        tempStr[region]=''
        try:
            with open(file, 'r') as f:
                var_data[region] = f.read()
        except FileNotFoundError as e:
            exit_menu(f'\nVariables file not found in region - {region}.......Exiting!!!\n')
        # Backup the existing Routes tf file
        shutil.copy(file, file + "_backup")

    for reg in ct.all_regions:
        for name, ocid in ct.ntk_compartment_ids.items():
            comp_tf_name=commonTools.check_tf_variable(name)
            searchstr = "variable \"" + comp_tf_name + "\""
            str=template.render(var_tf_name=comp_tf_name,values=ocid)
            if(searchstr not in var_data[reg]):
                tempStr[reg]=tempStr[reg]+str

        if ("linux" in sys.platform):
            os.system("dos2unix " + var_files[reg])

        with open(var_files[reg],"a") as vname:
            vname.write(tempStr[reg])
    print("Compartment info written to all region specific variables files under outdir folder")


if __name__ == '__main__':
    args = parse_args()
    fetch_compartments(args.outdir, args.config)
