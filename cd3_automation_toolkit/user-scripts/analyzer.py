#!/usr/bin/python3
# Copyright (c) 2026, Oracle and/or its affiliates. All rights reserved.
#
# This script provides AI-powered analysis of Terraform plans for OCI infrastructure.
# It integrates with OCI Generative AI service to perform security scanning and compliance checking
# against CIS OCI Benchmark v1.2 standards.

# Author: Ulaganathan N

import oci
import json
import sys
import os

# Add parent directory to path to find ocicloud module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ocicloud.python.ociCommonTools import ociCommonTools


# ANSI Color codes
class Colors:
    RED = '\033[1;31m'
    GREEN = '\033[1;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[1;34m'
    PURPLE = '\033[1;35m'
    CYAN = '\033[1;36m'
    WHITE = '\033[1;37m'
    BLACK = '\033[1;30m'
    BOLD = '\033[1m'
    END = '\033[0m'


# Default model that works with on-demand
# TODO need to research on this further to include/update additional LLM models.
DEFAULT_MODEL = "cohere.command-r-plus-08-2024"


def get_subscribed_regions(ct, config, signer):
    """Get all subscribed regions for the tenancy using ociCommonTools"""
    try:
        regions = ct.get_subscribedregions(config, signer)
        print(f"Found subscribed regions: {regions}")
        return regions
    except Exception as e:
        print(f"Could not get subscribed regions: {e}")
        return []


def extract_plan_summary(plan_data):
    """Extract detailed technical information from terraform plan"""
    if not plan_data or "resource_changes" not in plan_data:
        return None

    changes = plan_data["resource_changes"]
    summary = {
        "total_changes": len(changes),
        "actions": {"create": 0, "update": 0, "delete": 0},
        "resources": [],
        "resource_types": {},
        "shapes": {},
    }

    for change in changes:
        actions = change.get("change", {}).get("actions", [])
        change_details = change.get("change", {})

        after_config = change_details.get("after") or {}
        before_config = change_details.get("before") or {}

        resource_info = {
            "address": change.get("address"),
            "type": change.get("type"),
            "actions": actions,
            "shape": after_config.get("shape") or before_config.get("shape"),
        }

        for action in actions:
            if action in summary["actions"]:
                summary["actions"][action] += 1

        resource_type = change.get("type", "unknown")
        summary["resource_types"][resource_type] = summary["resource_types"].get(resource_type, 0) + 1

        if resource_info["shape"]:
            summary["shapes"][resource_info["shape"]] = summary["shapes"].get(resource_info["shape"], 0) + 1

    return summary


def create_colored_table(headers, rows, header_color, data_color):
    """Create colorful ASCII table for jenkins builds"""
    if not rows:
        return ""

    col_widths = [len(str(header)) for header in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    col_widths = [w + 4 for w in col_widths]

    table = []
    border = f"{Colors.BLACK}+" + "+".join("=" * w for w in col_widths) + f"+{Colors.END}"
    table.append(border)

    header_row = f"{Colors.BLACK}|{Colors.END}"
    for i, header in enumerate(headers):
        header_row += f"{header_color}{str(header).center(col_widths[i])}{Colors.END}{Colors.BLACK}|{Colors.END}"
    table.append(header_row)
    table.append(border)

    for row in rows:
        data_row = f"{Colors.BLACK}|{Colors.END}"
        for i, cell in enumerate(row):
            cell_str = str(cell)
            if cell_str == "SAFE":
                colored_cell = f"{Colors.GREEN}{cell_str}{Colors.END}"
            elif cell_str == "REVIEW":
                colored_cell = f"{Colors.YELLOW}{cell_str}{Colors.END}"
            elif cell_str == "CRITICAL":
                colored_cell = f"{Colors.RED}{cell_str}{Colors.END}"
            else:
                colored_cell = f"{Colors.BLACK}{cell_str}{Colors.END}"

            cell_length = len(str(cell))
            padding = (col_widths[i] - cell_length) // 2
            left_pad = ' ' * padding
            right_pad = ' ' * (col_widths[i] - cell_length - padding)

            data_row += f"{left_pad}{colored_cell}{right_pad}{Colors.BLACK}|{Colors.END}"
        table.append(data_row)

    table.append(border)
    return "\n".join(table)


def display_deployment_summary(plan_summary):
    """Display deployment summary tables"""
    if not plan_summary:
        return

    print(f"\n{Colors.BOLD}{Colors.PURPLE}>> DEPLOYMENT SUMMARY{Colors.END}")

    # Actions table
    print(f"\n{Colors.YELLOW}[ACTIONS BREAKDOWN]{Colors.END}")
    actions_data = [
        ["CREATE", plan_summary['actions']['create'], "SAFE"],
        ["UPDATE", plan_summary['actions']['update'], "REVIEW"],
        ["DELETE", plan_summary['actions']['delete'], "CRITICAL"]
    ]
    actions_table = create_colored_table(["Action", "Count", "Status"], actions_data, Colors.CYAN, Colors.WHITE)
    print(actions_table)

    # Resource types table
    if plan_summary['resource_types']:
        print(f"\n{Colors.GREEN}[RESOURCE TYPES]{Colors.END}")
        resource_data = [[rtype, count] for rtype, count in plan_summary['resource_types'].items()]
        resource_table = create_colored_table(["Resource Type", "Count"], resource_data, Colors.GREEN, Colors.WHITE)
        print(resource_table)

    # Shapes table
    if plan_summary['shapes']:
        print(f"\n{Colors.CYAN}[COMPUTE SHAPES]{Colors.END}")
        shapes_data = [[shape, count] for shape, count in plan_summary['shapes'].items()]
        shapes_table = create_colored_table(["Shape", "Instances"], shapes_data, Colors.YELLOW, Colors.WHITE)
        print(shapes_table)


def format_plan_for_ai(plan_data):
    summary = []
    if "resource_changes" not in plan_data:
        return "No resource changes found in the plan."

    for change in plan_data.get("resource_changes", []):
        address = change.get("address", "N/A")
        change_type = change.get("change", {}).get("actions", ["no-op"])[0].upper()
        if change_type == "NO-OP":
            continue
        summary.append(f"## {change_type}: {address}")

        # Include compartment info
        after = change.get("change", {}).get("after") or {}
        before = change.get("change", {}).get("before") or {}

        # Get actual compartment OCID (not tenancy root)
        compartment_id = after.get("compartment_id") or before.get("compartment_id") or "not specified"

        # Get key security-relevant properties
        if change_type in ["CREATE", "UPDATE"]:
            if after:
                # Extract important properties
                important_props = []
                for key in ['shape', 'assign_public_ip', 'display_name', 'subnet_id', 'vcn_id',
                            'bucket_name', 'public_access_type', 'encryption_type', 'kms_key_id',
                            'freeform_tags', 'defined_tags', 'source', 'destination']:
                    if key in after and after[key]:
                        important_props.append(f"{key}: {after[key]}")
                if important_props:
                    summary.append(f"  Compartment: {compartment_id}")
                    summary.append("  Properties: " + "; ".join(important_props))

        summary.append("")
    return "\n".join(summary)


def build_prompt(plan_summary, tenancy_info):
    return f"""
You are an expert Oracle Cloud Infrastructure (OCI) cloud and security DevOps architect specializing in CIS OCI Benchmark v1.2. Analyze this Terraform plan.

**Context:**
- Home Region: {tenancy_info.get('home_region', 'N/A')}

**Plan Details:**
{plan_summary[:3000]}

**Output Requirements - STRICT FORMAT:**

## OVERVIEW
One sentence: Overall risk level (Low/Medium/High/Critical) with main concern.

## CIS FINDINGS
Provide table with these EXACT columns - no extra text outside table:
| # | CIS-ID | Severity | Resource Type | Finding | Recommendation |

Examples:
| 1 | CIS 3.1 | HIGH | Compute | Public IP assigned | Set assign_public_ip=false |
| 2 | CIS 2.1 | MEDIUM | General | No compartment specified | Use sub-compartment OCID |

## RISK IMPACT
- Blast Radius: <one line>
- Compliance Status: <PASS/FAIL>  
- Issues Found: <count>

## ESTIMATE
- Deploy Time: <X-Y minutes>
- Est. Monthly Cost: <$X-Y USD>
- Resources: Create=<X> Update=<Y> Delete=<Z>

## REMEDIATION PRIORITY
List top 3 critical fixes needed as numbered bullets.

Be specific with resource names, OCIDs from the plan. No generic statements.
"""


def main():
    if len(sys.argv) != 2:
        print("Usage: python analyzer.py <path_to_tfplan.json>", file=sys.stderr)
        sys.exit(1)

    plan_file_path = sys.argv[1]

    try:
        with open(plan_file_path, 'r') as f:
            plan_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Plan file not found at {plan_file_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {plan_file_path}", file=sys.stderr)
        sys.exit(1)

    config_file = os.environ.get("OCI_CONFIG_FILE", oci.config.DEFAULT_LOCATION)
    auth_mechanism = os.environ.get("OCI_AUTH_MECHANISM", "api_key")

    ct = ociCommonTools()
    config, signer = ct.authenticate(auth_mechanism, config_file)

    # Extract and display plan summary
    plan_summary = extract_plan_summary(plan_data)
    if plan_summary:
        display_deployment_summary(plan_summary)

    # Get user's region from OCI config
    user_region = config.get("region", "")
    print(f"\nUser's OCI region: {user_region}")

    # Get model from environment variable
    model_id = os.environ.get("OCI_GENERATIVE_AI_MODEL", DEFAULT_MODEL)
    print(f"Using model: {model_id}")

    # Get all subscribed regions dynamically
    subscribed_regions = get_subscribed_regions(ct, config, signer)

    # Convert short region names to full region keys
    full_region_subscriptions = []
    for region in subscribed_regions:
        if region in ct.region_dict:
            full_region = ct.region_dict[region]
            if full_region not in full_region_subscriptions:
                full_region_subscriptions.append(full_region)
        elif region not in full_region_subscriptions:
            full_region_subscriptions.append(region)

    # Build list of regions to try
    regions_to_try = []

    if user_region and user_region != "None":
        regions_to_try.append(user_region)

    for region in full_region_subscriptions:
        if region not in regions_to_try:
            regions_to_try.append(region)

    if len(regions_to_try) <= 1:
        fallback_regions = ["uk-london-1", "eu-frankfurt-1", "sa-saopaulo-1"]
        for region in fallback_regions:
            if region not in regions_to_try:
                regions_to_try.append(region)

    print(f"Regions to try: {regions_to_try}")

    # Build tenancy info for the prompt
    tenancy_info = {
        'tenancy_id': config.get('tenancy', 'N/A'),
        'regions': full_region_subscriptions,
        'home_region': getattr(ct, 'home_region', 'N/A')
    }

    ai_plan_summary = format_plan_for_ai(plan_data)
    prompt = build_prompt(ai_plan_summary, tenancy_info)

    print(f"\n{Colors.CYAN}>> Generating AI analysis...{Colors.END}")

    analysis_result = None
    last_error = None

    # Try each subscribed region until one works
    for region in regions_to_try:
        service_endpoint = f"https://inference.generativeai.{region}.oci.oraclecloud.com"

        print(f"Trying region: {region}...")

        try:
            generative_ai_client = oci.generative_ai_inference.GenerativeAiInferenceClient(
                config=config,
                signer=signer,
                service_endpoint=service_endpoint
            )

            chat_request = oci.generative_ai_inference.models.CohereChatRequest(
                message=prompt,
                max_tokens=1024,
                temperature=0.2,
            )

            serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(
                model_id=model_id
            )

            chat_details = oci.generative_ai_inference.models.ChatDetails(
                compartment_id=config["tenancy"],
                serving_mode=serving_mode,
                chat_request=chat_request
            )

            response = generative_ai_client.chat(chat_details)

            if hasattr(response.data, 'chat_response'):
                analysis_result = response.data.chat_response.text
            else:
                analysis_result = str(response.data)

            print(f"Successfully connected using region: {region}")
            print(f"Service endpoint: {service_endpoint}")
            break

        except oci.exceptions.ServiceError as e:
            last_error = e
            print(f"Region {region} failed: {e.message}")
            continue
        except Exception as e:
            last_error = e
            print(f"Error with region {region}: {e}")
            continue

    if not analysis_result:
        print(f"\nError: All regions failed. Last error: {last_error}", file=sys.stderr)
        sys.exit(1)

    print(f"\n{Colors.BOLD}{Colors.PURPLE}>> AI ANALYSIS{Colors.END}")

    # Color code the OCI Gen AI response
    colored_analysis = analysis_result.replace("High", f"{Colors.RED}High{Colors.END}")
    colored_analysis = colored_analysis.replace("Medium", f"{Colors.YELLOW}Medium{Colors.END}")
    colored_analysis = colored_analysis.replace("Low", f"{Colors.GREEN}Low{Colors.END}")
    colored_analysis = colored_analysis.replace("CRITICAL", f"{Colors.RED}CRITICAL{Colors.END}")
    colored_analysis = colored_analysis.replace("HIGH", f"{Colors.RED}HIGH{Colors.END}")

    print(f"{Colors.PURPLE}{colored_analysis}{Colors.END}")
    print(f"\n{Colors.BOLD}{Colors.GREEN}{'=' * 80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.WHITE}{'ANALYSIS COMPLETE':^80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}{'=' * 80}{Colors.END}")


if __name__ == "__main__":
    main()
