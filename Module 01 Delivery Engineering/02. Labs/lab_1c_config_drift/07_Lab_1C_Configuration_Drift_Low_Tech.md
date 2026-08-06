# Lab 1C: Configuration Drift, the Low Tech Version


> This lab requires two Linux VMs, or two terminal sessions on one VM with separate directories simulating two machines. No cloud account, no Terraform, no cost.

### Objective

Experience configuration drift at the simplest level: one machine changed by hand, one machine configured by a script. Then see how quickly the hand managed machine becomes hard to reason about while the scripted one stays reproducible.

This lab is intentionally primitive. In Module 9, you will do the same kind of exercise with Terraform against real AWS infrastructure and compare the two experiences directly.

### What You Need
- Two Linux VMs, or two containers, or two directories on one VM if hardware is limited
- A terminal
- A text editor
- About 45 minutes

### Prerequisites
- Completed Part A of Module 1, especially the IaC section
- Read Part B Section 6, Infrastructure as Code, including configuration drift
- Basic comfort with the terminal: navigating directories, creating files, running commands

---

## The Setup

You will make the same configuration change on two machines using two methods, then observe what happens when an undocumented change is made to only one.

For this lab, the configuration goal is:

- install Nginx
- configure it to listen on port 8080
- enable the service to start on boot, if your environment supports `systemd`

To make the lab more reliable across Fedora and RHEL style systems, you will create a dedicated config file for this lab instead of editing `nginx.conf` with whitespace sensitive `sed` commands.

**One more thing that trips people up on a fresh Fedora or RHEL VM:** SELinux, which is enabled and enforcing by default on both, only allows nginx to bind to a specific set of ports out of the box (80, 81, 443, 488, 8008, 8009, 8443, and 9000). Port 8080 is not on that list, it's actually reserved for caching proxies. If you skip the SELinux step below, nginx will fail to bind to 8080 and the whole lab will look broken even though every config file is correct. This is included as its own explicit step so it doesn't cost you time guessing.

If you only have one VM, create two directories such as `~/vm-a` and `~/vm-b` and work through the comparison conceptually. If you are using containers or directory based simulation, `systemctl` and SELinux tooling may not apply. In that case, focus on the file state and reproducibility lesson rather than service boot behavior.

---

## Step 1: Machine A, the Manual Way

SSH into your first VM, or open a terminal for Machine A, and perform these steps by hand.

```bash
# Install nginx
sudo dnf install -y nginx
```
```bash
# Allow nginx to bind to port 8080 under SELinux
# (port 8080 is labeled for caching proxies by default, not for a server to listen on)
sudo dnf install -y policycoreutils-python-utils
if ! sudo semanage port -a -t http_port_t -p tcp 8080 2>/dev/null; then
    sudo semanage port -m -t http_port_t -p tcp 8080
fi
```
```bash
# Create a simple server block for this lab
cat << 'EOF' | sudo tee /etc/nginx/conf.d/lab1c.conf > /dev/null
server {
    listen 8080;
    server_name _;
    location / {
        return 200 'lab1c machine a';
        add_header Content-Type text/plain;
    }
}
EOF
```
```bash
# Validate config
sudo nginx -t

# Enable and start
sudo systemctl enable nginx
sudo systemctl restart nginx
```
```bash
# Verify
curl http://localhost:8080
```

Do not save these steps in a script. Do not document them anywhere. Just type them and move on.

That is the point. Manual infrastructure changes are often made quickly and correctly, but without a durable, reviewable, version controlled record of how the machine reached its current state.

---
## Step 2: Machine B, the Scripted Way

On your second VM, or in a second terminal, create a script:

```bash
cat > ~/setup-nginx.sh << 'SCRIPT'
#!/bin/bash
# Idempotent nginx setup script

set -euo pipefail

echo "Installing nginx..."
sudo dnf install -y nginx

echo "Configuring SELinux to allow nginx on port 8080..."
if command -v semanage > /dev/null 2>&1; then
    if ! sudo semanage port -a -t http_port_t -p tcp 8080 2>/dev/null; then
        sudo semanage port -m -t http_port_t -p tcp 8080
    fi
else
    echo "semanage not found, installing policycoreutils-python-utils..."
    sudo dnf install -y policycoreutils-python-utils
    if ! sudo semanage port -a -t http_port_t -p tcp 8080 2>/dev/null; then
        sudo semanage port -m -t http_port_t -p tcp 8080
    fi
fi

echo "Writing lab config..."
cat << 'EOF' | sudo tee /etc/nginx/conf.d/lab1c.conf > /dev/null
server {
    listen 8080;
    server_name _;
    location / {
        return 200 'lab1c machine b';
        add_header Content-Type text/plain;
    }
}
EOF

echo "Validating nginx config..."
sudo nginx -t

echo "Enabling and starting nginx..."
sudo systemctl enable nginx
sudo systemctl restart nginx

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

The second run should produce the same end state. That is the key idea: the script gives you a repeatable path back to the intended configuration, including the SELinux port rule, which is exactly the kind of easy to forget, one time system state that gets lost when work is done by hand.

Note that this is still a simple shell script, not a full declarative system. It is more reproducible than manual work, but not as strong as proper infrastructure as code.

---
## Step 3: Introduce Drift

Now simulate what happens three weeks later when someone makes a quick manual change to Machine A only.

On Machine A, edit the config by hand:

```bash
sudo sed -i 's/server_name _;/server_name testing.local;/' /etc/nginx/conf.d/lab1c.conf
```
```bash
sudo nginx -t
```
```bash
sudo systemctl restart nginx
```

Do not make this change on Machine B. Do not update any script. Do not write it down. Just do it and move on.

This is the drift event.

---
## Step 4: Compare the Two Machines

Now answer these questions by checking the machines, not from memory.

### Question 1: What is the current state of Machine A?

```bash
cat /etc/nginx/conf.d/lab1c.conf
```

Write down what you see.

### Question 2: What is the current state of Machine B?

```bash
cat /etc/nginx/conf.d/lab1c.conf
```

Write down what you see.

### Question 3: Can you tell from Machine A's filesystem alone that a manual change was made?

Maybe you can see that the file is different from what you remember. You may also have weak clues such as file timestamps.

But unless your environment has shell auditing or session recording, you usually do **not** have a durable, reviewable, version controlled record explaining:
- who changed it
- why they changed it
- whether it was reviewed
- how to reproduce the new state safely

That is the real operational problem.

### Question 4: If you needed to build a third machine identical to Machine A's current state, could you?

Only by inspecting the machine, reading files, guessing which changes were intentional, and recreating them manually. That inspection also has to include system level state that never shows up in a config file at all, like the SELinux port rule you added by hand in Step 1.

For one Nginx file, that is manageable. For a real server with many packages, services, and custom configs, it becomes slow and unreliable.

### Question 5: If you needed to build a third machine identical to Machine B's current state, could you?

Yes. Run the script.

---
## Step 5: Write the Reflection

Create `labs/lab-1c/drift-reflection.md` in your `devops-labs` repository and answer:

1. What is the current state of Machine A? List every Nginx configuration difference from the original lab config that you can identify.

2. What is the current state of Machine B? How do you know?

3. Machine A has drifted from its original configuration. At what point did the drift become hard to see? What would have prevented it?

4. A new engineer joins the team tomorrow and needs a development environment that matches production. Which machine can they reproduce, and how long would each take?

5. In Module 9, you will do this same exercise with Terraform against real AWS infrastructure. Based on this lab, what do you expect `terraform plan` to show you that the manual approach could not? Write your prediction. You will compare it later.

---
## Step 6: Commit

If you created the script on Machine B, copy it into your repository first so it is tracked.

```bash
mkdir -p ~/devops-labs/labs/lab-1c
```
```bash
cp ~/setup-nginx.sh ~/devops-labs/labs/lab-1c/setup-nginx.sh
```
```bash
cd ~/devops-labs
```
```bash
git add labs/lab-1c/drift-reflection.md
```
```bash
git add labs/lab-1c/setup-nginx.sh
```
```bash
git commit -m "feat(lab-1c): add configuration drift exercise and reflection"
```
```bash
git push origin main
```

---
## Expected Output

- `labs/lab-1c/setup-nginx.sh` committed to your repository
- `labs/lab-1c/drift-reflection.md` with written answers to all five questions
- A prediction about what Terraform will show in Module 9 that the manual approach could not

---
## Notes

### About SELinux and port 8080
If `curl http://localhost:8080` fails right after `systemctl restart nginx`, check whether SELinux is the cause before anything else:

```bash
sudo semanage port -l | grep 8080
```

If you see `http_cache_port_t` instead of `http_port_t` next to 8080, that's why nginx can't bind to it. Run the `semanage port -m -t http_port_t -p tcp 8080` command from Step 1 or Step 2 to fix it, then restart nginx again. You can also confirm SELinux is the culprit by checking `sudo tail /var/log/audit/audit.log | grep nginx` for a denial message, or by temporarily running `sudo setenforce 0` to test (remember to run `sudo setenforce 1` afterward, this is a diagnostic step only, not a fix).

### About service startup
If your environment does not support `systemctl`, skip the enable on boot part and focus on the file state comparison and reproducibility lesson.

### About local testing
If `curl http://localhost:8080` still fails after confirming SELinux is not the issue, first run:

```bash
sudo nginx -t
```

Then inspect the Nginx service status with `sudo systemctl status nginx`.

---
### About the Terraform version of this lab

Older course materials may place a Terraform drift detection exercise earlier in the course. That exercise now lives in Module 9 because it depends on Terraform knowledge you do not yet have.

This low tech version exists so you experience the drift problem first with almost no tooling, then solve it properly with real IaC tooling later.

---