/* Set the various stages of the build */
def tf_plan = "Changes"

pipeline {
    agent any
    options {
        ansiColor('xterm')
    }
    stages {
        stage('Set Environment Variables') {
            steps {
                script {
                    def jobName = env.JOB_NAME
                    def parts = "${env.JOB_NAME}".split('/')
                    env.Prefix = parts[0]

                    def propertiesFileContent = readFile "$JENKINS_HOME/jenkins.properties"
                    def result = [:]
                    def currentSection = null

                    propertiesFileContent.readLines().each { line ->
                        line = line.trim()
                        if (line.startsWith("#") || line.isEmpty()) {
                        // Ignore comments and empty lines
                        return
                        }

                    def sectionMatch = line =~ /^\[(.+)\]$/
                    if (sectionMatch) {
                        currentSection = sectionMatch[0][1]
                        result[currentSection] = [:]
                        } else if (currentSection) {
                        def kvMatch = line =~ /^([^=]+)=\s*(.+)$/
                        if (kvMatch) {
                            def key = kvMatch[0][1].trim()
                            def value = kvMatch[0][2].trim()
                            result[currentSection][key] = value
                            }
                        }
                    }
                    def tfortofuValue = result["${env.Prefix}"]["tf_or_tofu"]
                    env.tf_or_tofu = Eval.me(tfortofuValue)
                    def out_str = result["${env.Prefix}"]["outdir_structure"]
                    env.out_str = Eval.me(out_str)
                    if (env.out_str == 'Multiple_Outdir') {
                        // Assuming the job name format is <region_name>/job/<service_name>/job/job_name
                        env.Region = parts[2]
                        env.Service = parts[3]
                    } else {
                        // Assuming the job name format is <region_name>/job/job_name
                        env.Region = parts[2]
                        env.Service = ''
                        if (env.Region == 'global') {
                            env.Service = 'rpc'
                        }
                    }
                }
            }
        }

        //Terraform/Tofu Destroy Plan
        stage('Destroy Plan') {
            when {
                expression { return env.GIT_BRANCH == 'origin/develop'; }
            }

            steps {
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                    script {
                        def toolCmd = env.tf_or_tofu == 'terraform' ? 'terraform' : 'tofu'
                        sh "cd \"${WORKSPACE}/${env.Region}/${env.Service}\" && ${toolCmd} init -upgrade"
                        // Run destroy plan
                        destroyPlanOutput = sh(script: "cd \"${WORKSPACE}/${env.Region}/${env.Service}\" && ${toolCmd} plan -destroy", returnStdout: true).trim()

                        // Check if the plan contains any changes
                        if (destroyPlanOutput.contains('No changes.')) {
                            echo 'No changes in destroy plan. Skipping further stages.'
                            tf_plan = "No Changes"
                        } else {
                            echo "Proceeding with destroy. \n${destroyPlanOutput}"
                        }
                    }
                }
            }
        }

        /** Approval for Destroy **/
        stage('Get Approval') {
            when {
                allOf {
                    expression { return env.GIT_BRANCH == 'origin/develop'; }
                    expression { return tf_plan == "Changes" }
                    expression { return currentBuild.result != "FAILURE" }
                }
            }
            input {
                message "Do you want to perform destroy?"
            }
            steps {
                echo "Approval for the Destroy Granted!"
            }
        }

        // Terraforn/Tofu Destroy
        stage('Destroy') {
            when {
                allOf {
                    expression { return env.GIT_BRANCH == 'origin/develop'; }
                    expression { return tf_plan == "Changes" }
                    expression { return currentBuild.result != "FAILURE" }
                }
            }

            steps {
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                    script {
                        def toolCmd = env.tf_or_tofu == 'terraform' ? 'terraform' : 'tofu'
                        sh "cd \"${WORKSPACE}/${env.Region}/${env.Service}\" && ${toolCmd} destroy --auto-approve"
                    }
                }
            }
        }

        /** Main branch commit to keep changes in Sync **/
        stage('Commit To Main') {
            when {
                allOf {
                    expression { return env.GIT_BRANCH == 'origin/develop'; }
                    expression { return tf_plan == "Changes" }
                    expression { return currentBuild.result != "FAILURE" }
                }
            }
            steps {
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                    script {
                        def buildDir = "${WORKSPACE}/${BUILD_NUMBER}"
                        // Create directory with build number
                        sh "mkdir -p ${buildDir}"
                        // Commit changes to the main branch
                        dir(buildDir) {
                            sh """
                                git clone ${GIT_URL}
                                cd \$(ls -d */|head -n 1)
                                git checkout main
                                cd "${env.Region}/${env.Service}"
                                git pull --no-edit origin main
                                rm -f *.tfvars
                                git status
                                git add --all .
                            """

                            def git_status = false
                            while (!git_status) {
                                // Execute the git commands using shell
                                def gitResult = sh(script: """
                                    cd "\$(ls -d */|head -n 1)"
                                    cd "${env.Region}/${env.Service}"
                                    git fetch origin main
                                    git merge origin/main
                                    git commit -m "commit for destroy build - ${BUILD_NUMBER} for ${env.Region}/${env.Service}"
                                    git push --porcelain origin main
                                """, returnStatus: true)

                                if (gitResult == 0) {
                                    git_status = true
                                } else {
                                    echo "Git operation failed, retrying...."
                                    sleep 3  // 3 seconds before retrying
                                }
                            }
                        }
                    }
                }
            }

            post {
                always {
                    // Delete the build directory and the temporary directory
                    deleteDir()
                }
            }
        }
    }
}
