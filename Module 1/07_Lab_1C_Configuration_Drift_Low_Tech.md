# Lab 1C: Configuration Drift, the Low Tech Version

---
> *This lab requires two Linux VMs (or two terminal sessions on one VM with separate directories simulating two machines). No cloud account, no Terraform, no cost.*
---
### Objective

Experience configuration drift at the most basic level: one machine managed by hand, one machine managed by a script. Then see how quickly the hand managed machine becomes unknowable while the scripted one stays reproducible.

This is deliberately primitive. Module 9 does the same exercise with real Terraform against real AWS infrastructure, and you will be asked to compare the two experiences directly.

### What You Need
- Two Linux VMs (Fedora or RHEL in VirtualBox, or two containers, or two directories on one VM if hardware is limited)
- A terminal
- A text editor
- Approximately 45 minutes

### Prerequisites
- Completed Part A of Module 1 (specifically the IaC section)
- Read Part B Section 6 (Infrastructure as Code), subsection on Configuration Drift
- Basic comfort with the terminal: navigating directories, creating files, running commands

---
### The Setup

You will make the same configuration change on two machines using two different methods, then observe what happens when an undocumented change is made to only one.

For this lab, the configuration change is: install Nginx, change the default listening port from 80 to 8080, and enable the service to start on boot.

If you only have one VM, create two directories (`~/vm-a` and `~/vm-b`) and work through the exercise conceptually for the manual steps while actually running the script for the scripted side. The important part is the comparison, not the infrastructure.

---
### Step 1: Machine A, the Manual Way

SSH into your first VM (or open a terminal for Machine A) and perform the following steps by hand, typing each command:

```bash
# Install nginx
sudo dnf install -y nginx

# Edit the config to change the port
sudo sed -i 's/listen       80;/listen       8080;/' /etc/nginx/nginx.conf

# Enable and start
sudo systemctl enable nginx
sudo systemctl start nginx

# Verify
curl http://localhost:8080
```

Do not write these steps down anywhere. Do not save them in a script. Just type them and move on. This is how most manual infrastructure changes actually happen: quickly, correctly, and without documentation.

---
### Step 2: Machine B, the Scripted Way

On your second VM (or in a second terminal), create a script:

```bash
cat > ~/setup-nginx.sh << 'SCRIPT'
#!/bin/bash
# Idempotent nginx setup script
# Running this multiple times produces the same result

set -euo pipefail

echo "Installing nginx..."
sudo dnf install -y nginx

echo "Configuring port 8080..."
# Only change the port if it is still set to 80
if grep -q 'listen       80;' /etc/nginx/nginx.conf; then
    sudo sed -i 's/listen       80;/listen       8080;/' /etc/nginx/nginx.conf
    echo "Port changed to 8080"
else
    echo "Port already configured, no change needed"
fi

echo "Enabling and starting nginx..."
sudo systemctl enable nginx
sudo systemctl start nginx

echo "Verifying..."
if curl -s http://localhost:8080 > /dev/null; then
    echo "SUCCESS: nginx responding on port 8080"
else
    echo "FAILURE: nginx not responding on port 8080"
    exit 1
fi
SCRIPT

chmod +x ~/setup-nginx.sh
```

Run the script:

```bash
~/setup-nginx.sh
```

Then run it again:

```bash
~/setup-nginx.sh
```

Notice the output on the second run. The script detects that the port is already configured and skips the change. This is idempotency: running the operation multiple times produces the same result.

---
### Step 3: Introduce Drift

Now simulate what happens in a real environment three weeks later. An engineer needs to quickly test something and makes a manual change to Machine A:

On Machine A only, change the server name:

```bash
# Quick manual fix, no documentation, no commit, no PR
sudo sed -i 's/server_name  _;/server_name  testing.local;/' /etc/nginx/nginx.conf
sudo systemctl restart nginx
```

Do not make this change to Machine B. Do not update any script. Do not write it down. Just do it and move on, exactly as an engineer under time pressure would.

---
### Step 4: Compare the Two Machines

Now answer each of the following questions by actually checking, not from memory:

**Question 1: What is the current state of Machine A?**

```bash
# On Machine A
grep -E 'listen|server_name' /etc/nginx/nginx.conf
```

Write down what you see.

**Question 2: What is the current state of Machine B?**

```bash
# On Machine B
grep -E 'listen|server_name' /etc/nginx/nginx.conf
```

Write down what you see.

**Question 3: Can you tell from Machine A's filesystem alone that a manual change was made?**

There is no log of the `sed` command you ran. There is no commit message. There is no PR. The only evidence is that the config file differs from what you originally typed in Step 1, and you would need to remember what you originally typed, which you cannot, because you did not write it down.

**Question 4: If you needed to build a third machine identical to Machine A's current state, could you?**

You would need to SSH into Machine A, read every config file, figure out which changes were intentional and which were accidental, and reproduce them by hand. For one Nginx config, this takes five minutes. For a production server with dozens of packages, custom kernel parameters, cron jobs, and application configs, this takes days and is never fully accurate.

**Question 5: If you needed to build a third machine identical to Machine B's current state, could you?**

Run the script. Done.

---
### Step 5: Write the Reflection

Create `labs/lab-1c/drift-reflection.md` in your devops-labs repository and answer the following:

1. What is the current state of Machine A? List every Nginx configuration difference from the default that you can identify.

2. What is the current state of Machine B? How do you know?

3. Machine A has drifted from its original configuration. At what point did the drift become invisible? What would have prevented it?

4. A new engineer joins the team tomorrow and needs to set up a development environment that matches production. Which machine can they reproduce, and how long would it take for each?

5. In Module 9, you will do this same exercise with Terraform against real AWS infrastructure. Based on what you experienced here, what do you expect `terraform plan` to show you that the manual approach could not? Write your prediction. You will come back and compare it.

---
### Step 6: Commit

```bash
cd ~/devops-labs
git add labs/lab-1c/drift-reflection.md
git add labs/lab-1c/setup-nginx.sh
git commit -m "feat(lab-1c): add configuration drift exercise and reflection"
git push origin main
```

---
### Expected Output

- The `setup-nginx.sh` script committed to your repository
- The `drift-reflection.md` file with written answers to all five questions
- A prediction about what Terraform will show you in Module 9 that you can verify later

---
### Note on Where the Terraform Version of This Lab Lives

Your old lab materials may include a Terraform drift detection exercise using AWS security groups. That exercise is now Lab 9F in Module 9 (Infrastructure as Code with Terraform and OpenTofu). It was moved because the original placement required Terraform before Terraform was taught. This low tech version exists so you experience the drift problem first, with no tooling at all, and then solve it properly with real IaC tooling in Module 9.

---
