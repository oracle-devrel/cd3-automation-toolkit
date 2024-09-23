import jenkins.model.Jenkins
import hudson.model.ListView
import hudson.model.ViewGroup
import com.cloudbees.hudson.plugins.folder.Folder

// Function to create views for each region within profile directories
def createRegionViews() {
    def jenkinsInstance = Jenkins.getInstance()
    if (jenkinsInstance == null) {
        println("Jenkins instance not available.")
        return
    }

    // Read the properties file
    def JENKINS_HOME = System.getenv("JENKINS_HOME")
    File file = new File("$JENKINS_HOME/jenkins.properties")

    // Parse the properties file into profiles
    def profiles = [:]
    def currentProfile = ""
    file.eachLine { line ->
        if (line.startsWith('[')) {
            currentProfile = line.replace('[', '').replace(']', '').trim()
            profiles[currentProfile] = [:]
        } else if (line.contains('=')) {
            def parts = line.split('=')
            profiles[currentProfile][parts[0].trim()] = Eval.me(parts[1].trim())
        }
    }

    // Create views for each profile
    profiles.each { profileName, profile ->
        def profileFolder = jenkinsInstance.getItem(profileName)
        if (profileFolder != null && profileFolder instanceof ViewGroup) {
            profile.regions.each { region ->
                def viewName = region
                def view = profileFolder.getView(viewName)

                if (view == null) {
                    // println("Creating view: $viewName in profile: $profileName")
                    def newView = new ListView(viewName)
                    profileFolder.addView(newView)
                    newView.save()
                    // println("View '$viewName' created successfully in profile '$profileName'.")
                    view = newView
                }

                // Clear the view to remove any existing jobs
                view.items.clear()

                // Navigate through the structure to find jobs
                def terraformFilesFolder = profileFolder.getItem('terraform_files')
                if (terraformFilesFolder instanceof ViewGroup) {
                    def regionFolder = terraformFilesFolder.getItem(region)
                    if (regionFolder instanceof ViewGroup) {
                        regionFolder.items.each { serviceFolder ->
                            if (serviceFolder instanceof ViewGroup) {
                                addJobsToView(view, serviceFolder)
                            }
                        }
                    }
                }

                // Set the "Recurse in folders" option
                view.setRecurse(true)

                // Save the view configuration
                view.save()
            }
        } else {
            println("Profile folder not found: $profileName")
        }
    }
}

// Function to add jobs to view
def addJobsToView(ListView view, ViewGroup folder) {
    folder.items.each { item ->
        if (item instanceof hudson.model.Job) {
            view.add(item)
        } else if (item instanceof ViewGroup) {
            // Recursively add jobs from sub-folders
            addJobsToView(view, item)
        }
    }
}

// Function to create region views
createRegionViews()