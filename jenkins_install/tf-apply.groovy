def tf_plan = "Changes"

pipeline {
    agent any
    options {
        ansiColor('xterm')
    }
    stages {
        stage('Read Jenkins Properties File and Set Environment Variables') {
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

        stage('Terraform Plan') {
            when {
                expression {
                    return env.GIT_BRANCH == 'origin/develop';
                }
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

                            sh "cd \"${WORKSPACE}/${env.Region}/${env.Service}\" && terraform init -upgrade"

                            // Run Terraform plan and capture the output
                            terraformPlanOutput = sh(script: "cd \"${WORKSPACE}/${env.Region}/${env.Service}\" && terraform plan -out=tfplan.out", returnStdout: true).trim()
                        } else {
                            // Assuming the job name format is <region_name>/job/job_name
                            def regionName = parts[1]

                            // Set environment variables for reuse in subsequent stages
                            env.Region = regionName
                            sh "cd \"${WORKSPACE}/${env.Region}\" && terraform init -upgrade"

                            // Run Terraform plan and capture the output
                            terraformPlanOutput = sh(script: "cd \"${WORKSPACE}/${env.Region}\" && terraform plan -out=tfplan.out", returnStdout: true).trim()
                        }

                        // Check if the plan contains any changes
                        if (terraformPlanOutput.contains('No changes.')) {
                            echo 'No changes in Terraform plan. Skipping further stages.'
                            tf_plan = "No Changes"
                        } else {
                            // If there are changes, proceed with applying the plan
                            echo "Changes detected in Terraform plan. Proceeding with apply. \n${terraformPlanOutput}"
                        }
                    }
                }
            }
        }

        // OPA Stage
        stage('OPA') {
            when {
                allOf{
                    expression { return env.GIT_BRANCH == 'origin/develop' }
                    expression { return tf_plan == "Changes" }
                    expression { return currentBuild.result != "ABORTED" }
                    expression { return currentBuild.result != "FAILURE" }
                }
            }

            steps {
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                    script {
                        if (env.out_str == 'Multiple_Outdir') {
                            // Run Terraform show and capture the output
                            sh "set +x && cd \"${WORKSPACE}/${env.Region}/${env.Service}\" && terraform show -json tfplan.out > tfplan.json"
                            // Run OPA eval
                            opaOutput = sh(script: "opa eval -f pretty -b /cd3user/oci_tools/cd3_automation_toolkit/user-scripts/OPA/ -i \"${WORKSPACE}/${env.Region}/${env.Service}/tfplan.json\" data.terraform.deny", returnStdout: true).trim()
                        } else {
                            // Run Terraform show and capture the output
                            sh "set +x && cd \"${WORKSPACE}/${env.Region}\" && terraform show -json tfplan.out > tfplan.json"
                            // Run OPA eval
                            opaOutput = sh(script: "opa eval -f pretty -b /cd3user/oci_tools/cd3_automation_toolkit/user-scripts/OPA/ -i \"${WORKSPACE}/${env.Region}/tfplan.json\" data.terraform.deny", returnStdout: true).trim()
                        }

                        if (opaOutput == '[]') {
                            echo "No OPA rules are violated. Proceeding with the next stage."
                        } else {
                            echo "OPA Output:\n${opaOutput}"
                            unstable(message: "OPA Rules are violated.")
                        }
                    }
                }
            }
        }

        // Get Approval
        stage('Get Approval') {
            when {
                allOf{
                    expression { return env.GIT_BRANCH == 'origin/develop' }
                    expression { return tf_plan == "Changes" }
                    expression { return currentBuild.result != "ABORTED" }
                    expression { return currentBuild.result != "FAILURE" }
                }
            }

            options {
                timeout(time: 1440, unit: 'MINUTES') // 24 hours timeout
            }

            steps {
                script {
                    input message: "Do you want to apply the plan?"
                    echo "Approval for the Apply Granted!"
                }
            }
        }

        // Terraform Apply
        stage('Terraform Apply') {
            when {
                allOf{
                    expression { return env.GIT_BRANCH == 'origin/develop' }
                    expression { return tf_plan == "Changes" }
                    expression { return currentBuild.result != "ABORTED" }
                    expression { return currentBuild.result != "FAILURE" }
                }
            }

            steps {
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                    script {
                        if (env.out_str == 'Multiple_Outdir') {
                            sh "cd \"${WORKSPACE}/${env.Region}/${env.Service}\" && terraform apply --auto-approve tfplan.out"
                        } else {
                            sh "cd \"${WORKSPACE}/${env.Region}\" && terraform apply --auto-approve tfplan.out"
                        }
                    }
                }
            }
        }

        // Git Commit to main
        stage('Git Commit to main') {
            when {
                allOf{
                    expression { return currentBuild.result != "ABORTED" }
                    expression { return currentBuild.result != "FAILURE" }
                }
            }

            steps {
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                    script {
                        if (env.out_str == 'Multiple_Outdir') {
                            try {
                                sh '''
                                    set +x
                                    mkdir -p ${WORKSPACE}/../${BUILD_NUMBER}
                                    cd ${WORKSPACE}/../${BUILD_NUMBER}
                                    git clone ${GIT_URL}
                                    repo_name=${GIT_URL##*/}
                                    cd ${WORKSPACE}/../${BUILD_NUMBER}/${repo_name}
                                    git checkout main
                                    reg=`echo ${JOB_NAME}| cut -d "/" -f2`
                                    service=`echo ${JOB_NAME}| cut -d "/" -f3`
                                    copy_path=${reg}/${service}
                                    cp -r ${WORKSPACE}/${copy_path}/* ${copy_path}/
                                    git add ${copy_path}*
                                '''
                            } catch(Exception e1) {
                                println(e1)
                                sh '''
                                    set +x
                                    rm -rf ${WORKSPACE}/../${BUILD_NUMBER}
                                    exit 1
                                '''
                            }
                            sh '''
                                set +x
                                repo_name=${GIT_URL##*/}
                                reg=`echo ${JOB_NAME}| cut -d "/" -f2`
                                service=`echo ${JOB_NAME}| cut -d "/" -f3`
                                cd ${WORKSPACE}/../${BUILD_NUMBER}/${repo_name}
                                git_status=`git status --porcelain`
                                if [[ $git_status ]]; then
                                    git commit -m "commit for terraform-apply build - ${BUILD_NUMBER} for "${reg}"/"${service}
                                else
                                    echo "Nothing to commit"
                                fi
                            '''
                        } else {
                            try {
                                sh '''
                                    mkdir -p ${WORKSPACE}/../${BUILD_NUMBER}
                                    cd ${WORKSPACE}/../${BUILD_NUMBER}
                                    git clone ${GIT_URL}
                                    repo_name=${GIT_URL##*/}
                                    cd ${WORKSPACE}/../${BUILD_NUMBER}/${repo_name}
                                    git checkout main
                                    reg=`echo ${JOB_NAME}| cut -d "/" -f2`
                                    copy_path=${reg}
                                    cp -r ${WORKSPACE}/${copy_path}/* ${copy_path}/
                                    git add ${copy_path}*
                                '''
                            } catch(Exception e1) {
                                println(e1)
                                sh '''
                                    cd ${WORKSPACE}/..
                                    rm -rf ${WORKSPACE}/../${BUILD_NUMBER}
                                    exit 1
                                '''
                            }
                        }
                    }
                }
            }
        }
    }
}
