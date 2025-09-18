import sys
import subprocess


def main():
    if len(sys.argv) != 3:
        print("Usage: python connectCloud.py <cloud_provider> <properties_file_path>")
        print("Example: python connectCloud.py oci tenancyconfig.properties")
        print("Example: python connectCloud.py azure connectAzure.properties")
        return

    cloud_provider = sys.argv[1].lower()
    argument = sys.argv[2]

    if cloud_provider == 'oci':
        script_name = 'user-scripts/createTenancyConfig.py'
    elif cloud_provider == 'azure':
        script_name = 'user-scripts/connectAzure.py'
    else:
        print("Invalid cloud provider. Use 'azure' or 'oci'.")
        return

    try:
        subprocess.run([sys.executable, script_name, argument], check=True)
    except subprocess.CalledProcessError as e:
        pass


if __name__ == "__main__":
    main()