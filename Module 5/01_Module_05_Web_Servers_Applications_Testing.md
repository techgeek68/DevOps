# Module 5: Web Servers, Applications, and Testing Strategy

**Module objective.** Deploy web and application services and construct a delivery friendly reference application governed by a layered test suite. *Supports CLO 5.*

**How this module is organised.** The module moves from infrastructure to application to pipeline:

- **Section 5.1 Web and Application Servers.** 

Where each server sits, the process models of the two dominant web servers, virtual hosts, reverse proxying, and where to terminate TLS.

- **Section 5.2 Delivery Friendly Applications and the Twelve Factor Model.** 

The application properties that make automated delivery possible, and which parts of the twelve factor model still hold.

- **Section 5.3 Testing Strategy.** 

The test pyramid, contract testing, test data management, and the decision to quarantine a flaky test.

- **Section 5.4 Pipeline Speed as a Product Feature.** 

Caching, parallelism, and selective scheduling.

Sections 5.2 – 5.4 all operate on one **reference application** that is introduced in Section 5.2 and reused throughout, so the module builds a single coherent artefact rather than a set of disconnected exercises.

---
# Section 5.1: Web and Application Servers

---

# Theory

---
## 1. Web Servers vs. Application Servers

A **web server** handles HTTP and HTTPS requests. Its primary job is serving static content (HTML, CSS, JavaScript, images) and, optionally, forwarding dynamic requests to backend processes. Examples: Nginx, Apache HTTP Server.

An **application server** executes application code to generate responses. It handles business logic, database queries, and session management. Examples: Apache Tomcat (Java), Gunicorn (Python), Node.js.

In practice these roles overlap and are commonly combined. A typical architecture is: **Nginx as the front layer** receiving all traffic, serving static files directly, and proxying dynamic requests to an application server running behind it.

```
Client → Nginx (reverse proxy / TLS termination / static files)
               ↓ proxy_pass
         Application Server (Tomcat / Gunicorn / Node)
               ↓
         Database (PostgreSQL / MySQL / MongoDB)
```

**Where each sits, and why it matters.** The web server sits at the *edge*, closest to the client; the application server sits *behind* it, closest to the data. This separation is important in DevOps because it lets you scale the two independently, terminate TLS in one well understood place, serve static assets without waking application code, and isolate failures. The same separation reappears in Section 5.2, where the application is deliberately built to be a small, stateless unit that any edge server can sit in front of.

---
## 2. Process Models of the Two Dominant Web Servers

The two web servers that dominate the market are Nginx and Apache HTTP Server. They differ most fundamentally in their **process model** how they turn incoming connections into work. Understanding the process model is what lets you predict behaviour under load.

### 2.1 Nginx: Event Driven

Nginx was released in 2004 to solve the C10K problem the challenge of handling 10,000 simultaneous connections that caused thread based servers to exhaust memory.

Nginx uses an **event driven, asynchronous, non blocking** model:

- A **master process** reads configuration and manages worker processes.

- **Worker processes** (one per CPU core by default) each run a single threaded event loop.

- A single worker can handle thousands of connections simultaneously. When waiting for a network response or disk read, it does not block it registers a callback and handles other connections in the meantime.

- No new thread or process is created per connection, so memory usage stays low and predictable under high load.

### 2.2 Apache HTTP Server: Multi Processing Modules

Apache uses interchangeable **Multi Processing Modules (MPMs)**. Only one is active at a time.

| MPM | Model | Best For |
|---|---|---|
| `mpm_prefork` | One process per connection, no threads | Legacy non-thread-safe modules (old `mod_php`) |
| `mpm_worker` | Multiple processes, each with multiple threads | Better memory efficiency than prefork |
| `mpm_event` | Worker model with async keep-alive handling | Default on modern systems; best performance |

`mpm_event` is the default on Apache 2.4+ installations. It separates keep alive connection management from request processing: a dedicated listener thread monitors idle keep alive connections and only hands them to a worker thread when a new request arrives.

### 2.3 The Contrast

Compare Nginx's event loop to Apache's `mpm_prefork`: one process per connection. Under 5,000 simultaneous connections, that is 5,000 processes each consuming RAM and requiring context switches. Nginx handles the same 5,000 connections inside a handful of worker processes. This is why Nginx is the default at the edge and Apache remains common deeper in the stack, particularly for legacy, `.htaccess`-dependent, or PHP applications.

---
## 3. Virtual Hosts

A **virtual host** lets one server serve multiple websites, distinguished by the `Host:` HTTP header the client sends. Both dominant servers support it:

- **Name based virtual hosts**: Many sites share one IP address; the server routes by hostname. This is the common case.
- **IP based virtual hosts**: Each site has its own IP address. Used when a site needs a dedicated certificate on its own IP, or protocol level isolation.

In Nginx a virtual host is a `server {}` block keyed on `server_name`. In Apache it is a `<VirtualHost>` block keyed on `ServerName`/`ServerAlias`. The labs in this section configure both.

---
## 4. Reverse Proxying

A **reverse proxy** accepts client requests at the edge and forwards them to one or more backend servers. The client communicates only with the proxy; the backends are invisible from outside the network. A reverse proxy enables:

- **TLS termination** in one place (Section 5).
- **Load balancing** across multiple backends.
- **Centralised logging and access control.**
- **Static/dynamic split** the proxy serves static files itself and forwards only dynamic requests.

Both servers can reverse-proxy: Nginx with `proxy_pass`, Apache with `mod_proxy`. In greenfield deployments Nginx is the usual choice at the edge; Apache's `mod_proxy` is chosen mainly when a team is already invested in Apache for the application itself.

---
## 5. TLS Termination and Where to Terminate

**TLS termination** is the point at which encrypted client traffic is decrypted. Choosing *where* to terminate is a genuine engineering decision, not a default, because it trades off performance, security, and operational simplicity.

### 5.1 The Three Patterns

- **Terminate at the edge (most common).** The reverse proxy or load balancer holds the certificate, decrypts, and forwards **plaintext HTTP** to backends over a trusted private network.
  - *Pros:* certificates live in one place; backends do no crypto; the edge can inspect, route, cache, and add security headers.
  - *Cons:* traffic between edge and backend is unencrypted, so the internal network must be trusted.

- **TLS passthrough.** The edge forwards the encrypted stream untouched; the **backend** terminates TLS.
  - *Pros:* end to end encryption; the edge never sees plaintext.
  - *Cons:* the edge cannot inspect, route on URL, or cache; every backend must manage certificates.

- **Re-encryption (TLS bridging).** The edge terminates TLS, inspects/routes, then opens a **second** TLS connection to the backend.
  - *Pros:* end to end encryption **and** edge inspection.
  - *Cons:* two handshakes and double the crypto cost; most operationally complex.

### 5.2 The Decision

The default for most web and application stacks is **terminate at the edge**: it centralises certificate management and keeps application servers simple. Move to **re-encryption** when a compliance regime (for example, handling regulated health or payment data) forbids plaintext even on internal links. Choose **passthrough** only when the backend must own the certificate for example, a service that performs client certificate (mTLS) authentication itself.

This is exactly why, throughout this module, **Nginx terminates TLS at the edge and forwards plaintext to Tomcat, Gunicorn, or PHP-FPM**: it is the simplest correct default, and it keeps the reference application in Section 5.2 free of any TLS concerns of its own.

---
## 6. Apache Tomcat (an Application Server)

Apache Tomcat is a Java application server that implements the Jakarta Servlet and JavaServer Pages (JSP) specifications. It runs Java web applications packaged as `.war` (Web Application Archive) files.

Tomcat is not a general web server and is not a replacement for Nginx or Apache HTTP Server. In production, Tomcat typically sits **behind Nginx**, which handles TLS termination and static files while Tomcat handles Java application requests the edge termination pattern from Section 5.

### Version and JDK Compatibility

This is the most common source of Tomcat installation failures. The versions must match:

| Tomcat Version | Required Java | Jakarta EE Spec |
|---|---|---|
| 9.0.x | Java 8 or later | Servlet 4.0 / JSP 2.3 |
| 10.1.x | Java 11 or later | Servlet 6.0 / JSP 3.1 |
| 11.0.x | Java 17 or later | Servlet 6.1 / JSP 4.0 |

Always verify your Java version before installing Tomcat. If the JDK is too old, Tomcat fails to start with a cryptic JVM error rather than a clear message about incompatibility.

### Key Tomcat Concepts

- **`CATALINA_HOME`:** The Tomcat installation directory (e.g., `/opt/tomcat`).
- **`webapps/`:** Drop `.war` files here; Tomcat auto-deploys them on startup.
- **`conf/server.xml`:** Main configuration ports, connectors, virtual hosts.
- **`conf/tomcat-users.xml`:** User credentials for the Manager web interface.
- **`logs/catalina.out`:** Main log file; always check this first when troubleshooting.
- **Manager App:** Web GUI at `http://server:8080/manager/html` for deploying and managing applications.

### Security Note

Run Tomcat as a non root user. Create a dedicated `tomcat` system account with no login shell. Never run Tomcat as root a vulnerability in a Java application could give an attacker root access to the entire server.

---
## 7. Web Server Comparison

| Feature | Nginx | Apache HTTP Server | Tomcat |
|---|---|---|---|
| Type | Web server / reverse proxy | Web server / proxy | Java application server |
| Architecture | Event driven, async, non blocking | Process/thread MPM | JVM based, multi threaded |
| Static files | Excellent | Good | Not designed for this |
| Dynamic content | Via FastCGI/proxy | Via modules or proxy | Java Servlets / JSP natively |
| Per-directory config | No `.htaccess` equivalent | `.htaccess` supported | `web.xml` per app |
| TLS | Built-in | `mod_ssl` | Via connector (but terminate at Nginx) |
| Configuration style | `server {}` and `location {}` blocks | Directives and `<VirtualHost>` blocks | XML (`server.xml`, `web.xml`) |
| Best for | Reverse proxy, edge, microservices frontend | Legacy apps, `.htaccess`-dependent apps | Java EE applications |
| DevOps role | Front of every architecture | Common in LAMP stacks | Java application hosting |

In a full pipeline you will typically use all three: **Nginx** as the public facing edge, **Apache** for PHP-based applications, and **Tomcat** for Java based applications. The Tomcat lab in this section builds the exact deployment target that the CI/CD pipeline in **Section 5.4** delivers into.

### Market Position

Nginx is the most widely deployed web server and reverse proxy. Per W3Techs (April 2026): **Nginx 32.7%, Cloudflare Server 27.7%, Apache 23.7%** of all websites with a known server. These figures move month to month; treat them as an ordering (Nginx ahead of Apache, with Cloudflare's edge proxies now a close second) rather than fixed constants.

---
---
# SELinux Reference for Web Servers

SELinux is the most common cause of web-server failures on RHEL/CentOS. The fix is almost always one of three things: a wrong file context, a missing boolean, or an unlabeled port.

## 1. Wrong File Context (most common)

### `ls -Z`: View the SELinux label on files
- Syntax
```bash
ls -Z [OPTIONS] [PATH]
```
- Example:
```bash
ls -Z /var/www/mysite/
```
>Output shows `user:role:type:level`. For web content you want the type `httpd_sys_content_t`. If you see `default_t` or `user_home_t`, that is your problem.


### `chcon`: Change context immediately (temporary)
- Syntax
```bash
chcon [-R] -t TYPE PATH
```
>`-R` recurses into directories, `-t` sets the type. The change is lost on a full filesystem relabel, so treat it as a quick test rather than a fix.

- Example:
```bash
sudo chcon -R -t httpd_sys_content_t /var/www/mysite
```

### `restorecon`: Reset context from policy (persistent)
- Syntax:
```bash
restorecon [-R] [-v] [-n] PATH
```
>`-R` recurses, `-v` prints what changed, `-n` is a dry run.

- Example
```bash
sudo restorecon -Rv /var/www/mysite
```
>Dry run first if you want to see what would change:
```bash
sudo restorecon -Rvn /var/www/mysite
```

### `semanage fcontext`: Make a custom path permanent:

If your content lives outside `/var/www`, add a policy rule so `restorecon` knows the correct type.

- Syntax:
```bash
semanage fcontext -a -t TYPE "PATH_REGEX"
```

- Example:
```bash
sudo semanage fcontext -a -t httpd_sys_content_t "/srv/mysite(/.*)?"
```

Then apply it:
```bash
sudo restorecon -Rv /srv/mysite
```

---
## 2. Missing Boolean (reverse proxy, DB connections, mod_wsgi)

### `getsebool`: Read boolean values

- Syntax:
```bash
getsebool -a
```
```bash
getsebool BOOLEAN_NAME
```

- Example
```bash
getsebool -a | grep httpd
```
```bash
getsebool httpd_can_network_connect
```

---
### `setsebool`: Change a boolean

- Syntax
```bash
setsebool [-P] BOOLEAN_NAME on|off
```
>`-P` writes the change to policy so it survives a reboot. Without `-P` it reverts.

- Example: Allow proxying to a backend
```bash
sudo setsebool -P httpd_can_network_connect 1
```

- Example: Allow direct database connections
```bash
sudo setsebool -P httpd_can_network_connect_db 1
```

- Example: Allow mod_wsgi daemon mode
```bash
sudo setsebool -P httpd_execmem 1
```

- Example: Allow Apache to write to its content directories
```bash
sudo setsebool -P httpd_unified 1
```

---
## 3. Non Standard Port

### `semanage port -a`: label a new port

- Syntax
```bash
semanage port -a -t TYPE -p PROTOCOL PORT
```
> Use `-m` instead of `-a` if the port is already defined under another type.

- Example
```bash
sudo semanage port -a -t http_port_t -p tcp 8081
```

### `semanage port -l`: list labeled ports
- Syntax
```bash
semanage port -l
```

- Example:
```bash
sudo semanage port -l | grep http_port
```

---
## 4. Reading SELinux Denial Logs

### `ausearch`: Query the audit log

- Syntax
```bash
ausearch -m MESSAGE_TYPE -ts TIME_SPEC
```
>`-m avc` filters access-vector-cache denials. `-ts` accepts `recent`, `today`, `boot`, or a timestamp.

- Example:
```bash
sudo ausearch -m avc -ts recent | grep httpd
```
```bash
sudo ausearch -m avc -ts boot
```
---
### `journalctl -t`: Human readable explanations

- Syntax
```bash
journalctl -t IDENTIFIER
```

- Example
```bash
journalctl -t setroubleshoot
```
---
### `sealert`: Full analysis with suggested fixes

- Syntax:
```bash
sealert -a LOGFILE
```

- Example:
```bash
sudo sealert -a /var/log/audit/audit.log
```
---
## Stop and Remove Services (Before Switching Labs)

Switching between Apache and Nginx labs? Stop the unused service so it releases port 80.

### `systemctl disable --now`: Stop and disable in one step

- Syntax
```bash
systemctl disable SERVICE --now
```
>`--now` stops the running unit as well as disabling it at boot.

- Example: Apache
```bash
sudo systemctl disable httpd --now
```

- Example: Nginx
```bash
sudo systemctl disable nginx --now
```

- Example: Tomcat
```bash
sudo systemctl disable tomcat --now
```

---
### `dnf remove`: Uninstall the package
- Syntax:
```bash
dnf remove PACKAGE [-y]
```

- Example
```bash
sudo dnf remove httpd -y
```
```bash
sudo dnf remove nginx -y
```

---
### `ss`: Confirm the port is actually free

- Syntax:
```bash
ss -tlnp [| grep PORT]
```
> `-t` TCP, `-l` listening, `-n` numeric ports, `-p` show the owning process.

- Example:
```bash
sudo ss -tlnp | grep :80
```
> No output means port 80 is free and the next lab can start cleanly.

---
# Laboratory Exercises

---
## Lab 5.1.A: Apache HTTP Server: Installation, Virtual Hosts, and HTTPS

### Part 1: Install and Start Apache

```bash
# Verify Apache is not already installed
rpm -q httpd

# Install Apache
sudo dnf install httpd -y

# Start and enable at boot
sudo systemctl start httpd
sudo systemctl enable httpd
sudo systemctl status httpd

# Check version
httpd -v
```

Open firewall ports:

```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
sudo firewall-cmd --list-all
```

Verify: 

- Open `http://127.0.0.1` in a browser or run `curl -I http://127.0.0.1`. 

- To verify from the Host Computer, you must use the Server's IP address.

You should see the Apache test page:

![Apache Server Test Page](<images/Apache Webserver Default Page.png>)

---
Major configuration files:

```bash
cat /etc/httpd/conf/httpd.conf       # Main configuration
ls /etc/httpd/conf.d/                # Virtual host and module configs
```

Three directives to understand in `httpd.conf`:

```
ServerRoot "/etc/httpd"            # Base directory for all Apache config files
DocumentRoot "/var/www/html"       # Where website files are served from by default
Listen 80                          # Port Apache listens on
```

Always test configuration syntax before restarting:

```bash
sudo apachectl configtest
```

---
### Part 2: Serve a Static Website

```bash
# Create website directories
sudo mkdir -p /var/www/html/{About,Notes}

# Set ownership (Apache runs as the 'apache' user on RHEL/CentOS)
sudo chown -R apache:apache /var/www/html
sudo chmod -R 755 /var/www/html

# Verify
ls -ld /var/www/html/
```

Create the homepage
```bash
sudo vim /var/www/html/index.html
```

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DevOps</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #f3f1ec;
    --panel: #ffffff;
    --ink: #2a2622;
    --muted: #746e66;
    --rule: #e2ddd3;
    --signal: #b5622f;
    --signal-soft: #f4e6dc;
  }

  * { box-sizing: border-box; }

  body {
    margin: 0;
    min-height: 100vh;
    padding: 56px 20px;
    background: var(--bg);
    color: var(--ink);
    font-family: 'Inter', sans-serif;
    line-height: 1.55;
    display: flex;
    justify-content: center;
  }

  .card {
    width: 100%;
    max-width: 580px;
    background: var(--panel);
    border: 1px solid var(--rule);
    border-radius: 12px;
    padding: 34px 36px 38px;
    box-shadow: 0 12px 30px -22px rgba(42, 38, 34, 0.45);
  }

  .eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 10px;
  }

  h1 {
    margin: 0 0 10px;
    font-size: 1.7rem;
    font-weight: 600;
  }

  p.intro {
    margin: 0 0 26px;
    color: var(--muted);
    font-size: 0.98rem;
  }

  nav {
    display: flex;
    gap: 10px;
    margin-bottom: 26px;
    flex-wrap: wrap;
  }

  nav a {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    color: var(--ink);
    text-decoration: none;
    padding: 8px 15px;
    border: 1px solid var(--rule);
    border-radius: 7px;
    transition: border-color 0.15s ease, background-color 0.15s ease, transform 0.15s ease;
  }

  nav a:hover,
  nav a:focus-visible {
    border-color: var(--signal);
    background: var(--signal-soft);
    outline: none;
    transform: translateY(-1px);
  }

  nav a:active { transform: translateY(0); }

  main p {
    margin: 0;
    padding: 14px 16px;
    background: var(--signal-soft);
    border-left: 3px solid var(--signal);
    border-radius: 6px;
    font-size: 0.95rem;
  }

  footer {
    margin-top: 26px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: var(--muted);
  }

  @media (max-width: 480px) {
    .card { padding: 26px 22px 30px; }
  }
</style>
</head>
<body>
  <div class="card">
    <div class="eyebrow">DevOps: Webserver Lab</div>
    <h1>Hey, welcome in.</h1>
    <p class="intro">This is a small Apache box I use for testing deployments and configs before they go anywhere that matters. This static site is served from <code>/var/www/html</code>.</p>
    <nav>
    <a href="About/about.html">About</a>
    <a href="Notes/note.html">Notes</a>
    </nav>
    <main>
      <p>The Apache HTTP server is up and responding as expected.</p>
    </main>
    <footer>apache · static · last checked manually</footer>
  </div>
</body>
</html>
```

Create `About` and `Notes` with similar content:

```bash
sudo vi /var/www/html/About/about.html
```
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>About: DevOps</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #f3f1ec;
    --panel: #ffffff;
    --ink: #2a2622;
    --muted: #746e66;
    --rule: #e2ddd3;
    --signal: #b5622f;
    --signal-soft: #f4e6dc;
  }

  * { box-sizing: border-box; }

  body {
    margin: 0;
    min-height: 100vh;
    padding: 56px 20px;
    background: var(--bg);
    color: var(--ink);
    font-family: 'Inter', sans-serif;
    line-height: 1.6;
    display: flex;
    justify-content: center;
  }

  .card {
    width: 100%;
    max-width: 580px;
    background: var(--panel);
    border: 1px solid var(--rule);
    border-radius: 12px;
    padding: 34px 36px 38px;
    box-shadow: 0 12px 30px -22px rgba(42, 38, 34, 0.45);
  }

  .eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 10px;
  }

  h1 {
    margin: 0 0 16px;
    font-size: 1.6rem;
    font-weight: 600;
  }

  p {
    margin: 0 0 16px;
    color: var(--ink);
    font-size: 0.98rem;
  }

  p.muted { color: var(--muted); }

  code {
    font-family: 'IBM Plex Mono', monospace;
    background: var(--bg);
    border-radius: 3px;
    padding: 1px 5px;
    font-size: 0.85em;
  }

  a.back {
    display: inline-block;
    margin-top: 10px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    color: var(--ink);
    text-decoration: none;
    padding: 8px 15px;
    border: 1px solid var(--rule);
    border-radius: 7px;
    transition: border-color 0.15s ease, background-color 0.15s ease;
  }

  a.back:hover,
  a.back:focus-visible {
    border-color: var(--signal);
    background: var(--signal-soft);
    outline: none;
  }
</style>
</head>
<body>
  <div class="card">
    <div class="eyebrow">about</div>
    <h1>Why this box exists</h1>
    <p>I keep this Apache instance around to try things out before they touch a real environment config changes, a new vhost, a deploy script that might have a typo in it. Low stakes, easy to rebuild.</p>
    <p class="muted">It runs plain static files out of <code>/var/www/html</code>, no database, no build step. If it's up and this page loads, Apache is doing its job.</p>
    <a class="back" href="../index.html">Back Home</a>
  </div>
</body>
</html>
```
```bash
sudo vi /var/www/html/Notes/note.html
```
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DevOps: Webserver Lab</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #f3f1ec;
    --panel: #ffffff;
    --ink: #2a2622;
    --muted: #746e66;
    --rule: #e2ddd3;
    --signal: #b5622f;
    --signal-soft: #f4e6dc;
  }

  * { box-sizing: border-box; }

  body {
    margin: 0;
    min-height: 100vh;
    padding: 56px 20px;
    background: var(--bg);
    color: var(--ink);
    font-family: 'Inter', sans-serif;
    line-height: 1.6;
    display: flex;
    justify-content: center;
  }

  .card {
    width: 100%;
    max-width: 580px;
    background: var(--panel);
    border: 1px solid var(--rule);
    border-radius: 12px;
    padding: 34px 36px 38px;
    box-shadow: 0 12px 30px -22px rgba(42, 38, 34, 0.45);
  }

  .eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 10px;
  }

  h1 {
    margin: 0 0 18px;
    font-size: 1.6rem;
    font-weight: 600;
  }

  ul {
    list-style: none;
    margin: 0 0 8px;
    padding: 0;
  }

  li {
    display: flex;
    gap: 14px;
    padding: 12px 0;
    border-top: 1px solid var(--rule);
    font-size: 0.95rem;
  }

  li:first-child { border-top: none; }

  li time {
    flex: 0 0 auto;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem;
    color: var(--muted);
    padding-top: 2px;
    white-space: nowrap;
  }

  a.back {
    display: inline-block;
    margin-top: 22px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    color: var(--ink);
    text-decoration: none;
    padding: 8px 15px;
    border: 1px solid var(--rule);
    border-radius: 7px;
    transition: border-color 0.15s ease, background-color 0.15s ease;
  }

  a.back:hover,
  a.back:focus-visible {
    border-color: var(--signal);
    background: var(--signal-soft);
    outline: none;
  }
</style>
</head>
<body>
  <div class="card">
    <div class="eyebrow">notes</div>
    <h1>What I did to set this up</h1>
    <ul>
      <li><time>step 1</time><span>Installed Apache with <code>apt install apache2</code> and left the default config alone.</span></li>
      <li><time>step 2</time><span>Dropped these static files into <code>/var/www/html</code>, replacing the default landing page.</span></li>
      <li><time>step 3</time><span>Opened port 80 and confirmed the page loads from another machine on the network.</span></li>
      <li><time>step 4</time><span>Noted here so future-me remembers why this box is configured the way it is.</span></li>
    </ul>
    <a class="back" href="../index.html">Back Home</a>
  </div>
</body>
</html>
```

```bash
sudo apachectl configtest
sudo systemctl restart httpd
```

Test in the browser: 
```bash
http:IP_Address_of_Your_Server
```
![Homepage](<images/Homepage of Static Site Hosted From Apache Webserver.png>)

---
![About](<images/About of Static Site Hosted From Apache Webserver.png>)

---
![Notes](<images/Notes of Static Site Hosted From Apache Webserver.png>)

---
### Part 3: Name Based Virtual Hosts

A virtual host allows one Apache server to serve multiple websites on one IP, distinguished by the `Host:` HTTP header sent by the client.

```bash
sudo mkdir -p /var/www/myapp.local
sudo chown -R apache:apache /var/www/myapp.local
sudo chmod -R 755 /var/www/myapp.local
```

- Create a homepage:
```bash
sudo vim /var/www/myapp.local/index.html
```

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>myapp.local</title>
<style>
  /* Plain page, one soft background, nothing competing for attention. */
  body {
    font-family: sans-serif;
    max-width: 700px;
    margin: 3rem auto;
    padding: 32px 28px;
    color: #333;
    background: #fafaf8;
    border: 1px solid #e6e4df;
    border-radius: 10px;
    line-height: 1.5;
  }

  h1 {
    color: #2c3e50;
    margin: 0 0 10px;
    font-size: 1.5rem;
  }

  /* A short human line instead of a bare status message. */
  p {
    color: #5c5c5c;
    margin: 0;
  }

  code {
    background: #f0f0ec;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: monospace;
    font-size: 0.95em;
    color: #333;
  }
</style>
</head>
<body>
  <h1>Virtual Host: myapp.local</h1>
  <p>This one's served from <code>/var/www/myapp.local</code>.</p>
</body>
</html>
```

- Create the virtual host configuration:
```bash
sudo vi /etc/httpd/conf.d/myapp.local.conf
```

```apache
<VirtualHost *:80>
    ServerName myapp.local
    ServerAlias www.myapp.local
    DocumentRoot /var/www/myapp.local
    ServerAdmin admin@myapp.local

    ErrorLog /var/log/httpd/myapp.local_error.log
    CustomLog /var/log/httpd/myapp.local_access.log combined

    <Directory "/var/www/myapp.local">
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>
```

`Options -Indexes` prevents Apache from listing directory contents when no index file exists. Always set this in production exposing directory listings reveals your file structure to anyone on the internet.

```bash
sudo apachectl configtest
sudo httpd -S                    # Show all configured virtual hosts
sudo systemctl restart httpd
```

- If you want to access it from the VM's browser:
```bash
echo "<Your_Server_IP>  myapp.local  www.myapp.local" | sudo tee -a /etc/hosts
```
- If you want to access it from the host (Linux/macOS) browser:
```bash
sudo sh -c 'echo "<Your_Server_IP>  myapp.local  www.myapp.local" >> /etc/hosts'
```
- If you want to access it from the host (Windows) browser:
  - Open Notepad as Administrator
  - Notepad > File > Open > File name: `C:\Windows\System32\drivers\etc\hosts`
> Change the file type filter from "Text Documents" to "All Files" so Notepad shows it, since it has no extension.
  - Append
  ```text
  <Your_Server_IP>  myapp.local  www.myapp.local
  ```

Test on the browser: 

`http://myapp.local/`

![Virtual Host](<Testing Virtual Host.png>)

---
> To host more sites, repeat the pattern: each site gets its own directory and its own `.conf` file in `/etc/httpd/conf.d/`.

---
### Part 4: HTTPS with a Self-Signed Certificate

HTTPS encrypts traffic between client and server using TLS. This lab terminates TLS **at Apache** for a single server setup; in the multi tier pattern of Section 5.1 §5 you would instead terminate at Nginx. Certificate options:

- **Let's Encrypt:** Free, automated, 90 day certificates via `certbot`. Requires a publicly routable domain. Standard for production.
- **Commercial CA:** Paid certificates (DigiCert, Sectigo). Used when extended validation is required.
- **Self signed:** Generated locally, not trusted by browsers. Use only in lab or internal environments.

- Install mod_ssl
```bash
sudo dnf install mod_ssl openssl -y
```
- Generate a self-signed certificate
  - Syntax:
```bash
sudo openssl req -x509 -nodes -days <DAYS> -newkey rsa:<KEY_SIZE> \
    -keyout <PATH_TO_KEY> \
    -out <PATH_TO_CERT> \
    -subj "/C=<COUNTRY_CODE>/ST=<STATE>/L=<CITY>/O=<ORGANIZATION>/CN=<COMMON_NAME>"
```
Flags: 
  - `-x509` self-signed certificate
  - `-nodes` no passphrase on the key
  - `-days 365` one year validity
  - `-newkey rsa:2048` new 2048-bit RSA key pair
  - `-subj` subject fields without an interactive prompt.

- Delete a key
```bash
sudo rm /etc/pki/tls/private/<key_name>.key \
        /etc/pki/tls/certs/<certificate_name>.crt
```

---
**Complete Example: Cafe App**

```bash
sudo mkdir -p /var/www/brewhousecafe
sudo chown -R apache:apache /var/www/brewhousecafe
sudo chmod -R 755 /var/www/brewhousecafe
```

- Create a homepage:
```bash
sudo vim /var/www/brewhousecafe/index.html
```
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cafe Brew House</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #efe6d8;
    --card: #fbf8f2;
    --ink: #3a2a1c;
    --muted: #8a7863;
    --rule: #ddd0b9;
    --crema: #b9822f;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: 'IBM Plex Sans', sans-serif;
    background: var(--bg);
    color: var(--ink);
    display: flex;
    justify-content: center;
    padding: 44px 16px;
  }
  main { width: 100%; max-width: 430px; }
  h1 {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: 1.9rem;
    margin: 0 0 4px;
  }
  .sub { color: var(--muted); margin: 0 0 22px; font-size: 0.92rem; }
  .item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 16px 0;
    border-top: 1px solid var(--rule);
  }
  .item:first-of-type { border-top: none; }
  .name { font-weight: 600; font-size: 0.98rem; }
  .roast {
    font-size: 0.72rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--crema);
    margin-top: 2px;
  }
  .price { color: var(--muted); font-size: 0.85rem; margin-top: 3px; }
  .qty { display: flex; align-items: center; gap: 8px; }
  .qty button {
    width: 28px; height: 28px;
    border: 1px solid var(--rule);
    background: var(--card);
    border-radius: 50%;
    cursor: pointer;
    font-size: 1rem;
    line-height: 1;
    color: var(--ink);
  }
  .qty button:hover { border-color: var(--crema); color: var(--crema); }
  .qty span { min-width: 16px; text-align: center; font-size: 0.9rem; }
  .total {
    display: flex;
    justify-content: space-between;
    margin-top: 22px;
    padding-top: 18px;
    border-top: 2px solid var(--ink);
    font-weight: 600;
  }
  button.order {
    width: 100%;
    margin-top: 20px;
    padding: 13px;
    background: var(--ink);
    color: var(--bg);
    border: none;
    border-radius: 999px;
    font-size: 0.95rem;
    cursor: pointer;
  }
  button.order:hover { background: var(--crema); }
  .msg { text-align: center; margin-top: 12px; color: var(--muted); font-size: 0.85rem; min-height: 1.2em; }
</style>
</head>
<body>
<main>
  <h1>Cafe Brew House</h1>
  <p class="sub">Pick your coffee and adjust the cups you want.</p>
  <div id="menu"></div>
  <div class="total"><span>Total</span><span id="total">$0.00</span></div>
  <button class="order" onclick="placeOrder()">Place order</button>
  <p class="msg" id="msg"></p>
</main>

<script>
  const items = [
    { name: "Espresso", roast: "Dark roast", price: 3.0 },
    { name: "Cappuccino", roast: "Medium roast", price: 4.5 },
    { name: "Latte", roast: "Medium roast", price: 4.75 },
    { name: "Americano", roast: "Dark roast", price: 3.75 },
    { name: "Cold Brew", roast: "Steeped overnight", price: 4.25 },
  ];
  const qty = items.map(() => 0);

  function render() {
    const menu = document.getElementById("menu");
    menu.innerHTML = items.map((it, i) => `
      <div class="item">
        <div>
          <div class="name">${it.name}</div>
          <div class="roast">${it.roast}</div>
          <div class="price">$${it.price.toFixed(2)}</div>
        </div>
        <div class="qty">
          <button onclick="change(${i}, -1)">−</button>
          <span>${qty[i]}</span>
          <button onclick="change(${i}, 1)">+</button>
        </div>
      </div>
    `).join("");
    const total = items.reduce((sum, it, i) => sum + it.price * qty[i], 0);
    document.getElementById("total").textContent = "$" + total.toFixed(2);
  }

  function change(i, delta) {
    qty[i] = Math.max(0, qty[i] + delta);
    document.getElementById("msg").textContent = "";
    render();
  }

  function placeOrder() {
    const total = items.reduce((sum, it, i) => sum + it.price * qty[i], 0);
    const msg = document.getElementById("msg");
    if (total === 0) {
      msg.textContent = "Add a coffee to start your order.";
      return;
    }
    msg.textContent = "Order placed. Total $" + total.toFixed(2) + ". See you soon.";
  }

  render();
</script>
</body>
</html>
```
- Generate the self-signed certificate for the cafe app
```bash
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/pki/tls/private/brewhousecafe.key \
    -out /etc/pki/tls/certs/brewhousecafe.crt \
    -subj "/C=NP/ST=Bagmati/L=Kathmandu/O=Brew House Cafe/CN=brewhousecafe.com.np"
```

- Create the HTTPS virtual host
```bash
sudo vi /etc/httpd/conf.d/brewhousecafe.local-ssl.conf
```

```apache
# HTTPS virtual host
<VirtualHost *:443>
    ServerName brewhousecafe.com.np
    DocumentRoot /var/www/brewhousecafe
    ServerAdmin admin@brewhousecafe.com.np

    SSLEngine on
    SSLCertificateFile /etc/pki/tls/certs/brewhousecafe.crt
    SSLCertificateKeyFile /etc/pki/tls/private/brewhousecafe.key

    # Disable deprecated protocols; allow TLS 1.2 and 1.3 only
    SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1

    # Security headers
    Header always set Strict-Transport-Security "max-age=63072000; includeSubDomains"
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-Frame-Options "DENY"

    <Directory "/var/www/brewhousecafe">
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog /var/log/httpd/brewhousecafe.com.np_ssl_error.log
    CustomLog /var/log/httpd/brewhousecafe.com.np_ssl_access.log combined
</VirtualHost>

# Redirect all HTTP to HTTPS
<VirtualHost *:80>
    ServerName brewhousecafe.local
    Redirect permanent / https://brewhousecafe.local/
</VirtualHost>
```

- Add `https` service in the firewall
```bash
sudo firewall-cmd --add-service=https --permanent
sudo firewall-cmd --reload
```
- Check syntax and restart the service
```bash
sudo apachectl configtest
sudo systemctl restart httpd
```

Test: `https://www.brewhouse.com.np`

The browser warns because the cert is self-signed; proceed past it and confirm the padlock shows TLS is active.

![Browser Warning](<images/Warning HTTPS.png>)

![Procced Warning HTTPS](<images/Proceed Warning HTTPS.png>)

![Cafe Website https](<images/HTTPS Cafe Site Apache.png>)

---
**Let's Encrypt for production (Production domain required):**

- Syntax:
```bash
sudo dnf install certbot python3-certbot-<PLUGIN> -y
sudo certbot --<PLUGIN> -d <DOMAIN> -d <SUBDOMAIN>
sudo certbot renew --dry-run
```
* **`<PLUGIN>`** Configures the web server automatically (for example, `apache` or `nginx`).
* **`-d <DOMAIN>`** Adds a domain to the certificate. Repeat `-d` for multiple domains.
* **`certbot renew --dry-run`** Tests automatic certificate renewal without issuing a new certificate.

- Example: Brew House Cafe (production domain)
```bash
sudo dnf install certbot python3-certbot-apache -y
sudo certbot --apache -d brewhousecafe.com -d www.brewhousecafe.com
sudo certbot renew --dry-run                              # Test auto-renewal
```
>Note this only works with brewhousecafe.com being a real, publicly routable domain with DNS pointed at this server's public IP.

---
### Part 5: PHP Website with PHP-FPM

Apache serves PHP through **PHP-FPM** (FastCGI Process Manager), the current standard. PHP runs as a separate process pool; Apache proxies PHP requests to it. This is more efficient and more secure than in-process modules, and supports multiple PHP versions per server.

```bash
sudo dnf install php php-fpm php-mysqlnd php-json php-xml php-mbstring -y
```
```bash
sudo systemctl enable --now php-fpm
sudo systemctl status php-fpm
```
```bash
php -v
```
- Create a project Directory:
```bash
sudo mkdir -p /var/www/phpsite
sudo chown -R apache:apache /var/www/phpsite
sudo chmod -R 755 /var/www/phpsite
```
- Create the PHP application
```bash
sudo vi /var/www/phpsite/index.php
```

```php
<?php
session_start();
$_SESSION['visits'] = ($_SESSION['visits'] ?? 0) + 1;
$name = htmlspecialchars($_POST['name'] ?? '');
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PHP Demo</title>
    <style>
        body {
            font-family: sans-serif;
            max-width: 700px;
            margin: 3rem auto;
            padding: 20px;
            color: #333;
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 1rem;
        }
        p {
            margin: 0.4rem 0;
        }
        form {
            margin-top: 1.2rem;
        }
        input[type="text"] {
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 1rem;
        }
        button {
            padding: 8px 16px;
            margin-left: 6px;
            border: 1px solid #2c3e50;
            background: #2c3e50;
            color: #fff;
            border-radius: 4px;
            font-size: 1rem;
            cursor: pointer;
        }
        button:hover {
            background: #1f2d3a;
        }
    </style>
</head>
<body>
    <h1>PHP FPM Demo</h1>
    <p><strong>Server:</strong> <?= htmlspecialchars($_SERVER['SERVER_NAME']) ?></p>
    <p><strong>PHP Version:</strong> <?= PHP_VERSION ?></p>
    <p><strong>Session visits:</strong> <?= $_SESSION['visits'] ?></p>
    <form method="POST">
        <input type="text" name="name" placeholder="Enter your name" required>
        <button type="submit">Submit</button>
    </form>
    <?php if ($name): ?>
        <p>Hello, <strong><?= $name ?></strong>!</p>
    <?php endif; ?>
</body>
</html>
```

`htmlspecialchars()` converts special characters to HTML entities, preventing cross-site scripting (XSS). Always escape output derived from user input.

- Create virtual host configuration
```bash
sudo vi /etc/httpd/conf.d/phpsite.conf
```

```apache
<VirtualHost *:80>
    ServerName mytestwebphp
    DocumentRoot /var/www/phpsite
    ServerAdmin admin@mytestwebphp.com.np

    # Forward .php files to PHP-FPM via Unix socket
    <FilesMatch \.php$>
        SetHandler "proxy:unix:/run/php-fpm/www.sock|fcgi://localhost"
    </FilesMatch>

    <Directory "/var/www/mytestwebphp">
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog /var/log/httpd/mytestwebphp_error.log
    CustomLog /var/log/httpd/mytestwebphp_access.log combined
</VirtualHost>
```

```bash
sudo apachectl configtest
sudo systemctl restart php-fpm
sudo systemctl restart httpd
```
```bash
echo "<Your_Server_IP> mytestwebphp" | sudo tee -a /etc/hosts
```

Test: `http://mytestwebphp`

![php site accessing through browser](<images/PHP Website.png>)

---
### Part 6: Python Website with mod_wsgi

`mod_wsgi` bridges Apache and Python web applications. WSGI (Web Server Gateway Interface) is the standard Python interface between web servers and Python frameworks: Django, Flask, and most others implement it.

**Two deployment modes:**
- **Embedded mode:** Python runs inside Apache processes. Simple but less isolated.
- **Daemon mode (recommended):** Python runs in separate processes. Better isolation, graceful restarts without restarting Apache, and different Python environments per application.

```bash
sudo dnf install httpd python3 python3-mod_wsgi -y
```
```bash
sudo httpd -M | grep wsgi     # Verify the module loaded
```

- Create the directory layout. The WSGI script lives **outside** the document root so it can never be served as static source, even if mod_wsgi fails to intercept.
```bash
sudo mkdir -p /var/www/pysite/wsgi
sudo mkdir -p /var/www/pysite/public
sudo vim /var/www/pysite/wsgi/app.py
```

```python
#!/usr/bin/env python3
import sys

def application(environ, start_response):
    """A minimal WSGI application."""
    status = '200 OK'
    headers = [('Content-Type', 'text/html; charset=utf-8')]
    start_response(status, headers)

    rows = [
        ("Python version", sys.version.split()[0]),
        ("Server software", environ.get('SERVER_SOFTWARE', 'unknown')),
        ("Client address", environ.get('REMOTE_ADDR', 'unknown')),
        ("Request method", environ.get('REQUEST_METHOD', 'unknown')),
        ("Script name", environ.get('SCRIPT_NAME', '/')),
    ]
    rows_html = "".join(
        f'<div class="row"><span class="key">{k}</span><span class="val">{v}</span></div>'
        for k, v in rows
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>WSGI Daemon</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #e9ece6;
    --panel: #ffffff;
    --ink: #232a26;
    --muted: #6b7a70;
    --rule: #d6ddd0;
    --pine: #3f6b52;
    --pine-soft: #e3ece5;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    min-height: 100vh;
    padding: 48px 20px;
    background: var(--bg);
    color: var(--ink);
    font-family: 'Inter', sans-serif;
    display: flex;
    justify-content: center;
  }}
  .panel {{
    width: 100%;
    max-width: 460px;
    background: var(--panel);
    border: 1px solid var(--rule);
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 14px 34px -24px rgba(35, 42, 38, 0.5);
  }}
  .bar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 20px;
    background: var(--pine-soft);
    border-bottom: 1px solid var(--rule);
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: var(--pine);
    letter-spacing: 0.02em;
  }}
  .bar .dot {{
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--pine);
    display: inline-block;
    margin-right: 6px;
  }}
  .body {{
    padding: 24px 24px 26px;
  }}
  h1 {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.2rem;
    font-weight: 600;
    margin: 0 0 6px;
  }}
  .lead {{
    color: var(--muted);
    font-size: 0.92rem;
    margin: 0 0 20px;
  }}
  .row {{
    display: flex;
    justify-content: space-between;
    gap: 12px;
    padding: 10px 0;
    border-top: 1px solid var(--rule);
    font-size: 0.88rem;
  }}
  .row:first-of-type {{ border-top: none; }}
  .key {{
    color: var(--muted);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
  }}
  .val {{
    font-weight: 500;
    text-align: right;
    word-break: break-word;
  }}
</style>
</head>
<body>
  <div class="panel">
    <div class="bar"><span><span class="dot"></span>wsgi.application</span><span>daemon mode</span></div>
    <div class="body">
      <h1>Application running</h1>
      <p class="lead">Deployed behind Apache using mod_wsgi in daemon mode.</p>
      {rows_html}
    </div>
  </div>
</body>
</html>"""
    return [html.encode('utf-8')]
```

- Create the virtual host

```bash
sudo vi /etc/httpd/conf.d/pysite.conf
```
```apache
<VirtualHost *:80>
    ServerName pysite.test
    DocumentRoot /var/www/pysite/public
    ServerAdmin admin@pysite.com.np

    # Daemon mode: Python runs in separate processes, not inside Apache workers
    WSGIDaemonProcess pysite-app user=apache group=apache \
        processes=2 threads=15 python-path=/var/www/pysite/wsgi

    WSGIScriptAlias / /var/www/pysite/wsgi/app.py

    <Directory /var/www/pysite/wsgi>
        WSGIProcessGroup pysite-app
        WSGIApplicationGroup %{GLOBAL}
        Require all granted
    </Directory>

    <Directory /var/www/pysite/public>
        Options -Indexes
        AllowOverride None
        Require all granted
    </Directory>

    ErrorLog /var/log/httpd/pysite_error.log
    CustomLog /var/log/httpd/pysite_access.log combined
    LogLevel warn
</VirtualHost>
```

- Set permissions and SELinux context:
```bash
sudo chown -R apache:apache /var/www/pysite
sudo chmod -R 755 /var/www/pysite
```
```bash
sudo chcon -R -t httpd_sys_content_t /var/www/pysite
```
```bash
sudo apachectl configtest
sudo systemctl restart httpd
```

- Resolve host locally (replace `<Your_Server_IP>` with the actual IP):
```bash
echo "<Your_Server_IP>  pysite.test" | sudo tee -a /etc/hosts
```

- Test:
```text
http://pysite.test/
```

![Python Based Website](<images/Python Based Website.png>)

---
>A 403 Forbidden is almost always a wrong SELinux context or wrong ownership.

---
### Part 7: Apache Log Management

Apache writes an access log and an error log; reading them is essential when troubleshooting.

| File | Purpose |
|---|---|
| `/var/log/httpd/access_log` | All HTTP requests to the default virtual host |
| `/var/log/httpd/error_log` | Apache errors, module messages, application stderr |
| Virtual host logs | Defined per `<VirtualHost>` in `.conf` files |

```bash
sudo tail -f /var/log/httpd/access_log           # Follow access log in real time
```
```bash
sudo tail -f /var/log/httpd/error_log            # Follow error log in real time
```
```bash
sudo grep " 404 " /var/log/httpd/access_log      # Find 404 errors
```
```bash
sudo grep " 500 " /var/log/httpd/access_log      # Find 500 server errors
```
```bash
# HTTP status code distribution
sudo awk '{print $9}' /var/log/httpd/access_log | sort | uniq -c | sort -rn | head -10
```

**Combined Log Format**: One line, then its fields:
```
192.168.1.10 - alice [25/Jun/2026:09:15:23 +0545] "GET /index.php HTTP/1.1" 200 4823 "-" "Mozilla/5.0"
```

Fields: client IP, identity (usually `-`), auth user, timestamp, request line, status code, response bytes, referrer, user agent.

---
> Apache and Nginx can coexist on the same server, but they cannot listen on the same IP address and port simultaneously. Running both requires different ports, different IP addresses, or a reverse proxy configuration.
```bash
sudo systemctl disable httpd.service --now
```
---
## Lab 5.1.B: Nginx - Static Site, Reverse Proxy, and Load Balancer

### Part 1: Install and Start Nginx

```bash
sudo dnf install nginx -y
```
```bash
sudo systemctl enable --now nginx
sudo systemctl status nginx
```
```bash
nginx -v
```
```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

Test: `http://<Your_Server_IP>`

>You should see the Nginx welcome page.

Major commands:

```bash
sudo nginx -t                 # Test configuration syntax
```
```bash
sudo nginx -T                 # Test and dump the full config
```
```bash
sudo systemctl reload nginx   # Apply changes without dropping connections
sudo systemctl restart nginx  # Full restart (drops active connections briefly)
```

Always run `nginx -t` before reloading or restarting. A config error prevents Nginx from starting, taking the server offline.

---
### Part 2: Serve a Static Site

```bash
sudo mkdir -p /var/www/nginx-static
sudo vim /var/www/nginx-static/index.html
```

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Nginx Static Site</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  *{box-sizing:border-box;margin:0}
  body{background:#0e0e12;color:#d8dae0;font-family:Inter,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;padding:24px}
  .card{max-width:520px;width:100%;background:#18181f;border:1px solid #2a2a35;border-radius:12px;overflow:hidden}
  .bar{display:flex;justify-content:space-between;padding:10px 20px;border-bottom:1px solid #2a2a35;font:12px "Space Mono",monospace;color:#6b6e7a}
  .body{padding:32px 24px 24px}
  .label{font:11px/1 "Space Mono",monospace;letter-spacing:.12em;text-transform:uppercase;color:#b08d57;margin-bottom:12px}
  h1{font:600 26px/1.3 Inter,sans-serif;margin-bottom:16px}
  .pill{display:inline-flex;align-items:center;gap:8px;background:rgba(72,199,118,.12);border:1px solid rgba(72,199,118,.3);color:#48c776;font:13px "Space Mono",monospace;padding:6px 12px;border-radius:99px;margin-bottom:24px}
  .pill i{width:7px;height:7px;border-radius:50%;background:#48c776;animation:p 2s ease-out infinite}
  @keyframes p{0%{box-shadow:0 0 0 0 rgba(72,199,118,.5)}70%{box-shadow:0 0 0 8px transparent}to{box-shadow:0 0 0 0 transparent}}
  .info{background:#111116;border:1px solid #2a2a35;border-radius:8px;padding:14px 16px;margin-bottom:20px;font:13px "Space Mono",monospace}
  .row{display:flex;justify-content:space-between;padding:4px 0;color:#6b6e7a}
  .row span:last-child{color:#d8dae0}
  .note{font-size:14px;line-height:1.6;color:#6b6e7a}
  .note code{font-family:"Space Mono",monospace;background:#111116;border:1px solid #2a2a35;border-radius:4px;padding:1px 5px;color:#d8dae0;font-size:12px}
  .foot{display:flex;justify-content:space-between;padding:12px 24px;font:11px "Space Mono",monospace;color:#6b6e7a}
  @media(prefers-reduced-motion:reduce){.pill i{animation:none}}
</style>
</head>
<body>
  <div class="card">
    <div class="bar"><span>nginx</span><span>worker active</span></div>
    <div class="body">
      <p class="label">Server response</p>
      <h1>This box is answering requests. Nginx is running correctly.</h1>
      <div class="pill"><i></i>Online and serving</div>
      <div class="info">
        <div class="row"><span>Root</span><span>/var/www/nginx static</span></div>
        <div class="row"><span>Handler</span><span>nginx</span></div>
        <div class="row"><span>Loaded</span><span id="t">...</span></div>
      </div>
      <p class="note">Drop an <code>index.html</code> into the document root and it will replace this page on the next request.</p>
    </div>
    <div class="foot"><span>200</span><span id="c">...</span></div>
  </div>
  <script>
    const o={hour:'2-digit',minute:'2-digit',second:'2-digit'};
    document.getElementById('t').textContent=new Date().toLocaleTimeString(undefined,o);
    setInterval(()=>document.getElementById('c').textContent=new Date().toLocaleTimeString(undefined,o),1000);
  </script>
</body>
</html>
```

```bash
sudo chown -R nginx:nginx /var/www/nginx-static
```

```bash
sudo chcon -R -t httpd_sys_content_t /var/www/nginx-static
```

- Create the server block `
```bash
sudo vi /etc/nginx/conf.d/static-site.conf
```
```nginx
server {
    listen 80;
    server_name mysite.test;

    root /var/www/nginx-static;
    index index.html;

    # Deny access to hidden files (dot files like .env, .git)
    location ~ /\. {
        deny all;
    }

    access_log /var/log/nginx/static.local_access.log;
    error_log  /var/log/nginx/static.local_error.log;
}
```

```bash
sudo nginx -t
sudo systemctl reload nginx
```

```bash
echo "<Your_Server_IP>  mysite.test" | sudo tee -a /etc/hosts
```

Test: `http://mysite.test`

![Nginx Static Website](<Nginx Static Website.png>)

---
### Part 3: Nginx as a Reverse Proxy

A reverse proxy accepts client requests and forwards them to a backend. The client talks only to Nginx; the backend is invisible from outside. This enables TLS termination, centralised logging, access control, and load distribution without changing the application.

```
HOST machine                    │  VM (guest)
                                │
browser ──80──▶ 192.168.56.10 ──┼──▶ nginx (proxy.test) ──5000──▶ backend app
   ▲                            │                                  (127.0.0.1 only)
   └── /etc/hosts maps          │
       proxy.test → VM IP       │  port 5000 is not reachable from the host
```

Every step runs inside the VM unless it is marked on the host.

- Build the backend
```bash
sudo mkdir -p /opt/demo-backend
sudo vim /opt/demo-backend/app.py
```

```python
#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from datetime import datetime
import html
import re
import socket

LISTEN = ("127.0.0.1", 5000)          # loopback only: unreachable from outside
SHOW = ("Host", "X-Real-IP", "X-Forwarded-For", "X-Forwarded-Proto",
        "X-Server-Addr", "Connection", "User-Agent")

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Request waybill &mdash; backend behind Nginx</title>
<style>
  :root{
    --desk:#2B2D26; --paper:#E4E2D7; --ink:#23241E;
    --rule:#B7B5A6; --faint:#6E6D60; --stamp:#5A3E9B;
    --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace;
    --cond:"Arial Narrow","Helvetica Neue Condensed",Impact,system-ui,sans-serif;
  }
  *{box-sizing:border-box;margin:0}
  body{background:var(--desk);color:var(--ink);font-family:var(--mono);
       padding:40px 16px 64px;display:flex;justify-content:center}
  .sheet{position:relative;width:100%;max-width:680px;background:var(--paper);
         box-shadow:0 18px 40px rgba(0,0,0,.45)}
  .sheet::before{content:"";position:absolute;left:0;right:0;top:-9px;height:9px;
    background:radial-gradient(circle at 6px 9px,var(--desk) 4.5px,var(--paper) 5px) 0 0/12px 9px repeat-x}
  .masthead{display:flex;justify-content:space-between;align-items:flex-end;gap:16px;
            padding:26px 26px 14px;border-bottom:2px solid var(--ink)}
  .issuer{font-size:10px;letter-spacing:.22em;text-transform:uppercase;color:var(--faint)}
  h1{font-family:var(--cond);font-weight:700;font-size:34px;line-height:.95;
     letter-spacing:.04em;text-transform:uppercase}
  .serial{font-size:11px;letter-spacing:.12em;color:var(--faint);text-align:right;white-space:nowrap}
  .route{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 10px;
         padding:14px 26px;border-bottom:1px solid var(--rule);font-size:12px}
  .route i{font-style:normal;color:var(--faint)}
  .route b{font-weight:500}
  .route .last{color:var(--stamp)}
  .note{padding:22px 26px 6px;font-size:12.5px;line-height:1.75;color:#3E4038;max-width:56ch}
  .note em{font-style:normal;background:rgba(90,62,155,.12);padding:0 3px}
  .cap{padding:24px 26px 0;font-family:var(--cond);font-size:13px;font-weight:700;
       letter-spacing:.2em;text-transform:uppercase}
  .fields{padding:8px 26px 26px}
  .f{display:grid;grid-template-columns:minmax(0,15rem) 1fr;align-items:baseline;
     column-gap:12px;padding:9px 0;border-bottom:1px dotted var(--rule)}
  .k{font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--faint)}
  .v{font-size:13px;word-break:break-all}
  .v.off{color:#9C9A8C}
  .v.off::before{content:"\2014 ";color:var(--rule)}
  .stamp{position:absolute;right:22px;bottom:74px;transform:rotate(-7deg);
    padding:8px 14px 7px;border:2px solid var(--stamp);outline:1px solid var(--stamp);
    outline-offset:2px;color:var(--stamp);opacity:.82;mix-blend-mode:multiply;
    font-family:var(--cond);text-transform:uppercase;text-align:center;pointer-events:none}
  .stamp b{display:block;font-size:17px;font-weight:700;letter-spacing:.13em}
  .stamp span{display:block;font-family:var(--mono);font-size:9.5px;letter-spacing:.1em;margin-top:3px}
  .foot{display:flex;flex-wrap:wrap;gap:4px 28px;padding:12px 26px;
        border-top:2px solid var(--ink);font-size:10.5px;letter-spacing:.1em;
        text-transform:uppercase;color:var(--faint)}
  .foot b{font-weight:500;color:var(--ink);text-transform:none;letter-spacing:.04em}
  @media(max-width:560px){
    h1{font-size:26px}
    .masthead{flex-direction:column;align-items:flex-start;gap:8px}
    .serial{text-align:left}
    .f{grid-template-columns:1fr;gap:2px}
    .stamp{position:static;transform:rotate(-2deg);display:block;margin:0 26px 22px}
  }
</style>
</head>
<body>
  <div class="sheet">
    <div class="masthead">
      <div>
        <div class="issuer">Issued by nginx &middot; upstream copy</div>
        <h1>Request<br>waybill</h1>
      </div>
      <div class="serial">delivered {{TIME}}<br>{{HOSTNAME}}</div>
    </div>
    <div class="route">
      <i>from</i> <b>{{CLIENT}}</b>
      <i>via</i> <b>{{EDGE}}</b>
      <i>to</i> <b class="last">127.0.0.1:{{PORT}}</b>
    </div>
    <p class="note">Your browser never opened a socket to this process. It is bound to
      <em>127.0.0.1:{{PORT}}</em> and answers nothing else. Everything below is what actually
      arrived at the application &mdash; Nginx either carried it along or wrote it itself.</p>
    <p class="cap">Headers received</p>
    <div class="fields">
      {{ROWS}}
    </div>
    <div class="stamp"><b>Received<br>via proxy</b><span>port {{PORT}}</span></div>
    <div class="foot">
      <span>status <b>200</b></span>
      <span>path <b>{{PATH}}</b></span>
      <span>sheet 03 / proxied</span>
    </div>
  </div>
</body>
</html>"""

# render pipeline
# Values that never change are baked in once, at import time.
PAGE = (PAGE.replace("{{PORT}}", str(LISTEN[1]))
            .replace("{{HOSTNAME}}", html.escape(socket.gethostname())))

# The rest is split once into literal chunks and placeholder names, so each
# request is a single str.join instead of a chain of full-string copies.
_PARTS = re.split(r"\{\{(\w+)\}\}", PAGE)   # even = literal, odd = key


def render(values):
    out = _PARTS[:]
    for i in range(1, len(out), 2):
        out[i] = values[out[i]]
    return "".join(out)


# Header names and row numbers are static, so pre-build everything around
# the value: only the value itself is escaped per request.
_ROW_HEAD = tuple(
    '<div class="f"><span class="k">%s</span><span class="v' % html.escape(name)
    for name in SHOW
)


class Handler(BaseHTTPRequestHandler):
    server_version = "demo-backend/1.0"
    protocol_version = "HTTP/1.1"      # required for upstream keepalive
    disable_nagle_algorithm = True

    def _page(self):
        get = self.headers.get
        rows = []
        for head, name in zip(_ROW_HEAD, SHOW):
            value = get(name)
            if value:
                rows.append('%s">%s</span></div>' % (head, html.escape(value)))
            else:
                rows.append('%s off">not set</span></div>' % head)

        return render({
            "ROWS": "".join(rows),
            "CLIENT": html.escape(get("X-Real-IP") or self.client_address[0]),
            "EDGE": html.escape(get("X-Server-Addr") or "direct, no proxy"),
            "PATH": html.escape(self.path),
            "TIME": datetime.now().strftime("%H:%M:%S"),
        }).encode("utf-8")

    def _respond(self, payload, body=True):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        if body:
            self.wfile.write(payload)

    def do_GET(self):
        if self.path == "/favicon.ico":
            self.send_response(204)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        self._respond(self._page())

    def do_HEAD(self):
        self._respond(self._page(), body=False)

    def log_message(self, fmt, *args):
        print("[backend] " + fmt % args, flush=True)


class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


if __name__ == "__main__":
    server = Server(LISTEN, Handler)
    print("listening on %s:%d" % LISTEN, flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nshutting down", flush=True)
    finally:
        server.server_close()
```

> Note: if you rewrite this file more than once with `nano` or `vim`, mixed tabs and spaces can silently break indentation. Before running it, confirm the file compiles clean:
```bash
sudo python3 -c "import py_compile; py_compile.compile('/opt/demo-backend/app.py')"
```
> A clean run produces no output. An `IndentationError` here means the file needs to be rewritten, not patched.

Run it in the foreground once to confirm it works:

```bash
python3 /opt/demo-backend/app.py
```

- From a second terminal:

```bash
curl -s http://127.0.0.1:5000/ | grep -o "<h1>.*</h1>"
```
![Testing Proxy Server](<Testing Proxy Server Through Terminal.png>)

Stop it with `Ctrl+c`. systemd takes over next.


- Keep the backend running
```bash
sudo useradd --system --no-create-home --shell /sbin/nologin appuser
```
```bash
sudo chown -R appuser:appuser /opt/demo-backend
```
```bash
sudo vim /etc/systemd/system/demo-backend.service
```

```ini
[Unit]
Description=Demo backend behind Nginx
After=network.target

[Service]
Type=simple
User=appuser
ExecStart=/usr/bin/python3 /opt/demo-backend/app.py
Restart=on-failure
RestartSec=2

# The app never needs the filesystem or a public socket
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
```
```bash
sudo systemctl enable --now demo-backend
```
```bash
sudo systemctl status demo-backend --no-pager
```
```bash
ss -tlnp | grep 5000
```

> Verification step: `enable --now` can silently fail to start the unit if the previous command in your terminal history got mangled or double-pasted. Don't trust the command, trust the status output. If `systemctl status` reports `Active: inactive (dead)`, the service never actually started:
```bash
  sudo systemctl restart demo-backend
  sudo journalctl -u demo-backend -n 30 --no-pager
```

- Let Nginx open outbound connections (SELinux)

On RHEL family systems SELinux blocks nginx from connecting to anything by default. Skipping this step is the single most common cause of 502 Bad Gateway on a config that is otherwise correct.

```bash
sudo setsebool -P httpd_can_network_connect 1
getsebool httpd_can_network_connect        # httpd_can_network_connect --> on
```

- The proxy server block

```bash
sudo vim /etc/nginx/conf.d/reverse-proxy.conf
```

```nginx
upstream demo_backend {
    server 127.0.0.1:5000;
    keepalive 16;                 # pool of idle connections to reuse
}

server {
    listen 80;
    server_name proxy.test;

    location / {
        proxy_pass http://demo_backend;

        # Pass original request context to the backend
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Which address of this VM the client actually dialled
        proxy_set_header X-Server-Addr     $server_addr:$server_port;

        proxy_connect_timeout 10s;
        proxy_read_timeout    30s;
        proxy_send_timeout    30s;

        # HTTP/1.1 keepalive to the upstream
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }

    # Health endpoint answered by Nginx itself. Never touches the backend.
    location = /healthz {
        access_log off;
        return 200 "nginx ok\n";
        add_header Content-Type text/plain;
    }

    location ~ /\. {
        deny all;
    }

    access_log /var/log/nginx/proxy.test_access.log;
    error_log  /var/log/nginx/proxy.test_error.log;
}
```

**Why these headers matter:**

- `X-Real-IP` and `X-Forwarded-For`: your logs and analytics need the real client IP, not Nginx's. Without them, every entry shows 127.0.0.1.
- `X-Forwarded-Proto`: tells the backend whether the original request was HTTP or HTTPS. This is exactly how the backend learns TLS was terminated at the edge. Flask's `request.is_secure`, Django's `SECURE_PROXY_SSL_HEADER`, and most frameworks read it.
- `Host $host`: without it the backend receives `demo_backend` as its hostname, which breaks absolute URLs, redirects, and virtual host routing.
- `proxy_http_version 1.1` with `Connection ""`: reuses TCP connections to the backend instead of opening a new one per request. The empty `Connection` header is what stops Nginx from sending `Connection: close` upstream and defeating the keepalive pool.
- `X-Server-Addr`: not a standard header, added here purely so the page can show which address of the VM the request landed on. Real deployments rarely need it.
- `listen 80;` with no address binds every interface in the VM, which is what lets the host reach it. Keep it that way. Do not narrow it to `127.0.0.1`.

```bash
sudo nginx -t
sudo systemctl reload nginx
```

> Config loading check: confirm this file is actually included, and that no leftover default site is competing for the same `listen 80`:
```bash
grep -n "include /etc/nginx/conf.d" /etc/nginx/nginx.conf
sudo nginx -T | grep -B3 "listen 80"
```
> If a stray `default.conf` or similar is still present and serving the stock Fedora test page instead of your block, disable it:
```bash
sudo mv /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf.disabled
sudo nginx -t && sudo systemctl reload nginx
```

- Reach the VM from your host:

Open the firewall, inside the VM. Port 80 only, never 5000:

```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload
sudo firewall-cmd --list-all
```

> Zone check: adding the service only helps if it lands in the zone actually bound to your network interface. Confirm before assuming the rule applies:
```bash
sudo firewall-cmd --get-active-zones
```
> The interface shown against your active zone (for example `enp0s3`) must be the same zone `http` was added to. If it's a different zone, add the service there instead.

- Find the VM's address, inside the VM:

```bash
hostname -I
ip -4 addr show | grep -v 127.0.0.1 | grep inet
```

Map the name on the host, so `proxy.test` resolves there the same way it does in the VM:

- Linux or macOS: `sudo vim /etc/hosts`
- Windows: open Notepad as Administrator, then open file: `C:\Windows\System32\drivers\etc\hosts`

```
192.168.56.10   proxy.test
```

Use the VM's actual IP here, not the example above. If the VM's address changes (a new `vagrant up`, a DHCP renewal), this line goes stale and every request silently goes to the wrong place.

> The VM also needs to resolve its own name. The "test inside the VM first" step below requires `proxy.test` to resolve locally, and nothing sets that up automatically:
```bash
echo "127.0.0.1 proxy.test" | sudo tee -a /etc/hosts
```
> Skipping this makes the in-VM curl tests hang on DNS resolution rather than fail with a clear error, which is easy to misread as a proxy problem.

- Test

Inside the VM first. If this fails, nothing on the host will work:

```bash
curl -s http://proxy.test/healthz          # nginx ok, proxy alive
curl -sI http://proxy.test/ | head -3      # 200, Server: nginx
curl -s http://proxy.test/ | grep -A1 X-Real-IP
```

A useful variant that bypasses DNS entirely and isolates virtual host matching from networking:

```bash
curl -s http://127.0.0.1/ -H "Host: proxy.test" | grep -o "<title>.*</title>"
```

Then browser test, from the host:

`http://proxy.test/healthz`

![Server Health](<Reverse Proxy Server Health.png>)

---
`http://proxy.test/`

![Reverse Proxy Server](<Reverse Proxy Webpage.png>)

---
`http://<VM_IP>:5000/`

![Try Accessing Main Server](<Reverse Proxy Trying Accessing Main Server Directly.png>)

The proof that the proxy is doing its job: on the page you get from the host, `X-Real-IP` shows your host's address rather than `127.0.0.1`. That value crossed two hops, host to Nginx to backend, because of the `proxy_set_header` lines.

- Watch both sides at once:

```bash
sudo tail -f /var/log/nginx/proxy.test_access.log & sudo journalctl -u demo-backend -f
```


- When it breaks

Host to VM problems first, since they look like Nginx problems and are not:

| Symptom on the host | Cause | Fix |
|---|---|---|
| Browser hangs, then times out | VM firewall closed, wrong firewalld zone, or NAT with no forwarding rule | `firewall-cmd --get-active-zones` to confirm the interface's zone has `http` added; for NAT add the `--natpf1` rule |
| Connection refused immediately | Nothing listening on that host port, wrong port or wrong mode | `ss -tlnp \| grep :80` in the VM, then recheck the network mode table |
| Name does not resolve | The host `/etc/hosts` was not edited, or was edited without admin rights | `ping proxy.test` must answer with the VM IP; flush the DNS cache |
| Worked yesterday, dead today | DHCP gave the VM a new IP | `hostname -I` in the VM, update the host file, or move to a private adapter |
| Works in the VM, not from the host | A server block says `listen 127.0.0.1:80` | Use plain `listen 80;` |
| In-VM curl hangs with no output | The VM itself has no `/etc/hosts` entry for `proxy.test` | `echo "127.0.0.1 proxy.test" \| sudo tee -a /etc/hosts` |

Then the proxy itself:

| Symptom | Cause | Fix |
|---|---|---|
| Loads, but shows the Fedora/nginx default test page | A default server block is answering before your `server_name proxy.test` block | `nginx -T \| grep -B3 "listen 80"`; disable or rename the competing default config |
| 502 Bad Gateway | Backend down, or SELinux blocking the connect | `systemctl status demo-backend`; `setsebool -P httpd_can_network_connect 1`; check `sudo ausearch -m avc -ts recent` |
| 504 Gateway Time-out | Backend accepted but answered slowly | Raise `proxy_read_timeout`, or fix the slow endpoint |
| Backend logs show 127.0.0.1 for every client | `X-Real-IP` and `X-Forwarded-For` not set, or the app is not reading them | Add the `proxy_set_header` lines, then configure the app's proxy middleware |
| Redirects send users to `demo_backend` | The `Host` header was not forwarded | `proxy_set_header Host $host;` |
| Connection count climbing on the backend | Keepalive was never negotiated | `proxy_http_version 1.1;` and `proxy_set_header Connection "";` |
| `nginx: [emerg] host not found in upstream` | The backend name will not resolve at boot | Use an IP, or add `resolver` for dynamic names |

A useful split test when you cannot tell which side is at fault:

```bash
curl -sI http://127.0.0.1/ -H "Host: proxy.test"   # in the VM:  Nginx is fine
```
```bash
curl -sI http://<VM_IP>/   -H "Host: proxy.test"   # on the host: the path is fine
```

If the first works and the second does not, the problem is the firewall or VM networking, not your config.

**Diagnostic order, top to bottom, for any 502 or timeout:**

1. `ping <VM_IP>`: Confirms basic reachability.
2. `ss -tlnp | grep :80`: Confirms nginx is listening.
3. `curl -H "Host: proxy.test"` against `127.0.0.1` :Confirms the right server block answers, independent of DNS.
4. `systemctl status <backend>`: Confirms the app itself is alive.
5. `getsebool httpd_can_network_connect`: Confirms SELinux isn't blocking the proxy hop.

Each layer rules out one hop between browser and backend. Working top to bottom avoids chasing nginx config when the real problem is DNS, and avoids chasing SELinux when the real problem is the app never started.

> Note: the backend now has no public surface at all. Everything a client can reach is decided in one file, which is why the next steps (TLS termination, rate limiting, caching, and adding a second server line to the upstream block for load balancing) are edits to Nginx alone. The application never learns that any of it happened.

---
# Part 4: Nginx as a Load Balancer

A load balancer accepts client requests and spreads them across a pool of backends. The client talks only to Nginx; which node answered is invisible from outside. This gives fault tolerance, horizontal scale, and rolling deploys without changing the application.

```
HOST machine                    │  Lab network 10.10.0.0/24
                                │
                                │              ┌──80──▶ node1  10.10.0.7
browser ──80──▶ 10.10.0.6 ──────┼──▶ nginx ────┤        (nginx, static page)
   ▲                            │   10.10.0.6  │
   │                            │  round robin └──80──▶ node2  10.10.0.8
   └── /etc/hosts maps          │                       (nginx, static page)
       lb.test → 10.10.0.6      │
                                │  the browser never learns which node answered
```

Three VMs. Every command is marked with the machine it runs on. Substitute your own addresses throughout.

| Role | Hostname | IPv4 |
| :--- | :--- | :--- |
| Load balancer | `loadbalancer` | `10.10.X.X` |
| Node 1 | `node1` | `10.10.X.X` |
| Node 2 | `node2` | `10.10.X.X` |

![Infrastructure](<images/Load Balancer Lab Prerequisites.png>)

Set the hostnames, one per machine:
```bash
sudo hostnamectl set-hostname loadbalancer
sudo hostnamectl set-hostname node1
sudo hostnamectl set-hostname node2
```

Build the nodes first. A load balancer pointed at backends that do not exist yet returns 502 and tells you nothing about whether your config is right.

---
- Build the backend nodes

Everything in this section runs on **node1 and node2**, identically, except the one line that differs.

```bash
sudo dnf install nginx -y    
```
```bash
sudo systemctl enable --now nginx
sudo systemctl status nginx --no-pager
```

Open port 80 to the load balancer only. The nodes have no reason to answer anyone else:

```bash
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="10.10.X.X" port port="80" protocol="tcp" accept'
sudo firewall-cmd --reload
sudo firewall-cmd --list-all
```

>If you would rather keep it simple while learning, `sudo firewall-cmd --permanent --add-service=http` works too, it just leaves the nodes publicly reachable, which defeats half the point of putting a proxy in front of them.

Give each node a page that names itself:

- On **node1**:
```bash
sudo mkdir -p /usr/share/nginx/html/devops
```
```bash
sudo vim /usr/share/nginx/html/devops/index.html
```
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Backend Server — node1</title>
<style>
/* per-backend block: color, glow (color+40 alpha), numeral */
:root{--node:#ff4d2e;--glow:#ff4d2e55;--id:"01"}
*{margin:0;box-sizing:border-box}
body{min-height:100vh;padding:6vmin;display:flex;flex-direction:column;justify-content:space-between;
  background:#0d0d0f;overflow:hidden;color:#f4f4f5;letter-spacing:.02em;
  background-image:radial-gradient(115vmin 85vmin at 85% 112%,var(--glow),transparent 68%);
  font:500 clamp(13px,1.4vw,16px)/1.5 ui-monospace,"SF Mono",Menlo,monospace}
h1{font-size:inherit;font-weight:500;text-transform:uppercase;letter-spacing:.35em;color:#a1a1aa}
h2{font-size:clamp(1.6rem,6vw,4rem);font-weight:600;max-width:12ch;line-height:1.05;letter-spacing:-.02em}
b{color:var(--node);font-weight:600}
p{text-transform:uppercase;letter-spacing:.22em;color:#a1a1aa}
p::after{content:var(--id);float:right;color:var(--node)}
i{width:.55em;height:.55em;border-radius:50%;background:var(--node);display:inline-block;
  margin-right:.7em;animation:pulse 2s infinite}
@keyframes pulse{0%{box-shadow:0 0 0 0 var(--node)}70%,100%{box-shadow:0 0 0 .9em transparent}}
.mark{position:fixed;right:-.07em;bottom:-.3em;font-size:70vmin;line-height:.8;font-weight:700;
  color:var(--node);opacity:.34;pointer-events:none;user-select:none}
</style>
</head>
<body>
  <h1>Backend Server</h1>
  <h2>This is a <b>load balancer</b> test page</h2>
  <p><i></i>Served by node1</p>
  <div class="mark">01</div>
</body>
</html>
```

- On **node2**
```bash
sudo mkdir -p /usr/share/nginx/html/devops
```
```bash
sudo vim /usr/share/nginx/html/devops/index.html
```
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Backend Server — node2</title>
<style>
/* per-backend block: color, glow (color+40 alpha), numeral */
:root{--node:#00d492;--glow:#00d49255;--id:"02"}
*{margin:0;box-sizing:border-box}
body{min-height:100vh;padding:6vmin;display:flex;flex-direction:column;justify-content:space-between;
  background:#0d0d0f;overflow:hidden;color:#f4f4f5;letter-spacing:.02em;
  background-image:radial-gradient(115vmin 85vmin at 85% 112%,var(--glow),transparent 68%);
  font:500 clamp(13px,1.4vw,16px)/1.5 ui-monospace,"SF Mono",Menlo,monospace}
h1{font-size:inherit;font-weight:500;text-transform:uppercase;letter-spacing:.35em;color:#a1a1aa}
h2{font-size:clamp(1.6rem,6vw,4rem);font-weight:600;max-width:12ch;line-height:1.05;letter-spacing:-.02em}
b{color:var(--node);font-weight:600}
p{text-transform:uppercase;letter-spacing:.22em;color:#a1a1aa}
p::after{content:var(--id);float:right;color:var(--node)}
i{width:.55em;height:.55em;border-radius:50%;background:var(--node);display:inline-block;
  margin-right:.7em;animation:pulse 2s infinite}
@keyframes pulse{0%{box-shadow:0 0 0 0 var(--node)}70%,100%{box-shadow:0 0 0 .9em transparent}}
.mark{position:fixed;right:-.07em;bottom:-.3em;font-size:70vmin;line-height:.8;font-weight:700;
  color:var(--node);opacity:.34;pointer-events:none;user-select:none}
</style>
</head>
<body>
  <h1>Backend Server</h1>
  <h2>This is a <b>load balancer</b> test page</h2>
  <p><i></i>Served by node2</p>
  <div class="mark">02</div>
</body>
</html>
```

- The **node1** and **node2** server block, identical on both:
```bash
sudo vim /etc/nginx/conf.d/backend.conf
```
```nginx
server {
    listen 80 default_server;
    server_name _;                 # match any Host header, see below

    root /usr/share/nginx/html/devops;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }

    # For a single-page app, serve the shell instead of 404:
    # try_files $uri $uri/ /index.html;

    location /health {
        access_log off;
        default_type text/plain;
        return 200 "healthy\n";
    }

    access_log /var/log/nginx/backend_access.log;
    error_log  /var/log/nginx/backend_error.log;
}
```

`server_name _;` matters more than it looks. The load balancer forwards `proxy_set_header Host $host`, so the request that reaches node1 carries the *load balancer's* hostname, not `10.10.X.X`. A server block named after the node's own IP never matches it, the request falls through to whatever is default, and you end up debugging a page you did not write. Match anything and the node stops caring what the front end calls itself.

```bash
sudo nginx -t
sudo systemctl reload nginx
```

Leave `root` out of `nginx.conf` entirely. The document root belongs in `backend.conf` and nowhere else set in two places, it drifts.

Prove each node on its own, before the load balancer exists:

```bash
curl -s http://10.10.X.X/health              # healthy
curl -s http://10.10.X.X/ | grep "Served by" # Served by node1.
```
```bash
curl -s http://10.10.X.X/health              # healthy
curl -s http://10.10.X.X/ | grep "Served by" # Served by node2.
```

If either fails, stop. Nothing downstream will work.

---
- Install Nginx on the load balancer

On the **load balancer**:

```bash
sudo dnf install nginx -y
```
```bash
sudo systemctl enable --now nginx
```

This is the only machine the outside world reaches, so it gets the public ports:

```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
```
```bash
sudo firewall-cmd --reload
sudo firewall-cmd --list-all
```

443 is opened for TLS termination later. Nothing listens on it yet.

---
- Let Nginx open outbound connections (SELinux)

On RHEL family systems SELinux blocks nginx from connecting to anything by default. Skipping this step is the single most common cause of 502 Bad Gateway on a config that is otherwise correct. On the **load balancer**:

```bash
getenforce                                      # Enforcing
sudo setsebool -P httpd_can_network_connect 1
getsebool httpd_can_network_connect             # httpd_can_network_connect --> on
```

If it still fails, the denial is in the audit log and names the exact operation:

```bash
sudo ausearch -m avc -ts recent
sudo grep nginx /var/log/audit/audit.log
```

> Three modes exist: `Enforcing` blocks and logs, `Permissive` logs only, `Disabled` does neither. Permissive is a diagnostic, not a fix.

---
- The load balancer server block

On the **load balancer**:

```bash
sudo vim /etc/nginx/conf.d/loadbalancer.conf
```

```nginx
upstream backend_servers {
    # Round robin is the default; no directive needed.
    #
    # max_fails=3      three failures inside fail_timeout...
    # fail_timeout=30s ...takes the node out for 30s, then probes it again
    server 10.10.x.x:80 max_fails=3 fail_timeout=30s;
    server 10.10.x.x:80 max_fails=3 fail_timeout=30s;

    keepalive 32;                 # pool of idle connections to reuse
}

# $upstream_addr is the whole reason for a custom format: it names the node
log_format upstreamlog '$remote_addr -> $upstream_addr "$request" $status '
                       'upstream=$upstream_status rt=$request_time urt=$upstream_response_time';

server {
    listen 80;
    server_name lb.test 10.10.0.6;

    location / {
        proxy_pass http://backend_servers;

        # Pass original request context to the backend
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # HTTP/1.1 keepalive to the upstream
        proxy_http_version 1.1;
        proxy_set_header Connection "";

        # One dead node should be invisible to the client
        proxy_next_upstream         error timeout http_502 http_503 http_504;
        proxy_next_upstream_tries   2;
        proxy_next_upstream_timeout 15s;

        proxy_connect_timeout 30s;
        proxy_send_timeout    30s;
        proxy_read_timeout    30s;
    }

    # Answered by Nginx itself. Says nothing about backend health.
    location = /lb-health {
        access_log off;
        default_type text/plain;
        return 200 "lb ok\n";
    }

    # Connection counters for this Nginx, trusted network only
    location = /nginx_status {
        stub_status on;
        access_log off;
        allow 10.10.0.0/24;
        deny all;
    }

    location ~ /\. {
        deny all;
    }

    access_log /var/log/nginx/lb_access.log upstreamlog;
    error_log  /var/log/nginx/lb_error.log;
}
```

Comment out the stock default server block here too, then:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

Reload, not restart. Reload lets the old workers finish the requests they are holding before retiring; restart drops every open connection. On the one machine every client is talking to, that distinction is the difference between an invisible config change and an outage.

- Map the name(IP of Load balancer) on your host machine so `lb.test` resolves the same way it does on the lab network:

  - Linux or macOS: `sudo vim /etc/hosts`
  - Windows: open Notepad as Administrator, then `C:\Windows\System32\drivers\etc\hosts`

```
10.10.X.X   lb.test
```

---
## 5. Test

From the **load balancer**, or any client on the network. If this fails, nothing from the host will work:

```bash
curl -s  http://lb.test/lb-health          # lb ok, balancer alive
curl -sI http://lb.test/ | head -3         # 200, Server: nginx
```

- Then from the host browser: `http://lb.test/`, and reload. The page alternates between node1 and node2.


![Page Served from Node 1](<Webpage of Node 1.png>)
---

![Page Served from Node 2](<Webpage of Node 2.png>)


- Watch the routing decision as it happens:

```bash
sudo tail -f /var/log/nginx/lb_access.log.    # 10.10.x.x -> 10.10.x.x:80 "GET / HTTP/1.1" 200 upstream=200 rt=0.003 urt=0.003
```
- Watch both ends at once:
```bash
sudo tail -f /var/log/nginx/lb_access.log     # on the load balancer
```
```bash
sudo tail -f /var/log/nginx/backend_access.log # on each node
```

---
## 6. Test the failover

This is the part worth doing slowly. On **node1**:

```bash
sudo systemctl stop nginx
```

- From the client:
```bash
for i in $(seq 1 20); do curl -s http://lb.test/ | grep -o "node[12]"; done | sort | uniq -c
#   20 node2
```

> Not one request failed. The first attempt after the stop hit node1, was refused, and `proxy_next_upstream error` retried on node2 before the client saw anything. `max_fails=3` then pulled node1 out of rotation for `fail_timeout`. The error log holds what the browser never showed:

```bash
sudo tail -3 /var/log/nginx/lb_error.log
# connect() failed (111: Connection refused) while connecting to upstream
```

Start node1 again. Rotation resumes on its own once `fail_timeout` expires; there is no command to run on the load balancer.

```bash
sudo systemctl start nginx
sleep 31
for i in $(seq 1 6); do curl -s http://lb.test/ | grep -o "node[12]"; done
```

Passive health checks are all open source Nginx has: a node is discovered to be sick only when a real request to it fails, so somebody eats the retry. Active checks — `health_check`, probing on a schedule regardless of traffic — are Nginx Plus. In the meantime, tighten `max_fails=1 fail_timeout=5s` if you want the pool to react faster, and keep `/health` on the nodes for whatever monitors them from outside.

---
**Changing the method**

The method is the first line inside `upstream`. Change it, `nginx -t`, reload, then re-run the 200-request counter from section 5 and watch the numbers move.

- Round robin: the default no directive. Sequential rotation. Right for uniform, stateless nodes:

```nginx
upstream backend {
    server 10.10.0.7:80;
    server 10.10.0.8:80;
}
```

- Least connections: Sends each request to the node holding the fewest. Right when request durations vary — uploads, reports, long polls:

```nginx
upstream backend {
    least_conn;
    server 10.10.0.7:80;
    server 10.10.0.8:80;
}
```

- Weighted: A share per node, combines with any method. Right when the machines are not the same size:

```nginx
upstream backend {
    server 10.10.0.7:80 weight=3;    # ~60% of traffic
    server 10.10.0.8:80 weight=2;    # ~40%
}
```

- IP hash: Pins a client to a node so in-memory sessions survive. For IPv4 the key is the first three octets, so a whole /24 lands on one node which is why an office behind one NAT becomes one node's problem:

```nginx
upstream backend {
    ip_hash;
    server 10.10.0.7:80;
    server 10.10.0.8:80;
}
```

- Generic hash: Route on any variable. `$request_uri` gives cache affinity each node caches a distinct slice and `consistent` limits how many keys reshuffle when a node joins or leaves:

```nginx
upstream backend {
    hash $request_uri consistent;
    server 10.10.0.7:80;
    server 10.10.0.8:80;
}
```

- Random with two choices: Since 1.15.1. Picks two at random, then the emptier of the two. Right for large pools, or when several load balancers front one pool and a shared `least_conn` view would herd:

```nginx
upstream backend {
    random two least_conn;
    server 10.10.0.7:80;
    server 10.10.0.8:80;
}
```

Least response time (`least_time header` or `least_time last_byte`) is Nginx Plus. In open source, `nginx -t` rejects it with `unknown directive "least_time"`.

Two server flags worth knowing. `down` drains a node for maintenance while keeping it in the config, and `backup` holds a node in reserve until every primary is gone the latter is not accepted with `hash`, `ip_hash`, or `random`:

```nginx
upstream backend {
    server 10.10.0.7:80;
    server 10.10.0.8:80 down;      # drained, deliberately
    server 10.10.0.9:80 backup;    # only if every primary is down
}
```

Each worker keeps its own view of which node is failing, so with four workers a dead node is discovered up to four times. `zone` puts that state in shared memory:

```nginx
upstream backend {
    zone backend 64k;
    least_conn;
    server 10.10.0.7:80 max_fails=3 fail_timeout=30s;
    server 10.10.0.8:80 max_fails=3 fail_timeout=30s;
}
```

---
**Beyond the lab**

The pool is two static IPs in a file. Production replaces each part of that sentence.

**Service discovery.** Consul, etcd, or the Kubernetes API rewrite the upstream block as nodes come and go; the Nginx Ingress Controller watches endpoints directly. DNS names work too, with a caveat:

```nginx
upstream backend {
    server backend-service.internal.com;

    resolver 10.0.0.2 valid=30s;
    resolver_timeout 5s;
}
```

Open source resolves that name once, at startup or reload, and refuses to start if it fails. Continuous re-resolution is the `resolve` parameter, which is Nginx Plus. Consul Template covers the gap by regenerating the file and reloading:

```nginx
upstream backend {
    {{ range service "web" }}
    server {{ .Address }}:{{ .Port }};
    {{ end }}
}
```

**Blue/green.** Both environments in the pool, one held with `down`. The cutover is moving that one word, then `nginx -t && systemctl reload nginx`. Without `down` you have not staged a release, you have split traffic:

```nginx
upstream backend {
    server blue-environment:80;         # live
    server green-environment:80 down;   # staged, idle
}
```

**Canary.** Weights shift the share gradually while you watch the metrics; consistent hashing on a cookie keeps a given user on one version for the duration:

```nginx
upstream backend {
    server stable-version:80 weight=90;
    server canary-version:80 weight=10;
}

upstream backend_sticky {
    hash $cookie_canary consistent;
    server stable-version:80;
    server canary-version:80;
}
```

Argo Rollouts and Flagger automate the promotion and the rollback; Kubernetes labels and selectors do the routing.

**Rate limiting.** Zones live in the `http` context, the limits in `location`:

```nginx
limit_req_zone  $binary_remote_addr zone=api:10m rate=10r/s;
limit_conn_zone $binary_remote_addr zone=addr:10m;

location /api/ {
    limit_req  zone=api burst=20 nodelay;   # queue up to 20, no artificial delay
    limit_conn addr 10;                     # 10 concurrent connections per IP
    limit_req_status 429;                   # instead of the default 503
    proxy_pass http://backend_servers;
}
```

`rate` is the sustained ceiling (`r/s` or `r/m`), `burst` the queue depth above it, `nodelay` processes that queue immediately rather than smoothing it. Exempt the internal network by mapping it to an empty key, which disables the limit:

```nginx
geo $limited_region {
    default      0;
    10.10.0.0/24 1;
}

map $limited_region $limit_key {
    0 $binary_remote_addr;
    1 "";
}

limit_req_zone $limit_key zone=geo_aware:10m rate=5r/s;
```

**Tracing.** Propagate the header and the request is followable across the whole path in Jaeger, Zipkin, or Datadog:

```nginx
proxy_set_header traceparent $http_traceparent;
```

**Global.** 

GeoDNS (Route 53, Traffic Manager, Cloud DNS) resolves one name to the nearest regional load balancer; Anycast does it at the IP layer. Each region runs the config above and fails over to another region.

**Cloud.** 

AWS ELB/ALB/NLB, Azure Load Balancer or Application Gateway, and GCP Cloud Load Balancing all terminate in front of Nginx in hybrid designs, or replace it entirely. In Kubernetes, a service annotation maps the Ingress to the cloud load balancer.

Worth carrying into any of them: monitor with the Prometheus Nginx exporter and Grafana, keep `$upstream_addr` in the log format, terminate TLS at the edge and forward `X-Forwarded-Proto`, manage the config with Ansible or Terraform, and gate every deploy on `nginx -t` before the reload.


> Note: The nodes never learned any of this happened. They serve one static file to whoever connects, exactly as they did in section 1, and the entire behaviour a client experiences which node, how many retries, at what rate, over which protocol is decided in one file on one machine. Adding a third node is one `server` line and a reload. That is the reason the pool is worth building this way, and it is the same reason TLS, caching, and rate limiting all belong here rather than in the application.

---
**Passive health checks.** 

Open-source Nginx observes real traffic: when it sees a backend fail, it stops sending to it and spreads requests across the healthy ones. `max_fails=2 fail_timeout=10s` means: if a backend fails twice within 10 seconds, mark it unavailable for 10 seconds, then send one probe; if that succeeds, it returns to rotation.

```bash
echo "127.0.0.1  lb.local" | sudo tee -a /etc/hosts
sudo nginx -t
sudo systemctl reload nginx

# Observe distribution and failover
for i in {1..6}; do curl -s http://lb.local/ >/dev/null && echo "request $i served"; done
kill $(lsof -t -i:5002)     # Kill one backend; requests now go to 5001 and 5003
curl -s http://lb.local/
```

---
### Part 5: Nginx Log Management

```bash
sudo tail -f /var/log/nginx/access.log            # Default access log
sudo tail -f /var/log/nginx/error.log             # Default error log

sudo grep " 502 " /var/log/nginx/access.log       # Bad gateway (upstream down)
sudo grep " 504 " /var/log/nginx/access.log       # Gateway timeout (upstream too slow)
sudo grep "connect() failed" /var/log/nginx/error.log   # Backend connection failures
```

A custom log format that records the upstream address is invaluable for load-balancer debugging; add to the `http` block of `nginx.conf`:

```nginx
log_format upstream '$remote_addr - $host [$time_local] '
                    '"$request" $status $body_bytes_sent '
                    '$upstream_addr $upstream_status';
```

---
### Part 6: Clean Up Nginx Test Processes

```bash
kill $(lsof -t -i:5000) $(lsof -t -i:5001) $(lsof -t -i:5002) $(lsof -t -i:5003) 2>/dev/null || true
```

---
## Lab 5.1.C: Apache Tomcat - Java Application Server

Tomcat is the deployment target for the Java `.war` produced by the CI/CD pipeline in **Section 5.4**. This lab installs Tomcat, runs it as a systemd service, deploys a test WAR, and puts Nginx in front of it.

### Part 1: Install Java (OpenJDK)

Tomcat 10.1.x requires Java 11 or later. We use Tomcat 10.1.x in this course; OpenJDK 17 (current LTS) is recommended.

```bash
sudo dnf install java-17-openjdk java-17-openjdk-devel -y
java -version
javac -version
dirname $(dirname $(readlink -f $(which java)))    # Note this JAVA_HOME path
```

---

### Part 2: Create a Dedicated Tomcat User

```bash
# System user, no login shell, home at /opt/tomcat
sudo useradd -r -m -U -d /opt/tomcat -s /bin/false tomcat
id tomcat
```

---

### Part 3: Download and Install Tomcat

Check the current stable release at `tomcat.apache.org` before running these commands; the version will change over time.

```bash
TOMCAT_VERSION=10.1.44

wget https://dlcdn.apache.org/tomcat/tomcat-10/v${TOMCAT_VERSION}/bin/apache-tomcat-${TOMCAT_VERSION}.tar.gz
ls -lh apache-tomcat-${TOMCAT_VERSION}.tar.gz

sudo mkdir -p /opt/tomcat
sudo tar -xzf apache-tomcat-${TOMCAT_VERSION}.tar.gz -C /opt/tomcat --strip-components=1
ls /opt/tomcat/
```

You should see: `bin/  conf/  lib/  logs/  temp/  webapps/  work/`

---

### Part 4: Set Permissions

```bash
sudo chown -R tomcat:tomcat /opt/tomcat
sudo chmod +x /opt/tomcat/bin/*.sh
ls -l /opt/tomcat/bin/startup.sh
```

---

### Part 5: Create a systemd Service Unit

Running Tomcat under systemd means it starts at boot, restarts on failure, and integrates with `systemctl` and `journalctl`. Create `/etc/systemd/system/tomcat.service`:

```ini
[Unit]
Description=Apache Tomcat Web Application Container
After=network.target

[Service]
Type=forking
User=tomcat
Group=tomcat

Environment="JAVA_HOME=/usr/lib/jvm/java-17-openjdk"
Environment="CATALINA_PID=/opt/tomcat/temp/tomcat.pid"
Environment="CATALINA_HOME=/opt/tomcat"
Environment="CATALINA_BASE=/opt/tomcat"
Environment="CATALINA_OPTS=-Xms512M -Xmx1024M -server -XX:+UseParallelGC"
Environment="JAVA_OPTS=-Djava.awt.headless=true -Djava.security.egd=file:/dev/./urandom"

ExecStart=/opt/tomcat/bin/startup.sh
ExecStop=/opt/tomcat/bin/shutdown.sh

Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Confirm the exact `JAVA_HOME` with `dirname $(dirname $(readlink -f $(which java)))`, then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now tomcat
sudo systemctl status tomcat
sudo tail -f /opt/tomcat/logs/catalina.out       # Look for "Server startup in [N] milliseconds"
```

If Tomcat fails to start, check: (1) `JAVA_HOME` correct (`ls $JAVA_HOME/bin/java`); (2) `tomcat` owns `/opt/tomcat` (`ls -la /opt/tomcat/`); (3) port 8080 free (`ss -tlnp | grep 8080`).

---

### Part 6: Open Firewall and Verify

```bash
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload
```

Test: `http://server-ip:8080` — you should see the Tomcat welcome page.

---

### Part 7: Configure the Tomcat Manager Application

The Manager app provides a web UI and an HTTP API for deploying, undeploying, and reloading WARs. The CI/CD pipeline in Section 5.4 deploys through this same API. Edit `/opt/tomcat/conf/tomcat-users.xml` and add before `</tomcat-users>`:

```xml
<role rolename="manager-gui"/>
<role rolename="manager-script"/>
<user username="devops"
      password="DevOps@2026!"
      roles="manager-gui,manager-script"/>
```

`manager-gui` grants the web interface; `manager-script` grants the HTTP API used by CI deploy plugins. By default the Manager restricts access to localhost. To allow it from your network (for remote CI deployments), edit `/opt/tomcat/webapps/manager/META-INF/context.xml` and, **for lab use only**, comment out the address valve:

```xml
<!--
<Valve className="org.apache.catalina.valves.RemoteAddrValve"
       allow="127\.\d+\.\d+\.\d+|::1|0:0:0:0:0:0:0:1" />
-->
```

```bash
sudo systemctl restart tomcat
```

Test the Manager at `http://server-ip:8080/manager/html` and log in with the `devops` credentials.

---

### Part 8: Deploy a WAR File

A WAR (Web Application Archive) is a ZIP-format package containing a complete Java web application.

**Method 1 — copy to `webapps/` (simplest for labs):**

```bash
wget https://tomcat.apache.org/tomcat-10.1-doc/appdev/sample/sample.war -O /tmp/sample.war
sudo cp /tmp/sample.war /opt/tomcat/webapps/
sudo chown tomcat:tomcat /opt/tomcat/webapps/sample.war
sudo tail -f /opt/tomcat/logs/catalina.out       # Watch auto-deploy
```

Test: `http://server-ip:8080/sample/`

**Method 2 — Manager API (how the CI pipeline deploys):**

```bash
curl -u devops:DevOps@2026! \
     -T /tmp/sample.war \
     "http://localhost:8080/manager/text/deploy?path=/myapp&update=true"
# Success: OK - Deployed application at context path [/myapp]
```

This curl command is exactly how the CI deploy step in Section 5.4 interacts with Tomcat.

```bash
# List and undeploy
curl -u devops:DevOps@2026! http://localhost:8080/manager/text/list
curl -u devops:DevOps@2026! "http://localhost:8080/manager/text/undeploy?path=/myapp"
```

---

### Part 9: Nginx as Reverse Proxy in Front of Tomcat (Production Pattern)

In production Tomcat is never exposed directly on port 8080. Nginx sits in front, terminates TLS, and proxies to Tomcat — the edge-termination pattern from Section 5.1 §5, and the target the CI/CD pipeline builds toward. Create `/etc/nginx/conf.d/tomcat-proxy.conf`:

```nginx
server {
    listen 80;
    server_name java.local;

    location / {
        proxy_pass http://127.0.0.1:8080;

        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_http_version 1.1;
        proxy_set_header Connection "";

        proxy_connect_timeout 10s;
        proxy_read_timeout    60s;    # Java apps can be slow to start; allow longer
    }

    access_log /var/log/nginx/tomcat_access.log;
    error_log  /var/log/nginx/tomcat_error.log;
}
```

```bash
echo "127.0.0.1  java.local" | sudo tee -a /etc/hosts
sudo nginx -t
sudo systemctl reload nginx
```

Test: `http://java.local/sample/` — Tomcat now reached through Nginx on port 80.

---
# Section 5.2: Delivery Friendly Applications and the Twelve Factor Model

## 1. What Makes an Application Friendly to Automated Delivery

Section 5.1 deployed servers. This section builds the **reference application** those servers will run — and does so deliberately, because most delivery pain is designed into the application long before the pipeline is written. An application is "delivery-friendly" when a machine, with no human in the loop, can configure it, test it, and build it identically every time. Three properties make this possible.

### 1.1 Environment-Sourced Configuration

Configuration that varies between environments — database URLs, credentials, feature flags, the port to listen on — must come from the **environment**, not from files baked into the code.

- **Why:** the *same build artefact* must run in development, staging, and production. If configuration is compiled in, each environment needs a different build, and "the thing you tested" is no longer "the thing you shipped."
- **How:** read config from environment variables (or a secrets manager) at startup; commit a documented list of the variables, never their values; provide safe defaults only for genuinely non-secret settings.

```python
# Good: configuration is read from the environment at startup
import os
DATABASE_URL = os.environ["DATABASE_URL"]          # required; fail fast if missing
PORT         = int(os.environ.get("PORT", "8000")) # non-secret default is acceptable
DEBUG        = os.environ.get("DEBUG", "false").lower() == "true"
```

The corollary is the *twelve-factor rule of thumb*: could you open-source the repository right now without leaking a single credential? If not, configuration is in the wrong place.

### 1.2 Testable Units

The application must be decomposed so that behaviour can be verified **without** standing up the whole system. That means business logic lives in small functions and classes with explicit inputs and outputs, separated from I/O (HTTP handlers, database calls, the filesystem). Dependencies are injected rather than reached for globally, so a test can substitute a fake.

- A pure function `calculate_total(items) -> Decimal` is trivially testable.
- The same logic buried inside an HTTP handler that also reads the database and writes a response is not — you can only test it by running a server and a database.

Testable units are what make the **test pyramid** in Section 5.3 possible; an application without them can only ever be tested end-to-end, slowly and flakily.

### 1.3 Repeatable Builds

Building the application twice from the same source must produce functionally identical artefacts, on any machine, with no manual steps.

- **Pin dependencies** to exact versions with a lockfile (`requirements.txt` + hashes, `package-lock.json`, `pom.xml` with fixed versions). "Latest" is not repeatable.
- **Isolate the build** from the host — a container image or a clean virtual environment — so a developer laptop and a CI runner produce the same result.
- **One command** builds everything: `make build`, `docker build`, or an equivalent. If the build lives only in someone's shell history, it is not repeatable.

Repeatable builds are the precondition for the pipeline caching in Section 5.4: you can only safely reuse a cached artefact if identical inputs are guaranteed to produce identical outputs.

---

## 2. The Twelve-Factor App: The Enduring and the Dated

The **twelve-factor methodology** (Heroku, 2011) codified how to build applications for automated delivery. More than a decade on, some factors are foundational and some reflect the platform of their era. A mature engineer knows which is which.

### 2.1 The Enduring Factors

These remain correct and underlie everything in this module:

- **III. Config in the environment** — configuration from the environment, strictly separated from code (Section 1.1 above).
- **X. Dev/prod parity** — keep environments as similar as possible so tests are predictive.
- **VI. Processes are stateless** — the app holds no sticky in-process state; session and cache state live in a backing store (this is what made stateless load balancing viable in Lab 5.1.B).
- **IV. Backing services are attached resources** — a database, cache, or queue is reached by a URL from config and can be swapped without code changes.
- **V. Strictly separate build, release, run** — a build stage produces an artefact, a release stage binds it to config, and the run stage executes it; releases are immutable and numbered.
- **XI. Logs as event streams** — write to stdout/stderr and let the platform route logs; do not manage log files inside the app (note how the reference app below logs to stdout, while Nginx in Section 5.1 handled *its own* access logs at the edge).

### 2.2 The Dated (or Debated) Elements

These need reinterpretation in a container- and Kubernetes-centric world:

- **The "one codebase, one app" mapping** predates the modern monorepo, where many deployable services share a single repository. The principle (a codebase maps to a *release lineage*) survives; the strict one-repo-per-app reading does not.
- **Factor XII, "run admin tasks as one-off processes,"** assumed a Heroku-style `run` command. Today the same intent is met by Kubernetes Jobs, init containers, or migration steps in the pipeline — the *mechanism* is dated, the *idea* (admin tasks are first-class, versioned, and repeatable) endures.
- **"Port binding" (VII)** assumed the app exports HTTP by binding a port directly. Behind a container orchestrator and a service mesh, port binding is mediated by the platform; the app still listens on a port from config (Section 1.1), but "self-contained web server" is now the platform's job as much as the app's.
- **Concurrency via the process model (VIII)** — "scale out by adding processes" is still sound, but async runtimes and autoscaling controllers have made the picture richer than "add more unix processes."

The through-line: twelve-factor's *goals* — statelessness, environment config, build/release/run separation, disposability — are exactly the delivery-friendly properties of Section 1. Its *prescriptions* sometimes show their 2011 origins.

---

# Laboratory Exercise

---

## Lab 5.2: Build the Reference Application

Build a small, delivery-friendly HTTP service that Sections 5.3 and 5.4 will test and ship. It has one non-trivial piece of business logic (an order-total calculation) deliberately separated from its HTTP layer, so it can be unit-tested in isolation.

### Part 1: Project Layout

```
refapp/
├── refapp/
│   ├── __init__.py
│   ├── pricing.py        # pure business logic — no I/O
│   └── app.py            # HTTP layer (Flask) — thin, delegates to pricing
├── tests/
│   ├── test_pricing.py   # unit tests (Section 5.3)
│   └── test_api.py       # integration tests (Section 5.3)
├── requirements.txt      # pinned dependencies — repeatable builds
├── Dockerfile            # isolated, repeatable build
└── Makefile              # one command each: build, test, run
```

### Part 2: The Testable Unit — `refapp/pricing.py`

```python
from decimal import Decimal, ROUND_HALF_UP

TAX_RATE = Decimal("0.13")   # a domain constant, not configuration

def line_total(unit_price: Decimal, quantity: int) -> Decimal:
    if quantity < 0:
        raise ValueError("quantity must not be negative")
    return (unit_price * quantity).quantize(Decimal("0.01"), ROUND_HALF_UP)

def order_total(items: list[tuple[Decimal, int]]) -> Decimal:
    """items = [(unit_price, quantity), ...] -> tax-inclusive total."""
    subtotal = sum((line_total(p, q) for p, q in items), Decimal("0"))
    tax = (subtotal * TAX_RATE).quantize(Decimal("0.01"), ROUND_HALF_UP)
    return subtotal + tax
```

Every function here has explicit inputs and outputs and touches no network, database, or filesystem. This is the "testable unit" of Section 1.2.

### Part 3: Environment-Sourced Configuration — `refapp/app.py`

```python
import os
from decimal import Decimal
from flask import Flask, request, jsonify
from .pricing import order_total

def create_app() -> Flask:
    app = Flask(__name__)
    # Configuration comes from the environment, never hard-coded
    app.config["GREETING"] = os.environ.get("GREETING", "Reference App")
    app.config["PORT"]     = int(os.environ.get("PORT", "8000"))

    @app.get("/health")
    def health():
        return jsonify(status="ok", app=app.config["GREETING"])

    @app.post("/total")
    def total():
        payload = request.get_json(force=True)
        items = [(Decimal(str(i["price"])), int(i["qty"])) for i in payload["items"]]
        return jsonify(total=str(order_total(items)))

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=app.config["PORT"])  # logs go to stdout
```

The HTTP layer is thin: it parses the request, calls `order_total`, and serialises the result. All logic worth testing lives in `pricing.py`.

### Part 4: Repeatable Build — pinned deps, Dockerfile, Makefile

```
# requirements.txt — exact versions only
Flask==3.0.3
gunicorn==22.0.0
pytest==8.2.0
```

```dockerfile
# Dockerfile — isolated build, identical on laptop and CI
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=8000
EXPOSE 8000
# Stateless process, config from env, port from env, logs to stdout
CMD ["gunicorn", "-b", "0.0.0.0:8000", "refapp.app:create_app()"]
```

```makefile
# Makefile — one command each
build:
	docker build -t refapp:local .

test:
	pytest -q

run:
	GREETING="Reference App" PORT=8000 python -m refapp.app
```

### Part 5: Verify the Delivery-Friendly Properties

```bash
make build          # repeatable: same inputs -> same image
docker run --rm -e GREETING="Staging" -e PORT=8000 -p 8000:8000 refapp:local &
curl -s localhost:8000/health           # {"app":"Staging","status":"ok"}
curl -s -X POST localhost:8000/total \
     -H 'Content-Type: application/json' \
     -d '{"items":[{"price":"10.00","qty":2},{"price":"5.50","qty":1}]}'
# {"total":"28.82"}  ->  (20.00 + 5.50) = 25.50 subtotal + 13% tax 3.32 = 28.82
```

The **same image** ran as "Staging" purely by changing an environment variable — no rebuild. This image is what Section 5.4's pipeline will build once and promote across environments. In production it sits behind Nginx exactly as in Lab 5.1.B, with TLS terminated at the edge (Section 5.1 §5).

---

# Section 5.3: Testing Strategy

---

# Theory

---

## 1. Testing as a First-Class Engineering Concern

A test suite is not a chore bolted on at the end; it is part of the system's design. The reference application in Section 5.2 was *built* to be testable — logic separated from I/O, dependencies injected, config externalised — precisely so a fast, layered suite is possible. The strategy questions that follow are engineering decisions with real trade-offs: how to shape the suite, how to keep services compatible, how to manage test data, and what to do with a test that fails at random.

---

## 2. The Test Pyramid

The test pyramid describes the healthy *proportion* of tests by scope. Cost and speed rise as you move up; the number of tests should fall.

```
          /\        End-to-end        few, slow, brittle
         /  \       (full system)     high confidence, high cost
        /----\
       /      \     Integration       some, medium speed
      /        \    (app + real deps)
     /----------\
    /            \  Unit               many, fast, isolated
   /______________\ (pure logic)      cheap, precise failures
```

- **Unit tests** exercise a single testable unit (e.g. `order_total`) with no I/O. They are milliseconds each; you can have thousands. When one fails it points at the exact function.
- **Integration tests** exercise the app against real adjacent services — a database in a container, the HTTP layer end to end within the service. Fewer, slower, and they catch wiring mistakes units cannot.
- **End-to-end tests** drive the whole deployed system as a user would. They give the highest confidence but are slow and the most brittle, so keep them few and reserved for critical journeys.

The anti-pattern is the **ice-cream cone** — many end-to-end tests, few units. It is slow, flaky, and gives vague failures. Effort belongs at the base.

---

## 3. Contract Testing

When services talk to each other, end-to-end tests across all of them are slow and fragile. **Contract testing** verifies each side against a shared, versioned **contract** (the expected request/response shape) *independently*:

- The **consumer** test asserts "I send this request and expect this response shape," producing a contract.
- The **provider** test replays that contract against the real provider and asserts it still honours it.

Neither test needs both services running at once, so they stay in the fast integration tier rather than the slow end-to-end tier. Contract testing is what lets independently deployed services evolve without a combinatorial explosion of cross-service tests — the provider learns it has broken a consumer *before* deploying, from its own pipeline. Tools such as Pact implement this consumer-driven pattern.

---

## 4. Test Data Management

Tests need data, and where that data comes from determines whether the suite is fast, deterministic, and isolated.

- **Build data in the test, not from a shared database.** Each test constructs exactly the data it needs (fixtures/factories) and tears it down afterwards, so tests don't depend on order or leak state into each other.
- **Isolate integration data.** Run integration tests against a disposable database (an ephemeral container, or a transaction rolled back after each test) so one test's writes never pollute another's reads.
- **Keep production data out.** Real customer data in tests is a privacy and compliance risk; use synthetic or anonymised data that is safe to commit and reproduce.
- **Make it deterministic.** Freeze clocks, seed random generators, and avoid "today" or live external state — a test that depends on the wall clock or a third-party API is a flaky test waiting to happen (Section 5).

Good test-data hygiene is a direct enabler of the pipeline **parallelism** in Section 5.4: only tests that own their data can safely run at the same time.

---

## 5. Quarantining a Flaky Test — an Engineering Decision

A **flaky test** passes and fails on the same code without any change. Flakiness is corrosive: once developers see red builds that "just need a re-run," they start ignoring failures, and a genuine regression slips through behind the noise.

The disciplined response is to **quarantine** the test — a deliberate, tracked decision, not a silent deletion:

1. **Detect** flakiness (e.g. the test fails then passes on retry, or a flaky-test detector flags it across runs).
2. **Quarantine:** move it out of the blocking suite so it no longer fails the build, but keep running it in a non-blocking lane so its signal isn't lost.
3. **Ticket it:** file a tracked issue with an owner and a deadline. Quarantine is a loan against reliability, not a graveyard.
4. **Fix the root cause** — usually a timing/ordering dependency, shared mutable state, or reliance on an external service — then **return the test to the blocking suite**.

The trade-off is explicit: quarantining trades a small, *known* loss of coverage for a large gain in signal quality, because a suite everyone trusts and heeds is worth more than a suite that is nominally complete but routinely ignored. What you must never do is leave a test quarantined and untracked — that is how coverage quietly rots.

---

# Laboratory Exercise

---

## Lab 5.3: A Layered Test Suite for the Reference Application

Add unit and integration tests to the `refapp` project from Lab 5.2, then wire in a flaky-test example and quarantine it.

### Part 1: Unit Tests (the base) — `tests/test_pricing.py`

```python
from decimal import Decimal
import pytest
from refapp.pricing import line_total, order_total

def test_line_total_rounds_half_up():
    assert line_total(Decimal("1.005"), 1) == Decimal("1.01")

def test_order_total_applies_tax():
    # (10.00 * 2) + (5.50 * 1) = 25.50 subtotal; +13% tax = 28.82
    items = [(Decimal("10.00"), 2), (Decimal("5.50"), 1)]
    assert order_total(items) == Decimal("28.82")

def test_negative_quantity_rejected():
    with pytest.raises(ValueError):
        line_total(Decimal("10.00"), -1)
```

These run in milliseconds, need no server or database, and pinpoint the failing function. You can add dozens more cheaply — the wide base of the pyramid.

### Part 2: Integration Test (the middle) — `tests/test_api.py`

```python
import json
from refapp.app import create_app

def client():
    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()

def test_total_endpoint_returns_tax_inclusive_total():
    resp = client().post(
        "/total",
        data=json.dumps({"items": [{"price": "10.00", "qty": 2},
                                    {"price": "5.50", "qty": 1}]}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert resp.get_json()["total"] == "28.82"

def test_health_reads_config_from_env(monkeypatch):
    monkeypatch.setenv("GREETING", "IntegrationEnv")
    resp = client().get("/health")
    assert resp.get_json()["app"] == "IntegrationEnv"   # config truly from env
```

This exercises the HTTP layer wired to the real logic — fewer of these than unit tests, and slightly slower.

### Part 3: Deterministic Test Data

Note that both files above **construct their own data inline** and rely on no shared, pre-seeded database, and the config test sets its environment explicitly with `monkeypatch` rather than depending on ambient state. That is what lets these tests run in any order and in parallel (Section 5.4).

### Part 4: Introduce, Detect, and Quarantine a Flaky Test

A test that depends on the wall clock is a classic flake. Add one to see the pattern, then quarantine it:

```python
# tests/test_flaky.py
import time
import pytest

@pytest.mark.quarantine          # tagged: runs in a non-blocking lane, not the gate
def test_timing_sensitive():
    start = time.time()
    time.sleep(0.01)
    # Flaky: on a loaded CI runner the elapsed time can exceed the bound
    assert time.time() - start < 0.02
```

Register the marker and exclude it from the blocking run in `pytest.ini`:

```ini
[pytest]
markers =
    quarantine: known-flaky tests; tracked in issue REF-142, excluded from the gate
```

```bash
# Blocking suite (the gate) — quarantined tests excluded, so it stays trustworthy
pytest -q -m "not quarantine"

# Non-blocking lane — quarantined tests still run so their signal is not lost
pytest -q -m "quarantine" || true
```

The flaky test no longer fails the build, but it is still tracked (issue `REF-142`) and still executed for visibility. The next step in a real project is to fix the timing dependency — for example, inject a clock the test can control — and move the test back under the gate.

---

# Section 5.4: Pipeline Speed as a Product Feature

---

# Theory

---

## 1. Speed Is a Feature, Not a Nicety

The layered suite of Section 5.3 only helps if developers actually wait for it. A pipeline that takes forty minutes is a pipeline people route around — they merge on green-ish, batch changes, and stop trusting the gate. Fast feedback changes behaviour: small changes, merged often, verified while the context is still in the developer's head. So pipeline duration is treated as a **product feature** with a target (for example, "under ten minutes to first signal") and is measured over time like any other. Three levers deliver it: caching, parallelism, and selective scheduling.

---

## 2. Caching

Most of a pipeline's time is spent redoing work whose inputs did not change. Caching reuses prior results keyed on their inputs.

- **Dependency caches.** Restore `pip`, `npm`, or Maven downloads keyed on the **lockfile hash**. The cache is reused only while dependencies are unchanged and rebuilt automatically when the lockfile changes. This is safe precisely because Section 5.2 made builds repeatable — identical inputs guarantee identical dependencies.
- **Build-layer caches.** Docker layer caching reuses image layers whose instructions and inputs are unchanged. Ordering the `Dockerfile` so rarely-changed steps (installing dependencies) come *before* frequently-changed steps (copying source) maximises cache hits — which is exactly why the Lab 5.2 `Dockerfile` copies `requirements.txt` and installs *before* copying the application code.
- **The cache-key discipline.** A cache is only correct if its key captures every input that affects the output. Too broad a key serves stale results; too narrow a key never hits. Key on content hashes, not on "latest."

---

## 3. Parallelism

Independent work should run at the same time rather than in sequence.

- **Parallel jobs.** Lint, unit tests, and a type check share no state and can run as three simultaneous jobs; total wall-clock time becomes the slowest one, not their sum.
- **Test sharding.** A large unit suite is split across N runners (for example, by test file) and executed concurrently. This only works because Section 5.3's tests own their own data and share no state — sharding a suite full of order-dependent tests produces random failures.
- **Fan-out / fan-in.** Build once, then fan out to run many test shards against that single artefact, then fan in to a deploy step that runs only if every shard passed. The reference image is built one time and reused, never rebuilt per shard.

Parallelism has a floor: adding runners past the point where the longest single job dominates buys nothing, and it costs money. Parallelise until the critical path is a single irreducible job.

---

## 4. Selective Scheduling

The fastest work is the work you correctly skip. Selective scheduling runs only what a given change could affect.

- **Path-based triggers.** A change touching only documentation need not run the full build-and-test pipeline; a change under `refapp/pricing.py` must. Pipelines can gate whole stages on which paths changed.
- **Affected-target selection.** Build systems that understand the dependency graph (Bazel, Nx, Turborepo) compute the set of targets downstream of a change and test only those. In a monorepo this is the difference between testing one service and testing forty.
- **Test impact analysis.** More advanced setups map which tests exercise which code and, on a given change, run only the covering tests in the fast gate — deferring the full suite to a scheduled run.

The safeguard is honesty about the dependency graph: selective scheduling is only safe when "what this change affects" is computed correctly. When in doubt the system must fall back to running more, not less — a fast pipeline that ships a regression is not fast, it is broken. A common, safe pattern is *selective on every push, exhaustive on merge to main and on a nightly schedule*.

---

# Laboratory Exercise

---

## Lab 5.4: A Fast Pipeline for the Reference Application

Assemble a CI pipeline for `refapp` that applies all three levers, builds the image once, runs the layered suite from Section 5.3, and deploys the WAR-equivalent artefact to the environment stood up in Section 5.1. The example uses GitHub Actions syntax; the concepts map directly to GitLab CI, Jenkins, or any modern runner.

```yaml
# .github/workflows/refapp.yml
name: refapp

on:
  push:
    # Selective scheduling: skip the pipeline for docs-only changes
    paths-ignore: ["**.md", "docs/**"]

jobs:
  # ---- Parallel job 1: fast checks, with a dependency cache ----
  unit:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        shard: [1, 2]          # parallelism: shard the unit suite across 2 runners
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"          # caching: keyed on requirements.txt hash
      - run: pip install -r requirements.txt
      # Quarantined tests excluded from the gate (Section 5.3)
      - run: pytest -q -m "not quarantine" --splits 2 --group ${{ matrix.shard }}

  # ---- Parallel job 2: lint, runs at the same time as `unit` ----
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12", cache: "pip" }
      - run: pip install -r requirements.txt && python -m pyflakes refapp

  # ---- Build once; fan-in requires unit + lint to have passed ----
  build:
    needs: [unit, lint]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/build-push-action@v6
        with:
          context: .
          tags: refapp:${{ github.sha }}
          cache-from: type=gha       # build-layer cache (Section 2)
          cache-to: type=gha,mode=max

  # ---- Deploy the single artefact built above (only on main) ----
  deploy:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - run: |
          # Same Manager API call demonstrated in Lab 5.1.C, Part 8
          curl -u "$TOMCAT_USER:$TOMCAT_PASS" \
               -T build/refapp.war \
               "http://$TARGET:8080/manager/text/deploy?path=/refapp&update=true"
        env:
          TOMCAT_USER: ${{ secrets.TOMCAT_USER }}   # config + secrets from the environment
          TOMCAT_PASS: ${{ secrets.TOMCAT_PASS }}
          TARGET:      ${{ vars.DEPLOY_TARGET }}
```

What each lever contributes here: **caching** (`cache: pip`, `cache-from: gha`) skips re-downloading and re-building unchanged inputs; **parallelism** (`unit` and `lint` run together, `unit` shards across two runners); **selective scheduling** (`paths-ignore` skips docs-only pushes, `if: github.ref == 'refs/heads/main'` deploys only from main). The image is built exactly once in `build` and the deploy consumes that single artefact — the "build once, promote everywhere" principle from Section 5.2, closing the loop back to the servers configured in Section 5.1.

---

*End of Module 5: Web Servers, Applications, and Testing Strategy.*

*This module deployed web and application services (Section 5.1), built a delivery-friendly reference application governed by externalised config, testable units, and repeatable builds (Section 5.2), placed it under a layered test suite (Section 5.3), and delivered it through a pipeline treated as a product feature (Section 5.4) — fulfilling the module objective in support of CLO 5.*
