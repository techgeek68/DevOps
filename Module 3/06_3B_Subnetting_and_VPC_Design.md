# Lab 3B: Subnetting and a Three Tier VPC Design

**Module 3: Networking Fundamentals**
**Time:** 45 minutes
**Equipment:** paper and a pen. No VM, no cloud account, no terminal until the very end.

---

> Do the arithmetic by hand first, then verify with a tool. Reversing that order teaches you nothing, because a calculator that hands you the answer never shows you where the boundary is. The whole value of this lab is that you will be able to do it in your head during a design review, while someone is waiting for you to answer.

---

## Part 1: Given 192.168.1.0/26

Calculate, showing your working:

1. The subnet mask in dotted decimal
2. The network address
3. The broadcast address
4. The usable host range
5. The number of usable hosts

---

### The Method

A /26 has 26 network bits and 6 host bits. Write the mask out once, in binary, and you will not need to again.

```
11111111.11111111.11111111.11000000
   255       255       255      192
```

**Block size** is `256 minus the last non zero octet of the mask`, so `256 - 192 = 64`. Subnets of this size therefore begin at multiples of 64 in the final octet: .0, .64, .128, .192. The block beginning at .0 ends one below the next block, at .63.

| Item | Value |
|---|---|
| Subnet mask | 255.255.255.192 |
| Network address | 192.168.1.0 |
| Broadcast address | 192.168.1.63 |
| Usable host range | 192.168.1.1 to 192.168.1.62 |
| Usable hosts | 2^6 minus 2 = 62 |

Two addresses are subtracted in every subnet: the network address, which names the subnet, and the broadcast address, which addresses every host in it at once. Neither can be assigned to a machine.

---

### The Shortcut, Stated Plainly

Given any address and any prefix, three steps:

1. **Block size** = 256 minus the interesting octet of the mask
2. **Network address** = round the address down to the nearest multiple of the block size
3. **Broadcast address** = the next multiple, minus one

Everything else follows. The usable range is network plus one to broadcast minus one, and the host count is 2 to the power of the host bits, minus two.

Worked on a second example, `192.168.1.130/26`: block size 64, and 130 falls in the block starting at 128. Network 192.168.1.128, broadcast 192.168.1.191, usable .129 to .190, 62 hosts. No binary required.

---

### Practice, Without Looking Back

Work each to the same five answers. Target: under thirty seconds each.

| Given | Mask | Network | Broadcast | Usable range | Hosts |
|---|---|---|---|---|---|
| 192.168.1.130/26 | | | | | |
| 10.0.5.200/27 | | | | | |
| 172.16.4.77/28 | | | | | |
| 192.168.10.19/30 | | | | | |
| 10.20.30.40/25 | | | | | |

Only once you have committed an answer to paper, verify it:

```bash
sudo dnf install -y ipcalc
ipcalc 192.168.1.130/26
```

> `/30` is worth noticing. Two usable addresses out of four, which is exactly enough for a point to point link between two routers and nothing else. That is what it exists for, and you will see it again the first time you configure a VPN tunnel.

---
---

## Part 2: Design a Three Subnet VPC Layout in 10.0.0.0/16

You are handed `10.0.0.0/16`, which is 65,536 addresses. That is far more than you need, and that is deliberate.

The goal is not to use it all. The goal is to divide it so the tiers are separable, the boundaries are obvious to a human reading a route table at two in the morning, and there is room left for the thing nobody has thought of yet.

### Requirements

- A public web tier, reachable from the internet
- A private application tier, reachable only from the web tier
- A private database tier, reachable only from the application tier
- Room to add a fourth tier later without renumbering anything that already exists

---

### The Minimal Answer: Three Subnets

| Tier | CIDR | Mask | Usable (standard) | Usable (AWS) | Route for 0.0.0.0/0 points to |
|---|---|---|---|---|---|
| Public web | 10.0.1.0/24 | 255.255.255.0 | 254 | 251 | Internet gateway |
| App | 10.0.2.0/24 | 255.255.255.0 | 254 | 251 | NAT gateway |
| Database | 10.0.3.0/24 | 255.255.255.0 | 254 | 251 | NAT gateway, or nothing at all |

Read the last column carefully, because it carries the entire design.

**A subnet is public if and only if its route table has a route to an internet gateway.** A subnet is private if that route points at a NAT gateway instead, or does not exist. Everything else about the two, the names, the tags, the colours on the architecture diagram, is convention. That one line is the fact.

**Why 251 and not 254 in AWS.** AWS reserves five addresses in every subnet: the network address, the broadcast address, and three more for the VPC router, DNS, and future use. A /24 gives 251. A /28, the smallest AWS permits, gives 11, which an autoscaling group and a load balancer will exhaust faster than you expect.

---

### The Answer You Would Actually Deploy

A subnet lives in exactly one availability zone. A design with one subnet per tier therefore cannot survive the loss of one zone, which makes the table above a teaching example rather than an architecture. Real designs place every tier in at least two zones.

| Tier | AZ a | AZ b |
|---|---|---|
| Public web | 10.0.0.0/24 | 10.0.1.0/24 |
| App | 10.0.10.0/24 | 10.0.11.0/24 |
| Database | 10.0.20.0/24 | 10.0.21.0/24 |

Notice what the numbering buys you. Tiers are separated by a gap of ten in the third octet, so a fourth tier slots in at 10.0.30.0/24 and 10.0.31.0/24, and a third availability zone slots in at 10.0.2.0/24, 10.0.12.0/24, and 10.0.22.0/24, without a single existing subnet moving.

Anyone reading `10.0.21.0/24` in a route table can say immediately: database tier, second zone. Address plans are read far more often than they are written, and this is what that principle looks like on paper.

Six /24 subnets consumed out of the 256 available in a /16. Roughly 98 percent of the range is untouched. That is not waste. That is the design working.

---

### Draw the Route Tables

An address plan without route tables is decoration. Complete these.

| Route table | Attached to | Destination | Target |
|---|---|---|---|
| `rt-public` | Public web subnets | 10.0.0.0/16 | local |
| | | 0.0.0.0/0 | |
| `rt-private-app` | App subnets | 10.0.0.0/16 | local |
| | | 0.0.0.0/0 | |
| `rt-private-db` | Database subnets | 10.0.0.0/16 | local |
| | | 0.0.0.0/0 | |

The `local` route for the VPC CIDR is created automatically and cannot be removed. It is why every subnet in a VPC can reach every other subnet by default, and it is why security groups, not subnet boundaries, are what actually keep your database private.

---

## Deliverables

1. The completed table for Part 1, with binary working shown, plus all five practice rows
2. Your VPC address table, and the completed route table above
3. Three sentences explaining why the database tier has no route to an internet gateway, and how it installs security patches anyway
4. One sentence naming the CIDR you would allocate to a second VPC in another region, and why it must not overlap this one
5. One sentence on what breaks if you size the database subnet as a /28 instead of a /24
6. One sentence answering this: if every subnet in a VPC can reach every other subnet through the `local` route, what is actually stopping the internet from reaching your database?

---

## Assessment

You pass when the /26 arithmetic is correct with working shown, the VPC design names the route table target for every subnet, and the plan leaves room to grow in both dimensions, a new tier and a new availability zone, without renumbering.

---

> **Keep this page.** In Module 8 you will build this design in Terraform and compare what you planned against what you had to change. The gap between the two is the most useful thing you will learn in that module, and it only exists if you commit to a design now, before you know the answer.
