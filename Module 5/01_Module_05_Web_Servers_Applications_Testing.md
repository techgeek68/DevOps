# Module 5: Web Servers, Applications, and Testing Strategy

**Module objective.** Deploy web and application services and construct a delivery friendly reference application governed by a layered test suite. *Supports CLO 5.*

**How this module is organised.** The module moves from infrastructure to application to pipeline:

- **Section 5.1 Web and Application Servers.** Where each server sits, the process models of the two dominant web servers, virtual hosts, reverse proxying, and where to terminate TLS.
- **Section 5.2 Delivery Friendly Applications and the Twelve Factor Model.** The application properties that make automated delivery possible, and which parts of the twelve-factor model still hold.
- **Section 5.3 Testing Strategy.** The test pyramid, contract testing, test data management, and the decision to quarantine a flaky test.
- **Section 5.4 Pipeline Speed as a Product Feature.** Caching, parallelism, and selective scheduling.

Sections 5.2–5.4 all operate on one **reference application** that is introduced in Section 5.2 and reused throughout, so the module builds a single coherent artefact rather than a set of disconnected exercises.

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

Verify: open `http://127.0.0.1` in a browser or run `curl -I http://127.0.0.1`. You should see the Apache test page.

Key configuration files:

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
sudo mkdir -p /var/www/html/{page1,page2}

# Set ownership (Apache runs as the 'apache' user on RHEL/CentOS)
sudo chown -R apache:apache /var/www/html
sudo chmod -R 755 /var/www/html

# Verify
ls -ld /var/www/html/
```

Create the homepage `/var/www/html/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DevOps Lab - Static Site</title>
    <style>
        body { font-family: sans-serif; max-width: 900px; margin: 2rem auto; padding: 20px; color: #333; }
        header { border-bottom: 2px solid #ddd; padding-bottom: 20px; margin-bottom: 30px; }
        h1 { color: #2c3e50; }
        nav a { color: #0066cc; text-decoration: none; padding: 8px 16px; margin-right: 8px; }
        nav a:hover { background-color: #f0f0f0; border-radius: 4px; }
    </style>
</head>
<body>
    <header>
        <h1>DevOps Lab</h1>
        <p>Apache static website — served from /var/www/html</p>
        <nav>
            <a href="/page1">Page 1</a>
            <a href="/page2">Page 2</a>
        </nav>
    </header>
    <main>
        <p>Apache HTTP Server is running correctly.</p>
    </main>
</body>
</html>
```

Create `page1` and `page2` with similar content. Then:

```bash
sudo apachectl configtest
sudo systemctl restart httpd
```

Test: `http://localhost/`, `http://localhost/page1`, `http://localhost/page2`.

---

### Part 3: Name-Based Virtual Hosts

A virtual host allows one Apache server to serve multiple websites on one IP, distinguished by the `Host:` HTTP header sent by the client.

```bash
sudo mkdir -p /var/www/myapp.local
sudo chown -R apache:apache /var/www/myapp.local
sudo chmod -R 755 /var/www/myapp.local
sudo vim /var/www/myapp.local/index.html
```

```html
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>myapp.local</title></head>
<body>
    <h1>Virtual host: myapp.local</h1>
    <p>Served from /var/www/myapp.local</p>
</body>
</html>
```

Create the virtual host configuration `/etc/httpd/conf.d/myapp.local.conf`:

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

`Options -Indexes` prevents Apache from listing directory contents when no index file exists. Always set this in production — exposing directory listings reveals your file structure to anyone on the internet.

```bash
sudo apachectl configtest
sudo httpd -S                    # Show all configured virtual hosts
sudo systemctl restart httpd
echo "127.0.0.1  myapp.local  www.myapp.local" | sudo tee -a /etc/hosts
```

Test: `http://myapp.local/`. To host more sites, repeat the pattern: each site gets its own directory and its own `.conf` file in `/etc/httpd/conf.d/`.

---
### Part 4: HTTPS with a Self-Signed Certificate

HTTPS encrypts traffic between client and server using TLS. This lab terminates TLS **at Apache** for a single-server setup; in the multi-tier pattern of Section 5.1 §5 you would instead terminate at Nginx. Certificate options:

- **Let's Encrypt:** Free, automated, 90-day certificates via `certbot`. Requires a publicly routable domain. Standard for production.
- **Commercial CA:** Paid certificates (DigiCert, Sectigo). Used when extended validation is required.
- **Self-signed:** Generated locally, not trusted by browsers. Use only in lab or internal environments.

**Install mod_ssl and generate a self-signed certificate:**

```bash
sudo dnf install mod_ssl openssl -y

sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/pki/tls/private/myapp.key \
    -out /etc/pki/tls/certs/myapp.crt \
    -subj "/C=NP/ST=Bagmati/L=Kathmandu/O=DevOps Lab/CN=myapp.local"
```

Flags: `-x509` self-signed certificate; `-nodes` no passphrase on the key; `-days 365` one year validity; `-newkey rsa:2048` new 2048-bit RSA key pair; `-subj` subject fields without an interactive prompt.

**Create the HTTPS virtual host** `/etc/httpd/conf.d/myapp.local-ssl.conf`:

```apache
# HTTPS virtual host
<VirtualHost *:443>
    ServerName myapp.local
    DocumentRoot /var/www/myapp.local
    ServerAdmin admin@myapp.local

    SSLEngine on
    SSLCertificateFile /etc/pki/tls/certs/myapp.crt
    SSLCertificateKeyFile /etc/pki/tls/private/myapp.key

    # Disable deprecated protocols; allow TLS 1.2 and 1.3 only
    SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1

    # Security headers
    Header always set Strict-Transport-Security "max-age=63072000; includeSubDomains"
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-Frame-Options "DENY"

    <Directory "/var/www/myapp.local">
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog /var/log/httpd/myapp.local_ssl_error.log
    CustomLog /var/log/httpd/myapp.local_ssl_access.log combined
</VirtualHost>

# Redirect all HTTP to HTTPS
<VirtualHost *:80>
    ServerName myapp.local
    Redirect permanent / https://myapp.local/
</VirtualHost>
```

```bash
sudo apachectl configtest
sudo systemctl restart httpd
```

Test: `https://myapp.local/`. The browser warns because the cert is self-signed; proceed past it and confirm the padlock shows TLS is active.

**Let's Encrypt for production (real domain required):**

```bash
sudo dnf install certbot python3-certbot-apache -y
sudo certbot --apache -d example.com -d www.example.com
sudo certbot renew --dry-run                              # Test auto-renewal
```

---

### Part 5: PHP Website with PHP-FPM

Apache serves PHP through **PHP-FPM** (FastCGI Process Manager), the current standard. PHP runs as a separate process pool; Apache proxies PHP requests to it. This is more efficient and more secure than in-process modules, and supports multiple PHP versions per server.

```bash
sudo dnf install php php-fpm php-mysqlnd php-json php-xml php-mbstring -y
sudo systemctl enable --now php-fpm
sudo systemctl status php-fpm
php -v
```

**Create virtual host configuration** `/etc/httpd/conf.d/phpsite.conf`:

```apache
<VirtualHost *:80>
    ServerName phpsite.local
    DocumentRoot /var/www/phpsite
    ServerAdmin admin@phpsite.local

    # Forward .php files to PHP-FPM via Unix socket
    <FilesMatch \.php$>
        SetHandler "proxy:unix:/run/php-fpm/www.sock|fcgi://localhost"
    </FilesMatch>

    <Directory "/var/www/phpsite">
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog /var/log/httpd/phpsite_error.log
    CustomLog /var/log/httpd/phpsite_access.log combined
</VirtualHost>
```

**Create the PHP application** `/var/www/phpsite/index.php`:

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
    <title>PHP Demo</title>
</head>
<body>
    <h1>PHP-FPM Demo</h1>
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

```bash
sudo mkdir -p /var/www/phpsite
sudo chown -R apache:apache /var/www/phpsite
sudo chmod -R 755 /var/www/phpsite
sudo find /var/www/phpsite -type f -exec chmod 644 {} \;

echo "127.0.0.1  phpsite.local" | sudo tee -a /etc/hosts

sudo apachectl configtest
sudo systemctl restart php-fpm
sudo systemctl restart httpd
```

Test: `http://phpsite.local/`

---

### Part 6: Python Website with mod_wsgi

`mod_wsgi` bridges Apache and Python web applications. WSGI (Web Server Gateway Interface) is the standard Python interface between web servers and Python frameworks — Django, Flask, and most others implement it.

**Two deployment modes:**
- **Embedded mode:** Python runs inside Apache processes. Simple but less isolated.
- **Daemon mode (recommended):** Python runs in separate processes. Better isolation, graceful restarts without restarting Apache, and different Python environments per application.

```bash
# RHEL/CentOS/Fedora
sudo dnf install httpd python3 python3-mod_wsgi -y
# Debian/Ubuntu:  sudo apt install apache2 libapache2-mod-wsgi-py3 -y

sudo httpd -M | grep wsgi     # Verify the module loaded
```

**Create the application** `/var/www/pysite/app.py`:

```python
#!/usr/bin/env python3
import sys

def application(environ, start_response):
    """A minimal WSGI application."""
    status = '200 OK'
    headers = [('Content-Type', 'text/html; charset=utf-8')]
    start_response(status, headers)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Python WSGI Demo</title></head>
<body>
    <h1>WSGI Application Running</h1>
    <p>Deployed on Apache with mod_wsgi in daemon mode.</p>
    <p>Python Version: {sys.version.split()[0]}</p>
    <p>Server: {environ.get('SERVER_SOFTWARE', 'unknown')}</p>
    <p>Client IP: {environ.get('REMOTE_ADDR', 'unknown')}</p>
</body>
</html>"""
    return [html.encode('utf-8')]
```

**Create the virtual host** `/etc/httpd/conf.d/pysite.conf`:

```apache
<VirtualHost *:80>
    ServerName pysite.local
    DocumentRoot /var/www/pysite
    ServerAdmin admin@pysite.local

    # Daemon mode: Python runs in separate processes, not inside Apache workers
    WSGIDaemonProcess pysite-app user=apache group=apache \
        processes=2 threads=15 python-path=/var/www/pysite

    WSGIScriptAlias / /var/www/pysite/app.py

    <Directory /var/www/pysite>
        WSGIProcessGroup pysite-app
        WSGIApplicationGroup %{GLOBAL}
        Options -Indexes
        AllowOverride None
        Require all granted
    </Directory>

    ErrorLog /var/log/httpd/pysite_error.log
    CustomLog /var/log/httpd/pysite_access.log combined
    LogLevel warn
</VirtualHost>
```

**Set permissions and SELinux context:**

```bash
sudo mkdir -p /var/www/pysite
sudo chown -R apache:apache /var/www/pysite
sudo chmod -R 755 /var/www/pysite
sudo chcon -R -t httpd_sys_content_t /var/www/pysite
sudo setsebool -P httpd_execmem 1          # Needed by mod_wsgi daemon mode

echo "127.0.0.1  pysite.local" | sudo tee -a /etc/hosts
sudo apachectl configtest
sudo systemctl restart httpd
```

Test: `http://pysite.local/`. A **403 Forbidden** is almost always a wrong SELinux context (`chcon`) or wrong ownership (`chown -R apache:apache`).

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
sudo tail -f /var/log/httpd/error_log            # Follow error log in real time
sudo grep " 404 " /var/log/httpd/access_log      # Find 404 errors
sudo grep " 500 " /var/log/httpd/access_log      # Find 500 server errors

# HTTP status code distribution
sudo awk '{print $9}' /var/log/httpd/access_log | sort | uniq -c | sort -rn | head -10
```

**Combined Log Format** — one line, then its fields:

```
192.168.1.10 - alice [25/Jun/2026:09:15:23 +0545] "GET /index.php HTTP/1.1" 200 4823 "-" "Mozilla/5.0"
```

Fields: client IP, identity (usually `-`), auth user, timestamp, request line, status code, response bytes, referrer, user agent.

---

## Lab 5.1.B: Nginx — Static Site, Reverse Proxy, and Load Balancer

### Part 1: Install and Start Nginx

```bash
sudo dnf install nginx -y
sudo systemctl enable --now nginx
sudo systemctl status nginx
nginx -v

sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

Test: `http://localhost` — you should see the Nginx welcome page.

Key commands:

```bash
sudo nginx -t                 # Test configuration syntax
sudo nginx -T                 # Test and dump the full config
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
<head><meta charset="UTF-8"><title>Nginx Static Site</title></head>
<body>
    <h1>Nginx Static Site</h1>
    <p>Served from /var/www/nginx-static. Nginx is running correctly.</p>
</body>
</html>
```

```bash
sudo chown -R nginx:nginx /var/www/nginx-static
sudo chcon -R -t httpd_sys_content_t /var/www/nginx-static
```

Create the server block `/etc/nginx/conf.d/static-site.conf`:

```nginx
server {
    listen 80;
    server_name static.local;

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
echo "127.0.0.1  static.local" | sudo tee -a /etc/hosts
sudo nginx -t
sudo systemctl reload nginx
```

Test: `http://static.local/`

---

### Part 3: Nginx as a Reverse Proxy

A reverse proxy accepts client requests and forwards them to a backend. The client talks only to Nginx; the backend is invisible from outside. This enables TLS termination, centralised logging, access control, and load distribution without changing the application.

Simulate a backend with a simple Python HTTP server:

```bash
# In a separate terminal: a minimal HTTP server on port 5000
python3 -m http.server 5000 --directory /var/www/nginx-static &
```

Create `/etc/nginx/conf.d/reverse-proxy.conf`:

```nginx
server {
    listen 80;
    server_name proxy.local;

    location / {
        proxy_pass http://127.0.0.1:5000;

        # Pass original request context to the backend
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_connect_timeout 10s;
        proxy_read_timeout    30s;
        proxy_send_timeout    30s;

        # HTTP/1.1 keep-alive to the upstream
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }

    access_log /var/log/nginx/proxy.local_access.log;
    error_log  /var/log/nginx/proxy.local_error.log;
}
```

Why these headers matter:

- `X-Real-IP` / `X-Forwarded-For`: your logs and analytics need the real client IP, not Nginx's. Without them, every entry shows `127.0.0.1`.
- `X-Forwarded-Proto`: tells the backend whether the original request was HTTP or HTTPS. This is exactly how the backend learns TLS was terminated at the edge (Section 5.1 §5) — Flask's `request.is_secure`, Django's `SECURE_PROXY_SSL_HEADER`, and most frameworks read it.
- `proxy_http_version 1.1` + `Connection ""`: reuses TCP connections to the backend instead of opening a new one per request.

```bash
echo "127.0.0.1  proxy.local" | sudo tee -a /etc/hosts
sudo nginx -t
sudo systemctl reload nginx
```

Test: `http://proxy.local/` — served by the Python backend through Nginx.

---

### Part 4: Nginx as a Load Balancer

A load balancer distributes requests across multiple backends, preventing any single server from being overwhelmed and providing fault tolerance: if one backend fails, Nginx routes to the healthy ones.

```bash
# Simulate three backends on different ports
python3 -m http.server 5001 --directory /var/www/nginx-static &
python3 -m http.server 5002 --directory /var/www/nginx-static &
python3 -m http.server 5003 --directory /var/www/nginx-static &
```

**Round-robin (default)** `/etc/nginx/conf.d/load-balancer.conf`:

```nginx
upstream app_backends {
    # Round-robin is the default; no directive needed
    server 127.0.0.1:5001 max_fails=2 fail_timeout=10s;
    server 127.0.0.1:5002 max_fails=2 fail_timeout=10s;
    server 127.0.0.1:5003 max_fails=2 fail_timeout=10s;
}

server {
    listen 80;
    server_name lb.local;

    location / {
        proxy_pass http://app_backends;

        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_http_version 1.1;
        proxy_set_header Connection "";

        # If a backend returns 502/503/504, try the next server
        proxy_next_upstream error timeout http_502 http_503 http_504;
    }

    access_log /var/log/nginx/lb.local_access.log;
    error_log  /var/log/nginx/lb.local_error.log;
}
```

**Least connections** — use when request duration varies significantly; round-robin assumes equal request weight:

```nginx
upstream app_backends {
    least_conn;
    server 127.0.0.1:5001 max_fails=2 fail_timeout=10s;
    server 127.0.0.1:5002 max_fails=2 fail_timeout=10s;
    server 127.0.0.1:5003 max_fails=2 fail_timeout=10s;
}
```

**IP hash (sticky sessions)** — routes a given client IP to the same backend. Use only when the app stores session state in process memory rather than a shared store like Redis; if a server goes down, its sessions are lost:

```nginx
upstream app_backends {
    ip_hash;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
    server 127.0.0.1:5003;
}
```

**Passive health checks.** Open-source Nginx observes real traffic: when it sees a backend fail, it stops sending to it and spreads requests across the healthy ones. `max_fails=2 fail_timeout=10s` means: if a backend fails twice within 10 seconds, mark it unavailable for 10 seconds, then send one probe; if that succeeds, it returns to rotation.

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

## Lab 5.1.C: Apache Tomcat — Java Application Server

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

## SELinux Reference for Web Servers

SELinux is the most common cause of web-server failures on RHEL/CentOS. The fix is almost always one of three things.

**Wrong file context (most common):**

```bash
ls -Z /var/www/mysite/                                  # Check current context
sudo chcon -R -t httpd_sys_content_t /var/www/mysite    # Fix immediately
sudo restorecon -Rv /var/www/mysite                     # Fix from policy (persistent)
```

**Missing boolean (reverse proxy, DB connections, mod_wsgi):**

```bash
getsebool -a | grep httpd
sudo setsebool -P httpd_can_network_connect 1       # Allow proxy connections to backends
sudo setsebool -P httpd_can_network_connect_db 1    # Allow direct DB connections
sudo setsebool -P httpd_execmem 1                   # Allow mod_wsgi daemon mode
```

**Non-standard port:**

```bash
sudo semanage port -a -t http_port_t -p tcp 8081    # Allow Apache on a custom port
sudo semanage port -l | grep http_port              # Verify
```

**Reading SELinux denial logs:**

```bash
sudo ausearch -m avc -ts recent | grep httpd
journalctl -t setroubleshoot                        # Human-readable explanations
```

---

## Stop and Remove Services (Before Switching Labs)

Switching between Apache and Nginx labs? Stop the unused service to free port 80:

```bash
sudo systemctl disable httpd --now && sudo dnf remove httpd -y     # Apache → Nginx
sudo systemctl disable nginx --now && sudo dnf remove nginx -y     # Nginx → Apache
sudo systemctl disable tomcat --now                               # Tomcat when unneeded
```

---

# Section 5.2: Delivery-Friendly Applications and the Twelve-Factor Model

---

# Theory

---

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
