# Lab FM1.C: DevOps Infinity Loop Diagram

---
**Objective**
 
Internalize the eight DevOps lifecycle stages and the tools that operate at each one by building a reference diagram.

---
**What You Need**
 
Choose one: paper and pen, draw.io (app.diagrams.net, free), Mermaid (mermaid.live, free), or any diagramming tool.

---
**Prerequisites**
 
Read Section F.3 of this module before starting.

---
**Instructions**
 
Draw the DevOps infinity loop with all eight stages in the correct order:
```
Plan > Code > Build > Test > Release > Deploy > Operate > Monitor
```

Your diagram must include:
 
1. All eight stages are labeled in order

2. At least two tools are labeled at each stage from the table below

3. Arrows showing the continuous cyclic flow, including the feedback arrow from Monitor back to Plan

4. One sentence annotation at each stage describing what happens there


**Tool reference**
 
| Stage | Tools to Label |
|---|---|
| Plan | Jira, Confluence, GitHub Issues |
| Code | Git, GitHub, VS Code |
| Build | GitHub Actions, Jenkins, Maven |
| Test | PyTest, Selenium, Trivy |
| Release | GitHub Actions, Jenkins |
| Deploy | Ansible, Terraform, Kubernetes, ArgoCD |
| Operate | Kubernetes, Ansible |
| Monitor | Prometheus, Grafana, Elastic Stack, Jaeger |

---
**Expected Output**

A diagram image (PNG, JPG, or PDF), a Mermaid code block that renders correctly, or a clear photograph of a hand-drawn diagram.

---
**Reference diagram:**
 
![DevOps Infinity Loop](https://github.com/user-attachments/assets/b9499b9d-f59e-424f-8830-8d754548c123)

---
**Common mistakes to avoid**
 
- Drawing the loop as linear (left to right) instead of cyclic. The infinity shape is intentional: the process never ends.

- Labeling stages without annotations. Annotations show understanding of what happens at each stage, not just the names.

- Using only one tool per stage.

---