import oci
import pandas as pd
import os
from openpyxl import load_workbook
from openpyxl.utils import column_index_from_string
from openpyxl.styles import Alignment, PatternFill, Font
import argparse
from commonLib import *

parser = argparse.ArgumentParser()
parser.add_argument("-o", "--ocid", help="Provide the DR Plan OCID")
parser.add_argument("-s", "--sheet", help="Provide the sheet name under which the value is stored")
parser.add_argument("-f", "--file", help="Provide name of the file to be created/updated")
parser.add_argument("-c", "--config", help="OCI config profile path")
parser.add_argument("-i", "--instance_principal", help="OCI config profile path", nargs='?', const=1, type=int)
args = parser.parse_args()

# Define a function to extract the region from the OCID


try:
    region_file = os.path.dirname(os.path.abspath(__file__))+"/region_file.json"
    region_map = load_region_map(region_file)
    region = get_region_from_ocid(args.ocid, region_map)
except Exception as e:
    print(f"Error loading region map: {str(e)}")
    exit(1)

try:
    config = oci.config.from_file(file_location=args.config)
except Exception as e:
    print(f"Error loading OCI config: {str(e)}")
    print(".....Exiting!!!")
    exit(1)

if args.ocid:
    config['region'] = region

try:
    if args.instance_principal == 1:
        signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
    elif args.config != '':
        signer = oci.signer.Signer(config['tenancy'], config['user'], config['fingerprint'], config['key_file'])
except Exception as e:
    print(f"Error creating signer: {str(e)}")
    exit(1)

try:
    # Get DR Plan
    disaster_recovery_client = oci.disaster_recovery.DisasterRecoveryClient(
        config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY, signer=signer)
    get_dr_plan_response = disaster_recovery_client.get_dr_plan(dr_plan_id=args.ocid)
    plan_groups = get_dr_plan_response.data.plan_groups
    # Extract the order of plan groups
    original_order = [pg.id for pg in plan_groups]

    # Manually convert DrPlanGroup objects to dictionaries
    plan_dicts = []
    for pg in plan_groups:
        steps = []
        for step in pg.steps:
            step_dict = {
                'display_name': step.display_name,
                'error_mode': step.error_mode,
                'id': step.id,
                'is_enabled': step.is_enabled,
                'timeout': step.timeout,
                'type': step.type,
            }
            if hasattr(step, 'user_defined_step') and step.user_defined_step:
                user_defined_step = {
                    'step_type': step.user_defined_step.step_type,
                    'run_as_user': getattr(step.user_defined_step, 'run_as_user', None),
                    'run_on_instance_id': getattr(step.user_defined_step, 'run_on_instance_id', None),
                    'function_id': getattr(step.user_defined_step, 'function_id', None),
                    'function_region': getattr(step.user_defined_step, 'function_region', None),
                    'request_body': getattr(step.user_defined_step, 'request_body', None),
                    'object_storage_script_location': {
                        'bucket': getattr(step.user_defined_step.object_storage_script_location, 'bucket', None),
                        'namespace': getattr(step.user_defined_step.object_storage_script_location, 'namespace', None),
                        'object': getattr(step.user_defined_step.object_storage_script_location, 'object', None)
                    } if getattr(step.user_defined_step, 'object_storage_script_location', None) else None,
                    'run_on_instance_region': getattr(step.user_defined_step, 'run_on_instance_region', None),
                    'script_command': getattr(step.user_defined_step, 'script_command', None)
                }
                step_dict['user_defined_step'] = user_defined_step
            steps.append(step_dict)
        plan_dicts.append({
            'display_name': pg.display_name,
            'id': pg.id,
            'type': pg.type,
            'steps': steps
        })

    # Convert the parsed plan data to a DataFrame
    df = pd.json_normalize(plan_dicts)

    # Split the data into two parts based on the "type" value
    built_in_df = df[df['type'] == 'BUILT_IN']
    other_df = df[df['type'] != 'BUILT_IN']

    # Function to normalize and reformat data
    def normalize_and_reformat(df):
        dict_list_orient = df.to_dict('records')
        normalized_data = pd.json_normalize(dict_list_orient, "steps", ['display_name', 'id', 'type'], record_prefix='steps.')
        columns_order = [
            'display_name', 'id', 'steps.display_name', 'steps.error_mode', 'steps.id', 'steps.is_enabled',
            'steps.timeout', 'steps.type', 'type'
        ]
        normalized_data = normalized_data.reindex(columns=columns_order, fill_value=None)
        return normalized_data

    def normalize_other_data(df):
        dict_list_orient = df.to_dict('records')
        normalized_data = pd.json_normalize(dict_list_orient, "steps", ['display_name', 'id', 'type'], record_prefix='steps.')
        columns_order = [
            'display_name', 'id', 'steps.display_name', 'steps.error_mode', 'steps.id', 'steps.is_enabled',
            'steps.timeout', 'steps.type', 'steps.user_defined_step.step_type',
            'steps.user_defined_step.run_as_user', 'steps.user_defined_step.run_on_instance_id',
            'steps.user_defined_step.function_id', 'steps.user_defined_step.function_region', 'steps.user_defined_step.request_body',
            'steps.user_defined_step.object_storage_script_location.bucket', 'steps.user_defined_step.object_storage_script_location.namespace', 'steps.user_defined_step.object_storage_script_location.object',
            'steps.user_defined_step.run_on_instance_region', 'steps.user_defined_step.script_command', 'type'
        ]
        normalized_data = normalized_data.reindex(columns=columns_order, fill_value=None)
        return normalized_data

    # Normalize and reformat both subsets of data
    built_in_data = normalize_and_reformat(built_in_df)
    other_data = normalize_other_data(other_df)

    # Append both subsets of data into one DataFrame
    combined_data = pd.concat([other_data, built_in_data], ignore_index=True)

    # Sort the combined data based on the original order
    combined_data['sort_order'] = pd.Categorical(combined_data['id'], categories=original_order, ordered=True)
    combined_data.sort_values('sort_order', inplace=True)
    combined_data.drop(columns=['sort_order'], inplace=True)

    # Write the combined data to an Excel file
    excel_file = args.file
    sheet = args.sheet
    combined_data.to_excel(excel_file, index=False, sheet_name=sheet)

    # Load the workbook and select the sheet
    wb = load_workbook(excel_file)
    ws = wb[sheet]

    # Function to merge and center cells with the same values in a column
    def merge_and_center(ws, col):
        max_row = ws.max_row
        for row in range(2, max_row + 1):
            cell_value = ws.cell(row=row, column=col).value
            start_row = row
            while row <= max_row and ws.cell(row=row, column=col).value == cell_value:
                row += 1
            end_row = row - 1
            if start_row != end_row:
                ws.merge_cells(start_row=start_row, start_column=col, end_row=end_row, end_column=col)
                merged_cell = ws.cell(row=start_row, column=col)
                merged_cell.alignment = Alignment(horizontal='center', vertical='center')

    # Check if the file exists
    if os.path.isfile(excel_file):
        with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            combined_data.to_excel(writer, sheet_name=sheet, index=False)
            workbook = writer.book
            worksheet = writer.sheets[sheet]
    else:
        with pd.ExcelWriter(excel_file, engine='openpyxl', mode='w') as writer:
            combined_data.to_excel(writer, sheet_name=sheet, index=False)
            workbook = writer.book
            worksheet = writer.sheets[sheet]

    # Define the columns to merge and center (using 1-based index)
    columns_to_merge = ['A', 'B']  # Example: 'display_name', 'id', 'type'

    for col in columns_to_merge:
        col_index = column_index_from_string(col)
        merge_and_center(ws, col_index)

    # Define fill colors
    fill_blue = PatternFill(start_color="346EC9", end_color="346EC9", fill_type="solid")
    fill_purple = PatternFill(start_color="858491", end_color="858491", fill_type="solid")
    font_white = Font(color="FFFFFF", bold=True)

    # Apply fill colors to headers
    header_cells = ws[1]  # First row is header
    for cell in header_cells:
        if cell.column_letter in ['A', 'B', 'T']:
            cell.fill = fill_blue
            cell.font = font_white
        else:
            cell.fill = fill_purple
            cell.font = font_white

    # Auto-adjust column widths
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter  # Get the column name
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column].width = adjusted_width

    # Save the modified workbook
    wb.save(excel_file)
    print("Excel file updated successfully.")
except Exception as e:
    print(f"An error occurred: {str(e)}")
    exit(1)
