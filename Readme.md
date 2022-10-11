# CD3 Automation Toolkit


### To build an image and run CD3 container.

* Change directory to cd3-automation-toolkit(i.e. cloned repo).
* Run docker build -t cd3toolkit:${image_tag} -f Dockerfile --pull --no-cache .
* Run docker save cd3toolkit:${image_tag} | gzip > cd3toolkit_${image_tag}.tar.gz
* Run docker load < cd3toolkit_${image_tag}.tar.gz
* Follow the toolkit docs(i.e. inside cd3_automation_toolkit dir) to know HOW TO use to toolkit further.

Note : image_tag should be replaced with suiteable tag as per your requirements/standards.
