from oci.identity import IdentityClient
import oci
import os
import xml.etree.ElementTree as ET
import datetime
import ssl
import pathlib
import urllib
import shutil
import sys
class cd3Services():

    #Get OCI Cloud Regions
    regions_list = ""
    def fetch_regions(self,config,signer):
        #config = oci.config.from_file(file_location=configFileName)
        idc = IdentityClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)
        try:
            regions_list = idc.list_regions().data
        except Exception as e:
            print(e)
            if ('NotAuthenticated' in str(e)):
                print("\nInvalid Credetials - check your keypair/fingerprint/region...Exiting!!!")
                exit(1)

        if ("OCSWorkVM" in os.getcwd() or 'user-scripts' in os.getcwd()):
            os.chdir("../")

        tempStr = '#Region:Region_Key\n'
        reg_dict = {}

        for reg in regions_list:
            cd3key = str(reg.name.split('-',1)[1]).lower()

            if 'dcc' in cd3key:
                cd3key = str(cd3key.split('-',1)[1]).lower()

            name = str(reg.name).lower()
            reg_dict[cd3key] = name

        keys = []
        new_reg_dict={}
        for key,val in reg_dict.items():
            keyy = key.split("-")[0]
            if keyy not in keys:
                keys.append(keyy)
                new_reg_dict[keyy]=val
            else:
                new_reg_dict[key] = val

                #replace prev
                old_val = new_reg_dict[keyy]
                old_val_key = str(old_val.split('-', 1)[1]).lower()
                if 'dcc' in old_val_key:
                    old_val_key = str(old_val_key.split('-', 1)[1]).lower()

                new_reg_dict[old_val_key] = old_val
                new_reg_dict.pop(keyy)

        for cd3key,name in new_reg_dict.items():
            line = cd3key + ":" + name
            tempStr = tempStr + line + '\n'

        with open('OCI_Regions', 'w+') as f:
            f.write(tempStr)
        f.close()
        print("Updated OCI_Regions file !!!\n")

    # Parse XML - Used by OCI Protocols
    def parse_xml(source: str) -> ET.Element:
        it = ET.iterparse(open(source))
        # strip namespaces
        for _, el in it:
            if "}" in el.tag:
                el.tag = el.tag.split("}", 1)[1]
        root = it.root  # mypy: ignore
        return root

    # Parse Date - Used by OCI Protocols
    def parse_date(root_xml: ET.Element) -> datetime:
        updated = root_xml.find("updated")
        assert updated is not None and isinstance(updated.text, str)
        return datetime.datetime.strptime(updated.text, "%Y-%m-%d")

    # write_protocols_file - Used for OCI Protocols
    def write_protocols_file(source: str, destination: str) -> datetime:
        root = cd3Services.parse_xml(source)
        updated = cd3Services.parse_date(root)
        destination = str(pathlib.Path.cwd())+"/"+destination
        with open(destination,"w+") as dst:
            dst.write("#protocol number:protocol name\n")
            for r in root.iter("record"):
                desc_ = r.find("description")
                if desc_ is None or desc_.text is None:
                    desc = ""
                else:
                    desc = desc_.text
                name_ = r.find("name")
                value_ = r.find("value")
                if (value_ is None
                    or value_.text is None):
                    continue
                if (name_ is None
                    or name_.text is None):
                    name = desc
                    dst.write(str(value_.text) + ":" + name + "\n")
                    continue
                alias = name_.text.split()[0]
                value = int(value_.text)
                dst.write(str(value)+":"+alias+"\n")
        return updated

    def download(url: str, path: str) -> None:
        with open(path, "wb") as dst, urllib.request.urlopen(url) as src:
            shutil.copyfileobj(src, dst)

    #Get OCI Protocols
    def fetch_protocols(self) -> None:

        ssl._create_default_https_context = ssl._create_unverified_context
        PROTOCOLS_URL = "https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xml"
        PROTOCOLS_XML = "protocol-numbers.xml"
        PROTOCOLS_FILE = "OCI_Protocols"

        ##### main code for oci protocols ####
        protocols_xml = str(pathlib.Path.cwd()) + "/" + PROTOCOLS_XML
        try:
            cd3Services.download(PROTOCOLS_URL, protocols_xml)
        except OSError as e:
            print("Could not download iana service names and port numbers: {}".format(e),
                  file=sys.stderr,
                  )
            sys.exit(1)
        cd3Services.write_protocols_file(protocols_xml, PROTOCOLS_FILE)
        rem_file = pathlib.Path(protocols_xml)
        rem_file.unlink()

        print("Updated OCI_Protocols file !!!\n")