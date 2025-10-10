import sys
import subprocess


def main():
    if len(sys.argv) != 3:
        print("Usage: python setUpCloud.py <cloud_provider> <properties_file_path>")
        print("Example: python setUpCloud.py azure setUpAzure.properties")
        print("Example: python setUpCloud.py oci setUpOCI.properties")
        return

    cloud_provider = sys.argv[1].lower()
    argument = sys.argv[2]

    if cloud_provider == 'oci':
        script_name = 'setUpOCI.py'
    elif cloud_provider == 'azure':
        script_name = 'user-scripts/setUpAzure.py'
    else:
        print("Invalid cloud provider. Use 'azure' or 'oci'.")
        return

    try:
        subprocess.run([sys.executable, script_name, argument], check=True)
    except subprocess.CalledProcessError as e:
        pass


if __name__ == "__main__":
    main()