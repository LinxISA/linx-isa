# Access Control Ring (ACR)

Linx Instruction Set Architecture uses Access Control Ring (ACR) ([ACR](../exception/acr.md)) to control the function access permissions of the running software roles.

Each Linx logical core (LxLC) on the program order is always on a specific ACR at each specific moment. Software instances designed to always run on a certain ACR are considered by this standard to have the identity of that ACR.

Depending on the usage context, the name ACR can represent the name of the Access Control Ring (ACR) mechanism, or a privileged state (ring) running in the Linx logical core (LxLC), or a software instance running in this privileged state.

ACR determines how the Linx logic core (LxLC) responds to various requests. It can only be changed by specific events and can only change along a specific path.

This is specifically defined in the chapter [Access Control Ring (ACR)](../exception/acr.md).