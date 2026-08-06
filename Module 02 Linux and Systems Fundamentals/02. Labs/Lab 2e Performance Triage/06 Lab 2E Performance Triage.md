# Lab 2E: Performance Triage

**Module 2: Linux and Systems Fundamentals**  |  **Weight: 20 marks**

**Prerequisites:** Labs 2A and 2B complete. `sysstat` and `stress-ng` installed.

**What is being assessed:** A diagnostic method. The answer is worth nothing without the path you took to it.

**Deliverable format.** One markdown file, `module-02/lab-2e.md`, in your course repository. Every command you ran, the output you got, and a note wherever what happened differed from what you expected. Commands without evidence do not count. A report showing a failure, a diagnosis, and a fix is worth more than a clean run, because a clean run tells me nothing about whether you understood it.

---

## Environment

* Fedora Server 44 or RHEL 10, `multi-user.target`, no GUI.
* Two adapters: NAT for egress, host only (`192.168.56.0/24`) for SSH from your laptop.
* `dnf` is DNF5 on this platform. `netstat` and `ifconfig` are not installed; use `ss` and `ip`.
* Persistent network configuration lives in `/etc/NetworkManager/system-connections/`.

---

**Goal.** A VM is "slow". You have a shell and nothing else. No dashboards, no APM, no Grafana. Determine whether the bottleneck is CPU, memory, disk, or network, and write up the path you took.

There is one real bottleneck. There are three deliberate red herrings, each of which is a metric that looks alarming and is not the cause. Finding the real one is half the exercise. Correctly **dismissing** the other three, with a reason, is the other half.

## 2E.1 Setting up the scenario

An instructor, or you yourself if you can manage to forget what you did, plants the scenario. Run these on the lab VM and then walk away for ten minutes so you approach it cold.

```bash
sudo dnf install -y sysstat stress-ng htop
sudo systemctl enable --now sysstat
```

```bash
# The real problem: sustained synchronous writes saturating the virtual disk.
# Pin the workload to a known on-disk path and confirm free space first, so the
# stressor does not silently land in an arbitrary working directory.
sudo mkdir -p /var/tmp/lab2e-io
df -hT /var/tmp/lab2e-io
sudo systemd-run --unit=lab2e-io \
  stress-ng --temp-path /var/tmp/lab2e-io --hdd 2 --hdd-opts sync,wr-seq --hdd-bytes 1G --timeout 3600s

# Red herring 1: one busy core on a multi core box
sudo systemd-run --unit=lab2e-cpu \
  stress-ng --cpu 1 --cpu-load 100 --timeout 3600s

# Red herring 2: a large page cache, which makes "free" memory look almost exhausted
sudo systemd-run --unit=lab2e-cache \
  bash -c 'cat /usr/lib/* /usr/bin/* > /dev/null 2>&1; sleep 3600'

# Red herring 3: many idle established connections.
# Stand up a dedicated local listener and open a couple of hundred clients
# against it. This does NOT abuse sshd: unauthenticated SSH connections get
# timed out by LoginGraceTime and throttled by MaxStartups, so they would not
# stay established. A --recv-only client blocks and holds its socket open.
sudo dnf install -y nmap-ncat
sudo systemd-run --unit=lab2e-net bash -c '
  ncat -k -l 127.0.0.1 9999 &
  sleep 1
  for i in $(seq 1 100); do ncat --recv-only 127.0.0.1 9999 & done
  wait'
```

Confirm the connections are actually up before you walk away, rather than trusting that the loop worked:

```bash
ss -tan state established | wc -l
systemctl status lab2e-net
```

Tear down afterwards:

```bash
for u in lab2e-io lab2e-cpu lab2e-cache lab2e-net; do sudo systemctl stop "$u" 2>/dev/null; done
```

## 2E.2 The method

Work outside in. Never start with `top`; start with a question about which of the four resources is exhausted, and let each tool eliminate one.

**Step 1. Is the machine actually loaded, and by what kind of work?**

```bash
uptime
```

Load average will be high, well above the core count. This tells you the run queue is long. It does **not** tell you the machine is CPU bound, and this is the single most misread number in Linux. On Linux, load average counts processes in the `R` (runnable) state **and** processes in the `D` (uninterruptible sleep) state, which is overwhelmingly processes blocked on disk I/O. A load of 12 on a 2 vCPU box with idle CPUs means the queue is full of tasks waiting on something that is not the CPU.

**Step 2. Is the CPU the constraint?**

```bash
vmstat 1 5
mpstat -P ALL 2 3
```

Read the columns, not the summary. If `%idle` is substantial and `%iowait` is high, the CPU is not the bottleneck; it is sitting there waiting. In `vmstat`, look at the `b` column (processes blocked on I/O) against the `r` column (processes runnable). A high `b` with a low `r` is a disk story, not a CPU story.

The single busy process at 100% of one core (red herring 1) shows up here as one CPU pegged in `mpstat -P ALL` output while the others have idle time. On a 2 vCPU box it costs you half your compute, which is real, but it does not explain a load average of 12 and it does not produce `%iowait`.

**Step 3. Is memory the constraint?**

```bash
free -h
vmstat 1 5
```

`free -h` will show almost no "free" memory and a large `buff/cache` figure (red herring 2). This is normal and desirable. Linux uses otherwise idle RAM as page cache, and it will hand that memory back the instant a process asks for it. **The column that matters is `available`, not `free`.** If `available` is healthy, you have memory.

The definitive test for memory pressure is not `free` at all, it is swapping: the `si` and `so` columns in `vmstat`. Sustained nonzero `si`/`so` means the machine is paging to disk and memory is genuinely the problem. In this scenario they are zero. Check the kernel's own view too:

```bash
dmesg -T | grep -i -E "out of memory|oom-killer"
```

Nothing. Memory is eliminated.

**Step 4. Is the disk the constraint?**

```bash
iostat -xz 2 5
```

This is where the answer is. Read three columns:

* `%util` near 100 means the device is servicing requests essentially all the time.
* `await` (or `r_await`/`w_await`), the average time a request spends waiting plus servicing, in milliseconds. On a virtual disk backed by SSD, single digit milliseconds is typical, though what counts as "normal" depends on the backend (provisioned IOPS, host contention, caching). Tens or hundreds of milliseconds means the queue is deep and requests are stacking up.
* `aqu-sz`, the average queue depth. A number well above 1 means requests are waiting on each other.

Now attribute it to a process:

```bash
sudo iotop -oPa          # if available
pidstat -d 2 5           # from sysstat, no extra tooling needed
ps -eo state,pid,comm --no-headers | awk '$1 ~ /D/'
```

`pidstat -d` gives you per process kB read and written per second. The `ps` line above lists exactly the processes in `D` state, which is the population that inflated the load average in step 1. The story now closes: the same processes that are blocked in `D` are the ones doing the writes that pinned `%util` at 100.

**Step 5. Is the network the constraint?**

```bash
ss -s
ss -tan state established | wc -l
sar -n DEV,EDEV 2 5
```

`ss -s` reports a couple of hundred established sockets (red herring 3), which looks like a lot on a lab box. Connection **count** is not a bottleneck; throughput and errors are. `sar -n DEV` shows negligible `rxkB/s` and `txkB/s` (the traffic report), and `sar -n EDEV` shows no errors, drops, or frame/FIFO problems (the error report — `DEV` alone does not carry those counters, which is why you ask for both). A few hundred idle sockets are not, by themselves, evidence of network saturation; confirm traffic, retransmissions, drops, and application limits before treating connection count as the bottleneck. Network is eliminated.

## 2E.3 The answer

The bottleneck is **disk I/O**. A process is issuing sustained synchronous sequential writes that saturate the virtual disk. `%util` is pinned near 100, `await` is an order of magnitude above normal, the queue depth is deep, and the processes responsible are sitting in `D` state, which is what inflated the load average that made the machine look CPU bound in the first place.

The three red herrings and their dismissals:

| Signal | Why it looks alarming | Why it is not the cause |
|---|---|---|
| Load average of 12 on 2 vCPUs, one core pegged at 100% | Looks like CPU exhaustion | Other cores show idle time, `%iowait` is high, and Linux load counts `D` state tasks. The busy core is one process and explains none of the wait. |
| `free` shows almost no free memory | Looks like memory exhaustion | The memory is page cache. `available` is healthy, `si`/`so` are zero, and there is no OOM activity in `dmesg`. |
| Roughly 200 established TCP connections | Looks like a connection flood | `sar -n DEV` shows almost no traffic and `sar -n EDEV` shows zero errors or drops. Idle sockets cost nothing. |

## 2E.4 Deliverable

A diagnostic write up, not a list of commands. It must contain:

1. The hypothesis you started with and why.
2. Each command you ran, the output, and **the specific number in that output that changed your mind**. "I ran `vmstat`" is worthless. "`vmstat` showed `b`=6 against `r`=1 with 40% idle CPU, which ruled out CPU saturation and pointed at blocking I/O" is the whole point.
3. Your dismissal of each red herring, with the metric that dismissed it.
4. The process responsible, identified by PID and name, with the evidence linking it to the device.
5. What you would do next in production, given that you have found the cause. Killing the process is one answer. Throttling it with a systemd `IOWeight=` or `IOReadBandwidthMax=` directive, moving the workload to a faster device, or asking whether the writes need to be synchronous at all are better ones, and which is right depends on what the process is for.
