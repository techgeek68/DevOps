# Lab 3C: Two VMs on Different Subnets, Connected with Static Routes

**Module 3: Networking Fundamentals**
**Time:** 60 to 90 minutes
**Machines:** three VMs

---

> Snapshot all three VMs before you start. This lab changes kernel forwarding behaviour and firewall zones on the router, and a rollback is faster than a rescue.

---

## What This Lab Is Actually Teaching

Routing stops being a diagram the moment you have built one with your own hands. By the end you will have seen three things that no amount of reading conveys:

- A packet that is never sent, because the kernel has no route for it
- A packet that is sent, arrives, and whose reply has nowhere to go
- A router that is fully willing to forward and still drops everything, because the firewall is a second, separate gate

---

## Topology

```
    vm-a                       vm-r (router)                      vm-b
10.10.1.10/24  ---------  10.10.1.1/24  10.10.2.1/24  ---------  10.10.2.10/24
   net-1                     net-1          net-2                    net-2
```

| VM | Interfaces | Addresses |
|---|---|---|
| `vm-a` | NAT, plus one on internal network `net-1` | 10.10.1.10/24 |
| `vm-r` | NAT, plus one on `net-1` and one on `net-2` | 10.10.1.1/24 and 10.10.2.1/24 |
| `vm-b` | NAT, plus one on internal network `net-2` | 10.10.2.10/24 |

In VirtualBox, create two internal networks named `net-1` and `net-2`. Every VM keeps its existing NAT adapter for internet access. That adapter takes no part in this lab, and the only thing it demands from you is care in picking the right interface name.

Find the right interface on each VM before typing anything else:

```bash
ip -br link
```

The internal adapter is usually `enp0s8` on `vm-a` and `vm-b`, and `enp0s8` plus `enp0s9` on `vm-r`. Substitute your own names throughout.

---

## Step 1: Address the Interfaces

**vm-a:**

```bash
sudo ip addr add 10.10.1.10/24 dev enp0s8
sudo ip link set enp0s8 up
```

**vm-b:**

```bash
sudo ip addr add 10.10.2.10/24 dev enp0s8
sudo ip link set enp0s8 up
```

**vm-r**, both interfaces:

```bash
sudo ip addr add 10.10.1.1/24 dev enp0s8
sudo ip addr add 10.10.2.1/24 dev enp0s9
sudo ip link set enp0s8 up
sudo ip link set enp0s9 up
ip -br addr show
```

---

## Step 2: `ip route` Before. Capture This.

On **vm-a**:

```bash
ip route show
```

```
10.10.1.0/24 dev enp0s8 proto kernel scope link src 10.10.1.10
```

One route, and the kernel added it by itself the moment you assigned the address. There is no entry for 10.10.2.0/24 anywhere. The consequence is immediate:

```bash
ping -c 2 10.10.1.1        # the router's near side: succeeds, same subnet, no routing needed
ping -c 2 10.10.2.10       # vm-b: fails
```

```
ping: connect: Network is unreachable
```

Read that error. It is not a timeout and it is not a refusal. The kernel is telling you it has no route toward that network and therefore **did not put a single packet on the wire**. Nothing was dropped by anyone, because nothing was ever sent.

Run the same three commands on **vm-b** and capture those too. Both sets of "before" output are part of the deliverable.

---

## Step 3: Turn vm-r Into a Router

A Linux host with two interfaces does not forward between them by default. Two separate gates must both open, and understanding that they are two is the real content of this lab.

### Gate one: the kernel must be willing to forward

```bash
# 0 means forwarding is off
cat /proc/sys/net/ipv4/ip_forward

# turn it on now
sudo sysctl -w net.ipv4.ip_forward=1

# and make it survive a reboot
echo 'net.ipv4.ip_forward = 1' | sudo tee /etc/sysctl.d/99-router.conf
sudo sysctl --system
sysctl net.ipv4.ip_forward
```

### Gate two: the firewall must permit forwarded traffic

This is the step that catches everybody, including people who have done it before. `firewalld` filters packets passing **through** the host, not only packets addressed **to** it. Forwarding can be fully enabled in the kernel and every packet still silently dropped.

For an isolated lab, place both internal interfaces in the trusted zone:

```bash
sudo firewall-cmd --permanent --zone=trusted --change-interface=enp0s8
sudo firewall-cmd --permanent --zone=trusted --change-interface=enp0s9
sudo firewall-cmd --reload
sudo firewall-cmd --get-active-zones
```

> The `trusted` zone is correct for an isolated lab and wrong for anything else. In production you would write an explicit policy permitting only the flows you intend and nothing more. What matters here is that you have now seen the two gates as two gates. A kernel willing to forward a packet may still not forward it.

Before moving on, prove the router can reach both sides itself:

```bash
ping -c 2 10.10.1.10
ping -c 2 10.10.2.10
```

Both must succeed. If either fails, fix that first, because a static route pointing at a router that cannot reach the destination is a route pointing at nothing.

---

## Step 4: Add the Static Routes

`vm-r` knows both networks because it has an interface on each. `vm-a` and `vm-b` do not. Tell them.

**vm-a:**

```bash
sudo ip route add 10.10.2.0/24 via 10.10.1.1 dev enp0s8
```

**vm-b:**

```bash
sudo ip route add 10.10.1.0/24 via 10.10.2.1 dev enp0s8
```

---

### Do This Deliberately: Break It First

Before adding the second route, ping from `vm-a` with only the first one in place.

```bash
# on vm-a only, with vm-b still having no return route
ping -c 3 10.10.2.10
```

It hangs, then times out. It does **not** say `Network is unreachable`, because this time `vm-a` had a route, sent the packet, and the packet arrived. `vm-b` received it, generated a reply, consulted its own routing table, found nothing for 10.10.1.0/24, and dropped the reply on the floor. `vm-a` waits for an answer that was never sent.

A route is a one way instruction. This is the most important thirty seconds in the lab, because no amount of investigation on `vm-a` alone would ever reveal the cause. Now add the return route on `vm-b` and watch it recover.

---

## Step 5: `ip route` After. Capture This Too.

On **vm-a**:

```bash
ip route show
```

```
10.10.1.0/24 dev enp0s8 proto kernel scope link src 10.10.1.10
10.10.2.0/24 via 10.10.1.1 dev enp0s8
```

The second line is entirely your work. Now prove it end to end:

```bash
ping -c 3 10.10.2.10
traceroute -n 10.10.2.10
```

The traceroute shows two hops, 10.10.1.1 then 10.10.2.10. Seeing the router in the path is the visible proof that the packet is being routed rather than handed to a neighbour on the local link.

Then ask the kernel to explain its own decision, which is always faster than reasoning about it yourself:

```bash
ip route get 10.10.2.10
```

```
10.10.2.10 via 10.10.1.1 dev enp0s8 src 10.10.1.10 uid 1000
```

**Watch the traffic cross the router.** On `vm-r`:

```bash
sudo tcpdump -n -i enp0s9 icmp
```

and ping from `vm-a` again. Seeing your own packets arrive on one interface and leave by the other is the moment routing stops being abstract.

---

## Step 6: Make It Persistent

Everything you did with `ip` is gone at reboot. That is correct behaviour, and it is an unpleasant surprise to anyone who assumed otherwise.

Persist the route through NetworkManager on **vm-a**:

```bash
nmcli connection show
sudo nmcli connection modify "<connection-name>" +ipv4.routes "10.10.2.0/24 10.10.1.1"
sudo nmcli connection up "<connection-name>"
ip route show
```

Do the same on `vm-b` with the mirrored route. Then reboot both VMs and run `ip route show` again.

If the routes are still there, you have done this properly. If they are not, you configured the running system and not the system.

---

## Deliverables

1. `ip route show` from `vm-a` and `vm-b`, before and after. Four outputs.
2. The failing `ping` from Step 2, with its exact error text, and the succeeding `ping` from Step 5.
3. The hanging `ping` from the deliberate one way route in Step 4, with a note on how its symptom differed from Step 2.
4. `traceroute -n 10.10.2.10` showing the router as an intermediate hop.
5. `ip route get 10.10.2.10` output.
6. `ip route show` after a reboot, proving persistence.
7. In prose, four questions:
   - You enabled `net.ipv4.ip_forward` and traffic still did not pass until you touched `firewalld`. Describe what each gate does and why both must open.
   - With only one route in place, the ping hung rather than failing immediately. Explain precisely where the packets went and why the symptom changed.
   - Compare `Network is unreachable` with a silent hang. What does each tell you about how far the packet travelled?
   - In a cloud VPC you never run any of these commands. What does AWS replace them with, and which part of this lab does a route table object correspond to?

---

## Troubleshooting

| Symptom | Likely cause | Check |
|---|---|---|
| `Network is unreachable` after adding the route | Route added on the wrong interface, or the interface is down | `ip -br link`, `ip route show` |
| Ping hangs with no reply | Missing return route on the far host, or `firewalld` dropping forwarded traffic on `vm-r` | `ip route show` on the far host; `firewall-cmd --get-active-zones` on `vm-r` |
| Router can ping both hosts, hosts cannot reach each other | `ip_forward` is 0 | `sysctl net.ipv4.ip_forward` |
| Everything works, then stops after reboot | Configured with `ip` rather than `nmcli`, so nothing was persisted | `nmcli connection show <name> \| grep routes` |
| `Destination host unreachable` from the router itself | ARP failing; the two VMs are not actually on the same virtual network | Compare the internal network names in the hypervisor settings |
| Traceroute shows no router hop, but ping works | You are pinging the wrong address, or both VMs ended up on the same subnet | `ip -br addr show` on both |

---

## Cleanup

```bash
sudo ip route del 10.10.2.0/24          # vm-a
sudo ip route del 10.10.1.0/24          # vm-b
sudo sysctl -w net.ipv4.ip_forward=0    # vm-r
sudo rm /etc/sysctl.d/99-router.conf    # vm-r
```

---

## Assessment

You pass when the before and after `ip route` output is captured from both hosts, the traceroute shows the router hop, the routes survive a reboot, and the write up explains why kernel forwarding and firewall policy are two separate gates that must both open.

The idea to carry forward: everything you did by hand here is what a cloud route table does for you, and what a Kubernetes CNI plugin does for pods. When either of those misbehaves, you will already know what layer of the problem you are looking at.
