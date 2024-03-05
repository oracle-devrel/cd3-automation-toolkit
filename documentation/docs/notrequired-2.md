
``` mermaid
stateDiagram-v2
  
  classDef custom fill:#f00,color:white,font-weight:bold,stroke-width:2px,stroke:teal

  start: Launch CD3 Container
  Use: Use Toolkit
  RM: RM Stack
  Local: Local Environment
  connect: Connect Container to tenancy
  Create: Create, Manage or Export Resources in OCI
  
    start --> RM: Option 1
    start --> Local: Option 2
  
  
    RM --> connect
    Local --> connect
    connect --> Use
    Use --> Jenkins: Option 1
    Use --> CLI: Option 2
    Jenkins --> Create
    CLI --> Create
  
```