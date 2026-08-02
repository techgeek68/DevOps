# Lab 1B: SLO and Error Budget Calculation

---
> *No terminal is needed for this lab. A calculator, a spreadsheet, and a GitHub account are enough.*
---
### Objective

Work through the mathematics of SLIs, SLOs, and error budgets across multiple realistic scenarios. By the end, you will be able to calculate error budgets, evaluate outage scenarios against a budget, and design your own SLI/SLO/SLA stack for a real service.

This is the calculation work a DevOps or SRE engineer does before defining reliability targets and before agreeing to any SLA with a customer.

---
### What You Need
- A calculator or spreadsheet (Google Sheets or Excel)
- No terminal or cloud account required
- Approximately 60 minutes

---
### Prerequisites
- Read Part B of Module 1, specifically Sections 3 (SRE) and 4 (DORA Metrics)
- Completed Lab 1A (your analysis of why certain DORA metrics cannot be observed externally will inform your thinking here)

---
### Part 1: Error Budget Reference Table

**A 30 day month contains exactly 43,200 minutes.**

The formula for error budget in minutes is:

```
error budget (minutes) = (1 - SLO as decimal) * 43,200
```

Calculate the error budget for each availability target. Show your working for each row.

| SLO Target | Error Budget (minutes/30 days) | Error Budget (hours) | Working |
|---|---|---|---|
| 99.0% | ? | ? | `(1 - 0.990) * 43,200 = ?` |
| 99.5% | ? | ? | |
| 99.9% | ? | ? | |
| 99.95% | ? | ? | |
| 99.99% | ? | ? | |
| 99.999% | ? | ? | |

After filling in the table, answer these two questions before moving on:

1. The difference between 99.9% and 99.99% is only 0.09 percentage points. How many fewer minutes of error budget does 99.99% give you compared to 99.9%? Why does this matter when setting an SLO?

2. A team sets a 99.999% SLO ("five nines") for their service. Their planned maintenance window takes 10 minutes each month. Assume the maintenance window counts against the SLO, meaning nothing here is carved out as an exclusion. Is this SLO compatible with monthly maintenance windows? Show your reasoning.

**Answer key for Part 1** (check your own work):

| SLO | Error Budget (minutes) | Error Budget (hours) |
|---|---|---|
| 99.0% | 432.0 min | 7.2 hours |
| 99.5% | 216.0 min | 3.6 hours |
| 99.9% | 43.2 min | 0.72 hours |
| 99.95% | 21.6 min | 0.36 hours |
| 99.99% | 4.32 min | 0.072 hours |
| 99.999% | 0.432 min | 0.0072 hours |

*Note: this lab uses an exact 30 day month (43,200 minutes) for every calculation. Some SRE references use a 30.4 day average month instead, which gives slightly different numbers (for example 43.8 minutes rather than 43.2 for a 99.9% SLO). Neither convention is wrong, but stick to the exact 30 day version throughout this lab so your numbers stay consistent across all three parts.*

---
### Part 2: Outage Scenario Analysis

Work through each scenario completely. Show all calculations.

---
**Scenario A: The Payment Service**

Your payment processing service has a 99.95% availability SLO measured over a **fixed 30-day window**. It is currently day 20 of the window.

*Why fixed rather than rolling: a rolling window continuously slides forward, so old incidents age out of it as new days are added, and there is no clean "day 20 of 30 with 10 days remaining." A fixed window has a defined start and end date, which is what makes the "10 days remaining" framing in this scenario meaningful. Real production SLOs are usually rolling. This scenario simplifies to a fixed window on purpose, so the arithmetic below has a clean answer.*

Incidents this window so far:
- Day 8: A misconfigured load balancer caused a 9-minute outage
- Day 15: A database connection pool exhaustion caused a 5-minute degraded state (classified as full downtime for SLO purposes)
- Day 18: A bad deployment caused a 4-minute outage before an automated rollback recovered the service

Answer each question. Show your calculation.

1. What is the total error budget for this 30-day window in minutes?

2. How much error budget has been consumed so far (sum of all incidents)?

3. How many minutes remain in the error budget for the remaining 10 days?

4. The infrastructure team has two planned maintenance windows coming up:
   - Day 22: Database index rebuild, estimated 6 minutes
   - Day 26: Network switch replacement, estimated 8 minutes
   
   Can both proceed without breaching the SLO? If not, can either one proceed on its own, and what do you recommend?

5. The Day 22 maintenance runs long and takes 11 minutes instead of 6. What is the impact? Is the SLO now breached?

6. Based on this window's incident pattern, what process change would you make before the next window begins? Be specific.

---
**Scenario B: The Search API Latency SLO**

Your search API has a latency SLO: 99% of requests must complete in under 300ms, measured over a rolling 7-day window.

Service characteristics:
- Average request rate: 800 requests per minute
- 7-day window total minutes: 10,080

Answer each question:

1. Total requests in a 7-day window: `800 req/min * 10,080 min = ?`

2. At a 99% SLO, how many requests are allowed to exceed 300ms over the 7-day window? This is your request error budget, a count of requests, not a count of minutes.

3. On day 4, a database query regression causes the p99 latency to spike to 850ms for 45 minutes.

   Note on what p99 actually tells you: a p99 of 850ms means 99% of requests during that window completed faster than 850ms, and roughly 1% were at or above it. It does **not** mean every request was slow. In a real incident you would need histogram or log data to know exactly how many requests crossed the 300ms threshold during those 45 minutes.

   **For this exercise, assume as a simplifying rule that all requests during the 45-minute window are counted as exceeding the 300ms threshold.** This is a deliberate simplification to make the arithmetic tractable, not something you could conclude from the p99 figure alone in a real incident review. How many requests does this assumption count as exceeding 300ms?

4. After the 45-minute incident, how many requests remain in the error budget for the rest of the 7-day window?

5. Is the SLO breached for the full 7-day window? Show your calculation.

6. The team proposes adding a database query cache to prevent this regression from recurring. Assume the cache reduces database query latency by 120ms on cached requests, but adds approximately 5ms of cache lookup overhead to every request, cached or not. Does this change affect the SLO positively or negatively? Explain, showing the net effect on a typical request's latency.

---
**Scenario C: Multi Service SLO Budget Allocation**

You are the DevOps lead for a three-tier e-commerce application:

| Service | Function | SLO | Error Budget (min/30 days) |
|---|---|---|---|
| Frontend CDN | Serves the website globally | 99.95% | ? |
| API Gateway | Routes all backend requests | 99.9% | ? |
| Payment Service | Processes all transactions | 99.99% | ? |

Fill in the error budget column first.

**Before you answer the questions below, fix the measurement point for each SLI, and read this carefully, because it changes the answers.**

For the calculations in this scenario, each service's SLI is measured **independently, at that service's own boundary**:

- **Frontend CDN SLO:** measured by the CDN's own edge success rate, for example the percentage of requests the CDN itself serves without a 5xx or timeout, regardless of what happens downstream.
- **API Gateway SLO:** measured at the Gateway's own ingress, counting only requests that reach the Gateway and recording whether the Gateway itself processed them successfully.
- **Payment Service SLO:** measured at the Payment Service's own load balancer, counting only requests that reach Payment and recording whether Payment itself processed them successfully.

Because each SLI only counts requests that actually reach that component, and each component is assumed to fail independently of the others, you can use the multiplicative model in question 2: system-wide availability, meaning the probability all three layers succeed for a given customer request, is the product of the three individual availabilities.

**This is different from measuring all three SLIs end to end**, where every check runs the full CDN, then Gateway, then Payment path. End to end measurement is also valid and common in real systems, but it produces nested, correlated SLIs rather than independent ones, and you cannot multiply nested SLIs together to get system availability, because a single upstream outage would already be counted inside every downstream number. This lab uses the independent, per-component version specifically so the multiplicative model in question 2 is mathematically valid. If you design SLIs end to end for your own service in Part 3, do not apply this multiplicative shortcut to them.

Now answer:

1. The frontend CDN has a planned maintenance window that will take 30 minutes. Can this proceed without breaching its own SLO?

2. During the maintenance window for the CDN, no customer requests can reach the Gateway or Payment Service at all, because the CDN sits in front of everything.

   a. Does this 30-minute CDN outage count against the Payment Service's own SLO as defined above? Explain why or why not, given that Payment's SLI only counts requests that reach Payment's own load balancer.

   b. Even though it may not count against Payment's own component SLI, the customer still could not complete a purchase for 30 minutes. Calculate the system-wide availability for a customer transaction using the multiplicative model: `CDN availability * Gateway availability * Payment availability`, and explain why a business would care about this number even when every individual component's own SLO says it is fine.

   c. Based on parts a and b, explain the practical reason platforms track both component-level SLOs (for engineering ownership) and a separate customer-journey or platform-level SLO (for what the customer actually experiences), rather than relying on component SLOs alone.

3. A single incident takes down all three services simultaneously for 12 minutes (a core network switch failure that affects every layer directly, not just the CDN). Which services breach their own component SLO for the month if this happens after each has already used half of its error budget?

4. The business team wants to set a customer-facing SLA for the entire e-commerce platform. Using the multiplicative model from question 2b as your starting point, what availability percentage would you recommend for the platform-level SLA, and why would you set the SLA below that calculated number rather than exactly at it?

---
### Part 3: Design Your Own SLI, SLO, and SLA

Choose one of the following services:

**Option A:** A user authentication API (handles login, session validation, and password reset)

**Option B:** A file upload service (accepts files up to 500MB, stores them in object storage, returns a download URL)

**Option C:** A real-time notification delivery service (sends in-app, email, and SMS notifications)

For your chosen service, complete the following design work.

---
**Step 1: Define Three SLIs**

For each SLI, specify all components:

| Component | What to Define |
|---|---|
| What you measure | The specific metric in plain English |
| Measurement point | Where in the request path this is measured: at the service's own load balancer or internal boundary, or end to end through every upstream dependency a real customer request would pass through. State this explicitly, since it determines whether an upstream outage counts against this SLI, and whether this SLI can later be combined multiplicatively with others. |
| Eligible events | Which events count toward the denominator at all, and which are excluded. For example, decide explicitly whether a request rejected for an invalid password, an expired account, rate limiting, or a malformed client request counts as an eligible event, a bad event, or is excluded from the SLI entirely. Do not assume every request your service receives should automatically count. |
| Numerator | The count of "good" events |
| Denominator | The count of all eligible events |
| Time window | How long you measure over (e.g., rolling 28 days) |
| Collection method | How Prometheus, a log pipeline, or your monitoring system captures this |

Example for reference (do not copy this for your service):

```
SLI: API request success rate
What: Percentage of API requests that return a non-5xx status code
Measurement point: At the API's own edge load balancer, not through a synthetic external check, so this SLI only reflects failures inside this API's own infrastructure
Eligible events: All requests that reach this load balancer. Requests rejected upstream (for example, blocked by the CDN or WAF before reaching this service) are excluded, since this service never saw them. Client errors such as 400 or 404 are excluded from the denominator entirely, since they reflect client behavior, not service reliability. 5xx and timeouts count as bad events.
Numerator: Requests returning 2xx or 4xx status codes, excluding 4xx codes already excluded above
Denominator: All eligible requests received
Time window: Rolling 28-day window
Collection: Prometheus counter metric http_requests_total, filtered by status code label
```

Define three SLIs that together cover the most important aspects of your chosen service. A good set covers: availability (is it up?), correctness (does it work correctly?), and latency (is it fast enough?).

**A note on the example above:** treating 2xx and 4xx as success and 5xx as failure is not a universal rule, it is a choice that happened to fit that example service. For your own service, decide deliberately: a 401 or 404 might be entirely expected client behavior for one service and a real failure signal for another, depending on what the response means for that specific user journey. Define good and bad events based on user-visible behavior for your chosen service, not by assuming HTTP status code classes carry the same meaning everywhere.

---
**Step 2: Set Three SLOs**

For each SLI, set an SLO. For each target, justify your choice.

| SLI | SLO Target | Justification |
|---|---|---|
| [SLI 1 name] | | Why this target and not higher or lower? |
| [SLI 2 name] | | |
| [SLI 3 name] | | |

Rules for setting your targets:
- Do not set 100% for any SLO
- Consider what a single planned maintenance window would consume from the budget
- Consider what a realistic worst-case incident would consume
- Your most critical SLO should be the one you can actually meet based on the service's realistic behavior

---
**Step 3: Calculate Error Budgets**

For each SLO, calculate the error budget in minutes per 30 days.

| SLO | Error Budget (minutes/30 days) | What this means in practice |
|---|---|---|
| | | e.g., "This allows approximately one 20-minute outage per month" |
| | | |

---
**Step 4: Propose an External SLA**

Your most critical SLO becomes the basis for your external SLA.

1. What is your most critical SLO (the one breach of which most impacts users)?
2. What availability percentage would you propose for the external SLA?
3. What is the buffer between your SLO and your proposed SLA in minutes per 30 days?
4. Why is that buffer amount appropriate? What events would it absorb?

---
**Step 5: Design a Grafana Alert**

Describe one Grafana alert you would configure to protect your most critical SLO. Cover:

- What PromQL query or metric does the alert watch
- The threshold that triggers the alert
- The time window of the alert condition (e.g., "if this condition persists for 5 minutes")
- Who the alert routes to (on-call engineer, Slack channel, PagerDuty)
- What the on-call engineer's first action should be when the alert fires

You do not need to write actual PromQL here. Describe what the alert does in plain English clearly enough that a colleague could implement it.

---
### Expected Output

- Part 1: Completed error budget table with answers to both questions
- Part 2: Full calculations and written answers for all three scenarios, including the stated measurement point and independence assumption for Scenario C
- Part 3: Completed SLI definitions (including measurement point and eligible events for each), SLO table, error budget table, SLA proposal, and alert description

---
### Common Mistakes

**Setting SLO and SLA to the same number:** An external SLA is typically set less strictly than the internal SLO, giving the engineering team an operational buffer before an SLO breach becomes a contractual violation. If SLO and SLA are set to the same number, every SLO breach is immediately a contractual violation, which leaves no room to recover.

**Not showing calculations:** In a real engineering environment, your SLO decisions need to be defensible with data. Get into the habit of showing the math.

**Making the SLO too aspirational:** An SLO that you cannot actually meet is not an SLO. It is a wish. Do not base the target purely on your current best performance either, since that only reflects what the system happens to do today, not what users actually need or whether that level of reliability is worth its engineering cost. Start from a measurable SLI, then set the target using historical performance, real user expectations, business requirements, and the cost of achieving higher reliability. Review and adjust the target as you collect more evidence.

**Forgetting the time window:** "99.9% availability" is incomplete without specifying the measurement window and how the SLI is defined. The same outage consumes a tiny fraction of the yearly budget but more than half of the daily budget. Always specify the window.

**Forgetting the measurement point:** An SLI is incomplete and potentially misleading without clearly specifying its measurement point. The same service can show two different SLO outcomes for the identical outage, depending on whether the SLI is measured at its own internal boundary or end to end through every upstream dependency. State the measurement point every time you define an SLI, not just in this lab, and never multiply end-to-end SLIs together as though they were independent components.

---