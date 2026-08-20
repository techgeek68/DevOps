# Module 5: Web Servers, Applications, and Testing Strategy


>**Module objective.** Deploy web and application services and construct a delivery friendly reference application governed by a layered test suite.

---


## Contents


### 01. Notes/01. Section 5.1 Web and Application Servers
* 01. Web Servers vs. Application Servers
* 02. Process Models of the Two Dominant Web Servers
* 03. Virtual Hosts
* 04. Reverse Proxying
* 05. TLS Termination and Where to Terminate
* 06. Apache Tomcat (an Application Server)
* 07. Web Server Comparison
* images/ (8)

### 01. Notes/02. SELinux Reference for Web Servers
* 01. File Context
* 02. Booleans (proxy, DB, mod_wsgi)
* 03. Non-Standard Ports
* 04. Reading Denials
* images/ (1)

### 01. Notes/03. Web Server Labs
* 01. Lab 5.1.A Apache HTTP Server Installation, Virtual Hosts, and HTTPS/  (lab.md, Source Code/ [12], images/ [2], screenshots/ [10])
* 02. Lab 5.1.B Nginx - Static Site, Reverse Proxy, and Load Balancer/  (lab.md, Source Code/ [26], images/ [1], screenshots/ [8])
* 03. Lab 5.1.C Apache Tomcat - Java Application Server/  (lab.md, Source Code/ [12], images/ [1], screenshots/ [5])

### 01. Notes/04. Section 5.2 Delivery Friendly Applications and the Twelve Factor Model
* 01. What Makes an Application Friendly to Automated Delivery
* 02. The Twelve Factor App The Enduring and the Dated
* images/ (2)

### 01. Notes/05. Lab 5.2 Build the Reference Application
* Lab 5.2 Build the Reference Application
* images/ (1), Source Code/ (5)

### 01. Notes/06. Section 5.3 Testing Strategy
* 01. Testing as a First-Class Engineering Concern
* 02. The Test Pyramid
* 03. Contract Testing
* 04. Test Data Management
* 05. Quarantining a Flaky Test an Engineering Decision
* images/ (3)

### 01. Notes/07. Lab 5.3 A Layered Test Suite for the Reference Application
* Lab 5.3 A Layered Test Suite for the Reference Application
* images/ (1), Source Code/ (4)

### 01. Notes/08. Section 5.4 Pipeline Speed as a Product Feature
* 01. Speed Is a Feature, Not a Nicety
* 02. Caching
* 03. Parallelism
* 04. Selective Scheduling
* images/ (4)

### 01. Notes/09. Lab 5.4 A Fast Pipeline for the Reference Application
* Lab 5.4 A Fast Pipeline for the Reference Application
* images/ (1), Source Code/ (1)

### 02. Labs  (standalone lab set)
* lab_5a_tls_virtual_hosts/  (lab.md, Source Code/ [3])
* lab_5b_static_proxy_loadbalancing/  (lab.md, Source Code/ [2])
* lab_5c_reference_application/  (lab.md, Source Code/ [7])
* lab_5d_testing_and_runtime/  (lab.md, Source Code/ [5])
* lab_5e_schema_migration/  (lab.md, Source Code/ [3])

## Structure notes

Two lab sets are included. The **embedded labs** live under `01. Notes` next to the theory they belong to: the three web-server labs (Apache 5.1.A, Nginx 5.1.B, Tomcat 5.1.C) sit inside `03. Web Server Labs`, and Labs 5.2 to 5.4 are their own numbered folders. The **standalone lab set** (5A to 5E) is under `02. Labs`.

Every lab folder, in both sets, has its own `Source Code` folder holding the files that lab has you write, extracted verbatim from the lab text. For the command-heavy web-server labs the file names are inferred from context (for example `vhost.conf`, `ssl-vhost.conf`, `proxy.conf`, `index.html`, `tomcat-users.xml`, `WEB-INF/web.xml`), so treat them as a starting point rather than canonical paths. Shell command sequences were left in the lab text, not turned into files.

The 23 screenshots are filed into the web-server lab they belong to: Apache screenshots under Lab 5.1.A, Nginx and proxy/load-balancer screenshots under Lab 5.1.B, and Tomcat screenshots under Lab 5.1.C, each in that lab's `screenshots/` folder. They are not referenced inline in the text; the source contains no image slots for them.
