# Lab 2C: A Bash Health Check Script, Scheduled with cron

**Module 2: Linux and Systems Fundamentals**  |  **Weight: 20 marks**

**Prerequisites:** Labs 2A and 2B complete. You need `nginx` installed, which 2B does.

**What is being assessed:** Bash that a colleague would accept in review: functions, conditionals, a loop, quoted expansions, meaningful exit codes.

**Deliverable format.** One markdown file, `module-02/lab-2c.md`, in your course repository. Every command you ran, the output you got, and a note wherever what happened differed from what you expected. Commands without evidence do not count. A report showing a failure, a diagnosis, and a fix is worth more than a clean run, because a clean run tells me nothing about whether you understood it.

---

## Environment

* Fedora Server 44 or RHEL 10, `multi-user.target`, no GUI.
* Two adapters: NAT for egress, host only (`192.168.56.0/24`) for SSH from your laptop.
* `dnf` is DNF5 on this platform. `netstat` and `ifconfig` are not installed; use `ss` and `ip`.
* Persistent network configuration lives in `/etc/NetworkManager/system-connections/`.

---

**Goal.** A Bash script that takes a service name as an argument, checks whether it is running, logs the result with a timestamp, and exits with a meaningful code. Then schedule it with cron.

## 2C.1 Requirements

1. Takes exactly one argument: the service name. With zero or more than one argument, print a usage message to **stderr** and exit `2`.
2. If the service does not exist as a systemd unit at all, that is a different failure from a service that exists and is stopped. Exit `3` for the former.
3. If the service is active, log `OK` and exit `0`. If it exists and is not active, log `CRITICAL`, attempt one restart, log the result of that attempt, and exit `1`.
4. Every log line goes to `/var/log/healthcheck.log` in the format `2026-07-14T09:15:03+05:45 [OK] nginx is active`. Use ISO 8601 timestamps. Do not invent a date format.
5. Use `set -euo pipefail`. Quote every variable expansion. Use at least two functions and one conditional block.

## 2C.2 Reference implementation

```bash
#!/usr/bin/env bash
#
# healthcheck.sh: verify a systemd service is running, log the result,
# attempt one restart if it is not.
#
# Usage:  healthcheck.sh <service-name>
# Exit:   0 running, 1 not running, 2 usage error, 3 unknown unit

set -euo pipefail

readonly LOGFILE="/var/log/healthcheck.log"
readonly SERVICE="${1:-}"
readonly MAX_ATTEMPTS=5
readonly RETRY_DELAY=2

usage() {
    echo "Usage: $(basename "$0") <service-name>" >&2
    exit 2
}

log() {
    local level="$1"
    local message="$2"
    local timestamp
    timestamp="$(date --iso-8601=seconds)"
    printf '%s [%s] %s\n' "$timestamp" "$level" "$message" | tee -a "$LOGFILE"
}

unit_exists() {
    systemctl list-unit-files --type=service --no-legend --no-pager \
        | awk '{print $1}' \
        | grep -qx "${1}.service"
}

main() {
    [[ $# -eq 1 ]] || usage

    if ! unit_exists "$SERVICE"; then
        log "UNKNOWN" "no systemd unit named ${SERVICE}.service"
        exit 3
    fi

    if systemctl is-active --quiet "$SERVICE"; then
        log "OK" "${SERVICE} is active"
        exit 0
    fi

    log "CRITICAL" "${SERVICE} is not active, attempting restart"

    if ! systemctl restart "$SERVICE"; then
        log "FAILED" "${SERVICE} restart command failed"
        exit 1
    fi

    # Poll rather than sleeping blindly. A service may take several seconds to
    # bind its socket, and a fixed sleep is either too short or wasted time.
    local attempt
    for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
        if systemctl is-active --quiet "$SERVICE"; then
            log "RECOVERED" "${SERVICE} became active after ${attempt} check(s)"
            exit 1
        fi
        sleep "$RETRY_DELAY"
    done

    log "FAILED" "${SERVICE} still not active after ${MAX_ATTEMPTS} checks"
    exit 1
}

main "$@"
```

Points worth noticing, because they are the points being assessed:

* `"${1:-}"` rather than `"$1"`. Under `set -u`, referencing an unset `$1` aborts the script before your usage function can ever run, and the user gets a shell error instead of your message.
* `is-active --quiet` returns a **status**, not text. Testing `$(systemctl is-active x) == "active"` works until the day it prints `activating` or `failed`, and the exit status is what the tool is actually designed to give you.
* The script exits `1` after a successful recovery, not `0`. It is reporting on the state it **found**, which is what a monitoring check must do. A check that heals a problem and then reports success hides an incident.
* The recovery check is a **loop**, not a `sleep 2`. Services bind sockets on their own schedule, and a fixed sleep is either too short (false failure) or wasted wall clock. Polling five times at two second intervals bounds the wait and reports how long recovery actually took.
* `main "$@"` at the bottom keeps argument handling in one place and makes the script sourceable for testing.

## 2C.3 Install and test

```bash
sudo install -m 0755 healthcheck.sh /usr/local/bin/healthcheck.sh
sudo touch /var/log/healthcheck.log
sudo chown root:root /var/log/healthcheck.log
sudo chmod 0640 /var/log/healthcheck.log
```

Test every path, and record the exit code each time with `echo $?`:

```bash
sudo /usr/local/bin/healthcheck.sh                 # expect usage, exit 2
sudo /usr/local/bin/healthcheck.sh nginx extra     # expect usage, exit 2
sudo /usr/local/bin/healthcheck.sh notarealservice # expect UNKNOWN, exit 3
sudo systemctl start nginx
sudo /usr/local/bin/healthcheck.sh nginx           # expect OK, exit 0
sudo systemctl stop nginx
sudo /usr/local/bin/healthcheck.sh nginx           # expect CRITICAL then RECOVERED, exit 1
```

Then run it under the debugger and paste a few lines of the trace into your report:

```bash
sudo bash -x /usr/local/bin/healthcheck.sh nginx
```

Finally, run it through ShellCheck. Fix everything it flags, or justify in your report why you did not.

```bash
sudo dnf install -y ShellCheck
shellcheck healthcheck.sh
```

## 2C.4 Schedule with cron

```bash
sudo crontab -e
```

```cron
*/5 * * * * /usr/local/bin/healthcheck.sh nginx >> /var/log/healthcheck-cron.log 2>&1
```

Two things will bite you here and both are worth experiencing once. First, cron runs with an almost empty environment: `PATH` is typically `/usr/bin:/bin` and `$HOME` may not be what you expect. Always use absolute paths inside a cron job. Second, `%` is special in a crontab and must be escaped as `\%`, which is why a naive `date +%F` inside a crontab line breaks.

Confirm it actually ran, rather than assuming:

```bash
sudo journalctl -u crond --since "-10 min"
sudo tail -f /var/log/healthcheck.log
```

## 2C.5 Deliverable

The script, the ShellCheck output, the exit code from each of the five test cases, the crontab line, and journal evidence that cron fired it at least twice.
