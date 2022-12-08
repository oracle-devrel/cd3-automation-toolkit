# CD3 Automation Toolkit

### Introduction
The CD3 Automation toolkit has been developed to help in automating the OCI resource object management. 
<br>
It reads input data in the form of CD3 Excel sheets and generates the terraform files instead of handling the task through the OCI console manually. This simplifies the management of the company's infrastructure as code.
<br>
![img.png](img.png)
<br><br>
### To build an image

* Change directory to cd3-automation-toolkit(i.e. cloned repo).
* Run docker build -t cd3toolkit:${image_tag} -f Dockerfile --pull --no-cache .
<br><br>
### To save the image (Optional)

* Run docker save cd3toolkit:${image_tag} | gzip > cd3toolkit_${image_tag}.tar.gz
<br><br>
### To run the CD3 container and exec into it
* Run docker run -it -d -v <path_in_local_system_where_the_files_must_be_generated>:/cd3user/tenancies <image_name>:<image_tag>
* Run docker ps
* Run docker exec -it <container_id> bash
<br><br>
Follow the toolkit docs i.e. from section "Configuring the Docker Container to connect to OCI Tenancy" of "01 CD3 Automation Tookit - End to End Process" inside cd3_automation_toolkit/documentation/user_guide to know HOW TO use to toolkit further.
<br><br>
https://github.com/oracle-devrel/cd3-automation-toolkit/blob/develop/cd3_automation_toolkit/documentation/user_guide/01%20CD3%20Automation%20Toolkit%20-%20End%20to%20End%20Process.pdf
<br><br>
Note : ${image_tag} should be replaced with suitable tag as per your requirements/standards.

       The above steps have been tested on Windows (Git Bash) and MacOS.
