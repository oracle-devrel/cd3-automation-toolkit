# CD3 Automation Toolkit


### To build an image and run CD3 container.

* Change directory to cd3-automation-toolkit(i.e. cloned repo).
* Run docker build -t cd3toolkit:${image_tag} -f Dockerfile --pull --no-cache .
* Run docker save cd3toolkit:${image_tag} | gzip > cd3toolkit_${image_tag}.tar.gz
* Follow the toolkit docs i.e. from section "Deploy" of "01 CD3 Automation Tookit - End to End Process" inside cd3_automation_toolkit/documentation/user_guide dir to know HOW TO use to toolkit further.

Note : image_tag should be replaced with suiteable tag as per your requirements/standards.
