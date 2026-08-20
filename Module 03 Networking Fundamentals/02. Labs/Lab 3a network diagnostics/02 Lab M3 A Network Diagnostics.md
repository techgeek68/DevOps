# Lab 3A: Network Diagnostics, DNS and Routing

**Module 3: Networking Fundamentals**

> **Status: merged and updated.** This lab is built from your existing Lab M2.A. The tool reference in Part 2, the healthy baseline in Part 3, the deliberate DNS break, and the routing section are all preserved. What is new: a Layer 4 stage using `ss` and `firewalld`, so the lab now exercises all four tools the new syllabus names (`ping`, `traceroute`, `ss`, `dig`) as diagnostic instruments rather than only as reference material; a diagnostic log table that forces you to record the **order** you worked in, which the new syllabus asks for explicitly; and corrections where commands have changed since the original was written. Nothing useful was discarded.

---
### Objective

Use the standard Linux networking toolkit, `ping`, `traceroute`, `ss`, `nslookup`, and `dig`, to diagnose a deliberately broken DNS and routing scenario. Before breaking anything, you will build a solid working knowledge of each tool's flags and output. By the end, you will have practiced the bottom up diagnostic habit from the study note on a real, broken system instead of a healthy one, which is where the habit actually earns its value.

The new requirement, and the one you will be assessed on: **document what each command actually told you, and in what order you used them.** The commands are not the skill. The order is the skill. An engineer who runs the right five commands in the wrong order takes an hour; one who runs them bottom to top takes four minutes.

---
### What You Need

- A Linux VM (Fedora, CentOS Stream 9, RHEL 9, or Rocky 9) with network access
- Sudo access on the VM
- A second machine, any operating system, that can reach the VM over the network. Part 6 requires testing from off the box.
- Required tools: `ping`, `traceroute`, `ss`, `nslookup`, `dig`, `curl`, `firewall-cmd`

### Prerequisites

- Read Module 3 sections 3.1 (the OSI model), 3.2 (TCP/IP), 3.3 (routing), and 3.4 (DNS)
- A working VM from the Module 2 virtualization setup
- **Take a snapshot before you begin.** This lab breaks networking on a machine you are logged into. If you are connected over SSH, keep a hypervisor console session open as a second way in.

---
### Part 1: Build Your Diagnostic Toolkit

Before breaking anything, confirm every tool you need is installed and working. You cannot install packages after you have broken DNS, which is a lesson better learned here than during an incident.

- Confirm each tool is present
```bash
which ping traceroute ss nslookup dig curl
```
- Install anything missing
```bash
sudo dnf install -y traceroute bind-utils mtr nginx
```

`ping` and `ss` ship with the base system. `traceroute` and the DNS tools (`nslookup`, `dig`) come from separate packages on Fedora and RHEL family systems; `dig` lives in `bind-utils`, which minimal cloud images routinely omit.

---
### Part 2: Understand Your Tools

Work through each tool below before moving on. For each one, run the example commands against a known good target and read the explanation of what the output means. You will rely on this reference throughout the rest of the lab.

---
#### `ping`

`ping` sends ICMP Echo Request packets to a host and reports whether it responds. It tests basic reachability at Layer 3.

```bash
# Basic ping: send 4 packets and stop
ping -c 4 8.8.8.8

# Ping a hostname (tests DNS resolution AND reachability, two questions in one result)
ping -c 4 google.com

# Ping with a specific packet size (tests MTU issues)
ping -c 4 -s 1400 8.8.8.8
```

**What the output tells you:**

- `icmp_seq`: sequence number. Gaps indicate dropped packets.
- `ttl`: Time to Live. Lower TTL suggests more hops to the destination.
- `time`: round trip latency in milliseconds.
- `packet loss`: any percentage above 0% indicates a network problem.

**Diagnostic scenarios:**

- `ping 8.8.8.8` succeeds but `ping google.com` fails: DNS resolution is broken, not connectivity.
- `ping 192.168.1.1` (your gateway) fails: a local network or firewall issue, not an internet issue.
- 100% packet loss: the host is unreachable, a firewall is blocking ICMP, or the host does not exist.

**Read the error text, not just the failure.** These three are not interchangeable, and telling them apart is the fastest thirty seconds available to you in an incident:

| Message | What happened to the packet | What it rules out |
|---|---|---|
| `Network is unreachable` | It was never sent. The kernel has no route toward that destination. | Everything above Layer 3. Fix the route first. |
| Silent timeout, no reply | It was sent, and something swallowed it. A firewall dropping, or no return path. | A listening service answering, since nothing answered at all. |
| `Destination host unreachable` | It reached a router that had nowhere to forward it, or ARP failed on the local link. | A correct next hop. |

> Some hosts block ICMP even when services on them are perfectly reachable. A failed `ping` does not conclusively prove a host is down. Follow up with `curl` or `nc -zv` on a specific port.

---
#### `traceroute`

`traceroute` maps the path packets take from your host to a destination, showing each router hop along the way.

```bash
# Basic traceroute
traceroute 8.8.8.8

# Skip reverse DNS lookups, so a broken resolver cannot make a routing tool appear to hang
traceroute -n 8.8.8.8

# Use ICMP instead of UDP (sometimes gets through firewalls that block UDP)
sudo traceroute -I 8.8.8.8

# Continuous trace showing per hop loss over time
mtr -n 8.8.8.8
```

**What the output tells you:**

- Each line is one router hop.
- Three latency values are shown, one per probe.
- `* * *` means the router does not respond to traceroute probes. This is common on internet routers and does not necessarily mean the path is broken. **If later hops respond, the route is working.**

**Corrections from the earlier version of this lab:** the default UDP mode generally runs unprivileged on current Linux. The ICMP mode (`-I`) is the one that needs root or the `cap_net_raw` capability, hence the `sudo` above. Always add `-n` when you are already suspicious of DNS, or you will be diagnosing your resolver while believing you are diagnosing your routes.

**When to use it:**

- A server is reachable but slow. Traceroute shows which hop adds the latency.
- Traffic is not arriving at the right destination.
- Debugging routing inside a VPC, between VPCs, or across a static route you configured yourself (you will do exactly this in Lab 3C).

---
#### `ss` (Socket Statistics), and `netstat`

`ss` is the modern replacement for `netstat`. Both show active connections and listening sockets. Use them to answer a Layer 4 question that nothing else answers: **is anything actually listening, and on which interface?**

```bash
# Show all listening TCP sockets with process names
ss -tlnp

# Show all listening UDP sockets
ss -ulnp

# Show all established connections
ss -tnp

# Connections on a specific port
ss -tnp | grep :22

# Summary statistics
ss -s

# Count connections by TCP state: the first check when you suspect port exhaustion
ss -tan | awk '{print $1}' | sort | uniq -c | sort -rn

# netstat equivalent, for reference on older systems
netstat -tlnp
```

**Major flags:** `-t` TCP, `-u` UDP, `-l` listening only, `-n` numeric (no name resolution), `-p` show the owning process.

**Reading `ss -tlnp`, and this is the part that matters:**

- `0.0.0.0:22` means sshd is listening on **all** interfaces on port 22, reachable from other machines.
- `127.0.0.1:3306` means MySQL is listening **only on localhost** and cannot be reached from outside the machine, no matter what the firewall says.
- The Process column shows exactly which process owns each socket.

> A service bound to `127.0.0.1` passes every test you can run on the machine itself and is unreachable from every other machine on earth. This is the single most common reason a correctly running service is unreachable, and no amount of firewall work will ever fix it. Read the local address column before you touch `firewall-cmd`.

---
#### `nslookup`

`nslookup` queries DNS servers to resolve hostnames to IP addresses, or the reverse.

```bash
# Resolve a hostname to an IP
nslookup google.com

# Reverse lookup: IP to hostname
nslookup 8.8.8.8

# Query a specific DNS server, bypassing your default resolver
nslookup google.com 1.1.1.1

# Query for a specific record type
nslookup -type=MX google.com
nslookup -type=NS google.com
nslookup -type=TXT google.com
```

**What the output tells you:**

- `Server:` which DNS resolver your system used.
- `Non-authoritative answer:` the response came from a cache, not the authoritative name server.
- The resolved address.

> `nslookup` is fine for a quick answer. For anything you actually need to reason about, use `dig`.

---
#### `dig`

`dig` is the primary tool for DNS diagnostics. It gives full control over what you query and shows the complete response, including TTL values, record types, and which server answered.

```bash
# Basic forward lookup
dig google.com

# Specific record types
dig google.com A
dig google.com AAAA
dig google.com MX
dig google.com NS
dig google.com TXT

# Reverse lookup
dig -x 8.8.8.8

# Query a specific DNS server directly, bypassing your local configuration
dig @1.1.1.1 google.com A

# Short output, just the answer
dig +short google.com A

# Trace the full resolution path from the root servers down, ignoring caches
dig +trace google.com
```

**Reading `dig google.com A`:**

| Field | Example | Meaning |
|---|---|---|
| status | `NOERROR` | Query succeeded. `NXDOMAIN` means the name does not exist at all, a very different problem from the name existing and pointing somewhere wrong. |
| ANSWER SECTION | `142.250.182.14` | The records returned |
| TTL | `122` | Seconds remaining before this cached answer expires |
| SERVER | `10.10.0.1` | Which resolver answered |
| Query time | `9ms` | Fast, so likely cached upstream |

> The single most useful `dig` habit: **`dig` against your resolver, then `dig @1.1.1.1` against a public one.** If the second works and the first does not, the fault is your local DNS configuration, and you have proven it by changing exactly one variable. You will use this in Part 5.

> `dig +trace` is the tool for the case where an authoritative server has the correct new answer but your application still sees the old one. It walks the chain from root to TLD to authoritative, ignoring caches. If the authoritative answer is right and yours is wrong, the problem is a cache between the two, which is a TTL problem, not a DNS configuration problem.

---
### Part 3: Establish a Healthy Baseline

You cannot recognize broken behavior if you have never seen working behavior on the same machine. Run each tool once against a known good target and record the output **before** you touch any configuration.

```bash
# Layer 3: does this host have an address, and a route out?
ip -br addr show
ip route show

# Layer 3: basic reachability, names taken out of the picture
ping -c 4 8.8.8.8

# Layer 3 plus name resolution, two questions fused into one result
ping -c 4 google.com

# The path packets take to a known good destination
traceroute -n 8.8.8.8

# Layer 4: what is listening on this machine
ss -tlnp

# Name resolution, working normally
nslookup google.com
dig google.com A
resolvectl status | head -20
```

For each command, write one sentence in your own words describing what a healthy result looks like. You will compare this baseline against the broken scenario in Part 5.

---
### Part 4: Break It Deliberately

You are about to misconfigure your own VM. This is safe in a lab VM. Do not do this on a production system.

Three faults, introduced at once, on purpose. A real incident does not arrive one symptom at a time, and a lab that breaks one thing teaches a habit that fails the moment two things break together.

Have a partner run this script while you look away, or run it yourself and then stop thinking about what it did.

```bash
#!/usr/bin/env bash
# break-network.sh    Run with sudo. Snapshot first.
set -x

CON=$(nmcli -t -f NAME connection show --active | head -1)

# Back up the resolver configuration, as in the original lab
cp /etc/resolv.conf /etc/resolv.conf.backup

# Fault 1, Layer 3: remove the default route
ip route del default

# Fault 2, name resolution: point the resolver at an address that will never answer.
# 192.0.2.0/24 is TEST-NET-1, reserved for documentation, guaranteed never to be a real host.
nmcli connection modify "$CON" ipv4.dns "192.0.2.1"
nmcli connection modify "$CON" ipv4.ignore-auto-dns yes
nmcli connection up "$CON"

# Fault 3, Layer 4: stop the web service and close its port
systemctl stop nginx
firewall-cmd --permanent --remove-service=http
firewall-cmd --reload

echo "Three faults introduced."
```

> **Why the `nmcli` route and not just editing `/etc/resolv.conf`.** The original version of this lab edited the file directly and then noted that NetworkManager tends to overwrite it. On RHEL 9 and Fedora that file is generated, not authored: an edit may survive for minutes and then vanish, which produces a fault that appears to fix itself and teaches nothing. Configure the resolver where the system actually reads it from.

---
### Part 5: Diagnose, Bottom to Top

Work the layers in order. Do not skip a step because you think you already know the answer. Capture every command and its output as you go; the record is the deliverable.

**Step 1, does the host have a valid address?**

```bash
ip -br addr show
```

A `169.254.x.x` address means DHCP failed, and nothing above it can work. A normal address means you may climb.

**Step 2, does the host know how to leave its own subnet?**

```bash
ip route show
ping -c 3 <gateway_ip>
```

Fault 1 shows itself here. There is no `default` line. The gateway still answers a ping, because it sits on the local link and needs no route to reach. **Local link healthy, no default route** is the signature. Write down what that combination rules out.

**Step 3, reachability with names taken out of the picture.**

```bash
ping -c 4 8.8.8.8
```

Use an address, never a hostname, at this stage. `Network is unreachable` is the kernel telling you it never put a packet on the wire. That is not the far end being down.

Fix Fault 1, then continue:

```bash
sudo ip route add default via <gateway_ip> dev <interface>
ping -c 4 8.8.8.8            # now succeeds
```

**Step 4, where does the packet die on the way out?**

```bash
traceroute -n 8.8.8.8
```

A trace that dies at the first hop is local. A trace that runs several hops and then shows asterisks usually means the path is fine and something downstream does not answer ICMP. Do not treat every asterisk as a fault.

**Step 5, name resolution, considered separately from reachability.**

```bash
ping -c 4 8.8.8.8            # succeeds
ping -c 4 google.com         # fails
```

That pair is the classic DNS signature: the network is fine, names are not. Now stop pinging and use the tools that answer the resolution question alone.

```bash
nslookup google.com          # error or timeout, capture the exact message
dig google.com A             # hangs, then times out
resolvectl status            # shows the configured resolver: 192.0.2.1
cat /etc/resolv.conf
```

**Step 6, isolate it by changing exactly one variable.**

```bash
dig @8.8.8.8 google.com A
dig @1.1.1.1 google.com A
```

Both succeed. Write two or three sentences explaining why this single command proves the problem is specifically your local DNS configuration, and not a broader internet connectivity problem, and not a problem with anyone else's DNS infrastructure.

**Step 7, cross check with authoritative data.**

```bash
nslookup -type=NS github.com
dig @1.1.1.1 github.com A
dig +trace github.com
```

From the `+trace` output, identify the root server, the TLD server, and the authoritative name server for `github.com`. Note the TTL on the answer, and state what it would mean for a cutover if that TTL were 86400 rather than what it is.

**Step 8, Layer 4. Is anything listening, and can anyone else reach it?**

```bash
curl -I http://localhost      # Connection refused
ss -tlnp | grep ':80'         # nothing listening
```

`Connection refused` on localhost is unambiguous and instant: nothing is bound to that port on this machine. It is **not** a firewall, because a firewall drop produces a hang, not a rejection.

```bash
sudo systemctl start nginx
ss -tlnp | grep ':80'         # now listening. Read the local address column.
curl -I http://localhost      # 200 from the machine itself
```

Now test **from the second machine**:

```bash
curl -I http://<vm-ip>        # hangs, then times out
```

Service listening, localhost fine, remote client hanging. That is a firewall, every single time.

```bash
sudo firewall-cmd --list-all                        # http is absent from the services list
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload
curl -I http://<vm-ip>                              # from the second machine: answers
```

---
### Part 6: Fix and Verify

```bash
CON=$(nmcli -t -f NAME connection show --active | head -1)
sudo nmcli connection modify "$CON" ipv4.ignore-auto-dns no
sudo nmcli connection modify "$CON" ipv4.dns ""
sudo nmcli connection up "$CON"
sudo resolvectl flush-caches
```

Confirm against your Part 3 baseline:

```bash
nslookup google.com
dig google.com A
ping -c 4 google.com
ip route show
ss -tlnp | grep ':80'
```

All should now match the healthy baseline.

> **Correction:** the old `systemd-resolve --flush-caches` form appears in most tutorials. The binary was renamed `resolvectl` in systemd 239, and `systemd-resolve` survives only as a deprecated symlink. Use `resolvectl flush-caches`.

---
### Part 7: The Routing Table, Read Properly

```bash
ip route show
```

```
default via 192.168.1.1 dev enp0s1 proto dhcp metric 100
192.168.1.0/24 dev enp0s1 proto kernel scope link src 192.168.1.50 metric 100
```

The second line is a **directly connected route**, added by the kernel the moment an address was assigned. Anything in that range is reachable on the local link with no router involved.

The first line is the **catch all**. `default` is another way of writing `0.0.0.0/0`, the route that matches every possible address. Anything matching no other entry goes there.

When several routes could match, the kernel picks the **longest prefix**, meaning the most specific. Ask it directly rather than reasoning in your head:

```bash
ip route get 8.8.8.8
ip route get <gateway_ip>
```

Now compare two traces:

```bash
traceroute -n <gateway_ip>      # completes in one hop
traceroute -n 8.8.8.8           # several hops
```

Write two or three sentences explaining what the default route line means and exactly what would happen to your outbound traffic if it were deleted. You have already seen the answer in Step 2, so answer from what you observed, not from theory.

---
### Deliverable: The Diagnostic Log

This table is the new requirement, and it is the centre of the assessment. Fill it in **as you work**, not afterwards from memory. The `ruled out` column is what separates diagnosis from guessing.

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
| 9 | | | | |
| 10 | | | | |

---
### Lab Tasks Summary

Document all of the following in a single write up:

1. Your healthy baseline output from Part 3, with one sentence per tool describing normal behavior
2. The exact faults introduced in Part 4
3. **The completed diagnostic log table**, showing the order you worked in and what each step ruled out
4. Your full bottom to top diagnosis from Part 5, with reasoning written out at each step, not just raw output
5. The specific command and reasoning that proved the problem was local DNS configuration and not broader connectivity
6. Your `nslookup -type=NS github.com` output identifying GitHub's authoritative name servers, and your comparison of the `1.1.1.1` answer against your local resolver's answer
7. A `dig +trace github.com` run identifying the root server, TLD server, and authoritative name server, plus the TTL and what it would mean during a cutover
8. Your Layer 4 evidence: `ss -tlnp` before and after starting nginx, `curl` from localhost, and `curl` from the second machine before and after the firewall change
9. Confirmation that you restored everything in Part 6
10. Your routing table output from Part 7 and your explanation of the default route

**Written answers:**

1. Both a missing default route and a dead resolver make `ping google.com` fail. Name the single command that distinguishes them and explain why it is decisive.
2. You saw `Connection refused`, `Network is unreachable`, and a silent timeout. For each, say what happened to the packet and what that rules out.
3. Starting nginx was not enough to make the service reachable. Name the test that proved a second fault existed, and explain why testing only from localhost would have hidden it forever.

**Submission:** paste the command and output for each item, with a one sentence explanation under each. Real captured output, not paraphrased.

---
### Common Issues

**`/etc/resolv.conf` keeps reverting on its own.** On RHEL 9 and Fedora, the file is generated by NetworkManager or systemd-resolved. Configure the resolver with `nmcli ipv4.dns` and `ipv4.ignore-auto-dns`, as Part 4 does, rather than editing the file.

**`ping 8.8.8.8` also fails, not just `ping google.com`.** That is Fault 1, and it is intentional in this version of the lab. Confirm with `ip route show` that the `default` line is missing, restore it, and continue.

**Every command hangs, including ones with no network involvement.** A broken resolver makes tools do reverse lookups that time out. Add `-n` to `traceroute`, `ss`, and `ip`.

**`traceroute` shows nothing but asterisks for every hop.** Some networks block the UDP probes traceroute uses by default. Try `sudo traceroute -I 8.8.8.8` to switch to ICMP, which needs root.

**Your SSH session dies the moment you run the break script.** You removed the default route on the path you were connected through. Use the hypervisor console, restore the route, and take the snapshot warning seriously next time.

**`dig: command not found`, and now DNS is broken so you cannot install it.** Restore from the snapshot, install `bind-utils`, break it again. This failure is the reason Part 1 exists.

---
### Expected Output

A written report containing all ten items above with real captured command output, the completed diagnostic log table, and the three written answers.
