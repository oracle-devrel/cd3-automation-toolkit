#! /bin/bash -e

: "${REF:="/usr/share/jenkins/x``"}"

# Check if JENKINS_HOME exists
if [ ! -d "$JENKINS_HOME" ]; then
    # If it doesn't exist, create it
    #mkdir -p "$JENKINS_HOME"
    #echo "Directory created: $JENKINS_HOME"
    echo "Jenkins should be configured only if Devops parameter is set during tenancy configuration for the toolkit"
    exit
fi

## Copy Required files to JENKINS_HOME
#cp ${JENKINS_INSTALL}/jcasc.yaml "$JENKINS_HOME/"
#if [ ! -d "$JENKINS_HOME/jobs/setUpOCI" ]; then
#  mkdir -p "$JENKINS_HOME/jobs/setUpOCI"
#fi
#cp ${JENKINS_INSTALL}/setUpOCI_config.xml "$JENKINS_HOME/jobs/setUpOCI/config.xml"
#cp -r ${JENKINS_INSTALL}/scriptler $JENKINS_HOME

cp ${JENKINS_INSTALL}/jcasc.yaml "$JENKINS_HOME/"
if [ ! -e "/cd3user/.ssh/config" ]; then
	ln -s /cd3user/tenancies/jenkins_home/git_config /cd3user/.ssh/config
fi

# Copy scriptler directory
cp -r "${JENKINS_INSTALL}/scriptler" "$JENKINS_HOME"
echo "Copied scriptler directory to $JENKINS_HOME" # Debug line

#Generate Self Signed Cert and Copy to JENKINS_HOME
keytool -genkey -keystore "$JENKINS_INSTALL/oci_toolkit.jks" -alias "automationtoolkit" -keyalg RSA -validity 60 -keysize 2048 -dname "CN=oci-automation, OU=toolkit, C=IN" -ext SAN=dns:automationtoolkit,ip:127.0.0.1 -storepass automationtoolkit && keytool -importkeystore -srckeystore "$JENKINS_INSTALL/oci_toolkit.jks" -srcstoretype JKS -deststoretype PKCS12 -destkeystore "$JENKINS_HOME/oci_toolkit.p12" -srcstorepass automationtoolkit -deststorepass automationtoolkit -noprompt

touch "${COPY_REFERENCE_FILE_LOG}" || { echo "Can not write to ${COPY_REFERENCE_FILE_LOG}. Wrong volume permissions?"; exit 1; }
echo "--- Copying files at $(date)" >> "$COPY_REFERENCE_FILE_LOG"
find "${REF}" \( -type f -o -type l \) -exec bash -c '. ${JENKINS_INSTALL}/jenkins-support; for arg; do copy_reference_file "$arg"; done' _ {} +


# if `docker run` first argument start with `--` the user is passing jenkins launcher arguments
if [[ $# -lt 1 ]] || [[ "$1" == "--"* ]]; then

  # read JAVA_OPTS and JENKINS_OPTS into arrays to avoid need for eval (and associated vulnerabilities)
  java_opts_array=()
  while IFS= read -r -d '' item; do
    java_opts_array+=( "$item" )
  done < <([[ $JAVA_OPTS ]] && xargs printf '%s\0' <<<"$JAVA_OPTS")

  readonly agent_port_property='jenkins.model.Jenkins.slaveAgentPort'
  if [ -n "${JENKINS_SLAVE_AGENT_PORT:-}" ] && [[ "${JAVA_OPTS:-}" != *"${agent_port_property}"* ]]; then
    java_opts_array+=( "-D${agent_port_property}=${JENKINS_SLAVE_AGENT_PORT}" )
  fi

  if [[ "$DEBUG" ]] ; then
    java_opts_array+=( \
      '-Xdebug' \
      '-Xrunjdwp:server=y,transport=dt_socket,address=5005,suspend=y' \
    )
  fi

  jenkins_opts_array=( )
  while IFS= read -r -d '' item; do
    jenkins_opts_array+=( "$item" )
  done < <([[ $JENKINS_OPTS ]] && xargs printf '%s\0' <<<"$JENKINS_OPTS")

  # Start Jenkins on 8443 port using Self Signed Cert
  exec java -Duser.home="$JENKINS_HOME" "${java_opts_array[@]}" -jar ${JENKINS_INSTALL}/jenkins.war "${jenkins_opts_array[@]}" "$@" --httpsPort=8443 --httpPort=-1 --httpsKeyStore="$JENKINS_INSTALL/oci_toolkit.jks" --httpsKeyStorePassword=automationtoolkit
fi

# As argument is not jenkins, assume user want to run his own process, for example a `bash` shell to explore this image
exec "$@"