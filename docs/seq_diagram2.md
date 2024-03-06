``` mermaid
stateDiagram-v2

  start: Launch CD3 Container
  Use: Use Toolkit
  RM: RM Stack
  Local: Local Environment
  connect: Connect Container to tenancy
  Create: Create, Manage or Export Resources in OCI
   state if_state <<choice>>
    RM --> connect
    Local --> connect
    connect --> Use
    Use --> if_state
    if_state --> Jenkins
    if_state --> CLI
    Jenkins --> Create
    CLI --> Create
  
```