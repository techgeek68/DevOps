# Lab 2D: The Same Job as a systemd Unit and Timer

**Module 2: Linux and Systems Fundamentals**  |  **Weight: 20 marks**

**Prerequisites:** Lab 2C complete. This lab reschedules the script you already wrote.

**What is being assessed:** Understanding what systemd gives you that cron cannot, and being able to argue the trade honestly.

**Deliverable format.** One markdown file, `module-02/lab-2d.md`, in your course repository. Every command you ran, the output you got, and a note wherever what happened differed from what you expected. Commands without evidence do not count. A report showing a failure, a diagnosis, and a fix is worth more than a clean run, because a clean run tells me nothing about whether you understood it.

---

## Environment

* Fedora Server 44 or RHEL 10, `multi-user.target`, no GUI.
* Two adapters: NAT for egress, host only (`192.168.56.0/24`) for SSH from your laptop.
* `dnf` is DNF5 on this platform. `netstat` and `ifconfig` are not installed; use `ss` and `ip`.
* Persistent network configuration lives in `/etc/NetworkManager/system-connections/`.

---

**Goal.** Reimplement Lab 2C's schedule as a systemd service plus timer, confirm it fires, read its output with `journalctl`, and then argue for one scheduler over the other.

## 2D.1 The service unit

A scheduled job is `Type=oneshot`. It runs, it exits, it is done. It is not a daemon, and it must not be enabled directly: the timer is what gets enabled.

```bash
sudo tee /etc/systemd/system/healthcheck@.service > /dev/null <<'EOF'
[Unit]
Description=Health check for %i
Documentation=https://git.example.com/module-02
After=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/healthcheck.sh %i
SuccessExitStatus=0 1
User=root
EOF
```

Two design choices to defend in your report. The `@` makes this a **template** unit, so `%i` is filled in with whatever follows the `@` in the instance name, and one unit file covers every service you want to watch. `SuccessExitStatus=0 1` tells systemd that exit code `1` (service was down, restart attempted) is a valid outcome of the check rather than a failure of the check itself, so the unit is not marked `failed` and does not need resetting.

## 2D.2 The timer unit

```bash
sudo tee /etc/systemd/system/healthcheck@.timer > /dev/null <<'EOF'
[Unit]
Description=Run health check for %i every 5 minutes

[Timer]
OnBootSec=2min
OnUnitActiveSec=5min
AccuracySec=10s
RandomizedDelaySec=30s
Persistent=true
Unit=healthcheck@%i.service

[Install]
WantedBy=timers.target
EOF
```

* `OnBootSec` is the first run after boot. `OnUnitActiveSec` is the interval between runs thereafter. Together they are the monotonic form, which is what you want for "every five minutes" rather than "at 09:05".
* `AccuracySec=10s` narrows systemd's default one minute coalescing window. Without it, your five minute timer may fire up to a minute late, and students report this as a bug when it is not one.
* `RandomizedDelaySec=30s` staggers the start. Across a fleet of a hundred nodes, an unstaggered timer produces a synchronised thundering herd against whatever the job talks to.
* `Persistent=true` means that if the machine was off when a run was due, the job runs once at the next boot. Cron has no equivalent without `anacron`.

For a calendar based schedule instead, `OnCalendar=*:0/5` gives you every five minutes on the wall clock. Test any calendar expression before trusting it:

```bash
systemd-analyze calendar "*:0/5"
systemd-analyze calendar "Mon *-*-* 03:30:00"
```

## 2D.3 Enable and verify

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now healthcheck@nginx.timer
```

```bash
systemctl list-timers --all
```

The output shows `NEXT`, `LEFT`, `LAST`, `PASSED`, and the unit it activates. This one table replaces the entire practice of guessing whether cron ran.

```bash
systemctl status healthcheck@nginx.timer
sudo systemctl start healthcheck@nginx.service   # force one run now, do not wait
journalctl -u healthcheck@nginx.service -n 50 --no-pager
journalctl -u healthcheck@nginx.service -f
```

Note what you get for free that cron never gave you: the script's stdout and stderr are captured in the journal automatically, tagged with the unit name, with microsecond timestamps, and no redirection to a log file you have to rotate yourself. The `>> /var/log/... 2>&1` in your crontab line exists only because cron cannot do this.

Now break it on purpose and read the failure through the journal:

```bash
sudo systemctl stop nginx
sudo systemctl start healthcheck@nginx.service
journalctl -u healthcheck@nginx.service -n 20 --no-pager
```

## 2D.4 The three sentences

Write exactly three sentences on when you would choose a timer over cron, or the other way round. A defensible answer looks something like this, and yours should be your own:

> Use a systemd timer when the job is part of the system's service graph: when it needs to run only after another unit is up, when it must run as a specific user with resource limits or a private `/tmp`, when you want its output in the journal alongside everything else, or when you need a missed run to be caught up after downtime. Use cron when the job is trivial, portable across non systemd hosts, and belongs to a user rather than to the system, or when you are working on a machine where another team owns the unit files and adding one is more friction than editing a crontab. The honest summary is that timers are strictly more capable and cron is strictly more familiar, and on a modern Linux fleet the capability wins, which is why every distribution now ships its own periodic maintenance as timers rather than cron jobs.

## 2D.5 Deliverable

Both unit files, `systemctl list-timers` output showing the timer scheduled, `journalctl` output covering at least two automatic runs and one deliberately failed run, and your three sentences.
