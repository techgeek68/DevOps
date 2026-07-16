# Lab 3C: Static Routing

**Module 3: Networking Fundamentals**

> **Status: merged and updated.** Built from your existing Lab M2.C. The two VM topology, the interface identification step, the before and after routing table capture, the `ip route add` walkthrough, the traceroute verification, the ordered troubleshooting checklist, and all three reflection questions are preserved. What changed: IP forwarding is now presented as one of **two** gates rather than one, because `firewalld` filters forwarded traffic and a router with `ip_forward=1` can still drop every packet, which is the single most common way this lab fails; persistence via `nmcli` is now a required step rather than a footnote, so the route survives a reboot; `ip route get` is added, since it is the fastest way to make the kernel explain its own decision; and an optional Part 9 adds a third VM to demonstrate the missing return route, a failure the two VM topology cannot produce and which every engineer eventually meets.

---
### Objective

Configure a static route between two VMs sitting on different subnets and watch connectivity go from failing to working as the direct, visible result of a single command. This makes the abstract idea of a routing table concrete by forcing you to build, break, and fix connectivity yourself rather than reading about how it works.

The syllabus requirement: **show `ip route` before and after.** That before and after pair is the evidence, and it is the whole point.

---
### What You Need

- Two Linux VMs on the same hypervisor, each with two network interfaces
- Sudo access on both
- Optional for Part 9: a third VM with one interface on the second subnet

---
### Prerequisites

- Read Module 3 sections 3.3 (Routing) and 3.10 (NAT, Addressing, and CIDR)
- Two VMs cloned from your base image, following the cloning process from the Module 2 virtualization labs
- Each VM must have a second network adapter attached, in addition to the management adapter you SSH in through
- **Snapshot both VMs.** This lab changes kernel forwarding behaviour and firewall zones.

---
### Lab Network Design

| Host | Interface | IP Address | Role |
|---|---|---|---|
| VM1 | Management (existing) | Whatever you currently SSH in on | Reaching the VM from your host machine |
| VM1 | Private (second adapter) | 10.0.1.1/24 | Source host in Subnet A |
| VM2 | Management (existing) | Whatever you currently SSH in on | Reaching the VM from your host machine |
| VM2 | Private (second adapter) | 10.0.1.254/24 **and** 10.0.2.1/24 | Router between Subnet A and Subnet B, and the destination |

The goal: make VM1, sitting in Subnet A at `10.0.1.1`, able to reach `10.0.2.1` in Subnet B, an address only VM2 holds. VM1 has no way to reach Subnet B until you explicitly tell it how.

Confirm both VMs have a second adapter attached **on the same virtual network** in your hypervisor settings before starting. In VirtualBox this usually means both second adapters on the same Host Only or Internal network. If they are on different virtual networks, no amount of correct IP configuration will save you, because the underlying wiring is wrong.

---
### Step 1: Identify Your Second Interface Name

Interface names vary by hypervisor and configuration.

```bash
ip -br link
```

Look for an interface beyond `lo` and your existing management interface. It might be `ens224`, `eth1`, `enp0s8`, or similar. Use the actual name you see wherever this guide says `<private-iface>`.

---
### Step 2: Assign the Addresses

On **VM1**:

```bash
sudo ip addr add 10.0.1.1/24 dev <private-iface>
sudo ip link set <private-iface> up
ip addr show <private-iface>
```

On **VM2**:

```bash
sudo ip addr add 10.0.1.254/24 dev <private-iface>
sudo ip addr add 10.0.2.1/24 dev <private-iface>
sudo ip link set <private-iface> up
ip addr show <private-iface>
```

VM2 now holds two addresses on one physical interface, one in each subnet. This is intentional and it is what lets VM2 act as the connection point between Subnet A and Subnet B.

These addresses are temporary and will not survive a reboot. Step 8 makes the routing persistent; persisting the addresses themselves follows the same `nmcli` pattern.

---
### Step 3: Gate One, Enable IP Forwarding on VM2

By default, Linux does not forward packets between interfaces or between subnets it holds. A packet arriving for an address the host does not own is dropped unless forwarding is explicitly enabled.

On **VM2 only**:

```bash
# Current value. 0 means forwarding is off.
cat /proc/sys/net/ipv4/ip_forward

# Enable immediately
sudo sysctl -w net.ipv4.ip_forward=1
sysctl net.ipv4.ip_forward
```

Expected: `net.ipv4.ip_forward = 1`

Make it persistent. **Corrected from the previous version of this lab:** append to a file in `/etc/sysctl.d/` rather than editing `/etc/sysctl.conf`, which is the current convention and keeps your change identifiable and removable.

```bash
echo 'net.ipv4.ip_forward = 1' | sudo tee /etc/sysctl.d/99-router.conf
sudo sysctl --system
sysctl net.ipv4.ip_forward
```

---
### Step 4: Gate Two, Let the Firewall Forward the Traffic

This step is new, and it is the reason most attempts at this lab stall.

`firewalld` filters packets passing **through** the host, not only packets addressed **to** it. Forwarding can be fully enabled in the kernel and every packet still silently dropped, which produces a ping that hangs with no error and no clue.

On **VM2**:

```bash
# What zone is the private interface in right now?
sudo firewall-cmd --get-active-zones

# For an isolated lab, put it in the trusted zone
sudo firewall-cmd --permanent --zone=trusted --change-interface=<private-iface>
sudo firewall-cmd --reload
sudo firewall-cmd --get-active-zones
```

> The `trusted` zone is correct for an isolated lab and wrong for anything else. In production you would write an explicit forwarding policy permitting only the flows you intend. What matters here is that you have now seen the two gates **as two gates**. A kernel willing to forward a packet may still not forward it.

---
### Step 5: Capture the Routing Table Before

On **VM1**, before adding anything:

```bash
ip route show
```

You should see something like:

```
default via <your-gateway> dev <management-iface> proto dhcp metric 100
<your-management-subnet> dev <management-iface> proto kernel scope link
10.0.1.0/24 dev <private-iface> proto kernel scope link src 10.0.1.1
```

Notice what is missing. VM1 knows how to reach its management network and its own private subnet `10.0.1.0/24` automatically, because it holds an address directly on those networks. The kernel added those routes itself. There is **no entry at all** for `10.0.2.0/24`.

**Save this exact output. This is your before evidence, and it is a graded deliverable.**

Confirm the gap experimentally:

```bash
ping -c 2 10.0.1.254      # VM2's near side: succeeds, same subnet, no routing needed
ping -c 2 10.0.2.1        # Subnet B: fails
```

```
ping: connect: Network is unreachable
```

**Read that error rather than skimming it.** It is not a timeout and it is not a refusal. The kernel is telling you it has no route toward that network and therefore did not put a single packet on the wire. Nothing was dropped by anyone, because nothing was ever sent. That distinction is worth more in a real incident than most of what you will read this month.

Ask the kernel to confirm:

```bash
ip route get 10.0.2.1
```

---
### Step 6: Add the Static Route

On **VM1**:

```bash
sudo ip route add 10.0.2.0/24 via 10.0.1.254 dev <private-iface>
```

Read the command and understand each part. You are telling VM1: to reach anything in `10.0.2.0/24`, hand the packet to `10.0.1.254`, using `<private-iface>`. `10.0.1.254` is VM2's address in the subnet VM1 can already reach directly, which is what makes it a valid next hop. A next hop you cannot already reach is not a route, it is a wish.

---
### Step 7: Capture the Routing Table After, and Verify

On **VM1**:

```bash
ip route show
```

A new line appears:

```
10.0.2.0/24 via 10.0.1.254 dev <private-iface>
```

**Save this as your after evidence.** Compare it directly against Step 5. That single line is the entire difference, and it is the entire reason connectivity now works.

```bash
ping -c 4 10.0.2.1          # should now succeed
ip route get 10.0.2.1       # the kernel explains its own decision
```

```
10.0.2.1 via 10.0.1.254 dev <private-iface> src 10.0.1.1 uid 1000
```

**Confirm the path:**

```bash
traceroute -n 10.0.2.1
```

```
traceroute to 10.0.2.1 (10.0.2.1), 30 hops max, 60 byte packets
 1  10.0.1.254   0.5 ms  0.4 ms  0.4 ms
 2  10.0.2.1     0.8 ms  0.7 ms  0.7 ms
```

Hop one is VM2 acting as the router. Hop two is the destination. This is direct visual proof that traffic takes the path you configured rather than arriving by some other means.

**Optional, and worth thirty seconds:** watch the packets cross the router. On VM2, run `sudo tcpdump -n -i <private-iface> icmp` and ping again from VM1. Seeing your own packets arrive and be forwarded is the moment routing stops being abstract.

**If the ping fails**, work this checklist **in order**. It is ordered from most common cause to least, and each step rules out exactly one thing.

1. The route exists on VM1: `ip route show`, look for the Step 7 line
2. Forwarding is on at VM2: `sysctl net.ipv4.ip_forward` must return `1`
3. The firewall on VM2 is not dropping forwarded traffic: `sudo firewall-cmd --get-active-zones` and `sudo firewall-cmd --list-all`. To rule the firewall out entirely for a moment, `sudo systemctl stop firewalld`, test, then start it again and fix it properly rather than leaving it off
4. VM2 genuinely holds both addresses: `ip addr show <private-iface>` must list both `10.0.1.254/24` and `10.0.2.1/24`
5. Both private interfaces are on the same virtual network in the hypervisor

---
### Step 8: Make the Route Persistent

This step is new and it is required. Everything done with `ip` vanishes at reboot. That is correct behaviour, and it is an unpleasant surprise to anyone who assumed otherwise. In production, a critical route that silently disappears the next time a server restarts is an outage waiting for a maintenance window.

On **VM1**:

```bash
nmcli connection show
sudo nmcli connection modify "<connection-name>" +ipv4.routes "10.0.2.0/24 10.0.1.254"
sudo nmcli connection up "<connection-name>"
ip route show
```

Reboot VM1 and run `ip route show` again. If the route is still there, you configured the system. If it is not, you configured the running kernel, which is not the same thing.

> On RHEL 9, Rocky 9, and Fedora, NetworkManager stores this in a keyfile at `/etc/NetworkManager/system-connections/<name>.nmconnection`. The old `/etc/sysconfig/network-scripts/route-<iface>` file still appears in older documentation; that format is deprecated from RHEL 9 and **removed entirely in RHEL 10 and Rocky 10**. Use `nmcli`.

---
### Step 9 (Optional but Recommended): The Missing Return Route

The two VM topology above cannot produce one of the most common routing failures in the field, because VM2 is both the router and the destination, and it already holds a directly connected route back to Subnet A. Reflection Question 1 asks you to explain exactly that.

To see the failure the topology hides, add a third VM.

**VM3:** one interface on the same virtual network, address `10.0.2.50/24`, no routes configured beyond what the kernel adds automatically.

From VM1:

```bash
ping -c 3 10.0.2.50
```

It **hangs**, then times out. It does not say `Network is unreachable`, because this time VM1 had a route, sent the packet, and the packet arrived. VM3 received it, built a reply addressed to `10.0.1.1`, consulted its own routing table, found nothing for `10.0.1.0/24`, and dropped the reply on the floor. VM1 waits for an answer that was never sent.

A route is a one way instruction. Fix it on **VM3**:

```bash
sudo ip route add 10.0.1.0/24 via 10.0.2.1 dev <private-iface>
```

Ping again from VM1. It works.

Capture both, the hang and the recovery. This is the single most valuable thirty seconds in the lab, because no amount of investigation on VM1 alone would ever have revealed the cause.

---
### Reflection Questions

Answer in writing after completing the lab.

**Question 1.** In Step 6 you ran a single `ip route add` on VM1 and did not need a matching command on VM2 for the return traffic to work. Explain why VM2 needs no separate route back to VM1. Your answer must refer to what the kernel does automatically when an address is assigned to an interface.

**Question 2.** This lab used `ip route add`, which vanishes on reboot. Name the approach you used in Step 8 to make the route permanent on a RHEL family system, and explain at a high level how it differs from the temporary command. Where on disk does that configuration actually live?

**Question 3.** This two subnet, one router setup is a small scale version of exactly what an AWS VPC route table does between a public and a private subnet. What AWS component plays the role VM2 played, and what AWS component plays the role your `ip route add` command played?

**Question 4 (new).** You enabled `net.ipv4.ip_forward` and traffic still did not pass until you touched `firewalld`. Describe what each of those two gates does, and explain why a kernel that is willing to forward a packet may still not forward it.

**Question 5 (new, requires Step 9).** Compare the two failures you saw. In Step 5 the ping failed instantly with `Network is unreachable`. In Step 9 it hung silently. For each, say exactly how far the packet travelled and what that tells you about where to look first.

---
### Expected Output

- `ip addr show` from both VMs, confirming the configured addresses
- **`ip route show` from VM1, captured both before and after Step 6.** These two outputs are the core deliverable.
- The exact `ip route add` command you ran
- `ip route get 10.0.2.1` output
- Successful `ping -c 4 10.0.2.1` from VM1
- Successful `traceroute -n 10.0.2.1` from VM1, showing the two hop path
- `ip route show` from VM1 **after a reboot**, proving persistence
- If you did Step 9: the hanging ping, and the successful ping after adding the return route
- Written answers to all five reflection questions

---
### Common Issues

**`ip addr add` reports the address is already in use.** Check for a leftover address from an earlier attempt with `ip addr show <private-iface>` and remove it with `sudo ip addr del <old-address>/24 dev <private-iface>`.

**Ping still fails even after confirming the route exists.** This is almost always IP forwarding still disabled on VM2, or `firewalld` silently dropping forwarded traffic. Work the Step 7 checklist in the exact order given; it is ordered from most common to least.

**Ping hangs rather than failing immediately.** A hang means the packet was sent and something swallowed it: a firewall drop, or a missing return route. An immediate `Network is unreachable` means it was never sent at all. Do not treat these as the same symptom, because they point at opposite ends of the path.

**The two VMs cannot reach each other at all, even within the same subnet.** Confirm both private interfaces are attached to the same virtual network in the hypervisor. If they are on different virtual networks, no IP configuration will fix it, because the virtual wiring itself is wrong.

**Everything works, then stops after a reboot.** You configured with `ip` and skipped Step 8. Check with `nmcli connection show <name> | grep routes`.

---
### Cleanup

```bash
sudo ip route del 10.0.2.0/24                    # VM1
sudo sysctl -w net.ipv4.ip_forward=0             # VM2
sudo rm /etc/sysctl.d/99-router.conf             # VM2
sudo firewall-cmd --permanent --zone=public --change-interface=<private-iface>   # VM2
sudo firewall-cmd --reload                       # VM2
```

Or roll back to your snapshot, which is faster, and is why you took one.
