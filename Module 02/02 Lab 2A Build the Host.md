# Lab 2A: Build the Host

**Module 2: Linux and Systems Fundamentals**  |  **Weight: 20 marks**

**Prerequisites:** None. This is the first lab of the module.

**What is being assessed:** Everything else in Module 2 runs on the VM this lab produces. Do not skip it and do not borrow a classmate's box.

**Deliverable format.** One markdown file, `module-02/lab-2a.md`, in your course repository. Every command you ran, the output you got, and a note wherever what happened differed from what you expected. Commands without evidence do not count. A report showing a failure, a diagnosis, and a fix is worth more than a clean run, because a clean run tells me nothing about whether you understood it.

---

## Environment

* Fedora Server 44 or RHEL 10, `multi-user.target`, no GUI.
* Two adapters: NAT for egress, host only (`192.168.56.0/24`) for SSH from your laptop.
* `dnf` is DNF5 on this platform. `netstat` and `ifconfig` are not installed; use `ss` and `ip`.
* Persistent network configuration lives in `/etc/NetworkManager/system-connections/`.

---

**Goal.** A Fedora Server 44 or RHEL 10 VM with a fixed hostname, a static IP you control, and key based SSH login only. This is the machine you will use for the rest of the module, and, honestly, the rest of the course.

## 2A.1 Create the VM

Any Type 2 hypervisor is fine: VirtualBox, VMware Workstation or Fusion, UTM on Apple silicon, or `virt-manager` on a Linux host, which gives you KVM and is closest to what production looks like.

| Setting | Value |
|---|---|
| ISO | Fedora Server 44 or RHEL 10 (a free Red Hat Developer subscription covers RHEL) |
| vCPU | 2 |
| RAM | 4096 MB |
| Disk | 25 GB |
| Adapter 1 | NAT, for outbound internet |
| Adapter 2 | Host only network, for SSH from your laptop |

The two adapter arrangement is deliberate. NAT gives the VM internet access for package installs. The host only network gives you a stable private address that does not change when you move between a home network and a cafe. Note the host only subnet your hypervisor uses. VirtualBox typically offers `192.168.56.0/24`.

Install with the minimal or server package set. No GUI. `multi-user.target` is the correct default target for this machine.

Confirm this after first boot:

```bash
systemctl get-default
```
```bash
uname -r
cat /etc/os-release
```

## 2A.2 Set the hostname

```bash
sudo hostnamectl set-hostname web01.lab.local
```
```bash
hostnamectl status
```

Add it to `/etc/hosts` so that the machine can resolve its own fully qualified name without a DNS server:

```bash
echo "192.168.56.20 web01.lab.local web01" | sudo tee -a /etc/hosts
```

Log out and back in to see the new prompt.

## 2A.3 Configure the static IP with `nmcli`

Do this **on the VM console**, not over SSH. You are about to change the address you would be connected on.

Identify the host only adapter first. It is usually the second one, and it will be the one without a default route.

```bash
nmcli device status
ip route show
```

If the host only device already has a profile, modify it:

```bash
sudo nmcli connection modify "enp0s8" \
  ipv4.method manual \
  ipv4.addresses 192.168.56.20/24 \
  connection.autoconnect yes
```

If Fedora 44's installer created no profile for it, which is now the normal case for a NIC added after installation, create one:

```bash
sudo nmcli connection add type ethernet con-name host-only ifname enp0s8 \
  ipv4.method manual \
  ipv4.addresses 192.168.56.20/24 \
  autoconnect yes
```

Note what is **not** here: no gateway and no DNS on this profile. The host only network has no route to the internet, and if you set a second default gateway on it you will create a routing conflict with the NAT interface and break outbound traffic in a way that is genuinely annoying to debug. Leave the default route to the NAT adapter.

> **A note on the profile name.** The verification and persistence commands below assume the profile is called `host-only`, which is the name the **create** branch gives it. If you took the **modify** branch instead, your profile keeps whatever name it already had (often the device name, e.g. `enp0s8`, as shown by `nmcli connection show`). Substitute that name wherever `host-only` appears in the rest of this step.

Apply and verify:

```bash
sudo nmcli connection up host-only
ip addr show enp0s8
ip route show
ping -c 3 8.8.8.8      # proves the NAT adapter still routes
```

Confirm that the configuration is persistent by rebooting and checking again. A static IP that does not survive `reboot` is not a static IP.

```bash
sudo systemctl reboot
```

Show the file that makes it persistent:

```bash
sudo cat /etc/NetworkManager/system-connections/host-only.nmconnection
```

## 2A.4 Enable SSH

On Fedora and RHEL, `sshd` is installed and enabled by default. Confirm rather than assume:

```bash
systemctl is-enabled sshd
systemctl status sshd
sudo ss -tlnp | grep :22
```

Open the port in `firewalld` if it is not already open, and check which zone the host only interface actually lands in:

```bash
sudo firewall-cmd --get-active-zones
sudo firewall-cmd --list-all
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

## 2A.5 Key based authentication

On **your laptop**, not the VM:

```bash
ssh-keygen -t ed25519 -C "module02-lab"
```

Accept the default path, `~/.ssh/id_ed25519`, and set a passphrase. A passphrase on a key is not optional in this course; the SSH agent exists so that it costs you nothing after the first unlock.

Copy the public key to the VM. This still uses password authentication, which is the last time you will:

```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub youruser@192.168.56.20
```

Confirm it worked before you touch the server configuration:

```bash
ssh -i ~/.ssh/id_ed25519 youruser@192.168.56.20
```

If that logs you in without asking for the account password, and only then, continue.

## 2A.6 Disable password authentication

On current Fedora and RHEL, `/etc/ssh/sshd_config` ends with an `Include /etc/ssh/sshd_config.d/*.conf` line, and the first matching directive wins. Dropping a file into the include directory is therefore both cleaner and more reliable than editing the main file, and package updates will not touch it.

```bash
sudo tee /etc/ssh/sshd_config.d/50-hardening.conf > /dev/null <<'EOF'
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
EOF
```

`KbdInteractiveAuthentication no` matters. Setting `PasswordAuthentication no` alone leaves a keyboard interactive path open through PAM on some configurations, which means you have not actually disabled password login. Students discover this during a security review, usually the hard way.

Validate the configuration **before** restarting. `sshd -t` parses the config and exits nonzero on error. Skipping this step is how you lock yourself out of a remote server permanently.

```bash
sudo sshd -t && echo "config OK"
sudo systemctl restart sshd
```

Now, **keeping your existing session open**, open a second terminal and prove both directions:

```bash
# should succeed
ssh -i ~/.ssh/id_ed25519 youruser@192.168.56.20

# should fail with: Permission denied (publickey)
ssh -o PubkeyAuthentication=no youruser@192.168.56.20
```

## 2A.7 Deliverable

Your report must contain:

1. `hostnamectl status`, `ip addr show`, and `nmcli connection show` output after a reboot.
2. The contents of your `.nmconnection` keyfile and your `sshd_config.d` drop in.
3. Evidence of the successful key login and the rejected password login.
4. One paragraph: why did you set `PasswordAuthentication no` rather than simply choosing a long password? Answer in terms of what an attacker can do at scale against port 22, not in terms of "keys are more secure".
