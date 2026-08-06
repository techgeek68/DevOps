# Module 2: Linux and Systems Fundamentals

> **What this module is for.** 

> Every later module in this course assumes you can drive a Linux host without hesitation. Containers are Linux kernel features. Kubernetes nodes are Linux hosts. Terraform provisioners, Ansible modules, CI runners, and observability agents all land on Linux. If the shell, systemd, permissions, networking, and SSH are not second nature, everything after this point becomes guesswork.

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

---
### [01. Notes/Part 1 Virtualization and Why Linux](<01. Notes/Part 1 Virtualization and Why Linux>)
* [01. Hypervisors](<01. Notes/Part 1 Virtualization and Why Linux/01. Hypervisors.md>)
* [02. Why Linux Dominates DevOps](<01. Notes/Part 1 Virtualization and Why Linux/02. Why Linux Dominates DevOps.md>)
* [images/](<01. Notes/Part 1 Virtualization and Why Linux/images>) (4 figures)

---
### [01. Notes/Part 2 Linux for DevOps](<01. Notes/Part 2 Linux for DevOps>)
* [01. Fundamental Linux Commands](<01. Notes/Part 2 Linux for DevOps/01. Fundamental Linux Commands.md>)
* [02. Getting Help in Linux](<01. Notes/Part 2 Linux for DevOps/02. Getting Help in Linux.md>)
* [03. Text Processing and Pipelines](<01. Notes/Part 2 Linux for DevOps/03. Text Processing and Pipelines.md>)
* [04. Compression and Archiving](<01. Notes/Part 2 Linux for DevOps/04. Compression and Archiving.md>)
* [05. Managing Users and Groups](<01. Notes/Part 2 Linux for DevOps/05. Managing Users and Groups.md>)
* [06. Managing Permissions and Ownership](<01. Notes/Part 2 Linux for DevOps/06. Managing Permissions and Ownership.md>)
* [07. Package Management](<01. Notes/Part 2 Linux for DevOps/07. Package Management.md>)
* [08. Text Editors](<01. Notes/Part 2 Linux for DevOps/08. Text Editors.md>)
* [09. Shell Environment and Configuration](<01. Notes/Part 2 Linux for DevOps/09. Shell Environment and Configuration.md>)
* [10. Bash Shell Scripting](<01. Notes/Part 2 Linux for DevOps/10. Bash Shell Scripting.md>)
* [11. Scheduling Tasks](<01. Notes/Part 2 Linux for DevOps/11. Scheduling Tasks.md>)
* [12. Viewing and Managing Logs](<01. Notes/Part 2 Linux for DevOps/12. Viewing and Managing Logs.md>)
* [13. Process Management, System Monitoring, and Performance Tuning](<01. Notes/Part 2 Linux for DevOps/13. Process Management, System Monitoring, and Performance Tuning.md>)
* [14. Networking](<01. Notes/Part 2 Linux for DevOps/14. Networking.md>)
* [15. Firewall Management](<01. Notes/Part 2 Linux for DevOps/15. Firewall Management.md>)
* [16. Disk Management](<01. Notes/Part 2 Linux for DevOps/16. Disk Management.md>)
* [17. Terminal Multiplexers tmux](<01. Notes/Part 2 Linux for DevOps/17. Terminal Multiplexers tmux.md>)
* [18. Remote Login with SSH](<01. Notes/Part 2 Linux for DevOps/18. Remote Login with SSH.md>)
* [images/](<01. Notes/Part 2 Linux for DevOps/images>) (20 figures)

---
### [01. Notes/Part 3 systemd in Depth](<01. Notes/Part 3 systemd in Depth>)
* [01. systemd The Foundation of a Linux Server](<01. Notes/Part 3 systemd in Depth/01. systemd The Foundation of a Linux Server.md>)
* [02. Quick Reference Virtualization and systemd](<01. Notes/Part 3 systemd in Depth/02. Quick Reference Virtualization and systemd.md>)
* [03. Common Mistakes with systemd](<01. Notes/Part 3 systemd in Depth/03. Common Mistakes with systemd.md>)
* [images/](<01. Notes/Part 3 systemd in Depth/images>) (5 figures)

---
### [01. Notes/Part 4 Errata and Version Notes](<01. Notes/Part 4 Errata and Version Notes>)
* [01. Reference platform](<01. Notes/Part 4 Errata and Version Notes/01. Reference platform.md>)
* [02. dnf is now DNF5](<01. Notes/Part 4 Errata and Version Notes/02. dnf is now DNF5.md>)
* [03. ifcfg files are gone](<01. Notes/Part 4 Errata and Version Notes/03. ifcfg files are gone.md>)
* [04. The installer no longer creates a profile for every NIC](<01. Notes/Part 4 Errata and Version Notes/04. The installer no longer creates a profile for every NIC.md>)
* [05. sshd socket activation is not the Fedora default](<01. Notes/Part 4 Errata and Version Notes/05. sshd socket activation is not the Fedora default.md>)
* [06. OpenSSH is now split into sshd and sshd-session](<01. Notes/Part 4 Errata and Version Notes/06. OpenSSH is now split into sshd and sshd-session.md>)
* [07. Node.js versions in the install from source example](<01. Notes/Part 4 Errata and Version Notes/07. Node.js versions in the install from source example.md>)
* [08. netstat is not installed](<01. Notes/Part 4 Errata and Version Notes/08. netstat is not installed.md>)
* [09. iptables on RHEL 10](<01. Notes/Part 4 Errata and Version Notes/09. iptables on RHEL 10.md>)

---
### [01. Notes/Part 5 Labs](<01. Notes/Part 5 Labs>)
* [01. Lab 2A Build the Host](<01. Notes/Part 5 Labs/01. Lab 2A Build the Host.md>)
* [02. Lab 2B The Linux Core Skills Grind](<01. Notes/Part 5 Labs/02. Lab 2B The Linux Core Skills Grind.md>)
* [03. Lab 2C A Health Check Script](<01. Notes/Part 5 Labs/03. Lab 2C A Health Check Script.md>)
* [04. Lab 2D The Same Thing as a systemd Timer](<01. Notes/Part 5 Labs/04. Lab 2D The Same Thing as a systemd Timer.md>)
* [05. Lab 2E Performance Triage](<01. Notes/Part 5 Labs/05. Lab 2E Performance Triage.md>)
* [images/](<01. Notes/Part 5 Labs/images>) (1 figure)

---
### [02. Labs](<02. Labs>)
* [Lab 2a Build the Host/](<02. Labs/Lab 2a Build The Host>) > [02 Lab 2A Build the Host.md](<02. Labs/Lab 2a Build The Host/02 Lab 2A Build the Host.md>)

* [Lab 2b Core Skills Grind/](<02. Labs/Lab 2b Core Skills Grind>) > [03 Lab 2B The Core Skills Grind.md](<02. Labs/Lab 2b Core Skills Grind/03 Lab 2B The Core Skills Grind.md>)

* [Lab 2c Health Check Cron/](<02. Labs/Lab 2c Health Check Cron>) > [04 Lab 2C Bash Health Check Script Scheduled with cron.md](<02. Labs/Lab 2c Health Check Cron/04 Lab 2C Bash Health Check Script Scheduled with cron.md>)

* [Lab 2d Systemd Timer/](<02. Labs/Lab 2d Systemd Timer>) > [05 Lab 2D The Same Job 2C as a systemd Unit and Timer.md](<02. Labs/Lab 2d Systemd Timer/05 Lab 2D The Same Job 2C as a systemd Unit and Timer.md>)

* [Lab 2e Performance Triage/](<02. Labs/Lab 2e Performance Triage>) > [06 Lab 2E Performance Triage.md](<02. Labs/Lab 2e Performance Triage/06 Lab 2E Performance Triage.md>)

---
## Lab order and prerequisites

Prerequisite text is quoted from each lab file.

| Lab | Prerequisite |
|---|---|
| [Lab 2A](<02. Labs/Lab 2a Build The Host/02 Lab 2A Build the Host.md>) | None. This is the first lab of the module. |
| [Lab 2B](<02. Labs/Lab 2b Core Skills Grind/03 Lab 2B The Core Skills Grind.md>) | Lab 2A complete. You need a working VM and SSH access to it. |
| [Lab 2C](<02. Labs/Lab 2c Health Check Cron/04 Lab 2C Bash Health Check Script Scheduled with cron.md>) | Labs 2A and 2B complete. You need `nginx` installed, which 2B does. |
| [Lab 2D](<02. Labs/Lab 2d Systemd Timer/05 Lab 2D The Same Job 2C as a systemd Unit and Timer.md>) | Lab 2C complete. This lab reschedules the script you already wrote. |
| [Lab 2E](<02. Labs/Lab 2e Performance Triage/06 Lab 2E Performance Triage.md>) | Labs 2A and 2B complete. `sysstat` and `stress-ng` installed. |
