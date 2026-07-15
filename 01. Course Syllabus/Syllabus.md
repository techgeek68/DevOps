# DevOps and Platform Engineering

---
*A curriculum spanning Linux systems fundamentals through cloud native and AI assisted delivery operations.*

---
## 1. Course Information

| Field | Details |
|---|---|
| Program title | DevOps and Platform Engineering |
| Course codes | DVP 101, DVP 201, DVP 301, and DVP 150 (Elective track) |
| Credit hours | 3, 4, 4, and 2 for the elective track |
| Academic level | Undergraduate / Professional Certificate |
| Total duration | 40 weeks across three sequential courses |
| Scheduled contact hours | 6 hours of instruction per week delivered as two sessions of 3 hours, plus 1 scheduled hour of supervised laboratory support |
| Independent study | 6 to 8 hours per week |
| Delivery mode | In person or synchronous online, cohort based, with recorded sessions. The program is not self paced. |

| Course | Focus | Duration |
|---|---|---|
| DVP 101: Foundations of Delivery Engineering | Linux administration, networking, version control, web and application services, testing, containers, and continuous integration | 12 weeks |
| DVP 201: Cloud Native Infrastructure and Delivery | Cloud fundamentals, infrastructure as code, configuration management, Kubernetes, observability, GitOps, and progressive delivery | 14 weeks |
| DVP 301: Reliability, Security, Platform, and AI Driven Operations | Site reliability engineering, chaos engineering, disaster recovery, secure delivery, supply chain integrity, service mesh, cost engineering, platform engineering, AI assisted operations, and capstone | 14 weeks |
| DVP 150: Enterprise and Legacy Stack (elective) | Enterprise Java delivery, alternate automation servers, the classic web stack, and enterprise container and log platforms | Approximately 25 hours, self paced |

---
## 2. Course Description

Software delivery has advanced through several distinct engineering eras: a traditional separation of development from operations, the emergence of automation and shared ownership under DevOps, the standardization of containers, orchestration, and infrastructure as code under the cloud native model, and the current transition in which AI assistants generate a growing share of code and infrastructure. In this present era the engineer is evaluated less on authoring speed and more on the ability to review, question, and operate generated artifacts safely.

This evaluation reflects a documented empirical finding. The DORA Accelerate research of 2024 and 2025 reports that AI adoption raises individual throughput while reducing team level delivery stability on average, with change failure rate and rework increasing unless the surrounding delivery system is already mature. AI adoption amplifies the maturity of the system it enters rather than correcting its weaknesses. Review discipline, automated quality gates, observability, and reliable rollback are therefore treated in this program as core engineering controls rather than optional ceremony.

The program teaches four layers in prerequisite order because a practicing engineer encounters legacy systems, cloud native systems, and AI assisted workflows within the same working week. Every concept is anchored to a laboratory exercise or an integrative project so that graduates leave with a demonstrable engineering portfolio.

---
**Complex engineering problems addressed.** 

The curriculum requires students to engage with problems that exhibit the recognized characteristics of complex engineering problems. Students confront conflicting technical and non technical requirements, for example, the direct tension between the GitOps principle that desired cluster state resides in version control and the security principle that credentials must never be committed. They design solutions with no single correct answer, such as selecting among canary deployment, blue green deployment, and feature flags under differing risk, cost, and reversibility constraints. They analyze systems with many interacting subcomponents, including networking, identity, orchestration, storage, and observability. They reason about consequences that extend beyond the technical domain, including cost exposure, data integrity during schema evolution, security blast radius, and the reliability commitments encoded in service level objectives. They also serve diverse stakeholders including developers, operators, security reviewers, and non technical decision makers, translating engineering findings into audience appropriate communication.

---
## 3. Prerequisites

The sole formal prerequisite is completion of the ungraded Module 0 primer, which establishes shell scripting, introductory programming, relational query, and structured data literacy. Prior professional Linux or networking experience is not required. The program is designed for graduates of Computer Science and Information Technology, Computer Applications, Computer Engineering, and Information Technology Engineering programs, and for early career practitioners seeking a structured path. A supervised support session precedes Week 1 for students who identify gaps during the primer self check.

Course level prerequisites are enforced as stated in Section 1.

---
## 4. Course Learning Outcomes

On successful completion of the program, students will be able to:

| Code | Course Learning Outcome |
|---|---|
| CLO 1 | Explain the software delivery lifecycle and the current DORA metric framework, and relate DevOps, site reliability engineering, and platform engineering as complementary engineering disciplines. |
| CLO 2 | Administer Linux systems, including identity, permissions, services, automation scripting, and systematic performance diagnosis. |
| CLO 3 | Analyze and design networks, including subnetting, name resolution, load balancing, and firewall and segmentation policy. |
| CLO 4 | Apply professional version control and collaborative engineering workflows, including structured code review and branch protection. |
| CLO 5 | Design and deploy web and application services, and construct delivery friendly applications governed by a layered automated test suite. |
| CLO 6 | Build, run, and secure containerized workloads using open container standards. |
| CLO 7 | Design continuous integration and continuous delivery pipelines authenticated through short lived federated credentials. |
| CLO 8 | Provision reproducible cloud infrastructure as code and converge configuration state using declarative and idempotent methods. |
| CLO 9 | Deploy, secure, and scale applications on Kubernetes and on managed clusters. |
| CLO 10 | Implement observability across metrics, logs, and distributed traces using vendor neutral open standards. |
| CLO 11 | Operate GitOps and progressive delivery with metric driven automatic rollback and safe, reversible database schema evolution. |
| CLO 12 | Apply site reliability, chaos, and disaster recovery practices, and quantify recovery objectives as measured engineering targets. |
| CLO 13 | Integrate security controls across the delivery lifecycle, including secrets management, static and composition analysis, supply chain integrity, and policy as code. |
| CLO 14 | Evaluate advanced traffic management, multi cloud portability, cost engineering, and platform engineering, and communicate findings to technical and non technical audiences. |
| CLO 15 | Apply AI assisted engineering responsibly, evaluate its measured effect on delivery stability, and threat model the risks introduced by autonomous tooling. |
| CLO 16 | Integrate the complete toolchain into an automated, observable, secure delivery platform, and defend the design decisions under examination. |

---
---
## 5. Module 0: Preparatory Primer

**Objectives.** 

Establish the foundational literacy assumed by Week 1 so that later modules do not silently depend on unstated prerequisites. Self paced and ungraded, completed before instruction begins.

**Topics and subtopics.**
- Shell scripting fundamentals: variables, conditionals, loops, functions, exit codes, quoting, pipes, and redirection.
- Introductory programming: variables, control flow, functions, file input and output, and package installation, sufficient to read and modify a small web application.
- Relational query fundamentals: selection, insertion, update, joins, and the meaning of a connection string.
- Structured data literacy: indentation, key and value structure, lists compared with maps, and equivalent representations across serialization formats.
- Version control essentials: clone, add, commit, and push.

**Assessment.** 

A short ungraded self check identifies students who should attend the pre course support session.

---
---
# DVP 101: Foundations of Delivery Engineering

Twelve weeks, two sessions of three hours each per week.

---
## Module 1: The Delivery Engineering Mindset

**Objectives.** 

Establish the conceptual frame for the program: the delivery lifecycle, measurable delivery performance, and the relationship among the delivery disciplines. Supports CLO 1.

**Topics and subtopics.**

- The delivery lifecycle: plan, code, build, test, release, deploy, operate, and monitor.
- Agile and DevOps as complementary rather than competing models.
- Site reliability engineering alongside DevOps: error budgets, service level indicators, objectives, and agreements, and when each model applies.
- The DORA metric framework as an evolving research program. Students distinguish throughput metrics from stability metrics, apply the current definition of failed deployment recovery time, and treat rework as a distinct dimension, verifying definitions against the current published guidance rather than legacy summaries.
- The documented relationship between AI adoption and delivery stability is stated at the outset because it motivates the structure of the entire program.
- Infrastructure as code as a concept and the shift from interactive provisioning to declarative provisioning.
- Architectural trade offs between microservices and monoliths.

**Practical laboratories.**

- Lab 1A. Measure deployment frequency and lead time for changes from the public history of a real open source project, then argue with evidence why change failure rate, failed deployment recovery time, and rework cannot be derived from public data and what instrumentation would be required to measure them.
- Lab 1B. Compute error budgets across several availability targets over a thirty day window, evaluate outage scenarios against the remaining budget, and design a matched service level indicator, objective, and agreement for a chosen service.
- Lab 1C. Compare manual configuration against a small idempotent script across two identical virtual machines, introduce undocumented drift into one, and evaluate the difficulty of determining and reproducing each machine's state. This exercise is revisited with declarative tooling in Module 9.
- Lab 1D. Assess the delivery baseline of a described organization with a manual, single person dependent process, then design a target lifecycle, a ninety day improvement plan, an initial objective, and a concrete remedy for single person deployment dependency.

**Assignments.** 

Written analysis of the DORA baseline for a case organization, with an argued improvement roadmap.

---
## Module 2: Linux and Systems Fundamentals

**Objectives.** 

Develop competent administration of Linux systems as the substrate for all later work. This is the longest module because its compression is a common cause of failure in delivery engineering instruction. Supports CLO 2.

**Topics and subtopics.**

- Rationale for Linux as the default platform, and the distinction between hypervisors and containers as a bridge to Module 6.
- Filesystem hierarchy and core commands for navigation, inspection, and manipulation.
- Text processing with pattern matching, stream editing, and field extraction pipelines.
- Compression and archiving.
- Identity and access: users, groups, permissions in symbolic and octal form, privilege delegation, special permissions, and access control lists.
- Package management across major distribution families and installation from source.
- Service management with the system and service manager, including unit files, targets, and the journal.
- Shell environment configuration and scripting in practice, including arrays, control structures, functions, here documents, debugging, exit status, and signal handling.
- Scheduling with recurring jobs and timers.
- Log management and rotation.
- Process control, monitoring, and introductory performance tuning across the processor, memory, disk, and network dimensions.
- Host networking utilities, firewall configuration, storage mounting, terminal multiplexing, and secure shell configuration and hardening.

**Practical laboratories.**

- Lab 2A. Build a Linux virtual machine, configure hostname and static addressing, and enforce key based secure shell access only.
- Lab 2B. Complete a documented skills exercise across navigation, text processing, permission management, identity management, package installation, process control, and firewall rules.
- Lab 2C. Author a health check script that accepts a service argument, evaluates state, logs a timestamped result, returns a correct exit code, and runs on a schedule.
- Lab 2D. Reimplement the same check as a service unit and timer, verify execution through the journal, and justify the choice of timer over recurring job scheduling.
- Lab 2E. Perform performance triage on a degraded virtual machine using command line tools only, identifying the true bottleneck among deliberate distractors and documenting the diagnostic path. This exercise develops experimentation and data interpretation skills for ABET Student Outcome six.

**Assignments.** 

A documented diagnostic report from the performance triage exercise.

---
## Module 3: Networking Fundamentals

**Objectives.** 

Enable analysis and design of the networks a delivery engineer operates. Supports CLO 3.

**Topics and subtopics.**

- The layered network model is restricted to the layers a delivery engineer touches, and the discipline of diagnosing from the bottom upward.
- Transport protocols, the connection handshake, ports, sockets, connection states, and port exhaustion.
- Routing tables, default gateways, and static and dynamic routing at a conceptual level.
- Name resolution records, time to live management, and split horizon resolution.
- Load balancing at the transport and application layers, distribution algorithms, session affinity, and health checking.
- Stateful and stateless firewalls, default deny posture, security groups, and network access control lists.
- Address assignment, network address translation, private and public addressing, and classless addressing.
- Subnetting arithmetic, and the rationale for several small segments over one large segment.
- Outbound only connectivity for private segments through managed translation.
- Transport layer security and the certificate trust chain.
- Common failure modes, including overlapping address ranges, undersized segments, neglected propagation delay during cutover, and overly permissive temporary rules.

**Practical laboratories.**

- Lab 3A. Diagnose a deliberately broken resolution and routing scenario using standard tools, documenting what each tool reported and the order of investigation.
- Lab 3B. Given a fixed address block, calculate the mask, broadcast address, and usable host range, then design a three tier segmented network on paper for later physical realization in Module 8. This design exercise supports ABET Student Outcome one.
- Lab 3C. Connect two machines on separate segments using static routes and evidence the routing table before and after.

**Assignments.** 

A written subnet design with justification, carried forward for comparison in Module 8.

---
## Module 4: Version Control and Collaborative Engineering Workflows

**Objectives.** 

Establish professional collaborative workflows, with emphasis on review as the emerging majority of engineering work. Supports CLO 4.

**Topics and subtopics.**

- Distributed version control as a mental model rather than a history log.
- Branching strategies and their trade offs across team sizes.
- Pull requests and code review, and what distinguishes a substantive review from a formality.
- Conventional commit conventions and their payoff in automated versioning, changelog generation, and release automation.
- Developer machine safeguards through commit hooks.
- Signed commits and branch protection as baseline hygiene.
- Issue tracking and traceability from backlog to production.

**Practical laboratories.**

- Lab 4A. Execute the full collaboration cycle across two clones, including a deliberate merge conflict and its resolution.
- Lab 4B. Demonstrate with evidence the difference between history rewriting and safe reversal on a shared branch, and articulate the correct response to a colleague who force pushed to the main branch. This exercise develops professional communication for ABET Student Outcome Three.
- Lab 4C. Configure a repository with ignore rules, commit hooks including secret scanning, branch protection requiring review and passing checks, enforced commit conventions, and an automated release that produces a version and changelog on merge.
- Lab 4D. Build a project board, trace one feature from epic through pull request to automatic issue closure on merge.

**Assignments.** 

A configured repository demonstrating the full governance and release automation chain.

---
## Module 5: Web Servers, Applications, and Testing Strategy

**Objectives.** 

Deploy web and application services and construct a delivery friendly reference application governed by a layered test suite. Supports CLO 5.

**Topics and subtopics.**

- The distinction between web servers and application servers and where each sits.
- Process models, virtual hosts, and reverse proxying for the two dominant web servers.
- Transport layer security termination and the engineering choice of where to terminate.
- Properties that make an application friendly to automated delivery: environment sourced configuration, testable units, and repeatable builds.
- The enduring and the dated elements of the twelve factor model.
- Testing strategy as a first class engineering concern: the test pyramid, contract testing, test data management, and the engineering decision to quarantine a flaky test.
- Pipeline speed as a product feature, addressed through caching, parallelism, and selective scheduling.

**Practical laboratories.**

- Lab 5A. Serve two named virtual hosts with transport layer security using a locally issued certificate and customized logging.
- Lab 5B. Configure static serving, reverse proxying, and load balanced upstream distribution.
- Lab 5C. Build the reference application carried through the program: a small service exposing health, metrics, and at least one feature endpoint, configured entirely from the environment, connected to a real database, with no embedded credentials.
- Lab 5D. Author a layered test suite with unit and integration coverage against a containerized database, diagnose and repair a deliberately flaky test, and record total suite runtime as a controlled metric. This experimentation and measurement exercise supports ABET Student Outcome Six.
- Lab 5E. Introduce a schema migration tool and commit the first migration, which becomes decisive for reversible rollback in Module 15.

**Assignments.** 

The reference application and its measured, layered test suite.

---
## Module 6: Containers and Open Container Standards

**Objectives.** 

Build, run, and secure containerized workloads using open standards. Supports CLO 6.

**Topics and subtopics.**

- The problems containers solve: environment parity, dependency isolation, and rapid startup.
- Containers compared with virtual machines.
- Open container standards for image, runtime, and distribution, and their role in portability.
- Image layering, layer caching, and the effect of layer order on build time.
- Multi stage builds that separate build dependencies from the runtime image.
- Daemon based and daemonless container architectures, and rootless execution as a security control rather than a preference.
- Image vulnerability scanning: the meaning and limits of a vulnerability identifier and severity score, the effect of base image currency, and the difference between a reported vulnerability and an exploitable one. Scanning recurs for infrastructure in Module 9 and for pipeline gating in Module 19.

**Practical laboratories.**

- Lab 6A. Containerize the reference application with a clean build context.
- Lab 6B. Convert to a multi stage build and compare image size and vulnerability count, reasoning about which removed findings were ever reachable. This is a controlled before and after measurement supporting ABET Student Outcome six.
- Lab 6C. Run the image rootless and prove it, then generate a Kubernetes style manifest retained for Module 11.
- Lab 6D. Compose the application and its database with persistent volumes and environment sourced credentials across two compatible runtimes.
- Lab 6E. Tag and publish the image manually so the mechanics precede their automation in Module 7.

**Assignments.** 

A hardened multi stage image with a documented vulnerability comparison.

---
## Module 7: Continuous Integration

**Objectives.** 

Design continuous integration pipelines authenticated by short lived federated credentials. Supports CLO 7.

**Topics and subtopics.**

- Pipeline vocabulary: workflow, event, job, step, runner, secret, and environment.
- Reusable workflows, composite actions, and matrix builds.
- Approval gated environments.
- Self hosted runners and their appropriate use.
- Federated authentication through short lived credentials as the default, so that no static cloud key is ever stored. Long lived keys in a pipeline are treated as a standing liability.
- A build wrapper that makes local, hosted, and alternate orchestrations invoke identical commands.
- Artifact versioning, pinning, and the reading of pipeline cost.

**Practical laboratories.**

- Lab 7A. Build a first workflow that installs dependencies, runs tests, and publishes status.
- Lab 7B. Extend to a matrix across multiple runtime versions.
- Lab 7C. Introduce a build wrapper so the pipeline invokes named targets rather than inline commands.
- Lab 7D. Add a container build and publish step.
- Lab 7E. Extract the test job into a reusable workflow invoked from a second repository.
- Lab 7F. Repair a pipeline seeded with four planted faults under time pressure and document the diagnostic process. This exercise is the model for the practical checkpoints and directly develops ABET Student Outcome six.

**Assignments.** 

A reusable, versioned integration pipeline for the reference application.

---
### DVP 101 Weekly Schedule

| Week | Modules | Focus | Deliverables |
|---|---|---|---|
| 1 | 1 | Delivery mindset, DORA, reliability, drift | Labs 1A, 1B |
| 2 | 1 and 2 | Case study, Linux foundations begin | Labs 1D, 2A |
| 3 | 2 | Text processing, permissions, packages | Lab 2B |
| 4 | 2 | Service management, scripting, scheduling, logs | Labs 2C, 2D |
| 5 | 2 and 3 | Processes, performance, secure shell, networking begins | Lab 2E |
| 6 | 3 | Transport, resolution, load balancing, subnetting | Labs 3A, 3B |
| 7 | 3 and 4 | Networking, then version control | Labs 3C, 4A |
| 8 | 4 | Collaborative workflows and governance. Checkpoint 1.1 | Labs 4B, 4C, 4D |
| 9 | 5 | Web services, application design, testing strategy | Labs 5A, 5B, 5C |
| 10 | 5 and 6 | Test suite, containers begin | Labs 5D, 5E, 6A |
| 11 | 6 | Multi stage, rootless, compose, registry | Labs 6B, 6C, 6D, 6E |
| 12 | 7 | Continuous integration. Checkpoint 1.2 | Labs 7A through 7F |

---
# DVP 201: Cloud Native Infrastructure and Delivery

Fourteen weeks. Observability is scheduled before progressive delivery because metric driven rollback cannot be taught without established metrics.

---
## Module 8: Cloud Fundamentals and Cost Guardrails

**Objectives.** 

Establish cloud fundamentals and cost control as an engineering discipline. Supports CLO 8. This module introduces economic constraint as a first class design consideration for ABET Student Outcome two.

**Topics and subtopics.**

- Cloud service models and their mapping to real services.
- Global infrastructure: regions, availability zones, and local zones.
- Identity and access management with least privilege as the default.
- Virtual private networks: public and private segments, gateways, translation, route tables, and layered controls.
- Elastic compute: machine images, instance types, instance profiles, and initialization.
- Object storage: policies, versioning, and lifecycle rules.
- Cost as an engineering constraint: distinguishing genuine free allowances from apparent ones, identifying the most common sources of unexpected charges, reading cost reporting, and treating teardown as a required habit.

**Practical laboratories.**

- Lab 8A. The billing guardrail exercise, completed before any other cloud work: configure a budget, a warning alarm, and a hard alarm routed to a monitored address, then deliberately trip the warning alarm and evidence that it fired. Students on the equitable access path complete an equivalent instrumented budget simulation, described in Appendix B.
- Lab 8B. Launch a compute instance, serve traffic, and decommission it with evidence of an empty console.
- Lab 8C. Construct a permission boundary, prove it holds, then attach an instance role that reads object storage with no static keys, and justify why the role based approach is superior.
- Lab 8D. Build the segmented network designed on paper in Lab 3B, prove that the private instance reaches the internet outbound only, compare against the paper design, then decommission the costly translation component the same day and quantify the avoided cost.
- Lab 8E. Configure versioning, lifecycle rules, and a bucket policy, then break and repair the policy to observe the failure mode.

**Assignments.** 

A cost controlled network deployment with a written comparison against the Module 3 design.

---
## Module 9: Infrastructure as Code

**Objectives.** 

Provision reproducible infrastructure declaratively and manage state safely. Supports CLO 8.

**Topics and subtopics.**

- Declarative infrastructure and desired state as the core model.
- State: what it tracks, why its loss is costly, and why it must never reside in version control.
- The provisioning workflow, and the discipline of reading the plan before every apply, especially when the definition was generated by an assistant.
- State locking and environment isolation without duplication.
- Modules as the unit of reuse.
- Licensing awareness: the migration of major provisioning and secrets tools from open source to source available licenses, the community forks that resulted, the corporate acquisition that followed, and the general lesson of knowing the license of any tool on which a platform depends.

**Practical laboratories.**

- Lab 9A. Provision compute and a security group, then verify and decommission.
- Lab 9B. Parameterize the definition and publish an output.
- Lab 9C. Move the state to remote storage with locking and observe the lock blocking a concurrent apply.
- Lab 9D. Refactor into a reusable module invoked with two distinct inputs.
- Lab 9E. Integrate automated cost estimation into pull requests and confirm that a cost tripling change is caught. This exercise supports economic evaluation under ABET Student Outcome Two.
- Lab 9F. Introduce drift through the console, detect it through the plan, and correct it, then compare directly against the manual drift exercise of Lab 1C.
- Lab 9G. Add configuration scanning to the pipeline and remediate at least one real finding.

**Assignments.** A modular, scanned, cost estimated infrastructure definition with remote state.

---
## Module 10: Configuration Management

**Objectives.** 

Converge configuration state idempotently and integrate provisioning with configuration. Supports CLO 8.

**Topics and subtopics.**

- Agentless architecture over secure shell.
- Static and dynamic inventory, including cloud discovery.
- Idempotency and its empirical verification through a second run that changes nothing.
- The complementary relationship between provisioning and configuration convergence.
- Templating, variables, and filters.
- Encrypted secrets at rest in the repository.
- Roles and the standard directory layout.

**Practical laboratories.**

- Lab 10A. Establish a control node, write a grouped static inventory, and run ad hoc commands before writing any playbook, so that the gap between a single command and a repeatable playbook is experienced directly.
- Lab 10B. Author a playbook that installs and configures a web server, deploys the reference application as a managed service, restarts only on genuine change, encrypts the database credentials, and proves idempotency on a second run.
- Lab 10C. Convert the playbook into a proper role with templated configuration.
- Lab 10D. Discover provisioned instances through dynamic inventory and configure them with the role, so the provisioning to configuration boundary becomes concrete.

**Assignments.** 

A role driven configuration pipeline integrated with dynamic inventory.

---
## Module 11: Kubernetes Fundamentals

**Objectives.** 

Deploy and operate applications on Kubernetes and on managed clusters. Supports CLO 9.

**Topics and subtopics.**

- Control plane and worker node components.
- Core workload objects and their appropriate use.
- Service types and their exposure semantics.
- Ingress and its successor gateway model, with the operator and developer role split, and how to recognize which is in use.
- Resource requests, limits, and the noisy neighbor problem.
- Liveness, readiness, and startup probes as the basis of self healing.
- Configuration and secret objects, and the plain fact that a cluster secret is encoded rather than encrypted, whose consequences are addressed in Module 14.
- Persistent storage abstractions.
- Rolling updates and rollback.
- Role based access control.
- Cluster name resolution and its debugging.
- Managed Kubernetes and the rationale for not self operating a control plane.

**Practical laboratories.**

- Lab 11A. Apply, scale, expose, update, and roll back a deployment on a local cluster.
- Lab 11B. Add probes and limits, observe self healing, then misconfigure a probe to observe a healthy pod killed in a loop, a real world failure mode.
- Lab 11C. Wire configuration and secret objects into a pod, apply the manifest generated in Lab 6C, and compare it against manifests written by hand.
- Lab 11D. Route paths through an ingress controller, then reproduce the routing with the gateway model and evaluate what the newer model provides.
- Lab 11E. Debug cluster name resolution from inside a pod.
- Lab 11F. Package the application with a chart and with an overlay tool, and articulate when each is appropriate.
- Lab 11G. Provision a managed cluster with infrastructure as code, deploy the application, and decommission the cluster at the end of the session.

**Assignments.** 

The reference application was deployed to both a local and a managed cluster with documented configuration parity.

---
## Module 12: Kubernetes in Production

**Objectives.** 

Secure and scale clusters to a production standard. Supports CLO 9. Health, safety, and welfare considerations under ABET Student Outcome Two are made concrete through least privilege, admission control, and network isolation.

**Topics and subtopics.**

- Least privilege access control for automation identities, and why broad administrative rights in a pipeline repeat the mistake of a static key.
- Built in workload security admission at the baseline and restricted levels, taught before any external policy engine so that the platform's native controls are understood first.
- Default deny east west network policy as the unglamorous first step of zero trust, and the network plugin support it requires.
- Namespaces, quotas, and limit ranges as a multi tenancy story.
- Storage in practice and the distinction between stateful and stateless workloads.
- Horizontal and vertical autoscaling, node level autoscaling, and the dependency of the autoscaler on accurate requests and limits.

**Practical laboratories.**

- Lab 12A. Bind an automation identity to a minimal role, prove it cannot read secrets, and capture the exact denial.
- Lab 12B. Apply restricted workload security to a namespace, observe rejection, and remediate the application until it is admitted.
- Lab 12C. Impose a default deny network policy, observe the resulting breakage, and open only the required paths.
- Lab 12D. Impose quotas and limit ranges and observe the enforcement errors.
- Lab 12E. Configure horizontal autoscaling against request rate, load test it, then collect real utilization data, right size requests and limits, and quantify the monthly saving. This experiment connects measured data to an economic outcome under ABET Student Outcomes two and six.

**Assignments.** 

A hardened namespace with a quantified right sizing analysis.

---
## Module 13: Observability on Open Standards

**Objectives.** 

Implement observability across metrics, logs, and traces using vendor neutral standards. Supports CLO 10.

**Topics and subtopics.**

- Metrics, logs, and traces, and what each answers that the others cannot.
- Vendor neutral instrumentation that allows a single instrumentation to export to any backend.
- The metric data model, host metric collection, and the core query patterns for rate, increase, and quantile estimation.
- Alert routing, grouping, inhibition, and silencing, and alert fatigue as the dominant failure mode of monitoring.
- Dashboards, variables, and annotations.
- Structured logging.
- Cardinality, and how one poorly chosen label can destabilize a metrics store.

**Practical laboratories.**

- Lab 13A. Deploy metric collection into the cluster, confirm targets, and instrument the application to export metrics and traces from a single instrumentation.
- Lab 13B. The author queries for request rate, error rate, and tail latency from a histogram, then deliberately introduces a high cardinality label, observes memory growth, and removes it. This controlled experiment supports ABET Student Outcome Six.
- Lab 13C. Build a dashboard of core service signals.
- Lab 13D. Route a real alert to a channel, then author a deliberately noisy alert and document the effect of alert fatigue on an on call engineer.
- Lab 13E. Slow a query deliberately and trace the same fault through a metric, a span, and a log line, evaluating the value of correlated signals.

**Assignments.** 

An instrumented service with dashboards, alerting, and tracing.

---
## Module 14: Continuous Delivery, GitOps, and Cluster Secrets

**Objectives.** 

Operate GitOps delivery and resolve the secrets problem it creates. Supports CLO 11 and CLO 7.

**Topics and subtopics.**
- Push based delivery contrasted with pull based GitOps.
- The application resource, sync policies, health status, self healing, and cluster level drift detection.
- Federated authentication as the modern replacement for long lived cloud keys.
- The GitOps secrets problem and its three established resolutions: encryption into version control with in cluster decryption, a reference in version control with the value in an external store, and injection at pod start. Students build one and can defend the trade offs of the others. This is a complex engineering problem with conflicting correct principles under ABET Student Outcome Two.

**Practical laboratories.**

- Lab 14A. Add a real deploy stage that applies manifests to a managed cluster.
- Lab 14B. Establish federated authentication, replace static keys with a scoped short lived role, delete the static keys, and analyze the blast radius difference between a leaked static key and a leaked short lived credential with specific timelines.
- Lab 14C. Install the delivery controller, observe synchronization from version control, and observe reversion of a manual cluster change.
- Lab 14D. Introduce a secret into the GitOps flow without committing it, using an external secret operator backed by a real store, and prove through a full history search that the secret value appears nowhere in the repository.

**Assignments.** 

A GitOps delivery flow with externally sourced secrets and evidenced repository cleanliness.

---
## Module 15: Progressive Delivery, Feature Flags, and Safe Migrations

**Objectives.** 

Operate progressive delivery with metric driven rollback and reversible schema evolution. Supports CLO 11.

**Topics and subtopics.**

- Canary and blue green delivery as alternatives to a plain rolling update.
- Automated rollback driven by a real metric, made possible by the observability established in Module 13.
- Feature flags as the separation of deployment from release, their advantages, and the cost of flag debt.
- Database migrations and the rollback that appears to succeed while the application remains broken because the code rolled back and the data did not. The remedy is the expand and contract pattern, in which every schema change is split into a backward compatible expansion, a deploy, and a later contraction, so that a reversible deploy remains reversible. This is the reason the migration tool was introduced in Lab 5E.

**Practical laboratories.**

- Lab 15A. Convert the deployment to a canary governed by an analysis that queries error rate, ship a deliberately broken version, and observe automatic rollback before promotion.
- Lab 15B. Configure a blue green rollout with instant cutover and abort based rollback, and justify when it is preferable to a canary.
- Lab 15C. Introduce a feature flag, ship code dark, enable it for a fraction of traffic without deploying, disable it in seconds, and compare the experience honestly against Lab 15A.
- Lab 15D. Demonstrate the rollback that lies by shipping a destructive migration and observing dashboards report success while the service remains broken, then reimplement with expand and contract and demonstrate a rollback that genuinely restores service. This capstone laboratory of the course integrates data integrity as a safety consideration under ABET Student Outcome Two.

**Assignments.** 

A demonstrated reversible schema change under automated progressive delivery.

---
### DVP 201 Weekly Schedule

| Week | Modules | Focus | Deliverables |
|---|---|---|---|
| 1 | 8 | Cloud fundamentals, identity, cost guardrails | Labs 8A, 8B, 8C |
| 2 | 8 | Network, compute, storage | Labs 8D, 8E |
| 3 | 9 | Infrastructure as code: state and workflow | Labs 9A, 9B, 9C |
| 4 | 9 | Modules, drift, scanning, cost | Labs 9D through 9G |
| 5 | 10 | Configuration management foundations | Labs 10A, 10B |
| 6 | 10 and 11 | Roles, dynamic inventory, Kubernetes begins. Checkpoint 2.1 | Labs 10C, 10D |
| 7 | 11 | Objects, services, probes, configuration | Labs 11A through 11C |
| 8 | 11 | Ingress, gateway, packaging, managed clusters | Labs 11D through 11G |
| 9 | 12 | Access control, admission, network policy, storage | Labs 12A through 12D |
| 10 | 12 | Autoscaling and right sizing | Lab 12E |
| 11 | 13 | Metrics, query language, instrumentation | Labs 13A, 13B |
| 12 | 13 | Dashboards, alerting, tracing, structured logs | Labs 13C through 13E |
| 13 | 14 | GitOps, federated identity, cluster secrets | Labs 14A through 14D |
| 14 | 15 | Progressive delivery, flags, safe migrations. Checkpoint 2.2 | Labs 15A through 15D |

---
# DVP 301: Reliability, Security, Platform, and AI Driven Operations

Fourteen weeks. The capstone begins in Week 1 and is built incrementally as each module lands.

---
## Module 16: Site Reliability Practices and Incident Response

**Objectives.** 

Apply reliability engineering and structured incident response. Supports CLO 12. Teamwork under ABET Student Outcome Five is developed through the paired incident simulation.

**Topics and subtopics.**

- Indicators, objectives, and error budgets as an engineering discipline, and the error budget as a negotiated permission to ship.
- On call structure, escalation, severity, and the authority to declare an incident.
- Incident command roles and why role separation shortens incidents.
- Incident communication discipline.
- Blameless postmortems and why blame degrades systems.
- Introductory capacity planning.

**Practical laboratories.**

- Lab 16A. Define real objectives, instrument the matching indicators, and build a burn rate alert.
- Lab 16B. Connect an alert to a paging tool and walk the full escalation path.
- Lab 16C. Conduct a paired incident simulation in which each student in turn runs a real incident on a partner introduced fault, communicating on a schedule, mitigating, and authoring a blameless postmortem with timeline, root cause, and follow up actions. This exercise develops teamwork and communication under ABET Student Outcomes three and five.

**Assignments.** 

A blameless postmortem from the incident simulation.

---
## Module 17: Chaos Engineering and Resilience

**Objectives.** 

Test resilience deliberately and interpret the response. Supports CLO 12.

**Topics and subtopics.**

- Resilience as a tested property rather than an assumed one.
- The distinction between a chaos experiment and an outage: a written hypothesis, a bounded blast radius, and a stop mechanism.
- Selection of a sensible first blast radius.

**Practical laboratories.**

- Lab 17A. Author a hypothesis in advance, run one contained fault injection experiment, and document what recovered automatically, what did not, and the resulting design change. A result in which nothing surprising occurred is a valid outcome and is written up as such. This exercise embodies hypothesis driven experimentation under ABET Student Outcome Six.

**Assignments.** 

A documented chaos experiment with hypothesis, result, and design conclusion.

---
## Module 18: Disaster Recovery and Business Continuity

**Objectives.** 

Execute recovery exercises and quantify recovery objectives. Supports CLO 12.

**Topics and subtopics.**

- Recovery point and recovery time objectives as concrete measured numbers.
- Backup strategies and their trade offs in cost, speed, and complexity.
- Cluster state backup as distinct from workload and volume backup.
- The gap between possessing a backup and having a proven restore.

**Practical laboratories.**

- Lab 18A. Set a recovery time target in advance, back up and restore a full namespace, measure actual recovery time against the target, identify the bottleneck if the target is missed, and write a one page postmortem. This exercise requires quantitative comparison of measured results against a specified target under ABET Student Outcome Six.
- Lab 18B. Schedule recurring database dumps to object storage and prove data integrity through a restore into a fresh database.

**Assignments.** 

A measured recovery exercise with a written continuity analysis.

---
## Module 19: Security Across the Delivery Lifecycle

**Objectives.** 

Integrate security controls throughout the pipeline. Supports CLO 13. Professional and ethical responsibility under ABET Student Outcome Four is developed through secure handling of credentials and data.

**Topics and subtopics.**

- Shifting security earlier, with the cost argument for early detection.
- The prevailing catalogue of application security risks at a working level.
- Secrets management and the licensing awareness that parallels Module 9.
- Static analysis and software composition analysis.
- Image scanning, base image currency, pinned references, and non root execution.
- Dependency update automation as the necessary complement to scanning, since a scan without a remediation path produces an unread report.
- Secrets scanning across current code and full history.
- Rootless execution as a real control, connecting to Module 6.
- Zero trust as a mental model with network policy as its first step.
- Least privilege in the pipeline as a running theme.

**Practical laboratories.**

- Lab 19A. Retrieve a secret from a managed store into a pipeline step rather than a workflow file, and repeat against the community fork to observe how little it changes.
- Lab 19B. Add static and composition analysis as failing gates, then handle a false positive through a documented suppression rather than by disabling the check.
- Lab 19C. Remediate a real critical finding in the image and add scanning as a gate.
- Lab 19D. Detect a planted credential across full history, add secret scanning as both a commit hook and a pipeline step, compare pattern based against entropy and verification based detection, and articulate when each is appropriate.
- Lab 19E. Enable dependency update automation, review and merge a generated update, then configure automatic merging for low risk updates only and justify where the line was drawn.

**Assignments.** 

A pipeline with integrated security gates and a documented remediation.

---
## Module 20: Supply Chain Security and Policy as Code

**Objectives.** 

Establish supply chain integrity and enforce policy as code. Supports CLO 13.

**Topics and subtopics.**

- Real supply chain compromises and why they succeeded, with a clear distinction between a supply chain compromise and a dependency vulnerability, which are frequently conflated.
- Software bills of materials and the two dominant formats.
- Image signing and keyless signing.
- Admission control, and the difference between a validating and a mutating webhook.
- Policy expressed as native cluster resources, with the reminder to verify what native workload security already provides before installing a policy engine.
- The maturity framework these practices ladder toward and its concrete levels.

**Practical laboratories.**

- Lab 20A. Generate a bill of materials, attach it as an artifact, then use it to locate every image in the cluster containing a given library.
- Lab 20B. Sign the image and add a verification gate that refuses unsigned images, confirmed by a rejected unsigned deployment.
- Lab 20C. Enforce policies that block privileged workloads and require verified signatures in production, then identify which of these native workload security features could have been enforced without a policy engine.

**Assignments.** 

A signed, verified supply chain with an enforced admission policy.

---
## Module 21: Service Mesh and Advanced Traffic Management

**Objectives.** 

Evaluate service mesh architectures and advanced traffic control. Supports CLO 14.

**Topics and subtopics.**

- What a mesh adds atop cluster networking and what it does not.
- The current architecture landscape: the per pod proxy model, the shared node level model, and kernel based approaches, and the trade off between resource overhead and isolation.
- Mutual transport layer security for east west traffic.
- Traffic shifting as a mechanism distinct from changing replica counts.
- Distribution and support realities that affect tool selection at an organizational level, including release and licensing considerations, and the current mechanism for traffic shifting through the gateway routing model rather than deprecated resources.

**Practical laboratories.**

- Lab 21A. Inject a mesh into the application namespace, confirm traffic encryption, and compare the mesh golden metrics against the application's own reporting.
- Lab 21B. Shift a fraction of traffic to a second version using a weighted route, then articulate how this differs from the earlier progressive delivery rollout and when both would be used together.

**Assignments.** 

A mesh enabled namespace with a documented weighted traffic shift.

---
## Module 22: Multi Cloud, Serverless, and Cost Engineering

**Objectives.** 

Evaluate portability, serverless fit, and cost engineering, and communicate findings across audiences. Supports CLO 14. Communication under ABET Student Outcome three is directly assessed.

**Topics and subtopics.**

- The five primitives every major cloud shares under different names: identity and access, virtual networking, object storage, managed compute, and managed databases.
- Where the equivalence breaks down, particularly in identity trust models, which genuinely differ.
- Where serverless fits alongside containers, including cold starts and operational trade offs.
- Cost engineering at the level a delivery engineer requires: tagging and allocation, right sizing, capacity commitment, and the elimination of unused resources.

**Practical laboratories.**

- Lab 22A. Deploy one function and compare its operational profile against the same logic in a container across deploy time, cold start, observability, and cost at low and high request volumes.
- Lab 22B. Identify, on paper, exactly what would change to port an existing infrastructure module to another provider, specifying which changes are trivial and which are not. This design analysis supports ABET Student Outcome Two.
- Lab 22C. Convert the technical right sizing of Lab 12E into a one page memorandum for a non technical executive audience, including current spend, proposed spend, the risk of error, and a validation plan. This exercise directly assesses communication with a range of audiences under ABET Student Outcome three.

**Assignments.** 

A portability analysis and an executive cost memorandum.

---
## Module 23: Platform Engineering

**Objectives.** 

Evaluate platform engineering, golden paths, and internal developer platforms. Supports CLO 14.

**Topics and subtopics.**

- The cognitive load argument for platform engineering and how its absence produces shadow systems.
- Golden paths and internal developer platforms as a catalogue rather than a single tool, where a golden path is a paved road and not a fence.
- A reference open source implementation.
- Platform as a product whose users are engineers.
- The relationship between the program capstone and what a real platform team provides on day one.

**Practical laboratories.**

- Lab 23A. Explore a reference platform and map previously built artifacts onto catalogue templates.
- Lab 23B. Document the day one developer experience for the student's own project with and without a golden path, quantifying the difference in steps, decisions, and failure modes. This quantitative comparison supports ABET Student Outcome Six.

**Assignments.** 

A golden path definition with a quantified value analysis.

---
## Module 24: AI Assisted Delivery and Platform Operations

**Objectives.** 

Apply AI assisted engineering responsibly, evaluate its effect on stability, and threat model its risks. Supports CLO 15. Ethical and professional responsibility under ABET Student Outcome four and the acquisition of new knowledge under ABET Student Outcome seven are central.

**Topics and subtopics.**

- Review discipline as the counterpart to generation, since generated infrastructure can be confident, plausible, and wrong.
- The empirical finding that AI adoption raises throughput and lowers stability, and that it amplifies the maturity of the system it enters, which makes the preceding twenty three modules the precondition for benefit.
- Operational analytics: anomaly detection, log clustering, and predictive scaling, together with their failure modes.
- Conversational operations grounded in real observability data, and where they mislead.
- Machine learning operations from the platform perspective: model versioning, model serving as deployment, and accelerator scheduling.
- Prompt injection and agent security, and the application of least privilege to autonomous tooling that will act on instructions it reads.

**Practical laboratories.**

- Lab 24A. Draft infrastructure and a manifest with an assistant, review both as a senior engineer would before applying, then apply and evaluate what the review missed.
- Lab 24B. Add an automated review step to a pull request pipeline, compare its findings against deterministic analysis, evaluate what it caught and what it fabricated, and defend a position on whether it should block a merge.
- Lab 24C. Summarize recent metric data with a language model, check the summary against known ground truth from the incident simulation, and report the failure modes.
- Lab 24D. Request an accelerator resource in a pod specification and observe scheduler behavior when the resource cannot be satisfied.
- Lab 24E. Author a threat model for an internal assistant with cluster and chat access, specifying at least three distinct attack scenarios, each with the specific tool call, the resulting exfiltration or state change, and the specific least privilege control that would prevent it. This exercise develops ethical reasoning and risk analysis under ABET Student Outcome four.

**Assignments.** 

An evaluated AI review integration and a threat model with at least three defended scenarios.

---
### DVP 301 Weekly Schedule

| Week | Modules | Focus |
|---|---|---|
| 1 | 16 | Reliability practices. Capstone kickoff and proposal due |
| 2 | 16 and 17 | Incident response, then chaos engineering |
| 3 | 18 | Disaster recovery and continuity |
| 4 | 19 | Security foundations, secrets, static and composition analysis |
| 5 | 19 | Image and secret scanning, dependency automation. Capstone checkpoint 1 |
| 6 | 20 | Supply chain security and policy as code |
| 7 | 21 | Service mesh and advanced traffic management |
| 8 | 22 | Multi cloud, serverless, and cost engineering |
| 9 | 23 | Platform engineering. Capstone checkpoint 2 |
| 10 | 24 | AI assisted delivery and platform operations |
| 11 to 13 | 25 | Capstone build with weekly review |
| 14 | 25 | Capstone presentations and live defenses |

---
## Module 25: Capstone Project

**Objectives.** 

Integrate the complete toolchain into an automated, observable, secure delivery platform, and defend every design decision under examination. Supports CLO 16 and consolidates all preceding outcomes.

**Engineering design framing.** The capstone is the program's principal engineering design experience and satisfies the ABET requirement for a culminating design activity. Students execute a complete design process: eliciting requirements, proposing an architecture, evaluating alternatives, building incrementally, validating against measured criteria, and defending decisions. The design is bounded by multiple realistic constraints and considerations, which students must document and reconcile:

- Economic. Cloud spend is bounded by budget guardrails, and right sizing is quantified.
- Health, safety, and welfare. Reliability objectives, reversible schema evolution, and security controls protect the users and operators of the delivered system.
- Environmental and sustainability. Right sizing and autoscaling reduce wasted compute and its associated energy and carbon footprint.
- Social and professional. Accessibility of the developer experience and blameless operational culture are explicit design goals.
- Ethical and global. Credential handling, data protection, license awareness, and cross provider portability are addressed as professional obligations.

**Structure.** 

The capstone begins in Week 1 of DVP 301, is proposed and approved, is built incrementally as each module lands, and is presented in Week 14. Two review checkpoints provide early correction.

**Core requirements, all mandatory.**

1. Application with health and metrics endpoints, at least one feature covered by unit and integration tests, environment sourced configuration, and a migration tool with at least one migration.
2. Version control with protected main branch, reviewed pull requests, enforced commit conventions, automated release, and secret scanning as a commit hook.
3. Multi stage, non root container image published to a registry with no embedded credentials.
4. A continuous integration and delivery pipeline ordered as checkout, secret scan, halting unit tests, integration tests, static and composition analysis, image build and publish, gating vulnerability scan, and deploy, with all cloud authentication through short lived federated credentials and no static keys anywhere, and automated dependency updates.
5. Cluster secrets sourced without committing them to version control, using one established method, with a defended justification of the choice.
6. Infrastructure as code that provisions the whole environment reproducibly with remote locked state and a configuration scan in the pipeline.
7. Configuration management that converges the deployment target after provisioning using dynamic inventory and idempotent definitions.
8. A hardened Kubernetes deployment with least privilege access control, restricted workload security, a default deny network policy with only required paths opened, and requests, limits, and autoscaling.
9. Observability with dashboards for core service signals, at least one alert rule that has actually fired, and distributed tracing through open instrumentation.
10. A safe schema change demonstrated through expand and contract with a proven reversible rollback.
11. A platform catalogue entry describing the whole system as a golden path a new developer could follow on day one.

**Electives, choose exactly two, completed thoroughly.**

- A. Progressive delivery with automated metric driven rollback, or a justified feature flag equivalent.
- B. Supply chain integrity with a bill of materials, signing, verification, and enforced admission policy.
- C. Service mesh with confirmed mutual transport layer security and one weighted traffic shift.
- D. Disaster recovery with a measured restore against a preset recovery target, written as a one page postmortem.
- E. An evaluated AI review step with a written assessment of its findings, fabrications, and merge blocking suitability.

**Deliverables.** 

The repository, a live application at a stable address, a dashboard, evidence for both electives, a written record of AI assistant contributions and errors, a fifteen minute presentation that includes at least one real problem and its resolution, and a ten minute live defense.

**Equitable access.** 

Every core and elective requirement is completable through the equitable access path described in Appendix B. Requirements whose native form depends on a managed cloud, specifically the billing guardrail and the managed control plane experience, are assessed through equivalent emulated exercises that measure the same underlying competency. Students electing this path notify the instructional team in Week 1 of DVP 201 so that laboratories are adapted in advance.

---
## 6. Assessment Scheme

### 6.1 Course Weightings

| Component | DVP 101 | DVP 201 | DVP 301 |
|---|:---:|:---:|:---:|
| Graded laboratories, best subset of many | 60% | 50% | 30% |
| Two timed practical checkpoints | 30% | 30% | 20% |
| Live defenses | 10% | 10% | 10% |
| Integrative milestone project | not applicable | 10% | not applicable |
| Capstone project | not applicable | not applicable | 40% |
| Total | 100% | 100% | 100% |

The passing mark for each course is 60 percent, subject to a floor: no course is passed with less than 50 percent on the timed practical checkpoints, because the profession imposes time pressure that coursework cannot simulate.

### 6.2 Laboratory Rubric

Each graded laboratory is scored out of 10.

| Band | Marks | Criterion |
|---|:---:|---|
| Works | 0 to 4 | The result performs the required function, with attached evidence. |
| Explained | 0 to 3 | The write up states what was done and why, including at least one approach that failed. |
| Cleaned up | 0 to 1 | Cloud resources decommissioned, no committed secrets, sensible ignore rules. |
| Defended | 0 to 2 | Follow up questions answered. |

A laboratory that works but cannot be explained is capped at 5 out of 10, which encodes the program's central pedagogy: the ability to explain a system is valued as highly as the ability to produce it.

### 6.3 Practical Checkpoints

Two per course, three hours each, conducted on an unfamiliar machine presenting a broken system. Students are told the intended behavior, shown the actual behavior, and required to diagnose, repair, and document their findings. Each checkpoint is scored against a published rubric weighting correct diagnosis, correct remediation, and quality of the written diagnostic narrative in equal thirds. Laboratory 7F is the training equivalent of this format.

### 6.4 Live Defenses

Every graded artifact is defended in a ten minute examination, individually or before the cohort, in which the instructional team selects specific lines of the student's work and requires explanation. An artifact that cannot be defended does not pass regardless of whether it functions. This models professional code review and directly develops communication under ABET Student Outcome three.

### 6.5 Late Work

Laboratories are accepted up to one week late at 80 percent of the awarded mark, after which they score zero unless prior arrangement was made before the deadline. Practical checkpoints and capstone milestones follow a separate accommodation policy published in the course handbook, under which documented circumstances are arranged in advance with the instructional team.

### 6.6 Direct Assessment and Continuous ABET Evaluation

The following instruments provide direct measurement of Course Learning Outcomes and the mapped ABET Student Outcomes. Each is evaluated against a defined performance indicator with a target that at least 70 percent of students achieve a score of 70 percent or higher. Results are reviewed each cohort to drive continuous improvement.

| Assessment instrument | Course Learning Outcomes measured | ABET Student Outcomes measured |
|---|---|---|
| Module 1 measurement and improvement laboratories | CLO 1 | 1, 4, 7 |
| Module 2 performance triage report | CLO 2 | 1, 6 |
| Module 3 subnet design and diagnosis | CLO 3 | 1, 6 |
| Module 4 governance and communication laboratories | CLO 4 | 3, 5 |
| Module 5 layered test suite and measurement | CLO 5 | 1, 6 |
| Module 6 hardened image comparison | CLO 6 | 1, 2 |
| Module 7 integration pipeline and fault repair | CLO 7 | 2, 6 |
| Modules 8 to 10 infrastructure and configuration builds | CLO 8 | 1, 2, 6 |
| Modules 11 and 12 cluster deployment and hardening | CLO 9 | 1, 2 |
| Module 13 observability build | CLO 10 | 6 |
| Modules 14 and 15 delivery and safe migration | CLO 11 | 2, 6 |
| Modules 16 to 18 reliability, chaos, and recovery | CLO 12 | 4, 5, 6 |
| Modules 19 and 20 security and supply chain | CLO 13 | 2, 4 |
| Modules 21 to 23 mesh, cost memorandum, and platform | CLO 14 | 2, 3, 4 |
| Module 24 AI review evaluation and threat model | CLO 15 | 4, 7 |
| Module 25 capstone and live defense | CLO 16 | 1, 2, 3, 6 |

The practical checkpoints, the live defenses, and the capstone provide triangulated direct evidence across every ABET Student Outcome, and the equal weighting of the live defense within the capstone rubric ensures that explanation and judgment are measured alongside function.

### 6.7 Capstone Rubric

| Component | Marks |
|---|:---:|
| Core components one to eleven, working and evidenced | 45 |
| The two electives, completed thoroughly | 15 |
| Live defense, explanation of the delivered system | 20 |
| Presentation, including an honest account of a real problem | 10 |
| Write up quality, including the AI contribution record | 10 |
| Total | 100 |

The live defense carries twice the weight of the presentation by design, because a system the student can fully explain demonstrates the competency the program certifies.

---
## 7. Program Policies

**Use of AI assistants.** Students are expected to use AI assistants throughout the program. Because assessment centers on the live defense, fluency with assistants raises rather than lowers the standard: every artifact must be defended line by line. Two rules apply. First, every submission discloses which assistant was used, for what, and what it produced incorrectly. Second, no credential, private key, or client data is ever provided to an assistant, a rule with a strict consequence grounded in the reasoning of Module 24.

**Academic integrity.** Integrity is enforced through the defense model. Any work a student cannot explain does not pass, which makes undisclosed copying self defeating.

**Cost and equitable access.** The cloud components of the program incur charges that the standard free allowances do not fully cover. A disciplined student who decommissions costly resources after each session can expect total spend in the range of roughly 40 to 90 United States dollars across the program, while a student who leaves managed resources running will exceed this substantially. Three controls are mandatory: the billing guardrail laboratory precedes all other cloud work, every cloud laboratory ends with an assessed teardown step, and a fully documented equitable access path exists. The equitable access path, detailed in Appendix B, allows completion of every graded requirement using local clusters and cloud service emulation. Requirements whose native form depends on managed cloud infrastructure are assessed through equivalent exercises that measure the same competency. Students who cannot incur cloud spend take this path without penalty and notify the instructional team in Week 1 of DVP 201.

**Hardware.** A workstation with at least 8 gigabytes of memory, 60 gigabytes of free disk, and four cores with virtualization enabled is the minimum, with 16 gigabytes and 100 gigabytes recommended. Laboratories that assume concurrent virtual machine and cluster operation provide a single node variant for the minimum configuration. Students below the minimum are provided a supported shared cloud workstation.

**Accessibility and conduct.** Accommodation needs are arranged from Week 1. The program enforces a code of professional conduct that prohibits harassment and belittlement, consistent with the blameless culture taught in Module 16, because a team that hides mistakes is the failure mode the reliability curriculum exists to prevent.

---
## 8. References

### 8.1 Required and Recommended Texts

- Forsgren, Humble, and Kim. *Accelerate: The Science of Lean Software and DevOps.* The research foundation of the DORA metrics. Required reading before citing a DORA metric.
- Beyer, Jones, Petoff, and Murphy, editors. *Site Reliability Engineering*, and *The Site Reliability Workbook.* Chapters on service level objectives, error budgets, and postmortem culture support Module 16.
- Skelton and Pais. *Team Topologies.* The source of the cognitive load argument in Module 23.
- Burns, Beda, Hightower, and Evenson. *Kubernetes Up and Running.* Reference for Modules 11 and 12.
- Brikman. *Terraform Up and Running.* Reference for Module 9.

### 8.2 Official Documentation

- The DORA research program and current metrics guidance, including the Accelerate State of DevOps reports of 2024 and 2025.
- Kubernetes documentation, including workloads, services, access control, and the gateway routing model.
- Prometheus and the query language, and the vendor neutral observability project documentation.
- Infrastructure as code documentation for the primary tool and its community fork.
- Configuration management documentation.
- Managed cloud provider documentation for the primary provider, with conceptual reference to alternate providers.
- Continuous delivery, progressive delivery, policy engine, and service mesh project documentation.

### 8.3 Industry and Engineering Standards

- OWASP Top Ten application security risks.
- Open Container Initiative image, runtime, and distribution specifications.
- NIST Special Publication 800 190, Application Container Security Guide.
- NIST Special Publication 800 218, Secure Software Development Framework.
- Supply Chain Levels for Software Artifacts framework.
- Software bill of materials formats, namely SPDX and CycloneDX.
- The Kubernetes Gateway API specification.
- Semantic Versioning specification.
- CIS Benchmarks for Kubernetes and Linux.
- ISO/IEC 27001 information security management principles at an awareness level.

---
## 9. Skills and Competencies

On completion, graduates demonstrate the following professional competencies:

- Systems administration and diagnostic reasoning on Linux hosts.
- Network analysis, subnet design, and segmentation policy.
- Collaborative version control, structured code review, and release automation.
- Application delivery readiness and layered automated testing.
- Container construction, hardening, and open standard portability.
- Continuous integration and delivery design with federated short lived authentication.
- Declarative infrastructure provisioning and idempotent configuration convergence.
- Kubernetes deployment, security hardening, and autoscaling.
- Observability instrumentation and metric, log, and trace correlation.
- GitOps operation, progressive delivery, and reversible schema evolution.
- Reliability engineering, incident command, chaos experimentation, and disaster recovery.
- Security integration across the lifecycle, supply chain integrity, and policy as code.
- Cost engineering, cross provider portability analysis, and platform engineering.
- Responsible and security aware use of AI assisted tooling.
- Technical communication tuned to engineering and executive audiences.
- Engineering judgment under examination, evidenced through live defense of delivered systems.

---
# Appendix A: Enterprise and Legacy Stack Elective (DVP 150)

This elective exists because a substantial fraction of employment, particularly in finance, telecommunications, government, and established enterprises, runs on a stack the core program does not teach. The material is current in those settings, though it is not what a new project begins with today. It is scheduled with dedicated hours rather than folded into the core as untimed optional content.

- Part 1, enterprise Java delivery, approximately 8 hours. Application container fundamentals and the enterprise build lifecycle, culminating in building and deploying a packaged web application.
- Part 2, alternate automation server, approximately 8 hours. Controller and agent architecture, pipeline as code, webhook triggering, and ephemeral build agents, culminating in a pipeline that invokes the same build wrapper targets defined in Lab 7C, which demonstrates the value of the build wrapper directly.
- Part 3, the classic web stack, approximately 4 hours. Reconstructing the reference application idea on the classic scripting and relational stack and deploying it with the Module 10 role.
- Part 4, enterprise container and log platforms, approximately 5 hours. An enterprise Kubernetes distribution with tighter security defaults and its native routing, and an enterprise log platform through ingestion, pipeline processing, and visualization. Given the breadth, this part is treated as guided exposure rather than mastery, and its laboratory targets a single end to end path through each platform.

Students on the alternate automation server track may submit an equivalent pipeline definition in place of the core continuous integration workflow for the capstone, since both invoke identical build wrapper targets.

---
# Appendix B: Equitable Access Path

| Native component | Equivalent |
|---|---|
| Managed Kubernetes | A single node local cluster on the student workstation |
| Managed cloud object storage, database, identity, and secret services | A local cloud service emulator exposing compatible interfaces |
| Managed translation gateway and a real virtual network | The Module 3 and Module 8 network designs on paper, with a virtual internal network to evidence routing |
| A managed load balancer | The ingress controller in the local cluster |
| Remote cloud infrastructure state | Local emulated object and lock storage, with identical definitions and a different endpoint |

The equitable access path cannot reproduce the experience of a managed control plane or the shape of a real cloud bill. Where a graded requirement depends on either, specifically the billing guardrail laboratory and the managed control plane laboratory, an equivalent emulated exercise measures the same underlying competency, so that no student is disadvantaged in assessment. Students able to spend in the range of roughly 40 to 90 United States dollars across the program are encouraged to use managed infrastructure for the added realism, and students who cannot take the equitable access path without penalty.

---
# Appendix C: Certification Alignment

None of the following certifications is required. The coursework aligns closely enough that a prepared graduate can pursue them with confidence. Certification names and codes change, and students should verify current details with each certifying body.

| After | Reasonable targets |
|---|---|
| DVP 101 | A Linux system administration certification and an introductory version control certification aligned to Module 4. |
| DVP 201 | An introductory cloud native certification, an infrastructure as code associate certification, a Kubernetes administrator or application developer certification, an associate cloud architecture certification, and associate certifications in GitOps, progressive delivery projects, metrics, and observability. |
| DVP 301 | A professional cloud delivery engineering certification, a Kubernetes security specialist certification, associate certifications in cloud native security and policy engines, a developer platform associate certification, and a platform engineering certification as a longer term target. |

Students pursuing an infrastructure as code certification should note that the primary tool is now under a source available license and corporate ownership, facts that do not diminish the certification's value but should be held alongside it.

---
# Appendix D: Explicitly Excluded Scope

The program deliberately excludes topics that constitute distinct disciplines to preserve depth over breadth. It does not teach model training and evaluation, addressing only the platform side of machine learning operations. It does not cover Windows server administration, mobile delivery pipelines, or game build pipelines. It treats cost engineering only at the level a delivery engineer requires. It does not pursue an offensive security path, and its security content is defensive by design. It teaches service mesh concepts and one hands on mesh rather than the full breadth of every mesh implementation, an honest trade acknowledged so that graduates entering an environment running an unfamiliar mesh know precisely what additional study they require.

---
