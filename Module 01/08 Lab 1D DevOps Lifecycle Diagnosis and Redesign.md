# Lab 1D: DevOps Lifecycle Diagnosis and Redesign


> Lab 1C introduces configuration drift hands on. Lab 1D brings together the main ideas from Module 1 in one applied design exercise.

### Objective

Take a broken delivery process and redesign it using the concepts from Part B and the previous three labs. This lab combines the core topics from Module 1 into one practical engineering exercise.

This is the kind of analysis you might do in your first month at a new company, in a system design interview, or when making the case to leadership for investment in platform work.

### What You Need
- Paper, a whiteboard, draw.io, or any diagramming tool
- Your completed Lab 1A report and Lab 1B calculations for reference
- No terminal or cloud account required
- About 75 minutes

### Prerequisites
- Completed Labs 1A, 1B, and 1C
- Read all of Part B, Sections 1 through 8

---
## The Scenario

You are the first dedicated DevOps engineer joining a nine person team at a startup building a SaaS invoicing tool. The product consists of a Python Flask API, a React frontend, and a PostgreSQL database, all deployed on a single AWS EC2 instance.

Here is the current state.

**Development**
- All code lives on GitHub
- Developers push directly to `main`
- There are no feature branches and no pull requests
- API unit tests exist, but developers run them manually on their laptops before pushing
- The frontend has no tests

**Deployment**
- One engineer, Ramesh, does all deployments by SSH-ing into the production EC2 instance and running:
  ```bash
  cd /opt/invoicing-app && git pull && pip install -r requirements.txt && sudo systemctl restart app
  ```
- Ramesh is the only person who knows the process
- Deployments happen once a week on Friday afternoons
- Ramesh is going on paternity leave in six weeks

**Infrastructure**
- One `t3.medium` EC2 instance runs the web server, app, and PostgreSQL
- The instance was created manually in the AWS console two years ago
- There is no staging environment
- There is no Terraform or other IaC
- There are no instance or database backups

**Monitoring**
- No monitoring tools are in place
- The team learns about outages when customers email support
- Average time from outage start to team awareness is 2 to 4 hours
- Last month there were three outages totaling about 5 hours of downtime

**Incidents**
- No incident management process
- Whoever is available tries to fix the problem
- No postmortems
- No runbooks

---
## Part 1: Baseline DORA Assessment

Before improving anything, estimate the team's current DORA metrics from the scenario.

| Metric | Estimated Current Value | DORA Level | Evidence from the Scenario |
|---|---|---|---|
| Deployment Frequency | | | |
| Lead Time for Changes | | | |
| Change Failure Rate | | | |
| Failed Deployment Recovery Time (FDRT) | | | |
| Deployment Rework Rate | | | |

For each metric, write one sentence explaining the evidence behind your estimate.

You do not need exact numbers. Use the scenario to estimate a likely value or range and justify your reasoning.

**A note on Deployment Rework Rate:** this is the newest DORA metric, added in 2024. It measures what share of deployments are unplanned work forced by a production incident, as opposed to planned feature or maintenance work, which means it depends on knowing intent, not just outcome. If the scenario doesn't give you enough to estimate this with any confidence, say so directly and explain what you would need to know instead of guessing. That's a legitimate answer, and it mirrors the reasoning you did in Lab 1A about metrics that can't be pulled from limited data.

---
## Part 2: Identify the Risks

List the four most critical operational risks in the current setup. For each one, describe:
- what the risk is
- the likely consequence if it happens
- how soon it could happen: imminently, within months, or eventually

One risk is obvious from the scenario. Find the other three.

| Risk | Consequence | Urgency |
|---|---|---|
| | | |
| | | |
| | | |
| | | |

---
## Part 3: Design the Target State

Design the DevOps lifecycle for this team over a six month transformation. For each stage, specify:
- the current state
- the target state
- the tool that enables it
- the success condition

Example for **Plan**:

| | Current | Target |
|---|---|---|
| What happens | Informal Slack discussions | |
| Tool | None | |
| Responsible | Whoever is loudest | |
| Success condition | N/A | |

Complete this table for all eight stages:
- Plan
- Code
- Build
- Test
- Release
- Deploy
- Operate
- Monitor

For **Deploy** and **Monitor**, be specific.

For Deploy, name both:
- the automation tool
- the deployment strategy

For Monitor, name:
- the monitoring tools
- the key dashboards you would build

---
## Part 4: Prioritize the First 90 Days

You need to present a 90 day plan to the CTO.

The team can implement about two significant engineering changes per two week sprint. That gives you roughly six sprints and twelve major changes total.

From the list below, choose and sequence your top eight priorities for the first 90 days. Justify each one in one or two sentences.

Available improvements:
- Branch protection rules and pull request workflow on GitHub
- GitHub Actions CI pipeline with lint and unit tests on every PR
- Add a staging environment on a separate EC2 instance
- Automated deployment pipeline to replace manual SSH deployment
- Terraform for existing infrastructure, including the EC2 instance and security groups
- Separate PostgreSQL to a dedicated RDS instance
- Daily automated database backups to S3 or another backup target
- Prometheus and Node Exporter on the EC2 instance
- Grafana dashboard with CPU, memory, and application error rate panels
- PagerDuty or similar alerting so the team knows about outages before customers do
- Runbook documentation for the three most common failure scenarios
- On call rotation with at least three engineers
- SLO definition and Grafana SLO dashboard
- End to end tests with Playwright for the critical invoicing workflow

Present your 90 day plan as a sprint by sprint table.

| Sprint | Changes | Justification |
|---|---|---|
| 1, weeks 1 to 2 | | |
| 2, weeks 3 to 4 | | |
| 3, weeks 5 to 6 | | |
| 4, weeks 7 to 8 | | |
| 5, weeks 9 to 10 | | |
| 6, weeks 11 to 12 | | |

**Constraint:** Ramesh leaves in six weeks, at the end of Sprint 3. Any knowledge or process currently locked in his head must be documented or automated before then.

---
## Part 5: Define the First SLO

The team has never defined a reliability target. You need to define an initial SLO before building service level alerting, otherwise alerts are hard to prioritize and often become noisy.

The most critical user journey is this:

a customer logs in, creates an invoice, and sends it to their client.

If that journey fails, the product has failed.

Define:

1. One SLI that measures the success rate of this journey end to end. Be specific about:
   - numerator
   - denominator
   - time window
   - where the measurement happens

2. An SLO target for this SLI. Justify your choice using the scenario data: three outages last month totaling 5 hours of downtime.

   For this exercise, you may use that 5 hours of outage time as a rough proxy for end to end journey unavailability.

   Hint: estimate the current availability first, then choose a pragmatic initial SLO near current performance rather than at the theoretical ceiling. You can note how the team should raise it over time as reliability improves.

3. The error budget in minutes per 30 days.

4. The external SLA you would propose to enterprise customers. What buffer are you building in between the internal SLO and the external SLA?

5. The first Grafana alert you would configure after defining the SLO. Be specific about:
   - the condition
   - the threshold
   - the time window
   - the routing target

---
## Part 6: The Ramesh Problem

Write a 150 to 200 word response to this question.

Ramesh is going on paternity leave in six weeks. He is the only person who can deploy the application and the only person who knows how the production server is configured. What specifically do you do in the next six weeks, and in what order?

Your answer must name specific tools or documents and address both:
- the knowledge transfer problem, such as runbooks and documentation
- the process problem, such as automating deployment so it no longer depends on one person

---
## What Strong Answers Look Like

**Weak:** "Add monitoring to the system."

**Strong:** "Deploy Prometheus with Node Exporter to the EC2 instance in Sprint 3. Instrument the Flask API with `prometheus_flask_exporter` to expose a `/metrics` endpoint. Build a Grafana dashboard for CPU, memory, request rate, error rate, and latency. Configure an alert that fires when the 5 minute HTTP 500 rate exceeds 2% of total requests, routing to PagerDuty. This should reduce detection time from hours to minutes."

Every improvement you recommend should be concrete enough that a colleague could implement it the next morning without asking you clarifying questions.

---