# Lab 3A: Diagnose a Deliberately Broken DNS and Routing Scenario

**Module 3: Networking Fundamentals**
**Time:** 60 to 90 minutes
**Tools:** `ping`, `traceroute`, `ss`, `dig`, `ip route`, `curl`, `firewall-cmd`

---

> **Read before you touch anything.** This lab deliberately breaks networking on a machine you are logged into. Snapshot the VM before you begin. If you are working over SSH, keep a hypervisor console session open as a second way in. Deleting a default route over the same SSH session you depend on is a lesson every engineer learns exactly once, and there is no reason for it to be today.

---

## What This Lab Is Actually Teaching

Not the commands. You already have the commands. It is teaching the **order**, and the discipline of changing one variable at a time.

An engineer who runs the right five commands in the wrong order takes an hour. An engineer who runs them bottom to top takes four minutes. The difference is not talent and it is not typing speed. It is that every layer you confirm working eliminates an entire category of cause, and the engineer who skips a layer is guessing without knowing they are guessing.

---

## Environment

| VM | Role | OS | Networks |
|---|---|---|---|
| `vm-diag` | The target | RHEL 9, Rocky 9, Fedora, or CentOS Stream 9 | NAT with internet access |
| Any second machine | Remote tester | Anything | Must be able to reach `vm-diag` |

Install the tools **before** you break anything, because you will not be able to install them afterwards:

```bash
sudo dnf install -y bind-utils iproute traceroute mtr nginx nmap-ncat tcpdump
```

`bind-utils` provides `dig` and `nslookup`. Minimal cloud images ship without it, and an incident is a poor time to discover that.

---

## Step 0: Record the Healthy Baseline

You cannot recognize broken if you never looked at working. Capture this and keep it somewhere outside the VM.

```bash
ip -br addr show
ip route show
resolvectl status | head -20
cat /etc/resolv.conf
ping -c 3 8.8.8.8
dig +short redhat.com
ss -tlnp
```

---

## Step 1: Break It

Have a partner run this while you look away, or run it yourself and then deliberately stop thinking about what it did. Three faults land at once, on purpose, because a real incident does not arrive one symptom at a time.

```bash
#!/usr/bin/env bash
# break-network.sh    Run with sudo. Snapshot first.
set -x

CON=$(nmcli -g NAME connection show --active | head -1)

# Fault 1 (Layer 3): remove the default route
ip route del default

# Fault 2 (name resolution): point the resolver at an address that will never answer.
# 192.0.2.53 is inside TEST-NET-1, reserved for documentation, guaranteed dead.
nmcli connection modify "$CON" ipv4.ignore-auto-dns yes
nmcli connection modify "$CON" ipv4.dns "192.0.2.53"
nmcli connection up "$CON"

# Fault 3 (Layer 4): stop the web service and close its port
systemctl stop nginx
firewall-cmd --permanent --remove-service=http
firewall-cmd --reload

echo "Three faults introduced. Good luck."
```

Do not read the script again until you have finished diagnosing. If you already know the answers, the lab teaches you nothing.

---

## Step 2: Work the Layers, Bottom to Top

Each question rules out an entire category of failure before you climb. Write down what each command told you **as you go**, not afterwards from memory. That record is the deliverable.

---

### Question 1. Does this host have a valid address?

```bash
ip -br addr show
```

A `169.254.x.x` address means DHCP failed, and nothing above it can possibly work. A normal address means the interface is up and configured, and you may climb.

---

### Question 2. Does the host know how to leave its own subnet?

```bash
ip route show
ping -c 3 <gateway_ip>
```

This is where Fault 1 shows itself. With the default route gone, `ip route show` has no `default` line at all. The gateway still answers a ping, because it sits on the local link and needs no route to reach.

That exact combination, **local link healthy but no default route**, is the signature. Learn to see it on sight.

---

### Question 3. Can I reach the internet by address, with names taken out of the picture?

```bash
ping -c 3 8.8.8.8
```

Use an address here, never a hostname. If you ping a name at this stage and it fails, you have learned nothing, because the failure could be resolution or reachability and you have fused two questions into one result.

With Fault 1 in place this returns `Network is unreachable`. Read the message rather than skimming it. The kernel is not saying the far end is down. It is saying it never put a packet on the wire, because it has nowhere to send it.

**Fix Fault 1:**

```bash
sudo ip route add default via <gateway_ip> dev <interface>
ping -c 3 8.8.8.8          # now succeeds
```

---

### Question 4. Where does the packet die on the way out?

```bash
traceroute -n 8.8.8.8
```

`-n` skips reverse DNS lookups, so a broken resolver cannot make a routing tool appear to hang.

A trace that dies at the first hop is a local or gateway problem. A trace that runs several hops and then shows only asterisks usually means the path is fine and something downstream simply does not answer ICMP, which is common and often harmless. Do not treat every asterisk as a fault.

---

### Question 5. Does name resolution work, considered separately from reachability?

```bash
ping -c 3 8.8.8.8          # succeeds
ping -c 3 redhat.com       # fails
```

That pair is the classic DNS signature: the network is fine, names are not. Now stop pinging and use the tool that answers the resolution question **alone**.

```bash
dig redhat.com             # hangs, then times out
dig @1.1.1.1 redhat.com    # answers immediately
resolvectl status          # shows the configured resolver: 192.0.2.53
cat /etc/resolv.conf
```

The moment `dig @1.1.1.1` succeeds while plain `dig` times out, the fault is located and proven: DNS itself works, and the resolver this host was told to use does not answer. You found it by changing exactly one variable.

**Fix Fault 2:**

```bash
CON=$(nmcli -g NAME connection show --active | head -1)
sudo nmcli connection modify "$CON" ipv4.ignore-auto-dns no
sudo nmcli connection modify "$CON" ipv4.dns ""
sudo nmcli connection up "$CON"
resolvectl flush-caches
dig +short redhat.com      # now answers
```

---

### Question 6. Is anything listening on the port, and can anyone else reach it?

```bash
curl -I http://localhost   # Connection refused
ss -tlnp | grep ':80'      # nothing listening
```

`Connection refused` on localhost is unambiguous and instant. Nothing is bound to that port on this machine. It is not a firewall, because a firewall drop produces a hang, not a rejection. That single distinction is the most valuable thirty seconds in any incident.

```bash
sudo systemctl start nginx
ss -tlnp | grep ':80'      # now listening, and note the bind address
curl -I http://localhost   # 200 from the machine itself
```

Now test **from the second machine**. It hangs and eventually times out. Service listening, localhost fine, remote client hanging: that is a firewall, every single time.

```bash
sudo firewall-cmd --list-all               # http is absent from services
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload
```

Test again from the second machine. It answers.

> While you are in `ss -tlnp`, read the local address column carefully. A service bound to `127.0.0.1:80` passes every test you can run on the machine itself and is unreachable from every other machine on earth. `0.0.0.0:80` means all interfaces. This is the single most common reason a correctly running service is unreachable, and no amount of firewall work will ever fix it.

---

## Step 3: Deliverables

### 3A.1 The diagnostic log

Fill this in as you work. The order column is the entire point of the exercise.

| # | Command | Why I ran it at this point | What it told me | What it ruled out |
|---|---|---|---|---|
| 1 | `ip -br addr show` | Confirm an address exists before testing anything above it | Address present, link up | DHCP failure, interface down |
| 2 | `ip route show` | The next thing above an address is a route | No `default` entry | ... |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |
| 6 | | | | |
| 7 | | | | |
| 8 | | | | |

### 3A.2 Written answers

1. Both a missing default route and a dead resolver make `ping redhat.com` fail. Name the single command that distinguishes them, and explain why it is decisive.
2. You saw `Connection refused`, `Network is unreachable`, and a silent timeout in this lab. For each, say what happened to the packet and what that rules out.
3. You fixed Fault 3 in two separate actions. Explain why starting the service was not sufficient, and name the test that proved it.
4. `curl http://localhost` returns 200, but a colleague cannot reach the service. List, in order, the three things you would check, and why in that order.

---

## Troubleshooting

| Symptom | Likely cause | Check |
|---|---|---|
| Every command hangs, including ones with no network involvement | A broken resolver is making tools do reverse lookups | Add `-n` to `traceroute`, `ss`, and `ip` |
| `dig` not found | `bind-utils` was never installed, and now DNS is broken so you cannot install it | Restore from snapshot, install, break again |
| SSH session dies the moment you run the break script | You removed the default route on the path you were connected through | Use the hypervisor console, restore the route |
| Firewall changes appear to do nothing | You omitted `--permanent`, or omitted `--reload` after using it | `firewall-cmd --list-all` |

---

## Restore

```bash
sudo systemctl start nginx
sudo firewall-cmd --permanent --add-service=http && sudo firewall-cmd --reload
sudo ip route add default via <gateway_ip> dev <interface>
CON=$(nmcli -g NAME connection show --active | head -1)
sudo nmcli connection modify "$CON" ipv4.ignore-auto-dns no
sudo nmcli connection modify "$CON" ipv4.dns ""
sudo nmcli connection up "$CON"
```

Or roll back to the snapshot, which is faster and is why you took one.

---

## Assessment

You pass this lab when the diagnostic log shows a bottom to top order, every row states what the command **ruled out** rather than only what it showed, and the written answers correctly distinguish a refusal from a timeout from an unreachable network.

The habit this lab exists to build: when something is broken, start at Layer 3 and climb. Engineers who do this look fast. They are not faster. They are just not guessing.
