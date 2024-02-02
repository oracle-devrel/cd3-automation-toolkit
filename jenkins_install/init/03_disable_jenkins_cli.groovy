
// Disable CLI access over HTTP
def removal = { lst ->
  lst.each { x -> if (x.getClass().name?.contains("CLIAction")) lst.remove(x) }
  }
  def j = jenkins.model.Jenkins.get();
  removal(j.getExtensionList(hudson.cli.CLIAction.class))
  removal(j.getExtensionList(hudson.ExtensionPoint.class))
  removal(j.getExtensionList(hudson.model.Action.class))
  removal(j.getExtensionList(hudson.model.ModelObject.class))
  removal(j.getExtensionList(hudson.model.RootAction.class))
  removal(j.getExtensionList(hudson.model.UnprotectedRootAction.class))
  removal(j.getExtensionList(java.lang.Object.class))
  removal(j.getExtensionList(org.kohsuke.stapler.StaplerProxy.class))
  removal(j.actions)

  println "Jenkins cli is disabled..."
