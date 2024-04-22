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
                    def fileContent = readFile "${JENKINS_HOME}/jenkins.properties"
                    // Split file content into lines
                    def lines = fileContent.readLines()

                    // Process each line to extract variable name and value
                    def variables = [:]
                    lines.each { line ->
                        def parts = line.split('=')
                        if (parts.size() == 2) {
                            variables[parts[0].trim()] = parts[1].trim()
                        }
                    }

                    def variableOds = variables['outdir_structure'].toString().replaceAll("\\[|\\]", '').replaceAll('"', '')
                    env.out_str = "${variableOds}"
                }
            }
        }

        stage('Terraform Destroy Plan') {
            when {
                expression { return env.GIT_BRANCH == 'origin/develop';}
            }

            steps {
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                    script {
                        def jobName = env.JOB_NAME
                        def parts = jobName.split('/')

                        if (env.out_str == 'Multiple_Outdir') {
                            // Assuming the job name format is <region_name>/job/<service_name>/job/job_name
                            def regionName = parts[1]
                            def serviceName = parts[2]

                            // Set environment variables for reuse in subsequent stages
                            env.Region = regionName
                            env.Service = serviceName

                            } else {
                            // Assuming job name format is <region_name>/job/job_name
                            def regionName = parts[1]
                            def serviceName = ''
                            if (regionName == 'global') {
                                serviceName = 'rpc'
                            }
                            // Set environment variables for reuse
                            env.Region = regionName
                            env.Service = serviceName

                            }
                        sh "cd \"${WORKSPACE}/${env.Region}\" && terraform init -upgrade"
                        // Run Terraform plan
                        terraformPlanOutput = sh(script: "cd \"${WORKSPACE}/${env.Region}\" && terraform plan -destroy", returnStdout: true).trim()

                        // Check if the plan contains any changes
                        if (terraformPlanOutput.contains('No changes.')) {
                            echo 'No changes in Terraform plan. Skipping further stages.'
                            tf_plan = "No Changes"
                        } else {
                            // If there are changes, proceed with applying the plan
                            echo "Proceeding with destroy. \n${terraformPlanOutput}"
                        }
                    }
                }
            }
        }

        /** Approval for Terraform Apply **/
        stage('Get Approval') {
            when {
                allOf {
                    expression {return env.GIT_BRANCH == 'origin/develop'; }
                    expression {return tf_plan == "Changes" }
                    expression {return currentBuild.result != "FAILURE" }
                }
            }
            input {
                message "Do you want to perform terraform destroy?"
            }
            steps {
                echo "Approval for the Destroy Granted!"
            }
        }

        stage('Terraform Destroy') {
            when {
                allOf {
                    expression {return env.GIT_BRANCH == 'origin/develop'; }
                    expression {return tf_plan == "Changes" }
                    expression {return currentBuild.result != "FAILURE" }
                }
            }

            steps {
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                    script {
                        if (env.out_str == 'Multiple_Outdir') {
                            sh "cd \"${WORKSPACE}/${env.Region}/${env.Service}\" && terraform destroy --auto-approve"
                        } else {
                            sh "cd \"${WORKSPACE}/${env.Region}\" && terraform destroy --auto-approve"
                        }
                    }
                }
            }
        }

        /** Main branch commit to keep changes in Sync  **/
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
                        if (env.out_str == 'Multiple_Outdir') {
                            def buildDir = "${WORKSPACE}/${BUILD_NUMBER}"
                            // Create directory with build number
                            sh "mkdir -p ${buildDir}"

                            // Commit changes to the main branch
                            dir(buildDir) {
                                sh """
                                    git clone ${GIT_URL}
                                    cd \$(ls -d */|head -n 1)
                                    git checkout main
                                    ls -lrtha
                                    cd "${env.Region}/${env.Service}"
                                    git pull --no-edit origin main
                                    rm -f *.tfvars
                                    git rm *.tfvars
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
                                        git commit -m "commit for terraform-destroy build - ${BUILD_NUMBER} for "${env.Region}"/"${env.Service}

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
                        } else {
                            def buildDir = "${WORKSPACE}/${BUILD_NUMBER}"
                            // Create a directory with the build number
                            sh "mkdir -p ${buildDir}"

                            // Commit the changes to the main branch
                            dir(buildDir) {
                                sh """
                                    git clone ${GIT_URL}
                                    cd \$(ls -d */|head -n 1)
                                    git checkout main
                                    cd "${env.Region}"
                                    git pull --no-edit origin main
                                    rm -f *.tfvars
                                    git rm *.tfvars
                                    git status
                                    git add --all .
                                """

                                def git_status = false
                                while (!git_status) {
                                    // Execute the git commands using shell
                                    def gitResult = sh(script: """
                                        cd "\$(ls -d */|head -n 1)"
                                        cd "${env.Region}"
                                        ls -lrtha
                                        git fetch origin main
                                        git merge origin/main
                                        git commit -m "commit for terraform-destroy build - ${BUILD_NUMBER} for "${env.Region}

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
