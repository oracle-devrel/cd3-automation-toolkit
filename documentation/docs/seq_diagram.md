``` mermaid
stateDiagram-v2
  
  classDef custom fill:#f00,color:white,font-weight:bold,stroke-width:2px,stroke:teal

  start: Launch CD3 Container
  RM: RM Stack
  Local: Local Desktop
  connect: Connect Container to tenancy
  
    state if_state <<choice>>
    start --> if_state
    if_state --> RM
    if_state --> Local 
    RM --> connect
    Local --> connect
    
```

[Launch with Resource Manager Stack](singleclickdeploy.md){ .md-button } [Launch with Local Desktop](Launch_Docker_container.md){ .md-button }