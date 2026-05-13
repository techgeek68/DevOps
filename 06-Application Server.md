# Application Servers & Apache Tomcat

---

## What is an Application Server?

An application server is a software platform that provides a runtime environment for dynamic application code such as Java Servlets, JSP, WebSocket endpoints, and REST APIs. It handles:

- Business logic execution (transactions, security integration)
- Resource management (thread pools, connection pools, clustering hooks)
- Standard APIs (Servlet, JSP, WebSocket, Expression Language; in full Jakarta EE servers: JPA, JMS, CDI, JTA)
- Deployment model (WAR, EAR, exploded or packaged)

Examples:
- Lightweight / Servlet containers: Apache Tomcat, Jetty, Undertow
- Full Jakarta EE / Enterprise: WildFly, Payara, WebLogic, WebSphere

---

## Web Server vs. Application Server

| Feature | Web Server (HTTPD, Nginx) | Application Server (Tomcat, WildFly) |
|---------|--------------------------|--------------------------------------|
| Primary Role | Static content, reverse proxy, TLS termination | Dynamic request execution (Servlets/JSP), APIs |
| Execution Model | File streaming | Managed components (Servlet lifecycle) |
| Protocols | HTTP/HTTPS (+ optional FastCGI, gRPC proxy) | HTTP/HTTPS + Jakarta EE API implementation |
| Caching | Strong static cache, edge friendly | Caches objects in heap (depends on app design) |
| Scaling | Horizontal (stateless) | Horizontal + session handling (sticky or replicated) |
| Use Case | Front tier, static content, proxy, load balancing | Backend dynamic logic |

Web servers specialise in efficient HTTP request handling and static file delivery. Application servers host and execute code that produces dynamic responses.

---

## Apache Tomcat

### What is Tomcat?

Apache Tomcat is an open source Java Servlet/JSP container. The current major release, **Tomcat 11**, implements the following Jakarta EE 11 specifications:

- Servlet 6.1
- JSP (Pages) 4.0
- Expression Language (EL) 6.0
- WebSocket 2.2
- Authentication 3.1

Tomcat is not a full Jakarta EE stack. It does not include built-in EJB, JPA, JMS, or JTA. These are typically provided at the application layer via frameworks like Spring and Hibernate.

>**Important for Tomcat 10 and later:** The primary package namespace changed from `javax.*` to `jakarta.*` as part of the move to the Eclipse Foundation. Applications written for Tomcat 9 or earlier will require code changes or use of the [Apache Tomcat Migration Tool for Jakarta EE](https://tomcat.apache.org/download-migration.cgi) before running on Tomcat 10 or 11.

---

### Core Internal Components

- **Coyote:** Protocol handler (HTTP/1.1, HTTP/2 via upgrade, AJP if enabled)
- **Catalina:** Servlet container (deployment, lifecycle management, URL mapping, filter chains)
- **Jasper:** JSP compiler; converts `.jsp` files to Java servlet source, then compiles to bytecode
- **Realm:** Authentication and authorisation integration (MemoryRealm, JDBCRealm, JNDIRealm, etc.)
- **Connectors:** Network endpoints (HTTP, HTTPS, AJP)
- **Executor:** Optional shared thread pool for connectors and servlet threads, enabling centralised control

---

### Request Flow

```
Client > Connector (Coyote) > Catalina Mapping > Filter Chain > Servlet/JSP > Response Commit > Output via Coyote
```

```
+-------------------------------+      +-------------------------------+      +---------------------------------+
|      Client (Browser)         |<---->|  Coyote (HTTP connector)      |<---->|   Servlet engine (Catalina)     |
|  HTTP request                 |      |  Acceptor threads             |      |  Servlets/JSP processing        |
|  HTTP response                |      |  Worker threads               |      |                                 |
|                               |      |  SSL/TLS encryption (if HTTPS)|      |                                 |
+-------------------------------+      +-------------------------------+      +---------------------------------+
                                                                                 |                            |
                                                                                 v                            v
                                                                                +-------------------------------+
                                                                                | Jasper                        |
                                                                                | (JSP engine, if JSP)          |
                                                                                | JSP compilation (if JSP file) |
                                                                                | and Java bytecode delivery    |
                                                                                | for Catalina processing       |
                                                                                +-------------------------------+
```

- **Client (Browser):** Sends HTTP request, receives HTTP response.
- **Coyote (HTTP Connector):** Listens for incoming connections, handles SSL/TLS, and hands requests to Catalina.
- **Catalina (Servlet Engine):** Manages the Servlet lifecycle; delegates JSP rendering to Jasper.
- **Jasper (JSP Engine):** Compiles JSPs to Servlet classes (bytecode), which are then executed by Catalina.

---

## Environment & Prerequisites

| Item | Recommendation |
|------|----------------|
| OS | RHEL / CentOS / Rocky / AlmaLinux / Debian / Ubuntu |
| Java Version | Tomcat 11 requires Java 17 or later. Use the current LTS (OpenJDK 21) for best results. Virtual thread support (Project Loom) requires JDK 21+. |
| User Separation | Run Tomcat as a non root user (e.g., `tomcat`) |
| Firewall | Restrict inbound to required ports only |
| SELinux/AppArmor | Configure policies rather than disabling |


>Prerequisites for this chapter: Create one VM (Server with GUI)

**Set hostname (Optional):**
```bash
sudo hostnamectl set-hostname tomcatserver.devopsclass.com
```
```bash
exec bash
```

Configure network (Optional for this lab):
```bash
nmtui
```

---

### Install Java

Debian/Ubuntu:
```bash
sudo apt install -y openjdk-21-jdk
```

RHEL/CentOS/Rocky:
```bash
sudo dnf install java-21-openjdk-devel
```

> Use a consistent Java version throughout. Avoid the wildcard `java-*-openjdk-devel` on RHEL in production, as it may install an unexpected version.

Verify:
```bash
java -version
```

Add variables to your shell startup file or a system-wide profile (e.g., `/etc/profile.d/tomcat.sh`):

```bash
sudo vim ~/.bashrc
```

For **Debian/Ubuntu** (OpenJDK 21 path):
```bash
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
export CATALINA_HOME=/opt/tomcat
export PATH=$PATH:$CATALINA_HOME/bin
```

For **RHEL/Rocky** (OpenJDK 21 path):
```bash
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk
export CATALINA_HOME=/opt/tomcat
export PATH=$PATH:$CATALINA_HOME/bin
```

> The exact `JAVA_HOME` path varies by distribution. Verify with `dirname $(dirname $(readlink -f $(which java)))` after installation.

```bash
source ~/.bashrc
```

---
<img width="940" height="123" alt="Screenshot 2026-05-06 at 8 39 42 AM" src="https://github.com/user-attachments/assets/60b59544-58ae-434f-8edc-d0eb29d5e043" />

---

## Install Tomcat

| Method | Pros | Cons |
|--------|------|------|
| tar.gz manual | Full control, multiple versions side by side | Manual updates, no automatic service management |
| OS packages | Easy updates via package manager | May lag latest upstream, uses opinionated paths |
| Container image | Fast portability, immutable layering | Requires container orchestration hygiene |
| Configuration mgmt (Ansible) | Repeatable, versionable | Setup complexity |

---

Transfer a previously downloaded archive on anyother machine:
```bash
scp <apache-tomcat.tar.gz> user_name@<IP_Addr>:/opt
```
---

### tar.gz Manual Install

Visit [Apache Tomcat](https://tomcat.apache.org/) to find the latest download link.

Download Tomcat (replace the version with the latest stable release):

```bash
cd /tmp
```
---
<img width="1470" height="828" alt="Screenshot 2026-05-06 at 9 35 05 AM" src="https://github.com/user-attachments/assets/3c5014c4-e2a9-48d0-bcc6-cb378a10c5a6" />

---
```bash
wget https://dlcdn.apache.org/tomcat/tomcat-11/v11.0.22/bin/apache-tomcat-11.0.22.tar.gz
```

Extract:
```bash
sudo tar -xzf apache-tomcat-*.tar.gz
```
>-x > extract > Unpacks files from the archive.

>-z > gzip > Tells tar the archive is compressed using gzip (.gz).

>-f > file > Specifies the archive filename that follows.

Remove the archive:
```bash
sudo rm -r apache-tomcat-*.tar.gz
```

Move to `/opt`:
```bash
sudo mv apache-tomcat-* /opt/tomcat
```

Return to home directory:
```bash
cd
```

Create a `tomcat` group:
```bash
sudo groupadd tomcat
```

Create a `tomcat` user with no login shell and set the home directory:
```bash
sudo useradd -g tomcat -d /opt/tomcat -s /sbin/nologin tomcat
```

Assign ownership of `/opt/tomcat` to the `tomcat` user and group:
```bash
sudo chown -R tomcat:tomcat /opt/tomcat
```

View the directory layout:
```bash
sudo tree /opt/tomcat
```
---
<img width="797" height="448" alt="Screenshot 2026-05-06 at 9 43 27 AM" src="https://github.com/user-attachments/assets/f59cdc71-4888-4f1e-856f-063e76daa62d" />


> In production, avoid modifying the default `webapps` directory directly. Deploy only required WARs. Remove unused default applications (`docs`, `examples`, `manager`, `host-manager`) to reduce the attack surface.

---

## Running Tomcat

### Manual Start/Stop

Start Tomcat:
```bash
sudo -u tomcat /opt/tomcat/bin/startup.sh
```

Check port (default 8080):
```bash
netstat -tnlp | grep 8080
```

Stop Tomcat:
```bash
sudo -u tomcat /opt/tomcat/bin/shutdown.sh
```

---

## Automated Process: Making Tomcat Persistent

### Method 1: rc.local

`rc.local` is a traditional Linux init script that runs at the end of the boot sequence. On modern systemd-based systems it is largely superseded by systemd services and should be treated as a legacy fallback.

> `/etc/rc.d/rc.local` must exist and be executable for this to work.

```bash
sudo vim /etc/rc.d/rc.local
```

Add the full path to the Tomcat startup script:
```bash
sudo -u tomcat /opt/tomcat/bin/startup.sh
```

Set executable permission:
```bash
sudo chmod u+x /etc/rc.d/rc.local
```

---

### Method 2: Systemd Service (Preferred)

Stop any manually started Tomcat instance:
```bash
sudo -u tomcat /opt/tomcat/bin/catalina.sh stop || true
```

If still running:
```bash
ps -ef | grep java | grep tomcat
sudo pkill -u tomcat java || true
```

Ensure the temp directory is clean:
```bash
sudo rm -f /opt/tomcat/temp/tomcat.pid
sudo mkdir -p /opt/tomcat/temp
sudo chown tomcat:tomcat /opt/tomcat/temp
```

Apply SELinux context to the Tomcat installation (RHEL-based systems):
```bash
sudo semanage fcontext -a -t bin_t "/opt/tomcat/bin(/.*)?"
sudo semanage fcontext -a -t usr_t "/opt/tomcat/(conf|lib|webapps|logs|temp|work)(/.*)?"
sudo restorecon -Rv /opt/tomcat
```

> These are generic SELinux type assignments for a manual install where no Tomcat-specific SELinux policy module is present. If your distribution ships a `tomcat_t` policy (e.g., via the `tomcat-selinux` package), use that instead for tighter confinement.

Create an environment file:
```bash
sudo tee /etc/default/tomcat <<EOF
JAVA_HOME=/usr/lib/jvm/java-21-openjdk
CATALINA_HOME=/opt/tomcat
CATALINA_BASE=/opt/tomcat
CATALINA_PID=/opt/tomcat/temp/tomcat.pid
CATALINA_OPTS="-Xms256m -Xmx512m -XX:+UseG1GC -Djava.security.egd=file:/dev/urandom"
EOF
```

> `/dev/urandom` is sufficient on modern Linux kernels (4.8+) and JVMs. The older `/dev/./urandom` workaround (used to bypass blocking on early JVMs) is no longer necessary.

Create the systemd unit file:
```bash
sudo tee /etc/systemd/system/tomcat.service <<'EOF'
[Unit]
Description=Apache Tomcat 11 Servlet Container
After=network.target

[Service]
Type=forking
User=tomcat
Group=tomcat
EnvironmentFile=-/etc/default/tomcat

ExecStartPre=/usr/bin/mkdir -p /opt/tomcat/temp
ExecStartPre=/usr/bin/chown tomcat:tomcat /opt/tomcat/temp

ExecStart=/opt/tomcat/bin/catalina.sh start
ExecStop=/opt/tomcat/bin/catalina.sh stop

Restart=on-failure
RestartSec=5
UMask=0027
LimitNOFILE=65536
PrivateTmp=true
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
EOF
```

Verify syntax, reload systemd, then enable and start the service:
```bash
sudo systemd-analyze verify /etc/systemd/system/tomcat.service
sudo systemctl daemon-reload
```
```bash
sudo systemctl enable --now tomcat
sudo systemctl status tomcat
```

---
<img width="1294" height="493" alt="Screenshot 2025-11-24 at 7 57 07 AM" src="https://github.com/user-attachments/assets/bee80e0a-8715-4093-b000-5ef2dac9771d" />


---

## Changing the Default Tomcat Port (Optional)

Check whether the desired port (e.g., 5080) is already in use:
```bash
netstat -tnlp | grep 5080
```

Edit `server.xml`:
```bash
sudo vim $CATALINA_HOME/conf/server.xml
```

Update the Connector element:
```xml
<Connector port="5080" protocol="HTTP/1.1"
           connectionTimeout="20000"
           redirectPort="8443" />
```
---
<img width="753" height="146" alt="Screenshot 2025-11-21 at 8 08 02 AM" src="https://github.com/user-attachments/assets/f92dfb60-49f3-459f-b837-7fc5e9afbebe" />

---
<img width="801" height="557" alt="Screenshot 2026-05-06 at 7 14 12 AM" src="https://github.com/user-attachments/assets/893ca882-ffc6-4f2d-9d7d-561d4eaf9f98" />

---

## Set Firewall Rules

```bash
sudo firewall-cmd --list-all
```
```bash
sudo firewall-cmd --permanent --add-port=8080/tcp
```
```bash
sudo firewall-cmd --add-port=5080/tcp --permanent
```
```bash
sudo firewall-cmd --permanent --add-port=80/tcp
```
```bash
sudo firewall-cmd --reload
```

---

## Secure Remote Access to Manager/Host Manager

Tomcat's Manager and Host Manager are locked to localhost by default. Accessing `http://server:8080/manager` from another machine returns **403 Forbidden**. Fix this by editing `context.xml` for both apps and adding your IP to `RemoteAddrValve`.

Allow specific IPs:
```
allow="127\.\d+\.\d+\.\d+|::1|0:0:0:0:0:0:0:1|192\.168\.1\.10|10\.10\.5\.157"
```

Allow an entire subnet:
```
allow="127\.\d+\.\d+\.\d+|::1|0:0:0:0:0:0:0:1|192\.168\.1\.\d+|10\.10\.0\.\d+"
```

### Host Manager

`host-manager/META-INF/context.xml` configures the Host Manager application (manage virtual hosts), scoped to server-wide host administration.

```bash
sudo vim $CATALINA_HOME/webapps/host-manager/META-INF/context.xml
```

Option A: Regex (RemoteAddrValve):
```xml
<Valve className="org.apache.catalina.valves.RemoteAddrValve"
       allow="127\.\d+\.\d+\.\d+|::1|0:0:0:0:0:0:0:1|10\.10\.0\.\d+" />
```

> Never remove or comment out `RemoteAddrValve` in production; doing so removes all IP restrictions.

Option B: CIDR (RemoteCIDRValve):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Context antiResourceLocking="false" privileged="true" ignoreAnnotations="true">
  <CookieProcessor className="org.apache.tomcat.util.http.Rfc6265CookieProcessor"
                   sameSiteCookies="strict" />
  <Valve className="org.apache.catalina.valves.RemoteCIDRValve"
         allow="127.0.0.0/8,::1/128,10.10.0.0/16" />
  <Manager sessionAttributeValueClassNameFilter="java\.lang\.(?:Boolean|Integer|Long|Number|String)|org\.apache\.catalina\.filters\.CsrfPreventionFilter\$LruCache(?:\$1)?|java\.util\.(?:Linked)?HashMap"/>
</Context>
```
---
<img width="907" height="300" alt="Screenshot 2026-05-06 at 1 06 50 PM" src="https://github.com/user-attachments/assets/748caf76-0507-44b7-a10b-3a977ee05acf" />

---

### Manager App

`manager/META-INF/context.xml` configures the Manager application (deploy, undeploy, start, and stop applications; view runtime status).

```bash
sudo vim $CATALINA_HOME/webapps/manager/META-INF/context.xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Context antiResourceLocking="false" privileged="true" ignoreAnnotations="true">
  <CookieProcessor className="org.apache.tomcat.util.http.Rfc6265CookieProcessor"
                   sameSiteCookies="strict" />
  <Valve className="org.apache.catalina.valves.RemoteCIDRValve"
         allow="127.0.0.0/8,::1/128,10.10.0.0/16" />
  <Manager sessionAttributeValueClassNameFilter="java\.lang\.(?:Boolean|Integer|Long|Number|String)|org\.apache\.catalina\.filters\.CsrfPreventionFilter\$LruCache(?:\$1)?|java\.util\.(?:Linked)?HashMap"/>
</Context>
```
---
<img width="912" height="299" alt="Screenshot 2026-05-06 at 1 07 32 PM" src="https://github.com/user-attachments/assets/a115dd45-78c8-44d5-8830-ff33a47df312" />

---

### Verify

Check from the terminal:
```bash
sudo grep -i "allow" $CATALINA_HOME/webapps/host-manager/META-INF/context.xml
sudo grep -i "allow" $CATALINA_HOME/webapps/manager/META-INF/context.xml
```

Restart Tomcat:
```bash
sudo systemctl restart tomcat
```
---
<img width="906" height="188" alt="Screenshot 2026-05-06 at 1 08 29 PM" src="https://github.com/user-attachments/assets/c2e0a14a-d409-4b08-a9a5-0a360f4089d0" />

---

## Create Roles and Users (tomcat-users.xml)

```bash
sudo vim $CATALINA_HOME/conf/tomcat-users.xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<tomcat-users xmlns="http://tomcat.apache.org/xml"
              xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
              xsi:schemaLocation="http://tomcat.apache.org/xml tomcat-users.xsd"
              version="1.0">

  <role rolename="manager-gui"/>
  <role rolename="manager-script"/>
  <role rolename="manager-jmx"/>
  <role rolename="manager-status"/>
  <role rolename="admin-gui"/>
  <role rolename="admin-script"/>

  <user username="admin"
        password="devops"
        roles="manager-gui,manager-status,admin-gui"/>

  <user username="deployer"
        password="devops"
        roles="manager-script,manager-jmx,manager-status,admin-script"/>

</tomcat-users>
```

> The password `devops` is used here for demonstration only. In production, use a strong, unique password. Restrict `manager-gui` access to the internal network only and avoid assigning all roles to a single account.
---
<img width="906" height="524" alt="Screenshot 2026-05-06 at 1 09 17 PM" src="https://github.com/user-attachments/assets/7e6783fa-b6f8-47b5-822d-4486fc153475" />

---

Reload Tomcat to apply changes:
```bash
sudo systemctl restart tomcat
```

### Verify

Access from a browser on your host machine:
```
http://<server_ip>:8080
```
---
<img width="1470" height="924" alt="Screenshot 2026-05-06 at 1 10 23 PM" src="https://github.com/user-attachments/assets/accca0a9-2082-40b7-8995-6fc6f398add5" />

---
```
http://<server_ip>:8080/host-manager/html
```
---
<img width="1470" height="928" alt="Screenshot 2026-05-06 at 1 12 23 PM" src="https://github.com/user-attachments/assets/87c33402-9a98-4ecb-8f21-cdf88ed8bb56" />

---
<img width="1470" height="911" alt="Screenshot 2026-05-06 at 1 16 59 PM" src="https://github.com/user-attachments/assets/de7b6214-b42a-466d-89ef-66f7073d0eef" />

---

```
http://<server_ip>:8080/manager/html
```
---
<img width="1470" height="927" alt="Screenshot 2026-05-06 at 1 10 55 PM" src="https://github.com/user-attachments/assets/0c05aaae-2a7a-4f61-95ea-6cff9ebe49db" />

---
<img width="1468" height="929" alt="Screenshot 2026-05-06 at 1 16 22 PM" src="https://github.com/user-attachments/assets/33cc9ba8-06b3-45a9-9e5b-49608dd25a05" />

---

## Security Recommendations

| Area | Action |
|------|--------|
| Default Apps | Remove `/webapps/docs`, `/webapps/examples` |
| Manager Access | Restrict by IP + strong credentials; consider placing behind a reverse proxy with additional HTTP auth |
| TLS | Prefer a reverse proxy (Nginx/HAProxy) for TLS termination; Tomcat's native NIO/APR connectors also support SSL directly |
| Headers | Add security headers (CSP, HSTS, X-Frame Options) via Tomcat Filters or the proxy layer |
| JMX | Bind JMX to localhost; protect with a password file and SSL, or disable remote JMX entirely if not needed |
| Users | Manage roles in `tomcat-users.xml` for simple setups; prefer an external Realm (LDAP/OIDC) in enterprise environments |
| Logging | Configure `logrotate` to prevent disk exhaustion from growing log files |
| File Permissions | The `tomcat` user should have read only access to binaries and write access only to `logs/`, `temp/`, and `work/` |
| Updates | Track Tomcat and Java CVEs; apply security patches promptly |
| AJP Connector | Disabled by default since Tomcat 9.0.31 / 8.5.51 (CVE-2020-1938 "Ghostcat"). Leave disabled unless you specifically need AJP with a front end connector like mod_jk |
| Shutdown Port | The default `server.xml` uses port 8005 with the plain text command `SHUTDOWN`. Change the command to a random string or set `port="-1"` to disable the shutdown port entirely if you manage lifecycle through systemd |
| Session Security | Set session cookies with `HttpOnly` and `Secure` flags; configure an appropriate session timeout |

Minimal `tomcat-users.xml` entry example:
```xml
<role rolename="manager-status"/>
<user username="statususer" password="StrongPass123!" roles="manager-status"/>
```

Restrict full GUI admin access to the internal network only.

---

## Performance & Tuning

| Parameter | Description | Strategy |
|-----------|-------------|----------|
| maxThreads | Maximum concurrent worker threads | Start around 200; tune upward based on throughput testing and thread dump analysis |
| acceptCount | Queue depth when all threads are busy | Set above your typical spike volume (e.g., 200–500) to avoid premature connection refusal |
| connectionTimeout | Socket read timeout in milliseconds | 20,000 ms is the default; reduce for APIs that should respond quickly |
| Executor | Shared thread pool across connectors | Enables centralised min/max thread configuration and monitoring |
| JVM Heap | `-Xms` / `-Xmx` sizing | Size based on application profiling; monitor GC pause time and frequency |
| GC Strategy | G1GC (default in JDK 9+), ZGC for large heaps | Validate with representative load testing; ZGC targets sub-millisecond pauses |
| Compression | `compression="on"` for text responses | Reduces bandwidth but adds CPU overhead; exclude binary and already-compressed formats |
| KeepAlive | Controls HTTP connection reuse | Improves efficiency for HTTP/1.1 clients; HTTP/2 uses multiplexing instead |
| HTTP/2 | Request multiplexing over a single connection | Requires the `Http2Protocol` upgrade protocol added to the connector in `server.xml` |
| Virtual Threads | Lightweight concurrency via Project Loom | Available in Tomcat 11 with JDK 21+; set `executor="virtual"` on the Connector |

Add to `$CATALINA_HOME/bin/setenv.sh` (create if it does not exist):
```bash
export JAVA_OPTS="-Xms512m -Xmx1024m -XX:+UseG1GC -XX:MaxGCPauseMillis=200 -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/opt/tomcat/logs"
```

---

## Monitoring

- JMX (local access + Prometheus JMX exporter for metrics collection)
- Access logs (latency patterns, error rate trends)
- Heap and GC metrics (VisualVM, Java Mission Control, `jstat`)
- Thread dumps for diagnosing hangs and stalls (`jstack <pid>`)
- APM integration (e.g., OpenTelemetry Java agent)

Prometheus JMX exporter config example snippet:
```yaml
rules:
  - pattern: 'java.lang<type=Memory><HeapMemoryUsage>(.*)'
```

---

## Deployment & Lifecycle

| Step | Action |
|------|--------|
| Build | Produce a WAR via Maven or Gradle |
| Scan | Run SAST/DAST and dependency vulnerability checks (e.g., OWASP Dependency-Check) |
| Stage | Copy WAR to `webapps/` or use the `/manager/text/deploy` endpoint |
| Validate | Check a health endpoint (`/health` or a custom servlet) after deployment |
| Traffic Shift | Use a reverse proxy or load balancer to drain the old instance before cutting over |
| Rollback | Keep the previous WAR versioned (e.g., `app-1.4.2.war`) for quick rollback |

CLI Manager (requires `manager-script` role):
```bash
curl -u admin:devops "http://10.10.5.4:5080/manager/text/list"
curl -u admin:devops "http://10.10.5.4:5080/manager/text/deploy?path=/app&war=file:/opt/releases/app-1.4.2.war"
curl -u admin:devops "http://10.10.5.4:5080/manager/text/undeploy?path=/app"
```

**Zero Downtime Strategy:**

- **Blue/green:** Run `app-v1` and `app-v2` as separate context paths behind a proxy that rewrites the route at cutover.

- **Rolling instance replacement:** Pre-deploy to a new Tomcat instance, then deregister the old instance from the load balancer once the new one is healthy.

---

## Logging & Diagnostics

Default log files:

| File | Purpose |
|------|---------|
| `catalina.out` | JVM stdout/stderr; does not self-rotate — handle externally with logrotate |
| `localhost_access_log*.txt` | Access log |
| `localhost.yyyy-MM-dd.log` | Per-host application log |
| `manager.yyyy-MM-dd.log` | Manager App activity |

Rotation via logrotate (`/etc/logrotate.d/tomcat`):
```
/opt/tomcat/logs/*.log {
  daily
  rotate 14
  compress
  missingok
  copytruncate
  notifempty
}
```

Thread dump (investigate hangs or slowness):
```bash
jstack $(pgrep -f 'org.apache.catalina.startup.Bootstrap') > /tmp/tdump.txt
```

Heap dump (triggered automatically on OOM with the JVM flag `-XX:+HeapDumpOnOutOfMemoryError`): analyse the resulting `.hprof` file with Eclipse MAT or VisualVM.

---

## Reverse Proxy Integration

Nginx sample:
```nginx
server {
  listen 80;
  server_name app.example.com;

  location / {
    proxy_pass http://127.0.0.1:5080;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $remote_addr;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Port $server_port;
  }
}
```

For Tomcat to trust forwarded headers and issue correct redirects and secure cookie flags, add `RemoteIpValve` inside `<Engine>` or `<Host>` in `server.xml`:
```xml
<Valve className="org.apache.catalina.valves.RemoteIpValve"
       internalProxies="127\.0\.0\.1"
       remoteIpHeader="X-Forwarded-For"
       protocolHeader="X-Forwarded-Proto" />
```

---

## Session Management & Scalability

| Strategy | Description | Trade-offs |
|----------|-------------|------------|
| Sticky Sessions | Load balancer always routes a user to the same node | Simple; session is lost if that node fails |
| Session Replication | Delta or full session replication between cluster nodes | Higher memory and network overhead; built into Tomcat clustering |
| External Store | Redis / Memcached via a custom session Manager | Decouples session state from the JVM; adds network latency per request |
| Stateless (Token) | JWT/OAuth2 tokens; minimal or no server-side session | Cleanest approach for scaling; requires refactoring legacy session-based apps |

For horizontal scaling, prefer an external session store or a fully stateless design.

---

## Comparison: Tomcat vs Alternatives

| Feature | Tomcat | Jetty | Undertow | Full EE (WildFly) |
|---------|--------|-------|----------|-------------------|
| Footprint | Small | Smaller | Very small | Larger |
| Async Support | Yes (Servlet 3.1+) | Strong | Strong | Yes |
| WebSocket | Yes | Yes | Yes | Yes |
| HTTP/2 | Yes (config required) | Yes | Yes | Yes |
| Jakarta EE Full | No | No | No | Yes |
| Embedded Mode | Yes (native `tomcat-embed-core` API; also via Spring Boot) | Native | Native | Not typical |
| Startup Speed | Fast | Faster | Very fast | Moderate |

---
---

### WAR Deployment Lab

Understanding how to package and deploy a Java web application is foundational.

**Build a sample WAR with Maven:**
```bash
sudo apt install -y maven          # Debian/Ubuntu
sudo dnf install maven             # RHEL/Rocky
```

Create a minimal Maven project:
```bash
mvn archetype:generate \
  -DgroupId=com.example \
  -DartifactId=myapp \
  -DarchetypeArtifactId=maven-archetype-webapp \
  -DinteractiveMode=false
cd myapp
mvn package
```

This produces `target/myapp.war`. Deploy it:
```bash
sudo cp target/myapp.war /opt/tomcat/webapps/
sudo systemctl restart tomcat
```

Verify in a browser:
```
http://<server_ip>:8080/myapp
```

Undeploy (remove the WAR and the expanded directory):
```bash
sudo rm -rf /opt/tomcat/webapps/myapp.war /opt/tomcat/webapps/myapp
```

---

### Virtual Hosts (Multiple Applications on One Server)

Tomcat supports multiple virtual hosts via `<Host>` elements in `server.xml`. Each host can serve a different domain and point to its own `appBase` directory.

```xml
<Engine name="Catalina" defaultHost="localhost">

  <Host name="app1.example.com" appBase="/opt/apps/app1"
        unpackWARs="true" autoDeploy="true">
    <Valve className="org.apache.catalina.valves.AccessLogValve"
           directory="logs" prefix="app1_access_log" suffix=".txt"
           pattern="%h %l %u %t &quot;%r&quot; %s %b" />
  </Host>

  <Host name="app2.example.com" appBase="/opt/apps/app2"
        unpackWARs="true" autoDeploy="true">
  </Host>

</Engine>
```

Each `appBase` directory must exist and be owned by the `tomcat` user.

---

### HTTPS / TLS Configuration

For production, TLS termination at a reverse proxy (Nginx/HAProxy) is the recommended approach. However, you should know how to configure it directly on Tomcat as well.

**Using a self-signed certificate (for testing):**

Generate a keystore:
```bash
keytool -genkey -alias tomcat \
  -keyalg RSA -keysize 2048 \
  -keystore /opt/tomcat/conf/keystore.jks \
  -validity 365 \
  -storepass changeit -keypass changeit \
  -dname "CN=localhost, OU=Dev, O=Example, L=City, S=State, C=US"
sudo chown tomcat:tomcat /opt/tomcat/conf/keystore.jks
sudo chmod 640 /opt/tomcat/conf/keystore.jks
```

Add an HTTPS connector in `server.xml`:
```xml
<Connector port="8443" protocol="org.apache.coyote.http11.Http11NioProtocol"
           maxThreads="150" SSLEnabled="true">
  <SSLHostConfig>
    <Certificate certificateKeystoreFile="conf/keystore.jks"
                 certificateKeystorePassword="changeit"
                 type="RSA" />
  </SSLHostConfig>
</Connector>
```

Restart and verify:
```bash
sudo systemctl restart tomcat
curl -k https://<server_ip>:8443/
```

Allow the port through the firewall:
```bash
sudo firewall-cmd --permanent --add-port=8443/tcp
sudo firewall-cmd --reload
```

> In production, use a certificate from a trusted CA (e.g., Let's Encrypt) and prefer Nginx as the TLS terminator.

---

### JNDI DataSource Configuration

Applications often need database connections. Rather than hardcoding connection strings, Tomcat supports JNDI DataSources so the container manages the connection pool.

Add a JDBC driver JAR to `/opt/tomcat/lib/` (example: MySQL):
```bash
sudo cp mysql-connector-j-*.jar /opt/tomcat/lib/
sudo chown tomcat:tomcat /opt/tomcat/lib/mysql-connector-j-*.jar
```

Define the DataSource in `$CATALINA_HOME/conf/context.xml` (global) or in your application's `META-INF/context.xml`:
```xml
<Resource name="jdbc/mydb"
          auth="Container"
          type="javax.sql.DataSource"
          driverClassName="com.mysql.cj.jdbc.Driver"
          url="jdbc:mysql://localhost:3306/mydb"
          username="dbuser"
          password="dbpass"
          maxTotal="20"
          maxIdle="10"
          maxWaitMillis="10000" />
```

Reference it in your application's `web.xml`:
```xml
<resource-ref>
  <description>DB Connection</description>
  <res-ref-name>jdbc/mydb</res-ref-name>
  <res-type>javax.sql.DataSource</res-type>
  <res-auth>Container</res-auth>
</resource-ref>
```

---

### Access Log Configuration

Tomcat ships with the `AccessLogValve` but it needs to be explicitly configured. Add it inside your `<Host>` block in `server.xml`:

```xml
<Valve className="org.apache.catalina.valves.AccessLogValve"
       directory="logs"
       prefix="localhost_access_log"
       suffix=".txt"
       pattern="%h %l %u %t &quot;%r&quot; %s %b %D"
       resolveHosts="false" />
```

The `%D` pattern field records request processing time in milliseconds — useful for detecting slow requests.

---
---
## Complete Example:

**Prerequisites: Java & OS setup**

Install Java 21 (LTS) and confirm the version. Tomcat 10.x requires Java 11+.
```bash
sudo dnf install -y java-21-openjdk java-21-openjdk-devel wget tar
```

Verify Java
```bash
java -version
```
- Expected: openjdk version "21.x.x"
  
```bash
echo $JAVA_HOME
```

- If empty, set it:
```
readlink -f $(which java)
```
```bash
sudo echo 'export JAVA_HOME=/usr/lib/jvm/java-21-openjdk' | sudo tee /etc/profile.d/java.sh > /dev/null
```
```
source /etc/profile.d/java.sh
```

Create a dedicated Tomcat user (no login shell)
```bash
sudo useradd -m -U -d /opt/tomcat -s /bin/false tomcat
```

Download & extract Tomcat 10
```bash
TOMCAT_VER="10.1.55"
```
```bash
cd /tmp
wget https://downloads.apache.org/tomcat/tomcat-10/v${TOMCAT_VER}/bin/apache-tomcat-${TOMCAT_VER}.tar.gz
```
```bash
sudo tar -xzf apache-tomcat-${TOMCAT_VER}.tar.gz -C /opt/tomcat --strip-components=1
```
```bash
cd
```
```bash
sudo chown -R tomcat:tomcat /opt/tomcat
sudo chmod -R 750 /opt/tomcat
```

Create a systemd service unit
```
sudo vim /etc/systemd/system/tomcat.service
```
```
[Unit]
Description=Apache Tomcat 10 Web Application Server
After=network.target

[Service]
Type=forking
User=tomcat
Group=tomcat

Environment="JAVA_HOME=/usr/lib/jvm/java-17-openjdk"
Environment="CATALINA_HOME=/opt/tomcat"
Environment="CATALINA_BASE=/opt/tomcat"
Environment="CATALINA_PID=/opt/tomcat/temp/tomcat.pid"
Environment="CATALINA_OPTS=-Xms512M -Xmx1024M -server -XX:+UseParallelGC"

ExecStart=/opt/tomcat/bin/startup.sh
ExecStop=/opt/tomcat/bin/shutdown.sh

UMask=0007
RestartSec=10
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable & start the service
```
sudo systemctl daemon-reload
sudo systemctl enable --now tomcat
sudo systemctl status tomcat
```

Open firewall port 8080
```
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload
```

**Build & deploy a WAR with Maven**

Install Maven on the build machine (or the same server)
```bash
sudo dnf install -y maven
```
```bash
mvn -version
```

Generate a sample webapp skeleton & build
```bash
mvn archetype:generate \
  -DgroupId=com.example \
  -DartifactId=myapp \
  -DarchetypeArtifactId=maven-archetype-webapp \
  -DinteractiveMode=false
```
```bash
cd myapp
```
```bash
mvn package      # Produces: target/myapp.war
```

Deploy the WAR to Tomcat
```bash
sudo cp target/myapp.war /opt/tomcat/webapps/
```
```bash
sudo systemctl restart tomcat
```
- Verify in browser:
```bash
curl http://localhost:8080/myapp/
```
---
<img width="1470" height="277" alt="Screenshot 2026-05-13 at 1 13 14 PM" src="https://github.com/user-attachments/assets/b6dde3ea-d378-4503-a7aa-fda2557bb272" />


---
# Change the content of App

```bash
cd myapp
```
```
tree
```
```
sudo vim src/main/webapp/index.jsp 
```
```
<html>
<body>
  <h2>Tip Calculator App</h2>
  <input type="number" id="bill" placeholder="Bill Amount">
  <button onclick="calc()">Calculate 15% Tip</button>
  <h3 id="result"></h3>

  <script>
    function calc() {
      const amount = document.getElementById('bill').value;
      const tip = (amount * 0.15).toFixed(2);
      document.getElementById('result').innerText = `Total Tip: $${tip}`;
    }
  </script>
</body>
</html>
```
```
mvn package
```
```
sudo cp target/myapp.war /opt/tomcat/webapps/
```
```
sudo systemctl restart tomcat
```
---
<img width="1470" height="293" alt="Screenshot 2026-05-13 at 1 27 52 PM" src="https://github.com/user-attachments/assets/90bd0340-4c70-4356-af49-0e608d75c242" />


---

**Undeploy cleanly**

```bash
sudo rm -rf /opt/tomcat/webapps/myapp.war \
             /opt/tomcat/webapps/myapp
sudo systemctl restart tomcat
```

---
---

**Virtual hosts: multiple apps on one server**

Edit `/opt/tomcat/conf/server.xml`. Each <Host> element maps a domain to its own webapps directory.

Create app directories & set ownership
```bash
sudo mkdir -p /opt/apps/app1 /opt/apps/app2
sudo chown -R tomcat:tomcat /opt/apps
```
```bash
# Set SELinux context so Tomcat can read the dirs
sudo semanage fcontext -a -t tomcat_var_lib_t "/opt/apps(/.*)?"
sudo restorecon -Rv /opt/apps
```

Virtual host block inside <Engine> in server.xml
`vim /opt/tomcat/conf/server.xml`
```xml
<Engine name="Catalina" defaultHost="localhost">

  <!-- Default localhost host (keep as-is) -->
  <Host name="localhost" appBase="webapps"
        unpackWARs="true" autoDeploy="true">
  </Host>

  <Host name="app1.example.com" appBase="/opt/apps/app1"
        unpackWARs="true" autoDeploy="true">
    <Valve className="org.apache.catalina.valves.AccessLogValve"
           directory="logs" prefix="app1_access_log" suffix=".txt"
           pattern="%h %l %u %t &quot;%r&quot; %s %b %D"
           resolveHosts="false" />
  </Host>

  <Host name="app2.example.com" appBase="/opt/apps/app2"
        unpackWARs="true" autoDeploy="true">
    <Valve className="org.apache.catalina.valves.AccessLogValve"
           directory="logs" prefix="app2_access_log" suffix=".txt"
           pattern="%h %l %u %t &quot;%r&quot; %s %b %D"
           resolveHosts="false" />
  </Host>

</Engine>
```

Deploy a WAR to a virtual host
```bash
# The ROOT.war becomes the root context for that vhost
sudo cp myapp.war /opt/apps/app1/ROOT.war
sudo chown tomcat:tomcat /opt/apps/app1/ROOT.war
sudo systemctl restart tomcat
```

> For local testing, add app1.example.com to /etc/hosts, pointing to your server IP.

---

**HTTPS / TLS configuration**

Two approaches are shown: direct Tomcat TLS (testing) and Nginx reverse proxy with Let's Encrypt (production recommended).

**Option A: Self-signed certificate (dev/testing only)**

```bash
# Generate a JKS keystore
sudo -u tomcat keytool -genkey -alias tomcat \
  -keyalg RSA -keysize 2048 \
  -keystore /opt/tomcat/conf/keystore.jks \
  -validity 365 \
  -storepass changeit -keypass changeit \
  -dname "CN=localhost, OU=Dev, O=Example, L=Kathmandu, S=Bagmati, C=NP"

sudo chmod 640 /opt/tomcat/conf/keystore.jks
```

Add HTTPS connector to server.xml (after the existing 8080 connector)

`sudo vim /opt/tomcat/conf/server.xml`

```bash
<Connector port="8443"
           protocol="org.apache.coyote.http11.Http11NioProtocol"
           maxThreads="150" SSLEnabled="true">
  <SSLHostConfig>
    <Certificate
      certificateKeystoreFile="conf/keystore.jks"
      certificateKeystorePassword="changeit"
      type="RSA" />
  </SSLHostConfig>
</Connector>
```

Open port & test
```bash
sudo firewall-cmd --permanent --add-port=8443/tcp
sudo firewall-cmd --reload
sudo systemctl restart tomcat
```
```bash
curl -k https://localhost:8443/
```

**Option B: Nginx TLS termination (production recommended)**

```bash
sudo dnf install -y nginx certbot python3-certbot-nginx
```
```bash
# Obtain a cert (replace with your domain)
sudo certbot --nginx -d app1.example.com
```

Nginx reverse proxy config

`sudo vim /etc/nginx/conf.d/app1.conf`

```nginx
server {
    listen 443 ssl;
    server_name app1.example.com;

    ssl_certificate     /etc/letsencrypt/live/app1.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app1.example.com/privkey.pem;

    location / {
        proxy_pass         http://127.0.0.1:8080;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name app1.example.com;
    return 301 https://$host$request_uri;
}
```

>With Nginx in front, keep Tomcat bound to 127.0.0.1 (not 0.0.0.0) by setting address="127.0.0.1" on the Connector to prevent direct public access on port 8080.


**JNDI DataSource: MySQL connection pool**

Install MySQL & create the database

```bash
sudo dnf install -y mysql-server
sudo systemctl enable --now mysqld
```
```sql
sudo mysql -u root -p <<'SQL'
CREATE DATABASE mydb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'dbuser'@'localhost' IDENTIFIED BY 'StrongPass1!';
GRANT ALL PRIVILEGES ON mydb.* TO 'dbuser'@'localhost';
FLUSH PRIVILEGES;
SQL
```

Download MySQL JDBC driver & place in Tomcat lib
```bash
# Download from Maven Central (adjust version as needed)
JDBC_VER="9.1.0"
wget https://repo1.maven.org/maven2/com/mysql/mysql-connector-j/${JDBC_VER}/mysql-connector-j-${JDBC_VER}.jar \
     -O /tmp/mysql-connector-j.jar

sudo cp /tmp/mysql-connector-j.jar /opt/tomcat/lib/
sudo chown tomcat:tomcat /opt/tomcat/lib/mysql-connector-j.jar
```

Define the DataSource resource

`sudo vim /opt/tomcat/conf/context.xml`

```
<Context>

  <!-- Disable session persistence across restarts (optional) -->
  <Manager pathname="" />

  <Resource name="jdbc/mydb"
            auth="Container"
            type="javax.sql.DataSource"
            driverClassName="com.mysql.cj.jdbc.Driver"
            url="jdbc:mysql://localhost:3306/mydb?serverTimezone=UTC&useSSL=false"
            username="dbuser"
            password="StrongPass1!"
            maxTotal="20"
            maxIdle="10"
            minIdle="5"
            maxWaitMillis="10000"
            validationQuery="SELECT 1"
            testOnBorrow="true" />

</Context>
```

Reference it in your webapp's WEB-INF/web.xml

`sudo vim src/main/webapp/WEB-INF/web.xml`

```
<resource-ref>
  <description>MySQL DB Connection Pool</description>
  <res-ref-name>jdbc/mydb</res-ref-name>
  <res-type>javax.sql.DataSource</res-type>
  <res-auth>Container</res-auth>
</resource-ref>
```

Lookup the DataSource in your Java servlet
```
Context initCtx = new InitialContext();
Context envCtx  = (Context) initCtx.lookup("java:comp/env");
DataSource ds   = (DataSource) envCtx.lookup("jdbc/mydb");

try (Connection conn = ds.getConnection()) {
    // use conn...
}
```

>Never commit database passwords to source control. Consider externalising them via environment variables or Vault and referencing with ${DB_PASS} in context.xml.


**Access log configuration**

Add the AccessLogValve inside each <Host> block in server.xml. The %D field records request time in ms, useful for spotting slow requests.

Valve configuration with extended pattern

`sudo vim /opt/tomcat/conf/server.xml` (inside <Host>)
```
<Valve className="org.apache.catalina.valves.AccessLogValve"
       directory="logs"
       prefix="localhost_access_log"
       suffix=".txt"
       pattern="%h %l %u %t &quot;%r&quot; %s %b %D"
       resolveHosts="false"
       rotatable="true" />
```

Pattern field reference

|token	|meaning
|%h	remote host
|%l	remote logical username
|%u	authenticated user
|%t	request timestamp
|%r	first line of request
|%s	HTTP status code
|%b	bytes sent
|%D	processing time (ms) < slow request detection 

Tail the access log live
```
tail -f /opt/tomcat/logs/localhost_access_log.$(date +%Y-%m-%d).txt
```

**Systemd management & firewall**
```
sudo systemctl start tomcat       # start
sudo systemctl stop tomcat        # stop
sudo systemctl restart tomcat     # restart (config changes)
sudo systemctl reload tomcat      # graceful reload (if supported)
sudo systemctl status tomcat      # service status + recent log lines
sudo journalctl -u tomcat -f      # follow live logs via journald
```
```
# HTTP (Tomcat direct)
sudo firewall-cmd --permanent --add-port=8080/tcp
```
```
# HTTPS (Tomcat direct / testing)
sudo firewall-cmd --permanent --add-port=8443/tcp
```
```
# Standard HTTPS (when using Nginx in front)
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-service=http
```
```
sudo firewall-cmd --reload
sudo firewall-cmd --list-all     # verify
```

SELinux — allow Tomcat to bind to non-standard ports if needed
```
# e.g. if you change Tomcat to port 9090
sudo semanage port -a -t http_port_t -p tcp 9090

# Check current Tomcat-related SELinux contexts
sudo semanage port -l | grep tomcat
```
---
---

### Tomcat Cluster and Session Replication (Concepts)

For high availability, Tomcat supports in-memory session replication between cluster nodes using multicast or static member configuration. The key elements in `server.xml` are `<Cluster>`, `<Manager className="org.apache.catalina.ha.session.DeltaManager">`, and `<Channel>`.

In practice, most teams at mid-level use an external session store (Redis via a session manager library) or design stateless applications instead of relying on Tomcat's built-in clustering. Understanding the concept and the trade-offs is more important than memorising the full cluster XML.

---

### Tomcat Version and Java Compatibility Quick Reference

| Tomcat Version | Min Java | Jakarta EE / Java EE | Status |
|----------------|----------|-----------------------|--------|
| 11.0.x | Java 17 | Jakarta EE 11 | Current (stable as of April 2025) |
| 10.1.x | Java 11 | Jakarta EE 10 | Supported |
| 9.0.x | Java 8 | Java EE 8 | Supported (extended until at least March 2027) |
| 8.5.x | Java 7 | Java EE 7 (subset) | End of Life |

Source: [Apache Tomcat: Which Version?](https://tomcat.apache.org/whichversion.html)

---
