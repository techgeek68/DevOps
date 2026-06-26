## 2. Configuring the Network

### 3.1 Networking Concepts

**Network communication types:**

- Unicast: one source to one destination (web browsing, SSH)
- Broadcast: one source to all devices on the network (ARP, DHCP)
- Multicast: one source to a group of subscribed devices (video streaming, OSPF routing)
- Anycast: one source to the nearest of multiple identical destinations (DNS, CDNs)

**IP address types:**

- IPv4: 32-bit, dotted decimal notation (e.g., `192.168.1.1`), approximately 4.3 billion addresses
- IPv6: 128-bit, hexadecimal notation (e.g., `2001:db8::1`), effectively unlimited addresses

**IP address classes (historical, still useful for understanding):**

| Class | First Octet | Private Range | Default Mask |
|---|---|---|---|
| A | 1-126 | 10.0.0.0/8 | /8 |
| B | 128-191 | 172.16.0.0/12 | /16 |
| C | 192-223 | 192.168.0.0/16 | /24 |
| D | 224-239 | Multicast | — |
| E | 240-255 | Reserved/Experimental | — |

Special ranges: 127.0.0.0/8 (loopback), 169.254.0.0/16 (link-local/APIPA).

**DNS resolution process:**

Client queries recursive resolver > resolver checks cache > queries root servers > queries TLD servers > queries authoritative server > returns IP to client.

Common resolvers: `8.8.8.8` (Google), `1.1.1.1` (Cloudflare), `9.9.9.9` (Quad9).

### 3.2 Linux Networking Commands

**Interface and address management:**

```bash
ip addr show                                    # Show all interfaces and IPs
ip a                                            # Short form
ip -br addr show                                # Brief summary
ip link show                                    # Show interface link status
ip link set eth0 up                             # Bring interface up
ip link set eth0 down                           # Bring interface down
ip addr add 192.168.1.100/24 dev eth0           # Add IP (temporary, lost on reboot)
ip addr del 192.168.1.100/24 dev eth0           # Remove IP
ip addr flush dev eth0                          # Remove all IPs from interface
```

**Routing:**

```bash
ip route show                                   # Show routing table
ip route get 8.8.8.8                            # Show which route is used for a destination
ip route add default via 192.168.1.1            # Add default gateway (temporary)
ip route add 10.0.0.0/8 via 192.168.1.1 dev eth0   # Add specific route (temporary)
ip route del 10.0.0.0/8                         # Delete route
```

**Connections and sockets:**

```bash
ss -tulnp                                       # Show all listening TCP/UDP sockets with process names
ss -tnp                                         # Show established TCP connections
ss -tunap                                       # Show all TCP/UDP connections
ip neigh show                                   # ARP table (modern)
arp -n                                          # ARP table (legacy)
```

**DNS:**

```bash
cat /etc/resolv.conf                            # Current DNS resolver configuration
resolvectl status                               # systemd-resolved status
nmcli device show eth0 | grep DNS               # DNS assigned by NetworkManager
dig example.com A                               # DNS lookup with full detail
dig +short example.com                          # Just the IP
nslookup example.com                            # Simple DNS lookup
nslookup example.com 1.1.1.1                    # Query a specific resolver
host example.com                                # Basic DNS query
```

**Connectivity testing:**

```bash
ping -c 4 8.8.8.8                               # Test basic reachability
traceroute example.com                          # Trace path to destination
tracepath example.com                           # Trace path (no root required)
curl -I http://example.com                      # Test HTTP service (headers only)
curl -v http://example.com                      # Verbose HTTP test
nc -zv example.com 80                           # Test if port is open
```

**Legacy tools (deprecated, know for older systems):**

```bash
ifconfig                                        # Legacy interface info (from net-tools)
netstat -tulnp                                  # Legacy socket info (replaced by ss)
route -n                                        # Legacy routing table
```

### 3.3 Persistent Network Configuration

On RHEL, CentOS Stream, and Fedora, the recommended tool is `nmcli` (NetworkManager CLI).

**Using `nmcli`:**

```bash
nmcli connection show                           # List all connections
nmcli device status                             # Show device status

# Configure a static IP on a connection
sudo nmcli connection modify "Wired connection 1" \
  ipv4.method manual \
  ipv4.addresses 192.168.1.100/24 \
  ipv4.gateway 192.168.1.1 \
  ipv4.dns "8.8.8.8,8.8.4.4"

# Apply changes
sudo nmcli connection down "Wired connection 1"
sudo nmcli connection up "Wired connection 1"

# Verify
ip addr show
ip route show
```

Find your gateway and DNS:

```bash
ip route show | grep default                    # Shows default gateway
cat /etc/resolv.conf                            # Shows current DNS
```

**Using `/etc/hosts` for local resolution:**

```bash
sudo vim /etc/hosts
```

Add entries:
```
192.168.1.10  server1.example.com server1
192.168.1.20  server2.example.com server2
```

Entries in `/etc/hosts` take precedence over DNS for local name resolution.

**Ubuntu / Debian — Netplan:**

File: `/etc/netplan/01-netcfg.yaml`

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

```bash
sudo netplan apply
```

### 3.4 Network Troubleshooting

Troubleshoot systematically from Layer 1 upward:

```bash
ip -br addr show                          # Is the interface up and has an IP?
ping -c 3 192.168.1.1                     # Can we reach the gateway?
ping -c 3 8.8.8.8                         # Can we reach the internet?
dig google.com                            # Does DNS resolution work?
curl -I http://example.com                # Does HTTP work?
ss -tulnp | grep :80                      # Is the web server actually listening?
firewall-cmd --list-all                   # Is the firewall blocking anything?
journalctl -u NetworkManager -f           # NetworkManager log for connection issues
```

Common issues and fixes:

| Symptom | Likely Cause | Fix |
|---|---|---|
| `ping 8.8.8.8` works, `ping google.com` fails | DNS not configured | Update `/etc/resolv.conf` or NetworkManager DNS setting |
| No internet, gateway not pingable | Interface down or wrong gateway | `ip link set up`, verify gateway IP |
| Service not reachable from outside | Firewall rule missing | `firewall-cmd --add-port=<port>/tcp --permanent && firewall-cmd --reload` |
| Gets `169.254.x.x` IP | DHCP failure | Check DHCP server or assign static IP |
| IP conflict | Two devices with same IP | Change one to a unique address |

---

## 2. Managing Firewalls

### 2.1 Firewall Concepts

A firewall filters incoming and outgoing network traffic based on rules. On Linux, firewalls are implemented in the kernel via the **netfilter** framework. User-space tools (`firewalld`, `nftables`, `ufw`) are interfaces to that framework.

**Stateless vs stateful:**
- Stateless: evaluates each packet independently. You must allow both request and response directions.
- Stateful (connection tracking): tracks connection state. Permitting a connection automatically allows return traffic.

`firewalld` is stateful. It uses the `nftables` backend on RHEL 8+, CentOS Stream 9+, and Fedora 32+.

### 2.2 `firewalld` (RHEL / CentOS / Fedora — Primary Tool)

`firewalld` is the default on RHEL-family systems and the recommended tool for this course.

**Zones** determine what traffic is allowed on each interface. The most used zones:
- `public` — default for external interfaces; only explicitly allowed traffic is permitted
- `trusted` — all traffic is allowed
- `drop` — all incoming traffic is silently dropped

```bash
firewall-cmd --state                                         # Check if firewalld is running
firewall-cmd --get-default-zone                              # Show default zone
firewall-cmd --get-active-zones                              # Show zones in use
firewall-cmd --list-all                                      # Show all rules in active zone

# Allow services by name (more readable)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https

# Allow a specific port
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --permanent --add-port=3306/tcp

# Remove a rule
sudo firewall-cmd --permanent --remove-port=8080/tcp
sudo firewall-cmd --permanent --remove-service=http

# Apply permanent rules to the running config
sudo firewall-cmd --reload

# Verify the backend
cat /etc/firewalld/firewalld.conf | grep FirewallBackend

# Block a specific IP with a rich rule
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="192.168.1.100" reject'
sudo firewall-cmd --reload

# Remove the block
sudo firewall-cmd --permanent --remove-rich-rule='rule family="ipv4" source address="192.168.1.100" reject'
sudo firewall-cmd --reload

# Verify all rules
sudo firewall-cmd --list-all
```

Important: `--permanent` writes the rule to disk so it survives reboots. Without it, the change applies only until the next reboot or `firewall-cmd --reload`. Always pair `--permanent` with `--reload`.

### 2.3 `nftables`

`nftables` is the current Linux packet filtering framework and the backend for `firewalld` on modern systems. It replaced `iptables` and consolidates IPv4, IPv6, ARP, and bridge filtering into one tool.

For most DevOps work, you interact with `firewalld` rather than `nftables` directly. You may inspect `nftables` rules to understand what `firewalld` has configured:

```bash
sudo nft list ruleset                                        # Show all nftables rules
```

When you need to write `nftables` rules directly (e.g., on a minimal system without `firewalld`):

```bash
# Create a table
sudo nft add table inet my_filter

# Create chains
sudo nft add chain inet my_filter input '{ type filter hook input priority 0; policy drop; }'
sudo nft add chain inet my_filter output '{ type filter hook output priority 0; policy accept; }'

# Add rules
sudo nft add rule inet my_filter input ct state established,related accept
sudo nft add rule inet my_filter input iifname "lo" accept
sudo nft add rule inet my_filter input tcp dport 22 accept
sudo nft add rule inet my_filter input tcp dport 80 accept

# View configuration
sudo nft list table inet my_filter

# Save and persist (RHEL/CentOS)
sudo nft list ruleset > /etc/sysconfig/nftables.conf
sudo systemctl enable --now nftables
```

### 2.4 `iptables` (Legacy Context)

`iptables` is the predecessor to `nftables`. On RHEL 9, the `iptables-nft` package is formally deprecated. On CentOS Stream 10 and RHEL 10, the `iptables` kernel module is not included by default.

You should not use `iptables` for new configurations. Know it for reading legacy documentation and troubleshooting older systems.

```bash
sudo iptables -L -n -v --line-numbers    # List all rules
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT    # Allow SSH
sudo iptables -A INPUT -s 192.168.1.100 -j DROP       # Block an IP
```

`iptables` rules are not persistent by default and are lost on reboot.

### 2.5 UFW (Ubuntu/Debian)

`ufw` (Uncomplicated Firewall) is the default tool on Ubuntu. It is a simplified frontend for `iptables`.

```bash
sudo ufw status verbose
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh                       # Allow SSH by service name
sudo ufw allow 22/tcp                    # Allow SSH by port
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 21                         # Block FTP
sudo ufw delete allow 22                 # Remove a rule
sudo ufw deny from 192.168.1.50         # Block a specific IP
```

### 2.6 SELinux (RHEL / CentOS)

SELinux is a mandatory access control system built into the Linux kernel. It enforces fine-grained policies that restrict what processes and users can do, even if they have appropriate file permissions.

```bash
sestatus                    # Show SELinux status and mode
getenforce                  # Quick check: Enforcing, Permissive, or Disabled
```

Modes:
- **Enforcing**: SELinux policies are active and violations are blocked.
- **Permissive**: Violations are logged but not blocked. Use for troubleshooting.
- **Disabled**: SELinux is off. Avoid in production.

```bash
sudo setenforce 0           # Switch to Permissive (temporary, lost on reboot)
sudo setenforce 1           # Switch to Enforcing (temporary)
```

To change mode permanently, edit `/etc/selinux/config`:

```
SELINUX=enforcing
```

Reboot required for permanent changes.

**Allowing services on non-standard ports with SELinux:**

When you run a service on a non-default port (e.g., Apache on port 9090 instead of 80), SELinux will block it. You must label the port:

```bash
sudo semanage port -a -t http_port_t -p tcp 9090      # Allow Apache on port 9090
sudo semanage port -a -t ssh_port_t -p tcp 2222       # Allow SSH on port 2222
sudo semanage port -l | grep http                     # Verify allowed ports for HTTP
sudo semanage port -l | grep ssh                      # Verify allowed ports for SSH
```

In production, keep SELinux in Enforcing mode. Use Permissive only temporarily when troubleshooting.

### 2.7 AppArmor (Ubuntu/Debian)

AppArmor is Ubuntu's equivalent of SELinux. It uses per-application profiles to restrict what a process can access.

```bash
sudo apparmor_status                     # Show AppArmor status
sudo aa-enforce /path/to/profile         # Set profile to enforcing mode
sudo aa-complain /path/to/profile        # Set profile to complain mode (log only)
sudo systemctl reload apparmor           # Reload profiles after changes
sudo aa-logprof                          # Interactively tune profiles based on log entries
```

Profiles are in `/etc/apparmor.d/`.
