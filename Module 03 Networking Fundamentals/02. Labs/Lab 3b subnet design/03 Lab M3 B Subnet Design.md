# Lab 3B: Subnet Design

**Module 3: Networking Fundamentals**

> **Status: merged and updated.** Built from your existing Lab M2.B. The six step binary worked example, the five practice problems with their answer key, the three tier VPC design exercise, the three design questions, and the Common Mistakes section are all preserved. What changed: the VPC allocation is now `10.0.0.0/16` as the new syllabus specifies, rather than `10.20.0.0/16`; a block size shortcut is added alongside the binary method, because the binary method builds the model and the shortcut is what you will actually use in a design review; a route table exercise is added, since the syllabus now asks students to distinguish public from private subnets and that distinction lives in the route table, not in the address; and the lab now closes by pointing forward at Module 8, where the design gets built for real.

---
### Objective

Build real fluency with CIDR math by working a full subnet calculation by hand, then apply that fluency to design a realistic three tier VPC layout. By the end you should be able to look at a CIDR block and know its size without reaching for a calculator, and correctly design address ranges for VPCs, subnets, and firewall rules.

Every DevOps engineer who works with cloud infrastructure needs this. When you design a VPC you assign CIDR blocks to the VPC and to each subnet. Get the ranges wrong, through overlapping subnets, insufficient host capacity, or a miscalculated broadcast address, and the network will not route correctly.

---
### What You Need

- A calculator or spreadsheet, used only to check your work, never to do it for you
- No VM or terminal required, except optionally at the very end to verify

---
### Prerequisites

Read Module 3 section 3.10, NAT, Addressing, and CIDR in Practice.

---
### Part 1: Worked Example, the Full Binary Method

Work through `192.168.1.0/26` using the complete binary method. Do not skip steps, even the ones that feel obvious. The goal is to build the underlying mental model, not to memorize a formula.

**Step 1: Determine the subnet mask**

The prefix `/26` means 26 bits belong to the network portion. The remaining `32 - 26 = 6` bits belong to the host portion.

```
11111111 . 11111111 . 11111111 . 11000000
   255    .   255    .   255    .   192
```

Subnet mask: `255.255.255.192`

**Step 2: Determine the block size**

Block size equals 2 raised to the power of the host bits. `2^6 = 64`. Valid subnets of this size therefore start on multiples of 64: `.0`, `.64`, `.128`, `.192`.

**Step 3: Find the network address**

The first address in the block, with every host bit set to 0.

Network address: `192.168.1.0`

**Step 4: Find the broadcast address**

The last address in the block, with every host bit set to 1.

```
Last octet of the network address in binary: 00000000
Set all 6 host bits to 1:                    00111111  =  63
```

Broadcast address: `192.168.1.63`

**Step 5: Determine the usable host range**

```
First usable: 192.168.1.1   (network address plus 1)
Last usable:  192.168.1.62  (broadcast address minus 1)
```

**Step 6: Count usable hosts**

`2^6 - 2 = 62`. You subtract 2 because the network address and the broadcast address both exist within the range but neither can be assigned to an actual device.

**Final summary table:**

| Property | Value |
|---|---|
| Network | 192.168.1.0/26 |
| Prefix length | /26 |
| Subnet mask | 255.255.255.192 |
| Network address | 192.168.1.0 |
| Broadcast address | 192.168.1.63 |
| First usable host | 192.168.1.1 |
| Last usable host | 192.168.1.62 |
| Usable hosts | 62 |

---
### Part 1b: The Same Answer in Ten Seconds

The binary method above builds the model. This is what you will actually use once the model is built, and it is worth learning properly because a design review does not wait while you draw out octets.

1. **Block size** = 256 minus the interesting octet of the mask. For /26: `256 - 192 = 64`.
2. **Network address** = round the given address **down** to the nearest multiple of the block size.
3. **Broadcast address** = the next multiple, **minus one**.

Everything else follows: usable range is network plus one to broadcast minus one, and the host count is 2 to the power of the host bits, minus two.

Try it on `192.168.1.130/26`. Block size 64. The multiples are 0, 64, 128, 192, and 130 falls in the block starting at 128. Network `192.168.1.128`, broadcast `192.168.1.191`, usable `.129` to `.190`, 62 hosts. No binary, no calculator.

Verify with a tool, but only after you have committed to an answer on paper:

```bash
sudo dnf install -y ipcalc
ipcalc 192.168.1.130/26
```

---
### Part 2: Practice Problems

Solve each using the six step method from Part 1, then check the shortcut gives the same answer. Show your full working. Do not skip to the answer key.

| # | Network | Find |
|---|---|---|
| 1 | 10.0.0.0/24 | Subnet mask, network address, broadcast address, usable host range, host count |
| 2 | 172.16.0.0/20 | Subnet mask, network address, broadcast address, usable host range, host count |
| 3 | 10.0.1.0/28 | Subnet mask, network address, broadcast address, usable host range, host count |
| 4 | 192.168.10.64/26 | Subnet mask, network address, broadcast address, usable host range, host count |
| 5 | 10.0.0.0/16 | How many separate /24 subnets fit inside this one network |
| 6 | 192.168.10.19/30 | Subnet mask, network address, broadcast address, usable host range, host count |

**Answer key. Check only after attempting each problem.**

| # | Subnet Mask | Network | Broadcast | Host Range | Host Count |
|---|---|---|---|---|---|
| 1 | 255.255.255.0 | 10.0.0.0 | 10.0.0.255 | 10.0.0.1 to 10.0.0.254 | 254 |
| 2 | 255.255.240.0 | 172.16.0.0 | 172.16.15.255 | 172.16.0.1 to 172.16.15.254 | 4094 |
| 3 | 255.255.255.240 | 10.0.1.0 | 10.0.1.15 | 10.0.1.1 to 10.0.1.14 | 14 |
| 4 | 255.255.255.192 | 192.168.10.64 | 192.168.10.127 | 192.168.10.65 to 192.168.10.126 | 62 |
| 5 | N/A | N/A | N/A | 256 separate /24 subnets fit inside one /16 | N/A |
| 6 | 255.255.255.252 | 192.168.10.16 | 192.168.10.19 | 192.168.10.17 to 192.168.10.18 | 2 |

> Problem 6 is new, and it is worth a moment. A `/30` gives exactly two usable addresses out of four, which is precisely enough for a point to point link between two routers and nothing else. That is what it exists for, and you will meet it again the first time you configure a VPN tunnel. Note also that `.19` is the **broadcast** address here, not a host address, which is the kind of off by one that quietly breaks a real configuration.

---
### Part 3: Design a Three Tier VPC

Apply what you have practiced to a realistic design problem.

**The scenario.** You are designing the network layout for a small production application with three tiers: a web tier, an application tier, and a database tier. You have been allocated `10.0.0.0/16` for this entire VPC.

**Requirements:**

1. The web tier must be reachable from the public internet and needs room for up to 50 hosts as the application grows
2. The application tier must never be directly reachable from the public internet, and needs room for up to 100 hosts
3. The database tier must never be directly reachable from the public internet, requires the strongest isolation of the three, and needs room for fewer than 10 hosts
4. You must design for two availability zones, meaning every tier needs a subnet in each zone

**Task: complete the layout.**

| Subnet Name | CIDR Block | Tier | Availability Zone | Public or Private | Usable Hosts (AWS) |
|---|---|---|---|---|---|
| | | Web | AZ-A | | |
| | | Web | AZ-B | | |
| | | App | AZ-A | | |
| | | App | AZ-B | | |
| | | Database | AZ-A | | |
| | | Database | AZ-B | | |

Choose CIDR blocks that comfortably meet each tier's stated host requirement without wasting excessive address space, and show the host count math for each.

> **AWS reserves five addresses in every subnet:** the network address, the broadcast address, and three more for the VPC router, DNS, and future use. A `/24` gives **251** usable addresses in AWS, not 254. A `/28`, the smallest AWS permits, gives 11. Size the database tier with that in mind before you reach for the smallest block that technically fits.

---
### Part 3b: Now Draw the Route Tables

This part is new, and it is the part that turns an address plan into a design. An address plan without route tables is decoration.

**The rule that carries the whole thing:** a subnet is **public** if and only if its route table has a route to an **internet gateway**. A subnet is **private** if that route points at a **NAT gateway** instead, or does not exist at all. Everything else about the two, the names, the tags, the colours on the diagram, is convention. That one line is the fact.

Complete this:

| Route table | Attached to | Destination | Target |
|---|---|---|---|
| `rt-public` | Web subnets, both AZs | 10.0.0.0/16 | local |
| | | 0.0.0.0/0 | |
| `rt-private-app` | App subnets, both AZs | 10.0.0.0/16 | local |
| | | 0.0.0.0/0 | |
| `rt-private-db` | Database subnets, both AZs | 10.0.0.0/16 | local |
| | | 0.0.0.0/0 | |

The `local` route for the VPC CIDR is created automatically and cannot be removed. It is why every subnet in a VPC can reach every other subnet by default, and it has an important consequence you will answer for below.

---
### Design Questions

Answer in writing.

1. Why does the database tier need its own separate subnet rather than simply sharing the application tier's subnet with stricter security group rules layered on top?

2. Your `/16` provides roughly 65,000 addresses. Add up what your six subnets actually consume. What does the large remaining gap tell you about how real organizations plan VPC address space, and why is that intentional rather than wasteful?

3. If the company later adds a fourth tier, a caching layer for example, does your current design accommodate it without redesigning any existing subnet? Explain why or why not. If it does not, renumber your design so that it does, and explain what you changed.

4. **New.** The database subnet has no route to an internet gateway. How does it install security patches? Name the component, say which subnet it lives in, and explain in one sentence why traffic can go out through it but cannot come back in through it uninvited.

5. **New.** Every subnet in your VPC can reach every other subnet through the automatic `local` route. Given that, what is actually stopping the internet from reaching your database, and what is *not* stopping it?

6. **New.** Name the CIDR you would allocate to a second VPC in a different region, and explain in one sentence why it must not overlap this one.

---
### Expected Output

- Part 1: the complete worked example reproduced in your own notes
- Part 1b: the shortcut applied to `192.168.1.130/26`, arrived at without binary
- Part 2: all six practice problems solved with full working shown, not just final answers
- Part 3: the completed six subnet design table with host count math
- Part 3b: the completed route table, with a target named for every `0.0.0.0/0` row
- Written answers to all six design questions

---
### Common Mistakes

**Choosing a subnet size by guessing instead of calculating.** Always calculate the usable host count for a candidate block before committing to it. A `/27` looks similar to a `/26` at a glance and holds half as many usable addresses.

**Forgetting AWS reserves five addresses per subnet.** A `/24` gives 251 usable addresses in AWS, not 254. This rarely changes an overall design decision, but it matters the moment you size something close to its limit.

**Designing only for today's host count with zero room to grow.** A subnet sized exactly to current need leaves no room for autoscaling. Sizing generously up front, within reason, is far cheaper than a redesign later, once real resources already depend on the range.

**Numbering the subnets consecutively.** `10.0.1.0/24`, `10.0.2.0/24`, `10.0.3.0/24` and so on leaves no gap for a new tier or a third availability zone, and a design that must be renumbered to grow will not be grown. Leave gaps deliberately. A gap of ten in the third octet costs nothing and buys you the next two years.

**Assuming a subnet is private because you called it private.** It is private because of its route table. Check the route table.

---
### Submission

Show your full working for the `192.168.1.0/26` example, all six Part 2 practice problems, the completed Part 3 subnet design table with host count math, the completed Part 3b route table, and written answers to all six design questions.

---

> **Keep this design.** In Module 8 you will build it for real in Terraform and compare what you planned against what you had to change. That comparison is the most useful thing you will get out of Module 8, and it only exists if you commit to a design now, before you know the answer.
