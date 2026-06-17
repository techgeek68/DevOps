# Module 3: Linux for DevOps

## Section 3.1: Linux Fundamentals

---

# Theory

---

## Why Linux in DevOps?

The majority of servers, cloud instances, containers, and DevOps tools run on Linux. Web servers, CI/CD agents, Kubernetes nodes, Docker hosts, and monitoring systems all run Linux by default. As a DevOps engineer, the command line is your primary interface with infrastructure. If you are not comfortable in Linux, every module in this course will be harder than it needs to be.

This section covers Linux from fundamentals through the practical skills needed in a real DevOps environment: file operations, user management, permissions, package management, scripting, scheduling, networking, firewall management, process monitoring, and SSH.

---

# Laboratory Works

---

## 1. Basic Linux Commands

### Session Basics

When you log in to a Linux system, the shell prompt tells you who you are and where you are:

- `$` — normal user prompt
- `#` — root user prompt
- `~` — shorthand for the current user's home directory

```bash
whoami          # Print the current logged-in user
hostname        # Show the system hostname
pwd             # Print the current working directory
clear           # Clear the terminal screen
```
---
<img width="762" height="135" alt="Screenshot 2026-06-17 at 7 39 02 PM" src="https://github.com/user-attachments/assets/3304546e-6c45-429b-a5c0-6879eb37e4c9" />

---

### Changing the Hostname

* Synatx: Set the hostname
```bash
sudo hostnamectl set-hostname <new-hostname>
```
* Reload the shell session
```bash
exec bash
```
* Verify the hostname
```bash
hostname
```
---
<img width="818" height="226" alt="Screenshot 2026-06-17 at 7 43 36 PM" src="https://github.com/user-attachments/assets/4e8fa739-d45e-4010-961a-7e8e03337f88" />

---

### Switching Between GUI and Terminal (Systems with a Desktop)

- `Ctrl + Alt + F2` through `F6` — switch to a text terminal (TTY)
- `Ctrl + Alt + F1` or `Ctrl + Alt + F7` — switch back to the graphical session

The exact function key for the GUI varies by distribution and display manager.

---

### Filesystem Navigation

```bash
ls                     # List files in the current directory
ls -l                  # Long format: permissions, owner, size, date
ls -la                 # Include hidden files (names starting with .)
cd /var/log            # Change to an absolute path
cd ~                   # Go to your home directory
cd ..                  # Go up one directory level
pwd                    # Print current directory
find /etc -name "*.conf"   # Find files matching a pattern
locate sshd_config     # Search a prebuilt database of filenames (requires updatedb)
```

### File Viewing

```bash
cat /etc/passwd              # Print entire file
cat -n file.txt              # Print with line numbers
tac /etc/passwd              # Print file in reverse (last line first)
more /etc/passwd             # Page through file (forward only)
less /etc/passwd             # Page through file (forward and backward; q to quit)
less -N /etc/passwd          # Same but with line numbers
head /etc/passwd             # Show first 10 lines
head -n 5 file.txt           # Show first 5 lines
tail /etc/passwd             # Show last 10 lines
tail -n 20 /etc/passwd       # Show last 20 lines
tail -f /var/log/messages    # Follow file in real time (useful for log monitoring)
```

### File Operations

```bash
touch emptyfile              # Create an empty file or update timestamp
vi devopsfile                # Open file in vi editor (press i to insert, Esc then :wq to save)
cp file.txt /tmp/            # Copy file to /tmp/
cp -r mydir /tmp/            # Copy directory recursively
mv oldname newname           # Rename a file or directory
mv file.txt /tmp/            # Move file to another location
rm file.txt                  # Delete a file
rm -r mydir                  # Delete a directory and its contents
```

### Directory Operations

```bash
mkdir devops                           # Create a single directory
mkdir dir1 dir2 dir3                   # Create multiple directories at once
mkdir -p SoftTech/{Admin,Dev,Ops}      # Create a nested tree structure
tree SoftTech                          # Show directory tree (install with: dnf install tree)
```

### Hidden Files and Special Characters

Files and directories beginning with a dot are hidden from `ls` by default.

```bash
mkdir .hiddendir
touch .hiddenfile
ls        # Hidden files do not appear
ls -a     # All files including hidden ones appear
```

Files with spaces or special characters in their names require quoting or escaping:

```bash
touch "backup file"
mkdir "my new @dir"
mkdir back\ up\ directory
```

### Path Specifications

An absolute path starts from the root `/` and is unambiguous regardless of where you are:

```bash
cd /home/cnode/SoftTech/Dev
```

A relative path starts from the current directory:

```bash
cd ../../Ops          # Go up two levels then into Ops
```

### Searching Within Files

```bash
grep phpdev /etc/passwd               # Search for pattern in a file
cat /etc/passwd | grep javadev        # Pipe output into grep
grep -r "404" /var/www/html/          # Recursive search through all files in a directory
grep -n "error" /var/log/messages     # Show line numbers with matches
```

### Pipelines

A pipeline connects commands so the output of one becomes the input of the next:

```bash
cat /etc/passwd | grep '/bin/bash' | wc -l    # Count users with bash as their shell
ps aux | sort -rk 3,3 | head -n 5             # Top 5 processes by CPU usage
ls -l | grep ".conf"                           # Filter ls output
```

### I/O Redirection

```bash
echo "Hello" > output.txt           # Write to file (overwrite)
echo "World" >> output.txt          # Append to file
cat < output.txt                    # Feed file as input
ls /nonexistent 2> error.log        # Redirect stderr to a file
ls /nonexistent &> all.log          # Redirect both stdout and stderr
command > /dev/null 2>&1            # Discard all output
```

### Compression and Archiving

**Compression tools:**

| Tool | Compress | Keep original | Decompress |
|---|---|---|---|
| gzip | `gzip words` | `gzip -k words` | `gunzip words.gz` |
| bzip2 | `bzip2 words` | `bzip2 -k words` | `bunzip2 words.bz2` |
| xz | `xz words` | `xz -k words` | `unxz words.xz` |
| zip | `zip words.zip words` | (zip never deletes) | `unzip words.zip` |

**tar for archiving multiple files:**

`tar` packages files together. Add compression flags to compress at the same time.

| Flag | Meaning |
|---|---|
| `-c` | Create a new archive |
| `-x` | Extract from an archive |
| `-v` | Verbose: list files as they are processed |
| `-f` | Specify the archive filename |
| `-z` | Compress/decompress with gzip (.tar.gz) |
| `-j` | Compress/decompress with bzip2 (.tar.bz2) |
| `-J` | Compress/decompress with xz (.tar.xz) |
| `-t` | List contents without extracting |

```bash
# Create archive
tar -cvf backup.tar file1 file2 dir1

# Create compressed archive
tar -czvf archive.tar.gz file1 dir1

# List contents
tar -tvf archive.tar
tar -tzvf archive.tar.gz

# Extract
tar -xvf archive.tar
tar -xzvf archive.tar.gz
```

### System Information Commands

```bash
hostname                    # System hostname
uname -a                    # Kernel name, hostname, version, architecture
hostnamectl                 # Detailed host and OS metadata
cat /etc/os-release         # Distribution name and version
lscpu                       # CPU architecture summary
cat /proc/cpuinfo           # Detailed per-CPU information
free -h                     # RAM and swap usage in human-readable format
cat /proc/meminfo           # Detailed memory statistics
vmstat                      # CPU, memory, and I/O activity snapshot
lsblk                       # List block devices and mount points
df -h                       # Disk usage for mounted filesystems
uptime                      # System uptime and load averages
who                         # Users currently logged in
id                          # Current user's UID, GID, and group memberships
top                         # Real-time process and resource view (interactive)
htop                        # Enhanced interactive process viewer (if installed)
```

### Linux Filesystem Hierarchy

| Path | Purpose |
|---|---|
| `/` | Root of the entire filesystem |
| `/boot` | Boot loader, kernel image, and initrd |
| `/dev` | Device files (disks, terminals, etc.) |
| `/etc` | System-wide configuration files |
| `/home` | User home directories |
| `/lib` | Shared libraries for `/bin` and `/sbin` |
| `/media` | Mount points for removable media |
| `/mnt` | Temporary mount points |
| `/opt` | Optional third-party application packages |
| `/proc` | Virtual filesystem: process and kernel information |
| `/root` | Home directory for the root user |
| `/run` | Runtime data since last boot |
| `/sbin` | System administration binaries |
| `/srv` | Data served by system services |
| `/sys` | Virtual filesystem exposing kernel and hardware info |
| `/tmp` | Temporary files, cleared on reboot |
| `/usr` | User utilities and applications |
| `/usr/bin` | User commands |
| `/usr/local` | Locally installed software (not managed by the package manager) |
| `/var` | Variable data: logs, mail spools, caches |
| `/var/log` | System and application log files |

---

## 2. Getting Help in Linux

### `man` — Manual Pages

```bash
man ls
man ssh
man firewall-cmd
```

Navigation inside man:
- Arrow keys or Page Up / Page Down — scroll
- `/text` — search forward; `n` next match; `N` previous match
- `q` — quit

### `--help`

Quick usage summary, faster than man:

```bash
ls --help
cp --help
ls --help | grep sort    # Filter help output
```

### `info`

More detailed documentation for GNU tools:

```bash
info ls
info mv
```

Navigation: `n` next node, `p` previous node, `u` up to parent, `q` quit.

### Finding Commands

```bash
apropos copy             # Search man page descriptions for a keyword
whatis tar               # One-line description of a command
type ls                  # How the shell resolves a command (binary, alias, builtin)
which python3            # Full path of the executable in PATH
whereis ls               # Location of binary, source, and man pages
```

---

## 3. Managing Users and Groups

User and group management is a core responsibility for DevOps engineers. Access control, security auditing, and automation all depend on correctly managed users and groups.

### Key Concepts

**User types:**
- Normal users: people who log in and run applications
- System accounts: used by services and daemons (www-data, nobody, sshd); do not log in interactively
- Root: full administrative access to everything on the system

**Group types:**
- Primary group: assigned at user creation; files created by the user belong to this group
- Secondary groups: additional group memberships that extend a user's access

Important files:
- `/etc/passwd` — user account information: `username:x:UID:GID:comment:home:shell`
- `/etc/shadow` — encrypted passwords and password policy
- `/etc/group` — group definitions: `groupname:x:GID:members`

### Group Management

```bash
groupadd developer                      # Create a group
groupadd -g 1009 admin                  # Create with a specific GID
groupmod -n administration admin        # Rename group 'admin' to 'administration'
groupdel developer                      # Delete a group
cat /etc/group                          # View all groups
getent group                            # Query the group database
```

### User Management

```bash
useradd harry                           # Create a user (no home directory by default on RHEL)
useradd -m harry                        # Create user with home directory
useradd -m -s /bin/bash -G wheel thomas # Create user with home dir, bash shell, and sudo group
useradd -g developer -G operation david # Set primary and secondary groups

passwd harry                            # Set or change harry's password
passwd -l natasha                       # Lock an account (disables password login)
passwd -u natasha                       # Unlock an account

su - thomas                             # Switch to user thomas (full login shell)
whoami                                  # Confirm current user
exit                                    # Return to previous user

cat /etc/passwd | grep harry            # Verify user was created
groups harry                            # Show harry's group memberships
```

### Modifying Existing Users

```bash
usermod -a -G operation thomas          # Add thomas to the operation group (append, not replace)
usermod -g developer thomas             # Change thomas's primary group to developer
usermod -s /bin/bash thomas             # Change thomas's login shell
usermod -l newname oldname              # Rename a user account
usermod -d /new/home -m username        # Move home directory

userdel david                           # Delete user but keep home directory
userdel -r david                        # Delete user and remove home directory and mail spool
```

### Sudo Management

Edit the sudoers file only with `visudo`. It validates syntax before saving, preventing you from locking yourself out.

```bash
sudo visudo
```

Common sudoers entries:

```
# Full admin access for alice
alice ALL=(ALL:ALL) ALL

# Allow bob to manage only nginx
bob ALL=(ALL) /usr/bin/systemctl restart nginx, /usr/bin/systemctl status nginx

# Group-based full sudo
%wheel ALL=(ALL) ALL

# Passwordless sudo for backup operations
%backup ALL=(ALL) NOPASSWD: /usr/bin/rsync

# Log all sudo commands
Defaults logfile="/var/log/sudo.log"
```

---

## 4. Managing Permissions and Ownership

### Viewing Permissions

```bash
ls -l file.txt          # Show file permissions
ls -ld directory/       # Show directory permissions
```

Permissions are shown as: `-rwxr-xr--`

- Character 1: file type (`-` = file, `d` = directory, `l` = symlink)
- Characters 2-4: owner permissions (user)
- Characters 5-7: group permissions
- Characters 8-10: others permissions

### Permission Values

| Permission | Symbol | Numeric |
|---|---|---|
| Read | r | 4 |
| Write | w | 2 |
| Execute | x | 1 |
| None | - | 0 |

Add values for each class: `rwx` = 7, `r-x` = 5, `r--` = 4, `---` = 0.

### `chmod` — Change Permissions

```bash
# Symbolic notation
chmod u+x script.sh              # Add execute for the owner
chmod g-w file.txt               # Remove write for the group
chmod a=rw file.txt              # Set read+write for everyone
chmod u=rwx,g=rx,o= mydir        # Owner: full; Group: read+execute; Others: none

# Octal notation
chmod 755 mydir                  # rwxr-xr-x
chmod 644 file.txt               # rw-r--r--
chmod 700 script.sh              # rwx------
chmod 750 mydir                  # rwxr-x---
chmod 500 mydir                  # r-x------
```

### `chown` — Change Ownership

```bash
sudo chown natasha file.txt              # Change owner to natasha
sudo chown natasha:developer file.txt   # Change owner and group
sudo chown -R harry htmldir             # Recursively change owner of directory
```

### `chgrp` — Change Group

```bash
sudo chgrp developer file.txt          # Change group ownership only
sudo chgrp -R team shared_dir/         # Recursively change group
```

### `umask` — Default Permission Mask

`umask` determines the permissions removed from newly created files and directories.

Default permissions: files start at 666, directories at 777. The umask is subtracted.

```bash
umask           # Show current umask (usually 022)
umask 022       # Files get 644, directories get 755
umask 027       # Files get 640, directories get 750
```

To set permanently for the current user:

```bash
echo "umask 022" >> ~/.bashrc
source ~/.bashrc
```

### Special Permissions

**Sticky bit:** Prevents users from deleting files they do not own in a shared directory. The `/tmp` directory uses this.

```bash
chmod +t /shared/dir                   # Add sticky bit (symbolic)
chmod 1777 /shared/dir                 # Full permissions + sticky bit (octal)
ls -ld /tmp                            # Verify: shows 't' at the end of permissions
```

**Setuid:** Execute a file with the owner's permissions rather than the caller's.

```bash
chmod u+s /usr/bin/myprog              # Add setuid
chmod 4755 /usr/bin/myprog             # Same using octal
ls -l /usr/bin/myprog                  # Shows 's' in owner execute position: rwsr-xr-x
```

**Setgid:** On files, runs with the group's permissions. On directories, new files inherit the directory's group.

```bash
chmod g+s /shared/dir                  # Add setgid on directory
chmod 2770 /shared/dir                 # rwxrws---
```

### Access Control Lists (ACLs)

ACLs extend the standard permission model to allow per-user and per-group permission assignments.

```bash
getfacl file.txt                                      # View ACLs on a file
setfacl -m u:natasha:rwx file.txt                     # Grant natasha full access
setfacl -m g:developer:r-- file.txt                   # Grant developer group read-only
setfacl -x u:natasha file.txt                         # Remove natasha's ACL entry
setfacl -b file.txt                                   # Remove all ACL entries
setfacl -R -m g:dev:r-- dir/                          # Apply recursively to a directory
setfacl -d -m u:harry:rwx dir/                        # Set default ACL (inherited by new files)
```

Note: The filesystem must be mounted with ACL support. On most modern Linux distributions this is enabled by default. If not, add `acl` to the mount options in `/etc/fstab`.

---

## 5. Package Management

### Package Managers by Distribution

| Distribution | High-level tool | Low-level tool |
|---|---|---|
| RHEL, CentOS Stream, Fedora | `dnf` | `rpm` |
| Debian, Ubuntu | `apt` | `dpkg` |
| Arch Linux | `pacman` | — |
| openSUSE | `zypper` | `rpm` |

Note on `yum`: `yum` is a legacy alias for `dnf` on RHEL 8+ and CentOS Stream 9+. On CentOS Stream 9 and 10, `dnf` is the correct command to use. `yum` may still work as a compatibility shim but `dnf` is the authoritative tool.

### Querying Packages

```bash
dnf search apache                    # Search for packages by keyword
dnf search *database*                # Wildcard search
dnf info httpd                       # Show detailed info about a package
dnf info gzip

dnf list installed                   # List all installed packages
rpm -qa | grep httpd                 # List installed packages matching a name
rpm -qf /usr/bin/tar                 # Find which package owns a file
rpm -ql httpd                        # List all files provided by a package
```

### Installing and Removing Packages

```bash
sudo dnf update                       # Update all packages
sudo dnf install httpd -y             # Install Apache
sudo dnf install git mariadb nginx    # Install multiple packages
sudo dnf remove httpd -y              # Remove a package
sudo dnf autoremove                   # Remove unused dependencies

# From a local RPM file
sudo dnf install ./package.rpm        # DNF resolves dependencies automatically
sudo rpm -ivh package.rpm             # RPM installs directly; no dependency resolution
```

### Ubuntu/Debian Package Management

```bash
sudo apt update                       # Refresh package lists
sudo apt install nginx -y             # Install a package
sudo apt upgrade                      # Upgrade all packages
sudo apt full-upgrade                 # Upgrade with dependency changes
sudo apt remove nginx                 # Remove (keep config files)
sudo apt purge nginx                  # Remove and delete config files
sudo apt autoremove                   # Remove unused dependencies
```

### Managing Services

```bash
sudo systemctl start httpd            # Start the service
sudo systemctl stop httpd             # Stop the service
sudo systemctl restart httpd          # Stop then start (use for major changes)
sudo systemctl reload httpd           # Reload config without stopping (use for config changes)
sudo systemctl enable httpd           # Enable service to start at boot
sudo systemctl disable httpd          # Disable auto-start at boot
systemctl status httpd                # Check if the service is running
systemctl is-enabled httpd            # Check if enabled at boot
```

The difference between restart and reload: `restart` stops and starts the service, briefly interrupting connections. `reload` re-reads the configuration file without dropping connections. Use `reload` when you change an Apache or Nginx configuration file and need it applied without downtime.

### systemd Unit Files

```bash
ls /usr/lib/systemd/system/           # Unit files from installed packages
ls /etc/systemd/system/               # Unit files created or modified by administrators
sudo systemctl daemon-reload          # Reload systemd after editing unit files
systemctl list-dependencies httpd     # Show what httpd depends on
```

### Troubleshooting Services

```bash
journalctl -u httpd                   # View logs for a specific service
journalctl -u httpd -f                # Follow logs in real time
journalctl -u httpd --since today     # Logs since midnight
journalctl -p err -u httpd            # Show only errors
journalctl --since "2025-01-01 00:00:00"
systemd-analyze verify httpd.service  # Validate unit file syntax
ss -tlnp | grep :80                   # Confirm Apache is listening on port 80
```

### Installing Software from Source (Binaries)

When a package is not available in repositories, download and install pre-compiled binaries.

**Example: Install Node.js 22.x on CentOS Stream 9/10**

Node.js follows a predictable LTS schedule. Even-numbered versions transition into Long-Term Support and are maintained for a longer period, typically 36 months. As of the course revision date (June 2026), Node.js 20 reached end of life on April 30, 2026. The current LTS version is **Node.js 22.x**, which should be used instead.

```bash
# Check architecture
uname -m

# Download Node.js 22.x binary (x86_64)
wget https://nodejs.org/dist/v22.11.0/node-v22.11.0-linux-x64.tar.xz

# Extract
tar -xvf node-v22.11.0-linux-x64.tar.xz

# Install system-wide
cd node-v22.11.0-linux-x64
sudo cp -r bin include lib share /usr/local/

# Verify
node -v
npm -v
```

Always check the official Node.js release schedule at `nodejs.org/en/about/previous-releases` before downloading. Only install Active LTS or Maintenance LTS versions in lab and production environments.

---

## 6. Bash Shell Scripting

### Terminal vs Shell

| Component | Function | Examples |
|---|---|---|
| Shell | Executes commands and scripts | bash, zsh, sh, fish |
| Terminal emulator | Hosts the shell and handles display | GNOME Terminal, xterm, iTerm2 |

Bash (Bourne Again SHell) is the default shell on most Linux distributions and the standard for DevOps scripting.

### Script Structure

Every Bash script should start with a shebang line identifying the interpreter:

```bash
#!/bin/bash
# This is a comment

echo "Hello from my first script"
echo "Working directory: $PWD"
```

Make the script executable and run it:

```bash
chmod +x scriptexample.sh
./scriptexample.sh
```

### Variables

```bash
# Define a variable (no spaces around =)
name="phpdev"
count=10
app="nginx"

# Reference variables with $
echo "Hello, $name"
echo "Count is $count"
echo "App: $app"
```

**Environment variables:**

```bash
echo $HOME      # Home directory
echo $USER      # Current user
echo $PATH      # Executable search path
echo $SHELL     # Default shell
echo $PWD       # Present working directory
```

**Export for subprocesses:**

```bash
export MY_VAR="hello"
bash -c 'echo "child sees: $MY_VAR"'
```

**Constants with `readonly`:**

```bash
readonly PI=3.14159
declare -r MAX_USERS=100
```

**Local variables in functions:**

```bash
my_func() {
  local temp="only visible inside this function"
  echo "$temp"
}
my_func
echo "$temp"    # Empty; local variable is out of scope
```

**Reading user input:**

```bash
read -p "Enter hostname: " host
echo "Target: $host"

read -sp "Enter password: " secret    # -s hides input
echo ""
```

### Data Types

Bash treats all variables as strings by default. Use arithmetic context `$(( ))` or `let` for integer math, and `bc` for floating-point calculations.

```bash
# Integer arithmetic
a=5
b=3
sum=$((a + b))
echo $sum

let "result = a * b"
echo $result

# Float via bc
float_result=$(echo "3.14 + 2.71" | bc)
echo $float_result

# Boolean simulation (0 = true, non-zero = false)
is_valid=true
if [ "$is_valid" = "true" ]; then
    echo "Valid"
fi
```

### Operators

**Arithmetic:** `+`, `-`, `*`, `/`, `%`, `**`, `++`, `--`

**Comparison (numeric, inside `[ ]` or `[[ ]]`):**

| Operator | Meaning |
|---|---|
| `-eq` | Equal |
| `-ne` | Not equal |
| `-lt` | Less than |
| `-le` | Less than or equal |
| `-gt` | Greater than |
| `-ge` | Greater than or equal |

**String comparison:**

| Operator | Meaning |
|---|---|
| `=` or `==` | Equal |
| `!=` | Not equal |
| `-z` | String is empty |
| `-n` | String is not empty |

**File tests:**

| Operator | Meaning |
|---|---|
| `-e` | File exists |
| `-f` | Regular file |
| `-d` | Directory |
| `-r` | Readable |
| `-w` | Writable |
| `-x` | Executable |
| `-s` | Size greater than zero |

**Logical:**

| Operator | Meaning |
|---|---|
| `&&` | AND |
| `\|\|` | OR |
| `!` | NOT |

### Control Structures

**if / elif / else:**

```bash
read -p "Enter your age: " age
if [ $age -ge 18 ]; then
  echo "Adult"
elif [ $age -ge 13 ]; then
  echo "Teenager"
else
  echo "Child"
fi
```

Use `[ ]` (POSIX test) or `[[ ]]` (Bash extended test). `[[ ]]` is safer: it handles empty variables without errors and supports pattern matching with `==` and regex with `=~`.

```bash
path="/etc/passwd"
x=15

# POSIX style
if [ -f "$path" ] && [ -r "$path" ]; then
  echo "Readable file"
fi

# Bash style (safer)
if [[ -f $path && -r $path ]]; then
  echo "Readable file"
fi

# Arithmetic context
if (( x > 10 )); then
  echo "x is greater than 10"
fi
```

**case statement:**

Use `case` instead of long if/elif chains when matching a single value against multiple patterns.

```bash
case $1 in
  start)
    echo "Starting service..."
    ;;
  stop)
    echo "Stopping service..."
    ;;
  restart)
    echo "Restarting service..."
    ;;
  *)
    echo "Usage: $0 {start|stop|restart}"
    ;;
esac
```

Confirmation prompt example:

```bash
read -p "Remove all logs? (y/N): " ans
case "$ans" in
  y|Y|yes|Yes)
    echo "Removing logs..."
    ;;
  n|N|no|No|"")
    echo "Aborted."
    ;;
  *)
    echo "Please answer yes or no."
    ;;
esac
```

### Loops

**for loop:**

```bash
# List iteration
for fruit in apple banana cherry; do
  echo "Fruit: $fruit"
done

# Numeric range (brace expansion)
for i in {1..24}; do
  echo "Number: $i"
done

# C-style numeric loop
for ((i=0; i<5; i++)); do
  echo "i is $i"
done

# Iterate over array
arr=("one" "two with space" "three")
for item in "${arr[@]}"; do
  echo "Item: $item"
done

# Iterate over files
for file in *.txt; do
  [ -e "$file" ] || { echo "No .txt files"; break; }
  echo "Found: $file"
done
```

**while loop:**

```bash
# Counter
count=1
while (( count <= 5 )); do
  echo "Count: $count"
  ((count++))
done

# Wait for a file to appear
FILE="${1:-myfile.txt}"
echo "Waiting for $FILE..."
while [ ! -f "$FILE" ]; do
  sleep 1
done
echo "$FILE is now present."
```

**until loop:**

Runs while the condition is false (opposite of while):

```bash
count=1
until [ "$count" -gt 10 ]; do
  echo "Count: $count"
  ((count++))
done
```

**break and continue:**

```bash
for i in {1..10}; do
  if (( i == 3 )); then
    continue     # Skip 3
  fi
  if (( i == 7 )); then
    break        # Stop at 7
  fi
  echo "Value: $i"
done
# Prints 1, 2, 4, 5, 6
```

### Functions

```bash
# Basic function
greet_user() {
  echo "Hello, $1 $2!"
}
greet_user "Ram" "Bahadur"

# Return value via stdout
add_numbers() {
  local sum=$(( $1 + $2 ))
  echo "$sum"
}
result=$(add_numbers 5 7)
echo "Sum is $result"

# Return status code
is_even() {
  (( $1 % 2 == 0 )) && return 0 || return 1
}
if is_even 4; then
  echo "even"
else
  echo "odd"
fi
```

### Making Scripts Globally Available

```bash
mkdir ~/bin
mv deploy.sh ~/bin/
chmod +x ~/bin/deploy.sh
echo 'export PATH=$PATH:~/bin' >> ~/.bashrc
source ~/.bashrc
deploy.sh    # Now runs from anywhere
```

### Debugging

```bash
bash -x script.sh           # Trace every command as it executes

# Inside a script, enable/disable tracing:
set -x          # Start tracing
echo "debug"
ls
set +x          # Stop tracing
```

### Exit Status

Every command returns an exit status. `0` means success. Any other value means failure.

```bash
ls /tmp
echo $?       # 0 (success)

ls /no/such/path
echo $?       # 2 (failure)
```

In scripts, use `exit` to return a status to the caller:

```bash
#!/usr/bin/env bash
if [ ! -f "$1" ]; then
  echo "File not found" >&2
  exit 1
fi
echo "File exists"
exit 0
```

---

## 7. Scheduling Tasks and Viewing Logs

### 7.1 Cron for Recurring Jobs

Cron runs commands on a schedule. Each user has their own crontab, and system-wide cron configuration exists in `/etc/crontab` and `/etc/cron.d/`.

```bash
crontab -e          # Edit your crontab
crontab -l          # List your current cron jobs
crontab -r          # Remove all your cron jobs (careful)
sudo crontab -u username -e    # Edit another user's crontab (root only)
```

**Service names:**
- RHEL / CentOS / Fedora: `crond` — check with `systemctl status crond`
- Debian / Ubuntu: `cron` — check with `systemctl status cron`

**Cron expression format (5 fields):**

```
Minute  Hour  Day-of-Month  Month  Day-of-Week  Command
  *       *         *          *        *        /path/to/command
```

| Field | Range | Notes |
|---|---|---|
| Minute | 0-59 | |
| Hour | 0-23 | |
| Day of Month | 1-31 | |
| Month | 1-12 | |
| Day of Week | 0-6 | 0 = Sunday |

**Operators:**
- `*` — any value
- `*/5` — every 5 units
- `1-5` — range (1, 2, 3, 4, 5)
- `1,15` — specific values (1 and 15)
- `8-18/2` — every 2 units between 8 and 18

**Aliases:**

| Alias | Equivalent |
|---|---|
| `@reboot` | Run once at startup |
| `@hourly` | `0 * * * *` |
| `@daily` | `0 0 * * *` |
| `@weekly` | `0 0 * * 0` |
| `@monthly` | `0 0 1 * *` |

**Cron examples:**

```bash
# Log who is logged in every minute
* * * * * /usr/bin/who >> $HOME/loginlist

# Every 5 minutes
*/5 * * * * /usr/local/bin/ping-health

# Daily at 3 AM with logging
0 3 * * * /usr/local/bin/backup.sh >> /var/log/backup.log 2>&1

# Weekdays at 9:15 AM
15 9 * * 1-5 /usr/local/bin/report.sh

# First of every month at 2:30 AM
30 2 1 * * /usr/local/bin/monthly.sh

# Every 2 minutes: memory and disk info
*/2 * * * * (echo "=== $(/usr/bin/date) ==="; /usr/bin/free -h; /usr/bin/df -h) >> $HOME/sysinfo
```

**Important notes:**
- Always use absolute paths for commands in cron. Cron runs with a minimal PATH.
- Redirect output to a log file or `/dev/null` — cron will email output if a local mail system is configured.
- The `%` character is special in cron (converted to newline). Escape as `\%` if needed.

**Where cron reads jobs from:**

| Location | Contents |
|---|---|
| `crontab -e` output → `/var/spool/cron/crontabs/<user>` | Per-user cron jobs (5-field format) |
| `/etc/crontab` | System crontab (6-field format: includes username) |
| `/etc/cron.d/` | Drop-in files (6-field format) |
| `/etc/cron.hourly/`, `/etc/cron.daily/`, etc. | Scripts run by `run-parts` |

**6-field format (for `/etc/crontab` and `/etc/cron.d/`):**

```
# m  h  dom  mon  dow  user  command
15   1   *    *    *   root  /usr/local/bin/rotate-keys
```

**Always set PATH and MAILTO at the top of your crontab:**

```
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
MAILTO=""    # Empty to suppress email output
```

### 7.2 One-Time Jobs with `at`

`at` runs a command once at a future time. The `atd` service must be running.

```bash
# Check atd is running
systemctl status atd

# Schedule interactively
at now + 1 minute
at> echo "Hello from at" >> ~/atjob
at> Ctrl+D    # Save and exit

# Non-interactive
echo 'echo "Hello" >> /tmp/atlog' | at now + 1 hour
at -f /path/to/script.sh 09:00 tomorrow

# Manage scheduled jobs
atq                 # List pending jobs
atrm <job_id>       # Remove a job
at -c <job_id>      # Show job contents
```

### 7.3 Viewing and Managing Logs

**Log file locations:**

| File | Contents |
|---|---|
| `/var/log/messages` | General system messages (RHEL/CentOS) |
| `/var/log/syslog` | General system messages (Debian/Ubuntu) |
| `/var/log/secure` | Authentication logs (RHEL/CentOS) |
| `/var/log/auth.log` | Authentication logs (Debian/Ubuntu) |
| `/var/log/boot.log` | Boot process messages |
| `/var/log/dnf.log` | Package manager activity |
| `/var/log/cron` | Cron job execution log (RHEL/CentOS) |
| `/var/log/nginx/` | Nginx access and error logs |

**Viewing logs:**

```bash
sudo cat /var/log/messages            # Print entire file
sudo tail -n 20 /var/log/secure       # Last 20 lines
sudo tail -f /var/log/messages        # Follow in real time
sudo less /var/log/dnf.log            # Scrollable view
grep "failed" /var/log/secure         # Filter for a pattern
grep "error" /var/log/messages | tail -20
```

**`journalctl` for systemd journals:**

```bash
journalctl                                           # All logs (oldest first)
journalctl -f                                        # Follow new entries in real time
journalctl -u nginx.service                          # Logs for nginx only
journalctl -u sshd --since "1 hour ago"
journalctl -b                                        # Logs since last boot
journalctl -p err -b                                 # Errors since boot
journalctl --since "2025-01-01" --until "2025-06-01"
journalctl -u httpd > httpd_logs.txt                 # Export logs to file
```

**Log rotation with `logrotate`:**

`logrotate` prevents log files from consuming all available disk space by archiving and removing old logs automatically.

Main config: `/etc/logrotate.conf`  
Per-service configs: `/etc/logrotate.d/`

Example Nginx configuration in `/etc/logrotate.d/nginx`:

```
/var/log/nginx/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 nginx adm
    sharedscripts
    postrotate
        systemctl reload nginx
    endscript
}
```

```bash
sudo logrotate -vf /etc/logrotate.d/nginx    # Force rotation immediately (test)
sudo logrotate -d /etc/logrotate.d/nginx     # Dry run (show what would happen)
sudo cat /var/lib/logrotate/logrotate.status # Check when last rotation ran
```

### 7.4 systemd Timers (Modern Alternative to Cron)

systemd timers are the modern replacement for cron on systems using systemd. They offer better logging, missed-run handling, and integration with systemd's dependency system.

Create two unit files:

`/etc/systemd/system/myjob.timer`:
```ini
[Unit]
Description=Run myjob daily

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

`/etc/systemd/system/myjob.service`:
```ini
[Unit]
Description=Run myjob script

[Service]
Type=oneshot
ExecStart=/usr/local/bin/myjob.sh
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now myjob.timer
systemctl list-timers                    # View all active timers
journalctl -u myjob.service             # View logs from runs
```

---

## 8. Configuring the Network

### 8.1 Networking Concepts

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

Client queries recursive resolver → resolver checks cache → queries root servers → queries TLD servers → queries authoritative server → returns IP to client.

Common resolvers: `8.8.8.8` (Google), `1.1.1.1` (Cloudflare), `9.9.9.9` (Quad9).

### 8.2 Linux Networking Commands

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

### 8.3 Persistent Network Configuration

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

### 8.4 Network Troubleshooting

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

## 9. Managing Firewalls

### 9.1 Firewall Concepts

A firewall filters incoming and outgoing network traffic based on rules. On Linux, firewalls are implemented in the kernel via the **netfilter** framework. User-space tools (`firewalld`, `nftables`, `ufw`) are interfaces to that framework.

**Stateless vs stateful:**
- Stateless: evaluates each packet independently. You must allow both request and response directions.
- Stateful (connection tracking): tracks connection state. Permitting a connection automatically allows return traffic.

`firewalld` is stateful. It uses the `nftables` backend on RHEL 8+, CentOS Stream 9+, and Fedora 32+.

### 9.2 `firewalld` (RHEL / CentOS / Fedora — Primary Tool)

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

### 9.3 `nftables`

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

### 9.4 `iptables` (Legacy Context)

`iptables` is the predecessor to `nftables`. On RHEL 9, the `iptables-nft` package is formally deprecated. On CentOS Stream 10 and RHEL 10, the `iptables` kernel module is not included by default.

You should not use `iptables` for new configurations. Know it for reading legacy documentation and troubleshooting older systems.

```bash
sudo iptables -L -n -v --line-numbers    # List all rules
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT    # Allow SSH
sudo iptables -A INPUT -s 192.168.1.100 -j DROP       # Block an IP
```

`iptables` rules are not persistent by default and are lost on reboot.

### 9.5 UFW (Ubuntu/Debian)

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

### 9.6 SELinux (RHEL / CentOS)

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

### 9.7 AppArmor (Ubuntu/Debian)

AppArmor is Ubuntu's equivalent of SELinux. It uses per-application profiles to restrict what a process can access.

```bash
sudo apparmor_status                     # Show AppArmor status
sudo aa-enforce /path/to/profile         # Set profile to enforcing mode
sudo aa-complain /path/to/profile        # Set profile to complain mode (log only)
sudo systemctl reload apparmor           # Reload profiles after changes
sudo aa-logprof                          # Interactively tune profiles based on log entries
```

Profiles are in `/etc/apparmor.d/`.

---

## 10. Process Management, System Monitoring, and Performance Tuning

### 10.1 Process Monitoring Tools

**`ps` — process snapshot:**

```bash
ps aux                      # BSD-style: all processes with CPU and memory usage
ps -ef                      # Unix-style: all processes with PID and PPID
ps auxf                     # Process tree (shows parent-child relationships)
ps -u cnode                 # Processes owned by user cnode
ps -C sshd                  # Processes named sshd
ps aux | grep nginx         # Filter by name
ps -eo pid,ppid,user,%cpu,%mem,command    # Custom columns
```

Key columns in `ps aux`:
- `USER` — process owner
- `PID` — process ID
- `%CPU` — CPU usage
- `%MEM` — memory usage
- `VSZ` — virtual memory size
- `RSS` — physical RAM in use
- `STAT` — state: R (running), S (sleeping), D (uninterruptible), Z (zombie), T (stopped)
- `COMMAND` — the command line

**`top` — real-time view:**

```bash
top
```

Interactive commands in top:

| Key | Action |
|---|---|
| `k` | Kill a process (prompts for PID) |
| `M` | Sort by memory |
| `P` | Sort by CPU |
| `u` | Filter by user |
| `1` | Show individual CPU cores |
| `q` | Quit |

**`htop` — enhanced interactive viewer:**

```bash
# Install
sudo dnf install epel-release -y && sudo dnf install htop -y    # RHEL/CentOS
sudo apt install htop -y                                         # Ubuntu/Debian

# Run
htop
```

htop key bindings:

| Key | Action |
|---|---|
| F3 | Search |
| F4 | Filter |
| F5 | Tree view |
| F6 | Sort |
| F9 | Kill process |
| F10 | Quit |

htop advantages over top: color-coded display, mouse support, vertical scrolling, easier process killing.

**Additional tools:**

```bash
pstree                      # Display process hierarchy as a tree
pstree -p                   # Include PIDs
pgrep nginx                 # Find PIDs by process name
pkill nginx                 # Send signal to processes by name
pidof sshd                  # Find PID of a named program
```

### 10.2 Process Signals

```bash
kill -15 1234               # Graceful termination (SIGTERM, default)
kill -9 1234                # Force kill (SIGKILL, cannot be caught or ignored)
kill -1 1234                # Reload config (SIGHUP)
killall -9 nginx            # Kill all processes named nginx
pkill firefox               # Kill by name
```

Prefer SIGTERM (15) over SIGKILL (9). SIGTERM allows the process to clean up (close files, flush data). SIGKILL terminates immediately without cleanup, which can leave files corrupted.

**Zombie processes:** A process that has finished but whose parent has not yet collected its exit status. The entry remains in the process table. Usually harmless in small numbers. If zombies accumulate, the parent process has a bug.

### 10.3 Background Job Control

```bash
sleep 60 &              # Start a command in the background
jobs                    # List current background jobs
jobs -l                 # List with PIDs

fg %1                   # Bring job 1 to the foreground
Ctrl+Z                  # Suspend the current foreground job
bg %1                   # Resume job 1 in the background

kill %1                 # Terminate background job 1
disown %1               # Detach job from shell (survives terminal close)

nohup ./script.sh &     # Run and ignore hangup signal (survives logout)
```

Job references: `%1` = job number 1, `%sleep` = job named sleep, `%%` = current job.

### 10.4 System Performance Monitoring

**`vmstat` — virtual memory statistics:**

```bash
vmstat 1            # One snapshot per second
vmstat 2 10         # Every 2 seconds, 10 times
```

Key metrics: `r` (run queue length), `b` (processes in uninterruptible sleep), `swpd` (swap used), `wa` (I/O wait), `us`/`sy`/`id` (user/system/idle CPU).

**`iostat` — I/O statistics:**

```bash
sudo dnf install sysstat -y
iostat
iostat -x 1             # Extended I/O stats, 1-second interval
```

Key metrics: `%util` (device utilization), `await` (I/O response time), `r/s` and `w/s` (reads/writes per second).

**`sar` — system activity reporter:**

```bash
sudo systemctl enable sysstat && sudo systemctl start sysstat
sar -u              # CPU statistics
sar -r              # Memory usage
sar -b              # I/O statistics
sar -u 1 5          # CPU every 1 second, 5 times
```

### 10.5 Setting Resource Limits

**`ulimit` — per-session limits:**

```bash
ulimit -a               # Show all current limits
ulimit -n               # Open file descriptors
ulimit -u               # Maximum user processes
ulimit -n 4096          # Set file descriptor limit for current session
```

**Persistent limits** — edit `/etc/security/limits.conf`:

```
# user  type   resource   limit
alice   soft   nofile     4096
alice   hard   nofile     8192
@admins soft   nproc      2048
*       hard   core       0       # Disable core dumps for all users
```

Limits are applied at login. Existing sessions are not affected.

---

## 11. Remote Login with SSH

### 11.1 SSH Overview

SSH (Secure Shell) encrypts all communication between client and server. It replaced insecure protocols like Telnet and rsh. SSH operates on TCP port 22 by default.

The typical connection sequence:
1. Client connects to server on port 22.
2. Server presents its host key (verified against `~/.ssh/known_hosts`).
3. Client authenticates (password or public key).
4. Encrypted session begins.

### 11.2 Basic SSH Connection

```bash
ssh username@192.168.1.10                   # Connect on default port 22
ssh -p 2222 username@192.168.1.10          # Connect on custom port
ssh -i ~/.ssh/id_ed25519 username@host     # Specify a private key
```

### 11.3 SSH Server Configuration

Edit `/etc/ssh/sshd_config` to harden the server. Reload after changes.

```
Port 2222                          # Change default port
PermitRootLogin no                 # Disallow direct root login
PasswordAuthentication no          # Require key-based authentication
PubkeyAuthentication yes           # Enable public key authentication
AllowUsers alice bob charlie       # Whitelist specific users
MaxAuthTries 3                     # Limit authentication attempts
ClientAliveInterval 300            # Send keepalive every 300 seconds
ClientAliveCountMax 2              # Disconnect after 2 missed keepalives
X11Forwarding no                   # Disable X11 forwarding
AllowTcpForwarding no              # Disable TCP forwarding (unless needed)
```

After editing:

```bash
sudo systemctl reload sshd
```

If you change the SSH port, update SELinux and the firewall:

```bash
sudo semanage port -a -t ssh_port_t -p tcp 2222
sudo firewall-cmd --permanent --add-port=2222/tcp
sudo firewall-cmd --permanent --remove-service=ssh
sudo firewall-cmd --reload
```

### 11.4 SSH Client Configuration

`~/.ssh/config` lets you define connection shortcuts:

```
Host webserver
    HostName 192.168.1.100
    User admin
    Port 2222
    IdentityFile ~/.ssh/id_ed25519

Host bastion
    HostName bastion.example.com
    User jumpuser
    Port 22

Host internal-web
    HostName 10.0.1.10
    User webadmin
    ProxyJump bastion             # Connect via bastion host

Host db-tunnel
    HostName db.example.com
    LocalForward 3306 127.0.0.1:3306    # Forward local port to remote DB
```

Usage:

```bash
ssh webserver                             # Connect using the alias
ssh db-tunnel                             # Establish tunnel then connect to localhost:3306
```

### 11.5 Key-Based Authentication

Key-based authentication is more secure than passwords. A key pair consists of:
- **Private key**: stays on your machine, never shared
- **Public key**: placed on the server in `~/.ssh/authorized_keys`

Authentication works by the server sending a challenge encrypted with your public key; only your private key can decrypt it.

**Generating keys:**

Ed25519 has been the OpenSSH-recommended default since version 7.0 (2015). Every modern SSH server supports it. Use Ed25519 for all new key generation.

```bash
ssh-keygen -t ed25519 -a 100 -C "cnode@hostname" -f ~/.ssh/id_ed25519
```

RSA remains an option for legacy systems that do not support Ed25519:

```bash
ssh-keygen -t rsa -b 4096 -C "cnode@hostname" -f ~/.ssh/id_rsa
```

Generated files:
- Private key: `~/.ssh/id_ed25519` (keep this secret)
- Public key: `~/.ssh/id_ed25519.pub` (copy this to servers)

**Correct permissions:**

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519           # Private key: owner read/write only
chmod 644 ~/.ssh/id_ed25519.pub       # Public key: readable by others
chmod 600 ~/.ssh/authorized_keys      # Authorized keys: owner read/write only
```

SSH will refuse to use a private key with loose permissions.

**Copying the public key to a server:**

```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub username@server    # Automatic
# or manually:
cat ~/.ssh/id_ed25519.pub | ssh username@server "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

**SSH Agent:**

The SSH agent holds your private key in memory so you enter the passphrase once per session:

```bash
eval "$(ssh-agent -s)"          # Start the agent
ssh-add ~/.ssh/id_ed25519       # Load your key
ssh-add -l                      # List loaded keys
ssh-add -D                      # Remove all keys from agent
```

**Disabling password authentication (after confirming key login works):**

In `/etc/ssh/sshd_config`:

```
PasswordAuthentication no
ChallengeResponseAuthentication no
```

```bash
sudo systemctl reload sshd
```

### 11.6 File Transfers Over SSH

**SCP — Secure Copy:**

```bash
scp file.txt user@remote:/path/                 # Local to remote
scp user@remote:/path/file.txt ./               # Remote to local
scp -r /local/dir/ user@remote:/path/           # Recursive directory copy
scp -P 2222 file.txt user@remote:/path/         # Custom port
```

**rsync — efficient synchronization:**

rsync only transfers changed portions of files, making it far faster than scp for large datasets or repeated syncs.

```bash
rsync -avz /local/dir/ user@remote:/remote/dir/             # Sync with compression
rsync -avz --delete /local/dir/ user@remote:/remote/dir/    # Mirror (delete remote extras)
rsync -avz -e "ssh -p 2222" /local/ user@remote:/remote/    # Custom SSH port
rsync -avz --partial /large/file user@remote:/path/          # Resume interrupted transfer
```

Flags: `-a` archive (preserve timestamps, permissions, symlinks), `-v` verbose, `-z` compress.

**SSHFS — mount remote directory as local:**

```bash
sudo dnf install -y fuse-sshfs    # Install (RHEL/CentOS)

sshfs user@remote:/remote/path /local/mountpoint             # Mount
sshfs user@remote:/remote/path /local/mountpoint -p 2222    # Custom port

fusermount -u /local/mountpoint                              # Unmount
```

### 11.7 SSH Hardening Summary

| Setting | Recommendation |
|---|---|
| SSH port | Change from 22 to a non-standard port |
| Root login | Disable (`PermitRootLogin no`) |
| Password auth | Disable (`PasswordAuthentication no`) |
| Key type | Ed25519 |
| Allowed users | Whitelist with `AllowUsers` |
| Auth tries | Limit with `MaxAuthTries 3` |
| Idle timeout | Set `ClientAliveInterval 300` and `ClientAliveCountMax 2` |
| Brute force | Install and configure Fail2Ban |
| Forwarding | Disable X11 and TCP forwarding if not needed |

**Fail2Ban — automatic IP banning after repeated failures:**

```bash
sudo dnf install fail2ban -y          # RHEL/CentOS
sudo apt install fail2ban -y          # Ubuntu/Debian
```

Configure `/etc/fail2ban/jail.local`:

```ini
[sshd]
enabled  = true
port     = 2222
filter   = sshd
logpath  = /var/log/secure
maxretry = 3
findtime = 600
bantime  = 3600
```

```bash
sudo systemctl enable --now fail2ban
sudo fail2ban-client status sshd        # Check status and ban list
```

### 11.8 Troubleshooting SSH

```bash
ssh -vvv -p 2222 user@host              # Verbose debug output
ls -la ~/.ssh/                          # Check key permissions
systemctl status sshd                   # Is the server running?
journalctl -u sshd --since "1 hour ago"  # Server-side logs
tail -f /var/log/secure                 # Authentication log (RHEL/CentOS)
nmap -p 2222 hostname                   # Verify port is open from outside
```

Common issues:
- Permission denied (publickey): wrong key, wrong permissions on `~/.ssh/`, key not in `authorized_keys`
- Connection refused: sshd not running, wrong port, firewall blocking
- Connection timeout: firewall rule missing, host unreachable, wrong IP

---

*End of Module 3, Section 3.1: Linux for DevOps*

*Next - Section 4:  Web and Application Servers*

---
