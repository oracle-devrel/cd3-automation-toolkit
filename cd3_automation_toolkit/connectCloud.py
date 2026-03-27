import sys
import subprocess


def main():
    if len(sys.argv) != 3:
        print("Usage: python connectCloud.py <cloud_provider> <properties_file_path>")
        print("Example: python connectCloud.py oci connectOCI.properties")
        print("Example: python connectCloud.py azure connectAzure.properties")
        print("Example: python connectCloud.py gcp connectGCP.properties")
        print("Example: python connectCloud.py aws connectAWS.properties")
        return

    cloud_provider = sys.argv[1].lower()
    argument = sys.argv[2]

    if cloud_provider == 'oci':
        script_name = 'user-scripts/createTenancyConfig.py'
    elif cloud_provider == 'azure':
        script_name = 'user-scripts/connectAzure.py'
    elif cloud_provider == 'gcp':
        script_name = 'user-scripts/connectGCP.py'
    elif cloud_provider == 'aws':
        script_name = 'user-scripts/connectAWS.py'
    else:
        print("Invalid cloud provider. Use 'azure' or 'aws' or 'oci' or 'gcp'.")
        return

    try:
        subprocess.run([sys.executable, script_name, argument], check=True)
    except subprocess.CalledProcessError as e:
        pass


if __name__ == "__main__":
    main()