#!/bin/bash

# Create Required Directories
mkdir -p ~/.oci

# Enable EPEL and Developer repositories
sudo dnf install -y oracle-epel-release-el9
sudo dnf install -y oraclelinux-release-el9
sudo dnf install -y procps-ng

# Upgrade pip
sudo dnf install python-pip -y
#sudo ln -s /usr/bin/pip3 /usr/bin/pip

# Install required Python packages
pip install --user oci-cli==3.51.2
pip install --user pycryptodomex==3.10.1
pip install --user regex==2022.10.31
pip install --user numpy==1.26.4
pip install --user pandas==1.1.5
pip install --user openpyxl==3.0.7
pip install --user xlrd==1.2.0
pip install --user xlsxwriter==3.2.0
pip install --user wget==3.2
pip install --user requests==2.28.2
pip install --user netaddr==0.8.0
pip install --user cfgparse==1.3
pip install --user ipaddress==1.0.23
pip install --user Jinja2==3.1.2
pip install --user simplejson==3.18.3
pip install --user GitPython==3.1.40
pip install --user PyYAML==6.0.1

# Add Python3 site-packages to PYTHONPATH
echo "export PYTHONPATH=\${PYTHONPATH}:/root/.local/lib/python3.9/site-packages/:/cd3user/.local/lib/python3.9/site-packages/" >> /cd3user/.bashrc

# Add Python binaries to PATH
echo "PATH=\$PATH:/cd3user/.local/bin" >> /cd3user/.bashrc


# Download and install Terraform
#sudo dnf install -y https://yum.oracle.com/repo/OracleLinux/OL9/developer/x86_64/getPackage/terraform-1.3.6-1.el9.x86_64.rpm
sudo dnf install -y wget
sudo dnf install -y unzip
#sudo wget https://releases.hashicorp.com/terraform/1.3.6/terraform_1.3.6_linux_amd64.zip
sudo wget https://releases.hashicorp.com/terraform/1.5.7/terraform_1.5.7_linux_amd64.zip
unzip terraform_1.5.7_linux_amd64.zip
sudo mv terraform /usr/local/sbin/
sudo rm terraform_1.5.7_linux_amd64.zip

# Download and Install OpenTofu
sudo wget --content-disposition "https://packagecloud.io/opentofu/tofu/packages/rpm_any/rpm_any/tofu-1.6.2-1.x86_64.rpm/download.rpm?distro_version_id=227"
sudo rpm -i tofu-1.6.2-1.x86_64.rpm
sudo rm tofu-1.6.2-1.x86_64.rpm

# Download and install OPA
curl -L -o opa https://openpolicyagent.org/downloads/v0.55.0/opa_linux_amd64_static
sudo chmod +x opa && sudo mv opa /usr/local/sbin/
