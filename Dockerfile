FROM oraclelinux:9-slim
LABEL maintainer="Team at Oracle"
LABEL description="OCI format to generate CD3 image"

ARG USERNAME=cd3user
ARG USER_UID=1001
ARG USER_GID=$USER_UID

RUN microdnf install -y sudo && \
    groupadd --gid $USER_GID $USERNAME && \
    useradd --uid $USER_UID --gid $USER_GID -d /$USERNAME -m $USERNAME && \
    echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME && \
    chmod 0440 /etc/sudoers.d/$USERNAME && \
    mkdir -p /cd3user/tenancies && \
    chown -R $USERNAME:$USERNAME /cd3user/tenancies/ && \
    microdnf install -y vim && \
    microdnf install -y dnf && \
    echo 'alias vi="vim"' >> /etc/bashrc

USER $USERNAME
WORKDIR /cd3user/oci_tools/
COPY cd3_automation_toolkit cd3_automation_toolkit/

WORKDIR /cd3user/

RUN  sudo dnf install -y oraclelinux-release-el9 && \
sudo chown -R $USERNAME:$USERNAME /cd3user/ && \
sudo sed -i -e 's/\r$//' /cd3user/oci_tools/cd3_automation_toolkit/shell_script.sh && \
bash /cd3user/oci_tools/cd3_automation_toolkit/shell_script.sh && \
sudo chown -R cd3user:cd3user /cd3user/ && \
sudo dnf clean all && \
sudo rm -rf /var/cache/dnf && \
sudo chmod -R 740 /cd3user/


##################################### START INSTALLING JENKINS ###################################
ARG JENKINS_VERSION=2.444
ARG JENKINS_SHA=ab093a455fc35951c9b46361002e17cc3ed7c59b0943bbee3a57a363f3370d2e
ARG JENKINS_PLUGIN_MANAGER_VERSION=2.12.13
ARG PLUGIN_CLI_URL=https://github.com/jenkinsci/plugin-installation-manager-tool/releases/download/${JENKINS_PLUGIN_MANAGER_VERSION}/jenkins-plugin-manager-${JENKINS_PLUGIN_MANAGER_VERSION}.jar

ARG JENKINS_HOME=/cd3user/tenancies/jenkins_home
ARG JENKINS_INSTALL=/usr/share/jenkins
ARG REF=/usr/share/jenkins/ref

RUN sudo microdnf install -y java-21-openjdk && \
    sudo microdnf install -y java-21-openjdk-devel && \
    sudo microdnf install git-2.39.3 -y && \
    sudo mkdir -p ${REF}/init.groovy.d && \
    sudo chown -R cd3user:cd3user ${JENKINS_INSTALL} && \
    sudo curl -fsSL http://updates.jenkins-ci.org/download/war/${JENKINS_VERSION}/jenkins.war -o ${JENKINS_INSTALL}/jenkins.war && \
    echo "${JENKINS_SHA}  ${JENKINS_INSTALL}/jenkins.war" | sha256sum -c - && \
    sudo curl -fsSL ${PLUGIN_CLI_URL} -o ${JENKINS_INSTALL}/jenkins-plugin-manager.jar

ENV JAVA_HOME /usr/lib/jvm/java-21-openjdk
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

RUN sudo java -jar ${JENKINS_INSTALL}/jenkins-plugin-manager.jar --war ${JENKINS_INSTALL}/jenkins.war --verbose -f ${REF}/plugins.txt && \
    sudo chown -R cd3user:cd3user ${JENKINS_INSTALL} && \
    sudo chmod +x ${JENKINS_INSTALL}/jenkins.sh