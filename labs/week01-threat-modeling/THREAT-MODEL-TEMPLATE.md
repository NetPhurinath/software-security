# Threat Model — <app name>
Ans. ForRest Warehouse

## 1. Data-flow diagram
(Insert your DFD image. Mark trust boundaries with dashed lines.)
![alt text](<ForRest warehouse DFD.png>)

## 2. Elements & trust boundaries
| Element | Type (process/store/entity/flow) | Trust boundary crossed? |
|---|---|---|
| Customer | external entity | yes(Untrusted zone → DMZ) |
| Supplier | external entity | yes(Untrusted zone → DMZ) |
| Web/API gateway | process | yes(DMZ → Trusted internal network) |
| Warehouse staff | external entity | no(remains in Trusted internal network)    |
| Order processing | process | |
| Inventory mgmt | process | |
| Orders database | data store | |
| Stock database | data store | |

## 3. STRIDE analysis
| Element | S | T | R | I | D | E |
| Spoofing | Tampering | Repudiation | Information disclosure | Denial of service |
Elevation of privilege |
| /notes | Attacker forging session cookies to post notes as another user | 
SQL Injection allowing an attacker to modify database entries | x | x | x | x |
| /upload | x | x | x | x | Uploading massive files repeatedly to exhaust server memory | 
Uploading executable code to gain remote code execution on the server |
| /files/<name> | x | x | Lack of access logging allows a user to deny they downloaded a specific sensitive file | Path traversal attacks to read sensitive system files outside the uploads/ directory | x | x |

## 4. Top 5 risks (likelihood × impact) + mitigation
1. Unrestricted File Upload leading to Remote Code Execution (High x Critical)
+ Enforce strict allow-lists for file extensions and disable execution permissions on the upload folder
2. Path Traversal/Local File Inclusion (Medium x High)
+ Use framework-safe path handling(like Flask's send_from_directory)
3. SQL Injection (Medium x High)
+ Exclusively use parameterized queries, never concatenate user input directly into SQL strings
4. Stored Cross-Site Scripting(XSS) (High x Medium)
+ Implement strict output encoding when rendering notes in the UI
5. Resource Exhaustion(DoS) (High x Medium)
+ Set a strict maximum file size limit in the web server and application configuration