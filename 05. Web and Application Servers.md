# Module 5: Web and Application Servers

## Section 5.1: Web and Application Servers

---

# Theory

---

## 1. Web Servers vs. Application Servers

A **web server** handles HTTP and HTTPS requests. Its primary job is serving static content (HTML, CSS, JavaScript, images) and optionally forwarding dynamic requests to backend processes. Examples: Nginx, Apache HTTP Server.

An **application server** executes application code to generate responses. It handles business logic, database queries, and session management. Examples: Apache Tomcat (Java), Gunicorn (Python), Node.js.

In practice these roles overlap and are commonly combined. A typical architecture is: **Nginx as the front layer** receiving all traffic, serving static files directly, and proxying dynamic requests to an application server running behind it.

```
Client → Nginx (reverse proxy / SSL termination / static files)
               ↓ proxy_pass
         Application Server (Tomcat / Gunicorn / Node)
               ↓
         Database (PostgreSQL / MySQL / MongoDB)
```

This separation is important in DevOps because it affects how you configure deployments, scale components independently, and troubleshoot failures.

---

## 2. Nginx

Nginx was released in 2004 to solve the C10K problem — the challenge of handling 10,000 simultaneous connections that caused thread-based servers to exhaust memory. Its architecture is fundamentally different from Apache.

### Architecture

Nginx uses an **event-driven, asynchronous, non-blocking** model:

- A **master process** reads configuration and manages worker processes.
- **Worker processes** (one per CPU core by default) each run a single-threaded event loop.
- A single worker can handle thousands of connections simultaneously. When waiting for a network response or disk read, it does not block — it registers a callback and handles other connections in the meantime.
- No new thread or process is created per connection, so memory usage stays low and predictable under high load.

Compare this to Apache's `mpm_prefork`: one process per connection. Under 5,000 simultaneous connections, that is 5,000 processes — each consuming RAM and requiring context switches.

### Primary Use Cases

- High-concurrency static file serving
- Reverse proxy in front of application servers
- Load balancing across multiple backends
- SSL/TLS termination
- HTTP caching

### Configuration Locations

- **RHEL / CentOS / Fedora:** `/etc/nginx/nginx.conf`, site configs in `/etc/nginx/conf.d/`
- **Debian / Ubuntu:** `/etc/nginx/nginx.conf`, site configs in `/etc/nginx/sites-available/` (symlinked to `/etc/nginx/sites-enabled/`)

### Market Position

Nginx has cemented its position as the world's most popular web server and reverse proxy, powering over 34% of all active websites as of early 2026.

---

## 3. Apache HTTP Server

Apache HTTP Server (package name `httpd` on RHEL) has been the most deployed web server historically. It is maintained by the Apache Software Foundation and is the core component of the LAMP stack (Linux, Apache, MySQL, PHP).

### Architecture: Multi-Processing Modules (MPMs)

Apache uses interchangeable MPMs. Only one is active at a time.

| MPM | Model | Best For |
|---|---|---|
| `mpm_prefork` | One process per connection, no threads | Legacy non-thread-safe modules (old `mod_php`) |
| `mpm_worker` | Multiple processes, each with multiple threads | Better memory efficiency than prefork |
| `mpm_event` | Worker model with async keep-alive handling | Default on modern systems; best performance |

`mpm_event` is the default on Apache 2.4+ installations. It separates keep-alive connection management from request processing: a dedicated listener thread monitors idle keep-alive connections and only hands them to a worker thread when a new request arrives.

### Key Features

- **Modular:** enable/disable capabilities with loadable modules (`mod_ssl`, `mod_rewrite`, `mod_proxy`, `mod_wsgi`, `mod_security`)
- **`.htaccess`:** per-directory configuration without a server restart. Useful for shared hosting, but a performance cost in production because Apache checks for `.htaccess` files on every request
- **Virtual hosting:** name-based and IP-based, host multiple sites on one server
- **`mod_proxy`:** built-in reverse proxying and load balancing

### Configuration Locations

- **RHEL / CentOS / Fedora:** `/etc/httpd/conf/httpd.conf`, virtual host configs in `/etc/httpd/conf.d/`
- **Debian / Ubuntu:** `/etc/apache2/apache2.conf`, site configs in `/etc/apache2/sites-available/`

### Market Share

According to W3Techs (April 2026): Nginx first at 32.7%, Cloudflare Server second at 27.7%, Apache third at 23.7%.

---

## 4. Apache Tomcat

Apache Tomcat is a Java application server that implements the Jakarta Servlet and JavaServer Pages (JSP) specifications. It runs Java web applications packaged as `.war` (Web Application Archive) files.

Tomcat is not a general web server. It is not a replacement for Nginx or Apache HTTP Server. In production, Tomcat typically sits behind Nginx, which handles SSL termination and static files while Tomcat handles Java application requests.

### Version and JDK Compatibility

This is the most common source of Tomcat installation failures. The versions must match:

| Tomcat Version | Required Java | Jakarta EE Spec |
|---|---|---|
| 9.0.x | Java 8 or later | Servlet 4.0 / JSP 2.3 |
| 10.1.x | Java 11 or later | Servlet 5.0 / JSP 3.1 |
| 11.0.x | Java 17 or later | Servlet 6.1 / JSP 4.0 |

Tomcat 10.1 was designed to run on Java SE 11 or later. Tomcat 11.0 was designed to run on Java SE 17 or later.

Always verify your Java version before installing Tomcat. If the JDK is too old, Tomcat will fail to start with a cryptic JVM error rather than a clear message about incompatibility.

### Key Tomcat Concepts

- **`CATALINA_HOME`:** The Tomcat installation directory (e.g., `/opt/tomcat`)
- **`webapps/`:** Drop `.war` files here; Tomcat auto-deploys them on startup
- **`conf/server.xml`:** Main configuration: ports, connectors, virtual hosts
- **`conf/tomcat-users.xml`:** User credentials for the Manager web interface
- **`logs/catalina.out`:** Main log file; always check this first when troubleshooting
- **Manager App:** Web-based GUI at `http://server:8080/manager/html` for deploying and managing applications

### Security Note

Run Tomcat as a non-root user for security. Create a dedicated `tomcat` system account with no login shell. Never run Tomcat as root — a vulnerability in a Java application could give an attacker root access to the entire server.

---

## 5. Web Server Comparison

| Feature | Nginx | Apache HTTP Server | Tomcat |
|---|---|---|---|
| Type | Web server / reverse proxy | Web server / proxy | Java application server |
| Architecture | Event-driven, async, non-blocking | Process/thread MPM | JVM-based, multi-threaded |
| Static files | Excellent | Good | Not designed for this |
| Dynamic content | Via FastCGI/proxy | Via modules or proxy | Java Servlets / JSP natively |
| Per-directory config | No `.htaccess` equivalent | `.htaccess` supported | web.xml per app |
| SSL/TLS | Built-in | mod_ssl | Via connector (but use Nginx for this) |
| Configuration style | `server {}` and `location {}` blocks | Directives and `<VirtualHost>` blocks | XML (`server.xml`, `web.xml`) |
| Best for | Reverse proxy, CDN-style, microservices frontend | Legacy apps, `.htaccess`-dependent apps | Java EE applications |
| DevOps role | Front of every architecture | Common in LAMP stacks | Java application hosting |

In a DevOps pipeline you will typically use all three: **Nginx** as the public-facing layer, **Apache** for PHP-based applications, and **Tomcat** for Java-based applications. The Jenkins CI/CD labs in Module 3 use Tomcat for Java WAR deployments.

---

# Laboratory Exercises

---

## Lab 2.3.A: Apache HTTP Server — Installation, Virtual Hosts, and HTTPS

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

Create the homepage:

```bash
sudo vim /var/www/html/index.html
```

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

Create the site directory:

```bash
sudo mkdir -p /var/www/myapp.local
sudo chown -R apache:apache /var/www/myapp.local
sudo chmod -R 755 /var/www/myapp.local
```

```bash
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

Create the virtual host configuration:

```bash
sudo vim /etc/httpd/conf.d/myapp.local.conf
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

`Options -Indexes` prevents Apache from listing directory contents when no index file exists. Always set this in production. Exposing directory listings reveals your file structure to anyone on the internet.

```bash
sudo apachectl configtest
sudo httpd -S                    # Show all configured virtual hosts
sudo systemctl restart httpd
```

Add local DNS entry for testing:

```bash
echo "127.0.0.1  myapp.local  www.myapp.local" | sudo tee -a /etc/hosts
```

Test: `http://myapp.local/`

To host multiple virtual hosts, repeat this pattern. Each site gets its own directory and its own `.conf` file in `/etc/httpd/conf.d/`.

---

### Part 4: HTTPS with a Self-Signed Certificate

HTTPS encrypts traffic between the client and server using TLS. Certificate options:

- **Let's Encrypt:** Free, automated, 90-day certificates via `certbot`. Requires a publicly routable domain. This is the standard for production.
- **Commercial CA:** Paid certificates (DigiCert, Sectigo). Used when extended validation is required.
- **Self-signed:** Generated locally, not trusted by browsers. Use only in lab or internal environments.

**Install mod_ssl:**

```bash
sudo dnf install mod_ssl openssl -y
```

**Generate a self-signed certificate:**

```bash
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/pki/tls/private/myapp.key \
    -out /etc/pki/tls/certs/myapp.crt \
    -subj "/C=NP/ST=Bagmati/L=Kathmandu/O=DevOps Lab/CN=myapp.local"
```

Flags explained:
- `-x509`: produce a self-signed certificate (not a signing request)
- `-nodes`: no passphrase on the key (server starts without prompting)
- `-days 365`: valid for one year
- `-newkey rsa:2048`: generate a new 2048-bit RSA key pair
- `-subj`: certificate subject fields without an interactive prompt

**Create the HTTPS virtual host:**

```bash
sudo vim /etc/httpd/conf.d/myapp.local-ssl.conf
```

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

Test: `https://myapp.local/`. The browser shows a certificate warning because the cert is self-signed. Proceed past it. Verify the padlock and connection details show TLS is active.

**Let's Encrypt for production (real domain required):**

```bash
sudo dnf install certbot python3-certbot-apache -y
sudo certbot --apache -d example.com -d www.example.com
sudo certbot renew --dry-run                              # Test auto-renewal
```

---

### Part 5: PHP Website with PHP-FPM

Apache serves PHP through two mechanisms. **PHP-FPM** (FastCGI Process Manager) is the current standard. PHP runs as a separate process pool; Apache proxies PHP requests to it. This is more efficient, more secure, and supports multiple PHP versions per server.

**Install PHP and PHP-FPM:**

```bash
sudo dnf install php php-fpm php-mysqlnd php-json php-xml php-mbstring -y
sudo systemctl start php-fpm
sudo systemctl enable php-fpm
sudo systemctl status php-fpm
php -v
```

**Create virtual host configuration:**

```bash
sudo vim /etc/httpd/conf.d/phpsite.conf
```

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

**Create the PHP application:**

```bash
sudo mkdir -p /var/www/phpsite
sudo vim /var/www/phpsite/index.php
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
    <title>PHP Demo</title>
    <style>
        body { font-family: sans-serif; max-width: 600px; margin: 3rem auto; padding: 20px; }
        .box { background: #f4f4f4; padding: 15px; margin: 12px 0; border-radius: 5px; }
        input, button { padding: 8px; margin: 4px 0; }
        button { background: #0066cc; color: white; border: none; cursor: pointer; border-radius: 4px; }
    </style>
</head>
<body>
    <h1>PHP-FPM Demo</h1>

    <div class="box">
        <strong>Server:</strong> <?= htmlspecialchars($_SERVER['SERVER_NAME']) ?><br>
        <strong>PHP Version:</strong> <?= PHP_VERSION ?><br>
        <strong>Time:</strong> <?= date('Y-m-d H:i:s') ?>
    </div>

    <div class="box">
        <strong>Session visits:</strong> <?= $_SESSION['visits'] ?>
    </div>

    <div class="box">
        <form method="POST">
            <input type="text" name="name" placeholder="Enter your name" required>
            <button type="submit">Submit</button>
        </form>
        <?php if ($name): ?>
            <p style="color: green; margin-top: 10px;">Hello, <strong><?= $name ?></strong>!</p>
        <?php endif; ?>
    </div>
</body>
</html>
```

Note: `htmlspecialchars()` converts special characters to HTML entities, preventing cross-site scripting (XSS). Always escape output from user input.

```bash
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

`mod_wsgi` bridges Apache and Python web applications. WSGI (Web Server Gateway Interface) is the standard Python interface between web servers and Python frameworks — Django, Flask, and most Python web frameworks implement it.

**Two deployment modes:**
- **Embedded mode:** Python runs inside Apache processes. Simple but less isolated.
- **Daemon mode (recommended):** Python runs in separate processes. Better isolation, allows graceful restarts without restarting Apache, and permits different Python environments per application.

**Install mod_wsgi:**

```bash
# RHEL/CentOS/Fedora
sudo dnf install httpd python3 python3-mod_wsgi -y

# Debian/Ubuntu
# sudo apt install apache2 libapache2-mod-wsgi-py3 -y

# Verify the module loaded
sudo httpd -M | grep wsgi
```

**Create the application:**

```bash
sudo mkdir -p /var/www/pysite
sudo vim /var/www/pysite/app.py
```

```python
#!/usr/bin/env python3
import sys

sys.path.insert(0, '/var/www/pysite')

def application(environ, start_response):
    """A minimal WSGI application."""
    status = '200 OK'
    headers = [('Content-Type', 'text/html; charset=utf-8')]
    start_response(status, headers)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Python WSGI Demo</title>
    <style>
        body {{ font-family: sans-serif; max-width: 700px; margin: 3rem auto; padding: 20px; }}
        .card {{ background: #f8f9fa; padding: 20px; border-radius: 8px;
                 border-left: 4px solid #667eea; margin: 15px 0; }}
        strong {{ color: #444; }}
        code {{ font-family: monospace; color: #555; background: #eee;
                padding: 2px 6px; border-radius: 3px; }}
    </style>
</head>
<body>
    <h1>WSGI Application Running</h1>
    <p>Deployed on Apache with mod_wsgi in daemon mode.</p>
    <div class="card">
        <p><strong>Python Version:</strong> <code>{sys.version.split()[0]}</code></p>
        <p><strong>Server:</strong> <code>{environ.get('SERVER_SOFTWARE', 'unknown')}</code></p>
        <p><strong>Method:</strong> <code>{environ.get('REQUEST_METHOD', 'GET')}</code></p>
        <p><strong>Path:</strong> <code>{environ.get('PATH_INFO', '/')}</code></p>
        <p><strong>Client IP:</strong> <code>{environ.get('REMOTE_ADDR', 'unknown')}</code></p>
    </div>
</body>
</html>"""
    return [html.encode('utf-8')]
```

**Create the virtual host:**

```bash
sudo vim /etc/httpd/conf.d/pysite.conf
```

```apache
<VirtualHost *:80>
    ServerName pysite.local
    DocumentRoot /var/www/pysite
    ServerAdmin admin@pysite.local

    # Daemon mode: Python runs in separate processes, not inside Apache workers
    WSGIDaemonProcess pysite-app \
        user=apache \
        group=apache \
        processes=2 \
        threads=15 \
        python-path=/var/www/pysite

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
sudo chown -R apache:apache /var/www/pysite
sudo chmod -R 755 /var/www/pysite

# SELinux: set the correct type so Apache can read the files
sudo chcon -R -t httpd_sys_content_t /var/www/pysite

# Allow Apache to execute memory (needed by mod_wsgi daemon mode)
sudo setsebool -P httpd_execmem 1

echo "127.0.0.1  pysite.local" | sudo tee -a /etc/hosts

sudo apachectl configtest
sudo systemctl restart httpd
```

Test: `http://pysite.local/`

If you see a 403 Forbidden error, the most likely causes are: wrong SELinux context (fix with `chcon`) or wrong file ownership (fix with `chown -R apache:apache`).

---

### Part 7: Apache Log Management

Apache writes two log files per virtual host. Knowing how to read them is essential when troubleshooting failed deployments or application errors.

**Log file locations (RHEL/CentOS):**

| File | Purpose |
|---|---|
| `/var/log/httpd/access_log` | All HTTP requests to the default virtual host |
| `/var/log/httpd/error_log` | Apache errors, module messages, application stderr |
| Virtual host logs | Defined per VirtualHost in `.conf` files |

**Reading logs:**

```bash
sudo tail -f /var/log/httpd/access_log           # Follow access log in real time
sudo tail -f /var/log/httpd/error_log            # Follow error log in real time
sudo grep " 404 " /var/log/httpd/access_log      # Find 404 errors
sudo grep " 500 " /var/log/httpd/access_log      # Find 500 server errors
sudo grep "PHP Fatal" /var/log/httpd/error_log   # Find PHP fatal errors

# HTTP status code distribution
sudo awk '{print $9}' /var/log/httpd/access_log \
  | sort | uniq -c | sort -rn | head -10
```

**Combined Log Format (what each field means):**

```
192.168.1.10 - alice [25/Jun/2026:09:15:23 +0545] "GET /index.php HTTP/1.1" 200 4823 "-" "Mozilla/5.0"
```

Fields: client IP, identity (usually `-`), auth user, timestamp, request line, status code, response bytes, referrer, user agent.

---

## Lab 2.3.B: Nginx — Static Site, Reverse Proxy, and Load Balancer

### Part 1: Install and Start Nginx

```bash
sudo dnf install nginx -y
sudo systemctl start nginx
sudo systemctl enable nginx
sudo systemctl status nginx
nginx -v
```

Open the firewall:

```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

Test: `http://localhost` — you should see the Nginx welcome page.

Key Nginx commands:

```bash
sudo nginx -t              # Test configuration syntax
sudo nginx -T              # Test and dump the full config
sudo systemctl reload nginx   # Apply config changes without dropping connections
sudo systemctl restart nginx  # Full restart (drops active connections briefly)
```

Always use `nginx -t` before reloading or restarting. A config error will prevent Nginx from starting, taking the server offline.

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
    <title>Nginx Static Site</title>
    <style>
        body { font-family: sans-serif; max-width: 800px; margin: 3rem auto; padding: 20px; }
        .badge { background: #e8f5e9; color: #2e7d32; padding: 10px 20px;
                 border-radius: 4px; display: inline-block; margin: 10px 0; }
    </style>
</head>
<body>
    <h1>Nginx Static Site</h1>
    <div class="badge">Served from /var/www/nginx-static</div>
    <p>Nginx is running correctly.</p>
</body>
</html>
```

Set the SELinux context and ownership:

```bash
sudo chown -R nginx:nginx /var/www/nginx-static
sudo chcon -R -t httpd_sys_content_t /var/www/nginx-static
```

Create the Nginx server block:

```bash
sudo vim /etc/nginx/conf.d/static-site.conf
```

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

A reverse proxy accepts client requests and forwards them to a backend server. The client communicates only with Nginx; the backend is invisible from outside the network. This enables SSL termination, centralized logging, access control, and load distribution without changing the application.

For this lab, simulate a backend by running a simple Python HTTP server:

```bash
# In a separate terminal: start a minimal HTTP server on port 5000
python3 -m http.server 5000 --directory /var/www/nginx-static &
```

Create the reverse proxy configuration:

```bash
sudo vim /etc/nginx/conf.d/reverse-proxy.conf
```

```nginx
server {
    listen 80;
    server_name proxy.local;

    location / {
        # Forward all requests to the backend
        proxy_pass http://127.0.0.1:5000;

        # Pass the original request headers to the backend
        # Without these, the backend sees Nginx's IP, not the client's
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeout settings
        proxy_connect_timeout 10s;
        proxy_read_timeout    30s;
        proxy_send_timeout    30s;

        # Use HTTP/1.1 (required for keep-alive with upstream)
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }

    access_log /var/log/nginx/proxy.local_access.log;
    error_log  /var/log/nginx/proxy.local_error.log;
}
```

Why these headers matter:

- `X-Real-IP` and `X-Forwarded-For`: your application logs and analytics need the real client IP, not Nginx's IP. Without these headers, every log entry shows `127.0.0.1`.
- `X-Forwarded-Proto`: tells the backend whether the original client request was HTTP or HTTPS. Flask's `request.is_secure`, Django's `SECURE_PROXY_SSL_HEADER`, and most frameworks use this to make HTTPS-aware decisions.
- `proxy_http_version 1.1` + `Connection ""`: enables HTTP keep-alive to the backend, reusing TCP connections instead of opening a new one for every request.

```bash
echo "127.0.0.1  proxy.local" | sudo tee -a /etc/hosts
sudo nginx -t
sudo systemctl reload nginx
```

Test: `http://proxy.local/` — the request should be served by the Python backend through Nginx.

---

### Part 4: Nginx as a Load Balancer

A load balancer distributes incoming requests across multiple backend servers. This prevents any single server from being overwhelmed and provides fault tolerance: if one backend fails, Nginx routes traffic to the remaining healthy servers.

For this lab, simulate three backends on different ports:

```bash
# Run three backends in the background
python3 -m http.server 5001 --directory /var/www/nginx-static &
python3 -m http.server 5002 --directory /var/www/nginx-static &
python3 -m http.server 5003 --directory /var/www/nginx-static &
```

**Round-Robin Load Balancer:**

```bash
sudo vim /etc/nginx/conf.d/load-balancer.conf
```

```nginx
# Define the upstream group of backend servers
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

        # If backend returns a 502/503/504, try the next server
        proxy_next_upstream error timeout http_502 http_503 http_504;
    }

    access_log /var/log/nginx/lb.local_access.log;
    error_log  /var/log/nginx/lb.local_error.log;
}
```

**Least Connections variant:**

```nginx
upstream app_backends {
    least_conn;
    server 127.0.0.1:5001 max_fails=2 fail_timeout=10s;
    server 127.0.0.1:5002 max_fails=2 fail_timeout=10s;
    server 127.0.0.1:5003 max_fails=2 fail_timeout=10s;
}
```

Use least connections when request duration varies significantly. Round-robin assumes equal request weight; if some requests take 10ms and others take 2 seconds, round-robin overloads whichever backend receives the slow requests.

**IP Hash (sticky sessions) variant:**

```nginx
upstream app_backends {
    ip_hash;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
    server 127.0.0.1:5003;
}
```

IP hash routes a given client IP to the same backend consistently. Use this only when the application stores session state in process memory (rather than a shared store like Redis). The limitation: if a server goes down, all sessions mapped to it are lost.

**Passive health checks explained:**

Nginx open source uses passive health checks, which rely on observing how the server behaves while handling real connections and traffic. When Nginx discovers a server is unhealthy it immediately forwards the request to a different server, stops sending requests to the unhealthy server, and distributes future requests among the remaining healthy servers.

`max_fails=2 fail_timeout=10s` means: if a backend fails 2 times within 10 seconds, mark it unavailable for 10 seconds. After that, Nginx sends one probe request; if it succeeds, the backend returns to rotation.

```bash
echo "127.0.0.1  lb.local" | sudo tee -a /etc/hosts
sudo nginx -t
sudo systemctl reload nginx
```

Test and observe round-robin distribution:

```bash
# Send 6 requests and observe which backend responds
for i in {1..6}; do curl -s http://lb.local/ | grep -o "port [0-9]*" || echo "request $i"; done
```

To verify a backend is removed when it fails:

```bash
# Kill backend on port 5002
kill $(lsof -t -i:5002)

# Test again — requests should only go to 5001 and 5003
curl -s http://lb.local/
```

---

### Part 5: Nginx Log Management

```bash
# Nginx log locations
sudo tail -f /var/log/nginx/access.log    # Default access log
sudo tail -f /var/log/nginx/error.log     # Default error log

# Filter for errors
sudo grep " 502 " /var/log/nginx/access.log     # Bad gateway (upstream down)
sudo grep " 504 " /var/log/nginx/access.log     # Gateway timeout (upstream too slow)
sudo grep "connect() failed" /var/log/nginx/error.log   # Backend connection failures

# Custom log format showing upstream address (useful for load balancer debugging)
# Add to nginx.conf http block:
# log_format upstream '$remote_addr - $host [$time_local] '
#                     '"$request" $status $body_bytes_sent '
#                     '$upstream_addr $upstream_status';
```

---

### Part 6: Clean Up Nginx Test Processes

```bash
# Stop the Python backend processes
kill $(lsof -t -i:5000) $(lsof -t -i:5001) $(lsof -t -i:5002) $(lsof -t -i:5003) 2>/dev/null || true
```

---

## Lab 2.3.C: Apache Tomcat — Java Application Server

Apache Tomcat is the standard Java application server used in the Jenkins WAR deployment labs in Module 3. This lab installs Tomcat correctly, configures it as a systemd service, deploys a test WAR file, and prepares it for the Jenkins pipeline.

### Part 1: Install Java (OpenJDK)

Tomcat 10.1 was designed to run on Java SE 11 or later. We use Tomcat 10.1.x in this course, so OpenJDK 11 or 17 is required. OpenJDK 17 is the current LTS release and is recommended.

```bash
# Install OpenJDK 17
sudo dnf install java-17-openjdk java-17-openjdk-devel -y

# Verify
java -version
javac -version

# Note the JAVA_HOME path (you will need this for the systemd service)
dirname $(dirname $(readlink -f $(which java)))
```

Expected output:
```
openjdk version "17.0.x" ...
```

---

### Part 2: Create a Dedicated Tomcat User

Run Tomcat as a non-root user for security. A dedicated system account with no login shell limits the blast radius if a Java application is compromised.

```bash
# Create a system user with no login shell and a home directory at /opt/tomcat
sudo useradd -r -m -U -d /opt/tomcat -s /bin/false tomcat

# Verify the user was created
id tomcat
```

---

### Part 3: Download and Install Tomcat

Check the current stable version at `tomcat.apache.org` before running these commands. The version number will change over time.

```bash
# Set the version (update this to the current stable release)
TOMCAT_VERSION=10.1.44

# Download from the official Apache distribution server
wget https://dlcdn.apache.org/tomcat/tomcat-10/v${TOMCAT_VERSION}/bin/apache-tomcat-${TOMCAT_VERSION}.tar.gz

# Verify the download
ls -lh apache-tomcat-${TOMCAT_VERSION}.tar.gz

# Extract into /opt/tomcat (strip the top-level version directory)
sudo mkdir -p /opt/tomcat
sudo tar -xzf apache-tomcat-${TOMCAT_VERSION}.tar.gz \
    -C /opt/tomcat \
    --strip-components=1

# Verify the directory structure
ls /opt/tomcat/
```

You should see: `bin/  conf/  lib/  logs/  temp/  webapps/  work/`

---

### Part 4: Set Permissions

```bash
# Give the tomcat user ownership of the entire installation
sudo chown -R tomcat:tomcat /opt/tomcat

# Make shell scripts executable
sudo chmod +x /opt/tomcat/bin/*.sh

# Verify
ls -l /opt/tomcat/bin/startup.sh
ls -ld /opt/tomcat/webapps/
```

---

### Part 5: Create a systemd Service Unit

Running Tomcat as a systemd service means it starts automatically at boot, restarts on failure, and integrates with `systemctl` and `journalctl`.

```bash
sudo vim /etc/systemd/system/tomcat.service
```

```ini
[Unit]
Description=Apache Tomcat Web Application Container
After=network.target

[Service]
Type=forking
User=tomcat
Group=tomcat

# Set JAVA_HOME to the installed JDK path
# Adjust this path if your JDK is installed elsewhere
Environment="JAVA_HOME=/usr/lib/jvm/java-17-openjdk"
Environment="CATALINA_PID=/opt/tomcat/temp/tomcat.pid"
Environment="CATALINA_HOME=/opt/tomcat"
Environment="CATALINA_BASE=/opt/tomcat"

# JVM tuning: 512MB min heap, 1GB max heap
Environment="CATALINA_OPTS=-Xms512M -Xmx1024M -server -XX:+UseParallelGC"
Environment="JAVA_OPTS=-Djava.awt.headless=true -Djava.security.egd=file:/dev/./urandom"

ExecStart=/opt/tomcat/bin/startup.sh
ExecStop=/opt/tomcat/bin/shutdown.sh

Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Find the exact JAVA_HOME path:

```bash
# Get the exact JDK path (use this in the service file above)
dirname $(dirname $(readlink -f $(which java)))
```

Apply and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl start tomcat
sudo systemctl enable tomcat
sudo systemctl status tomcat
```

Watch the startup log to confirm Tomcat started successfully:

```bash
sudo tail -f /opt/tomcat/logs/catalina.out
```

Look for: `Server startup in [N] milliseconds`

If Tomcat fails to start, check:
1. Is JAVA_HOME pointing to the correct path? (`ls $JAVA_HOME/bin/java`)
2. Is the `tomcat` user the owner of `/opt/tomcat`? (`ls -la /opt/tomcat/`)
3. Is port 8080 already in use? (`ss -tlnp | grep 8080`)

---

### Part 6: Open Firewall for Tomcat

```bash
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload
```

Test: `http://server-ip:8080` — you should see the Tomcat welcome page.

---

### Part 7: Configure the Tomcat Manager Application

The Manager app provides a web UI and API for deploying, undeploying, and reloading WAR files. Jenkins uses the Manager API in the CI/CD pipeline (Module 3).

```bash
sudo vim /opt/tomcat/conf/tomcat-users.xml
```

Add before `</tomcat-users>`:

```xml
<role rolename="manager-gui"/>
<role rolename="manager-script"/>
<role rolename="admin-gui"/>
<user username="devops"
      password="DevOps@2026!"
      roles="manager-gui,manager-script,admin-gui"/>
```

`manager-gui` allows access to the Manager web interface. `manager-script` allows the Manager HTTP API used by Jenkins and Maven deploy plugins.

By default, the Manager app restricts access to localhost only. To allow access from your network (needed for remote Jenkins deployments):

```bash
sudo vim /opt/tomcat/webapps/manager/META-INF/context.xml
```

Find the `Valve` element that restricts to `127\.\d+\.\d+\.\d+|::1|0:0:0:0:0:0:0:1` and either comment it out (for lab use) or replace the IP pattern with your network range.

For lab use only (comment out the restriction):

```xml
<!--
<Valve className="org.apache.catalina.valves.RemoteAddrValve"
       allow="127\.\d+\.\d+\.\d+|::1|0:0:0:0:0:0:0:1" />
-->
```

Restart Tomcat to apply:

```bash
sudo systemctl restart tomcat
```

Test the Manager: `http://server-ip:8080/manager/html`
Log in with the `devops` credentials you configured.

---

### Part 8: Deploy a WAR File

A WAR (Web Application Archive) is a ZIP-format package containing a complete Java web application: servlets, JSP pages, static files, and configuration.

**Method 1: Copy to webapps/ (simplest for labs):**

```bash
# Download a simple sample WAR for testing
wget https://tomcat.apache.org/tomcat-10.1-doc/appdev/sample/sample.war -O /tmp/sample.war

# Deploy by copying to webapps/
sudo cp /tmp/sample.war /opt/tomcat/webapps/
sudo chown tomcat:tomcat /opt/tomcat/webapps/sample.war

# Tomcat auto-deploys; watch the log
sudo tail -f /opt/tomcat/logs/catalina.out
```

Tomcat unpacks and deploys the WAR automatically. Test: `http://server-ip:8080/sample/`

**Method 2: Manager API (how Jenkins deploys):**

```bash
curl -u devops:DevOps@2026! \
     -T /tmp/sample.war \
     "http://localhost:8080/manager/text/deploy?path=/myapp&update=true"
```

A successful response: `OK - Deployed application at context path [/myapp]`

Test: `http://server-ip:8080/myapp/`

This curl command is exactly how the Jenkins Maven deploy plugin and other CI tools interact with Tomcat. Understanding it now makes the Jenkins lab in Module 3 much clearer.

**List deployed applications:**

```bash
curl -u devops:DevOps@2026! http://localhost:8080/manager/text/list
```

**Undeploy an application:**

```bash
curl -u devops:DevOps@2026! \
     "http://localhost:8080/manager/text/undeploy?path=/myapp"
```

---

### Part 9: Verify the Complete Setup

```bash
# Tomcat service running
systemctl status tomcat

# Tomcat process
ps aux | grep tomcat

# Port 8080 listening
ss -tlnp | grep 8080

# Log file (no errors should appear)
sudo tail -20 /opt/tomcat/logs/catalina.out

# Deployed applications
ls /opt/tomcat/webapps/
```

---

### Part 10: Nginx as Reverse Proxy in Front of Tomcat (Production Pattern)

In production, Tomcat is never exposed directly on port 8080. Nginx sits in front, handles SSL termination, and proxies requests to Tomcat on port 8080. This is the standard architecture for Java applications, and it is the pattern the Jenkins labs build toward.

```bash
sudo vim /etc/nginx/conf.d/tomcat-proxy.conf
```

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

Test: `http://java.local/sample/` — the Tomcat application is now accessible through Nginx on port 80.

---

## SELinux Reference for Web Servers

SELinux is the most common cause of web server failures on RHEL/CentOS. The fix is almost always one of three things.

**Wrong file context (most common):**

```bash
# Files you create may not have the correct SELinux label
ls -Z /var/www/mysite/                              # Check current context
sudo chcon -R -t httpd_sys_content_t /var/www/mysite    # Fix immediately
sudo restorecon -Rv /var/www/mysite                 # Fix using policy (persistent)
```

**Missing boolean (for reverse proxy, network connections):**

```bash
getsebool -a | grep httpd                           # List all httpd booleans
sudo setsebool -P httpd_can_network_connect 1       # Allow proxy connections to backends
sudo setsebool -P httpd_can_network_connect_db 1    # Allow direct DB connections
sudo setsebool -P httpd_execmem 1                   # Allow mod_wsgi daemon mode
```

**Non-standard port:**

```bash
sudo semanage port -a -t http_port_t -p tcp 8081   # Allow Apache on custom port
sudo semanage port -a -t ssh_port_t -p tcp 2222    # Allow SSH on custom port
sudo semanage port -l | grep http_port             # Verify
```

**Reading SELinux denial logs:**

```bash
sudo ausearch -m avc -ts recent | grep httpd       # Recent denials for Apache
sudo cat /var/log/audit/audit.log | grep denied | grep httpd
journalctl -t setroubleshoot                       # Human-readable explanations
```

---

## Stop and Remove Services (Before Switching Labs)

If you are switching from Apache to a fresh Nginx lab (or vice versa), stop the unused service to free port 80:

```bash
# Stop and disable Apache when switching to Nginx
sudo systemctl disable httpd --now
sudo dnf remove httpd -y

# Stop and disable Nginx when switching to Apache
sudo systemctl disable nginx --now
sudo dnf remove nginx -y

# Stop Tomcat when it is not needed
sudo systemctl disable tomcat --now
```

---

*End of Module 2, Section 2.3: Web and Application Servers*

*Next: Section 2.4 — Web Application Development Basics*
