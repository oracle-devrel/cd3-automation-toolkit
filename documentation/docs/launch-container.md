<center>
``` mermaid
flowchart TD
    A{Launch 
    CD3 Container}
    A ---> B[RM Stack]
    A ---> C[Local Desktop]
    B ---> D[Connect Container to tenancy]
    C ---> D

    
```
</center>

[Launch with Resource Manager Stack](launch-from-rmstack.md){ .md-button } [Launch with Local Desktop](launch-from-local.md){ .md-button }