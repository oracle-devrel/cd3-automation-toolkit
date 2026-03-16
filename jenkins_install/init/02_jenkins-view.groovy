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

    if (!file.exists()) {
        println("Properties file not found at $JENKINS_HOME/jenkins.properties")
        return
    }

    // Parse the properties file into profiles
    def profiles = [:]
    def currentProfile = ""
    file.eachLine { line ->
        line = line.trim()
        if (line.startsWith('[') && line.endsWith(']')) {
            currentProfile = line.replace('[', '').replace(']', '').trim()
            profiles[currentProfile] = [:]
        } else if (line.contains('=') && currentProfile != "") {
            def parts = line.split('=', 2)
            def key = parts[0].trim()
            def value = parts[1].trim()

            // Custom parsing logic to safely handle lists without Eval.me
            if (value.startsWith("[") && value.endsWith("]")) {
                def content = value.substring(1, value.length() - 1)
                if (content.trim().isEmpty()) {
                     profiles[currentProfile][key] = []
                } else {
                     // Split by comma, trim whitespace and remove quotes
                     def list = content.split(',').collect { it.trim().replaceAll(/^['"]|['"]$/, "") }
                     profiles[currentProfile][key] = list
                }
            } else {
                 // Try Eval.me for other types, fallback to string
                 try {
                     profiles[currentProfile][key] = Eval.me(value)
                 } catch (Exception e) {
                     profiles[currentProfile][key] = value
                 }
            }
        }
    }

    // Create views for each profile
    profiles.each { profileName, profile ->
        def profileFolder = jenkinsInstance.getItem(profileName)
        if (profileFolder != null && profileFolder instanceof ViewGroup) {

            def regions = profile.regions

            // SAFETY CHECK: Ensure regions is always a List
            // This prevents iterating over a String (which causes the 'l', 'o', 'n' views)
            if (regions == null) {
                regions = []
            } else if (regions instanceof String) {
                regions = [regions]
            }

            // Iterate only if it is a list
            if (regions instanceof List) {
                regions.each { region ->
                    // Cleanup name
                    region = region.toString().trim()
                    if (region.isEmpty()) return

                    def viewName = region
                    def view = profileFolder.getView(viewName)

                    if (view == null) {
                        def newView = new ListView(viewName)
                        profileFolder.addView(newView)
                        newView.save()
                        view = newView
                    }

                    // Clear the view to remove any existing jobs
                    view.items.clear()

                    // Navigate through the structure to find jobs
                    def terraformFilesFolder = profileFolder.getItem('terraform_files')
                    if (terraformFilesFolder instanceof ViewGroup) {
                        def regionFolder = terraformFilesFolder.getItem(region)
                        if (regionFolder instanceof ViewGroup) {
                            addJobsToView(view, regionFolder)
                        }
                    }

                    // Set the "Recurse in folders" option
                    view.setRecurse(true)

                    // Save the view configuration
                    view.save()
                }
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