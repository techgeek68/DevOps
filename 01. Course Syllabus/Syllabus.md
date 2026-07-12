# DevOps and Platform Engineering
---
### A complete curriculum from Linux fundamentals to AI driven cloud native operations
---
**Version 2.0** | Instructor: Anup Pyakurel | Contact: +977 9851124956

---
## Why this program exists

Software delivery has moved through a few real eras. First came the traditional split, where developers wrote code and a separate operations team kept it running, with long release cycles and manual handoffs. Then came the DevOps era, where automation, shared ownership, and continuous delivery closed that gap. Then came the cloud native era, where Kubernetes, containers, and infrastructure as code became the default way systems get built. Right now, the field is in the middle of a new shift, where AI assistants write a growing share of code and infrastructure, and engineers are judged less by how fast they can type a Terraform file and more by how well they can review, question, and operate what gets generated.

That last shift is not a marketing line. The DORA 2024 and 2025 Accelerate reports, which together surveyed several thousand engineers, found that AI adoption raises individual throughput while making team level delivery less stable on average. Change failure rate and rework rate get worse, not better, unless the surrounding delivery system is already strong. AI adoption tends to amplify the maturity, or the immaturity, of the delivery system it lands in. It does not fix a weak pipeline. It amplifies whatever is already there. That finding is the reason this program exists in the shape it does: the review discipline, the automated gates, the observability, and the rollback path are not old fashioned ceremony to get through before you get to the interesting AI part. They are the thing that decides whether the AI part helps you or hurts you.

So this program teaches all four layers in order, on purpose, because a working engineer meets legacy systems, cloud native systems, and AI assisted workflows in the same week of a real job. Every concept is anchored to a lab or a mini project, so a graduate leaves with a working portfolio, not just notes.

GitHub Actions is the primary CI/CD platform throughout, reflecting where the industry has moved for greenfield projects. Jenkins, Maven, Tomcat, PHP, OpenShift, and the Elastic stack are not scattered through the core as optional detours. They live in a separate, properly scheduled elective track at the end of this document, with their own hours and their own assessment, because "optional" content with no time budget is content that either does not get done or quietly wrecks the schedule.

---
## Who this is for

BSc CSIT, BCA, Computer Engineering, and IT Engineering graduates, plus anyone starting out or already a year or two into a junior DevOps role who wants a full, honest, structured path rather than a scattered pile of tutorials.

You do not need prior Linux or networking experience. The primer below is the only real prerequisite, and it is designed so that a motivated beginner can close the gap before Week 1.

---
## Program at a glance

| Field | Details |
|---|---|
| **Course codes** | DVP 101, DVP 201, DVP 301, plus DVP 150 (elective track) |
| **Credits** | 3, 4, 4, plus 2 for the elective track |
| **Level** | Undergraduate / Professional Certificate |
| **Total duration** | 40 weeks across three courses |
| **Contact hours** | 6 hours of class per week (two 3 hour sessions), plus 1 hour of scheduled lab support |
| **Independent study** | 6 to 8 hours per week |
| **Prerequisites** | Completion of the Module 0 primer. Nothing else. |
| **Cohort size** | 16 to 24 students. Above 24, the lab feedback loop breaks down. |
| **Delivery** | In person or live online, cohort based. Recordings available. Not self paced. |

---

| Course | Focus | Weeks |
|---|---|---|
| **DVP 101: Foundations of Delivery Engineering** | Linux, networking, Git, web servers, application and test fundamentals, containers, CI | 12 |
| **DVP 201: Cloud Native Infrastructure and Delivery** | Cloud, IaC, config management, Kubernetes, observability, GitOps, progressive delivery | 14 |
| **DVP 301: Reliability, Security, Platform, and AI Driven Operations** | SRE, chaos, DR, DevSecOps, supply chain, service mesh, FinOps, platform, AI, capstone | 14 |
| **DVP 150: Enterprise and Legacy Stack (elective)** | Jenkins, Maven, Tomcat, PHP/LAMP, OpenShift, Elastic Stack | Self paced, 25 hours |

DVP 201 requires a pass in DVP 101. DVP 301 requires a pass in DVP 201. The elective can be taken at any point after Week 8 of DVP 101 and is graded independently.

---
## What this program costs you in cash

The AWS free tier does not cover most of what you build in Course 2 and Course 3. Prices below are approximate US East figures at the time of writing, and you must check current AWS pricing yourself, but the shape of the number is right.

| Item | Roughly | When |
|---|---|---|
| EC2 t3.micro / t3.small for early labs | Free tier covers most of this | Course 2, Weeks 1 to 4 |
| NAT gateway | About 32 USD per month plus data charges, **not free tier** | Course 2, Week 2 onward |
| EKS control plane | About 73 USD per month per cluster, **not free tier** | Course 2, Week 8 onward |
| EKS worker nodes (two t3.medium) | About 60 USD per month if left running | Course 2 and 3 |
| Load balancer | About 16 USD per month plus usage | Course 2 and 3 |
| S3, DynamoDB, ECR, Lambda at lab scale | A few dollars total | Throughout |
| Secrets Manager at lab scale | A few dollars total | Course 3 Module 19 (free path: LocalStack or Vault dev mode) |

**Realistic total if you are disciplined: 40 to 90 USD across the whole program.** You destroy the expensive things after every lab session and only bring them up when you need them. **Realistic total if you forget one `terraform destroy` over a long weekend: 150 USD and a bad Monday.**

Three things are therefore mandatory, not suggested:

1. **Lab 8A is a billing lab, and it comes before anything else in Course 2.** You set an AWS Budget, a billing alarm at 10 USD, and a hard alarm at 50 USD, and you prove they fire.

2. **Every cloud lab ends with a teardown step, and the teardown is part of the grade.** A lab submitted with resources still running loses marks.

3. **There is a documented free path.** If cloud spend is not possible for you, you can complete every graded requirement in this program using kind or k3d for Kubernetes and LocalStack for AWS APIs. The free path is spelled out in Appendix B. You lose some realism, you lose no marks, and you must tell the instructor in Week 1 of Course 2 so the labs get adapted for you in advance rather than improvised on the day.

Everything else in the program is free: GitHub, Docker Hub or GHCR, all the CNCF tooling, and the Red Hat Developer sandbox. AI assistant access is discussed in the AI policy section below, and a free tier assistant is sufficient for every graded task.

---
## Hardware

| | Minimum | Comfortable |
|---|---|---|
| RAM | 8 GB | 16 GB |
| Free disk | 60 GB | 100 GB+ |
| CPU | 4 cores with virtualization enabled | 8 cores |

On 8 GB, you can do everything, but you run one thing at a time: the VM or the local Kubernetes cluster, not both. Labs that assume both are flagged, and each one has an 8 GB variant that uses a single node k3d cluster instead of kind plus a VM.

If you have less than 8 GB, tell the instructor in Week 1. A shared cloud VM can be arranged for Linux and container work at a cost of a few dollars a month, and that is a normal, supported path, not a favour.

---
## The AI policy, stated plainly

You may use AI assistants for everything in this program. You are expected to. Pretending otherwise in 2026 would be a bad joke, and a graduate who cannot work fluently with an assistant is already behind.

But that changes how you get graded, and it changes it in a way you should understand from day one.

**Every graded artefact is defended live.** Ten minutes, one on one or in front of the cohort. The instructor picks lines from your work and asks you to explain them. Why that CIDR block? What breaks if that readiness probe is deleted? What happens to this rollback if the migration has already run? Why did you choose this over the alternative? If you cannot answer, the artefact does not pass, regardless of whether it works.

This is not a trap. It is exactly the job. In a real team, an assistant will write a Terraform module for you in ninety seconds, and then you will spend an hour in review being asked exactly these questions by a senior engineer, and your answer is what you are actually paid for.

Two rules on top of that:

- **Disclose.** Every lab submission includes a one line note: which assistant, what you used it for, what it got wrong. This costs nothing and it builds the habit that Module 24 is about.
  
- **Never paste a credential, a private key, or client data into an assistant.** This is a hard rule with a hard consequence, and the reason gets covered properly in Module 24.

---
## Assessment and grading

### Weighting

| Component | DVP 101 | DVP 201 | DVP 301 |
|---|---|---|---|
| Labs (graded, best N of M) | 60% | 50% | 30% |
| Two practical checkpoints (timed, hands on) | 30% | 30% | 20% |
| Live defenses | 10% | 10% | 10% |
| Capstone | n/a | n/a | 40% |

**Pass mark is 60%, with a floor: you cannot pass any course with less than 50% on the practical checkpoints.** Coursework can carry you, but not past a demonstrated inability to do the work under time pressure, because the job has time pressure.

---
### The lab rubric (applies to every graded lab)

Each lab is out of 10.

| Band | Marks | What it means |
|---|---|---|
| Works | 0 to 4 | The thing does what was asked. Evidence attached (output, screenshot, or a passing pipeline). |
| Explained | 0 to 3 | The write up says what you did and, more importantly, *why*, including at least one thing you tried that did not work. |
| Cleaned up | 0 to 1 | Cloud resources destroyed. No secrets committed. `.gitignore` sane. |
| Defended | 0 to 2 | You answered the follow up questions. |

A lab that works perfectly and cannot be explained caps at 5 out of 10. That ratio is deliberate, and it is the whole philosophy of the program in one table.

---
### The practical checkpoints

Two per course, three hours each, on a machine you have not seen, with a broken system in front of you. Not a quiz. You get told what should be happening, you get shown what is happening, and you fix it and write up what you found. Lab 7F is the training wheels version of this, and it is why that lab exists.

---
### Late work

Labs are accepted up to one week late at 80% of the awarded mark. After that, they score zero unless you talked to the instructor *before* the deadline, in which case we sort it out like adults. Life happens. Silence is the only thing that costs you.

---
## Program outcomes, and where each one is actually assessed

Twenty two outcomes with no evidence trail is a wish list. Here is the trail.

| # | On completing this program you can... | Assessed by |
|---|---|---|
| 1 | Explain the delivery lifecycle, the five DORA metrics, and how DevOps, SRE, and platform engineering relate | Lab 1A, 1D|
| 2 | Administer Linux systems: users, permissions, services, scripting, performance | Labs 2A to 2E|
| 3 | Diagnose and design networks: subnetting, DNS, load balancing, firewalls | Labs 3A to 3C |
| 4 | Apply professional Git and GitHub workflows including review and branch protection | Labs 4A to 4D; capstone component 2 |
| 5 | Deploy and configure Apache and Nginx, and reason about where TLS terminates | Labs 5A, 5B |
| 6 | Build a delivery friendly application with environment config and a real test suite | Labs 5C to 5E; capstone component 1 |
| 7 | Build, run, and secure containers with Docker and Podman | Labs 6A to 6E |
| 8 | Design CI/CD pipelines in GitHub Actions, authenticating via short lived OIDC credentials | Labs 7A to 7F, 14B; capstone 4 |
| 9 | Automate configuration with Ansible roles, playbooks, and dynamic inventory | Labs 10A to 10D; capstone 7 |
| 10 | Provision and scan repeatable cloud infrastructure with Terraform or OpenTofu | Labs 9A to 9G; capstone 6 |
| 11 | Deploy and operate applications on Kubernetes and on managed EKS | Labs 11A to 11H; capstone 8 |
| 12 | Secure a cluster with NetworkPolicy, Pod Security Admission, RBAC, and resource limits | Labs 12A to 12D; capstone 8 |
| 13 | Scale workloads with HPA, Cluster Autoscaler or Karpenter, and right size against real data | Labs 12E, 22C |
| 14 | Implement observability on OpenTelemetry: Prometheus, Grafana, Jaeger, Alertmanager | Labs 13A to 13E; capstone 9 |
| 15 | Operate GitOps with ArgoCD, and get secrets into a cluster without putting them in Git | Labs 14A to 14D; capstone 5 |
| 16 | Run progressive delivery with metric driven automatic rollback, and know when a feature flag is the better tool | Labs 15A to 15C; capstone elective |
| 17 | Ship a database schema change that is safe to roll back | Lab 15D; capstone 4 |
| 18 | Apply SRE practice: SLIs, SLOs, error budgets, on call, blameless postmortems | Labs 16A to 16C, 17B |
| 19 | Run a chaos experiment and interpret the resilience response | Lab 17A |
| 20 | Execute a scoped DR exercise, measure real RPO and RTO, and write the postmortem | Labs 18A, 18B; capstone elective |
| 21 | Apply DevSecOps across the pipeline: secrets, SAST, SCA, image scanning, secrets scanning, dependency updates | Labs 19A to 19E; capstone 4 |
| 22 | Generate an SBOM, sign and verify images, and enforce cluster policy with Kyverno | Labs 20A to 20C; capstone elective |
| 23 | Explain service mesh fundamentals: mTLS, traffic shifting via Gateway API, mesh observability | Labs 21A, 21B; capstone elective |
| 24 | Reason about cost, and port a mental model between AWS, GCP, and Azure | Labs 22A to 22C |
| 25 | Describe platform engineering, golden paths, and internal developer platforms | Labs 23A, 23B; capstone 10 |
| 26 | Use AI assistants responsibly across code, infrastructure, and operations, and threat model the new risks | Labs 24A to 24E; every live defense |
| 27 | Deliver a complete, automated, observable, secure pipeline as a solo capstone | Module 25 |

---
## Module 0: The primer

Self paced, ungraded, finish it before Week 1. This closes the gaps that otherwise get quietly assumed and then cause real trouble in Week 5.

- **Bash fundamentals.** Variables, conditionals, loops, functions, exit codes, quoting, pipes, redirects. This gets used constantly from Week 2 onward, so it earns a real primer rather than an assumption.

- **Python basics.** Variables, control flow, functions, file IO, pip. Enough to read and change a small web application.

- **SQL basics.** SELECT, INSERT, UPDATE, joins, and what a connection string actually is.

- **YAML and JSON literacy.** Indentation, key value structure, lists versus maps, and how the same data looks in both. This shows up in almost every tool taught later, and more student hours are lost to YAML indentation than to any single concept in this course.

- **Git, the absolute basics.** Clone, add, commit, push. Module 4 does the real work, but arriving with zero Git is painful.

There is a short, ungraded self check at the end. If you struggle with it, come to the supplementary session in Week 0. That session exists so nobody falls behind quietly.

---
## Required accounts

| Requirement | Notes |
|---|---|
| GitHub account | Day one. Free tier is fine throughout. |
| Container registry | Docker Hub or GitHub Container Registry. Either. Free. |
| AWS account | Not needed until Course 2, Week 1. See the cost section above before you create it. |
| Virtualization | VirtualBox (free) or VMware Workstation Pro (free for personal, educational, and commercial use since Broadcom's 2025 licensing change, no key needed). |
| Red Hat Developer account | Free. Only needed for the OpenShift elective. |
| An AI assistant | Any. A free tier is enough for every graded task. |

---
---
# DVP 101: Foundations of Delivery Engineering

**12 weeks. Two 3 hour sessions per week.**

| Week | Module | Focus | Deliverable |
|---|---|---|---|
| 1 | 1 | Delivery engineering mindset, DORA, SRE, drift | Labs 1A, 1B |
| 2 | 1 / 2 | Case study, then Linux foundations begin | Lab 1D, 2A |
| 3 | 2 | Linux: text processing, permissions, packages | Lab 2B |
| 4 | 2 | Linux: systemd, scripting, cron, logs | Labs 2C, 2D |
| 5 | 2 / 3 | Linux: processes, performance, SSH. Networking begins | Lab 2E |
| 6 | 3 | Networking: TCP/IP, DNS, load balancing, subnetting | Labs 3A, 3B |
| 7 | 3 / 4 | Networking labs, then Git | Lab 3C, 4A |
| 8 | 4 | Git workflows, review, branch protection, issue tracking | Labs 4B, 4C, 4D. **Checkpoint 1.1** |
| 9 | 5 | Web servers, application design, testing strategy | Labs 5A, 5B, 5C |
| 10 | 5 / 6 | The app and its tests. Containers begin | Labs 5D, 5E, 6A |
| 11 | 6 | Containers: multi stage, rootless, compose, registry | Labs 6B, 6C, 6D, 6E |
| 12 | 7 | Continuous integration | Labs 7A to 7F. **Checkpoint 1.2** |

---
## Module 1: The Delivery Engineering Mindset

**Theory**

- The delivery lifecycle: plan, code, build, test, release, deploy, operate, monitor.
- Agile and DevOps: what each solves, and how they complement rather than replace each other.
- SRE next to DevOps: error budgets, SLIs, SLOs, SLAs, and when each model applies.
- **The DORA metric set, as of the 2024 and 2025 reports.** DORA has grown beyond the original four (deployment frequency, lead time for changes, change failure rate, and mean time to recover) that most articles still cite. Recent reports separate throughput metrics from stability metrics, redefine recovery as "failed deployment recovery time" (specifically, time to recover from a failure caused by a change to production, not from any outage), and add rework as a distinct dimension. Treat the DORA metric set as an evolving research program rather than a fixed list, and check the current `dora.dev` definitions when you cite it.
- What the DORA 2024 and 2025 research found about AI: individual throughput up, team level stability down on average, with the gap widening in teams whose delivery system is weak and closing in teams whose delivery system is strong. This is the thesis of the entire program, and we state it in Week 1 rather than saving it for Module 24.
- Infrastructure as code as a concept, and the shift from click ops to declarative provisioning. Hands on Terraform waits for Course 2.
- Microservices versus monoliths, as a trade off rather than a right answer.
- A preview of platform engineering and AI assisted operations, so you can see the whole road before you start walking it.

**Labs**

- **1A. Measure DORA, honestly.** Pick a real open source project. From its public commit history and release tags, calculate the two metrics you actually *can* observe from outside: deployment frequency and lead time for changes. Then write the more important half of this lab: explain why change failure rate, failed deployment recovery time, and rework rate **cannot** be derived from public data, and what instrumentation a team would need to add to measure them. The lesson here is that DORA requires instrumentation, not archaeology.

- **1B. Error budgets.** Calculate the error budget for several availability targets over 30 days. Analyse outage scenarios and see how much budget each consumes and whether a maintenance window still fits. Then design an SLI, a matching SLO, and an external SLA for a service of your choosing, so that the discipline behind a reliability buffer is something you have built once rather than only calculated.

- **1C. Drift, the low tech version.** Two identical Linux VMs. Make the same configuration change two ways: by hand over SSH on one, with a small idempotent shell script on the other. A week later, make an undocumented manual change to the first VM only. Compare how easy it is to know what state each machine is in, and how easy it would be to rebuild each from scratch. This is deliberately primitive. Module 9 does the same thing with real Terraform against real AWS, and you will be asked to compare the two.

- **1D. The broken startup.** A hypothetical company with a manual, single person dependent delivery process. Assess its DORA baseline, identify the operational risks, design the target lifecycle, build a sprint by sprint 90 day improvement plan, define the team's first SLO, and propose a concrete fix for the "only Ramesh can deploy" problem inside six weeks.

---
## Module 2: Linux and Systems Fundamentals

This is the longest module in the program, and it gets three full weeks, because it is the foundation everything else sits on and because compressing it is the single most common way a DevOps course fails its students.

**Theory**

- Why Linux is the default here: the tooling ecosystem, SSH first management, and a smaller attack surface.
- Hypervisors, Type 1 versus Type 2, and virtual machines versus containers, as a short comparison that sets up Module 6.
- Filesystem hierarchy and fundamental commands: navigation, viewing, file and directory operations, finding things, getting help.
- Text processing: grep, find, pipelines, redirection, awk, sed, cut, sort, uniq, wc.
- Compression and archiving: tar, gzip, bzip2, xz, zip.
- Users, groups, permissions: useradd, usermod, groupadd, sudo, chmod, chown, umask, special permissions, ACLs.
- Package management: dnf and apt, plus installing from source.
- systemd: unit files, targets, socket activation, service management, journald.
- Editors: vim, nano.
- Shell environment: startup files, PATH, aliases.
- Bash scripting in practice: variables, arrays, operators, control structures, loops, functions, heredocs, debugging, exit status, trap.
- Scheduling: cron, systemd timers, at.
- Logs: journalctl, logrotate.
- Processes, monitoring, and basic performance tuning: ps, top, htop, signals, background jobs, vmstat, iostat, sar, nice, renice, taskset, sysctl, tuned, ulimit.
- Host networking: the ip command, connectivity testing, DNS resolution, checking open ports, curl and wget.
- Firewalls with firewalld.
- Disks: mounting, fstab, basic partitioning.
- tmux.
- SSH: configuration, key based auth, the agent, scp, rsync, sshfs, hardening, troubleshooting.

**Labs**

- **2A.** Build a Fedora or RHEL VM. Set the hostname, configure a static IP with nmcli, enable SSH, and disable password authentication so only key based login works.

- **2B.** The core skills grind: navigation, grep, awk, sed, permissions in octal and symbolic form, user and group management, package installation, process management, firewall rules with firewall-cmd. Document every command.

- **2C.** Write a bash health check script that takes a service name as an argument, checks whether it is running, logs the result with a timestamp, and exits with a correct code. Functions, conditionals, loops, proper quoting. Schedule it with cron.

- **2D.** Rewrite the same thing as a systemd unit plus timer. Enable it, confirm it fires, read its output with journalctl. Then explain in three sentences why you would choose a timer over cron, or the other way round.

- **2E.** A performance triage: given a VM that is "slow", identify whether the bottleneck is CPU, memory, disk, or network, using only command line tools, and write up the diagnostic path you took. There is a deliberate answer, and there are three deliberate red herrings.

---
## Module 3: Networking Fundamentals

**Theory**

- The OSI model, restricted to the layers a delivery engineer actually touches (L3 to L7), plus the habit of diagnosing bottom to top.
- TCP/IP and how it maps to OSI.
- TCP versus UDP, the three way handshake, ports, sockets, common service ports.
- Connection states: ESTABLISHED, TIME_WAIT, CLOSE_WAIT, and what port exhaustion looks like when it bites you.
- Routing: routing tables, default gateway, static routes, a conceptual look at dynamic routing.
- DNS records: A, AAAA, CNAME, MX, NS, TXT, PTR. TTL management. Split horizon DNS.
- Load balancing: L4 versus L7, round robin, weighted, least connections, IP hash, sticky sessions, health checks.
- Firewalls and security groups: stateful versus stateless, default deny, firewalld zones, AWS security groups, NACLs, iptables basics.
- DHCP, and why address assignment matters even for containers and VMs.
- TLS and HTTPS: the handshake, certificates, CAs and chains, SNI, TLS configuration in Nginx.
- NAT, private versus public addressing, CIDR.
- Subnetting: masks, usable host calculations, and why real infrastructure uses several small subnets instead of one large one.
- NAT gateways, and how a private subnet gets outbound internet without being reachable from outside.
- Special ranges: loopback, link local, default route, broadcast.
- The mistakes that actually happen: overlapping CIDRs, undersized subnets, skipping the bottom up diagnostic order, ignoring TTL during a planned cutover, and firewall rules written wide "just for now".

**Labs**

- **3A.** Diagnose a deliberately broken DNS and routing scenario with ping, traceroute, ss, and dig. Document what each command actually told you and in what order you used them.

- **3B.** Given 192.168.1.0/26, calculate the mask, broadcast address, and usable host range. Then design a three subnet VPC style layout: 10.0.0.0/16 split into a public web tier, an app tier, and a database tier. Keep this on paper. You will build it for real in Module 8 and compare.

- **3C.** Two VMs on different subnets, connected with static routes. Show `ip route` before and after.

---
## Module 4: Git, GitHub, and Team Engineering Workflows

**Theory**

- Why distributed version control is a mental model, not just a history log.
- Branching strategies: Git Flow, trunk based development, feature branching, and the trade offs at different team sizes.
- Pull requests and code review: what makes a review useful rather than a rubber stamp. This section matters more every year because reviewing generated code is becoming the majority of the job.
- Conventional commits, and the payoff: automated semantic versioning, automated changelogs, automated releases. We do not enforce a commit format as bureaucracy. We enforce it, and then we cash it in in lab 4C.
- Pre commit hooks: catching problems on the developer machine before a pipeline ever sees them.
- Signed commits and branch protection as baseline hygiene.
- Issue tracking and traceability: epics, stories, sprints, boards, and following one feature from backlog to production. We use GitHub Issues and GitHub Projects because they are free, already in your workflow, and integrate with everything else here. Jira is described so that you recognise it in a job, but you will not be asked to run one.

**Labs**

- **4A.** The full cycle across two clones of the same repo: stage, commit, branch, cause a merge conflict on purpose, resolve it.

- **4B.** log, diff, stash, rebase, revert, reset. Then demonstrate clearly, with evidence, the difference between `reset` (rewrites history, destructive on a shared branch) and `revert` (safe on a shared branch). Explain when you would use each, and what you would say to a colleague who just force pushed to main.

- **4C.** Set up a real repo: sane `.gitignore`, pre commit hooks (trailing whitespace, YAML validity, secrets scan), branch protection requiring one review and passing checks, conventional commits enforced with commitlint. **Then wire up semantic release or release please so that merging a `feat:` commit automatically bumps the version and writes the changelog.** That last step is the point of the whole lab.

- **4D.** Build a project board, write an epic with user stories under it, start a sprint, commit a change referencing the issue, open a PR, confirm it links back, and watch the issue close on merge.

---
## Module 5: Web Servers, Applications, and Tests

**Theory**

- Web server versus application server, and where each sits.
- Apache HTTP Server: MPM models, prefork versus event, virtual hosts, mod_proxy.
- Nginx: event driven architecture, reverse proxying, upstream load balancing.
- TLS termination, and where it makes sense to terminate: load balancer, reverse proxy, or the app.
- What makes an application friendly to automated delivery: config from the environment, testable units, repeatable builds.
- The parts of the twelve factor model that matter day to day, and the parts that are dated.
- **Testing strategy, and this is not a footnote.** The test pyramid: many fast unit tests, fewer integration tests, very few end to end tests. What each layer catches and what each layer costs you in pipeline minutes. Contract testing between services. Test data management, and why "it passed locally" usually means "it used my local database". Flaky tests: why one flaky test poisons an entire team's trust in the pipeline, and why quarantining a flaky test is a real engineering decision rather than an admission of defeat.
- **Pipeline speed as a feature.** A test suite that takes forty minutes is a test suite people learn to skip. Caching, parallelism, and what to run on every commit versus what to run nightly.

**Labs**

- **5A.** Apache: two named virtual hosts (a static site and a Python app via WSGI), HTTPS with a self signed certificate, customised access and error log formats.

- **5B.** Nginx: static site, reverse proxy to a backend, then an upstream block round robining across two backend instances.

- **5C.** Build the application that carries through the rest of the program. A small Python API (FastAPI or Flask) with a health endpoint, a metrics endpoint, and at least one real feature endpoint. Config read entirely from environment variables, no hardcoded credentials anywhere, connected to a real database.

- **5D.** Write its test suite properly: unit tests for the business logic, at least one integration test that talks to a real database in a container, and a deliberate flaky test that you then diagnose and fix. Measure and record the total suite runtime, because you will be asked to keep it under control for the rest of the program.

- **5E.** Add a database migration tool (Alembic or equivalent) and commit the first migration. This looks like housekeeping now. In Module 15, it becomes the difference between a rollback that works and a rollback that lies to you.

---
## Module 6: Containers with Docker and Podman

**Theory**

- What containers actually solve: environment parity, dependency isolation, fast startup.
- Containers versus VMs: resource sharing, startup time, isolation trade offs.
- OCI standards: image spec, runtime spec, distribution spec, and why portability depends on them.
- Image layering: union filesystems, layer caching, and why layer order changes your build time.
- Multi stage builds, separating build dependencies from the runtime image.
- Docker's architecture: daemon, CLI, containerd, runc.
- Podman's architecture: daemonless, rootless by default, cgroups v2, drop in Docker CLI compatibility.
- Running as root in Docker versus rootless in Podman, and why this is a real security control rather than a preference.
- **Image scanning with Trivy, introduced here properly.** What a CVE is, what a CVSS score means and does not mean, why base image age is the single biggest lever on your vulnerability count, and why "critical" in a scanner is not the same as "exploitable in your context". Trivy comes back for infrastructure scanning in Module 9 and pipeline gating in Module 19, and it is taught here first so that neither of those is a forward reference.

**Labs**

- **6A.** Dockerfile for the API from Module 5. Build, run, inspect. Use a `.dockerignore` so the build context stays clean.

- **6B.** Rewrite it as a multi stage build. Compare image size and Trivy CVE count before and after, and explain which of the removed CVEs were ever actually reachable from your code.

- **6C.** Run the same image with Podman as a non root user and prove it is genuinely rootless. Use `podman generate kube` to produce a Kubernetes style manifest and keep the output. You will use it in Module 11.

- **6D.** Compose file for the API and its database: named volumes for persistence, env file for credentials. Bring it up with `docker compose`, verify, then repeat with `podman compose`.

- **6E.** Tag and push the image to your registry by hand once, so the mechanics are familiar before Module 7 automates the same push.

---
## Module 7: Continuous Integration

**Theory**

- GitHub Actions vocabulary: workflow, event, job, step, runner, secrets, environments.
- Reusable workflows and composite actions.
- Matrix builds.
- Environments and manual approval gates.
- Self hosted runners, and when hosted runners fall short (air gapped, GPU, very large builds).
- **OIDC based cloud authentication.** Long lived AWS keys sitting in CI secrets are a standing liability that will outlive the employee who created them. OIDC federation lets a workflow assume a scoped, short lived role for one run, with nothing stored anywhere. This is taught here as the *default*, not as an advanced upgrade, and you will never store a static cloud key in this program.
- Make the Makefile a build wrapper, so `make test` behaves identically from a laptop, from GitHub Actions, and from Jenkins.
- Artifact versioning: semantic versioning, snapshot versus release, and why pinning matters as soon as anything else depends on you.
- Caching and pipeline cost: what to cache, what not to, and how to read the minutes bill.

**Labs**

- **7A.** First workflow: checkout, install, run tests, badge on the repo.

- **7B.** Extend to a matrix across three Python versions.

- **7C.** Makefile with `install`, `test`, `lint`, `build`, `push`, `deploy`. The pipeline calls make targets, not inline shell.

- **7D.** Add a real Docker build and push, publishing the image to your registry.

- **7E.** Extract the test job into a reusable workflow and call it from a second repository to prove it really is reusable.

- **7F. The broken pipeline.** You are handed a pipeline with four planted faults: a misreferenced secret, a wrong image tag, a misconfigured trigger, and a caching bug that makes tests pass when they should fail. Fix all four under time pressure and write up the diagnostic process, not just the fix. This is closer to real on call work than anything else in Course 1, and it is the model for both practical checkpoints.
  
---
---
# DVP 201: Cloud Native Infrastructure and Delivery

**14 weeks.**

| Week | Module | Focus | Deliverable |
|---|---|---|---|
| 1 | 8 | AWS, IAM, cost guardrails | Labs 8A, 8B, 8C |
| 2 | 8 | VPC, EC2, S3 | Labs 8D, 8E |
| 3 | 9 | Terraform: state, workflow, variables | Labs 9A, 9B, 9C |
| 4 | 9 | Terraform: modules, drift, scanning, cost | Labs 9D to 9G |
| 5 | 10 | Ansible: inventory, playbooks, idempotency | Labs 10A, 10B |
| 6 | 10 / 11 | Ansible roles and dynamic inventory. Kubernetes begins | Labs 10C, 10D. **Checkpoint 2.1** |
| 7 | 11 | Kubernetes: objects, services, probes, config | Labs 11A to 11C |
| 8 | 11 | Kubernetes: ingress, Gateway API, Helm, Kustomize, EKS | Labs 11D to 11H |
| 9 | 12 | Kubernetes in production: RBAC, NetworkPolicy, PSA, storage | Labs 12A to 12D |
| 10 | 12 | Autoscaling and right sizing | Lab 12E |
| 11 | 13 | Observability: Prometheus, PromQL, Node Exporter, OTel | Labs 13A, 13B |
| 12 | 13 | Grafana, Alertmanager, tracing, structured logs | Labs 13C to 13E |
| 13 | 14 | GitOps with ArgoCD, OIDC federation, secrets into the cluster | Labs 14A to 14D |
| 14 | 15 | Progressive delivery, feature flags, safe migrations | Labs 15A to 15D. **Checkpoint 2.2** |

Note the ordering change from most curricula: **observability comes before progressive delivery.** You cannot do metric driven rollback without metrics, and teaching it the other way round forces an awkward "install just enough Prometheus" patch that nobody learns anything from.

---
## Module 8: Cloud Fundamentals and Cost Guardrails on AWS

**Theory**

- Cloud service models (IaaS, PaaS, SaaS) and where each maps to a real AWS service.
- Global infrastructure: regions, availability zones, local zones.
- IAM: users, groups, roles, policies, with least privilege as a default rather than an afterthought.
- VPC: public and private subnets, internet gateway, NAT gateway, route tables, security groups, NACLs.
- EC2: AMIs, instance types, key pairs, instance profiles, user data.
- S3: buckets, object storage, bucket policies, versioning, lifecycle rules.
- **Cost, taken seriously.** What is actually a free tier and what only looks like it? Why a NAT gateway is the most common surprise on a student bill. How to read Cost Explorer. What "destroy your lab" means as a habit rather than a chore.

**Labs**

- **8A. The billing lab, and it comes first.** Set an AWS Budget. Create a billing alarm at 10 USD and a hard alarm at 50 USD, routed to an email you actually read. Then deliberately trip the low alarm and prove it fired. You do not proceed to 8B until this is done and evidenced.

- **8B.** Launch an EC2 instance, install Nginx, confirm it serves traffic, and tear it down. Take a screenshot of the empty console.

- **8C.** IAM: build a user with no permissions, attach a narrow S3 read only policy, and prove the boundary holds by trying something you should not be able to do. Then build an IAM role for EC2 with S3 read access, attach it to an instance, and confirm the instance can read S3 with no access keys at all. Write two sentences on why the second approach is strictly better.

- **8D.** Build a real VPC: 10.0.0.0/16, public subnet 10.0.1.0/24, private subnet 10.0.2.0/24, internet gateway, NAT gateway. One EC2 in each. Prove the private instance can reach the internet outbound but cannot be reached from outside. Compare it to the paper design from lab 3B. **Then destroy the NAT gateway the same day, and say in your write up what it would have cost you if you had not.**

- **8E.** S3: versioning, a lifecycle rule, and a bucket policy. Break the bucket policy on purpose, observe the failure mode, and fix it.

---
## Module 9: Infrastructure as Code with Terraform and OpenTofu

**Theory**

- Declarative infrastructure versus imperative scripting. Desired state as the core model.
- State: what it tracks, why losing it ruins your week, and why it must never live in Git.
- The workflow: init, plan, apply, destroy. And the habit: read the plan. Every time. Especially when an assistant wrote the code.
- State locking with DynamoDB.
- Workspaces and environment isolation without duplication.
- Modules as the unit of reuse: local, registry, and Git sources.
- **Licensing, told straight.** HashiCorp moved every product, Terraform included, from the open source MPL 2.0 to the Business Source License in August 2023. BUSL is source available, not open source: you can read and use it, but not build a competing hosted service on it. OpenTofu is the community fork of the last MPL version, now under the Linux Foundation, and it is a drop in replacement for essentially everything you will do here. IBM completed its acquisition of HashiCorp in 2025, and Terraform's license did not revert. You will meet both names in the field, and you should know which is which and why the split happened. The same story repeats with Vault and OpenBao in Module 19, and it is the same lesson both times: know the license of the thing you are betting your platform on.

**Labs**

- **9A.** Provision an EC2 instance and a security group. Plan, apply, verify in the console, destroy.

- **9B.** Parameterise instance type and region with variables. Add an output printing the public IP.

- **9C.** Move state into S3 with DynamoDB locking. Then run two applies at once and watch the lock block one of them.

- **9D.** Refactor into a reusable module. Call it twice with different inputs: one web server, one build agent.

- **9E.** Run Infracost against the configuration, read the estimate, and wire it into a pull request as an automatic comment. Then make a change that triples the cost and watch the comment catch it.

- **9F. Drift, the real version.** Provision a security group with Terraform. Introduce drift by changing it in the AWS console. Catch it with `terraform plan` and correct it with `terraform apply`. Compare directly to lab 1C and write two paragraphs on what tooling bought you.

- **9G.** Add infrastructure scanning to the pipeline with Trivy's configuration scanning mode (the same Trivy you learned in Module 6), or Checkov as an alternative. Fix at least one real finding. Note for the record that tfsec, which used to be the default choice here, was folded into Trivy in 2024 and no longer receives new checks.

---
## Module 10: Configuration Management with Ansible

**Theory**

- Architecture: control node, managed nodes, agentless SSH execution.
- Inventory, static and dynamic, including the AWS EC2 plugin.
- Idempotency, and how to actually verify it: run it twice, and the second run changes nothing.
- Ansible next to Terraform rather than against it. One provisions infrastructure, the other converges configuration state.
- Jinja2 templating: variables, filters, conditionals.
- Ansible Vault, encrypting secrets at rest in the repository.
- Roles, the standard directory layout, and Galaxy.

**Labs**

- **10A.** Install Ansible on a control node, write a static inventory with `webservers` and `dbservers` groups, and run ad hoc commands (ping, command, service) before writing a single playbook, so that the gap between a one off command and a repeatable playbook is something you feel rather than read.

- **10B.** Write a playbook that installs and configures Nginx and deploys the Python API from Module 5 as a systemd service on a VM. Include a handler that restarts the service only on a genuine config change. Encrypt the database password with Ansible Vault. Run it twice and prove the second run is a no op.

- **10C.** Convert it into a proper role: tasks, handlers, templates, defaults. Generate the virtual host config from a Jinja2 template.

- **10D.** Terraform provisions two tagged EC2 instances. The AWS EC2 dynamic inventory plugin discovers them. Your role configures them. One exercise, and the Terraform to Ansible boundary stops being theory.

---
## Module 11: Kubernetes Fundamentals

**Theory**

- Control plane: API server, etcd, scheduler, controller manager.
- Worker node: kubelet, kube proxy, container runtime.
- Core objects: Pod, ReplicaSet, Deployment, StatefulSet, DaemonSet, Job, CronJob.
- Services: ClusterIP, NodePort, LoadBalancer, ExternalName.
- **Ingress and Gateway API.** Ingress is what you will find in every existing cluster, and it is effectively frozen. Gateway API is its GA successor, with a proper role split between cluster operator and application developer, and it is what new work should use. You learn both, and you learn which one you are looking at.
- Resource requests and limits, and why a production workload without them is a noisy neighbour waiting to happen.
- Liveness, readiness, and startup probes, because Kubernetes cannot self heal what it cannot detect.
- ConfigMaps and Secrets, and the flat truth that a Kubernetes Secret is base64, not encryption. Module 14 deals with the consequences.
- Persistent volumes, PVCs, storage classes.
- Rolling updates and rollback.
- RBAC: ServiceAccounts, Roles, ClusterRoles, RoleBindings.
- Cluster DNS: how CoreDNS resolves service names, and how to debug resolution from inside a pod.
- Managed Kubernetes on EKS, and why almost nobody builds their own control plane on AWS anymore.

**Labs**

- **11A.** Local cluster with kind (or k3d on 8 GB). Apply a deployment, scale it, expose it, update the image, watch the rolling update, roll it back.

- **11B.** Add liveness and readiness probes and resource limits. Kill the process inside a pod and watch Kubernetes bring it back. Then set the liveness probe wrong on purpose and watch it kill a healthy pod in a loop, which is a failure mode you will meet in the wild.

- **11C.** ConfigMap and Secret wired into a pod spec. Apply your `podman generate kube` output from lab 6C with kubectl and compare it to the manifests you have been writing by hand.

- **11D.** Install an ingress controller, route two paths to two services. Then do the same thing again with Gateway API and an HTTPRoute, and write up what the second model gives you that the first does not.

- **11E.** Exec into a debug pod, use nslookup and dig against a service's cluster DNS name, and confirm how CoreDNS resolution actually works.

- **11F.** Helm: deploy a public chart, then write a small chart for your own application. Kustomize: a base for the same app with a dev overlay and a prod overlay. Apply each and explain when you would reach for which.

- **11G.** Provision a real EKS cluster with Terraform and deploy the same application, so that the local cluster and the cloud cluster feel like two versions of one skill rather than two skills. **Destroy it at the end of the session.**

- **11H. Optional, no marks.** The Red Hat Developer sandbox, OpenShift web console, the `oc` CLI, and a comparison of an OpenShift Route to the Ingress from 11D. Fuller treatment lives in the elective track.

---
## Module 12: Kubernetes in Production

Everything in Module 11 gets you a running application. Everything in Module 12 is what stands between that and a cluster you would actually let a customer near.

**Theory**

- **RBAC in earnest.** Least privilege for a CI/CD service account. Why `cluster-admin` in a pipeline is the same mistake as a static AWS key, wearing a different hat.
- **Pod Security Admission.** The built in, free baseline. Privileged, baseline, and restricted. You learn this *before* Kyverno in Course 3, because you should know what the platform already gives you before you install a policy engine on top of it.
- **NetworkPolicy.** Default deny east west traffic. This is the free, built in, layer 3 and 4 control that is the actual first step of zero trust, and it is the thing most teams skip on their way to buying a service mesh. CNI plugins and why NetworkPolicy needs one that supports it.
- Namespaces, ResourceQuotas, and LimitRanges as a multi tenancy story.
- Storage in practice: storage classes, dynamic provisioning, volume expansion, and why a StatefulSet is not just a Deployment with a nicer name.
- **Autoscaling.** Horizontal Pod Autoscaler on CPU and on custom metrics. Vertical Pod Autoscaler and why it fights with HPA. Cluster Autoscaler versus Karpenter for node level scaling. The relationship between requests, limits, and what the autoscaler can actually see.

**Labs**

- **12A.** Create a ServiceAccount for a CI/CD pipeline, bound to a Role permitting only get, list, and update on Deployments in the app namespace. Prove it cannot read Secrets. Then try to make it read Secrets and show the exact error.

- **12B.** Apply Pod Security Admission at the `restricted` level to a namespace. Watch your own application get rejected. Fix the application (non root user, dropped capabilities, no privilege escalation) until it is admitted.

- **12C.** Write a default deny NetworkPolicy for a namespace, watch everything break, then open exactly the paths that are needed and no more. This lab is uncomfortable, and it is supposed to be.

- **12D.** ResourceQuota and LimitRange on a namespace. Try to exceed both. Read the errors.

- **12E.** Configure an HPA on the application against the request rate. Load test it and watch it scale. Then collect real utilisation data, right size the requests and limits, and quantify the monthly saving with Infracost. This is the lab that connects "I set some numbers in a YAML file" to "I saved the company money", and it is the one to put on your CV.

---
## Module 13: Observability Built on Open Standards

**Theory**

- Metrics, logs, and traces: what each answers that the other two cannot.
- OpenTelemetry is the vendor neutral standard that ties all three together, so you are never locked into one vendor's instrumentation format. Instrument once, export anywhere.
- The Prometheus data model: time series, labels, counters, gauges, histograms, summaries. Node Exporter for host metrics.
- PromQL, starting with the three queries you will actually reach for: `rate`, `increase`, `histogram_quantile`.
- Alertmanager: routing, grouping, inhibition, silencing. And alert fatigue, which is the failure mode that kills more monitoring stacks than any technical problem.
- Grafana: dashboards, variables, annotations, alert rules.
- Structured logging, and why JSON logs make everything downstream trivial.
- Cardinality, and how one badly chosen label (a user ID, a request ID) can take down your Prometheus. This is the single most common self inflicted observability injury.

**Labs**

- **13A.** Install Prometheus and Node Exporter into the cluster. Confirm all targets are up. Instrument the application with OpenTelemetry, exporting metrics to Prometheus and traces to Jaeger from the same instrumentation code.

- **13B.** Write PromQL by hand until it stops being frightening: request rate, error rate, p95 latency from a histogram. Then deliberately add a high cardinality label, watch Prometheus memory climb, and remove it.

- **13C.** Build a Grafana dashboard with real panels: CPU, memory, HTTP request rate, HTTP error rate, p95 latency.

- **13D.** Write an alert that fires on a real threshold, route it through Alertmanager to a chat channel, and confirm the notification arrives. Then write a *bad* alert that fires constantly, live with it for a day, and write two sentences on what alert fatigue does to an on call engineer.

- **13E.** Slow down a database query on purpose. Trace the same problem through a metric, a Jaeger span, and a log line. Write up how much harder this would have been with only one of the three.

---
## Module 14: Continuous Delivery, GitOps, and Getting Secrets Into a Cluster

**Theory**

- Push based delivery (the CI/CD pattern from Course 1) set next to pull based GitOps.
- ArgoCD: the Application resource, sync policies, health status, self healing, drift detection at the cluster level.
- OIDC federation as the modern replacement for long lived cloud keys sitting quietly in CI secrets.
- **The GitOps secrets problem, and this is not optional.** GitOps says the desired state of the cluster lives in Git. Security says credentials must never live in Git. Both are correct, and a curriculum that teaches ArgoCD and then goes quiet has left you with a broken system. The three real answers: Sealed Secrets (encrypt into Git, decrypt in cluster), External Secrets Operator (a reference in Git, the value in a real secret store), and the Vault Agent Injector or Secrets Store CSI driver (inject at pod start). You build one of them, and you can explain the trade offs of the other two.

**Labs**

- **14A.** Extend the pipeline from Course 1 with a real deploy stage that applies manifests to the EKS cluster.

- **14B.** Set up OIDC federation between GitHub and AWS. Replace the static access keys with a scoped, short lived role. Delete the old keys from secrets entirely. Write a short note comparing the blast radius of a leaked static key against a leaked short lived OIDC token, and be specific about the timelines.

- **14C.** Install ArgoCD, point it at the manifests repo. Change something in Git and watch it sync. Change something by hand in the cluster and watch ArgoCD revert it.

- **14D.** Now put a secret into that GitOps flow without putting the secret into Git. Install External Secrets Operator, back it with AWS Secrets Manager, and have ArgoCD sync an ExternalSecret that resolves to a real Secret in the cluster. Prove the secret value appears nowhere in your repository, including in the history. The correct way to prove this is `git log -p -S '<the secret value>' --all`, which searches every commit on every branch for that string. An empty result is your proof.

---
## Module 15: Progressive Delivery, Feature Flags, and Safe Migrations

**Theory**

- Canary and blue green as alternatives to a plain rolling update.
- Automated rollback driven by a real metric rather than a person staring at a dashboard. You already have the metrics from Module 13, which is why this module is in the right place.
- **Feature flags, and why infrastructure is only half the story.** A canary controls which *version* of the code is running. A feature flag controls whether a *behaviour* is switched on, for whom, and it can be turned off in a second without a deployment at all. Deploy and release are two different events, and the moment you internalise that, half of progressive delivery gets easier. Flags are cheaper than canaries; they work for things a canary cannot help with, and they carry their own cost: flag debt is real, and a flag you forgot to remove is a bug waiting for a quiet Sunday.
- **Database migrations, and the rollback that lies to you.** Here is the thing most courses never tell you. You set up a beautiful automated canary rollback. You ship a bad version. The rollback fires, the pods go back to the old image, the dashboard goes green, and your application is still broken because the deployment ran a migration that dropped a column, and the old code is now querying a column that no longer exists. Your rollback rolled back the code and not the data. It cannot roll back the data. The fix is not a better rollback tool, it is the expand and contract pattern: every schema change is split into a backward compatible expand (add the new column, write to both, read from the old), a deploy, and a contract (stop writing the old, drop it) that happens in a *later* release once you are certain you will not need to go back. Destructive migrations make a deploy one way, and a one way deploy is not a deploy you can canary. This single idea is why the migration tool went into your app back in lab 5E.

**Labs**

- **15A.** Install Argo Rollouts. Convert the deployment into a canary backed by an AnalysisTemplate that queries Prometheus for HTTP error rate. Ship a version that is broken on purpose. Watch it get caught and rolled back before promotion completes.

- **15B.** Configure a second rollout using blue green: a full parallel environment, an instant cutover, manual promotion, and a rollback by aborting. Write a short note on when you would reach for blue green over canary.

- **15C.** Add a feature flag (OpenFeature with a simple provider, or a flag service) to the application. Ship the code dark, behind the flag, in a normal deploy that changes nothing for users. Then turn it on for ten percent of traffic without deploying anything at all. Then turn it off in under five seconds because something looked wrong. Compare this experience to Lab 15A honestly.

- **15D. The rollback that lies.** Write a migration that drops a column. Deploy it with the canary from 15A. Roll back. Watch the application stay broken even though every dashboard says the rollback succeeded, and understand exactly why. Then redo the whole thing as expand and contract, and demonstrate a rollback that genuinely restores service. This lab is the most important one in Course 2, and it is deliberately the last.

---
---
# DVP 301: Reliability, Security, Platform, and AI Driven Operations

**14 weeks. The capstone starts in Week 1, not Week 11.**

| Week | Module | Focus |
|---|---|---|
| 1 | 16 | SRE: SLIs, SLOs, error budgets. **Capstone kickoff and proposal due.** |
| 2 | 16 / 17 | On call, incident response, blameless postmortems. Chaos engineering |
| 3 | 18 | Disaster recovery and business continuity |
| 4 | 19 | DevSecOps: secrets, Vault and OpenBao, SAST, SCA |
| 5 | 19 | Image scanning, secrets scanning, dependency updates. **Capstone checkpoint 1** |
| 6 | 20 | Supply chain security and policy as code |
| 7 | 21 | Service mesh and advanced traffic management |
| 8 | 22 | Multi cloud, serverless, and FinOps |
| 9 | 23 | Platform engineering. **Capstone checkpoint 2** |
| 10 | 24 | AI in modern DevOps and platform work |
| 11 to 13 | 25 | Capstone build, with a weekly review slot |
| 14 | 25 | Capstone presentations and live defenses |

---
## Module 16: SRE Practices and Incident Response

**Theory**

- SLIs, SLOs, and error budgets as an engineering discipline rather than a slogan. What an error budget is *for*: it is a negotiated permission to ship, and when it is exhausted, the negotiation changes.
- On call: rotation structure, escalation paths, severity levels, and who actually has the authority to declare an incident.
- Incident command: the incident commander, the communications lead, the scribe. Why one person doing all three at 3 am is how a one hour incident becomes a four hour one.
- Incident communication: status pages, stakeholder updates, and the discipline of saying "we are investigating" every twenty minutes even when there is nothing new.
- Blameless postmortems, and why blame produces quieter engineers rather than better systems.
- Basic capacity planning.

**Labs**

- **16A.** Define real SLOs for your service and instrument the matching SLIs in Prometheus. Build the error budget burn rate alert.

- **16B.** Connect an alert to a real paging tool and walk the full path: alert, page, acknowledgement, escalation on no ack.

- **16C. The incident simulation.** In pairs. One student breaks the other's cluster in a way agreed with the instructor. The other runs the incident: declares severity, communicates status on a schedule, diagnoses, mitigates, and writes the blameless postmortem afterwards with a timeline, a root cause, and follow up actions. Then swap. You will be asked to narrate one of these out loud in a job interview within a year, and this is where you get the story.

---
## Module 17: Chaos Engineering and Resilience

**Theory**

- Resilience as something tested on purpose rather than hoped for.
- The real difference between a chaos experiment and an outage: a hypothesis, a blast radius, and a stop button.
- What a sensible first blast radius looks like.

**Labs**

- **17A.** Install Chaos Mesh (or Litmus). Write the hypothesis down *first*. Run one contained experiment: kill a pod mid request, or add two seconds of latency between the app and its database. Document what recovered automatically, what did not, and what you would change in the deployment or rollout strategy as a result. An experiment where nothing surprising happened is a valid result and should be written up as one.

---
## Module 18: Disaster Recovery and Business Continuity

**Theory**

- RPO and RTO as concrete numbers rather than vague promises. If you cannot state yours in minutes, you do not have one.
- Backup strategies: full, incremental, snapshot. Cost, speed, and recovery complexity trade offs.
- Kubernetes specific DR: etcd backup for the cluster's own state, which is a different problem from Velero backing up namespaces and PVCs.
- The gap between having a backup file and having a proven restore. An untested backup is a rumour.

**Labs**

- **18A.** Set an RTO target *before* you start. Back up the full application namespace with Velero, delete the namespace, restore it, and measure the actual recovery time against your target. If you missed, find the bottleneck (image pull time, PVC bind time, init container ordering) and propose a fix. Write it up as a one page blameless postmortem.

- **18B.** Write a scheduled job that dumps the database regularly and ships it to object storage. Then restore from that dump into a fresh database and prove the data is intact, because a backup you have never restored is not a backup.

---
## Module 19: DevSecOps in Depth

**Theory**

- Shifting security left, in practice rather than as a slogan: catching a vulnerability at commit time costs a fraction of catching it in production.
- The OWASP Top 10 at a working level.
- **Secrets management with Vault, and the OpenBao question.** HashiCorp moved Vault to BUSL 1.1 in August 2023, the same move that produced OpenTofu from Terraform. Vault 1.14 was the last MPL release. OpenBao is the community fork of that version, API compatible, MPL 2.0, governed under the Linux Foundation. Vault is now an IBM product. You learn Vault because it is what you will find in a job, and you learn that OpenBao exists because your organisation may one day have to care about the license. Same story as Module 9, and it is not a coincidence.
- Static analysis (Bandit or equivalent) and software composition analysis (OWASP Dependency Check).
- Container image scanning, base image age, pinned tags, non root users.
- **Dependency update automation.** Scanning tells you that you have a vulnerable dependency. It does nothing to fix it. Renovate or Dependabot is the other half of the job, and a scan without an update pipeline just generates a report nobody reads.
- Secrets scanning across current code *and* full Git history, because deleting a committed key does not remove it from the history.
- Rootless containers as a real security control, connecting back to Podman in Module 6.
- Zero trust as a mental model, and NetworkPolicy (Module 12) as its unglamorous first step, rather than as something you buy.
- Least privilege in CI/CD as a running theme, connecting back to the OIDC pattern in Module 14.

**Labs**

- **19A.** Store a secret in Vault and pull it into a pipeline step, rather than writing it into a workflow file. Then do the same thing against OpenBao and note how little changed.

- **19B.** Add Bandit and a dependency check as pipeline stages that fail the build on high severity findings. Then find a false positive and handle it properly with a documented suppression rather than by turning the check off.

- **19C.** Run Trivy against the application image, find a real critical CVE, fix it (usually by updating the base image), and add Trivy as a pipeline gate that fails on critical.

- **19D.** Run gitleaks against the full Git history and catch a planted credential. Add gitleaks as a pre commit hook *and* as a pipeline step, so a secret that slips past the hook still gets caught. Then run trufflehog against the same repo with a second planted secret, and compare pattern matching against entropy based and verified detection. Say when you would reach for each.

- **19E.** Enable Renovate or Dependabot. Let it open a PR. Review that PR the way you would review any other, merge it, and watch the vulnerability count drop. Then configure it so that patch updates automerge on green CI and majors do not, and justify where you drew that line.

---
## Module 20: Supply Chain Security and Policy as Code

**Theory**

- Real supply chain attacks and why they worked: SolarWinds, the XZ Utils backdoor. And a clear distinction that matters: Log4Shell was a *dependency vulnerability*, a software composition problem, not a supply chain compromise. Different problem, different fix, and people conflate them constantly.
- SBOMs and the two dominant formats, SPDX and CycloneDX.
- Image signing with cosign and keyless signing through Sigstore.
- Admission controllers: how Kubernetes intercepts and validates API requests before they persist, and the difference between a validating webhook that blocks a bad request and a mutating webhook that quietly corrects one.
- Kyverno, policy written as plain Kubernetes resources. OPA Gatekeeper is noted for teams already invested in Rego. And a reminder from Module 12: check what Pod Security Admission already does for free before you install either.
- SLSA, the framework these practices ladder up to, and its concrete levels.

**Labs**

- **20A.** Generate an SBOM for the application image with syft, attach it as a build artifact, then actually use it: find every image in your cluster that contains a given library.

- **20B.** Sign the image with cosign after push. Add a verification step to the pipeline that refuses to deploy anything unsigned. Confirm it by trying to deploy a different, unsigned image and watching it get rejected.

- **20C.** Install Kyverno. Write a policy that blocks privileged pods. Write a second that requires a verified signature before a pod runs in the production namespace, leaving development unrestricted. Then explain which of these two Pod Security Admissions could have done for you without Kyverno at all.

---
## Module 21: Service Mesh and Advanced Traffic Management

**Theory**

- What a mesh adds on top of Kubernetes networking, and what it does not.
- **The architecture question, stated currently.** The sidecar proxy model (one proxy injected next to every pod) is what most existing meshes run and what most documentation describes. It is no longer the only model. Istio's ambient mode removes the per pod sidecar in favour of a shared node level component, and eBPF based approaches such as Cilium's take a different route again. The trade off is resource overhead and upgrade pain against isolation and per pod configurability. You should be able to describe all three and say which problem each is solving.
- Mutual TLS between services, and why encrypting east west traffic matters even inside a cluster you think you trust.
- Traffic shifting as a mechanism that is genuinely different from changing replica counts: a mesh controls where traffic goes regardless of which pods exist, while a rollout controls which pods exist in the first place.
- **Linkerd, and two things you need to know before you recommend it at work.** First, since February 2024, the Linkerd open source project no longer publishes stable release artifacts. The source and the weekly edge releases stay open and free, but stable, backported releases come through Buoyant's enterprise distribution, which is free for organisations under fifty employees and paid above that. This is a real budget conversation, and you should not be surprised by it in a meeting. Second, Linkerd's SMI TrafficSplit resource is deprecated and slated for removal; traffic shifting is now done with Gateway API HTTPRoute and GRPCRoute, which is the same Gateway API you learned in Module 11. We teach the current way. Istio is described because it is what you will see in job postings, and because a course that teaches only the smaller tool is not preparing you for the market.

**Labs**

- **21A.** Install Linkerd, inject it into the application namespace, and confirm traffic is actually encrypted with `linkerd viz`. Then read the mesh's own golden metrics and compare them to what your application was reporting on its own.

- **21B.** Shift ten percent of traffic to a second version using a weighted HTTPRoute (not TrafficSplit, which is deprecated). Then explain in your own words how this differs from what Argo Rollouts did in lab 15A, and when you would want both.

---
## Module 22: Multi Cloud, Serverless, and FinOps

**Theory**

- The five primitives every major cloud shares under different names: identity and access, virtual networking with public and private segmentation, object storage, managed compute, managed relational databases.

| Concept, already learned on AWS | GCP | Azure |
|---|---|---|
| IAM role and policy | IAM role and binding | Managed identity, RBAC role assignment |
| VPC and subnet | VPC network and subnet | Virtual network and subnet |
| S3 | Cloud Storage | Blob Storage |
| EC2 | Compute Engine | Virtual Machines |
| Security group | Firewall rule | Network security group |
| EKS | GKE | AKS |

- Where "the same thing with a different name" breaks down, and it does break down. IAM trust models genuinely differ: AWS has explicit role assumption with trust relationships, GCP has a more implicit project level model. That is a real difference, and flattening it will bite you.
- Where serverless fits next to containers rather than replacing them. Cold starts, execution limits, and the operational things you give up, along with the ones you gain.
- **FinOps at the level a delivery engineer needs.** Tagging and cost allocation. Rightsizing (which you already did in lab 12E). Spot and reserved capacity. The single biggest lever, which is almost always "turn off the thing nobody is using". This is not a FinOps specialisation, and it does not pretend to be.

**Labs**

- **22A.** Deploy one small function to Lambda. Compare the operational experience to the same logic in a container: deploy time, cold start, observability, debugging, cost at ten requests per day and at ten million.

- **22B.** Take your Terraform module from Module 9 and identify, on paper and without writing code, exactly what would have to change to port it to GCP or Azure: provider block, resource names, IAM model. Be specific about which change is trivial and which one is not.

- **22C.** Take the technical rightsizing you did in lab 12E and turn it into a one page memo aimed at a non technical reader, a director of engineering or a CFO. Same data, same number, but the language and the structure are for someone who will not read a Prometheus dashboard. Include the current monthly spend, the proposed monthly spend, the risk of getting it wrong, and one paragraph on how you would validate the change before rolling it out. Translating a technical finding into an audience appropriate document is a distinct skill from producing the finding, and it is the one that decides whether the finding gets acted on.

---
## Module 23: Platform Engineering

**Theory**

- Why platform engineering exists, and the cognitive load problem it solves. The framing here comes from Team Topologies, and the core claim is simple: a product team cannot hold Kubernetes, Terraform, the CI system, the observability stack, the policy engine, and their own domain in their heads at once, and asking them to is how you get shadow IT and a half configured cluster.
- Golden paths and internal developer platforms as a catalogue, not a single tool. A golden path is a paved road, not a fence: the easy way, not the only way.
- Backstage as the leading open source reference implementation.
- Platform as a product: your users are engineers, and if they route around you, you built the wrong thing.
- Why the capstone in this program is, in miniature, exactly what a real platform team hands a new developer on day one.

**Labs**

- **23A.** Explore a public Backstage demo. Map which pieces you have already built (CI templates, Kubernetes manifests, Kyverno policies, Terraform modules) onto what would become software templates in a real catalogue.

- **23B.** Write the day one developer experience for your own project, twice: once with a golden path and once without. Count the steps, count the decisions, count the ways to get it wrong. That difference is the entire value proposition of the discipline, in your own numbers.

---
## Module 24: AI in Modern DevOps and Platform Work

This module gives a proper home to a thread that has been running through the whole program, because AI tools now sit inside nearly every part of a real delivery workflow, and because you have been using them since Week 1 under a disclosure rule you may not have fully understood the reason for until now.

**Theory**

- **The review discipline.** AI assistants write a growing share of code and infrastructure. Generated Terraform can be confident, plausible, well formatted, and wrong in a way that costs money or opens a hole. The habit that has to sit next to the convenience is reading the plan every time and knowing enough to spot what is missing rather than only what is present. This is the skill the market is actually short of.
- **What the data says.** The 2025 DORA research found AI adoption improves throughput and worsens delivery stability: change failure rate and rework rate go the wrong way, at the team level, even as individuals feel faster. AI amplifies the system it lands in. A team with strong tests, real observability, and a working rollback gets faster. A team without them gets faster at breaking things. Everything in the previous 23 modules is the precondition for this module to pay off.
- **AIOps in practice.** Anomaly detection on metrics. Clustering unusual log patterns to catch what a fixed threshold would miss. Predicting scale needs from traffic patterns rather than reacting afterwards. And where each of these quietly fails.
- **Chat driven operations.** A language model that can query real observability data and summarise an incident in plain language. Where that genuinely helps an on call engineer at 3 am, and where it will confidently summarise an incident that is not the one you are having.
- **MLOps from the platform side.** Many delivery teams are now asked to support machine learning workloads. Model versioning. Model serving as just another kind of deployment. GPU scheduling in Kubernetes as an expected skill rather than a niche one.
- **Prompt injection and AI agent security.** Once an assistant has real access to production tools, the tools are the attack surface, and the untrusted input is anything the model reads. The same least privilege thinking you already apply to cloud credentials applies here, and it applies harder, because an agent will act on an instruction it found in a log line if you let it.

**Labs**

- **24A.** Use an AI assistant to draft a Terraform module and a Kubernetes manifest. Then review both the way a senior engineer would, listing every change you would demand and why, *before* applying anything. Then apply it and see what you missed.

- **24B.** Add an automated AI review step to a pull request pipeline. Compare its findings against Bandit and Trivy on the same change. Be specific about what it caught that they did not, and what it hallucinated. Then answer the design question: should this step be allowed to block a merge? Defend your answer.

- **24C.** Build a small script that pulls recent Prometheus data and asks a language model to summarise what changed. Check the summary against what you know actually happened, from lab 16C. Report the failure modes, not just the successes.

- **24D.** Deploy a small model serving workload and request a GPU resource in the pod spec, even without GPU hardware, to understand the request and limit syntax and what the scheduler does when it cannot satisfy it.

- **24E.** Write a threat model for an internal AI assistant with access to your Kubernetes cluster and your team chat. List what it must never be allowed to do unsupervised, and what a prompt injection delivered through a log line or a Jira ticket could achieve if you got the permissions wrong. A pass on this lab requires at least three distinct attack scenarios, each spelling out the specific tool call the assistant would make, the data exfiltration or state change that would result, and the specific least privilege policy (RBAC, tool allowlist, output sanitization) that would prevent it.

---
---
## Module 25: Capstone Project

One student, one complete pipeline. A Git push on your machine triggers a fully automated pipeline that tests, scans, and deploys to a Kubernetes cluster with no manual steps, short lived OIDC credentials instead of static keys, cluster policy enforcing what can run, observability watching the result, and no long lived credentials anywhere.

The capstone starts in **Week 1 of Course 3**, not Week 11. You propose it, you get it approved, you build it incrementally as each module lands, and you present it in Week 14. There are two review checkpoints where it gets looked at and where you find out early that something is wrong, rather than three days before the demo.

---
### Core, and all of it is required

1. **Application.** Health endpoint, metrics endpoint, at least one feature covered by automated tests at two levels (unit and integration), config read entirely from environment variables, and a migration tool with at least one migration.

2. **Version control.** GitHub. Feature branches through pull requests. Main protected. Conventional commits enforced with pre commit, and an automated release that produces a version and a changelog. GitLeaks as a pre commit hook.

3. **Containerisation.** Multi stage, non root Dockerfile. Image pushed to a registry. No credentials anywhere in the image.

4. **CI/CD pipeline**, in this order: checkout, secrets scan, unit tests that halt on failure, integration tests, SAST and dependency scan, image build and push, Trivy scan gating on critical, deploy. All cloud authentication through OIDC federation. **No static AWS keys, anywhere, ever.** Dependency updates automated with Renovate or Dependabot.

5. **Getting secrets into the cluster** without putting them in Git. One of Sealed Secrets, External Secrets Operator, the Vault, or OpenBao injector. You must be able to explain why you chose yours.

6. **Infrastructure as code.** Terraform or OpenTofu provisions the whole environment, reproducible from `apply`, remote state in S3, DynamoDB locking, and a Trivy or Checkov configuration scan in the pipeline.

7. **Configuration management.** Ansible configures the deployment target after provisioning, using dynamic inventory, with idempotent playbooks in the repo.

8. **Kubernetes, hardened.** The application runs on EKS (or on the documented free path). RBAC is scoped to the least privilege for the pipeline service account. Pod Security Admission at `restricted`. A default deny NetworkPolicy with only the required paths opened. Requests, limits, and an HPA.

9. **Observability.** Prometheus and Grafana with a dashboard showing CPU, memory, request rate, error rate, and p95 latency. One working Alertmanager rule that has actually fired. Jaeger traces the application through OpenTelemetry.

10. **A safe schema change.** Demonstrate one migration shipped using expand and contract, and demonstrate that you can roll the deployment back afterwards with the application still working. This is a core requirement and not an elective because it is the one everybody gets wrong.

11. **Platform catalogue entry.** A README describing the whole thing as a golden path a new developer could follow on day one.

---
### Electives: choose two

You pick two of the following and do them properly. You do not do all five badly. This is a deliberate change from the previous version of this syllabus, where the capstone asked one student for a quarter of work from a platform team, and got, predictably, a lot of things half done.

- **A. Progressive delivery.** Argo Rollouts canary with an AnalysisTemplate querying Prometheus. A deliberately broken deploy must trigger automatic rollback before promotion. Or the feature flag equivalent, with a documented argument for why flags were the better tool here.

- **B. Supply chain.** SBOM with syft, cosign signing after push, signature verified in the pipeline before deploy, and a Kyverno policy enforcing the same thing at the cluster level so that an unsigned image is rejected at admission.

- **C. Service mesh.** Linkerd installed, namespace injected, mTLS confirmed with `linkerd viz`, and one weighted HTTPRoute traffic shift demonstrated.

- **D. Disaster recovery.** Velero with an S3 backend. One backup, one successful restore, actual RTO measured against a target you set in advance, written up as a one page blameless postmortem.

- **E. AI in the pipeline.** An automated AI review step, with a written evaluation of what it caught that the deterministic tools did not, what it hallucinated, and whether you would let it block a merge.

---
### Deliverables

The repository. A live application at a stable address. A Grafana dashboard screenshot. Evidence for both electives. A short written record of what your AI assistant got right and wrong during the build. A fifteen minute presentation that must include at least one real problem you hit and how you got out of it. And a ten minute live defense where the instructor picks lines from your work and asks you to explain them.

---
### Capstone rubric, out of 100

| | Marks |
|---|---|
| Core components 1 to 11, working and evidenced | 45 |
| The two electives, done properly | 15 |
| Live defense: can you explain your own system | 20 |
| Presentation, including the honest problem story | 10 |
| Write up quality, including the AI record | 10 |

The live defense is worth twice the presentation, on purpose. A polished demo of a system you cannot explain is worth less than a rough system you understand completely, and every hiring manager you will ever meet agrees with that, even if they never say it out loud.

---
---
# DVP 150: Enterprise and Legacy Stack (elective)

**Self paced, roughly 25 hours, 2 credits, graded pass or fail on four submitted labs. Available from Week 8 of DVP 101 onward.**

This exists because a real fraction of jobs, especially in banks, telcos, government, and older enterprises, run on a stack the core course does not teach. Nothing here is dead. It is just not what a greenfield project starts with in 2026, and stuffing it into the core as "optional" content with no hours attached was doing nobody any favours.

**Part 1: Java enterprise (8 hours).** Tomcat: JVM requirements, connector architecture, the Manager app. Maven: the project object model, the build lifecycle, and dependency resolution. Lab: create a Maven servlet project, add a dependency, build with `mvn clean package`, verify the WAR, deploy it to Tomcat.

**Part 2: Jenkins (8 hours).** Controller, agents, executors, workspaces. Declarative versus scripted pipelines. The Jenkinsfile as code in the repo rather than clicks in a UI. Webhook triggering. Ephemeral Docker agents for clean build environments. Lab: install Jenkins, connect a build agent over SSH, create developer and admin roles and prove the boundary holds, and write a Jenkinsfile that invokes the **same make targets** from lab 7C, triggered by a GitHub webhook, running in an ephemeral Docker agent. The point of the make wrapper becomes obvious here: the commands are identical, only the orchestrator changed.

**Part 3: The LAMP path (4 hours).** Build the same idea as the Module 5 application in PHP with MySQL. Then deploy it with the Ansible role from Module 10. Useful if you are heading into a shop that still runs one.

**Part 4: OpenShift and Elastic (5 hours).** OpenShift: how it extends Kubernetes with tighter security defaults, a built in registry, and Routes instead of plain Ingress. Deploy through the web console and the `oc` CLI on the free Red Hat Developer sandbox, and compare the Route to the Ingress from lab 11D. Elastic: install Elasticsearch and Kibana, verify cluster health, ship a log file with Filebeat, write a Logstash pipeline with a grok filter, build a Kibana index pattern filtering on HTTP status. Worth doing if you are heading somewhere that already runs Elastic at scale, which many large enterprises still do.

Students on the Jenkins track may submit a Jenkinsfile in place of the GitHub Actions workflow for the capstone, invoking the same make targets, so the commands are identical.

---
## Certification alignment

None of these are required. The coursework maps closely enough that a motivated graduate can sit them with real confidence rather than starting from zero. Names and exam codes were checked against each certifying body's own site, and you should check them again yourself, because they change.

| After | Reasonable targets |
|---|---|
| **DVP 101** | Linux Foundation Certified System Administrator (LFCS) or CompTIA Linux+ (XK0-006) as the Linux specific route. GitHub Foundations as an optional lighter target that maps directly onto Module 4. |
| **DVP 201** | Kubernetes and Cloud Native Associate (KCNA) as an early Kubernetes checkpoint. HashiCorp Certified: Terraform Associate. Certified Kubernetes Administrator (CKA). Certified Kubernetes Application Developer (CKAD). AWS Certified Solutions Architect Associate. Along the way: Certified GitOps Associate (CGOA), Certified Argo Project Associate (CAPA), Prometheus Certified Associate (PCA), OpenTelemetry Certified Associate (OTCA). |
| **DVP 301** | AWS Certified DevOps Engineer Professional as a stretch. Certified Kubernetes Security Specialist (CKS) as an advanced stretch. Kubernetes and Cloud Native Security Associate (KCSA). Kyverno Certified Associate (KCA). Certified Backstage Associate (CBA). Cloud Native Platform Engineer (CNPE) as a longer term target. |

Two notes. KCNA, KCSA, CKA, CKAD, and CKS together make up what the Linux Foundation calls the Kubestronaut track, which is a decent long term goal if you want one badge that spans the ecosystem. And on the Terraform Associate: you are certifying on a product that is now BUSL licensed and owned by IBM, which does not make the certification less useful, but you should hold both facts in your head at once.

---
## Reading

Not optional, not long, and each one is here because it does something this syllabus cannot do in a paragraph.

- **Accelerate**, Forsgren, Humble, Kim. The research behind DORA. Read it before you quote a DORA metric at anyone.

- **The DORA Accelerate State of DevOps reports (2024 and 2025)** and the current metrics guide at dora.dev. Free, current, and the empirical basis for Module 24. The AI findings live in the 2024 and 2025 reports as major sections rather than a single standalone document, so cite the report and the year.

- **Site Reliability Engineering** and **The Site Reliability Workbook**, Google. Free online. Chapters 3, 4, and 15 are the ones that matter most for Module 16.

- **Team Topologies**, Skelton and Pais. The source of the cognitive load argument in Module 23.

- **Kubernetes Up and Running**, and **Terraform Up and Running**, Brikman. Reference, not cover to cover.

---
## What this curriculum leaves out on purpose

No curriculum covers everything, and pretending otherwise makes it worse, not better.

It does not go deep on **MLOps**. Module 24 gives you the platform side, which is what a delivery engineer is actually asked for. Training and evaluating models is a different discipline.

It does not go deep on **Windows Server administration**, **mobile CI/CD**, or **game engine build pipelines**. Different specialisations, and pretending otherwise would just make this document longer.

It touches **FinOps** at the level a delivery engineer needs and no further. A dedicated cost engineer needs far more.

It does not build toward an **offensive security** certification path. That is a genuinely different career direction from this one, and the DevSecOps here is defensive by design.

It does not teach **Istio hands on**. You get the concepts, the architectural comparison, and the vocabulary, but the hands on mesh is Linkerd because it can be learned in a week rather than a term. If you land somewhere running Istio, you will not be lost, but you will have reading to do, and this is an honest trade rather than a hidden one.

---
## Appendix A: Tool reference

| Area | Tools | Notes |
|---|---|---|
| Virtualization | VirtualBox, VMware Workstation Pro | Both free for this use |
| Linux | Fedora, RHEL, or Ubuntu | RHEL family preferred |
| Web servers | Apache, Nginx | Tomcat lives in the elective |
| Version control | Git, GitHub | pre commit, commitlint, semantic-release |
| Issue tracking | GitHub Issues and Projects | Jira described, not required |
| CI/CD | GitHub Actions | Matrix builds, reusable workflows, OIDC federation |
| Build wrapper | Make | Identical commands across every orchestrator |
| Testing | pytest, testcontainers | Unit, integration, and one deliberate flake |
| Migrations | Alembic or equivalent | Expand and contract, taught properly |
| Containers | Docker, Podman | Compose, rootless, multi stage |
| Config management | Ansible | Dynamic inventory, Vault, Jinja2 |
| IaC | Terraform, OpenTofu | Remote state, modules, Infracost, Trivy or Checkov |
| Cloud | AWS: EC2, S3, IAM, VPC, EKS, Lambda, DynamoDB, Secrets Manager | GCP and Azure conceptually |
| Cloud auth | OIDC federation | Never a static key |
| Orchestration | Kubernetes, kind or k3d, EKS, Helm, Kustomize | Ingress and Gateway API |
| Cluster security | RBAC, Pod Security Admission, NetworkPolicy | Before you install a policy engine |
| Autoscaling | HPA, Cluster Autoscaler, Karpenter | With real right sizing data |
| GitOps | ArgoCD | Plus External Secrets Operator, because secrets do not go in Git |
| Progressive delivery | Argo Rollouts, OpenFeature | Canary, blue green, and flags |
| Service mesh | Linkerd | Gateway API HTTPRoute, not deprecated TrafficSplit. Istio for awareness |
| Policy as code | Kyverno | OPA Gatekeeper noted |
| Supply chain | syft, cosign, Sigstore | SBOM, signing, verification |
| Observability | Prometheus, Alertmanager, Grafana, Node Exporter | The base for SLOs and for canary analysis |
| Tracing | OpenTelemetry, Jaeger | Vendor neutral, instrument once |
| Secrets | Vault, OpenBao | Know the license story |
| Security scanning | Trivy, Bandit, OWASP Dependency Check, gitleaks, trufflehog | Plus Renovate, because a scan without a fix is a report |
| Resilience | Chaos Mesh or Litmus | One experiment, with a written hypothesis |
| DR | Velero | Namespace and PVC backup, measured RTO |
| Platform | Backstage | Conceptual |
| AI | An AI coding assistant, an AI PR reviewer, an LLM for chatops | Used with an explicit review discipline throughout |

---
## Appendix B: The free path

| Instead of | Use |
|---|---|
| EKS | k3d or kind, single node, on your laptop |
| AWS S3, DynamoDB, IAM, Secrets Manager | LocalStack |
| A NAT gateway and a real VPC | The Module 3 and 8 network designs on paper, plus a VirtualBox internal network to prove the routing |
| A real load balancer | The ingress controller in your local cluster |
| Cloud based Terraform state | LocalStack S3 and DynamoDB, same code, different endpoint |

The one thing the free path cannot give you is the experience of a managed control plane and the shape of a real cloud bill, and those matter. If you can afford 40 to 90 USD across nine months, spend it. If you cannot, take the free path and do not think twice about it.

---
## Appendix C: Course policies

**Office hours.** Two hours per week, scheduled, plus a shared channel where questions get answered within one working day. Ask in the channel rather than by direct message, because the answer usually helps four other people.

**Code of conduct.** Be decent. No harassment, no discrimination, no belittling anyone for not knowing something yet. Everyone in this room did not know what a subnet mask was at some point. The person asking the "obvious" question is doing the room a favour, and treating them badly for it is the fastest way to build a team that hides its mistakes, which is the exact opposite of everything Module 16 is about.

**Accessibility.** Tell the instructor what you need in Week 1, and it gets arranged. Recordings, extended time on checkpoints, and alternative lab formats are all normal.

**Academic integrity.** Covered by the AI policy above. Short version: use whatever tools you like, and be able to defend every line. Copying another student's work and being unable to explain it fails on the defense anyway, which is rather the point of grading this way.

---
## Career and employability

- Treat the capstone as a portfolio centrepiece, not an assignment to forget. Keep the repository public and keep improving it after the course ends. It will be the best thing on your CV for at least two years.

- Turn three labs into short write ups: the DORA analysis (1A), the rightsizing proposal with a real number on it (12E), and the migration rollback that lied to you (15D). That third one, told well, will do more for you in an interview than any certificate, because almost nobody at your level can explain it.

- Practise narrating an incident out loud, using the postmortem from 16C. "Tell me about a time production broke" is the single most common interview question in this field, and a real, well documented story beats a rehearsed answer every time.

- Contribute something small to a real open source tool used in this course. Even a documentation fix. It is a concrete, checkable signal that costs you an evening.

- Join a cloud native community, locally or online. Meetups are still one of the fastest routes to hearing about a job before it gets posted.

---
