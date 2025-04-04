def buildstatus = ""
def git_status = 0
def prefix = "${env.JOB_NAME}".split('/')[0]
def exportNetworkRules(stage_name) {
    return {
        stage("${stage_name}") {
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                labelledShell( label: 'Executing setUpOCI python script', script: """
                    cd /cd3user/oci_tools/cd3_automation_toolkit
                    python setUpOCI.py --devops True --main_options "Network" --sub_options "Security Rules,Route Rules,DRG Route Rules" --sub_child_options "Export Security Rules (From OCI into SecRulesinOCI sheet),Add/Modify/Delete Security Rules (Reads SecRulesinOCI sheet),Export Route Rules (From OCI into RouteRulesinOCI sheet),Add/Modify/Delete Route Rules (Reads RouteRulesinOCI sheet),Export DRG Route Rules (From OCI into DRGRouteRulesinOCI sheet),Add/Modify/Delete DRG Route Rules (Reads DRGRouteRulesinOCI sheet)" --add_filter "comp_filter=,[],@," ${env.prop_file}
                """)
                script {
                    git_status = labelledShell( label: 'Check git status', script: 'cd ${prefix_dir}/terraform_files; git status --porcelain | wc -l', returnStdout: true).trim()
                    // Check if anything to commit
                    if ("${git_status}" > 0) {
                        labelledShell( label: 'Performing git commit to develop', script: '''
                            set +x
                            cd ${prefix_dir}/terraform_files
                            echo "-----start timestamp-----"
                            time_stamp="$(date +%m-%d-%Y-%H-%M-%S)"
                            commit_msg="commit for setUpOCI build ${BUILD_NUMBER}"
                            git add -A .
                            git commit -m "${commit_msg}"
                            git push origin develop
                         ''')
                    }else {
                        echo 'Nothing to commit. Skipping further stages.'
                    }
                }

                file_path = sh(script: "set +x; grep '^cd3file' ${env.prop_file}| cut -d'=' -f2", returnStdout: true).trim()
                file_name = sh(script:"set +x; echo '${file_path}'| rev|cut -d '/' -f1 | rev", returnStdout: true).trim()
                sh """
                set +x
                cp '${file_path}' '${WORKSPACE}/${file_name}'
                """
                archiveArtifacts "${file_name}"

                }
        }
    }
}
def generateStage(job) {
    return {
        stage("Stage: ${job}") {
            def values = job.split('/')
            if (values.size() > 1) {
                region = values[0]
                service = values[1]
                job_name = "./terraform_files/${region}/${service}/apply".replace("//","/")
            }else {
                region = values[0]
                job_name = "./terraform_files/${region}/apply".replace("//","/")
            }
           //build job: "${job_name}"
            def job_exec_details = build job: "${job_name}", propagate: false, wait: true // Here wait: true means current running job will wait for build_job to finish.

            //println(job_exec_details.getResult())
            //println(job_exec_details.getFullProjectName())
            //println((job_exec_details.getFullProjectName()).split("/")[3])
            if (!["ABORTED","FAILURE"].contains(job_exec_details.getResult()) && ["apply","network"].contains((job_exec_details.getFullProjectName()).split("/")[3])) {
                if ( SubOptions.contains('Create Network') || SubOptions.contains('Modify Network') )  {
                    def stage_name = "Export Network Rules"
                    parallel([stage_name : exportNetworkRules(stage_name)])
                }

            }
      }
    }
}
properties([
    parameters([
        [
            $class: 'ChoiceParameter',
            choiceType: 'PT_RADIO',
            description: 'Select Automation Toolkit Workflow',
            name: 'Workflow',
            script: [
                $class: 'ScriptlerScript',
                scriptlerScriptId:'Workflow.groovy'
            ]
        ],
        [
            $class: 'CascadeChoiceParameter',
            choiceType: 'PT_CHECKBOX',
            description: 'Select Main Options',
            name: 'MainOptions',
            referencedParameters: 'Workflow',
            script: [
                $class: 'ScriptlerScript',
                scriptlerScriptId:'MainOptions.groovy',
                parameters: [
                    [name:'Workflow', value: '${Workflow}']
                ]
            ]
       ],
       [
            $class: 'CascadeChoiceParameter',
            choiceType: 'PT_CHECKBOX',
            description: 'Select Sub Options',
            name: 'SubOptions',
            referencedParameters: 'MainOptions',
            script: [
                $class: 'ScriptlerScript',
                scriptlerScriptId:'SubOptions.groovy',
                parameters: [
                    [name:'MainOptions', value: '${MainOptions}']
                ]
            ]
       ],
       [
            $class: 'CascadeChoiceParameter',
            choiceType: 'PT_CHECKBOX',
            description: 'Select Options for the SubOptions selected above',
            name: 'SubChildOptions',
            referencedParameters: 'SubOptions',
            script: [
                $class: 'ScriptlerScript',
                scriptlerScriptId:'SubChildOptions.groovy',
                parameters: [
                    [name:'SubOptions', value: '${SubOptions}']
                ]
            ]
       ],
       [
            $class: 'DynamicReferenceParameter',
            choiceType: 'ET_FORMATTED_HTML',
            description: 'Select additional filters',
            name: 'AdditionalFilters',
            referencedParameters: 'Workflow,SubOptions,SubChildOptions,MainOptions',
             script: [
                $class: 'ScriptlerScript',
                scriptlerScriptId: 'AdditionalFilters.groovy',
                parameters: [
                    [name:'MainOptions',value:'${MainOptions}'],
                    [name:'SubOptions', value: '${SubOptions}'],
                    [name:'SubChildOptions', value: '${SubChildOptions}'],
                    [name:'Workflow', value: '${Workflow}'],
                    [name:'Prefix', value: "${prefix}"]
                ]
            ]
       ]
    ])
])
pipeline {
    agent any
        options {
        ansiColor('xterm')
    }
    environment {
        prefix_dir = "/cd3user/tenancies/${prefix}"
        prefix = "${prefix}"
        prop_file = "${prefix_dir}/${prefix}_setUpOCI.properties"
        current_timestamp = sh (script: 'date +%s', returnStdout: true).trim()
    }
    parameters {
        stashedFile (
            name: 'Excel_Template',
            description: "Upload input Excel file.\nPreviously uploaded file will be used if left empty."
            )
    }
    stages {
		stage ('Validate Input Parameters') {
		    steps {
		        catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                withFileParameter('Excel_Template') {
                    unstash 'Excel_Template'
                    script {
                            exlfile_check = labelledShell( label: 'Validating excel sheet', script: '''
                                set +x
                                if [[ -n "$Excel_Template_FILENAME" ]];then
                                	size=$(wc --bytes < "$Excel_Template")
                                    if [[ ( $size -gt 1000000 ) || ( $Excel_Template_FILENAME != *.xlsx ) ]]; then
                                        set -x
                                        echo "Excel File validation failed because of size limit or extension not xlsx"
                                    fi
                                fi
                                ''' , returnStdout: true).trim()
                            if ("${exlfile_check}".contains("Failed")) {
                                mitem = "excel template"
                                file_check = "Failed"
                            } else {
                                file_check = "Passed"
                                }
                    }
                }
        		script {
        		    def ParametersValidationScript = load "$JENKINS_HOME/scriptler/scripts/ValidateParams.groovy"
                    (ParametersValidation, ParametersList) = ParametersValidationScript.validate_params(Workflow,MainOptions,SubOptions,SubChildOptions,AdditionalFilters)
                    if (ParametersValidation == "Passed" && file_check == "Passed") {
                        echo 'Parameter Validation Successful.'

            		}else {
            		    if (file_check == "Failed"){
            		        fail_message = "Excel file validation failed"
            		    }
            		    else{
            		        fail_message = "Parameters validation failed for ${ParametersList.toString()} "

            		    }
            		    unstable(message:"${fail_message}. Setting Build to Unstable")
                        ParametersValidation = "Failed"
                    }
    		    }
		    }
        	}
		}
        stage('Update setUpOCI.properties') {
			when{
			    allOf {
                expression {return ParametersValidation == "Passed" }
                expression {return currentBuild.result != "ABORTED" }
                expression {return currentBuild.result != "FAILURE" }
			    }

            }
			steps {
			    catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
			    withFileParameter('Excel_Template') {
                    unstash 'Excel_Template'
                labelledShell( label: 'Updating properties file', script: '''
                    set +x
                    if [ "$Excel_Template_FILENAME" ]; then
                        time_stamp="$(date +%m-%d-%Y-%H-%M-%S)"
                        cd3_file="${prefix_dir}/$Excel_Template_FILENAME"
                        cd3_backup="${cd3_file}_${time_stamp}"
                        if [ -e "$cd3_file" ]; then
                            cp "$cd3_file" "$cd3_backup"
                        fi
                        cp "$Excel_Template" "$cd3_file"
                        sed -i "s|cd3file=.*|cd3file=${cd3_file}|g" $prop_file
                    fi
                    if grep -q "Create" <<< "${Workflow}"; then
                        workflow="create_resources"
                    elif grep -q "Export" <<< "${Workflow}"; then
                        workflow="export_resources"
                    fi
                    if [ `grep '^workflow_type'  $prop_file` ] ; then
                        sed -i "s/^workflow_type=.*/workflow_type=${workflow}/g" $prop_file
                    else
                        echo "\nworkflow_type=${workflow}" >> $prop_file
                    fi
                ''')
			    }
            }
        }
        }
        stage('Execute setUpOCI') {
            when{
                allOf {
                expression {return ParametersValidation == "Passed" }
                expression {return currentBuild.result != "ABORTED" }
                expression {return currentBuild.result != "FAILURE" }
                }
            }

			steps {
			    catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                    labelledShell( label: 'Executing setUpOCI python script', script: '''
                        set +x
                        cd /cd3user/oci_tools/cd3_automation_toolkit
                        python setUpOCI.py --devops True --main_options "${MainOptions}" --sub_options "${SubOptions}" --sub_child_options "${SubChildOptions}" --add_filter "${AdditionalFilters}" $prop_file
                        cd -
                        rm -rf *.*
                        # Check for cis_reports, show_oci  and vizoci directories
                        if [ -d "${prefix_dir}/othertools_files/${prefix}_cis_report" ]; then
                            last_modified=`stat -c "%Y" ${prefix_dir}/othertools_files/${prefix}_cis_report`
                            if [ $(($last_modified-$current_timestamp)) -gt 0 ]; then
                                cp -r ${prefix_dir}/othertools_files/${prefix}_cis_report .
                                tar -cf ${prefix}_cis_report.zip ${prefix}_cis_report/
                                rm -rf ${prefix}_cis_report
                            fi
                        fi
                        if [ -d "${prefix_dir}/othertools_files/${prefix}_showoci_report" ]; then
                        last_modified=`stat -c "%Y" ${prefix_dir}/othertools_files/${prefix}_showoci_report`
                        if [ $(($last_modified-$current_timestamp)) -gt 0 ]; then
                            cp -r ${prefix_dir}/othertools_files/${prefix}_showoci_report .
                            tar -cf ${prefix}_showoci_report.zip ${prefix}_showoci_report/
                            rm -rf ${prefix}_showoci_report
                        fi
                        fi

                        if [ -d "${prefix_dir}/othertools_files/${prefix}_vizoci_report" ]; then
                        last_modified=`stat -c "%Y" ${prefix_dir}/othertools_files/${prefix}_vizoci_report`
                        if [ $(($last_modified-$current_timestamp)) -gt 0 ]; then
                            cp -r ${prefix_dir}/othertools_files/${prefix}_vizoci_report .
                            tar -cf ${prefix}_vizoci_report.zip ${prefix}_vizoci_report/
                            rm -rf ${prefix}_vizoci_report
                        fi
                        fi

                        # For latest oci_fsdr plan XL file.
                        count=`ls -1 ${prefix_dir}/othertools_files/*.xl* 2>/dev/null | wc -l`
                        if [ $count != 0 ]; then
                		latest_fsdr_XL=`ls -t ${prefix_dir}/othertools_files/*.xl* | head -n 1`
                		last_modified=`stat -c \"%Y\" ${latest_fsdr_XL}`
                		if [ $(($last_modified-$current_timestamp)) -gt 0 ]; then
                		    cp "${latest_fsdr_XL}" .
                		fi
                		fi
            		''')

                }
            }
            post {
                failure {

                    labelledShell( label: 'Preparing archival', script: '''
                        set +x
                        # For CD3 Validator Log File
                        if [ -e "${prefix_dir}/terraform_files/${prefix}_cd3Validator.log" ]; then
                            last_modified=`stat -c "%Y" ${prefix_dir}/terraform_files/${prefix}_cd3Validator.log`
                            if [ $(($last_modified-$current_timestamp)) -gt 0 ]; then
                                rm -f ${prefix}_cd3Validator.log
                                cp ${prefix_dir}/terraform_files/${prefix}_cd3Validator.log .
                            fi
                        fi
                    ''')

                    archiveArtifacts '*_cd3Validator.log'
                }
                always {
                    script{
                    //For latest CD3 XL file.
                    file_path = labelledShell( label: 'Preparing archival', script: '''
                        set +x
                        cd3_file=`grep '^cd3file' ${prop_file}| cut -d'=' -f2`
                        cp "$cd3_file" .
                        echo "$cd3_file"
                        ''', returnStdout: true).trim()
                    }
                    archiveArtifacts "${file_path.split("/")[(file_path.split("/")).length-1]}, *.zip,*.xl*"

                }
            }
        }
        stage ('Run Import Commands') {
            when {
				allOf {
				    expression {return "${Workflow}".toLowerCase().contains("export")}
				    expression {return ParametersValidation == "Passed" }
				    expression {return currentBuild.result != "ABORTED" }
                    expression {return currentBuild.result != "FAILURE" }

				}
            }
            steps {
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                script {
                    def data = readFile(file: "${prefix_dir}/terraform_files/.safe/import_scripts.safe")
                    def lines = data.readLines()
                    for (line in lines) {
                        script_full_path = (line.replace('//','/')).split("/")
                        script_name = script_full_path.last()
                        script_path = line.split("${script_name}")[0]
                        labelledShell( label: "Running ${script_name}", script: """
                        set +x
                        cd ${script_path}
                        sh ./${script_name}
                        """)
                    }
                }
            }
        }
        }
        stage ('GIT Commit to develop') {
            when{
                allOf {
                    expression {return ParametersValidation == "Passed" }
                    expression {return currentBuild.result != "ABORTED" }
                    expression {return currentBuild.result != "FAILURE" }
                }
            }
			steps {
			    catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                script {
                    git_status = labelledShell( label: 'Check git status', script: 'cd ${prefix_dir}/terraform_files; git status --porcelain | wc -l', returnStdout: true).trim()
                    // Check if anything to commit
                    if ("${git_status}" > 0) {
                        labelledShell( label: 'Performing git operations', script: '''
                            set +x
                            cd ${prefix_dir}/terraform_files
                            echo "-----start timestamp-----"
                            time_stamp="$(date +%m-%d-%Y-%H-%M-%S)"
                            commit_msg="commit for setUpOCI build ${BUILD_NUMBER}"
                            git add -A .
                            git commit -m "${commit_msg}"
                            git push origin develop
                         ''')
                    }else {
                        echo 'Nothing to commit. Skipping further stages.'
                    }
                }
            }
        }
        }
        stage ('Trigger Pipelines'){
            when {
			    allOf{
    				expression {return "${git_status}" > 0}
    				expression {return ParametersValidation == "Passed" }
    				expression {return currentBuild.result != "ABORTED" }
                    expression {return currentBuild.result != "FAILURE" }
			    }
			}
            steps {
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                script {
                    def jobs = []
                    def data = readFile(file: "${prefix_dir}/terraform_files/.safe/updated_paths.safe")
                    def lines = data.readLines()
                    if (lines.size() == 0) {
                        println("No terraform configuration file generated")
                    }
                    for (line in lines) {
                        line = line.split('terraform_files/')[1]
                        jobs.add(line)
                    }
                    parallelStagesMap = jobs.collectEntries {
                        ["${it}" : generateStage(it)]
                    }
                }
                script{
                    parallel parallelStagesMap
                }
            }
        }
        }
    }

}