import jenkins.model.Jenkins

def createRegionViews() {
    def jenkinsInstance = Jenkins.getInstance()
    if (jenkinsInstance == null) {
        println("Jenkins instance not available.")
        return
    }

    def parentPath = "terraform_files"
    def parent = jenkinsInstance.getItemByFullName(parentPath)

    if (parent != null && parent instanceof hudson.model.ViewGroup) {
        parent.items.each { regionFolder ->
            def viewName = regionFolder.name
            def view = jenkinsInstance.getView(viewName)

            if (view == null) {
                view = new hudson.model.ListView(viewName, jenkinsInstance)
                jenkinsInstance.addView(view)
            }

            // Clear the view to remove any existing jobs
            view.items.clear()

            // Add jobs to the view
            addJobsToView(view, regionFolder)

            // Set the "Recurse in folders" option
            view.setRecurse(true)

            // Save the view configuration
            view.save()

            println("View '$viewName' created successfully.")
        }
    } else {
        println("Parent folder not found: $parentPath")
    }
}

def addJobsToView(hudson.model.ListView view, hudson.model.ViewGroup folder) {
    folder.items.each { item ->
        if (item instanceof hudson.model.Job) {
            view.add(item)
        } else if (item instanceof hudson.model.ViewGroup) {
            // Recursively add jobs from sub-folders
            addJobsToView(view, item)
        }
    }
}

// function to create region views
createRegionViews()