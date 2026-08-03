# Module 3: Networking Fundamentals

---
> **Prerequisites:** This module assumes you have completed the Foundation Module and Module 2. You already know what an IP address is, the difference between public and private addressing, what a subnet is conceptually, how DNS resolution works as a lookup chain, what a firewall does as a gatekeeper, and why a single server is never enough. This module builds on that with the engineering depth you need to actually configure, diagnose, and operate networked systems, and it ends with three labs you must complete before Module 4.
---

## What You Will Learn

- The OSI layers a delivery engineer actually touches, and the habit of diagnosing bottom to top
- How TCP/IP maps onto OSI, and why the mapping is loose
- TCP versus UDP, the three way handshake, ports, sockets, and the service ports you should know by memory
- Connection states, and what port exhaustion looks like from the outside when it bites you
- Routing tables, default gateways, static routes, and a conceptual look at dynamic routing
- DNS record types, TTL management around a cutover, and split horizon DNS
- Load balancing at L4 and L7, the four algorithms that matter, sticky sessions, and health checks
- Firewalls and security groups, stateful versus stateless, default deny, firewalld zones, AWS security groups, NACLs, and iptables
- DHCP, and why address assignment still matters for containers and cloud instances
- TLS and HTTPS, the handshake, certificates, chains, SNI, and a correct Nginx TLS block
- NAT, CIDR, subnetting math, NAT gateways, and the special address ranges you will see every week
- The mistakes that actually happen in production, and how to avoid making them

---

# Part 1: Theory

---

## 3.1 The OSI Model

You do not need to memorize all seven OSI layers as an academic exercise. What you need is a diagnostic habit: when something is broken, knowing which layer to check first saves you hours of guessing. In real DevOps work, almost everything you touch lives in layers 3 through 7.

### The Layers That Matter: Purpose, Common Issues, and Troubleshooting

| Layer | Name             | What It Does                                                                                   | Common Protocols / Examples                          | Common Symptoms / What Breaks Here                                                                                      | How You Check It                                                                        |
| :---: | ---------------- | ---------------------------------------------------------------------------------------------- | ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| **7** | **Application**  | Provides network services and protocols that applications use to communicate over the network. | HTTP, HTTPS, SSH, DNS, FTP, SMTP                     | The application returns an error, times out, or behaves incorrectly.                                                    | `curl -v`, browser developer tools, application logs                                    |
| **6** | **Presentation** | Translates data formats, handles encryption and decryption, and performs compression.          | TLS/SSL, UTF-8, JSON/XML serialization, gzip         | TLS handshake fails, or the certificate is invalid or expired.                                                          | `openssl s_client`, `curl -vI`                                                          |
| **5** | **Session**      | Establishes, manages, and terminates communication sessions between applications.              | NetBIOS, RPC                                         | Session establishment or persistence issues. Rare to diagnose directly in modern TCP/IP networks.                       | Usually folded into application or transport troubleshooting.                           |
| **4** | **Transport**    | Provides end to end communication, reliability, error checking, and flow control.              | TCP, UDP                                             | Port is closed, connection is refused, or the connection hangs.                                                         | `ss -tlnp`, `telnet <host> <port>`, `nc -zv <host> <port>`                              |
| **3** | **Network**      | Provides logical addressing and routes packets between networks.                               | IP, ICMP, OSPF, BGP                                  | Host is unreachable, routing is incorrect, or packets cannot reach the destination.                                     | `ping`, `traceroute`, `ip route`                                                        |
| **2** | **Data Link**    | Provides physical addressing and reliable communication over a single network segment.         | Ethernet, MAC addresses, ARP, VLANs                  | Frames are dropped, ARP resolution fails, VLANs are misconfigured, MAC learning issues occur, or the interface is down. | `ip link`, `ip neigh`, `bridge`, `tcpdump`, switch MAC/VLAN tables                      |
| **1** | **Physical**     | Transmits raw bits over the physical transmission medium.                                      | Cat6 cables, fiber optic cables, Wi-Fi radio signals | Cable or transceiver failure, no physical link, weak wireless signal, speed or duplex mismatch, or hardware failure.    | `ethtool`, `ip link`, NIC LEDs, cable tester, Wi-Fi signal strength, switch port status |

---
> Layers 1 and 2 (physical cables, Ethernet, MAC addresses) exist, but as a DevOps engineer working in cloud and virtualized environments, you seldom diagnose a problem at that level. The cloud provider or the hypervisor handles it.
> 
> You will see Layer 2 concepts again when working with Docker bridge networks and Kubernetes CNI plugins, but for now, your working range is L3 to L7.

---
### The Diagnostic Habit This Builds

When a deployment "is not working," that sentence carries no useful information. The skill is converting it into a layer by layer test, from the bottom of your working range upward.

```
Can I reach the host at all?                              > Layer 3 (ping, traceroute)
```
```
Is the port open and something listening to it?           > Layer 4 (ss, nc, telnet)
```
```
Does the TLS handshake complete?                          > Layer 6 (openssl s_client)
```
```
Does the application respond correctly?                   > Layer 7 (curl, browser)
```

Each step rules out an entire category of failure. If Layer 3 fails, there is no point in debugging your application code. If Layers 3 and 4 both succeed but Layer 7 returns a 500 error, you know the network is fine, and the problem is in the application itself. This single habit, working the stack from bottom to top, is the single most useful network debugging skill you will carry through this entire course.

---
### How This Looks in a Real Incident

A team deploys a new version of their API. Five minutes later, alerts fire: the health check is failing. An engineer who does not have the OSI habit starts reading application logs immediately, burning fifteen minutes scrolling through irrelevant stack traces. An engineer with the habit runs `curl -v https://api.internal/health` first. The connection fails at the TCP level: connection refused. That immediately tells them the application process is not even listening on the expected port, which is a deployment or configuration problem, not a code bug. They check the pod logs and find the container crashed on startup due to a missing environment variable. Total diagnosis time: two minutes, because the OSI layer check ruled out everything except "the process is not running."

---
### Naming the Failure by Its Symptom

Three Layer 3 and Layer 4 symptoms are easy to confuse, and telling them apart cuts your search space immediately.

| Symptom | What You See | What It Almost Always Means |
|---|---|---|
| Connection refused | The connection fails instantly | You reached the host, the port is open to you, but no process is listening on it. A Layer 4 answer, delivered fast. Application or service problem, not a network one. |
| Connection timed out | The connection hangs, then fails after several seconds | A firewall, security group, or NACL is dropping the packet silently, or the route does not exist. Nothing answered at all. |
| No route to host | Fails immediately with an explicit routing error | Your own kernel has no route toward that destination. Check `ip route` before anything else. |

A fast rejection means something answered you. A hang means something swallowed the packet. That single distinction is worth more in an incident than any amount of log reading.

---
## 3.2 TCP/IP

---

### The TCP/IP Stack

TCP/IP is the protocol suite that runs the Internet and most modern networks. Unlike OSI, it is an implementation. It has four layers that map roughly onto the seven OSI layers:

| TCP/IP Layer   | Equivalent OSI Layers | Key Protocols                      |
|----------------|-----------------------|------------------------------------|
| Application    | 5, 6, 7               | HTTP, HTTPS, SSH, DNS, SMTP, FTP   |
| Transport      | 4                     | TCP, UDP                           |
| Internet       | 3                     | IP (IPv4, IPv6), ICMP              |
| Network Access | 1, 2                  | Ethernet, ARP, Wi-Fi               |

The mapping is deliberately loose. OSI was designed as a reference model before the protocols existed; TCP/IP was built from working code and later described. When someone says "that is a Layer 7 problem," they are speaking OSI. When they configure a system, they are running TCP/IP. Both statements are normal and neither is wrong.

---
### TCP vs. UDP

These are the two protocols at the Transport layer. Understanding the difference is essential for reading firewall rules, diagnosing connection failures, and configuring services.

| Feature     | TCP (Transmission Control Protocol)               | UDP (User Datagram Protocol)                         |
|-------------|---------------------------------------------------|------------------------------------------------------|
| Connection  | Connection oriented (three way handshake)         | Connectionless                                       |
| Reliability | Guaranteed delivery, retransmission on loss       | No guarantee; packets may be lost or arrive out of order |
| Order       | Packets arrive in sequence                        | No ordering guarantee                                |
| Speed       | Slower due to overhead                            | Faster; minimal overhead                             |
| Use cases   | HTTP/HTTPS, SSH, database connections             | DNS queries, video streaming, VoIP, metrics over UDP |


> The TCP three way handshake: `SYN > SYN-ACK > ACK`. This is what happens every time your browser connects to a web server or your Jenkins agent connects to the controller. When a connection hangs, checking whether the handshake completes is the first diagnostic step.

**Reading the handshake for yourself.** Run a capture on one terminal and a connection on another. The three packets are visible in order, and once you have seen them you never forget them.

```bash
# Terminal 1: capture only handshake packets to a host
sudo tcpdump -n -i any 'tcp port 443 and host example.com'

# Terminal 2: open a connection
curl -sI https://example.com > /dev/null
```

You will see `Flags [S]`, then `Flags [S.]` (SYN plus ACK), then `Flags [.]` (the final ACK). If you only ever see repeated `[S]` packets with no reply, the SYN is being dropped by a firewall or is going somewhere with no route back. That is a Layer 3 or Layer 4 finding, and it saves you from reading application logs.

**Why UDP is not simply worse.** UDP has no handshake, no retransmission, and no ordering, which sounds like a list of missing features until you consider what those features cost. A DNS query and its answer fit in a single packet each; a handshake would triple the number of round trips for no benefit, and if the answer is lost the client simply asks again. QUIC, which carries HTTP/3, is built on UDP for exactly this reason: it moves reliability into user space where it can be improved without waiting for every operating system kernel on earth to be upgraded.

---
### Ports and Sockets

A port is a number that identifies a specific service running on a host. An IP address gets you to the right machine. A port gets you to the right service on that machine. A socket is the combination of an IP address, a port, and a protocol (TCP or UDP), uniquely identifying one end of a network connection.

This matters because a single server can run many services simultaneously, each bound to a different port. Your web server might be on port 443, your database on 5432, and your monitoring agent on 9100, all on the same machine, all reachable independently.

A TCP connection is not identified by one socket but by four values taken together: source IP, source port, destination IP, destination port. This four tuple is why a web server can hold ten thousand simultaneous connections on a single listening port. Every connected client has a different source IP or source port, so every connection is distinct even though they all terminate on port 443.

**Ephemeral ports.** When your machine initiates an outbound connection, the kernel picks an unused source port for it automatically, from a range called the ephemeral port range. On Linux this range is configurable and defaults to ports 32768 through 60999, roughly 28,000 ports.

```bash
# Show the ephemeral port range on this host
cat /proc/sys/net/ipv4/ip_local_port_range
```

That number, roughly 28,000, is the ceiling on how many simultaneous outbound connections a host can make to a single destination IP and port pair. It is the number that turns into an outage when a busy service opens a fresh connection for every request instead of reusing a pool. That is the mechanism behind port exhaustion, covered below.

**Privileged ports.** Ports below 1024 are privileged: binding to them traditionally requires root. This is why containers running Nginx as a non root user usually listen on 8080 internally and are published to 80 externally, and why a service that works when you run it with `sudo` and fails without it is often a port binding problem rather than a network one.

---
### Common Protocols and Their Ports

| Protocol       | Port | Transport   | Purpose                                                      |
|----------------|------|-------------|--------------------------------------------------------------|
| HTTP           | 80   | TCP         | Unencrypted web traffic                                      |
| HTTPS          | 443  | TCP         | TLS encrypted web traffic (also UDP 443 for HTTP/3 over QUIC) |
| SSH            | 22   | TCP         | Encrypted remote shell access                                |
| FTP (data)     | 20   | TCP         | File transfer (data channel)                                 |
| FTP (control)  | 21   | TCP         | File transfer (control channel)                              |
| SMTP           | 25   | TCP         | Email relay between servers                                  |
| DNS            | 53   | TCP and UDP | Domain name resolution (UDP for queries; TCP for zone transfers and large responses) |
| DHCP           | 67, 68 | UDP       | Address assignment (67 server, 68 client)                    |
| NTP            | 123  | UDP         | Time synchronization                                         |
| HTTP alt       | 8080 | TCP         | Common alternative port for web apps and Jenkins             |
| HTTPS alt      | 8443 | TCP         | Common alternative port for HTTPS services                   |
| MySQL          | 3306 | TCP         | MySQL/MariaDB database                                       |
| PostgreSQL     | 5432 | TCP         | PostgreSQL database                                          |
| Redis          | 6379 | TCP         | Redis in-memory data store                                   |
| Kubernetes API | 6443 | TCP         | kube-apiserver, the port every kubectl command talks to      |
| etcd           | 2379, 2380 | TCP   | etcd client and peer traffic in a Kubernetes control plane   |
| Node Exporter  | 9100 | TCP         | Prometheus metrics endpoint on a Linux host                  |

Knowing these ports by memory is a practical skill. When you write a firewall rule to allow Jenkins traffic, you need to know it runs on port 8080 by default. When you debug a failed database connection, you check whether port 3306 is reachable. When a `kubectl` command hangs, 6443 is the first port you test.

---
### Connection States: What ESTABLISHED and TIME_WAIT Actually Mean

When you run `ss -tnp` or `netstat -tnp`, you will see a column listing the state of each TCP connection. Two states come up constantly in real operational work, and understanding them prevents a lot of confused troubleshooting.

**ESTABLISHED** means the TCP three way handshake has been completed and the connection is actively open. Data can flow in both directions. This is the normal, healthy state for an active connection.

**TIME_WAIT** is the state a connection enters after it has been closed, but the operating system holds onto it for a short period (typically 60 to 120 seconds, depending on the OS) before fully releasing it. This exists for a specific reason: it prevents a delayed, duplicate packet from an old, already closed connection from being misinterpreted as belonging to a brand new connection that happens to reuse the same port.

The state lifecycle for a typical connection looks like this. The side that closes the connection first goes through one path; the side that receives the close goes through a different one:

```
SYN_SENT      client initiates the handshake
SYN_RECEIVED  server received the SYN, sent its own SYN-ACK
ESTABLISHED   handshake complete, data flowing

-- the side that closes first --

FIN_WAIT_1    sent a FIN, waiting for it to be acknowledged
FIN_WAIT_2    FIN was acknowledged, waiting for the other side's FIN
TIME_WAIT     both FINs exchanged, waiting out the safety period
CLOSED        fully released

-- the side that receives the close --

CLOSE_WAIT    received a FIN, waiting for the local application to close its end
LAST_ACK      sent its own FIN, waiting for the final acknowledgment
CLOSED        fully released
```
---
> `CLOSE_WAIT` is worth remembering on its own: if you see connections piling up in `CLOSE_WAIT` and staying there, it almost always means the application received the signal to close but never actually called close() on the socket, a real and common application bug, not a network problem.
---

On Linux, the TIME_WAIT duration is fixed at 60 seconds and is compiled into the kernel, not exposed as a tunable. Engineers who go looking for a sysctl to shorten it do not find one, which is a deliberate decision, not an oversight.

### Why TIME_WAIT Causes Real Problems

A high volume server, particularly one that opens many short lived outbound connections (a load balancer, a service making thousands of API calls per second), can accumulate a large number of connections sitting in TIME_WAIT. Each one technically still holds the local port it was using. If enough connections pile up in TIME_WAIT, the server can run out of available local ports to open new outbound connections with, a condition often called port exhaustion.

```bash
# Count connections by state, a useful first check when diagnosing
# connection exhaustion or unusual connection counts
ss -tan | awk '{print $1}' | sort | uniq -c | sort -rn
```

If you see thousands of connections sitting in TIME_WAIT on a high traffic server, this is a real signal, not noise. The common fixes are tuning the kernel's TCP settings (`net.ipv4.tcp_tw_reuse`), reducing how often new connections are opened by using connection pooling and keep alive instead of opening a fresh connection per request, or adding more outbound IP addresses to spread the load across a larger pool of available ports.

**What port exhaustion looks like from the outside.** It rarely announces itself. The symptoms are a service that works perfectly at low traffic and starts failing under load, with CPU and memory both looking healthy, and application logs full of connection timeouts or "cannot assign requested address" errors pointing at a downstream service. That last message is the giveaway: the kernel is telling you it has no source port left to give. Confirm it by counting TIME_WAIT sockets and comparing the total against the size of the ephemeral range.

```bash
# Sockets in TIME_WAIT right now
ss -tan state time-wait | wc -l

# Compare against the size of the ephemeral range
cat /proc/sys/net/ipv4/ip_local_port_range
```

**On the two tunables you will read about.** `net.ipv4.tcp_tw_reuse` allows the kernel to reuse a TIME_WAIT socket for a new outbound connection when it is safe to do so, and it remains the correct knob to reach for. `net.ipv4.tcp_tw_recycle` appears in a great many older blog posts and Stack Overflow answers, and it should never be used: it broke badly for clients behind NAT and was removed from the Linux kernel in version 4.12. If you find it in a runbook or a Terraform sysctl block, that configuration predates 2017 and needs review.

Tuning is a stopgap in any case. The durable fix is architectural: use HTTP keep alive and a connection pool so the same connections are reused instead of being torn down and reopened thousands of times per second.

---
### How This Appears in Real Companies

A team running a Node.js API behind Nginx notices that under heavy load, new requests start timing out, even though CPU and memory on the server look completely fine. The actual cause: their application was opening a new outbound HTTP connection to a downstream payment API for every single incoming request instead of reusing connections through a connection pool. Under load, thousands of these short lived connections piled up in TIME_WAIT, and the server ran out of local ports to assign to new outbound connections. The fix was not more hardware. It was switching the HTTP client library to use a persistent connection pool, which eliminated the constant churn of opening and closing connections.

---
## 3.3 Routing

Routing is how a packet finds its way from source to destination across one or more networks.

A router makes forwarding decisions based on a routing table: a list of destination networks and the next hop to reach them. Each entry says: "to reach network X, send the packet to Y."

**Default gateway:**

The router a host sends packets to when it has no more specific route. Every server needs a default gateway configured, or it cannot reach anything outside its local subnet. On Linux: `ip route add default via <gateway-ip>`.

**Static route:**

A manually configured route for a specific destination. Used in lab environments and simple networks where dynamic routing protocols are not needed.

**Dynamic routing protocols:**

In large networks, routers exchange route information automatically. OSPF is common inside enterprise networks. BGP runs the internet. In DevOps work, you will mostly see static routing in lab environments and rely on cloud-managed routing in production.

---
### Reading a Routing Table

Every Linux host has a routing table, and reading it correctly is a skill you will use in nearly every network incident.

```bash
ip route show
```

```
default via 192.168.1.1 dev enp0s1 proto dhcp metric 100
10.10.2.0/24 via 192.168.1.254 dev enp0s1 proto static metric 100
192.168.1.0/24 dev enp0s1 proto kernel scope link src 192.168.1.50 metric 100
```

Three entries, three meanings.

The `192.168.1.0/24` line is a directly connected route. The kernel added it automatically the moment an address in that range was assigned to `enp0s1`. Anything in this range is reachable on the local link with no router involved: the host resolves the destination MAC with ARP and sends the frame directly.

The `10.10.2.0/24` line is a static route. To reach that network, hand the packet to 192.168.1.254, which is a router on the local link that knows how to get there. This is exactly what you will configure by hand in Lab 3C.

The `default` line is the catch all. Anything that matches no other entry goes to 192.168.1.1. `default` is simply another way of writing `0.0.0.0/0`, the route that matches every possible address.

**The longest prefix match rule.** When several routes could match a destination, the kernel always picks the one with the longest prefix, meaning the most specific one. A packet bound for 10.10.2.5 matches both `10.10.2.0/24` (24 bits of prefix) and `default` (0 bits), so the /24 wins. This rule alone explains most "why is my traffic going the wrong way" questions. The `metric` value only breaks ties between routes with the same prefix length; it does not override specificity.

Ask the kernel directly rather than reasoning about it in your head:

```bash
ip route get 10.10.2.5
ip route get 8.8.8.8
```

This prints the exact route the kernel would use, including the source address it would send from. In a routing dispute it is the authoritative answer, and it takes one second.

---
### A Conceptual Look at Dynamic Routing

You will not configure BGP in this course, but you will hear it named in incident channels, and you should know what people are referring to.

A dynamic routing protocol is simply routers telling each other which networks they can reach, so that routing tables are built and repaired automatically rather than typed by hand. Two families matter.

**OSPF (Open Shortest Path First)** is an interior gateway protocol: it runs inside one organization's network. Every router floods a description of its own links to every other router, so each one builds a complete map of the network and computes shortest paths itself. It converges quickly and it is what enterprise data center networks typically run internally.

**BGP (Border Gateway Protocol)** is an exterior gateway protocol: it runs between organizations, and it is what stitches the independent networks of the internet into a single reachable whole. It does not choose routes by shortest path but by policy, because the question it answers is commercial as much as technical. BGP is also why "the internet broke" headlines happen: a misconfigured BGP announcement from one network can withdraw or hijack routes for a large part of the world, and it has, several times, taken major platforms offline for hours.

**Where this touches you.** In a cloud VPC you do not run a routing protocol at all: you edit a route table object, and the provider's software defined network enforces it. Where dynamic routing does reappear in DevOps work is in Kubernetes: several CNI plugins, Calico most prominently, use BGP to distribute pod network routes across nodes. That is the moment the word stops being trivia and starts being something you configure.

---
## 3.4 DNS in Practice

You already know DNS resolves names to IP addresses through a chain of lookups. The practical engineering knowledge sits in the record types you will actually configure and a few behaviors that catch people off guard in production.

---
### Record Types You Will Actually Use

|   Record  | What It Does                                                                                         | Common Uses                                                                                   | Example                                            |
| :-------: | ---------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- | -------------------------------------------------- |
|   **A**   | Maps a hostname to an IPv4 address.                                                                  | The most common DNS record, used by websites, APIs, and other services.                       | `example.com → 93.184.216.34`                      |
|  **AAAA** | Maps a hostname to an IPv6 address.                                                                  | Used when a service is reachable over IPv6.                                                   | `example.com → 2606:2800:220:1:248:1893:25c8:1946` |
| **CNAME** | Creates an alias from one hostname to another hostname. It does not point directly to an IP address. | Point `www.example.com` to `example.com`, or map a custom domain to a cloud service hostname. | `www.example.com → example.com`                    |
|   **MX**  | Identifies the mail servers responsible for receiving email for a domain.                            | Routes incoming email to the correct mail server.                                             | `example.com → mail.example.com`                   |
|   **NS**  | Identifies the authoritative name servers for a domain or subdomain.                                 | Delegates DNS management to specific name servers or DNS providers.                           | `example.com → ns1.example.net`                    |
|  **TXT**  | Stores arbitrary text associated with a domain.                                                      | SPF, DKIM, DMARC, domain ownership verification, and other verification records.              | `"v=spf1 include:_spf.google.com ~all"`            |
|  **PTR**  | Maps an IP address back to a hostname (reverse DNS).                                                 | Reverse DNS lookups, mail server validation, logging, and troubleshooting.                    | `93.184.216.34 → example.com`                      |

### Notes

* **A** and **AAAA** records are used for **forward DNS lookups** (hostname > IP address).
* **PTR** records are used for **reverse DNS lookups** (IP address > hostname).
* A **CNAME** record must point to another **hostname**, never directly to an IP address.
* A domain **cannot** have a **CNAME** record at the zone apex (for example, `example.com`) if other records such as **NS** or **SOA** exist there. Many DNS providers offer proprietary alternatives such as **ALIAS** or **ANAME** to work around this limitation.
* Modern email deployments commonly use multiple **TXT** records for **SPF**, **DKIM**, and **DMARC** authentication. This helps prevent email spoofing and improves email deliverability.
* **PTR** records live in a reverse zone (`in-addr.arpa`) controlled by whoever owns the IP block, which in practice means your cloud provider or hosting company, not you. You request a PTR record; you do not simply add one to your own zone file. This is why outbound mail from a fresh cloud instance is so often rejected.


> The record types you will configure most often as a DevOps engineer are the A record and the CNAME. A common real pattern: your application's actual address is something ugly generated by a cloud load balancer, like `my-app-1234567890.us-east-1.elb.amazonaws.com`. You create a CNAME record pointing `app.yourcompany.com` to that load balancer hostname, so users see a clean, branded domain while the underlying infrastructure can change without anyone needing to update a bookmark.

---
`/etc/resolv.conf` on Linux specifies which DNS server the system uses:

* View current DNS configuration
```bash
cat /etc/resolv.conf
```

* On systems using systemd-resolved
```bash
resolvectl status
```

On RHEL/Fedora with NetworkManager, DNS is managed via `nmcli` or connection profiles, not by editing `/etc/resolv.conf` directly. The file is often a symlink managed by `systemd-resolved`.

---
### Reading a `dig` Answer

`dig` is the tool you will reach for whenever a name resolves to something unexpected, and its output rewards a careful read.

```bash
dig example.com A
```

The answer is divided into sections. The QUESTION section repeats what you asked, which is useful when a search domain has silently been appended to your query. The ANSWER section contains the records returned, each with its remaining TTL in seconds as the second field. The `status: NOERROR` in the header means the query succeeded; `NXDOMAIN` means the name does not exist at all, which is a very different problem from a name existing and pointing at the wrong address.

Three flags do most of the work in practice:

```bash
# Just the answer, nothing else
dig +short example.com

# Ask a specific resolver, bypassing whatever your system is configured to use
dig @1.1.1.1 example.com
dig @8.8.8.8 example.com

# Walk the delegation chain from the root servers down, ignoring caches
dig +trace example.com
```

`+trace` is the one that settles arguments. It starts at the root, follows the NS delegations to the TLD servers, then to the authoritative servers for the domain, and shows you each hop. If the authoritative server returns the correct new address but your application still sees the old one, the problem is a cache somewhere between the two, which is a TTL problem, not a DNS configuration problem.

`dig` lives in the `bind-utils` package on RHEL and Fedora and `dnsutils` on Debian and Ubuntu. Minimal cloud images frequently ship without it, which is worth knowing before you need it at three in the morning.

---
### TTL: The Setting That Bites People During Migrations

TTL, time to live, controls how long a DNS answer is allowed to be cached before a resolver has to ask again. This number is invisible until the moment you need to change a DNS record quickly, and then it becomes the single most important number in the room.

If your A record has a TTL of 3600 seconds (one hour), and you change which server it points to, some fraction of the internet will keep using the old, cached answer for up to an hour. During a planned migration, this is manageable: you lower the TTL to something small, like 60 seconds, a day or two before the migration, wait for the old, longer TTL to fully expire out of caches everywhere, make the change, and then raise the TTL back up once everything is confirmed stable.

During an unplanned incident, a high TTL is a genuine problem. If a server's IP address needs to change immediately because of a security issue, and the TTL was left at 86400 seconds (24 hours), you are stuck waiting for caches around the world to expire naturally, with no way to force it.

- Planned migration timeline:
```
Day 1: Lower TTL on the existing record to 60 seconds
Day 2: Wait at least as long as the original (prechange) TTL value, so any caches that fetched the record before you lowered it have time to expire
Day 3: Make the actual change (update the A or CNAME record)
Day 4: Confirm traffic has shifted, then raise TTL back to a normal value
```

One caveat worth carrying: lowering the TTL is a request, not a command. Some resolvers, particularly on consumer ISP networks, clamp or ignore very low TTLs and hold answers longer than you asked them to. Plan the cutover so that the old address keeps serving traffic for a while after the change rather than being switched off at the moment the record flips. Keeping the old server alive and serving for an extra day costs almost nothing. Turning it off on schedule and discovering that a long tail of clients is still resolving to it costs a great deal.

---
### Split Horizon DNS

Split horizon DNS, sometimes called split brain DNS, is a setup where the same domain name resolves to different answers depending on who is asking. An internal employee on the company VPN querying `database.internal.company.com` might get a private IP address reachable only inside the company network. Someone outside the company querying the same name either gets no answer at all or gets routed somewhere entirely different.

This is common in real infrastructure for two reasons. First, security: internal services like databases and admin panels should never resolve to anything from the public internet at all, removing an entire category of attack surface. Second, practicality: an internal service might be reachable via a private IP on the company's internal network, while the same hostname, when queried from outside, might point to a public facing proxy or simply fail to resolve, which is the desired, intentional behavior.

In AWS this is not a bespoke setup but a first class feature: a Route 53 private hosted zone attached to a VPC answers queries from inside that VPC, while a public hosted zone with the same domain name answers everyone else. Kubernetes does the same thing inside a cluster, where CoreDNS resolves `service.namespace.svc.cluster.local` to a ClusterIP that means nothing outside the cluster. Both are split horizon DNS by another name.

The failure mode to watch for is the resulting confusion. When one engineer says a name resolves correctly and another says it does not, and both are telling the truth, split horizon is usually the reason. The correct next question is not "is it broken" but "which resolver were you asking."

---
### Common DNS Mistakes

**Leaving TTL high before a planned change.**

Always lower it ahead of time, not at the moment of the change.

**Forgetting that CNAME records cannot coexist with other records at the same name.**

If `example.com` has a CNAME record, you cannot also add an MX or TXT record at that same name. This is a real DNS rule, not a tooling limitation, and it trips up a lot of people setting up email on a domain that uses a CNAME for the root.

**Assuming a DNS change has propagated because it works for you.** 

Your own machine and resolver might already have a stale answer cached, or might be hitting a resolver that already refreshed. Use `dig @8.8.8.8` and `dig @1.1.1.1` to explicitly check what different public resolvers are currently returning before declaring a DNS change complete.

**Debugging with `ping` instead of `dig`.**

`ping` resolves a name and then immediately tries to reach it, so a failure tells you nothing about which of the two steps broke. `dig` answers the resolution question alone. Separate the two questions before you try to answer either.

---
## 3.5 Load Balancing

### What Is a Load Balancer?

A load balancer sits in front of a group of servers and distributes incoming requests across them. Without one, all traffic hits a single server. When that server becomes overloaded or fails, the application goes down.

---
**With a load balancer:**

- Traffic is spread across multiple servers, preventing any single one from being overwhelmed.
- If a server fails, the load balancer stops sending it traffic, and the application stays up.
- You can add or remove servers without changing anything the client sees.

---
### Layer 4 vs. Layer 7 Load Balancing

| Type              | Operates At    | Routing Basis                          | Awareness of Content |
|-------------------|----------------|----------------------------------------|----------------------|
| L4 (Transport)    | TCP/UDP level  | IP address and port                    | None; routes without reading the request |
| L7 (Application)  | HTTP level     | URL path, hostname, headers, cookies   | Full; can route based on request content |

An L7 load balancer can route `/api/*` requests to an API server cluster and `/static/*` to an object storage endpoint. An L4 load balancer cannot make that distinction.

Nginx functions as both. AWS Elastic Load Balancing offers an Application Load Balancer (ALB, Layer 7) and a Network Load Balancer (NLB, Layer 4).

The tradeoff is not simply "L7 is better." An L4 load balancer forwards packets without reading them, so it is faster, cheaper, and protocol agnostic: it will happily balance PostgreSQL, gRPC, or any TCP protocol it has never heard of, and it can preserve the client's source IP. An L7 load balancer must terminate the connection, parse the request, and open a new connection to the backend. That gives it path routing, header inspection, TLS termination, and retries, at the cost of latency and the fact that the backend now sees the load balancer's IP rather than the client's, which is why `X-Forwarded-For` exists. Choose L4 when you need raw throughput or a non HTTP protocol; choose L7 when routing decisions depend on what is inside the request.

---
## 3.6 Load Balancing Algorithms

You already know conceptually why load balancers exist. The engineering decision is choosing which algorithm fits a given workload, because the wrong choice creates real performance problems.

---
### Round Robin

Requests are distributed to backend servers in strict rotating order: server one, then server two, then server three, then back to server one. This is the simplest algorithm and the most common default.

Round robin works well when every backend server has roughly equal capacity, and every request takes roughly the same amount of time to process. It breaks down when those two assumptions are not true. If one request takes ten milliseconds and another takes ten seconds, round robin has no awareness of that difference and will happily send the next request to whichever server is next in line, even if that server is still struggling with a slow request from a moment ago.

- Example:

```nginx
upstream backend {
    server 192.168.1.10;
    server 192.168.1.11;
    server 192.168.1.12;
    # Round robin is the default; no directive needed
}
```

Limitation: It assumes all requests take the same time. If some requests are CPU heavy and others are trivial, round robin can overload one server while others sit idle.

---
**Weighted Round Robin**

Servers get a weight proportional to their capacity. A server with weight 3 receives three times as many requests as one with weight 1.

```nginx
upstream backend {
    server 192.168.1.10 weight=3;  # More powerful server
    server 192.168.1.11 weight=1;
}
```

Weights are also the mechanism behind a canary release: give the new version a weight of 1 against the old version's weight of 19, and roughly five percent of traffic reaches the new build while you watch its error rate.

---
### Least Connections

The load balancer tracks how many active connections each backend currently has open and routes each new request to whichever server currently has the fewest.

This is the better choice whenever the request duration varies significantly, which describes most real applications. A backend currently handling three long running requests will naturally receive fewer new requests than one sitting idle, because least connections actively accounts for current load rather than blindly rotating.

- Example:

```nginx
upstream backend {
    least_conn;
    server 192.168.1.10;
    server 192.168.1.11;
    server 192.168.1.12;
}
```

---
### IP Hash

The client's source IP address is run through a hash function, and the result determines which backend server handles that client. Critically, the same client IP always maps to the same backend server, as long as the pool of backend servers does not change.

This is used specifically when an application keeps session data in memory on a particular server rather than in a shared store like Redis. If a user logs in and their session data lives only in server two's memory, every subsequent request from that user needs to land on server two specifically, or the application will not recognize them as logged in.

This is commonly called sticky sessions, or session affinity, in practice. The tradeoff is real: if a server holding sticky sessions goes down, every user who was pinned to it gets disconnected and has to start a fresh session somewhere else. The long term fix used by most modern, well architected applications is to move session state out of the server entirely and into a shared store like Redis, which removes the need for sticky sessions altogether and lets you use least connections instead, which handles uneven load far better.

- Example:

```nginx
upstream backend {
    ip_hash;
    server 192.168.1.10;
    server 192.168.1.11;
    server 192.168.1.12;
}
```

Limitation: if a server goes down, all clients mapped to it get reassigned. Also, if many users share a NAT IP (for example, an entire office behind a single public IP), one server takes all their traffic. For long-term production use, move session state to a shared store like Redis and use least connections instead.

---
### Sticky Sessions Without IP Hash

IP hash is not the only way to achieve stickiness, and it is usually the crudest. An L7 load balancer can pin a client with a cookie instead, which survives a client changing IP address and does not collapse when an entire office shares one NAT address. AWS ALB does this with target group stickiness, setting its own `AWSALB` cookie. Nginx open source does not offer cookie based stickiness; the `sticky` directive is an Nginx Plus feature, and the community workaround is a hash on a request header or cookie value:

```nginx
upstream backend {
    hash $cookie_sessionid consistent;
    server 192.168.1.10;
    server 192.168.1.11;
}
```

The `consistent` keyword is worth understanding. With plain hashing, adding or removing one backend rehashes nearly every client and scatters every existing session. Consistent hashing remaps only the fraction of clients that belonged to the changed server. If you must be sticky, be sticky consistently.

---
### Choosing Between Them in Practice

| Situation | Best Choice | Why |
|---|---|---|
| Stateless API, uniform request cost | Round robin | Simple, even distribution, no downside |
| Requests vary widely in duration | Least connections | Adapts to actual current load |
| Server holds session state in memory | IP hash (sticky sessions) | Same user must reach the same server |
| Server holds session state in Redis or similar shared store | Least connections | No need for stickiness, better load distribution |
| Backends have unequal capacity, or you are running a canary | Weighted round robin | Traffic share is set explicitly, per server |

The pattern worth internalizing: sticky sessions are usually a sign of an architectural shortcut, not a long term design goal. Most experienced teams treat moving session state out of the application server as a priority specifically so they can stop using sticky sessions and switch to least connections.

---
### Health Checks

Any production load balancer should periodically probe each backend to confirm it is healthy and remove it from rotation if it fails.

Nginx open source uses passive health checks: it detects failures when a request to a backend actually fails. Nginx Plus adds active health checks. AWS ALB performs active health checks: it sends an HTTP request to a configured path (typically `/health`) on each backend every 30 seconds and removes backends that return non-2xx responses or time out.

**Passive checks in Nginx open source** are configured on the upstream server itself:

```nginx
upstream backend {
    server 192.168.1.10 max_fails=3 fail_timeout=30s;
    server 192.168.1.11 max_fails=3 fail_timeout=30s;
    server 192.168.1.12 backup;
}
```

Three failed requests within 30 seconds mark that backend unavailable for the next 30 seconds. The `backup` server receives traffic only when all primary servers are down. The important limitation: a passive check only learns a backend is broken by failing a real user's request against it. Some users pay for the discovery.

**AWS ALB defaults**, which you should know because they are what you get when you do not set them: a check every 30 seconds, a 5 second timeout, 2 consecutive failures to mark a target unhealthy, and 5 consecutive successes to mark it healthy again. Those defaults mean an unhealthy target recovering takes up to 150 seconds to return to service, which surprises people during deployments.

**What makes a good health endpoint.** A health check should verify that the process can serve traffic, and stop there. If `/health` also checks the database, a brief database blip marks every instance unhealthy at once and the load balancer removes the entire fleet, converting a degraded dependency into a full outage. Keep a shallow liveness check for the load balancer and put dependency checks somewhere else, such as a separate readiness endpoint or your monitoring system. This is exactly the distinction Kubernetes draws between liveness and readiness probes, which you will meet again in the Kubernetes module.

---
## 3.7 Firewalls and Security Groups
---
### What Is a Firewall?

A firewall is a network security system that monitors and controls traffic based on a defined set of rules. Rules specify: direction (inbound or outbound), source IP, destination IP, protocol (TCP/UDP/ICMP), and port. Traffic that matches an allow rule is permitted; everything else is denied (default deny posture) or vice versa.

---
### The Practical Difference: Stateful vs Stateless

A stateless firewall evaluates every single packet on its own, with no memory of what came before it. If you want to allow a client to make a request and receive a response, you have to write two separate rules: one allowing the request in, and a second allowing the response back out. The firewall has no concept of "this response belongs to that earlier request."

A stateful firewall tracks active connections. You write one rule allowing the initial request through, and the firewall automatically recognizes the response traffic as part of that same, already permitted connection, allowing it back through without a separate matching rule.

---
### Why This Distinction Actually Matters

This is not a minor technical detail. It changes how many rules you write and how easy your firewall configuration is to reason about and audit later.

With a stateless setup, every single service needs explicit rules in both directions. Forgetting the return path rule is one of the most common firewall misconfigurations, and it produces a specific, confusing symptom: the connection appears to initiate successfully, but then it simply hangs, because the response is silently being dropped on its way back.

With a stateful setup, you only think about the direction the connection was initiated in. Nearly everything you will configure throughout this course, AWS Security Groups, `firewalld` on RHEL based systems, is stateful, specifically because it removes this entire category of mistake.

---
### Default Deny

A default deny posture means that unless traffic explicitly matches an allow rule, it is blocked automatically. This stands in contrast to the default allow, where traffic passes through freely unless something explicitly blocks it.

Every serious production environment uses default deny. AWS Security Groups are default deny by design: when you create a brand new security group, it permits no inbound traffic at all until you add explicit allow rules. This is a deliberate, important safety decision. It means a forgotten or misconfigured rule results in something being unreachable, which is an obvious, loud, immediately noticeable problem. The alternative, default allow, means a forgotten rule results in something being exposed to the internet that should never have been reachable in the first place, which can sit completely silent and unnoticed for months until it becomes a real security incident.

---
### How This Looks in Practice

A team provisions a new database server. They correctly attach a security group allowing inbound traffic on port 5432 only from their application servers' security group, not from the broader internet. Three months later, a different engineer, debugging an unrelated issue, temporarily adds a rule allowing `0.0.0.0/0` (meaning literally any IP address on the internet) on port 5432 to make their own local testing easier, fully intending to remove it once their testing wraps up. They forget. Because the environment defaults to deny everything except what is explicitly allowed, this single overly permissive rule is now the one and only path that exposes the database directly to the public internet. A routine security audit a few weeks later catches it immediately, specifically because it stands out as the one rule that obviously does not belong, sitting in clear contrast to the otherwise tightly scoped default deny configuration.

---
### `firewalld` on Linux

`firewalld` is the default firewall management tool on RHEL, Fedora, and CentOS Stream. It uses zones to classify network interfaces. The most common zones:

- `public`: the default for external-facing interfaces. Only explicitly allowed services and ports are permitted.
- `trusted`: all traffic is allowed.
- `drop`: all incoming traffic is silently dropped.

Two more zones are worth knowing by name: `internal`, intended for a trusted internal network and slightly more permissive than `public`, and `block`, which rejects incoming traffic with an ICMP error rather than dropping it silently. The distinction between `drop` and `block` is exactly the distinction between a connection that times out and one that is refused, which is the diagnostic difference described in section 3.1.

Common `firewall-cmd` operations:

* List all rules in the active zone
```bash
firewall-cmd --list-all
```

* Allow SSH (`--permanent` survives reboot)
```bash
firewall-cmd --permanent --add-service=ssh
```

* Allow a specific port
```bash
firewall-cmd --permanent --add-port=8080/tcp
```

* Remove a port
```bash
firewall-cmd --permanent --remove-port=8080/tcp
```

* Reload to apply permanent changes to the running config
```bash
firewall-cmd --reload
```

>Without `--permanent`, changes apply only to the running configuration and are lost on reboot.

Two more commands you will want in the labs:

```bash
# Which zone is this interface in? The answer explains a lot of "blocked" traffic.
firewall-cmd --get-active-zones

# Move an interface into a zone permanently
firewall-cmd --permanent --zone=internal --change-interface=enp0s2
firewall-cmd --reload
```

Since RHEL 8, `firewalld` uses `nftables` as its backend rather than `iptables`. You configure zones and services; `firewalld` renders them into nftables rules underneath. This matters when you go looking for your rules with `iptables -L` and find almost nothing there.

---
### AWS Security Groups

In AWS, Security Groups function as virtual firewalls attached to EC2 instances and other resources. Key characteristics:

- Stateful: you define inbound rules; return traffic is automatically allowed.
- Default behavior: all inbound traffic is denied; all outbound traffic is allowed.
- You add explicit inbound allow rules by protocol, port range, and source (CIDR or another security group).
- Multiple security groups can be attached to one instance.

Example inbound rules for a web server:

| Type   | Protocol | Port Range | Source        | Purpose             |
|--------|----------|------------|---------------|---------------------|
| SSH    | TCP      | 22         | Your office IP /32 | Admin access   |
| HTTP   | TCP      | 80         | 0.0.0.0/0    | Public web traffic  |
| HTTPS  | TCP      | 443        | 0.0.0.0/0    | Public HTTPS traffic |

There is no deny rule in a security group. You can only add allow rules, and everything not allowed is denied. This is a feature, not a limitation: it makes a security group readable top to bottom with no rule ordering to reason about, and it means the answer to "can this reach that" is always the union of the allow rules, never a subtraction.

The most valuable habit in this section: use a security group as the source, not a CIDR block. A rule on the database security group allowing port 5432 from `sg-app` rather than from `10.0.2.0/24` keeps working when the app tier moves subnets, scales, or is rebuilt, and it cannot accidentally grant access to something else that happens to land in that CIDR range later.

---

**Security Groups vs. NACLs:** Security Groups operate at the instance level and are stateful. NACLs (Network Access Control Lists) operate at the subnet level and are stateless: you must explicitly allow both inbound and outbound directions. For most DevOps work, Security Groups are the primary tool. NACLs add an extra layer of subnet-level control when needed.

The stateless nature of NACLs has a consequence people meet exactly once and never forget. Because return traffic is not tracked, a NACL that allows inbound HTTPS on 443 but has no outbound rule covering the ephemeral port range will let requests in and silently drop every response. Any outbound NACL rule intended to permit replies must allow the ephemeral range, ports 1024 through 65535, not just the service port. NACLs also process rules in numbered order and stop at the first match, unlike security groups, and they do support explicit deny rules, which is the one thing they can do that security groups cannot. That makes them the correct tool for blocking a specific abusive IP range at the subnet edge, and the wrong tool for routine service to service access control.

| | Security Group | NACL |
|---|---|---|
| Attaches to | Instance / ENI | Subnet |
| State tracking | Stateful | Stateless |
| Rule types | Allow only | Allow and deny |
| Evaluation | All rules, union of allows | In number order, first match wins |
| Typical use | Everyday service access control | Coarse subnet level blocks |

---
### `iptables`

`iptables` is the lower level Linux firewall framework that `firewalld` builds on top of. On newer systems, `iptables` commands are translated to `nftables` rules. You will encounter `iptables` directly on older systems and in Docker networking, where Docker adds its own rules to manage container networking.

Key concepts:

- **Tables:** `filter` (controls packet acceptance), `nat` (address translation), `mangle` (modifies packet headers).

- **Chains in the filter table:** `INPUT` (traffic destined for this host), `OUTPUT` (traffic originating from this host), `FORWARD` (traffic passing through this host).

- **Policy:** the default action if no rule matches (`ACCEPT` or `DROP`).

* List all rules with line numbers
```bash
iptables -L -n -v --line-numbers
```

* Allow incoming SSH
```bash
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
```

* Drop all other incoming traffic
```bash
iptables -P INPUT DROP
```

`iptables` rules are not persistent by default. Save and restore them with `iptables-save` and `iptables-restore`, or use `firewalld` or `ufw` which handle persistence automatically.

> The `FORWARD` chain is not an academic footnote. It is the chain that decides whether a Linux host will route packets between two of its own interfaces, which is exactly what you are asking it to do in Lab 3C, and it is the reason a router VM with `ip_forward` enabled can still silently drop everything if the firewall says no.

On RHEL 9 and later, and on Fedora, the `iptables` command you type is a compatibility shim (`iptables-nft`) that writes nftables rules underneath. Two consequences follow. Rules created by `firewalld` may not appear in `iptables -L` output at all, which leads people to conclude no firewall is running when one very much is. And the native tool for inspecting what is actually loaded is `nft`:

```bash
# The rules actually in the kernel, as nftables sees them
sudo nft list ruleset
```

`iptables` knowledge remains worth having because Docker still writes iptables rules to publish container ports, and because Kubernetes `kube-proxy` in iptables mode implements Service routing with them. You will read those rules long before you write any of your own.

---
## 3.8 DHCP

DHCP (Dynamic Host Configuration Protocol) is what automatically assigns IP addresses to devices when they join a network. Without DHCP, every device would need a manually configured static IP, which is unmanageable at scale.

When a Linux server or container boots, it sends a broadcast request (DHCP Discover) looking for a DHCP server. The server responds with an offer (IP address, subnet mask, default gateway, DNS server, and lease duration). The client accepts the offer and uses those settings until the lease expires.

The four step exchange has a name worth remembering, because the acronym tells you which step failed when you read a packet capture: DORA, for Discover, Offer, Request, Acknowledge. The client broadcasts a Discover because it has no address yet and cannot send a unicast packet. Servers reply with an Offer. The client broadcasts a Request naming the offer it accepts, which is also how the servers it declined learn to release their reservations. The chosen server confirms with an Acknowledge. DHCP runs over UDP, port 67 on the server and port 68 on the client.

In AWS, every EC2 instance automatically receives an IP address, subnet mask, default gateway, and DNS resolver via DHCP. You do not configure this manually. The VPC's DHCP options set controls which DNS servers and domain names are handed out.

In Linux, you can see DHCP-assigned addresses with `ip addr show`. The lease information is stored in files like `/var/lib/dhclient/dhclient.leases` or managed by NetworkManager/systemd-networkd, depending on the distribution.

---
**Why does this matter in DevOps?**

- Containers and VMs in most environments get their networking via DHCP.

- If DHCP fails, devices fall back to link local addresses in the `169.254.0.0/16` range. If you see a `169.254.x.x` address on an interface that should have a real IP, DHCP has failed.

- When designing server infrastructure, critical services (databases, load balancers, DNS servers) should always have static IPs or use DHCP reservations, not floating leases.

- A cloud instance's private IP is handed to it by DHCP but is fixed for the life of the instance, so the address itself is stable. What is not stable is the assumption that it will be the same after a rebuild. This is precisely why service discovery and DNS exist, and why hardcoding an instance's IP into a configuration file is a mistake you make only once.

- Docker runs its own address assignment for the default bridge network, out of `172.17.0.0/16`. Kubernetes assigns pod addresses from a cluster wide pod CIDR through the CNI plugin, not through DHCP at all. Both are the same idea wearing different clothes: something has to hand out addresses, and the day it collides with an address range you already use on your corporate network is the day you learn which range it was using.

---
## 3.9 TLS and HTTPS

TLS (Transport Layer Security) is the protocol that encrypts traffic between a client and a server. It operates at the boundary between Layer 6 (Presentation) and Layer 7 (Application) in the OSI model. HTTPS is HTTP running over TLS.

As a DevOps engineer, you deal with TLS constantly: generating and renewing certificates, configuring Nginx to terminate TLS, debugging handshake failures, and setting up tools like Let's Encrypt or AWS Certificate Manager.

---
**How a TLS handshake works:**

1. The client connects to the server and sends the TLS versions and cipher suites it supports.
2. The server responds with its chosen cipher suite and its TLS certificate.
3. The client verifies the certificate against trusted Certificate Authorities (CAs).
4. They agree on a session key using asymmetric cryptography (an ephemeral Diffie-Hellman exchange, ECDHE in any modern configuration).
5. All subsequent traffic is encrypted with that session key using symmetric encryption (typically AES-GCM or ChaCha20-Poly1305).

**A correction worth making explicitly.** Older material, including earlier drafts of these notes, describes step 4 as using "RSA or ECDHE." That is now wrong in an important way. TLS 1.3 removed RSA key exchange entirely, along with static Diffie-Hellman, because neither provides forward secrecy: an attacker who records encrypted traffic today and later obtains the server's private key can decrypt all of it retroactively. Every TLS 1.3 handshake uses an ephemeral key exchange, so past sessions stay unreadable even if the server key is later compromised. RSA still appears in TLS 1.3, but only as a signature algorithm proving the server owns its certificate, never as the means of exchanging the session key. When you configure a cipher list for TLS 1.2 and see every suite begin with `ECDHE`, this is the reason.

TLS 1.3 also completes the handshake in one round trip rather than two, which is a visible latency improvement, and it encrypts more of the handshake itself.

---
**Major terms:**

- **Certificate:**
  
      A file containing the server's public key and identity, signed by a CA.

- **CA (Certificate Authority):**

      A trusted third party that signs certificates (Let's Encrypt, DigiCert, AWS ACM).

- **Self signed certificate:**

      A certificate signed by its own private key, not by a CA. Browsers and tools will warn or refuse to connect unless you explicitly trust it. Used in lab environments.

- **Certificate chain:**

      Many certificates are not signed directly by a root CA but by an intermediate CA. The full chain (leaf > intermediate > root) must be presented to clients.

- **SNI (Server Name Indication):**

      A TLS extension that lets a single server serve multiple certificates on one IP address. The client sends the hostname in the TLS handshake before encryption begins.

**On the chain, since this is the failure you will actually hit.** The server must send the leaf certificate and every intermediate above it, but not the root, which the client already has. Browsers often paper over a missing intermediate by fetching it themselves, so a site can look perfectly fine in Chrome and fail in `curl`, in a Java client, and in your CI pipeline. When someone reports that a certificate "works in the browser but breaks in the app," a missing intermediate is the first thing to check. With Let's Encrypt, always deploy `fullchain.pem`, never `cert.pem`, and the problem does not arise.

**On SNI.** Because the client sends the hostname in the clear before encryption begins, the server knows which certificate to present even when many sites share one IP address. This is what makes shared hosting and multi tenant ingress possible. It is also why a request that reaches the right IP can still be answered with the wrong certificate: if the client omits SNI, or sends a name the server has no server block for, it gets the default certificate. That is exactly the situation `openssl s_client -servername` exists to reproduce.

---
**Nginx TLS configuration:**

```nginx
server {
    listen 443 ssl;
    listen [::]:443 ssl;
    http2 on;

    server_name example.com;

    ssl_certificate     /etc/nginx/ssl/fullchain.pem;   # leaf plus intermediates
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305;
    ssl_prefer_server_ciphers off;

    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;

    add_header Strict-Transport-Security "max-age=63072000" always;
}
```

Three things in that block have changed from what older tutorials teach, and each is worth knowing.

`listen 443 ssl http2;` is deprecated as of Nginx 1.25.1. HTTP/2 is now enabled with a separate `http2 on;` directive inside the server block. The old form still parses but emits a warning on every `nginx -t`.

`ssl_ciphers HIGH:!aNULL:!MD5;` was standard advice for years and is now too loose: `HIGH` still admits CBC mode suites and other constructions that current guidance excludes. The list above is Mozilla's intermediate profile, which permits only ECDHE key exchange with AEAD ciphers. Note that `ssl_ciphers` has no effect on TLS 1.3 at all, which chooses from its own fixed set of three AEAD suites; the directive governs TLS 1.2 only.

`ssl_prefer_server_ciphers off;` looks wrong to anyone taught to force the server's ordering, but when the cipher list contains only strong suites, there is no weak option to protect the client from, and letting the client choose lets it pick whichever suite its hardware runs fastest. Mozilla sets this off deliberately in both the intermediate and modern profiles.

TLSv1.0 and TLSv1.1 are deprecated and disabled in modern configurations. Only TLSv1.2 and TLSv1.3 should be used in production. Rather than copying a cipher list from a blog post, generate one for your exact Nginx and OpenSSL versions from the Mozilla SSL Configuration Generator at `https://ssl-config.mozilla.org/`, which is the reference the rest of the industry treats as authoritative.

You can check the TLS configuration of any server with:

* View the certificate and negotiated protocol
```bash
curl -vI https://example.com 2>&1 | grep -E "(TLS|SSL|issuer|expire)"
```

* More detailed TLS inspection
```bash
openssl s_client -connect example.com:443 -servername example.com
```

* Check the expiry date without reading the whole certificate
```bash
echo | openssl s_client -connect example.com:443 -servername example.com 2>/dev/null \
  | openssl x509 -noout -dates -subject -issuer
```

* Verify the chain the server actually sends, which is where the missing intermediate shows up
```bash
openssl s_client -connect example.com:443 -servername example.com -showcerts
```

> Certificate expiry is one of the most common causes of a sudden, total, self inflicted outage, and it is entirely preventable. Automate renewal (`certbot` with a systemd timer, or AWS ACM, which renews by itself) and alert on days remaining, not on failure. A certificate that expires at 02:00 on a Saturday does not care how good your incident response is.

---
## 3.10 NAT, Addressing, and CIDR in Practice
---
### IPv4 Addressing

An IPv4 address is a 32-bit number written in four octets of decimal, separated by dots: `192.168.1.10`.

Each octet represents 8 bits, giving a range of 0 to 255 per octet. Total IPv4 address space: 2^32 = approximately 4.3 billion addresses.

An IP address has two parts: the network portion (which network) and the host portion (which device on that network). The subnet mask separates them.

---
### Subnetting and CIDR Notation

CIDR (Classless Inter Domain Routing) notation is simply the precise way engineers write down both an address range and its size in one compact expression, like `10.0.1.0/24`.

The number after the slash tells you how many bits are fixed as the network portion. The remaining bits are available for individual host addresses within that range. A smaller number after the slash means a larger range of addresses. A larger number after the slash means a smaller, more tightly scoped range.

| Prefix | Subnet Mask       | Network Bits | Host Bits | Usable Hosts |
|--------|-------------------|--------------|-----------|--------------|
| /8     | 255.0.0.0         | 8            | 24        | 16,777,214   |
| /16    | 255.255.0.0       | 16           | 16        | 65,534       |
| /24    | 255.255.255.0     | 24           | 8         | 254          |
| /25    | 255.255.255.128   | 25           | 7         | 126          |
| /26    | 255.255.255.192   | 26           | 6         | 62           |
| /27    | 255.255.255.224   | 27           | 5         | 30           |
| /28    | 255.255.255.240   | 28           | 4         | 14           |
| /30    | 255.255.255.252   | 30           | 2         | 2            |
| /32    | 255.255.255.255   | 32           | 0         | 1 (single host) |

Usable hosts = 2^(host bits) - 2. You subtract 2 because the first address is the network address and the last is the broadcast address. Neither can be assigned to a device.

---
**Example: 192.168.1.0/26**

- Prefix length: 26 bits network, 6 bits host
- Subnet mask: 255.255.255.192 (binary: 11111111.11111111.11111111.11000000)
- Network address: 192.168.1.0
- Broadcast address: 192.168.1.63 (all host bits set to 1)
- Usable host range: 192.168.1.1 to 192.168.1.62
- Number of usable hosts: 2^6 - 2 = 62
  
---
### Doing the Math Without Binary

You will do this often enough that the shortcut is worth learning properly, and slowly enough at first that the binary is worth writing out once.

The block size of a subnet is `256 - (last non zero octet of the mask)`. For a /26, the mask is 255.255.255.192, so the block size is `256 - 192 = 64`. Subnets therefore begin at multiples of 64 in the final octet: .0, .64, .128, .192. Any address you are given falls into whichever of those blocks contains it.

Take `192.168.1.100/26`. The block size is 64. The multiples of 64 are 0, 64, 128, 192, and 100 falls between 64 and 128. So:

- Network address: 192.168.1.64
- Broadcast address: 192.168.1.127 (one below the next block, 128)
- Usable range: 192.168.1.65 to 192.168.1.126
- Usable hosts: 62

Three questions, three seconds, no binary. Verify with a tool rather than trusting the arithmetic:

```bash
ipcalc 192.168.1.100/26        # RHEL/Fedora: dnf install ipcalc
sipcalc 192.168.1.100/26       # alternative, more detail
```

**AWS subtracts five, not two.** In every AWS subnet, five addresses are unavailable: the network address, the broadcast address, and three that AWS reserves for the VPC router, DNS, and future use. A /24 subnet gives 251 usable addresses in AWS, not 254. A /28, the smallest AWS permits, gives 11. This is not a rounding error when an autoscaling group and a load balancer are drawing from the same range.

---
### Why Real Infrastructure Uses Multiple Small Subnets Instead of One Large One

A common beginner instinct is to provision one enormous subnet and put every single resource into it. Real infrastructure rarely does this, for a few concrete, practical reasons.

Different tiers of an application need different exposure levels. Your web servers might need to be reachable from the public internet. Your database absolutely should not be. Placing them in separate subnets, a public subnet and a private subnet, lets you apply fundamentally different routing rules and security postures to each group, rather than relying entirely on security group rules to manually compensate within one giant, undifferentiated address space.

Cloud providers also organize infrastructure around availability zones, physically separate data centers within a region. A standard, resilient pattern places a public subnet and a private subnet in each availability zone, so that if one entire availability zone has a problem, the application can keep running using the resources in the others. This naturally produces several smaller subnets rather than one large flat one.

The distinction that actually defines a public subnet is worth stating plainly, because it is not a checkbox and not a naming convention. A subnet is public if and only if its route table has a route to an internet gateway. A subnet is private if its route table sends outbound traffic to a NAT gateway instead, or nowhere at all. Two subnets can be identical in every other respect and differ only in that one line of their route tables. Everything else, the names, the tags, the diagrams, is convention.

---
### NAT in Practice: Why Private Subnets Still Need Internet Access?

A private subnet, by design, has no direct route to the public internet and is not reachable from it. But servers living inside that private subnet still frequently need outbound internet access. They need to download security patches, install software packages, or call external APIs.

This is exactly what a NAT Gateway solves. It lives in a public subnet and allows instances in a private subnet to initiate outbound connections to the internet, while still remaining completely unreachable from the internet itself. The NAT Gateway translates the private instance's address as outbound traffic passes through it and routes any response back to the correct originating instance. Critically, the internet cannot use this same path to initiate a brand new inbound connection toward that private instance. The door only swings one way.


- Private subnet instance wants to run: `dnf update -y`
```
Private instance  >  NAT Gateway (sits in the public subnet)  >  Internet
                                    |
                       Response comes back through
                       the same NAT Gateway
```
The instance still has no public IP address of its own and remains completely unreachable from the internet.

**Another Example:**
1. Your VM (`192.168.1.10`) sends a packet to `8.8.8.8:53` (Google DNS).
2. The packet reaches the router/NAT gateway.
3. The router replaces the source address with its own public IP (`203.0.113.5`) and records the mapping in a translation table.
4. Google receives the packet from `203.0.113.5` and responds to it.
5. The router receives the response, looks up the translation table, and forwards the packet to `192.168.1.10`.

> The private device is completely hidden from the outside. This is why a home router can connect dozens of devices using a single public IP.

**The three details that turn into tickets.** A NAT gateway lives in one availability zone; if that zone fails, private subnets in other zones that route through it lose outbound internet. Production designs place one NAT gateway per availability zone for this reason. A NAT gateway also bills per hour and per gigabyte processed, which makes it a surprisingly common line item on a cloud bill when a private subnet is pulling container images from the public internet on every deployment. And a NAT gateway is IPv4 only: the IPv6 equivalent is an egress only internet gateway, which provides the same one way property for IPv6 traffic.

---
### Special Purpose Addresses:

| Range             | Purpose                                                                               |
|-------------------|---------------------------------------------------------------------------------------|
| 127.0.0.0/8       | Loopback (localhost). `127.0.0.1` always refers to the local machine.                |
| 169.254.0.0/16    | Link-local. Auto-assigned when DHCP fails. In AWS, `169.254.169.254` is the instance metadata endpoint (IMDS). |
| 0.0.0.0/0         | Represents all addresses. Used in routing tables (default route) and firewall rules.  |
| 255.255.255.255   | Limited broadcast. Sent to all hosts on the local network.                            |
| 100.64.0.0/10     | Carrier grade NAT (RFC 6598). Also used by some cloud services internally.            |
| 192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24 | Reserved for documentation and examples. Safe to use in your notes and diagrams. |

Two of these deserve a sentence each. `0.0.0.0` means two different things depending on where it appears, and conflating them causes real confusion: in a routing table or a firewall rule it means "any address," while as a bind address it means "listen on every interface on this host." A service bound to `127.0.0.1` is reachable only from the machine itself, which is the single most common reason a correctly running service is unreachable from outside. Check it with `ss -tlnp` and read the local address column before touching the firewall.

And `169.254.169.254`, the AWS instance metadata endpoint, is a link local address that every EC2 instance can reach and no one else can. It serves the instance's own identity and, importantly, its IAM role credentials, which is why a server side request forgery bug in an application running on EC2 is so dangerous: it can be tricked into fetching those credentials. IMDSv2, which requires a session token obtained by a PUT request, exists specifically to close that hole, and it should be enforced on every instance you create.

---
### Common Addressing Mistakes

**Overlapping CIDR ranges.** 

If two networks that eventually need to be connected, two AWS VPCs, or a VPC and an on premises office network, are accidentally assigned the same or overlapping address ranges, you cannot route between them without extensive, painful renumbering. Planning your address ranges carefully before provisioning anything prevents this entirely.

**Subnets sized too small to grow.** 

A `/28` subnet holds only 16 addresses, and AWS itself reserves five of those for internal use, leaving just 11 usable. This fills up surprisingly fast once auto scaling groups and load balancers start consuming addresses from the same range. A reasonable default for most general purpose subnets is `/24`, which leaves comfortable room to grow without needing a redesign later.

**Forgetting that AWS reserves five IP addresses in every subnet.** 

The network address, the broadcast address, plus three additional addresses AWS itself reserves for internal VPC services. A `/24` subnet, which is normally 256 total addresses, only gives you 251 usable addresses in AWS specifically, not 254 like in a standard, non cloud network calculation.

**Using 10.0.0.0/16 for everything, in every environment.**

It is the default in every tutorial, which means it is also the default in the VPC your colleague built, the one the acquired company built, and the one your VPN vendor uses internally. The day you need to peer two of them, you cannot. Allocate deliberately: one distinct range per environment and per region, written down in one place before anything is provisioned.

---
# Part 2: Linux and Cloud Networking Reference

> This part is your existing working reference, kept in full. Everything that follows is preserved from your earlier notes, with corrections added as callouts where a command or file location has changed since it was written. Nothing has been removed.

---
## 3.11 Networking Concepts

**Network Communication Types**

**1. Unicast (One to One)**
 - One source; One destination
 - Use: Web browsing, SSH, email
 - Example: `192.168.1.10 → 192.168.1.20`

**2. Broadcast (One to All)**
 - One source; All devices in networks
 - Use: ARP, DHCP
 - Example: `192.168.1.10 → 255.255.255.255`

**3. Multicast (One to Many)**
 - One source; Multiple specific devices
 - Use: Video streaming, conferencing
 - IP Range: 224.0.0.0 – 239.255.255.255
 - Example: `192.168.1.10 → 239.255.0.1`

**4. Anycast (One to Nearest)**
 - One source; Nearest of multiple identical destinations
 - Use: DNS servers, CDNs

---

**IP Address**

A unique numerical label assigned to every device on an IP network for identification and routing.

**Types:**
- **IPv4 (Internet Protocol Version 4):**
    - Format: 32 bit, dotted decimal notation
    - Example: `192.168.1.1`
    - Limitation: ~4.3 billion addresses (exhausted)
    
- **IPv6 (Internet Protocol Version 6):**
    - Format: 128 bit, hexadecimal notation
    - Example: `2001:0db8:85a3::8a2e:0370:7334`
    - Virtually unlimited addresses

**IP Address Functions:**
- Host Identification:
 - Uniquely identifies each device
- Interface Addressing:
 - Identifies specific network interfaces
- Routing:
 - Enables packet delivery to the correct destinations

**IP Address Categories:**
- Public IP Address:
  - Globally routable on the Internet
  - Allocated by IANA; Regional Internet Registries (RIRs); ISPs
  - Required for direct Internet access
    
- Private IP Address(RFC 1918)
  - Used within local networks only
  - Not routable on the public Internet
  - Requires NAT (Network Address Translation) for Internet access
    
**- Examples:**
```
10.0.0.0/8        (10.0.0.0 - 10.255.255.255)     - Large organizations
172.16.0.0/12     (172.16.0.0 - 172.31.255.255)   - Medium organizations  
192.168.0.0/16    (192.168.0.0 - 192.168.255.255) - Home/small business
```
<img width="919" height="58" alt="Screenshot 2025-10-28 at 8 19 54 AM" src="https://github.com/user-attachments/assets/fc3d9426-8154-4f33-b20f-a4fe844cca79" />


**Default Gateway**

A router that sends data between different networks, such as from a local network (LAN) to the Internet. It often uses NAT to convert private IP addresses to public ones.

**Functions:**
  - Routes traffic from the local network to external networks (LAN; Internet)
  - Typically performs NAT (Network Address Translation)
  - Serves as the "exit point" from the local network

**Example:**
  - Local device: 192.168.1.100
  - Gateway: 192.168.1.1
  - Internet destination: routed through the gateway

<img width="886" height="202" alt="Screenshot 2025-10-28 at 8 24 17 AM" src="https://github.com/user-attachments/assets/9cdb072c-cd1d-47aa-9dc2-f380c1f823dc" />


**DNS (Domain Name System)**

It’s what helps your computer find websites by turning names like example.com into the numerical addresses computers use to connect, kind of like looking up a contact’s phone number to make a call.

**DNS Components:**
 - Recursive resolver:
     - First point of contact for DNS queries
     - Caches responses for performance
     - Examples:
         - 8.8.8.8 (Google)
         - 1.1.1.1 (Cloudflare)
           
 - Authoritative nameserver:
     - Holds the official DNS records for domains
     - Provides definitive answers for specific domains
     - Managed by domain owners/hosting providers
 
 - DNS Resolution Process:
`1. Query recursive resolver → 2. Check cache → 3. Query root servers → 4. Query TLD servers → 5. Query authoritative servers → 6. Return IP address`

<img width="778" height="149" alt="Screenshot 2025-10-28 at 8 25 59 AM" src="https://github.com/user-attachments/assets/732c4d65-2791-4bde-b9ca-83d9e7833d66" />

---
## 3.12 IPv4 Classful Addressing & Special Ranges

While modern networks use CIDR (Classless Inter Domain Routing), understanding historical classful addressing helps interpret legacy systems and documentation.

**Unicast Address Classes (A, B, C):**

These were used for assigning addresses to hosts on the public internet and have corresponding private address blocks defined in RFC 1918.

| **Class** | **First Octet** | **   Public Range        ** | **      Private Range     **  | **Default Mask** | **CIDR** |
| :-------: | :-------------: | :-------------------------: | :--------------------------:  | :--------------: | :------: |
|   **A**   |      1–126      |  1.0.0.0 – 126.255.255.255  |  10.0.0.0 – 10.255.255.255    |    255.0.0.0     |   /8     |
|   **B**   |     128–191     | 128.0.0.0 – 191.255.255.255 | 172.16.0.0 – 172.31.255.255   |   255.255.0.0    |   /16    |
|   **C**   |     192–223     | 192.0.0.0 – 223.255.255.255 | 192.168.0.0 – 192.168.255.255 |  255.255.255.0   |   /24    |

**Special Use Address Classes (D, E) & Notable Reservations**:

These address ranges are reserved for specific protocols and are not used for general host addressing.

| **Class** | **First Octet** | **Address Range** | **Purpose** | **Examples** |
| :-------: | :-------------: | :---------------: | :---------: | :--------------- |
|   **D**   |     224–239     | 224.0.0.0 – 239.255.255.255 | **Multicast** | 224.0.0.1 (All hosts), 224.0.0.2 (All routers) |
|   **E**   |     240–255     | 240.0.0.0 – 255.255.255.255 | **Reserved / Experimental** | 255.255.255.255 (Limited broadcast) |
|  **N/A**  |      **127**    |   127.0.0.0/8     | **Loopback** | 127.0.0.1 (Localhost) |
|  **N/A**  |     **169.254** |   169.254.0.0/16  | **APIPA** | 169.254.x.x (Automatic Private IP Addressing) |
|  **N/A**  |    **192.0.2**  |   192.0.2.0/24    | **TEST NET** | 192.0.2.1 (Documentation & examples) |

Other reserved ranges:
- 198.51.100.0/24, 203.0.113.0/24 (documentation)
- 100.64.0.0/10 (Carrier Grade NAT)
- 255.255.255.255 (Local broadcast)

---
## 3.13 Linux Networking Commands

**Interface Configuration**

| Purpose | Command | Description |
|---------|---------|-------------|
| **Show all IP addresses** | `hostname -I` | Linux specific, shows all IPs |
| **Legacy interface info** | `ifconfig` | Deprecated (net tools package) |
| **Modern interface info** | `ip addr show`<br>`ip a` | Preferred modern method |
| **Interface status** | `ip link show` | Shows link layer status |
| **Bring interface up/down** | `ip link set eth0 up`<br>`ip link set eth0 down` | Replace `eth0` with interface name |
| **Add IP address** | `ip addr add 192.168.1.100/24 dev eth0` | Temporary (lost on reboot) |
| **Remove IP address** | `ip addr del 192.168.1.100/24 dev eth0` | Remove specific IP |
| **Flush all IPs** | `ip addr flush dev eth0` | Remove all IPs from interface |


**Routing & Gateway**

| Purpose | Command | Description |
|---------|---------|-------------|
| **Show routing table** | `ip route show`<br>`ip route` | Modern replacement |
| **Legacy routing table** | `route -n` | Deprecated |
| **Add default gateway** | `ip route add default via 192.168.1.1` | Set default route |
| **Add specific route** | `ip route add 10.0.0.0/8 via 192.168.1.1` | Add network route |
| **Delete route** | `ip route del 10.0.0.0/8` | Remove specific route |
| **Flush routing table** | `ip route flush all` | Clear all routes |


**DNS & Name Resolution**

| Purpose | Command | Description |
|---------|---------|-------------|
| **Show DNS servers** | `cat /etc/resolv.conf` | May be managed by NetworkManager |
| **Test DNS resolution** | `dig example.com A`<br>`dig +short example.com` | Detailed/short output |
| **Simple DNS lookup** | `nslookup example.com` | Legacy but simple |
| **Host lookup** | `host example.com` | Basic DNS query |
| **Flush DNS cache (systemd)** | `resolvectl flush-caches` | systemd-resolved |
| **Flush DNS cache (NetworkManager)** | `sudo systemctl restart NetworkManager` | Alternative method |

> **Corrected:** the old `systemd-resolve --flush-caches` form still appears in most tutorials. The binary was renamed to `resolvectl` in systemd 239 (2018) and `systemd-resolve` survives only as a deprecated symlink. Use `resolvectl flush-caches` and `resolvectl status`. On Debian and Ubuntu, `resolvectl` lives in the `systemd-resolved` package, which is not always installed.


**Network Connectivity Testing**

| Purpose | Command | Description |
|---------|---------|-------------|
| **Test reachability** | `ping 8.8.8.8`<br>`ping -c 4 8.8.8.8` | Continuous/limited pings |
| **Trace path** | `traceroute example.com` | Default UDP mode usually works unprivileged; ICMP mode (`-I`) needs root or `cap_net_raw` |
| **Rootless trace** | `tracepath example.com` | No root required |
| **Continuous trace** | `mtr example.com` | Combines ping and traceroute, shows per hop loss over time |
| **HTTP test** | `curl -I http://example.com` | Headers only |
| **Verbose HTTP** | `curl -v http://example.com` | Detailed connection info |
| **Download test** | `wget http://example.com/file` | Download file |


**Network Statistics & Monitoring**

| Purpose | Command | Description |
|---------|---------|-------------|
| **Legacy listening ports** | `netstat -tulnp` | net tools package |
| **Modern listening ports** | `ss -tulnp` | Faster, iproute2 package |
| **All connections** | `ss -tunap` | All TCP/UDP connections |
| **Interface statistics** | `ip -s link` | Show interface statistics |
| **Network statistics** | `netstat -i` | Interface table |
| **ARP table** | `ip neigh show` | Modern ARP table |
| **Legacy ARP** | `arp -n` | Deprecated ARP table |


**Troubleshooting & Advanced**

| Purpose | Command | Description |
|---------|---------|-------------|
| **Check network manager** | `nmcli device status` | NetworkManager status |
| **Restart networking** | `systemctl restart NetworkManager` | Redhat/Fedora/CentOS |
| **Restart networking** | `systemctl restart networking` | Debian/Ubuntu (ifupdown) |
| **Scan ports** | `nmap -sS 192.168.1.0/24` | Network discovery |
| **Check bandwidth** | `iftop` | Real-time bandwidth (install separately) |
| **Monitor traffic** | `tcpdump -i eth0` | Packet capture |
| **Follow system logs** | `journalctl -f -u NetworkManager` | NetworkManager logs |


**Configuration Files**

| File | Purpose |
|------|---------|
| `/etc/netplan/` | Ubuntu network configuration (YAML) |
| `/etc/network/interfaces` | Debian interface configuration |
| `/etc/sysconfig/network-scripts/` | RedHat/CentOS interface configs (**deprecated**, see note below) |
| `/etc/NetworkManager/system-connections/` | RHEL 9+, Fedora, Rocky 9+: NetworkManager keyfiles (`.nmconnection`), the current default |
| `/etc/resolv.conf` | DNS resolver configuration |
| `/etc/hosts` | Local hostname to IP mappings |


**Examples: Essential Commands**

**System overview:**
```bash
ip a                        # Show IP addresses
```
<img width="880" height="249" alt="Screenshot 2025-10-28 at 8 59 18 AM" src="https://github.com/user-attachments/assets/f21d086d-53c7-4ffa-bee5-0a7f0b790116" />

```bash
ip route                    # Show routing table
```

```bash
ss -tulnp                   # Show listening ports
```

<img width="852" height="199" alt="Screenshot 2025-10-28 at 9 01 26 AM" src="https://github.com/user-attachments/assets/0c9b0e56-61d5-4664-bc76-d52f9f2b12ea" />


**Connectivity testing**
```
ping 8.8.8.8           # Basic connectivity
```
<img width="831" height="166" alt="Screenshot 2025-10-28 at 9 04 01 AM" src="https://github.com/user-attachments/assets/3d7c8ea0-e0d0-4d4b-b404-b374e948b121" />

```
dig redhat.com         # DNS resolution test
```
<img width="846" height="631" alt="Screenshot 2025-10-28 at 9 05 56 AM" src="https://github.com/user-attachments/assets/276e963e-ed1d-4d64-9ddb-ad31956c2836" />

<img width="837" height="341" alt="Screenshot 2025-10-28 at 9 05 35 AM" src="https://github.com/user-attachments/assets/4f73fc82-7fde-4dc8-90af-70d747b7de08" />

```
curl -I example.com    # HTTP service test
```

<img width="995" height="190" alt="Screenshot 2025-10-28 at 9 08 13 AM" src="https://github.com/user-attachments/assets/950ae728-2bd0-4852-9b7d-4f1c59b9d70f" />


**Temporary configuration**
```
ip addr add 192.168.xxx.xxx/xx dev exxxx                 # Add IP
ip link set exxxx up                                     # Enable interface
ip route add default via 192.168.xxx.xx                  # Add gateway
```

Example:

<img width="918" height="569" alt="Screenshot 2025-10-28 at 9 31 30 AM" src="https://github.com/user-attachments/assets/6de30bea-f948-451e-afc2-6f04983588e9" />

---
## 3.14 Network Interface Configuration

**Using `ifconfig` (Legacy, so Avoid in New Systems)**
```bash
ifconfig                                              # List all interfaces
ifconfig eth0                                         # Show specific interface
ifconfig eth0 up                                      # Bring interface up
ifconfig eth0 down                                    # Bring interface down
ifconfig eth0 192.168.1.100 netmask 255.255.255.0     # Set IP and netmask
ifconfig eth0:0 192.168.1.101/24                      # Add alias interface
```
> Part of the deprecated net-tools package. Not recommended for new scripts.

**Using `ip` command (Modern and Preferred)**
```bash
# Interface management
ip link show                                        # Show all interfaces
ip link set eth0 up                                 # Bring interface up
ip link set eth0 down                               # Bring interface down
```
<img width="877" height="533" alt="Screenshot 2026-01-18 at 8 31 55 AM" src="https://github.com/user-attachments/assets/1e20fc58-f43c-4ae7-adcc-c87a60aaf0da" />

```bash
# IP address management
ip addr show                                        # Show all IP addresses
ip addr add 192.168.1.100/24 dev eth0               # Add IP address
ip addr del 192.168.1.100/24 dev eth0               # Remove IP address
ip addr flush dev eth0                              # Remove all IPs from interface
```
```bash
# Brief output formats
ip -br link show                                    # Brief interface status
ip -br addr show                                    # Brief IP address summary
```

Note:
 - `ip` commands are temporary and don't persist after reboot.
 - Always use `ip` for scripting and automation unless supporting legacy systems.

---
## 3.15 Configuring IP, Gateway, DNS (Persistent Configuration)

**Method 1: NetworkManager CLI (nmcli)**

- View current connections
```bash
nmcli connection show
nmcli device status
```
<img width="868" height="209" alt="Screenshot 2026-01-18 at 8 37 24 AM" src="https://github.com/user-attachments/assets/2aa6fac5-40d4-43fc-9cfb-205f100b3b02" />

- Configure static IP
```bash
nmcli connection modify "eth0" ipv4.addresses "192.168.1.100/24"
nmcli connection modify "eth0" ipv4.gateway "192.168.1.1"
nmcli connection modify "eth0" ipv4.dns "8.8.8.8,8.8.4.4"
nmcli connection modify "eth0" ipv4.method manual
```

- Apply changes and reload all connections
```bash
nmcli connection up "eth0"
nmcli connection reload 
```

- Create a new connection
```bash
nmcli connection add type ethernet con-name "static-eth0" ifname eth0 \
  ipv4.addresses "192.168.1.100/24" \
  ipv4.gateway "192.168.1.1" \
  ipv4.dns "8.8.8.8" \
  ipv4.method manual
```
<img width="880" height="282" alt="Screenshot 2026-01-18 at 8 39 14 AM" src="https://github.com/user-attachments/assets/3b3c9cd4-4720-4fa7-a1e4-15ad86b77b22" />

<img width="809" height="140" alt="Screenshot 2026-01-18 at 8 47 12 AM" src="https://github.com/user-attachments/assets/87c60139-17cf-406d-b4c6-042cd0e9264e" />


<img width="677" height="9" alt="Screenshot 2026-01-18 at 8 47 32 AM" src="https://github.com/user-attachments/assets/44cd63ff-be04-4e3e-8766-8e250eb38f03" />


<img width="882" height="209" alt="Screenshot 2026-01-18 at 8 47 47 AM" src="https://github.com/user-attachments/assets/48ce95eb-3516-4a59-bc64-371dbce05fbf" />


<img width="873" height="241" alt="Screenshot 2026-01-18 at 8 48 12 AM" src="https://github.com/user-attachments/assets/d30ca082-a59b-445e-8ab6-34ed5002cfbb" />


**Method 2: Netplan (Ubuntu 18.04+)**

- File: `/etc/netplan/01-netcfg.yaml`
  
```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      addresses:
        - 192.168.1.100/24
      routes:
        - to: default
          via: 192.168.1.1
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
```

Apply netplan configuration:
```bash
netplan generate
netplan apply
```

> **Outdated, kept for reference:** Method 3 below is the `ifcfg` format. Since RHEL 9, Fedora 36, and Rocky 9, NetworkManager writes keyfiles to `/etc/NetworkManager/system-connections/` by default and the `ifcfg` format is deprecated. RHEL 10 and Rocky Linux 10 remove `network-scripts` and `ifcfg` support entirely. Read Method 3 to understand systems you inherit; write new configuration with `nmcli` or keyfiles. Existing profiles can be converted with `nmcli connection migrate`.

**Method 3: Legacy System Configuration (RHEL/CentOS 7 and earlier)**

 - File: `/etc/sysconfig/network-scripts/ifcfg-eth0`
   
```ini
DEVICE=eth0
BOOTPROTO=static
ONBOOT=yes
IPADDR=192.168.1.100
NETMASK=255.255.255.0
GATEWAY=192.168.1.1
DNS1=8.8.8.8
DNS2=8.8.4.4
```

Restart service
```bash
systemctl restart network
```

**Method 4: systemd-networkd (Modern minimal distributions)**

 - File: `/etc/systemd/network/10-eth0.network`
   
```ini
[Match]
Name=eth0

[Network]
Address=192.168.1.100/24
Gateway=192.168.1.1
DNS=8.8.8.8
DNS=8.8.4.4
```

Enable and start:
```bash
systemctl enable systemd-networkd
systemctl start systemd-networkd
```

**NetworkManager Example (RedHat/CentOS 9+)**

 - Generate UUID: `uuidgen`
 - File: `cd /etc/NetworkManager/system-connections`
          
   
```ini
[connection]
id=static-enp
uuid=45882b4c-314c-11f0-bb1a-5254000dc1ee
type=ethernet
interface-name=enp0s1
autoconnect=true

[ipv4]
method=manual
addresses=192.168.100.199/24;
gateway=192.168.100.1
dns=192.168.100.1

[ipv6]
method=ignore
```
Apply:
```bash
nmcli connection reload
nmcli connection show
nmcli connection up static-enp
ip addr show enp0s1
```

Finding DNS, Gateway:

<img width="753" height="199" alt="Screenshot 2025-10-28 at 11 23 50 AM" src="https://github.com/user-attachments/assets/a830d7da-cc7c-47ec-9519-c3bc8edc77c8" />

Generating UUID:

<img width="778" height="60" alt="Screenshot 2025-10-28 at 11 25 06 AM" src="https://github.com/user-attachments/assets/9dee570c-5b83-4cfe-9ef4-7c3da29cb79f" />

Editing file: `vim xxxxxxx.nmconnection`
<img width="780" height="375" alt="Screenshot 2025-10-28 at 11 32 34 AM" src="https://github.com/user-attachments/assets/ab110e94-4c6e-44b8-aca1-63416d236ea4" />

<img width="708" height="65" alt="Screenshot 2025-10-28 at 11 37 54 AM" src="https://github.com/user-attachments/assets/196a14dc-d3b9-458e-b251-0d79f42fa60e" />

<img width="1014" height="259" alt="Screenshot 2025-10-28 at 11 35 19 AM" src="https://github.com/user-attachments/assets/9dff65bc-f515-4b0b-8923-70388e0ff4e5" />

<img width="1035" height="166" alt="Screenshot 2025-10-28 at 11 35 50 AM" src="https://github.com/user-attachments/assets/05786fb9-dce4-4cfa-a9b2-8c92575756fa" />

---
## 3.16 DNS Details

Viewing DNS Configuration:
```bash
cat /etc/resolv.conf                    # Current DNS resolvers
resolvectl status                       # systemd resolved status
nmcli device show eth0 | grep DNS       # NetworkManager DNS
```

Common DNS Resolvers:
```
nameserver 8.8.8.8          # Google DNS
nameserver 8.8.4.4          # Google DNS secondary
nameserver 1.1.1.1          # Cloudflare DNS
nameserver 192.168.1.1      # Local router/gateway
```
> Use multiple DNS resolvers for redundancy. Monitor DNS query latency.


- Managing DNS Cache:
 - systemd-resolved
```bash
resolvectl flush-caches          # current form
resolvectl statistics            # confirm the cache is empty
systemctl restart systemd-resolved
```
> `systemd-resolve --flush-caches` is the pre systemd 239 spelling and is deprecated. It still works on older systems only.
 - Alternative methods
```bash
sudo systemctl restart NetworkManager    # Restart NetworkManager
```

- Local Hostname Resolution:
 - File: `/etc/hosts`
```
127.0.0.1   localhost localhost.localdomain
192.168.1.10  server1.example.com server1
192.168.1.20  server2.example.com server2
```

<img width="763" height="161" alt="Screenshot 2025-10-28 at 12 40 37 PM" src="https://github.com/user-attachments/assets/6b1ba758-c1ed-48c1-8e17-9a78eb8d1c2d" />


---
## 3.17 Routing & Gateway

Viewing Routing Table:
```bash
ip route show              # Modern command
route -n                   # Legacy command
ip route get 8.8.8.8       # Show route for specific destination
```

<img width="782" height="78" alt="Screenshot 2025-10-28 at 12 42 39 PM" src="https://github.com/user-attachments/assets/3e94eae5-4189-43ba-bb72-c6978120977d" />

**Managing Routes:**
 
Example:
```bash
# Add default gateway (temporary)
ip route add default via 192.168.1.1 dev eth0

# Add specific network route (temporary)
ip route add 10.0.0.0/8 via 192.168.1.254 dev eth0

# Delete routes
ip route del default
ip route del 10.0.0.0/8

# Persistent routing (RHEL/CentOS)
echo "10.0.0.0/8 via 192.168.1.254 dev eth0" >> /etc/sysconfig/network-scripts/route-eth0
```

---

## 3.18 Network Troubleshooting


| Symptom | Diagnostic Steps | Possible Cause | Resolution |
|---------|------------------|----------------|------------|
| **No connectivity (ping fails)** | `ip addr show`<br>`ip link show`<br>`ping <gateway>`<br>`ethtool <interface>` | Interface down<br>Wrong IP/subnet<br>Cable disconnected<br>Driver issues | `ip link set <iface> up`<br>Correct IP configuration<br>Check physical connections<br>Update drivers |
| **DNS fails, IP works** | `ping 8.8.8.8` (works)<br>`ping example.com` (fails)<br>`nslookup example.com`<br>`cat /etc/resolv.conf` | DNS server misconfigured<br>DNS service down<br>Firewall blocking DNS | Update DNS in NetworkManager<br>Check `systemd-resolved` status<br>Adjust firewall rules |
| **Cannot reach outside subnet** | `ip route show`<br>`ping <gateway>`<br>`traceroute 8.8.8.8` | Missing default route<br>Gateway unreachable<br>Wrong subnet mask | `ip route add default via <gateway>`<br>Verify gateway IP<br>Check subnet configuration |
| **Slow DNS resolution** | `dig +trace example.com`<br>`time nslookup example.com`<br>`resolvectl statistics` | DNS server latency<br>DNS cache issues<br>Network congestion | Change to faster resolvers<br>Flush DNS cache<br>Use local caching resolver |
| **Port unreachable** | `ss -tulnp \| grep :port`<br>`sudo firewall-cmd --list-all`<br>`systemctl status <service>` | Service not listening<br>Firewall blocking<br>Wrong bind address | Start/restart service<br>Add firewall exception<br>Check service configuration |
| **Random IP after boot (169.254.x.x)** | `ip addr show`<br>`journalctl -u NetworkManager`<br>`dhclient -v` | DHCP failure<br>Network cable issue<br>Switch port blocked | Check DHCP server<br>Verify physical connectivity<br>Manual static IP assignment |
| **Duplicate IP conflict** | `arping -c 3 <IP>`<br>`journalctl \| grep -i arp`<br>`ip neigh show` | Multiple devices with same IP<br>Static IP in DHCP range<br>Rogue DHCP server | Assign unique static IP<br>Exclude static IPs from DHCP range<br>Network segmentation |


**Advanced Diagnostic Commands**

**Connectivity Testing Sequence**
```bash
ip -br addr show                        # Check local interface

ping -c 3 <gateway_ip>                  # Test the local network

ping -c 3 8.8.8.8                       # Test internet

nslookup google.com                     # Test DNS
dig google.com                          # Test DNS

telnet <server> <port>                  # Check the specific service
nc -zv <server> <port>                  # Check the specific service
```

**Network Service Status**
- Check relevant services
```bash
systemctl status NetworkManager
systemctl status systemd-resolved
systemctl status firewalld
systemctl status iptables

sudo systemctl restart NetworkManager                  # Restart if needed
```

**Packet Capture & Analysis**
```bash
# Basic packet capture
tcpdump -i eth0 -n host 8.8.8.8

# Capture DNS queries
tcpdump -i eth0 -n port 53

# Save to file for analysis
tcpdump -i eth0 -w capture.pcap
```

---

- Restart networking (RHEL/CentOS)
```bash
sudo systemctl restart NetworkManager
```
 - Restart networking (Ubuntu with netplan)
```bash
sudo netplan apply
```
 - Flush all temporary configurations
```bash
sudo ip addr flush dev eth0
sudo ip route flush all
```

**DNS Troubleshooting**
 - Test different DNS servers
```bash
nslookup google.com 8.8.8.8
nslookup google.com 1.1.1.1
```
 - Flush DNS cache (systemd)
```bash
sudo resolvectl flush-caches
```
 - Check DNS resolution path
```bash
dig +trace google.com
```

---

## 3.19 Cloud Networking Basics (AWS, Azure, GCP)

**AWS VPC & Security Groups**

**VPC Creation & Subnetting:**
```bash
aws ec2 create-vpc --cidr-block 10.0.0.0/16
aws ec2 create-subnet --vpc-id vpc-1234abcd --cidr-block 10.0.1.0/24
```

**Security Group Rules:**
```bash
aws ec2 describe-security-groups
aws ec2 authorize-security-group-ingress --group-id sg-12345678 --protocol tcp --port 22 --cidr 203.0.113.0/24
aws ec2 revoke-security-group-ingress --group-id sg-12345678 --protocol tcp --port 22 --cidr 0.0.0.0/0
```

>Restrict security group rules by CIDR. Avoid using wide-open routes (0.0.0.0/0) unless absolutely required for testing purposes.


**Azure Networking & Network Security Groups (NSG)**

**Create NSG Rule:**
```bash
az network nsg rule create \
  --resource-group myResourceGroup \
  --nsg-name myNSG \
  --name AllowSSH \
  --protocol tcp \
  --direction inbound \
  --priority 1000 \
  --source-address-prefixes '203.0.113.0/24' \
  --destination-port-ranges 22 \
  --access Allow
```

**List NSG Rules:**
```bash
az network nsg rule list --resource-group myResourceGroup --nsg-name myNSG
```
> Always set a specific source address/range, avoid '*' in production.


**GCP VPC & Firewall Rules**

**Create Firewall Rule:**
```bash
gcloud compute firewall-rules create allow-ssh \
  --direction=INGRESS \
  --priority=1000 \
  --network=default \
  --action=ALLOW \
  --rules=tcp:22 \
  --source-ranges=203.0.113.0/24
```

**List Firewall Rules:**
```bash
gcloud compute firewall-rules list
```
> Use restrictive source ranges. Audit rules regularly.


---
## 3.20 Container & Kubernetes Networking

**Docker**

- Expose container port:
```bash
docker run -d -p 8080:8080 myapp
```

- Verification:
```bash
curl localhost:8080
ss -tulnp | grep 8080
```

**Kubernetes**

- Simple NetworkPolicy example:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-nginx
spec:
  podSelector:
    matchLabels:
      app: nginx
  ingress:
    - from:
        - ipBlock:
            cidr: 10.0.0.0/24
```

- Verification:
```bash
kubectl describe networkpolicy allow-nginx
```
> Use least privilege policies only allow required ports and traffic between containers/pods.

---
## 3.21 Infrastructure as Code (IaC) for Networking

**Example: Terraform AWS Security Group**

```hcl
resource "aws_security_group" "web" {
  name        = "web-sg"
  description = "Allow HTTP and SSH"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["203.0.113.0/24"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

- Verification:
```bash
terraform plan
terraform apply
aws ec2 describe-security-groups
```

**Example: Terraform Azure NSG**
```hcl
resource "azurerm_network_security_group" "example" {
  name                = "example-nsg"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name

  security_rule {
    name                       = "AllowSSH"
    priority                   = 1000
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "203.0.113.0/24"
    destination_address_prefix = "*"
  }
}
```

- Verification:
```bash
terraform plan
terraform apply
az network nsg rule list --resource-group <resource-group> --nsg-name example-nsg
```

**Example: Terraform GCP Firewall Rule**
```hcl
resource "google_compute_firewall" "allow_ssh" {
  name    = "allow-ssh"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["203.0.113.0/24"]
  direction     = "INGRESS"
  priority      = 1000
}
```

- Verification:
```bash
terraform plan
terraform apply
gcloud compute firewall-rules list
```
> Store all networking resources in version control and review via PR before deployment.

---

## 3.22 Monitoring & Troubleshooting

**Linux**

- **Ping:** `ping 8.8.8.8`
- **Traceroute:** `traceroute example.com`
- **Socket state:** `ss -tulnp`
- **Firewall check:** `firewall-cmd --list-all`
- **System logs:** `journalctl -u NetworkManager`, `dmesg | grep eth`

**Cloud**

- **AWS CloudWatch:** Monitor VPC flow logs.
- **Azure Monitor:** NSG flow logs.
- **GCP Logging:** VPC flow logs.

> Aggregate logs and alerts centrally (e.g., ELK, Datadog, Splunk).

---
## 3.23 Cleanup & Reversion

- If you added a temporary IP:
```bash
ip addr del 192.168.1.100/24 dev eth0
```

- If you opened a firewall port (firewalld) for testing:
```bash
firewall-cmd --zone=public --remove-port=8080/tcp --permanent
firewall-cmd --reload
```

- If you modified a NetworkManager connection incorrectly:
```bash
nmcli connection reload
nmcli connection modify eth0 ipv4.method auto
nmcli connection up eth0
```

---
## 3.24 Legacy vs Modern

| Function | Legacy Tool(s) | Modern Preferred |
|----------|----------------|------------------|
| Interface management | `ifconfig` | `ip addr`, `ip link` |
| Routes | `route` | `ip route` |
| Sockets | `netstat` | `ss` |
| Firewall | `iptables` | `firewalld` (nftables backend since RHEL 8); inspect the real ruleset with `nft list ruleset` |
| DNS Query | `nslookup` | `dig`, `getent hosts` |
| DNS cache flush | `systemd-resolve --flush-caches` | `resolvectl flush-caches` |
| Interface config file | `ifcfg-*` in `/etc/sysconfig/network-scripts/` | `.nmconnection` keyfiles in `/etc/NetworkManager/system-connections/` |
| Traceroute | `traceroute` | `mtr` for continuous per hop loss |


---
## 3.25 References

- RFC 1918 – Address Allocation for Private Internets
- RFC 5735 / 6890 – Special Use IPv4 Addresses
- `man ip`, `man nmcli`, `man firewalld.richlanguage`
- Linux Advanced Routing & Traffic Control HOWTO
- [AWS VPC Documentation](https://docs.aws.amazon.com/vpc/latest/userguide/)
- [Azure VNet Documentation](https://learn.microsoft.com/en-us/azure/virtual-network/)
- [GCP VPC Documentation](https://cloud.google.com/vpc/docs)
- [Docker Networking](https://docs.docker.com/network/)
- [Kubernetes Networking](https://kubernetes.io/docs/concepts/cluster-administration/networking/)
- [Terraform Networking](https://developer.hashicorp.com/terraform/tutorials/aws/aws-networking)
- [RHEL 9: goodbye ifcfg files, hello keyfiles (Red Hat)](https://www.redhat.com/en/blog/rhel-9-networking-say-goodbye-ifcfg-files-and-hello-keyfiles)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
- [OWASP Transport Layer Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Security_Cheat_Sheet.html)
- [Nginx ngx_http_v2_module (the `http2` directive)](https://nginx.org/en/docs/http/ngx_http_v2_module.html)
- [AWS: VPC subnet sizing and reserved addresses](https://docs.aws.amazon.com/vpc/latest/userguide/subnet-sizing.html)
- RFC 8446 (TLS 1.3), RFC 6598 (Carrier Grade NAT range)

---
# Part 3: Labs

> **Before you start:** take a snapshot of every VM you touch in these labs. Lab 3A deliberately breaks networking on a machine you are connected to, and the fastest recovery from a mistake is a rollback, not a rescue. If you are working over SSH, keep a console session open through your hypervisor as well. Deleting a default route over the same SSH connection you are relying on is a lesson everyone learns exactly once.

---
## Lab 3A: Diagnose a Broken DNS and Routing Scenario

**Goal:** work a broken system from Layer 3 upward using `ping`, `traceroute`, `ip route`, `ss`, and `dig`, and produce a written record of what each command told you and why you ran it in that order.

**Machine:** one RHEL 9, Rocky 9, or Fedora VM with working networking and a snapshot taken.

---
### Step 1: Record the healthy baseline

You cannot recognize broken if you never looked at working. Capture this first and keep it.

```bash
ip -br addr show
ip route show
resolvectl status | head -20
cat /etc/resolv.conf
ping -c 3 8.8.8.8
dig +short redhat.com
```

Save the output. It is your reference for the rest of the lab.

---
### Step 2: Break it

Run the breakage script below, or have a partner run it while you look away. Each fault produces a different symptom, and the point of the lab is to distinguish them.

```bash
#!/usr/bin/env bash
# break-network.sh  -- run with sudo. Snapshot first.
set -x

# Fault 1: remove the default route
ip route del default

# Fault 2: point the resolver at an address that will never answer
#   192.0.2.53 is in the TEST-NET-1 documentation range and is guaranteed dead
nmcli connection modify "$(nmcli -g NAME connection show --active | head -1)" ipv4.ignore-auto-dns yes
nmcli connection modify "$(nmcli -g NAME connection show --active | head -1)" ipv4.dns "192.0.2.53"
nmcli connection up "$(nmcli -g NAME connection show --active | head -1)"

# Fault 3: stop a service that should be listening, and block its port
systemctl stop nginx 2>/dev/null
firewall-cmd --permanent --remove-service=http 2>/dev/null
firewall-cmd --reload
```

Fault 1 is a Layer 3 problem. Fault 2 is a Layer 7 name resolution problem that will look like a Layer 3 problem if you are careless. Fault 3 is a Layer 4 problem. They will overlap and confuse each other, which is the entire point, because that is what a real incident feels like.

---
### Step 3: Diagnose bottom to top

Work the layers in order. Do not skip a step because you think you already know the answer.

**Layer 3, question one: does this host have an address at all?**

```bash
ip -br addr show
```

A `169.254.x.x` address here means DHCP failed and nothing else you do will work. An address in the range you expect means the interface is up and configured, and you can move on.

**Layer 3, question two: can I reach my own gateway?**

```bash
ip route show                  # what does this host think the gateway is?
ping -c 3 <gateway_ip>         # can it be reached?
```

This is where Fault 1 announces itself. With the default route deleted, `ip route show` has no `default` line at all. Pinging the gateway still works, because it is on the local link and needs no route. That combination, local link fine but no default route, is the signature.

**Layer 3, question three: can I reach the internet by address, ignoring names entirely?**

```bash
ping -c 3 8.8.8.8
```

Use an IP address, never a hostname, at this stage. If you ping a name here and it fails, you have learned nothing: the failure could be name resolution or reachability, and you have merged two questions into one. With Fault 1 in place this returns `Network is unreachable`, and the message is the kernel telling you plainly that it has no route, not that the far end is down.

**Layer 3, question four: where does the packet actually die?**

```bash
traceroute -n 8.8.8.8
```

Run this after you restore the default route. Every hop that answers narrows the search. A trace that dies at the first hop is a local or gateway problem. A trace that gets several hops out and then shows only asterisks usually means the path is fine and something further along is not answering ICMP, which is common and often harmless. Use `-n` to skip reverse DNS lookups, so a broken resolver does not make a routing tool hang.

**Fix Fault 1, then continue.**

```bash
sudo ip route add default via <gateway_ip> dev <interface>
ping -c 3 8.8.8.8        # should now succeed
```

**Layer 7, question five: does name resolution work, separately from reachability?**

```bash
ping -c 3 8.8.8.8         # succeeds
ping -c 3 redhat.com      # fails
```

That pair of results is the classic DNS signature and you should learn to recognize it instantly: the network is fine, names are not. Confirm it with `dig`, which asks the resolution question alone:

```bash
dig redhat.com                    # hangs, then times out
dig @1.1.1.1 redhat.com           # works
resolvectl status                 # shows the configured resolver: 192.0.2.53
cat /etc/resolv.conf
```

The moment `dig @1.1.1.1` succeeds while plain `dig` times out, the fault is located: DNS resolution works, but the resolver this host has been told to use does not answer. That is Fault 2, and you found it by changing exactly one variable.

**Fix Fault 2.**

```bash
CON=$(nmcli -g NAME connection show --active | head -1)
sudo nmcli connection modify "$CON" ipv4.ignore-auto-dns no
sudo nmcli connection modify "$CON" ipv4.dns ""
sudo nmcli connection up "$CON"
resolvectl flush-caches
dig +short redhat.com             # should now answer
```

**Layer 4, question six: is the service listening, and is the port reachable?**

```bash
curl -I http://localhost           # connection refused
ss -tlnp | grep ':80'              # nothing listening
```

`Connection refused` on localhost is unambiguous: nothing is bound to that port on this machine. This is not a firewall problem, because a firewall drop produces a hang, not an instant refusal. Start the service and look again:

```bash
sudo systemctl start nginx
ss -tlnp | grep ':80'              # now listening
curl -I http://localhost           # 200 OK from the machine itself
```

Now test from another machine. It hangs and eventually times out. The service is listening, localhost works, the remote client times out: that is a firewall, every time.

```bash
sudo firewall-cmd --list-all       # http is absent from the services list
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload
```

Test again from the other machine. It answers.

---
### Step 4: The deliverable

Write up the incident as a table. This is the actual output of the lab, and it is the habit that transfers to your job.

| # | Command run | Why I ran it at this point | What it told me | What it ruled out |
|---|---|---|---|---|
| 1 | `ip -br addr show` | Confirm the host has a valid address before anything else | Address present, interface up | DHCP failure, interface down |
| 2 | `ip route show` | The next thing above an address is a route | No `default` route present | ... |
| 3 | ... | ... | ... | ... |

Two questions to answer in prose at the end, in a few sentences each:

1. Fault 2 (a dead resolver) and Fault 1 (a missing default route) both make `ping redhat.com` fail. Which single command distinguishes them, and why?
2. You saw both `Connection refused` and a hanging timeout in this lab. Explain what each one tells you about where the packet went, and why that difference is the fastest thing you can learn in the first thirty seconds of an incident.

---
## Lab 3B: Subnetting and a Three Tier VPC Design (On Paper)

**Goal:** do the arithmetic by hand, then design an address plan you will build for real in Module 8. No VMs, no cloud account. A pen is sufficient.

---
### Part 1: Given 192.168.1.0/26

Calculate, showing your working:

1. The subnet mask in dotted decimal
2. The network address
3. The broadcast address
4. The usable host range
5. The number of usable hosts

**Work it through.** The prefix is /26, meaning 26 network bits and 6 host bits. The mask has 26 leading ones:

```
11111111.11111111.11111111.11000000
   255   .   255   .   255  .  192
```

Block size is `256 - 192 = 64`, so /26 subnets of this network begin at .0, .64, .128, and .192. The block starting at .0 runs to .63.

| Item | Value |
|---|---|
| Subnet mask | 255.255.255.192 |
| Network address | 192.168.1.0 |
| Broadcast address | 192.168.1.63 |
| Usable host range | 192.168.1.1 to 192.168.1.62 |
| Usable hosts | 2^6 - 2 = 62 |

Now do the same for `192.168.1.130/26` without looking back. Block size 64; 130 falls in the block that starts at 128. Network 192.168.1.128, broadcast 192.168.1.191, usable .129 to .190, 62 hosts. Check yourself with `ipcalc 192.168.1.130/26`.

---
### Part 2: Design a three tier VPC layout in 10.0.0.0/16

You are given `10.0.0.0/16`: 65,536 addresses, far more than you need, which is the point. The goal is not to use it all. It is to divide it so the tiers are separable, the boundaries are obvious to a human reading a route table, and there is room left over.

**Requirements:**

- A public web tier, reachable from the internet
- A private application tier, reachable only from the web tier
- A private database tier, reachable only from the application tier
- Room to add a fourth tier later without renumbering anything

**A minimal answer, three subnets:**

| Tier | CIDR | Mask | Usable (standard) | Usable (AWS) | Route table sends 0.0.0.0/0 to |
|---|---|---|---|---|---|
| Public web | 10.0.1.0/24 | 255.255.255.0 | 254 | 251 | Internet gateway |
| App | 10.0.2.0/24 | 255.255.255.0 | 254 | 251 | NAT gateway |
| Database | 10.0.3.0/24 | 255.255.255.0 | 254 | 251 | Nothing, or NAT gateway if patching is needed |

That single line in the last column is the entire difference between a public and a private subnet. Everything else about them is identical.

**The answer you would actually deploy, spanning two availability zones:**

A single subnet lives in a single availability zone, so a design with one subnet per tier cannot survive the loss of one zone. Real designs place each tier in at least two.

| Tier | AZ a | AZ b |
|---|---|---|
| Public web | 10.0.0.0/24 | 10.0.1.0/24 |
| App | 10.0.10.0/24 | 10.0.11.0/24 |
| Database | 10.0.20.0/24 | 10.0.21.0/24 |

Note what the numbering does. Tiers are separated by a gap of ten in the third octet, so a fourth tier can be added at 10.0.30.0/24 and 10.0.31.0/24, and a third availability zone can be added at 10.0.2.0/24, 10.0.12.0/24 and 10.0.22.0/24, without a single existing subnet moving. Anyone reading `10.0.21.0/24` in a route table can tell at a glance that it is database tier, second zone. Address plans are read far more often than they are written.

Total consumed: six /24 subnets out of the 256 available in a /16. Roughly 98 percent of the range is still free. That is not waste. That is the design working.

**Deliverables:**

1. The completed table for Part 1, with working shown
2. Your VPC table, with a route table column for each subnet
3. Three sentences on why the database tier gets no route to an internet gateway, and how it installs security patches anyway
4. One sentence naming the address range you would allocate to a second VPC in a different region, and why it must not overlap this one

Keep this page. In Module 8 you will build it in Terraform and compare what you designed against what you had to change.

---
## Lab 3C: Two VMs on Different Subnets, Connected with Static Routes

**Goal:** make two hosts on different subnets talk to each other through a Linux router you configure yourself, and see `ip route` change before and after. This is the lab that turns routing from a diagram into something you have actually done.

---
### Topology

Three VMs. The router has an interface on each subnet; the hosts have one each.

```
   VM-A                     VM-R (router)                     VM-B
10.10.1.10/24  ------  10.10.1.1/24   10.10.2.1/24  ------  10.10.2.10/24
   net-1                  net-1  net-2                        net-2
```

In VirtualBox, create two internal networks named `net-1` and `net-2`. Give VM-A one adapter on `net-1`, VM-B one adapter on `net-2`, and VM-R two adapters, one on each. Keep each VM's existing NAT adapter for internet access; it does not participate in this lab.

---
### Step 1: Address the interfaces

On **VM-A** (substitute your real interface name from `ip -br link`):

```bash
sudo ip addr add 10.10.1.10/24 dev enp0s8
sudo ip link set enp0s8 up
```

On **VM-B**:

```bash
sudo ip addr add 10.10.2.10/24 dev enp0s8
sudo ip link set enp0s8 up
```

On **VM-R**, both:

```bash
sudo ip addr add 10.10.1.1/24 dev enp0s8
sudo ip addr add 10.10.2.1/24 dev enp0s9
sudo ip link set enp0s8 up
sudo ip link set enp0s9 up
```

---
### Step 2: `ip route` before

On VM-A:

```bash
ip route show
```

```
10.10.1.0/24 dev enp0s8 proto kernel scope link src 10.10.1.10
```

One directly connected route and nothing else for this network. Now prove the consequence:

```bash
ping -c 2 10.10.1.1        # the router's near side: works, same subnet
ping -c 2 10.10.2.10       # VM-B: fails
```

```
ping: connect: Network is unreachable
```

Read that message carefully. It is not a timeout and it is not a refusal. The kernel is saying it has no route toward 10.10.2.0/24 and therefore did not even put a packet on the wire. Capture this output; it is half your deliverable.

Run the same three commands on VM-B and record them too.

---
### Step 3: Turn VM-R into a router

A Linux host with two interfaces does not forward between them by default. Two things must be true.

**Enable IP forwarding:**

```bash
# Check the current value: 0 means forwarding is off
cat /proc/sys/net/ipv4/ip_forward

# Turn it on for now
sudo sysctl -w net.ipv4.ip_forward=1

# Make it survive a reboot
echo 'net.ipv4.ip_forward = 1' | sudo tee /etc/sysctl.d/99-router.conf
sudo sysctl --system
```

**Let the firewall forward the traffic.** This is the step that catches everyone. `firewalld` filters forwarded packets, not just packets addressed to the host itself, so forwarding can be enabled in the kernel and still drop everything. For a lab, place both internal interfaces in the trusted zone:

```bash
sudo firewall-cmd --permanent --zone=trusted --change-interface=enp0s8
sudo firewall-cmd --permanent --zone=trusted --change-interface=enp0s9
sudo firewall-cmd --reload
sudo firewall-cmd --get-active-zones
```

> The `trusted` zone is correct for an isolated lab and wrong for anything else. In production you would write an explicit forwarding policy allowing only the flows you intend. The point here is to see that IP forwarding and firewall policy are two separate gates, and traffic must pass both.

---
### Step 4: Add the static routes

VM-R knows both networks, because it has an interface on each. VM-A and VM-B do not. Tell them.

On **VM-A**:

```bash
sudo ip route add 10.10.2.0/24 via 10.10.1.1 dev enp0s8
```

On **VM-B**:

```bash
sudo ip route add 10.10.1.0/24 via 10.10.2.1 dev enp0s8
```

Both routes are required. A route is a one way instruction: without the second one, VM-A's packet reaches VM-B and VM-B's reply has nowhere to go. The symptom of a missing return route is a ping that hangs rather than failing fast, and diagnosing that from VM-A alone is impossible, which is a lesson in itself.

---
### Step 5: `ip route` after

On VM-A:

```bash
ip route show
```

```
10.10.1.0/24 dev enp0s8 proto kernel scope link src 10.10.1.10
10.10.2.0/24 via 10.10.1.1 dev enp0s8
```

The second line is new, and it is entirely the work you did. Now:

```bash
ping -c 3 10.10.2.10
traceroute -n 10.10.2.10
```

The ping succeeds. The traceroute shows two hops: 10.10.1.1, then 10.10.2.10. You can see the router in the path, which is the visible proof that the packet is being routed rather than delivered on the local link.

Ask the kernel to explain its own decision:

```bash
ip route get 10.10.2.10
```

```
10.10.2.10 via 10.10.1.1 dev enp0s8 src 10.10.1.10 uid 1000
```

---
### Step 6: Make it persistent

Everything above is lost at reboot, which is correct behaviour for `ip` commands and a nasty surprise if you assumed otherwise. Persist the route with NetworkManager on VM-A:

```bash
sudo nmcli connection modify "System enp0s8" +ipv4.routes "10.10.2.0/24 10.10.1.1"
sudo nmcli connection up "System enp0s8"
ip route show
```

Reboot the VM and run `ip route show` again. If the route is still there, you have done this properly.

---
### Deliverables

1. `ip route show` from VM-A and VM-B, before and after, four outputs total
2. The failed `ping` before, with its exact error message, and the successful `ping` after
3. The `traceroute -n` output showing the router in the path
4. The `ip route get 10.10.2.10` output
5. In prose: you enabled `net.ipv4.ip_forward` and it still did not work until you touched `firewalld`. Explain in a few sentences what each of those two gates does, and why a kernel that is willing to forward a packet may still not forward it.

**Cleanup**, if you are not keeping the topology:

```bash
sudo ip route del 10.10.2.0/24          # on VM-A
sudo ip route del 10.10.1.0/24          # on VM-B
sudo sysctl -w net.ipv4.ip_forward=0    # on VM-R
```

---
# Common Mistakes at This Level

**Diagnosing top down instead of bottom up.** 

Jumping straight into application logs before confirming basic reachability wastes time. Always confirm Layer 3 and Layer 4 first.

---
**Treating TTL as a value you only think about when first creating a record.** 

TTL needs active management around any planned infrastructure change, not just at creation time.

---
**Defaulting to sticky sessions instead of fixing the underlying architecture.** 

Sticky sessions are a workaround for stateful application servers, not a goal in themselves. The better long term fix is almost always moving session state to a shared store.

---
**Writing one giant security group rule instead of several specific ones.**

A rule allowing all traffic from `0.0.0.0/0` on all ports is sometimes added "temporarily" for convenience during testing and then forgotten. Default deny only protects you if the specific rules you add stay tightly scoped.

---
**Sizing a subnet for today's needs with no room for growth.** 

Address space is cheap to allocate generously up front and expensive to redesign later once real resources depend on it.

---
**Overlapping CIDR ranges across VPCs, accounts, and the office network.**

The cost is not paid on the day you allocate the range. It is paid on the day two networks need to be peered and cannot be, and by then real workloads depend on both.

---
**Debugging a name resolution problem with `ping` instead of `dig`.**

`ping` merges two questions, resolution and reachability, into one result. Separate them before trying to answer either.

---
**Testing only from localhost.**

`curl http://localhost` succeeding proves the process is running. It proves nothing about the firewall, the security group, or the bind address. A service bound to `127.0.0.1` passes every local test and is unreachable from every other machine on earth.

---