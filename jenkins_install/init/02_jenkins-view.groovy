		import jenkins.model.Jenkins

		def parentPath = "terraform_files"
		def jenkinsInstance = Jenkins.getInstance()

		def findRegionFolders(jenkinsInstance, parentPath) {
		    def parent = jenkinsInstance.getItemByFullName(parentPath)

		    if (parent != null && parent instanceof hudson.model.ViewGroup) {
		        return parent.items.findAll { it instanceof hudson.model.ViewGroup }
		    } else {
		        println("Parent folder not found: $parentPath")
		        return []
		    }
		}

		def addJobsToView(view, folder) {
		    folder.items.each { item ->
		        if (item instanceof hudson.model.Job) {
		           // println("Processing job: ${item.fullName}")
		            view.add(item)
		        } else if (item instanceof hudson.model.ViewGroup) {
		            // Recursively add jobs from subfolders
		            addJobsToView(view, item)
		        }
		    }
		}

		def processRegionFolder(jenkinsInstance, regionFolder) {
		    def viewName = "${regionFolder.name}"
		    def view = jenkinsInstance.getView(viewName)

		    if (view == null) {
		        // Create the view if it doesn't exist
		        view = new hudson.model.ListView(viewName, jenkinsInstance)
		        jenkinsInstance.addView(view)
		    }

		    addJobsToView(view, regionFolder)

		    // Set the "Recurse in folders" option
		    view.setRecurse(true)

		    // Save the view configuration
		    view.save()

		    println("View '$viewName' created successfully.")
		}

		def regionFolders = findRegionFolders(jenkinsInstance, parentPath)
		regionFolders.each { regionFolder ->
		    processRegionFolder(jenkinsInstance, regionFolder)
		}

		println("Processing completed for all region folders.")
