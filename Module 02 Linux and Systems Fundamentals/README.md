# Module 2: Linux and Systems Fundamentals

> **What this module is for.** Every later module in this course assumes you can drive a Linux host without hesitation. Containers are Linux kernel features. Kubernetes nodes are Linux hosts. Terraform provisioners, Ansible modules, CI runners, and observability agents all land on Linux. If the shell, systemd, permissions, networking, and SSH are not second nature, everything after this point becomes guesswork.

---
> **How this module is organised.**

> * **Part 1:** Virtualization, hypervisors, and why Linux is the default platform. This is the conceptual setup for Module 6 (containers).

> * **Part 2:** The core of Linux for DevOps. Filesystem hierarchy, commands, text processing, archiving, users and permissions, packages, editors, shell environment, Bash scripting, scheduling, logs, processes and performance, networking, firewalls, disks, tmux, and SSH.

> * **Part 3:** systemd in depth. Units, targets, journald, and socket activation.

> * **Part 4:** Errata and version notes as of July 2026. Read this before you follow any command in Part 2 on a brand new Fedora 44 or RHEL 10 host.

> * **Part 5:** Labs 2A through 2E. The theory is assessed through these, not separately.

---
> **Reference platform for this module:** Fedora Server 44 or RHEL 10. Ubuntu 24.04 LTS equivalents are given where the two families diverge.

---
## Contents


### 01. Notes/Part 1 Virtualization and Why Linux
* 01. Hypervisors
* 02. Why Linux Dominates DevOps
* images/ (4 figures)

### 01. Notes/Part 2 Linux for DevOps
* 01. Fundamental Linux Commands
* 02. Getting Help in Linux
* 03. Text Processing and Pipelines
* 04. Compression and Archiving
* 05. Managing Users and Groups
* 06. Managing Permissions and Ownership
* 07. Package Management
* 08. Text Editors
* 09. Shell Environment and Configuration
* 10. Bash Shell Scripting
* 11. Scheduling Tasks
* 12. Viewing and Managing Logs
* 13. Process Management, System Monitoring, and Performance Tuning
* 14. Networking
* 15. Firewall Management
* 16. Disk Management
* 17. Terminal Multiplexers tmux
* 18. Remote Login with SSH
* images/ (20 figures)

### 01. Notes/Part 3 systemd in Depth
* 01. systemd The Foundation of a Linux Server
* 02. Quick Reference Virtualization and systemd
* 03. Common Mistakes with systemd
* images/ (5 figures)

### 01. Notes/Part 4 Errata and Version Notes
* 01. Reference platform
* 02. dnf is now DNF5
* 03. ifcfg files are gone
* 04. The installer no longer creates a profile for every NIC
* 05. sshd socket activation is not the Fedora default
* 06. OpenSSH is now split into sshd and sshd-session
* 07. Node.js versions in the install from source example
* 08. netstat is not installed
* 09. iptables on RHEL 10

### 01. Notes/Part 5 Labs
* 01. Lab 2A Build the Host
* 02. Lab 2B The Linux Core Skills Grind
* 03. Lab 2C A Health Check Script
* 04. Lab 2D The Same Thing as a systemd Timer
* 05. Lab 2E Performance Triage
* images/ (1 figures)

### 02. Labs
* lab_2a_build_the_host/  (02 Lab 2A Build the Host.md)
* lab_2b_core_skills_grind/  (03 Lab 2B The Core Skills Grind.md)
* lab_2c_healthcheck_cron/  (04 Lab 2C Bash Health Check Script Scheduled with cron.md)
* lab_2d_systemd_timer/  (05 Lab 2D The Same Job 2C as a systemd Unit and Timer.md)
* lab_2e_performance_triage/  (06 Lab 2E Performance Triage.md)

## Lab order and prerequisites

Prerequisite text is quoted from each lab file.

| Lab | Prerequisite |
|---|---|
| Lab 2A | None. This is the first lab of the module. |
| Lab 2B | Lab 2A complete. You need a working VM and SSH access to it. |
| Lab 2C | Labs 2A and 2B complete. You need `nginx` installed, which 2B does. |
| Lab 2D | Lab 2C complete. This lab reschedules the script you already wrote. |
| Lab 2E | Labs 2A and 2B complete. `sysstat` and `stress-ng` installed. |
