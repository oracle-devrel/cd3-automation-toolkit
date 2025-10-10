

from typing import Dict
from common.python.commonTools import *
from typing import Dict, Optional
import os
# Azure SDKs
try:
    from azure.identity import ClientSecretCredential
    from azure.core.exceptions import HttpResponseError

except ImportError as e:
    raise ImportError(
        "Missing Azure SDK packages. Install with:\n"
        "  pip install azure-identity azure-mgmt-oracledatabase\n"
    )



def _read_properties_file(filepath: str) -> Dict[str, str]:
    """Read key=value pairs from setUpAzure.properties into a dict."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Azure properties file not found: {filepath}")
    props: Dict[str, str] = {}
    with open(filepath, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            props[k.strip()] = v.strip()
    required = ["subscription_id", "tenant_id", "client_id", "client_secret"]
    missing = [k for k in required if not props.get(k)]
    if missing:
        return "Missing required Azure credentials in {filepath}: {', '.join(missing)}"

    return props


class azrCommonTools():
    tagColumns = {'common tags', 'common_tags'}
    def authenticate(self,azure_properties_file):
        # Azure credential & client
        az = _read_properties_file(azure_properties_file)
        if "Missing required" in az:
            print("\nCannot run export workflow as authentication parameters are missing!!\n")
            exit()
        credential = ClientSecretCredential(
            tenant_id=az["tenant_id"],
            client_id=az["client_id"],
            client_secret=az["client_secret"],
        )
        credentials=[credential,az["subscription_id"]]
        return credentials

    def split_tag_values(columnname, columnvalue, tempdict):
        columnvalue = columnvalue.replace("\n", "")
        if ";" in columnvalue:
            # If there are more than one tag; split them by ";" and "="

            columnname = commonTools.check_column_headers(columnname)
            multivalues = columnvalue.split(";")
            multivalues = [part.split("=") for part in multivalues if part]

            tempdict = {columnname: multivalues}
        else:
            # If there is only one tag; split them only by "="; each key-value pair is stored as a list
            columnname = commonTools.check_column_headers(columnname)
            multivalues = columnvalue.split("=")
            multivalues = [str(part).strip() for part in multivalues if part]

            tempdict = {columnname: [multivalues]}
        return tempdict

    def _flatten_tags(tags: Optional[Dict[str, str]]) -> str:
        if not tags:
            return ""
        try:
            return ";".join([f"{k}={v}" for k, v in tags.items() if v is not None])
        except Exception:
            return ""

