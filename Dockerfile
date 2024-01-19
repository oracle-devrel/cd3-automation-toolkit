FROM oraclelinux:7-slim
LABEL maintainer="Team at Oracle"
LABEL description="OCI format to generate CD3 image"

ARG USERNAME=cd3user
ARG USER_UID=1001
ARG USER_GID=$USER_UID

RUN yum install sudo -y && groupadd --gid $USER_GID $USERNAME \
&& useradd --uid $USER_UID --gid $USER_GID -d /$USERNAME -m $USERNAME \
&& echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
&& chmod 0440 /etc/sudoers.d/$USERNAME \
&& mkdir -p /cd3user/tenancies && sudo chown -R $USERNAME:$USERNAME /cd3user/tenancies/ \
&& yum install -y vim && echo 'alias vi="vim"' >> /etc/bashrc


USER $USERNAME
WORKDIR /cd3user/oci_tools/
COPY cd3_automation_toolkit cd3_automation_toolkit/

WORKDIR /cd3user/

RUN sudo yum install -y oracle-softwarecollection-release-el7 \
&& sudo chown -R $USERNAME:$USERNAME /cd3user/

RUN sudo sed -i -e 's/\r$//' /cd3user/oci_tools/cd3_automation_toolkit/shell_script.sh \
&& bash /cd3user/oci_tools/cd3_automation_toolkit/shell_script.sh \
&& sudo chown -R cd3user:cd3user /cd3user/ && sudo yum clean all && sudo rm -rf /var/cache/yum \
&& sudo chmod -R 740 /cd3user/


##################################### START INSTALLING JENKINS ###################################
ARG JENKINS_VERSION=2.401.1
ARG JENKINS_SHA=600b73eabf797852e39919541b84f7686ff601b97c77b44eb00843eb91c7dd6c
ARG JENKINS_PLUGIN_MANAGER_VERSION=2.12.13
ARG PLUGIN_CLI_URL=https://github.com/jenkinsci/plugin-installation-manager-tool/releases/download/${JENKINS_PLUGIN_MANAGER_VERSION}/jenkins-plugin-manager-${JENKINS_PLUGIN_MANAGER_VERSION}.jar

ARG JENKINS_HOME=/cd3user/tenancies/jenkins_home
ARG JENKINS_INSTALL=/usr/share/jenkins
ARG REF=/usr/share/jenkins/ref

RUN sudo yum remove java-1.8.0-openjdk-1.8.0.345.b01-1.el7_9.x86_64 \
&& sudo yum install -y java-11-openjdk  \
&& sudo yum install -y java-11-openjdk-devel \
&& sudo yum install unzip -y \
&& sudo yum install git -y \
&& sudo mkdir -p ${REF}/init.groovy.d \
&& sudo chown -R cd3user:cd3user ${JENKINS_INSTALL} \
&& sudo curl -fsSL http://updates.jenkins-ci.org/download/war/${JENKINS_VERSION}/jenkins.war -o ${JENKINS_INSTALL}/jenkins.war \
&& echo "${JENKINS_SHA}  ${JENKINS_INSTALL}/jenkins.war" | sha256sum -c - \
&& sudo curl -fsSL ${PLUGIN_CLI_URL} -o ${JENKINS_INSTALL}/jenkins-plugin-manager.jar

ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-11.0.17.0.8-2.el8_6.x86_64
ENV JENKINS_HOME ${JENKINS_HOME}
ENV JENKINS_INSTALL ${JENKINS_INSTALL}
ENV REF ${REF}
ENV JENKINS_UC https://updates.jenkins.io
ENV JENKINS_UC_EXPERIMENTAL=https://updates.jenkins.io/experimental
ENV JENKINS_INCREMENTALS_REPO_MIRROR=https://repo.jenkins-ci.org/incrementals
ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false"
ENV COPY_REFERENCE_FILE_LOG ${JENKINS_HOME}/copy_reference_file.log
ENV CASC_JENKINS_CONFIG ${JENKINS_HOME}/jcasc.yaml

COPY --chown=cd3user:cd3user jenkins_install ${JENKINS_INSTALL}/
COPY --chown=cd3user:cd3user jenkins_install/init/*.groovy ${REF}/init.groovy.d/
COPY --chown=cd3user:cd3user jenkins_install/plugins.txt ${REF}/plugins.txt


RUN sudo java -jar ${JENKINS_INSTALL}/jenkins-plugin-manager.jar --war ${JENKINS_INSTALL}/jenkins.war --verbose -f ${REF}/plugins.txt \
&& sudo chown -R cd3user:cd3user ${JENKINS_INSTALL} \
&& sudo chmod +x ${JENKINS_INSTALL}/jenkins.sh
