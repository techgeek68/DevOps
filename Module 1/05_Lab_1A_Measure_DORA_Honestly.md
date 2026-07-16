# Lab 1A: Measure DORA, Honestly

---
> *No terminal is needed for this lab. A calculator, a spreadsheet, and a GitHub account are enough.*
---
### Objective

Measure the DORA metrics you actually *can* observe for a real open source project using only publicly available GitHub data. Then write the more important half: explain why the remaining metrics **cannot** be derived from public data, and what instrumentation a team would need to add to measure them.

This is the same analysis a DevOps engineer runs when joining a new team, evaluating a tool, or presenting engineering performance to leadership. The lesson here is that DORA requires instrumentation, not archaeology.

### What You Need
- A GitHub account (free at github.com)
- Git installed on your machine
- A text editor
- A calculator or spreadsheet for metric calculations
- No special permissions or paid accounts required

### Prerequisites
- Completed Part A of Module 1 (Foundations)
- Read Part B Section 4 of Module 1 (DORA Metrics)
- A GitHub repository to commit your report to (create a new one called `devops-labs` if you do not have one already)

---
### Background: What You Can and Cannot Observe

DORA metrics in production are measured through CI/CD platforms, deployment logs, incident management systems, and application monitoring. For open source projects viewed from the outside, you have access to none of these internal systems.

From public GitHub data, you can approximate two metrics with reasonable confidence:

| DORA Metric | Public Proxy | Confidence |
|---|---|---|
| Deployment Frequency | Number of GitHub Releases per time window | Moderate |
| Lead Time for Changes | Time from PR open to merge, plus time from merge to next release | Moderate |

You **cannot** meaningfully measure the other three from public data:

| DORA Metric | Why It Cannot Be Observed Externally |
|---|---|
| Change Failure Rate | Requires internal incident tracking; public patch releases are an unreliable proxy |
| Failed Deployment Recovery Time | Requires deployment timestamps and incident resolution timestamps from internal systems |
| Rework Rate | Requires knowing which deployments were unplanned fixes versus planned work |

Understanding *why* these cannot be observed is as important as measuring the ones that can. A DevOps engineer who quotes DORA numbers without understanding the limitations of the underlying data is making decisions on incomplete evidence.

---
### Step 1: Choose a Repository

Pick one well maintained open source project with an active release history. The repository must have:

- At least 10 releases in the last 12 months
- An active Issues tracker with labeled bugs
- Pull requests with clear merge timestamps

**Recommended options:**

- `github.com/grafana/grafana`
- `github.com/hashicorp/terraform`
- `github.com/prometheus/prometheus`
- `github.com/kubernetes/kubernetes`
- `github.com/cli/cli` (GitHub CLI, smaller and easier to navigate)

Avoid repositories with no releases in the last six months. If the Releases page is empty, check the README for how the project publishes versions (some use npm, PyPI, or Docker Hub instead of GitHub Releases).

Record your choice before proceeding.

---
### Step 2: Measure Deployment Frequency

1. Open the repository on GitHub and click **Releases** in the right sidebar.
2. Count the number of releases published in the last **90 days**. Include all types: major, minor, and patch.
3. Calculate the average release frequency:

```
releases in 90 days / 90 = average releases per day
```

4. If releases per day is less than 1, convert it:

```
90 / releases in 90 days = average days between releases
```

Record the raw count and your calculated frequency.

**Classify your result:**

| Frequency | DORA Level |
|---|---|
| Multiple per day | Elite |
| Between once per day and once per week | High |
| Between once per week and once per month | Medium |
| Less than once per month | Low |

---
> **What to pay attention to:** Many projects release patch versions frequently, but minor and major versions rarely. If you see this pattern, note it. It tells you the team can respond quickly to bugs, but major feature work takes longer to reach users.
---
### Step 3: Measure Lead Time for Changes

Lead time measures how long code takes to travel from a developer's commit to a production deployment.

1. Go to the **Pull Requests** tab. Filter by **Closed**. Sort by **Newest**.
2. Select five recently merged PRs. Choose feature or bug fix work. Skip documentation only PRs.
3. For each PR, collect:
   - Date the PR was opened (visible in the PR header)
   - Date the PR was merged (visible in the merge event at the bottom)
   - The next release published after this merge (look at the Releases page for the first release after the merge date)
   - Date of that release

4. For each PR, calculate:

```
Segment 1: PR open to merge = merge date minus open date (in days)
Segment 2: merge to release = release date minus merge date (in days)
Lead time approximation = Segment 1 + Segment 2
```

5. Average the five lead time values.

Create a table like this for your five PRs:

| PR Title | Opened | Merged | Segment 1 (days) | Released | Segment 2 (days) | Total Lead Time |
|---|---|---|---|---|---|---|
| | | | | | | |
| | | | | | | |
| | | | | | | |
| | | | | | | |
| | | | | | | |
| **Average** | | | | | | |

**Classify your average:**

| Lead Time | DORA Level |
|---|---|
| Less than one day | Elite |
| Between one day and one week | High |
| Between one week and one month | Medium |
| More than one month | Low |

**Note on open source projects:** PR review cycles in open source projects are often longer than in commercial teams because reviewers are volunteers. If lead time is 2 to 3 weeks, this does not necessarily mean the project is poorly run. Note this nuance in your report.

---
### Step 4: Explain Why the Other Three Metrics Cannot Be Measured

This is the more important half of the lab. For each of the three metrics below, write a paragraph covering:

1. What the metric actually measures (use the definitions from Part B Section 4, DORA Metrics)
2. What data source you would need to measure it properly
3. Why public GitHub data is an inadequate proxy
4. What instrumentation a team would need to add to measure it in their own delivery system

**Change Failure Rate**

You might be tempted to use patch releases as a proxy for failures (if v2.4.1 appeared within 72 hours of v2.4.0, maybe v2.4.0 was broken). Explain why this is unreliable. Consider: patch releases can be scheduled maintenance, minor improvements, or dependency updates that have nothing to do with a failure in the previous release. Without access to the team's incident tracker, you cannot distinguish a failure driven patch from a routine one.

**Failed Deployment Recovery Time (FDRT)**

You might be tempted to use the time between a bug report and its closure. Explain why this understates or overstates recovery time. Consider: issue creation and closure dates do not reflect when the failure was *detected* in production, when the team *started* working on it, or when the fix was actually *deployed*. FDRT requires deployment timestamps and incident management data that live in internal systems like PagerDuty, Datadog, or the CI/CD platform's deploy logs.

**Rework Rate**

Explain why there is no reliable public proxy at all. Consider: rework rate requires knowing the *intent* behind a deployment. Was this deployment planned feature work, or was it an unplanned fix for something that broke in a previous deployment? That classification exists in the team's issue tracker and sprint planning tool, not in the release tag name.

---
### Step 5: Set Up Your Repository and Write the Report

```bash
# If you do not already have a devops-labs repo
mkdir ~/devops-labs
cd ~/devops-labs
git init
git remote add origin https://github.com/<your-username>/devops-labs.git

# Create the folder for this lab
mkdir -p labs/lab-1a
cd labs/lab-1a
```

Create a file called `dora-baseline-report.md` in your `labs/lab-1a` folder. Your report must follow this structure:

---
---
---
# DORA Baseline Report

**Repository Analyzed:** [full GitHub URL]
**Analysis Date:** [today's date]
**Data Window:** [date range you examined]

---
## Summary Table

| DORA Metric | Measured Value | DORA Level | Observable from Public Data? |
|---|---|---|---|
| Deployment Frequency | | | Yes |
| Lead Time for Changes | | | Yes (approximate) |
| Change Failure Rate | Not measurable | N/A | No |
| Failed Deployment Recovery Time | Not measurable | N/A | No |
| Rework Rate | Not measurable | N/A | No |

---
## Deployment Frequency

**Raw data:** [releases counted, time window]
**Calculation:** [show your math]
**Result:** [value and DORA level]

**Observation:** [2 to 3 sentences: what does this frequency tell you about this team's delivery capability?]

---
## Lead Time for Changes

**PRs analyzed:**

| PR | Open to Merge | Merge to Release | Total |
|---|---|---|---|
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |
| Average | | | |

**Result:** [average and DORA level]

**Observation:** [2 to 3 sentences: what does this lead time tell you? Is any part of the pipeline slow?]

---
## Why the Other Three Metrics Cannot Be Measured from Public Data

### Change Failure Rate
[Your paragraph: what it measures, what data source is needed, why GitHub releases are an inadequate proxy, what instrumentation a team would add]

### Failed Deployment Recovery Time
[Your paragraph: what it measures, what data source is needed, why issue timestamps are an inadequate proxy, what instrumentation a team would add]

### Rework Rate
[Your paragraph: what it measures, why no public proxy exists at all, what internal systems would track it]

---
## If This Were My Team

If you were the DevOps engineer on this team and had access to their internal systems, which unmeasurable metric would you instrument first?

**Chosen metric:** [name it]

**Why:** [1 to 2 sentences: why is this the highest leverage improvement?]

**How you would instrument it:** [1 to 2 sentences: name the tool and the data source. Be specific.]

---
---
---
### Step 6: Commit and Push the Report

```bash
cd ~/devops-labs

# Stage the report
git add labs/lab-1a/dora-baseline-report.md

# Commit with a conventional commit message
git commit -m "feat(lab-1a): add DORA baseline report for [repo name]"

# Push to your remote repository
git push origin main
```

Verify the report is visible on GitHub before marking this lab complete.

---
### Expected Output

- A completed `dora-baseline-report.md` committed to your `devops-labs` GitHub repository
- Deployment frequency and lead time measured with supporting data tables
- Three written paragraphs explaining why change failure rate, FDRT, and rework rate cannot be measured from public data
- A specific instrumentation recommendation with a named tool

---
### Common Issues

**The Releases tab is empty:** Check the repository README for alternative release channels. Some projects publish to npm, PyPI, DockerHub, or use GitHub Packages. If you genuinely cannot find release data, pick a different repository from the recommended list.

**PR lead times are extremely long (months):** This is common in large open source projects where reviewers are maintainers with day jobs. Your report should note this explicitly as a structural difference from commercial teams and explain how this affects your lead time measurement.

**Git push fails:** Make sure the remote repository exists on GitHub and that your local `origin` remote URL is correct. Run `git remote -v` to verify.

---
