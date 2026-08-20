# Module 3: Networking Fundamentals

---
> Prerequisites:

> This module assumes you have completed the Foundation Module and Module 2. You already know what an IP address is, the difference between public and private addressing, what a subnet is conceptually, how DNS resolution works as a lookup chain, what a firewall does as a gatekeeper, and why a single server is never enough. This module builds on that with the engineering depth you need to actually configure, diagnose, and operate networked systems, and it ends with three labs you must complete before Module 4.
---
## What You Will Learn

- The OSI layers a delivery engineer actually touches, and the habit of diagnosing bottom to top

- How TCP/IP maps onto OSI, and why the mapping is loose

- TCP versus UDP, the three way handshake, ports, sockets, and the service ports you should know by memory

- Connection states, and what port exhaustion looks like from the outside when it bites you

- Routing tables, default gateways, static routes, and a conceptual look at dynamic routing

- DNS record types, TTL management around a cutover, and split horizon DNS
- Load balancing at L4 and L7, the four algorithms that matter, sticky sessions, and health checks

- Firewalls and security groups, stateful versus stateless, default deny, firewalld zones, AWS security groups, NACLs, and iptables

- DHCP, and why address assignment still matters for containers and cloud instances

- TLS and HTTPS, the handshake, certificates, chains, SNI, and a correct Nginx TLS block

- NAT, CIDR, subnetting math, NAT gateways, and the special address ranges you will see every week

- The mistakes that actually happen in production, and how to avoid making them

---
## Contents

### 01. Notes/Part 1 Theory
* 01. The OSI Model
* 02. TCP IP
* 03. Routing
* 04. DNS in Practice
* 05. Load Balancing
* 06. Load Balancing Algorithms
* 07. Firewalls and Security Groups
* 08. DHCP
* 09. TLS and HTTPS
* 10. NAT, Addressing, and CIDR in Practice
* images/ (28 figures)

### 01. Notes/Part 2 Linux and Cloud Networking Reference
* 01. Networking Concepts
* 02. IPv4 Classful Addressing & Special Ranges
* 03. Linux Networking Commands
* 04. Network Interface Configuration
* 05. Configuring IP, Gateway, DNS (Persistent Configuration)
* 06. DNS Details
* 07. Routing & Gateway
* 08. Network Troubleshooting
* 09. Cloud Networking Basics (AWS, Azure, GCP)
* 10. Container & Kubernetes Networking
* 11. Infrastructure as Code (IaC) for Networking
* 12. Monitoring & Troubleshooting
* 13. Cleanup & Reversion
* 14. Legacy vs Modern
* 15. References
* images/ (2 figures)

### 01. Notes/Part 3 Labs
* 01. Lab 3A Diagnose a Broken DNS and Routing Scenario
* 02. Lab 3B Subnetting and a Three Tier VPC Design (On Paper)
* 03. Lab 3C Two VMs on Different Subnets, Connected with Static Routes
* images/ (2 figures)

### 01. Notes  (Appendix files)
* Common Mistakes

### 02. Labs
* Lab 3a network diagnostics/  (02 Lab M3 A Network Diagnostics.md)
* Lab 3b subnet design/  (03 Lab M3 B Subnet Design.md)
* Lab 3c static routing/  (04 Lab M3 C Static Routing.md)

---
## Note to lab map

Prerequisite text is quoted from each lab file.

| Lab | Read first |
|---|---|
| Lab 3A: Network Diagnostics | Read Module 3 sections 3.1 (the OSI model), 3.2 (TCP/IP), 3.3 (routing), and 3.4 (DNS) |
| Lab 3B: Subnet Design | Read Module 3 section 3.10, NAT, Addressing, and CIDR in Practice |
| Lab 3C: Static Routing | Read Module 3 sections 3.3 (Routing) and 3.10 (NAT, Addressing, and CIDR) |
