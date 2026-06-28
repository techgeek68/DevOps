# DevOps Engineering

---
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

---
## Course Overview

This course takes an engineer from hands on Linux and networking fundamentals through the full modern cloud native delivery stack: version control, CI/CD, containers, Kubernetes, infrastructure as code, observability, and security. Every concept is anchored to a lab or mini project so students leave with a working portfolio, not just notes.

GitHub Actions is the primary CI/CD platform in this course. It reflects where the industry has moved for greenfield projects. Jenkins is retained as an optional enterprise track for students headed into large organizations with existing Jenkins infrastructure.

The curriculum also covers supply chain security (SBOM generation and image signing with cosign), policy as code enforcement with Kyverno, progressive delivery with canary rollouts and automated rollback, and disaster recovery fundamentals with measured RPO and RTO.

---
## Required Tools and Accounts

| Requirement | Notes |
|---|---|
| Workstation: 16 GB RAM, 100 GB free disk | Minimum for running a local Kubernetes cluster alongside VMs |
| VirtualBox or VMware Workstation | VirtualBox is free; VMware Workstation Pro is free for all users (commercial and personal) as of November 2024 |
| AWS Free Tier account | Required for Module 6; credit card needed for signup |
| GitHub account | Free at github.com |
| Docker Hub account | Free at hub.docker.com |
| Red Hat Developer account | Free at developers.redhat.com. OpenShift sandbox and RHEL downloads |

---
## Course Objectives

Upon completion, students will be able to:

1. Explain the DevOps philosophy, Agile alignment, and the distinction between DevOps and SRE.
2. Administer Linux VMs confidently: users, permissions, services, networking, and scripting.
3. Deploy and configure web servers (Apache, Nginx) and proxy traffic between services.
4. Apply professional Git workflows: branching strategies, pull requests, and protected branches.
5. Design and operate CI/CD pipelines primarily in GitHub Actions, with Jenkins as an optional enterprise track.
6. Automate configuration and deployments using Ansible roles and playbooks.
7. Build, run, and manage containers with Docker and Podman; understand their architectural differences.
8. Deploy and operate applications on Kubernetes using manifests, Helm, GitOps via ArgoCD, and progressive delivery via Argo Rollouts.
9. Enforce cluster policy with Kyverno: block privileged pods and require signed images before deploy.
10. Generate SBOMs with syft and sign/verify container images with cosign as part of the pipeline.
11. Provision repeatable cloud infrastructure on AWS using Terraform modules and remote state.
12. Implement production observability: Prometheus metrics, Grafana dashboards, distributed traces, and structured log pipelines.
13. Apply DevSecOps practices: secrets management, image scanning, SAST, dependency scanning, secrets scanning, and least privilege access.
14. Execute a scoped disaster recovery exercise: backup, restore, and measure RPO and RTO.
15. Deliver a complete, automated, observable, and secure application delivery pipeline as a solo capstone project.

---
# Module 1: DevOps Foundations

## Section 1.1 Core Concepts

### Theory

- The DevOps Lifecycle: plan, code, build, test, release, deploy, operate, monitor
- Agile vs. DevOps: what each solves, how they complement each other
- SRE vs. DevOps: error budgets, SLIs, SLOs, SLAs, and when each model applies
- Infrastructure as Code: the shift from click ops to declarative provisioning
- Microservices vs. monoliths: tradeoffs engineers see daily, not just theory
- The DORA four metrics: deployment frequency, lead time for changes, change failure rate, time to restore service

### Labs

- **Lab 1.A DORA Baseline:**

Pick any open source project on GitHub. Measure its approximate DORA metrics from public commit history, release tags, pull request timelines, and issue trackers. Document findings in a structured Markdown report committed to your own repository.

- **Lab 1.B SLO and Error Budget Calculation:**

Calculate error budgets for six availability targets over a 30 day window. Analyze three outage scenarios for hypothetical services to determine budget consumption and maintenance window feasibility. Design custom SLIs, SLOs, and an external SLA for a chosen service to understand the engineering discipline behind reliability buffers.

- **Lab 1.C IaC Drift Detection with Terraform:**

Provision an AWS security group using Terraform, introduce configuration drift by making manual changes directly through the AWS CLI, detect the drift using `terraform plan`, and restore declared state with `terraform apply`. Then add the same changes correctly through code to understand why version-controlled infrastructure eliminates the drift problem.

- **Lab 1.D DevOps Lifecycle Diagnosis and Redesign:**

Analyze a broken delivery process at a real-world startup scenario with manual deployments, no CI, no monitoring, and a single point of failure engineer. Assess the DORA baseline, identify operational risks, design the complete target lifecycle, build a sprint by sprint 90 day improvement plan, define the team's first SLO, and solve a concrete knowledge concentration problem with a six week deadline.

---
# Module 2: Infrastructure, Linux, and Web Servers

## Section 2.1 Networking Fundamentals

### Theory

- OSI model: only the layers DevOps engineers actually touch (L3-L7)
- TCP/IP: ports, sockets, connection states (ESTABLISHED, TIME_WAIT)
- DNS: resolution chain, A records, CNAMEs, TTL, split horizon
- Load balancing: round robin, least connections, IP hash, sticky sessions
- Firewalls and security groups: stateful vs. stateless, default deny posture
- NAT, private vs. public addressing, CIDR notation

### Labs

- **Lab 2.1.A Network Diagnostics:**

On a Linux VM, use `ping`, `traceroute`, `ss`, `nslookup`, and `dig` to diagnose a deliberately broken DNS and routing scenario. Document each command's output and explain what it reveals.

- **Lab 2.1.B Subnet Design:**

Given `192.168.1.0/26`, calculate the subnet mask, broadcast address, usable host range, and number of hosts. Then design a three subnet VPC layout for a typical web/app/db tier.

- **Lab 2.1.C Static Routing:**

Configure two VMs on different subnets. Add static routes to establish connectivity. Show the routing table before and after with `ip route`.

## Section 2.2 Virtualization and Linux

### Theory

- Hypervisors: Type 1 (bare metal) vs. Type 2 (hosted); VMs vs. containers, when each makes sense
- Why Linux dominates DevOps: tooling ecosystem, SSH first management, minimal attack surface
- systemd architecture: units, targets, journald, socket activation

### Labs

- **Lab 2.2.A VM Setup:**

Install the latest version of Fedora or RHEL in VirtualBox/VMware. Set hostname, configure a static IP with `nmcli`, enable SSH, and disable password auth (key only).

- **Lab 2.2.B Linux Core Skills:**

Complete each of the following and document the commands used: filesystem navigation and `find`; file operations with `grep`, `awk`, `sed`; user/group management and `/etc/shadow` inspection; `chmod` (octal and symbolic); `dnf`/`apt` package lifecycle; process management with `ps`, `top`, `kill`, `systemctl`; firewall management with `firewall-cmd`.

- **Lab 2.2.C Bash Mini Project:**

Write a health check script that accepts a service name as an argument, checks if the service is running, logs the status with a timestamp to `/var/log/healthcheck.log`, and exits with code `0` (healthy) or `1` (unhealthy). Schedule it every 5 minutes via cron. The script must use functions, conditionals, loops, and proper exit codes.

- **Lab 2.2.D systemd Deep Dive:**

Write a custom `.service` unit file that runs the health check script from Lab 2.2.C as a systemd timer instead of cron. Enable it, verify it fires, and inspect output with `journalctl -u`.

## Section 2.3 Web and Application Servers

### Theory

- Web vs. application servers: the distinction and where each sits in a stack
- Apache HTTP Server: MPM models (prefork vs. event), virtual hosts, `mod_proxy`
- Nginx: event driven architecture, reverse proxy, upstream load balancing
- TLS termination: where to terminate (load balancer, reverse proxy, or app)
- Apache Tomcat *(Java enterprise track only)*: JVM requirements, connector architecture, Manager app

### Labs

- **Lab 2.3.A Apache:**

Install `httpd`; configure two named virtual hosts (static site + Python WSGI via `mod_wsgi`); enable HTTPS with a self signed certificate; customize access and error log formats.

- **Lab 2.3.B Nginx:**

Install Nginx; serve a static site; configure it as a reverse proxy to a backend application; add an `upstream` block for round robin load balancing across two backends.

- **Lab 2.3.C Tomcat *(Optional, Java enterprise track)*:**

Install Tomcat; verify JDK compatibility; deploy a `.war` file; configure a manager user in `tomcat-users.xml`; access the Manager UI. Only required if you are following the Java legacy application stream.

## Section 2.4 Sample Applications

> **Note:** These apps are not throwaway exercises. Each one follows CI/CD friendly conventions (env based config, unit tests, build artifacts) and gets carried forward into Module 3 pipelines.

### Theory

- What makes an application CI/CD friendly: environment driven config, testable units, repeatable builds
- Twelve factor app principles (factors 1, 3, and 6 are directly relevant here)

### Labs

- **Lab 2.4.A PHP:**

Build a PHP app connecting to MySQL. Credentials come from environment variables only. Must display at least one DB record. This app is deployed in Lab 3.2.D.

- **Lab 2.4.B Python Flask:**

Build a Flask API returning JSON on `GET /health` and `GET /`. Include at least two `pytest` unit tests. Tests must pass from the command line before proceeding. This app is containerized in Module 5.

- **Lab 2.4.C Java *(Optional, Java enterprise track)*:**

Create a Maven servlet project. Build with `mvn clean package`; verify the `.war` in `target/`. This artifact is deployed to Tomcat in Lab 2.3.C. Skip if not following the Java stream.

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

- **Lab 3.1.A Git Fundamentals:**

Init a repo; stage and commit; create a feature branch; introduce a merge conflict deliberately; resolve it manually; push to GitHub; clone to a second location.

- **Lab 3.1.B History and Recovery:**

Demonstrate and document the use case for each: `git log --oneline --graph`, `git diff`, `git stash`, `git rebase -i`, `git revert`, `git reset`. Critically: show the difference between `reset` (rewrites history, destructive on shared branches) and `revert` (safe for shared branches).

- **Lab 3.1.C Professional GitHub Setup:**

Add a `.gitignore` (Python or Java template); install `pre-commit` with at least two hooks (`trailing-whitespace`, `check-yaml`); configure branch protection on `main` requiring one PR review and passing status checks; enforce conventional commit format via `commitlint`.

## Section 3.2 GitHub Actions *(Primary CI/CD Track)*

### Theory

- GitHub Actions core concepts: workflow, trigger event, job, step, runner, secrets, environment
- Reusable workflows and composite actions: reducing duplication across repositories
- Matrix builds: testing across multiple OS or language versions in parallel
- GitHub Environments: manual approval gates before deploying to production
- Self hosted runners: when hosted runners are not enough (air gapped, GPU, large builds)

### Labs

- **Lab 3.2.A First Workflow:**

Write `.github/workflows/ci.yml` triggering on push to `main`. Steps: checkout, run `make install`, run `make test`. Confirm green badge appears on the repo.

- **Lab 3.2.B Matrix Build:**

Extend the CI workflow to run tests across Python 3.10, 3.11, and 3.12 using a matrix strategy. All three must pass before the workflow succeeds.

- **Lab 3.2.C Full Delivery Workflow:**

Write a workflow with three jobs: `test` (pytest + Bandit), `build` (Docker image build and push), `deploy` (kubectl apply to the cluster). Add a GitHub Environment called `production` requiring one manual approval before deploy fires. Inject all credentials from GitHub Secrets.

- **Lab 3.2.D Reusable Workflow:**

Extract the test job into a reusable workflow at `.github/workflows/test.yml`. Call it from the main workflow with `uses:`. Verify that a second repository can call the same reusable workflow.

## Section 3.3 Jenkins *(Optional, Enterprise Track)*

### Theory

- Jenkins architecture: controller, agents, executors, workspaces
- Declarative Pipeline vs. Scripted Pipeline: when each is appropriate
- Jenkinsfile as code: the pipeline lives in the repo, not in the Jenkins UI
- Webhook based triggering: push events vs. polling (polling is a last resort)
- Jenkins agents on Docker: ephemeral, clean build environments on every run
- Why GitHub Actions has largely replaced Jenkins for greenfield projects

### Labs

- **Lab 3.3.A Jenkins Setup *(Optional)*:**

Install Jenkins via RPM or WAR on a Linux VM. Install plugins: Git, Pipeline, SSH Agent, Role Based Authorization Strategy. Connect a second VM as a build agent over SSH.

- **Lab 3.3.B RBAC *(Optional)*:**

Create developer and admin roles. Verify the developer cannot access administrative functions or modify pipeline configuration.

- **Lab 3.3.C Declarative Pipeline *(Optional)*:**

Write a `Jenkinsfile` with stages that invoke `make` targets: `make test`, `make build`, `make deploy`. Trigger on push via GitHub webhook. Notice that because the Makefile wraps all commands, this pipeline is nearly identical to the GitHub Actions workflow from Lab 3.2.C.

- **Lab 3.3.D Docker Agent Pipeline *(Optional)*:**

Run the pipeline inside an ephemeral Docker container agent (`agent { docker { image 'python:3.12-slim' } }`). Confirm the build environment is clean and reproducible across runs.

## Section 3.4 Build Tools

### Theory

- Maven: Project Object Model (`pom.xml`), build lifecycle phases, dependency resolution, repositories *(Java track)*
- Make and Makefile: polyglot build wrapper; the same `make test` invocation works in GitHub Actions and Jenkins
- Artifact versioning: semantic versioning, SNAPSHOT vs. release, why version pinning matters

### Labs

- **Lab 3.4.A Makefile:**

Write a `Makefile` for the Flask project with targets: `install`, `test`, `build` (Docker image), `push`, `deploy`. All CI pipelines invoke `make` targets, never inline shell commands. This is what makes the CI system swappable.

- **Lab 3.4.B Maven *(Optional, Java track)*:**

Create a project from an archetype; add a dependency; run `mvn clean package`; inspect `target/`. Verify the resulting `.war` deploys to Tomcat from Lab 2.3.C.

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
- Roles: standardised directory structure, reusability, Galaxy

### Labs

- **Lab 4.1.A Core Ansible:**

Install Ansible on a control node. Write a static inventory with `[webservers]` and `[dbservers]` groups. Run ad hoc commands (`ping`, `command`, `yum`, `service`). Write a playbook for installing and starting Apache with a handler that restarts only on a config change.

- **Lab 4.1.B Practical Playbooks:**

Write a playbook managing user accounts (create, password, groups). Write a second playbook deploying the PHP app from Lab 2.4.A (install Apache, copy files, set permissions, restart). Encrypt a `db_password` variable with `ansible-vault`.

- **Lab 4.1.C Roles Refactor:**

Convert the PHP deployment playbook into an Ansible role with the standard structure: `tasks/`, `handlers/`, `templates/`, `vars/`, `defaults/`. A Jinja2 template must generate the virtual host config file from variables.

- **Lab 4.1.D Dynamic Inventory:**

Replace the static inventory with the AWS EC2 dynamic inventory plugin. Target EC2 instances by tag (e.g., `Role=webserver`). Run the PHP deployment role against dynamically discovered hosts.

- **Lab 4.1.E CI/CD Integration:**

Add an Ansible deployment stage to the GitHub Actions workflow from Lab 3.2.C. Replace the direct `kubectl apply` deploy step with an `ansible-playbook` execution. Verify the full chain: Git push, Actions test, Actions build, Ansible deploys, app accessible. *(If following the Jenkins enterprise track, replicate this in the Jenkinsfile from Lab 3.3.C instead.)*

---
# Module 5: Containerization and Orchestration

## Section 5.1 Docker and Podman

> Docker dominates developer workflows and most CI/CD platforms. Podman is the default in RHEL 8+ and OpenShift environments and is growing in enterprises where rootless containers and daemonless architecture are security requirements. Mid level engineers need both.

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

- **Lab 5.1.A Docker Basics:**

Install Docker Engine. Pull an image; run with `docker run`. Inspect with `docker ps`, `logs`, `exec`, `inspect`. Write a `Dockerfile` for the Flask app (`FROM`, `RUN`, `COPY`, `EXPOSE`, `CMD`). Build and run. Use `.dockerignore`.

- **Lab 5.1.B Multi Stage Build:**

Rewrite the Flask `Dockerfile` as a multi stage build: a builder stage installs dependencies into a venv; the final stage copies only the venv and app code. Compare image sizes before and after. Scan both with `trivy` and note the difference in CVE count.

- **Lab 5.1.C Podman:**

Install Podman on RHEL/Fedora. Run the same Docker Hub image as a non root user. Build from the same `Dockerfile` with `podman build`. Verify rootless: `ps aux | grep <process>`. Use `podman generate kube` and inspect the output YAML.

- **Lab 5.1.D Compose:**

Write a `docker-compose.yml` for Flask + MySQL. Use named volumes for DB persistence. Use an `.env` file for credentials (never hardcoded). Start with `docker compose up`; verify connectivity. Repeat with `podman compose up`.

- **Lab 5.1.E Registry and CI/CD:**

Tag and push the Flask image to Docker Hub. Add a build and push stage to the GitHub Actions workflow from Lab 3.2.C. Jenkins enterprise track students: replicate in the Jenkinsfile from Lab 3.3.C.

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

- **Lab 5.2.A Cluster Setup:**

Set up a single node cluster with Minikube or kind. Then set up a multi node cluster (1 control plane + 2 workers) on separate VMs using kubeadm. Verify all nodes `Ready` with `kubectl get nodes`.

- **Lab 5.2.B Core Workloads:**

Write and apply a Pod manifest; inspect with `kubectl describe`. Write a Deployment for the Flask image; apply; verify pods are running. Scale to 3 replicas. Write a NodePort Service; access from the browser. Update the image tag; observe rolling update; roll back with `kubectl rollout undo`.

- **Lab 5.2.C Probes and Resource Limits:**

Add liveness (`/health` HTTP probe) and readiness probes to the Flask Deployment. Set resource requests and limits (`cpu: 100m/250m`, `memory: 128Mi/256Mi`). Kill the Flask process inside a pod and observe Kubernetes restart it automatically.

- **Lab 5.2.D Config and Secrets:**

Create a ConfigMap for Flask config; mount as env vars. Create a Secret for the DB password; reference it in the Pod spec. Apply the Podman generated YAML from Lab 5.1.C directly with `kubectl apply`.

- **Lab 5.2.E Ingress:**

Install the Nginx Ingress Controller in Minikube. Write an Ingress manifest routing `/api` to the Flask Service and `/` to a static site. Verify routing from the browser.

- **Lab 5.2.F RBAC:**

Create a ServiceAccount for the CI/CD pipeline. Bind it to a Role permitting only `get`, `list`, and `update` on Deployments in the app namespace. Verify it cannot access Secrets.

- **Lab 5.2.G Helm:**

Install Helm. Inspect a chart structure (`Chart.yaml`, `values.yaml`, `templates/`). Deploy the Nginx chart from Bitnami. Override values with `--set` and a custom `values.yaml`. Write a minimal Helm chart for the Flask app and deploy it.

- **Lab 5.2.H Kustomize:**

Write a Kustomize base for the Flask app (Deployment + Service). Create two overlays: `dev` (1 replica, debug env var) and `prod` (3 replicas, resource limits). Apply each with `kubectl apply -k`.

- **Lab 5.2.I CI/CD for Kubernetes:**

Extend the pipeline from Lab 5.1.E to add a `kubectl apply` stage after image push. Verify the new image is running in the cluster after the pipeline completes.

## Section 5.3 Supply Chain Security

### Theory

- Software supply chain attacks: what they are, why they are effective, real examples (SolarWinds, XZ Utils). Note: Log4Shell is a dependency vulnerability (SCA risk), not a supply chain compromise, the distinction matters.
- SBOM (Software Bill of Materials): a machine readable inventory of every component in a container image; SPDX and CycloneDX as the two dominant formats
- Image signing with cosign: asymmetric key signing of OCI artifacts; keyless signing via Sigstore
- Signature verification: blocking unsigned or unverified images before they reach the cluster
- SLSA (Supply Chain Levels for Software Artifacts): the framework behind these practices

### Labs

- **Lab 5.3.A SBOM Generation:**

Install `syft`. Run `syft <image-name> -o spdx-json > sbom.json` against the Flask image. Inspect the output: identify all packages, their versions, and their licenses. Attach the SBOM as a build artifact in the GitHub Actions workflow.

- **Lab 5.3.B Image Signing and Verification:**

Install `cosign`. Sign the Flask image after pushing: `cosign sign <image-digest>`. Add a verification step to the deployment pipeline: `cosign verify <image> --certificate-identity=<identity> --certificate-oidc-issuer=<issuer>`. Configure the pipeline to refuse to deploy if verification fails. Observe what happens when you attempt to deploy a different, unsigned image.

## Section 5.4 Policy as Code

> Admission controllers are the last line of defense before a workload runs in the cluster. Kyverno lets you express cluster policies as Kubernetes native resources. No Rego, no sidecar.

### Theory

- Admission controllers: how Kubernetes intercepts and validates API requests before they are persisted
- Validating vs. mutating webhooks: blocking bad requests vs. automatically correcting them
- Kyverno: policy as code with Kubernetes native CRDs; policies are YAML, not a separate language
- OPA Gatekeeper: the alternative for teams already invested in Rego; mentioned here for awareness
- Common policy patterns: deny privileged containers, require resource limits, require non root USER, enforce image registry allowlist, require signed images

### Labs

- **Lab 5.4.A Kyverno Setup:**

Install Kyverno in the cluster. Verify it is running: `kubectl get pods -n kyverno`.

- **Lab 5.4.B Block Privileged Pods:**

Write a Kyverno `ClusterPolicy` that denies any Pod spec with `securityContext.privileged: true`. Test it: attempt to apply a privileged Pod manifest and observe the admission denial. Then apply a non privileged Pod and verify it is admitted.

- **Lab 5.4.C Enforce Signed Images:**

Write a Kyverno policy that verifies cosign signatures before allowing a Pod to run. Test it with the signed Flask image (should be admitted) and an unsigned image pulled directly from Docker Hub (should be denied). Wire this policy to the production namespace only, leaving dev unrestricted.

---
## Section 5.5 GitOps

### Theory

- GitOps principles: declarative config in Git is the source of truth; agents reconcile actual vs. desired state
- Push based (traditional CI/CD) vs. pull based (GitOps) delivery: security and audit tradeoffs
- ArgoCD: Application CRD, sync policies, health status, self healing
- Drift detection: ArgoCD alerting when cluster state diverges from Git

### Labs

- **Lab 5.5.A ArgoCD:**

Install ArgoCD in the cluster. Expose the UI; log in. Connect ArgoCD to the GitHub repo containing Flask manifests. Update the replica count in Git; observe ArgoCD detect the drift and auto sync. Then introduce a manual `kubectl` change and observe ArgoCD revert it.

## Section 5.6 Progressive Delivery

### Theory

- Progressive delivery vs. rolling updates: traffic splitting vs. pod replacement
- Canary deployments: routing a percentage of traffic to the new version
- Blue/green deployments: two full environments, instant cutover
- Automated rollback: using a Prometheus metric query as the rollback trigger. If the error rate exceeds the threshold, Argo Rollouts reverts automatically
- Argo Rollouts: extends Kubernetes Deployments with canary and blue/green strategies; integrates with Prometheus for metric based analysis

### Labs

- **Lab 5.6.A Argo Rollouts Setup:**

Install Argo Rollouts in the cluster. Install the `kubectl argo rollouts` plugin. Convert the Flask Deployment manifest to a `Rollout` resource.

- **Lab 5.6.B Canary with Metric Based Rollback:**

Configure the Rollout with a canary strategy: 20% traffic to the new version for 5 minutes, then 50%, then 100%. Define an `AnalysisTemplate` querying Prometheus for HTTP 5xx error rate. Deploy a deliberately broken version of the Flask app (returns 500 on every request). Observe Argo Rollouts pause at 20%, detect the elevated error rate from the AnalysisTemplate, and automatically roll back to the stable version. Then deploy a healthy version and observe the full promotion sequence complete.

- **Lab 5.6.C Blue/Green Deployment:**

Configure a second Rollout using the blue/green strategy: full parallel environment, instant traffic cutover with no gradual weighting. Deploy Flask v2 as the green environment. Promote manually once satisfied. Roll back to blue by aborting the Rollout. Compare what the operator experience feels like vs. the canary from Lab 5.6.B and document when you would choose each.

## Section 5.7 Red Hat OpenShift

### Theory

- OpenShift vs. Kubernetes: additional security defaults, SCCs, built in image registry, Routes
- Source to Image (S2I): build from source without writing a Dockerfile
- OpenShift Routes vs. Kubernetes Ingress
- When to choose OpenShift vs. vanilla Kubernetes

### Labs

- **Lab 5.7.A OpenShift Sandbox:**

Access the Red Hat Developer Sandbox. Deploy the Flask app via web console and via `oc` CLI (`oc new-app`, `oc expose`, `oc get route`). Deploy using S2I directly from the GitHub repo. Compare the resulting Route to the Ingress from Lab 5.2.E.

---
# Module 6: Cloud and Infrastructure as Code

## Section 6.1 AWS Fundamentals

### Theory

- Cloud service models: IaaS, PaaS, SaaS, and where they map to real AWS services
- AWS global infrastructure: Regions, Availability Zones, Local Zones
- IAM: users, groups, roles, policies, least privilege by default
- VPC fundamentals: subnets (public/private), Internet Gateway, NAT Gateway, route tables, security groups, NACLs
- EC2: AMIs, instance types, key pairs, instance profiles, user data
- S3: buckets, object storage, bucket policies, versioning, lifecycle rules

### Labs

- **Lab 6.1.A AWS Setup and EC2:**

Create a Free Tier account; configure AWS CLI. Launch an EC2 instance (Amazon Linux 2023), SSH in, install and start Nginx, and confirm it serves traffic. Terminate after.

- **Lab 6.1.B IAM Least Privilege:**

Create an IAM user with no permissions; attach an S3 read only policy; verify it can list but not create buckets. Create an IAM Role for EC2 with S3 read access; attach it to an instance; verify the instance reads S3 without access keys.

- **Lab 6.1.C VPC Design and Build:**

Create a VPC (`10.0.0.0/16`) with a public subnet (`10.0.1.0/24`) and a private subnet (`10.0.2.0/24`). Attach an Internet Gateway to the public subnet. Add a NAT Gateway for private subnet outbound access. Launch one EC2 in each subnet; verify the private instance has outbound internet access but no inbound public IP.

## Section 6.2 Terraform

### Theory

- Terraform's declarative model: desired state vs. imperative scripting
- Terraform state: what it tracks, why it must not be lost, why it must not live in Git
- Terraform workflow: `init`, `plan`, `apply`, `destroy`
- State locking: DynamoDB as a lock backend to prevent concurrent applies
- Workspaces: environment isolation without duplication
- Modules: the unit of reuse in Terraform; module sources (local, registry, Git)

### Labs

- **Lab 6.2.A Terraform Basics:**

Install Terraform. Write `main.tf` provisioning one EC2 and one Security Group allowing SSH. Run `init`, `plan`, `apply`; verify in AWS Console. Run `destroy`.

- **Lab 6.2.B Variables and Outputs:**

Parameterize instance type and region via `variable` blocks. Add an `output` printing the public IP. Run `terraform apply -var="instance_type=t2.micro"`.

- **Lab 6.2.C Remote State with Locking:**

Create an S3 bucket and DynamoDB table for state. Configure `backend "s3"` with `dynamodb_table` for locking. Run `apply`; verify state file is in S3. Simulate a concurrent apply and observe the lock error.

- **Lab 6.2.D Modules:**

Refactor EC2 + Security Group into a reusable module. Call it twice from root config with different parameters: one web server, one build agent.

- **Lab 6.2.E Cost Estimation:**

Install Infracost. Run `infracost breakdown --path .` against the Terraform config from Lab 6.2.D. Interpret the cost estimate. Add `infracost comment` to the GitHub Actions workflow so every PR shows a cost diff.

## Section 6.3 Disaster Recovery

### Theory

- RPO (Recovery Point Objective): how much data loss is acceptable. The maximum age of the backup you can restore from
- RTO (Recovery Time Objective): how long the service can be down. The time from incident declaration to restored service
- Backup strategies: full, incremental, snapshot based. Tradeoffs in cost, speed, and recovery complexity
- Kubernetes specific DR: etcd backup, Velero for namespace/PVC backup, PostgreSQL dump to S3
- The difference between backup and DR: having a backup file is not DR until you have proven you can restore from it under time pressure

### Labs

- **Lab 6.3.A Velero Backup:**

Install Velero in the cluster with the AWS S3 storage backend. Take a backup of the entire application namespace: `velero backup create flask-backup --include-namespaces flask-app`. Verify the backup appears in S3.

- **Lab 6.3.B Database Backup:**

Write a CronJob manifest that runs `pg_dump` (or `mysqldump`) on a schedule and uploads the dump to S3 using the AWS CLI. Verify the dump file appears in S3 after the job runs.

- **Lab 6.3.C Restore and Measure:**

Delete the application namespace entirely. Record the start time. Restore from the Velero backup: `velero restore create --from-backup flask-backup`. Verify the application is accessible. Record the end time. Calculate your actual RTO. Compare it against a target RTO you defined before the exercise. If the actual RTO exceeded the target, identify the bottleneck (image pull time, PVC bind time, DNS propagation) and propose a remedy.

---
# Module 7: Observability and Security

## Section 7.1 Monitoring with Prometheus and Grafana

### Theory

- Three pillars of observability: metrics, logs, traces. What each answers, what each misses
- Prometheus data model: time series, labels, metric types (counter, gauge, histogram, summary)
- PromQL: `rate()`, `increase()`, `histogram_quantile()`. The three queries engineers reach for first
- Alertmanager: routing, grouping, inhibition, silencing, receiver integrations
- Grafana: panels, variables, annotations, alert rules
- Service Level Objectives: instrumenting SLOs with Prometheus

### Labs

- **Lab 7.1.A Prometheus and Node Exporter:**

Install Prometheus; configure `prometheus.yml` with two scrape targets. Install Node Exporter on each target. Verify targets `UP` in the Prometheus UI. Run PromQL queries: `up`, `rate(node_cpu_seconds_total[5m])`, `node_memory_MemAvailable_bytes`.

- **Lab 7.1.B Alertmanager:**

Deploy Alertmanager. Write an alert rule firing when CPU usage exceeds 80% for 2 minutes. Configure Alertmanager to route alerts to a Slack webhook. Trigger the alert and verify the notification arrives.

- **Lab 7.1.C Grafana:**

Install Grafana; add Prometheus as a data source. Import the Node Exporter Full dashboard (ID 1860). Build a custom dashboard with three panels: CPU usage (time series), memory usage (gauge), and HTTP request rate from the Flask app (requires adding `prometheus_client` to Flask and a `/metrics` endpoint).

## Section 7.2 Distributed Tracing

### Theory

- Why logs and metrics are not enough in a microservices environment
- OpenTelemetry: the open standard for traces, metrics, and logs. Vendor neutral instrumentation
- Trace anatomy: spans, trace context, parent child relationships, sampling
- Jaeger: open source distributed tracing backend

### Labs

- **Lab 7.2.A OpenTelemetry + Jaeger:**

Instrument the Flask app with `opentelemetry-sdk` and `opentelemetry-exporter-jaeger`. Deploy Jaeger in the Kubernetes cluster. Make several requests to Flask; find the resulting traces in the Jaeger UI; identify latency at each span.

## Section 7.3 Log Management with Elastic Stack

### Theory

- Elastic Stack components: Elasticsearch (indexing and search), Logstash (parsing and enrichment), Kibana (visualization), Filebeat (lightweight shipper)
- Log pipeline: collection, parsing, indexing, visualization
- Structured vs. unstructured logs: why structured logging (JSON) makes downstream parsing trivial
- Index lifecycle management: keeping storage costs under control

### Labs

- **Lab 7.3.A Stack Setup:**

Install Elasticsearch and Kibana. Verify cluster health: `curl http://localhost:9200/_cluster/health`.

- **Lab 7.3.B Log Pipeline:**

Install Filebeat on the Apache VM; configure it to ship `/var/log/httpd/access_log`. Write a Logstash pipeline with a `grok` filter parsing Apache Combined Log Format. In Kibana, create an index pattern and filter entries by HTTP status code.

- **Lab 7.3.C Kibana Dashboard:**

Build a dashboard with three panels: request count over time (area chart), HTTP status code distribution (pie chart), and top 10 requested URLs (data table).

## Section 7.4 DevSecOps

### Theory

- Shifting security left: finding vulnerabilities at commit time costs far less than finding them in production
- OWASP Top 10: the vulnerabilities every DevOps engineer must recognize
- Secrets management: why `.env` files committed to Git end careers, and what to do instead
- SAST (Static Application Security Testing): analyzing source code without running it
- SCA (Software Composition Analysis): known vulnerabilities in third party dependencies
- Secrets scanning: detecting credentials, tokens, and keys committed to version control, in history as well as in current code
- Container image security: base image age, pinned tags, non root `USER`
- Rootless containers as a security control: the attack surface when root in a container maps to root on the host
- Least privilege in CI/CD: pipeline credentials should have the minimum scope to do their job

### Labs

- **Lab 7.4.A HashiCorp Vault:**

Install Vault in dev mode. Write a DB password: `vault kv put secret/myapp db_password=<value>`. Retrieve it from a GitHub Actions workflow step using the HashiCorp Vault Action. Compare to the insecure alternative of writing the password directly in the workflow YAML. Jenkins enterprise track: replicate using the Vault plugin in the Jenkinsfile.

- **Lab 7.4.B SAST and Dependency Scanning:**

Run Bandit against the Flask app: `bandit -r app/`. Resolve at least one finding. Run OWASP Dependency Check against the project. Add both as pipeline stages; fail the pipeline on HIGH severity findings.

- **Lab 7.4.C Trivy Image Scanning:**

Install Trivy. Scan the Flask image: `trivy image <name>`. Identify at least one HIGH/CRITICAL CVE; research it; apply the fix (usually: update the base image). Add Trivy as a pipeline stage; configure it to fail on CRITICAL findings.

- **Lab 7.4.D Secrets Scanning with gitleaks:**

Install `gitleaks`. Run a scan against the full Git history of the Flask repository: `gitleaks detect --source . --verbose`. Introduce a deliberate secret into a commit (a fake AWS access key in a config file) and verify gitleaks catches it. Remove the secret and confirm the scan passes clean. Add gitleaks as a pre-commit hook so secrets are caught before they reach the remote. Then add it as a step in the GitHub Actions workflow so any secret that slips past the hook is caught in the pipeline before it can spread further.

- **Lab 7.4.E Secrets Scanning with trufflehog:**

Install `trufflehog`. Run it against the GitHub repository using the GitHub integration: `trufflehog github --repo=<your-repo-url>`. Observe the difference in output between gitleaks (pattern matching) and trufflehog (entropy analysis and verified secrets). Introduce a second fake secret — a real-looking but invalid Stripe key — and compare which tool catches it and how each reports it. Write a short note: when you would reach for gitleaks vs. trufflehog, and why running both in CI is reasonable given their different detection approaches.

- **Lab 7.4.F Secure Jenkins *(Optional, Enterprise Track)*:**

Configure Jenkins to serve over HTTPS with a self signed cert. Set controller executors to zero (all builds on agents). Confirm the developer role cannot modify pipelines or access admin settings.

## Section 7.5 Project Management with Jira

### Theory

- Agile in Jira: Epics, User Stories, Tasks, Sub tasks; Sprint planning; Kanban boards
- Jira + Git integration: commit messages linking to issues, PR status in Jira
- Jira in a DevOps context: tracing a feature from backlog to deployed

### Labs

- **Lab 7.5.A Jira Setup:**

Create a Scrum or Kanban project. Create an Epic; write three User Stories under it; create a Sprint; assign stories; start the Sprint.

- **Lab 7.5.B Git Integration:**

Commit a code change with the Jira issue key in the message. Open a GitHub PR; verify it appears in the Jira issue's development panel. Move the issue to Done on merge.

---
# Module 8: Capstone Project

The capstone requires each student to design, build, and operate a complete application delivery pipeline demonstrating all competencies from Modules 1 through 7. Completed individually. Presented in a 15 minute walkthrough during the final session.

## Objective

A Git push on the developer's machine triggers a fully automated pipeline that tests, scans, signs, and deploys the application to a Kubernetes cluster, with zero manual steps in between, cluster policy enforcing what can run, progressive delivery controlling how it rolls out, full observability watching the result, and no credentials in any file.

---
## Mandatory Components

All twelve components are required.

**1. Application**

A web application in PHP or Python Flask. Must connect to a database, include at least one feature covered by automated tests, expose a `/health` and `/metrics` endpoint, and read all configuration from environment variables.

**2. Version Control**

Hosted on GitHub with a branching strategy (feature branches merged via PR). `main` is protected by branch protection rules. Conventional commits are enforced via `pre-commit`. gitleaks runs as a pre-commit hook.

**3. Containerization**

A multi stage `Dockerfile` producing a minimal, non root image. Image pushed to Docker Hub or private registry. SBOM generated with `syft` and attached as a build artifact. No credentials in the image.

**4. CI/CD Pipeline (GitHub Actions, primary)**

Stages in this order: checkout, secrets scan (gitleaks), unit tests (fail and halt on failure), SAST/dependency scan, image build and push, SBOM generation, cosign image signing, Trivy scan (fail on CRITICAL), deploy to Kubernetes. Jenkins enterprise track students may use a Jenkinsfile instead, but must invoke `make` targets so the commands are identical.

**5. Supply Chain Security**

Container image signed with `cosign` after push. Signature verified in the pipeline before deploy. The Kyverno policies in Component 8 enforce this at the cluster level.

**6. Infrastructure as Code**

Terraform provisions the deployment environment. Fully reproducible from `terraform apply`. Remote state in S3 with DynamoDB locking.

**7. Configuration Management**

Ansible configures the deployment target after Terraform provisions it. Playbooks are in the repository and idempotent.

**8. Policy as Code**

Kyverno is installed in the cluster with two policies active: deny privileged pods, require cosign verified images in the production namespace.

**9. Progressive Delivery**

Application deployed via an Argo Rollouts canary strategy. An AnalysisTemplate queries Prometheus for HTTP error rate. A deliberately broken deploy must trigger automatic rollback before the full canary promotion completes.

**10. Observability**

Prometheus and Grafana are deployed in the cluster. Grafana dashboard with four panels: CPU usage, memory usage, HTTP request rate, HTTP error rate. One Alertmanager rule configured. Jaeger deployed and the Flask app instrumented with OpenTelemetry.

**11. Security**

All credentials in HashiCorp Vault or GitHub Secrets. No credential appears in source code, Dockerfiles, pipeline definitions, or pipeline logs. gitleaks and trufflehog both pass clean against the repository.

**12. Disaster Recovery**

Velero installed and configured with an S3 backend. One backup taken and one successful restore demonstrated. Actual RTO documented and compared against a predefined target.

---
## Deliverables

| Deliverable | Description |
|---|---|
| GitHub Repository | App source, `Dockerfile`, `Makefile`, pipeline definition, Terraform config, Ansible playbooks, Kubernetes manifests, Kyverno policies, Argo Rollouts manifest, README with architecture diagram |
| Live Application | Accessible via browser or API at a stable URL or IP at the time of presentation |
| Grafana Dashboard Screenshot | Four live panels from the running application |
| Canary Rollback Evidence | Screenshot or recording of Argo Rollouts detecting a bad deploy and rolling back automatically |
| DR Report | One page document: backup taken, restore executed, actual RTO measured, bottleneck identified |
| 15 Minute Presentation | Full walkthrough: Git push to running app. Must include one problem encountered and how it was resolved. |

---
# Appendix: Tool and Technology Reference

| Area | Tools | Notes |
|---|---|---|
| Virtualization | VirtualBox, VMware Workstation | VirtualBox free; VMware Workstation Pro free for all users (commercial and personal) as of November 2024 |
| Linux | Fedora / CentOS Stream / RHEL 9, Ubuntu | RHEL family preferred for Red Hat alignment |
| Web Servers | Apache, Nginx | Core track; Tomcat optional Java enterprise track only |
| Web Servers *(optional)* | Apache Tomcat | Java enterprise track only |
| Version Control | Git, GitHub | pre commit, conventional commits, commitlint |
| CI/CD *(primary)* | GitHub Actions | Hosted runners, matrix builds, reusable workflows |
| CI/CD *(optional)* | Jenkins | Enterprise track; Docker agents; optional only |
| Build Tools | Make | Makefile wraps all pipeline steps in both CI tracks |
| Build Tools *(optional)* | Apache Maven | Java enterprise track only |
| Config Management | Ansible | Dynamic inventory, Vault integration, Jinja2 templates |
| Containers | Docker, Podman, Buildah | Docker Compose, Podman Compose |
| Orchestration | Kubernetes (Minikube, kubeadm), Helm, Kustomize, ArgoCD | |
| Progressive Delivery | Argo Rollouts | Canary + blue/green + metric based automatic rollback |
| Policy as Code | Kyverno | Cluster admission policies; OPA Gatekeeper mentioned as alternative |
| Supply Chain | syft, cosign | SBOM generation (SPDX); image signing and verification via Sigstore |
| Enterprise Kubernetes | Red Hat OpenShift | Developer Sandbox (free) |
| IaC | Terraform | Remote state, modules, Infracost |
| Cloud | AWS (EC2, S3, IAM, VPC, DynamoDB) | Free Tier account required |
| Monitoring | Prometheus, Alertmanager, Grafana, Node Exporter | SLO instrumentation |
| Tracing | OpenTelemetry, Jaeger | Vendor neutral instrumentation |
| Logging | Elastic Stack (Elasticsearch, Logstash, Kibana, Filebeat) | |
| Security | HashiCorp Vault, Trivy, Bandit, OWASP Dependency Check, gitleaks, trufflehog | Secrets + image scan + SAST + SCA + secrets scanning |
| Disaster Recovery | Velero | Namespace + PVC backup to S3; RPO/RTO measurement |
| Project Management | Jira | Scrum/Kanban, Git integration |

---
## Official Documentation

- GitHub Actions: https://docs.github.com/en/actions
- Jenkins *(enterprise track)*: https://www.jenkins.io/doc/
- Kubernetes: https://kubernetes.io/docs/
- Argo Rollouts: https://argoproj.github.io/rollouts/
- ArgoCD: https://argo-cd.readthedocs.io/
- Kyverno: https://kyverno.io/docs/
- cosign: https://docs.sigstore.dev/cosign/signing/overview/
- syft: https://github.com/anchore/syft
- gitleaks: https://github.com/gitleaks/gitleaks
- trufflehog: https://github.com/trufflesecurity/trufflehog
- OpenShift: https://docs.openshift.com/
- Terraform: https://developer.hashicorp.com/terraform/docs
- Ansible: https://docs.ansible.com/
- Prometheus: https://prometheus.io/docs/
- OpenTelemetry: https://opentelemetry.io/docs/
- Jaeger: https://www.jaegertracing.io/docs/
- Elastic Stack: https://www.elastic.co/docs/
- Velero: https://velero.io/docs/
- Infracost: https://www.infracost.io/docs/
- Google SRE Book: https://sre.google/sre-book/table-of-contents/
---
