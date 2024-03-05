Follow the steps to set up the CD3 Automation Toolkit.

``` mermaid
stateDiagram-v2
  
  classDef custom fill:#f00,color:white,font-weight:bold,stroke-width:2px,stroke:teal

  start:   Launch CD3 Container
  connect: Connect CD3 Container to OCI
  
    
    start --> connect
    
```