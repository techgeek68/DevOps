# DevOps Engineering

### Course Syllabus

| Field | Details |
|---|---|
| **Course Code** | DVP 401 |
| **Credits** | 4 |
| **Level** | Undergraduate / Professional Certificate |
| **Target** | Entry Level to Mid Level Engineers |
| **Prerequisites** | Basic Linux; fundamental networking; any scripting experience |
| **Instructor** | Anup Pyakurel |
| **Contact** | +977 9851124956 |

 
## Course Overview
 
This course takes an engineer from hands on Linux and networking fundamentals to the full modern cloud native delivery stack: version control, CI/CD, containers, Kubernetes, infrastructure as code, observability, and security. Every concept is anchored to a lab or mini project, so students leave with a working portfolio, not just notes.
 
## Required Tools and Accounts
 
| Requirement | Notes |
|---|---|
| Workstation: 16 GB RAM, 100 GB free disk | Minimum for running a local Kubernetes cluster alongside VMs |
| VirtualBox or VMware Workstation | VirtualBox is free; VMware Workstation Pro is free for personal use |
| AWS Free Tier account | Required for Module 6; credit card needed for signup |
| GitHub account | Free at github.com |
| Docker Hub account | Free at hub.docker.com |
| Red Hat Developer account | Free at developers.redhat.com: OpenShift sandbox and RHEL downloads |
 
## Course Objectives
 
Upon completion, students will be able to:
 
1. Explain the DevOps philosophy, Agile alignment, and the distinction between DevOps and SRE.
2. Administer Linux VMs confidently: users, permissions, services, networking, and scripting.
3. Deploy and configure web servers (Apache, Nginx, Tomcat) and proxy traffic between services.
4. Apply professional Git workflows: branching strategies, pull requests, and protected branches.
5. Design and operate CI/CD pipelines in Jenkins and GitHub Actions with quality gates baked in.
6. Automate configuration and deployments using Ansible roles and playbooks.
7. Build, run, and manage containers with Docker and Podman; understand their architectural differences.
8. Deploy and operate applications on Kubernetes using manifests, Helm, and GitOps via ArgoCD.
9. Provision repeatable cloud infrastructure on AWS using Terraform modules and remote state.
10. Implement production observability: Prometheus metrics, Grafana dashboards, and structured log pipelines.
11. Apply DevSecOps practices: secrets management with Vault, image scanning with Trivy, and least privilege access.
12. Deliver a complete, automated, observable application delivery pipeline as a solo capstone project.

---

# Module 1: DevOps Foundations
 
## Section 1.1 Core Concepts
 
### Theory
 
- The DevOps Lifecycle: plan, code, build, test, release, deploy, operate, monitor
- Agile vs. DevOps: what each solves, how they complement each other
- SRE vs. DevOps: error budgets, SLIs, SLOs, SLAs and when each model applies
- Infrastructure as Code: the shift from click ops to declarative provisioning
- Microservices vs. monoliths: tradeoffs engineers see daily, not just theory
- The DORA four metrics: deployment frequency, lead time, change failure rate, MTTR

### Labs
 
- **Lab 1.A DORA Baseline:** Pick any open source project on GitHub. Measure its approximate DORA metrics from public commit history and release tags. Document findings in a one page markdown report committed to your own repo.
- **Lab 1.B Architecture Diagram:** Draw the DevOps infinity loop, annotate each stage with the specific tools used in this course, and map one DORA metric to each stage. Submit as PDF.

---
# Module 2: Infrastructure, Linux, and Web Servers
 
## Section 2.1 Networking Fundamentals
 
### Theory
 
- OSI model: only the layers DevOps engineers actually touch (L3 L7)
- TCP/IP: ports, sockets, connection states (ESTABLISHED, TIME_WAIT)
- DNS: resolution chain, A records, CNAMEs, TTL, split horizon
- Load balancing: round robin, least connections, IP hash, sticky sessions
- Firewalls and security groups: stateful vs. stateless, default deny posture
- NAT, private vs. public addressing, CIDR notation

### Labs
 
- **Lab 2.1.A Network Diagnostics:** On a Linux VM, use `ping`, `traceroute`, `ss`, `nslookup`, and `dig` to diagnose a deliberately broken DNS and routing scenario. Document each command's output and explain what it reveals.
- **Lab 2.1.B Subnet Design:** Given `192.168.1.0/26`, calculate subnet mask, broadcast address, usable host range, and number of hosts. Then design a three subnet VPC layout for a typical web/app/db tier.
- **Lab 2.1.C Static Routing:** Configure two VMs on different subnets. Add static routes to establish connectivity. Show routing table before and after with `ip route`.
 
## Section 2.2 Virtualization and Linux
 
### Theory
 
- Hypervisors: Type 1 (bare metal) vs. Type 2 (hosted); VMs vs. containers, when each makes sense
- Why Linux dominates DevOps: tooling ecosystem, SSH first management, minimal attack surface
- systemd architecture: units, targets, journald, socket activation

### Labs
 
- **Lab 2.2.A VM Setup:** Install Fedora or RHEL 9 in VirtualBox/VMware. Set hostname, configure a static IP with `nmcli`, enable SSH, and disable password auth (key only).
- **Lab 2.2.B Linux Core Skills:** Complete each of the following and document the commands used: filesystem navigation and `find`; file operations with `grep`, `awk`, `sed`; user/group management and `/etc/shadow` inspection; `chmod` (octal and symbolic); `dnf`/`apt` package lifecycle; process management with `ps`, `top`, `kill`, `systemctl`; firewall management with `firewall-cmd`.
- **Lab 2.2.C Bash Mini Project:** Write a health check script that accepts a service name as an argument, checks if the service is running, logs the status with a timestamp to `/var/log/healthcheck.log`, and exits with code `0` (healthy) or `1` (unhealthy). Schedule it every 5 minutes via cron. The script must use functions, conditionals, loops, and proper exit codes.
- **Lab 2.2.D systemd Deep Dive:** Write a custom `.service` unit file that runs the health check script from Lab 2.2.C as a systemd timer instead of cron. Enable it, verify it fires, and inspect output with `journalctl -u`.
 
## Section 2.3 Web and Application Servers
 
### Theory
 
- Web vs. application servers: the distinction and where each sits in a stack
- Apache HTTP Server: MPM models (prefork vs. event), virtual hosts, `mod_proxy`
- Nginx: event driven architecture, reverse proxy, upstream load balancing
- Apache Tomcat: JVM requirements, connector architecture, Manager app
- TLS termination: where to terminate (load balancer, reverse proxy, or app)

### Labs
 
- **Lab 2.3.A Apache:** Install `httpd`; configure two named virtual hosts (static site + Python WSGI via `mod_wsgi`); enable HTTPS with a self signed certificate; customize access and error log formats.
- **Lab 2.3.B Nginx:** Install Nginx; serve a static site; configure it as a reverse proxy to a backend application; add an `upstream` block for round robin load balancing across two backends.
- **Lab 2.3.C Tomcat:** Install Tomcat; verify JDK compatibility; deploy a `.war` file; configure a manager user in `tomcat-users.xml`; access the Manager UI.
 
## Section 2.4 Sample Applications
 
> **Note:** These apps are not throwaway exercises. Each one follows CI/CD friendly conventions (env based config, unit tests, build artifacts) and gets carried forward into Module 3 pipelines.
 
### Theory
 
- What makes an application CI/CD friendly: environment driven config, testable units, repeatable builds
- Twelve factor app principles (factors 1, 3, and 6 are directly relevant here)

### Labs
 
- **Lab 2.4.A PHP:** Build a PHP app connecting to MySQL. Credentials come from environment variables only. Must display at least one DB record. This app is deployed in Lab 3.2.D.
- **Lab 2.4.B Python Flask:** Build a Flask API returning JSON on `GET /health` and `GET /`. Include at least two `pytest` unit tests. Tests must pass from the command line before proceeding. This app is containerized in Module 5.
- **Lab 2.4.C Java:** Create a Maven servlet project. Build with `mvn clean package`; verify the `.war` in `target/`. This artifact is deployed to Tomcat in Lab 3.2.C.

---
# Module 3: Version Control and CI/CD Pipelines
 
## Section 3.1 Git and GitHub
 
### Theory
 
- Why distributed version control: the mental model engineers need, not history
- Branching strategies: Git Flow, trunk based development, feature branching, tradeoffs for each team size
- Pull requests and code review: what makes a good review, what slows teams down
- Conventional commits: structured commit messages and why they matter for release automation
- Pre commit hooks: shifting quality checks to the developer machine before CI even runs
- Signed commits and branch protection as baseline security hygiene

### Labs
 
- **Lab 3.1.A Git Fundamentals:** Init a repo; stage and commit; create a feature branch; introduce a merge conflict deliberately; resolve it manually; push to GitHub; clone to a second location.
- **Lab 3.1.B History and Recovery:** Demonstrate and document the use case for each: `git log --oneline --graph`, `git diff`, `git stash`, `git rebase -i`, `git revert`, `git reset`. Critically: show the difference between `reset` (rewrites history, destructive on shared branches) and `revert` (safe for shared branches).
- **Lab 3.1.C Professional GitHub Setup:** Add a `.gitignore` (Python or Java template); install `pre-commit` with at least two hooks (`trailing-whitespace`, `check-yaml`); configure branch protection on `main` requiring one PR review and passing status checks; enforce conventional commit format via `commitlint`.

## Section 3.2 Jenkins
 
### Theory
 
- Jenkins architecture: controller, agents, executors, workspaces
- Freestyle vs. Declarative Pipeline vs. Scripted Pipeline: when each is appropriate
- Jenkinsfile as code: the pipeline lives in the repo, not in the Jenkins UI
- Webhook based triggering: push events vs. polling (polling is a last resort)
- Jenkins agents on Docker: ephemeral, clean build environments on every run

### Labs
 
- **Lab 3.2.A Jenkins Setup:** Install Jenkins via RPM or WAR on a Linux VM. Install plugins: Git, Pipeline, Maven Integration, SSH Agent, Role Based Authorization Strategy. Connect a second VM as a build agent over SSH.
- **Lab 3.2.B RBAC:** Create developer and admin roles. Verify developer cannot access administrative functions or modify pipeline configuration.
- **Lab 3.2.C Java Pipeline to Tomcat:** Declarative `Jenkinsfile` with stages: `Checkout`, `Build` (`mvn clean package`), `Deploy` (`.war` to Tomcat via SSH Agent). Trigger on push via GitHub webhook.
- **Lab 3.2.D PHP Pipeline to Apache:** Declarative `Jenkinsfile`, `Checkout`, `Test` (static lint or syntax check), `Deploy` to Apache virtual host via SSH Agent.
- **Lab 3.2.E Flask Pipeline to Nginx:** Multi stage `Jenkinsfile`, `Checkout`, `Test` (`pytest`), fail and halt if tests fail, `Deploy` behind Nginx reverse proxy.
- **Lab 3.2.F Docker Agent Pipeline *(NEW)*:** Convert the Flask pipeline to run inside an ephemeral Docker container agent (`agent { docker { image 'python:3.12-slim' } }`). Confirm the build environment is clean and reproducible across runs.
 
## Section 3.3 GitHub Actions
 
### Theory
 
- GitHub Actions core concepts: workflow, trigger event, job, step, runner, secrets, environment
- Reusable workflows and composite actions: reducing duplication across repositories
- Matrix builds: testing across multiple OS or language versions in parallel
- GitHub Actions vs. Jenkins: hosted runners vs. self managed, GitHub native vs. platform agnostic
- GitHub Environments: manual approval gates before deploying to production

### Labs
 
- **Lab 3.3.A First Workflow:** Write `.github/workflows/ci.yml` triggering on push to `main`. Steps: checkout, install deps, run `pytest`. Confirm green badge appears on the repo.
- **Lab 3.3.B Matrix Build *(NEW)*:** Extend the CI workflow to run tests across Python 3.10, 3.11, and 3.12 using a matrix strategy. All three must pass before the workflow succeeds.
- **Lab 3.3.C Secrets and Deploy:** Store an SSH private key as a GitHub Secret. Write a workflow deploying the Flask app to a cloud server on merge to `main`, injecting the secret as an env variable. Add a GitHub Environment called `production` requiring one manual approval before deploy.
 
## Section 3.4 Build Tools
 
### Theory
 
- Maven: Project Object Model (`pom.xml`), build lifecycle phases, dependency resolution, repositories
- Make and Makefile: still widely used for polyglot projects and infrastructure tooling
- Artifact versioning: semantic versioning, SNAPSHOT vs. release, why version pinning matters

### Labs
 
- **Lab 3.4.A Maven:** Create a project from archetype; add a dependency; run `mvn clean package`; inspect `target/`. Verify the resulting `.war` deploys to Tomcat from Lab 2.3.C.
- **Lab 3.4.B Makefile *(NEW)*:** Write a `Makefile` for the Flask project with targets: `install`, `test`, `build` (Docker image), `push`, `deploy`. The Jenkins and GitHub Actions pipelines must invoke `make` targets rather than inline shell commands.

---

# Module 4: Configuration Management with Ansible
 
## Section 4.1 Ansible Fundamentals
 
### Theory
 
- Ansible architecture: control node, managed nodes, agentless SSH based execution
- Inventory: static vs. dynamic; AWS EC2 dynamic inventory plugin
- Idempotency: why it matters and how to verify it (run twice, check nothing changes)
- Ansible vs. Terraform: configuration state vs. infrastructure provisioning, not competitors
- Jinja2 templating: variables, filters, conditionals in templates
- Ansible Vault: encrypting secrets at rest in the repository
- Roles: standardized directory structure, reusability, Galaxy

### Labs
 
- **Lab 4.1.A Core Ansible:** Install Ansible on a control node. Write a static inventory with `[webservers]` and `[dbservers]` groups. Run ad hoc commands (`ping`, `command`, `yum`, `service`). Write a playbook installing and starting Apache with a handler that restarts only on config change.
- **Lab 4.1.B Practical Playbooks:** Write a playbook managing user accounts (create, password, groups). Write a second playbook deploying the PHP app from Lab 2.4.A (install Apache, copy files, set permissions, restart). Encrypt a `db_password` variable with `ansible-vault`.
- **Lab 4.1.C Roles Refactor:** Convert the PHP deployment playbook into an Ansible role with the standard structure: `tasks/`, `handlers/`, `templates/`, `vars/`, `defaults/`. A Jinja2 template must generate the virtual host config file from variables.
- **Lab 4.1.D Dynamic Inventory *(NEW)*:** Replace the static inventory with the AWS EC2 dynamic inventory plugin. Target EC2 instances by tag (e.g., `Role=webserver`). Run the PHP deployment role against dynamically discovered hosts.
- **Lab 4.1.E Jenkins Integration:** Add an Ansible deployment stage to the Jenkins pipeline from Lab 3.2.D. Replace the direct SSH step with `ansible-playbook` execution. Verify the full chain: Git push, Jenkins build, Ansible deploys, app accessible.

---

# Module 5: Containerization and Orchestration
 
## Section 5.1 Docker and Podman
 
### Theory
 
- What containers solve: environment parity, dependency isolation, fast startup
- Containers vs. VMs: resource sharing, startup time, isolation tradeoffs
- OCI standards: image spec, runtime spec, distribution spec, why they matter for portability
- Image layering: union filesystems, layer caching, why layer order affects build time
- Multi stage builds: separating build dependencies from the runtime image
- Docker architecture: daemon, CLI, containerd, runc
- Podman architecture: daemonless, rootless by default, cgroups v2, drop in Docker CLI compatibility
- Security implications: running as root in Docker vs. rootless in Podman

### Labs
 
- **Lab 5.1.A Docker Basics:** Install Docker Engine. Pull an image; run with `docker run`. Inspect with `docker ps`, `logs`, `exec`, `inspect`. Write a `Dockerfile` for the Flask app (`FROM`, `RUN`, `COPY`, `EXPOSE`, `CMD`). Build and run. Use `.dockerignore`.
- **Lab 5.1.B Multi Stage Build *(NEW)*:** Rewrite the Flask `Dockerfile` as a multi stage build: a builder stage installs dependencies into a venv; the final stage copies only the venv and app code. Compare image sizes before and after. Scan both with `trivy` and note the difference in CVE count.
- **Lab 5.1.C Podman:** Install Podman on RHEL/Fedora. Run the same Docker Hub image as a non root user. Build from the same `Dockerfile` with `podman build`. Verify rootless: `ps aux | grep <process>`. Use `podman generate kube` and inspect the output YAML.
- **Lab 5.1.D Compose:** Write a `docker-compose.yml` for Flask + MySQL. Use named volumes for DB persistence. Use an `.env` file for credentials (never hardcoded). Start with `docker compose up`; verify connectivity. Repeat with `podman compose up`.
- **Lab 5.1.E Registry and CI/CD:** Tag and push the Flask image to Docker Hub. Add a build and push stage to the Jenkins pipeline from Lab 4.1.E. Optionally: replace `docker` with `podman` in the pipeline and confirm identical behavior.
 
## Section 5.2 Kubernetes
 
### Theory
 
- Control plane components: API Server, etcd, Scheduler, Controller Manager
- Worker node components: kubelet, kube proxy, container runtime (containerd)
- Core objects: Pod, ReplicaSet, Deployment, StatefulSet, DaemonSet, Job, CronJob
- Service types: ClusterIP, NodePort, LoadBalancer, ExternalName
- Ingress: routing external traffic, Ingress controllers (Nginx Ingress)
- Resource requests and limits: why every production workload must define them
- Liveness, readiness, and startup probes: Kubernetes cannot self heal what it cannot detect
- ConfigMaps and Secrets: separating config from image
- Persistent Volumes and PVCs: stateful workloads in Kubernetes
- Rolling updates and rollback strategy
- RBAC: ServiceAccounts, Roles, ClusterRoles, RoleBindings

### Labs
 
- **Lab 5.2.A Cluster Setup:** Set up a single node cluster with Minikube or kind. Then set up a multi node cluster (1 control plane + 2 workers) on separate VMs using kubeadm. Verify all nodes `Ready` with `kubectl get nodes`.
- **Lab 5.2.B Core Workloads:** Write and apply a Pod manifest; inspect with `kubectl describe`. Write a Deployment for the Flask image; apply; verify pods running. Scale to 3 replicas. Write a NodePort Service; access from browser. Update the image tag; observe rolling update; roll back with `kubectl rollout undo`.
- **Lab 5.2.C Probes and Resource Limits *(NEW)*:** Add liveness (`/health` HTTP probe) and readiness probes to the Flask Deployment. Set resource requests and limits (`cpu: 100m/250m`, `memory: 128Mi/256Mi`). Kill the Flask process inside a pod and observe Kubernetes restart it automatically.
- **Lab 5.2.D Config and Secrets:** Create a ConfigMap for Flask config; mount as env vars. Create a Secret for the DB password; reference in the Pod spec. Apply the Podman generated YAML from Lab 5.1.C directly with `kubectl apply`.
- **Lab 5.2.E Ingress *(NEW)*:** Install the Nginx Ingress Controller in Minikube. Write an Ingress manifest routing `/api` to the Flask Service and `/` to a static site. Verify routing from the browser.
- **Lab 5.2.F RBAC *(NEW)*:** Create a ServiceAccount for the CI/CD pipeline. Bind it to a Role permitting only `get`, `list`, and `update` on Deployments in the app namespace. Verify it cannot access Secrets.
- **Lab 5.2.G Helm:** Install Helm. Inspect a chart structure (`Chart.yaml`, `values.yaml`, `templates/`). Deploy the Nginx chart from Bitnami. Override values with `--set` and a custom `values.yaml`. Write a minimal Helm chart for the Flask app and deploy it.
- **Lab 5.2.H Kustomize *(NEW)*:** Write a Kustomize base for the Flask app (Deployment + Service). Create two overlays: `dev` (1 replica, debug env var) and `prod` (3 replicas, resource limits). Apply each with `kubectl apply -k`.
- **Lab 5.2.I CI/CD for Kubernetes:** Extend the pipeline from Lab 5.1.E to add a `kubectl apply` stage after image push. Verify the new image is running in the cluster after the pipeline completes.
 
## Section 5.3 GitOps
 
### Theory
 
- GitOps principles: declarative config in Git is the source of truth; agents reconcile actual vs. desired state
- Push based (traditional CI/CD) vs. pull based (GitOps) delivery: security and audit tradeoffs
- ArgoCD: Application CRD, sync policies, health status, self healing
- Drift detection: ArgoCD alerting when cluster state diverges from Git

### Labs
 
- **Lab 5.3.A ArgoCD:** Install ArgoCD in the cluster. Expose the UI; log in. Connect ArgoCD to the GitHub repo containing Flask manifests. Update the replica count in Git; observe ArgoCD detect the drift and auto sync. Then introduce a manual `kubectl` change and observe ArgoCD revert it.
 
## Section 5.4 Red Hat OpenShift
 
### Theory
 
- OpenShift vs. Kubernetes: additional security defaults, SCCs, built in image registry, Routes
- Source to Image (S2I): build from source without writing a Dockerfile
- OpenShift Routes vs. Kubernetes Ingress
- When to choose OpenShift vs. vanilla Kubernetes

### Labs
 
- **Lab 5.4.A OpenShift Sandbox:** Access the Red Hat Developer Sandbox. Deploy the Flask app via web console and via `oc` CLI (`oc new-app`, `oc expose`, `oc get route`). Deploy using S2I directly from the GitHub repo. Compare the resulting Route to the Ingress from Lab 5.2.E.
 
# Module 6: Cloud and Infrastructure as Code
 
## Section 6.1 AWS Fundamentals
 
### Theory
 
- Cloud service models: IaaS, PaaS, SaaS and where they map to real AWS services
- AWS global infrastructure: Regions, Availability Zones, Local Zones
- IAM: users, groups, roles, policies, least privilege by default
- VPC fundamentals: subnets (public/private), Internet Gateway, NAT Gateway, route tables, security groups, NACLs
- EC2: AMIs, instance types, key pairs, instance profiles, user data
- S3: buckets, object storage, bucket policies, versioning, lifecycle rules

### Labs
 
- **Lab 6.1.A AWS Setup and EC2:** Create a Free Tier account; configure AWS CLI. Launch an EC2 instance (Amazon Linux 2023), SSH in, install and start Nginx, confirm it serves traffic. Terminate after.
- **Lab 6.1.B IAM Least Privilege:** Create an IAM user with no permissions; attach S3 read only policy; verify it can list but not create buckets. Create an IAM Role for EC2 with S3 read access; attach to an instance; verify the instance reads S3 without access keys.
- **Lab 6.1.C VPC Design and Build:** Create a VPC (`10.0.0.0/16`) with a public subnet (`10.0.1.0/24`) and a private subnet (`10.0.2.0/24`). Attach an Internet Gateway to the public subnet. Add a NAT Gateway for private subnet outbound access. Launch one EC2 in each subnet; verify the private instance has outbound internet access but no inbound public IP.
 
## Section 6.2 Terraform
 
### Theory
 
- Terraform's declarative model: desired state vs. imperative scripting
- Terraform state: what it tracks, why it must not be lost, why it must not live in Git
- Terraform workflow: `init`, `plan`, `apply`, `destroy`
- State locking: DynamoDB as a lock backend to prevent concurrent applies
- Workspaces: environment isolation without duplication
- Modules: the unit of reuse in Terraform; module sources (local, registry, Git)

### Labs
 
- **Lab 6.2.A Terraform Basics:** Install Terraform. Write `main.tf` provisioning one EC2 and one Security Group allowing SSH. Run `init`, `plan`, `apply`; verify in AWS Console. Run `destroy`.
- **Lab 6.2.B Variables and Outputs:** Parameterize instance type and region via `variable` blocks. Add an `output` printing the public IP. Run `terraform apply -var="instance_type=t2.micro"`.
- **Lab 6.2.C Remote State with Locking:** Create an S3 bucket and DynamoDB table for state. Configure `backend "s3"` with `dynamodb_table` for locking. Run `apply`; verify state file is in S3. Simulate a concurrent apply and observe the lock error.
- **Lab 6.2.D Modules:** Refactor EC2 + Security Group into a reusable module. Call it twice from root config with different parameters: one web server, one build agent.
- **Lab 6.2.E Cost Estimation *(NEW)*:** Install Infracost. Run `infracost breakdown --path .` against the Terraform config from Lab 6.2.D. Interpret the cost estimate. Add `infracost comment` to the GitHub Actions workflow so every PR shows a cost diff.

---
# Module 7: Observability and Security

## Section 7.1 Monitoring with Prometheus and Grafana
 
### Theory
 
- Three pillars of observability: metrics, logs, traces, what each answers, what each misses
- Prometheus data model: time series, labels, metric types (counter, gauge, histogram, summary)
- PromQL: `rate()`, `increase()`, `histogram_quantile()`, the three queries engineers reach for first
- Alertmanager: routing, grouping, inhibition, silencing, receiver integrations
- Grafana: panels, variables, annotations, alert rules
- Service Level Objectives: instrumenting SLOs with Prometheus

### Labs
 
- **Lab 7.1.A Prometheus and Node Exporter:** Install Prometheus; configure `prometheus.yml` with two scrape targets. Install Node Exporter on each target. Verify targets `UP` in the Prometheus UI. Run PromQL queries: `up`, `rate(node_cpu_seconds_total[5m])`, `node_memory_MemAvailable_bytes`.
- **Lab 7.1.B Alertmanager *(NEW)*:** Deploy Alertmanager. Write an alert rule firing when CPU usage exceeds 80% for 2 minutes. Configure Alertmanager to route alerts to a Slack webhook. Trigger the alert and verify the notification arrives.
- **Lab 7.1.C Grafana:** Install Grafana; add Prometheus as a data source. Import the Node Exporter Full dashboard (ID 1860). Build a custom dashboard with three panels: CPU usage (time series), memory usage (gauge), and HTTP request rate from the Flask app (requires adding `prometheus_client` to Flask and a `/metrics` endpoint).
 
## Section 7.2 Distributed Tracing
 
### Theory
 
- Why logs and metrics are not enough in a microservices environment
- OpenTelemetry: the open standard for traces, metrics, and logs, vendor neutral instrumentation
- Trace anatomy: spans, trace context, parent child relationships, sampling
- Jaeger: open source distributed tracing backend

### Labs
 
- **Lab 7.2.A OpenTelemetry + Jaeger:** Instrument the Flask app with `opentelemetry-sdk` and `opentelemetry-exporter-jaeger`. Deploy Jaeger in the Kubernetes cluster. Make several requests to Flask; find the resulting traces in the Jaeger UI; identify latency at each span.
 
## Section 7.3 Log Management with Elastic Stack
 
### Theory
 
- Elastic Stack components: Elasticsearch (indexing and search), Logstash (parsing and enrichment), Kibana (visualization), Filebeat (lightweight shipper)
- Log pipeline: collection, parsing, indexing, visualization
- Structured vs. unstructured logs: why structured logging (JSON) makes downstream parsing trivial
- Index lifecycle management: keeping storage costs under control

### Labs
 
- **Lab 7.3.A Stack Setup:** Install Elasticsearch and Kibana. Verify cluster health: `curl http://localhost:9200/_cluster/health`.
- **Lab 7.3.B Log Pipeline:** Install Filebeat on the Apache VM; configure it to ship `/var/log/httpd/access_log`. Write a Logstash pipeline with a `grok` filter parsing Apache Combined Log Format. In Kibana, create an index pattern and filter entries by HTTP status code.
- **Lab 7.3.C Kibana Dashboard:** Build a dashboard with three panels: request count over time (area chart), HTTP status code distribution (pie chart), and top 10 requested URLs (data table).
 
## Section 7.4 DevSecOps
 
### Theory
 
- Shifting security left: finding vulnerabilities at commit time costs far less than finding them in production
- OWASP Top 10: the vulnerabilities every DevOps engineer must recognize
- Secrets management: why `.env` files committed to Git end careers, and what to do instead
- SAST (Static Application Security Testing): analyzing source code without running it
- SCA (Software Composition Analysis): known vulnerabilities in third party dependencies
- Container image security: base image age, pinned tags, non root `USER`
- Rootless containers as a security control: the attack surface when root in container maps to root on host
- Least privilege in CI/CD: pipeline credentials should have the minimum scope to do their job

### Labs
 
- **Lab 7.4.A HashiCorp Vault:** Install Vault in dev mode. Write a DB password: `vault kv put secret/myapp db_password=<value>`. Retrieve it from a Jenkins pipeline step. Compare to the insecure alternative of writing it directly in the `Jenkinsfile`.
- **Lab 7.4.B SAST and Dependency Scanning *(NEW)*:** Run Bandit against the Flask app: `bandit -r app/`. Resolve at least one finding. Run OWASP Dependency Check against the project. Add both as pipeline stages; fail the pipeline on HIGH severity findings.
- **Lab 7.4.C Trivy Image Scanning:** Install Trivy. Scan the Flask image: `trivy image <name>`. Identify at least one HIGH/CRITICAL CVE; research it; apply the fix (usually: update the base image). Add Trivy as a pipeline stage; configure it to fail on CRITICAL findings.
- **Lab 7.4.D Secure Jenkins:** Configure Jenkins to serve over HTTPS with a self signed cert. Set controller executors to zero (all builds on agents). Confirm developer role cannot modify pipelines or access admin settings.
 
## Section 7.5 Project Management with Jira
 
### Theory
 
- Agile in Jira: Epics, User Stories, Tasks, Sub tasks; Sprint planning; Kanban boards
- Jira + Git integration: commit messages linking to issues, PR status in Jira
- Jira in a DevOps context: tracing a feature from backlog to deployed

### Labs
 
- **Lab 7.5.A Jira Setup:** Create a Scrum or Kanban project. Create an Epic; write three User Stories under it; create a Sprint; assign stories; start the Sprint.
- **Lab 7.5.B Git Integration:** Commit a code change with the Jira issue key in the message. Open a GitHub PR; verify it appears in the Jira issue's development panel. Move the issue to Done on merge.

---

# Module 8: Capstone Project
 
The capstone requires each student to design, build, and operate a complete application delivery pipeline demonstrating all competencies from Modules 1 through 7. Completed individually. Presented in a 15 minute walkthrough during the final session.
 
## Objective
 
A Git push on the developer's machine triggers a fully automated pipeline that tests, scans, builds, and deploys the application to a Kubernetes cluster, with zero manual steps in between, full observability, and no credentials in any file.
 
## Mandatory Components
 
All eight components are required.
 
**1. Application**
A web application in PHP, Python Flask, or Java. Must connect to a database, include at least one feature covered by automated tests, and read all configuration from environment variables.
 
**2. Version Control**
Hosted on GitHub with a branching strategy (feature branches merged via PR). `main` protected by branch protection rules. Conventional commits enforced via `pre-commit`.
 
**3. Containerization**
A multi stage `Dockerfile` producing a minimal, non root image. Image pushed to Docker Hub or private registry. No credentials in the image.
 
**4. CI/CD Pipeline (Jenkins or GitHub Actions)**
Stages in this order: checkout, unit tests (fail and halt on failure), SAST/dependency scan, image build and push, Trivy scan (fail on CRITICAL), deploy to Kubernetes.
 
**5. Infrastructure as Code**
Terraform provisions the deployment environment. Fully reproducible from `terraform apply`. Remote state in S3 with DynamoDB locking.
 
**6. Configuration Management**
Ansible configures the deployment target after Terraform provisions it. Playbooks are in the repository and idempotent.
 
**7. Observability**
Prometheus and Grafana deployed in the cluster. Grafana dashboard with four panels: CPU usage, memory usage, HTTP request rate, HTTP error rate. One alert rule configured in Alertmanager.
 
**8. Security**
All credentials in HashiCorp Vault or GitHub Secrets. No credential appears in source code, Dockerfiles, pipeline definitions, or pipeline logs.

---
## Deliverables
 
| Deliverable | Description |
|---|---|
| GitHub Repository | App source, `Dockerfile`, pipeline definition, Terraform config, Ansible playbooks, Kubernetes manifests, README with architecture diagram |
| Live Application | Accessible via browser or API at a stable URL or IP at time of presentation |
| Grafana Dashboard Screenshot | Four live panels from the running application |
| 15 Minute Presentation | Full walkthrough: Git push to running app. Must include one problem encountered and how it was resolved. |

---
# Appendix: Tool and Technology Reference
 
| Area | Tools | Notes |
|---|---|---|
| Virtualization | VirtualBox, VMware Workstation | VirtualBox free; VMware free for personal use |
| Linux | Fedora / CentOS Stream / RHEL 9, Ubuntu | RHEL family preferred for Red Hat alignment |
| Web Servers | Apache, Nginx, Tomcat | |
| Version Control | Git, GitHub | pre commit, conventional commits |
| CI/CD | Jenkins, GitHub Actions | Docker agents in Jenkins |
| Build Tools | Maven, Make | Makefile wraps all pipeline steps |
| Config Management | Ansible | Dynamic inventory, Vault integration |
| Containers | Docker, Podman, Buildah | Docker Compose, Podman Compose |
| Orchestration | Kubernetes (Minikube, kubeadm), Helm, Kustomize, ArgoCD | |
| Enterprise Kubernetes | Red Hat OpenShift | Developer Sandbox (free) |
| IaC | Terraform | Remote state, modules, Infracost |
| Cloud | AWS (EC2, S3, IAM, VPC, DynamoDB) | Free Tier account required |
| Monitoring | Prometheus, Alertmanager, Grafana, Node Exporter | |
| Tracing | OpenTelemetry, Jaeger | Added in this revision |
| Logging | Elastic Stack (Elasticsearch, Logstash, Kibana, Filebeat) | |
| Security | HashiCorp Vault, Trivy, Bandit, OWASP Dependency Check | SAST + SCA + image scanning |
| Project Management | Jira | Scrum/Kanban, Git integration |

---
## Official Documentation
 
- Jenkins: https://www.jenkins.io/doc/
- Kubernetes: https://kubernetes.io/docs/
- OpenShift: https://docs.openshift.com/
- Terraform: https://developer.hashicorp.com/terraform/docs
- Ansible: https://docs.ansible.com/
- Prometheus: https://prometheus.io/docs/
- OpenTelemetry: https://opentelemetry.io/docs/
- Elastic: https://www.elastic.co/docs/
- Google SRE Book: https://sre.google/sre-book/table-of-contents/
---
