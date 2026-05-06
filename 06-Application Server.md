# Application Servers & Apache Tomcat

---

**What is an Application Server?**
- An application server is a software platform that provides a runtime environment for dynamic application code (e.g., Java Servlets, JSP, WebSocket endpoints, REST APIs). It abstracts:
  - Business logic execution (transactions, security integration)
  - Resource management (thread pools, connection pools, clustering hooks)
  - Standard APIs (Servlet, JSP, WebSocket, Expression Language; in full Jakarta EE servers: JPA, JMS, CDI, JTA)
  - Deployment model (WAR, EAR, exploded or packaged)

Examples:
- Lightweight/Servlet containers: Apache Tomcat, Jetty, Undertow
- Full Jakarta EE/Enterprise: WildFly, Payara, WebLogic, WebSphere

**Web Server vs. Application Server**

| Feature         | Web Server (HTTPD, Nginx)                       | Application Server (Tomcat, WildFly)                |
|-----------------|-------------------------------------------------|-----------------------------------------------------|
| Primary Role    | Static content, reverse proxy, TLS termination  | Dynamic request execution (Servlets/JSP), APIs      |
| Execution Model | File streaming                                  | Managed components (Servlet lifecycle)              |
| Protocols       | HTTP/HTTPS (+ optional FastCGI, gRPC proxy)     | HTTP/HTTPS + implementation of Jakarta EE APIs      |
| Caching         | Strong static cache, edge friendly              | Caches objects in heap (depends on app design)      |
| Scaling         | Horizontal (stateless)                          | Horizontal + session handling (sticky or replicated)|
| Use Case        | Front tier, static content, proxy, load balancing | Backend dynamic logic                             |

> Web servers specialise in efficient HTTP request handling and static file delivery; application servers host and execute code that produces dynamic responses.

---

**Apache Tomcat**

**What is Tomcat?**
- Open source Java Servlet/JSP container
- Implements: Servlet, JSP, WebSocket, EL (Expression Language), and annotation based configuration
- Not a full Jakarta EE stack, no built-in EJB/JPA/JMS/JTA; these are typically supplied at the application layer via frameworks like Spring and Hibernate

**Core Internal Components**
- **Coyote:** Protocol handler (HTTP/1.1, HTTP/2 via upgrade, AJP if enabled)
- **Catalina:** Servlet container (deployment, lifecycle management, URL mapping, filter chains)
- **Jasper:** JSP compiler converts `.jsp` files to Java servlet source, then compiles to bytecode
- **Realm:** Authentication and authorisation integration (MemoryRealm, JDBCRealm, JNDIRealm, etc.)
- **Connectors:** Network endpoints (HTTP, HTTPS, AJP)
- **Executor:** Optional shared thread pool for connectors and servlet threads, enabling centralised control

**Request Flow**
```
Client > Connector (Coyote) > Catalina Mapping > Filter Chain > Servlet/JSP > Response Commit > Output via Coyote
```

- Tomcat Request Handling:
```
+-------------------------------+      +-------------------------------+      +---------------------------------+
|      Client (Browser)         |<---->|  Coyote (HTTP connector)      |<---->|   Servlet engine (Catalina)     |
|  HTTP request                 |      |  Acceptor threads             |      |  Servlets/JSP processing        |
|  HTTP response                |      |  Worker threads               |      |                                 |
|                               |      |  SSL/TLS encryption (if HTTPS)|      |                                 |
+-------------------------------+      +-------------------------------+      +---------------------------------+
                                                                                 |                            |
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

**Environment & Prerequisites**

| Item             | Recommendation |
|------------------|----------------|
| OS               | RHEL / CentOS / Rocky / AlmaLinux / Debian / Ubuntu |
| Java Version     | Use latest LTS (e.g., OpenJDK 21) |
| User Separation  | Run Tomcat as a non root user (e.g., `tomcat`) |
| Firewall         | Restrict inbound to required ports only |
| SELinux/AppArmor | Configure policies rather than disabling |

> Create one VM (Server with GUI)

- Set hostname:
```bash
sudo hostnamectl set-hostname tomcatserver.devopsclass.com
exec bash
```
---

<img width="800" height="192" alt="Screenshot 2026-05-05 at 1 13 50 PM" src="https://github.com/user-attachments/assets/b8eecf83-aea9-4920-af01-621e597719b4" />

---

- Configure network (Optional for this lab):
```bash
nmtui
```

---

- Install Java:
  
  - Debian/Ubuntu
    
```bash
sudo apt update                        # Optional
```
```bash
sudo apt install -y openjdk-21-jdk
```

  - RHEL/CentOS/Rocky
    
```bash
sudo dnf install java-21-openjdk-devel
```

> **Note:** Use a consistent Java version throughout. The examples below use Java 21 (current LTS). Avoid the wildcard `java-*-openjdk-devel` on RHEL in production, as it may install an unexpected version.

- Verify:
```bash
java -version
```

- Add variables to the shell startup file or a system wide profile (e.g., `/etc/profile.d/tomcat.sh`)

```bash
sudo vim ~/.bashrc
```
```bash
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk
export CATALINA_HOME=/opt/tomcat
export PATH=$PATH:$CATALINA_HOME/bin
```
```bash
source ~/.bashrc
```

<img width="940" height="123" alt="Screenshot 2026-05-06 at 8 39 42 AM" src="https://github.com/user-attachments/assets/60b59544-58ae-434f-8edc-d0eb29d5e043" />

---

**Install Tomcat**

| Method                        | Pros | Cons |
|-------------------------------|------|------|
| tar.gz manual                 | Full control, multiple versions side by side | Manual updates, no automatic service management |
| OS packages                   | Easy updates via package manager | May lag latest upstream, uses opinionated paths |
| Container image               | Fast portability, immutable layering | Requires container orchestration hygiene |
| Configuration mgmt (Ansible)  | Repeatable, versionable | Setup complexity |

**Transfer a previously downloaded archive:**
```bash
scp <apache-tomcat.tar.gz> user_name@<IP_Addr>:/opt
```

**tar.gz Manual Install**

- Visit [Apache Tomcat](https://tomcat.apache.org/) to find the latest download link.

<img width="1470" height="828" alt="Screenshot 2026-05-06 at 9 35 05 AM" src="https://github.com/user-attachments/assets/3c5014c4-e2a9-48d0-bcc6-cb378a10c5a6" />

---

- Download Tomcat (replace version with the latest stable release)
```bash
cd /tmp
```
> Paste the copied link address above together with the `wget` command.

```bash
wget https://dlcdn.apache.org/tomcat/tomcat-11/v11.0.22/bin/apache-tomcat-11.0.22.tar.gz
```

- Extract
```bash
sudo tar -xzf apache-tomcat-*.gz
```

- Remove the unwanted zip file
```bash
sudo rm -r apache-tomcat-*.gz
```

- Move to /opt
```bash
sudo mv apache-tomcat-* /opt/tomcat
```

- Return to home directory
```bash
cd
```

- Create a `tomcat` group
```bash
sudo groupadd tomcat
```

- Create a `tomcat` user with no login and set the home directory
```bash
sudo useradd -g tomcat -d /opt/tomcat -s /sbin/nologin tomcat
```

- Assign ownership of `/opt/tomcat` to the `tomcat` user and group
```bash
sudo chown -R tomcat:tomcat /opt/tomcat
```

- Directory Layout
```bash
sudo tree /opt/tomcat
```

<img width="797" height="448" alt="Screenshot 2026-05-06 at 9 43 27 AM" src="https://github.com/user-attachments/assets/f59cdc71-4888-4f1e-856f-063e76daa62d" />

> In production, avoid modifying the default `webapps` directory directly. Deploy only required WARs. Remove unused default applications (`docs`, `examples`, `manager`, `host-manager`) to reduce the attack surface.

---

**Running Tomcat**

**Handled Manually**

- Start Tomcat:
```bash
sudo -u tomcat /opt/tomcat/bin/startup.sh
```

- Check port (default 8080):
```bash
netstat -tnlp | grep 8080
```

<img width="988" height="237" alt="Screenshot 2025-11-20 at 1 20 56 PM" src="https://github.com/user-attachments/assets/00ac68c2-cdb5-40ba-bfa6-d45e125839ab" />

- Stop Tomcat:
```bash
sudo -u tomcat /opt/tomcat/bin/shutdown.sh
```

---

**Automated Process: Making this process persistent**

**Method 1: `rc.local`**
   
   `rc.local` is a traditional Linux init script that runs at the end of the boot sequence. It is a simple way to add startup tasks, but on modern systemd based systems, it is largely superseded by systemd services and should be treated as a legacy fallback.

> Note: `/etc/rc.d/rc.local` must exist and be executable for this to work.

```bash
sudo vim /etc/rc.d/rc.local
```

- Add the full path to the Tomcat startup script:
  
```bash
sudo -u tomcat /opt/tomcat/bin/startup.sh
```

<img width="743" height="268" alt="Screenshot 2025-11-21 at 7 47 33 AM" src="https://github.com/user-attachments/assets/836b8ea6-aada-463b-9f03-f8ffb05331ab" />

---

- Set executable permission:
```bash
sudo chmod u+x /etc/rc.d/rc.local
```

---

**Method 2: Systemd Service (Preferred over rc.local)**

- Stop any manually started Tomcat instance:
  
```bash
sudo -u tomcat /opt/tomcat/bin/catalina.sh stop || true
```

>If still running:
```bash
ps -ef | grep java | grep tomcat
sudo pkill -u tomcat java || true
```

- Ensure the temp directory is clean:
```bash
sudo rm -f /opt/tomcat/temp/tomcat.pid
```
```bash
sudo mkdir -p /opt/tomcat/temp
```
```bash
sudo chown tomcat:tomcat /opt/tomcat/temp
```

- Apply SELinux context to the Tomcat installation:
```bash
sudo semanage fcontext -a -t bin_t "/opt/tomcat/bin(/.*)?"
```
```bash
sudo semanage fcontext -a -t usr_t "/opt/tomcat/(conf|lib|webapps|logs|temp|work)(/.*)?"
```
```bash
sudo restorecon -Rv /opt/tomcat
```

> **Note:** These are generic SELinux type assignments for a manual install where no Tomcat specific SELinux policy module is present. If your distribution ships a `tomcat_t` policy (e.g., via the `tomcat selinux` package), use that instead for tighter confinement.

- Create an environment file:
```bash
sudo tee /etc/default/tomcat <<EOF
JAVA_HOME=/usr/lib/jvm/java-21-openjdk
CATALINA_HOME=/opt/tomcat
CATALINA_BASE=/opt/tomcat
CATALINA_PID=/opt/tomcat/temp/tomcat.pid
CATALINA_OPTS="-Xms256m -Xmx512m -XX:+UseG1GC -Djava.security.egd=file:/dev/urandom"
EOF
```

> **Note:** Values containing spaces or special characters must be quoted. Also note that `/dev/urandom` is sufficient on modern Linux kernels (4.8+) and JVMs; the older `/dev/./urandom` workaround (used to bypass blocking on early JVMs) is no longer necessary.

- Create the systemd unit file:
  
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

- Verify syntax, reload systemd, then enable and start the service:
  
```bash
sudo systemd-analyze verify /etc/systemd/system/tomcat.service
```
```bash
sudo systemctl daemon-reload
```
```bash
sudo systemctl enable tomcat
```
```bash
sudo systemctl start tomcat
```
```bash
sudo systemctl status tomcat
```

---

<img width="1294" height="493" alt="Screenshot 2025-11-24 at 7 57 07 AM" src="https://github.com/user-attachments/assets/bee80e0a-8715-4093-b000-5ef2dac9771d" />

---

**Changing the Default Tomcat Port [Optional]**

- Check whether the desired port (e.g., 5080) is already in use:
  
```bash
netstat -tnlp | grep 5080
```

- Edit `server.xml`:
  
```bash
sudo vim $CATALINA_HOME/conf/server.xml
```

- Update the Connector element:
  
```xml
<Connector port="5080" protocol="HTTP/1.1"
           connectionTimeout="20000"
           redirectPort="8443" />
```


<img width="753" height="146" alt="Screenshot 2025-11-21 at 8 08 02 AM" src="https://github.com/user-attachments/assets/f92dfb60-49f3-459f-b837-7fc5e9afbebe" />

---

<img width="801" height="557" alt="Screenshot 2026-05-06 at 7 14 12 AM" src="https://github.com/user-attachments/assets/893ca882-ffc6-4f2d-9d7d-561d4eaf9f98" />

---


**Set Firewall Rules:**

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


**Secure Remote Access to Manager/Host Manager**

Tomcat's Manager and Host Manager are locked to localhost by default. Accessing `http://server:8080/manager` from another machine returns **403 Forbidden**. Fix this by editing `context.xml` for both apps and adding your IP to `RemoteAddrValve`.

**Allow specific IPs:**
```
allow="127\.\d+\.\d+\.\d+|::1|0:0:0:0:0:0:0:1|192\.168\.1\.10|10\.10\.5\.157"
```

**Allow entire subnet:**
```
allow="127\.\d+\.\d+\.\d+|::1|0:0:0:0:0:0:0:1|192\.168\.1\.\d+|10\.10\.0\.\d+"
```

**Host Manager**

- **host manager/META-INF/context.xml**
  - Purpose: Configures the Host Manager application (manage virtual hosts).
  - Scope: Server wide host administration.

```bash
sudo vim $CATALINA_HOME/webapps/host-manager/META-INF/context.xml
```

**Option A-Regex (RemoteAddrValve):**
```xml
  <Valve className="org.apache.catalina.valves.RemoteAddrValve"
         allow="127\.\d+\.\d+\.\d+|::1|0:0:0:0:0:0:0:1|10\.10\.0\.\d+" />
```

> **Note:** Never remove or comment out `RemoteAddrValve` in production; it removes all IP restrictions.

**Option B-CIDR (RemoteCIDRValve):**
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

<img width="907" height="300" alt="Screenshot 2026-05-06 at 1 06 50 PM" src="https://github.com/user-attachments/assets/748caf76-0507-44b7-a10b-3a977ee05acf" />

---

**Manager App**:

- **manager/META-INF/context.xml**
  - Purpose: Configures the Manager application (manage web applications).
  - Scope: Deploy, undeploy, start, and stop applications; view runtime status.

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

<img width="912" height="299" alt="Screenshot 2026-05-06 at 1 07 32 PM" src="https://github.com/user-attachments/assets/a115dd45-78c8-44d5-8830-ff33a47df312" />

---

**Verify**:
  - Restart tomacat
```
sudo systemctl restart tomcat
```

  - Check from the terminal
```
sudo grep -i "allow" $CATALINA_HOME/webapps/host-manager/META-INF/context.xml
```
```
sudo grep -i "allow" $CATALINA_HOME/webapps/manager/META-INF/context.xml
```

<img width="906" height="188" alt="Screenshot 2026-05-06 at 1 08 29 PM" src="https://github.com/user-attachments/assets/c2e0a14a-d409-4b08-a9a5-0a360f4089d0" />


---


**Create Roles and Users (tomcat users.xml)**

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

> **Note:** The password `devops` is used here for demonstration only. In production, use a strong, unique password. Prefer restricting the `manager-gui` role to the internal network only and avoid assigning all roles to a single account.

<img width="906" height="524" alt="Screenshot 2026-05-06 at 1 09 17 PM" src="https://github.com/user-attachments/assets/7e6783fa-b6f8-47b5-822d-4486fc153475" />

---

- Reload Tomcat to apply changes:
  
```bash
sudo systemctl restart tomcat
```

---

**Verify:**
  - Access using your host computer and a web browser
  
```
http://<server_ip>:8080
```
- Example
```
http://10.10.4.5:8080
```

- Expected landing page text:

<img width="1470" height="924" alt="Screenshot 2026-05-06 at 1 10 23 PM" src="https://github.com/user-attachments/assets/accca0a9-2082-40b7-8995-6fc6f398add5" />


---

- http://10.10.0.132:8080/host-manager/html

<img width="1470" height="928" alt="Screenshot 2026-05-06 at 1 12 23 PM" src="https://github.com/user-attachments/assets/87c33402-9a98-4ecb-8f21-cdf88ed8bb56" />

---

<img width="1470" height="911" alt="Screenshot 2026-05-06 at 1 16 59 PM" src="https://github.com/user-attachments/assets/de7b6214-b42a-466d-89ef-66f7073d0eef" />

---

- http://10.10.0.132:8080/manager/html

<img width="1470" height="927" alt="Screenshot 2026-05-06 at 1 10 55 PM" src="https://github.com/user-attachments/assets/0c05aaae-2a7a-4f61-95ea-6cff9ebe49db" />

---
<img width="1468" height="929" alt="Screenshot 2026-05-06 at 1 16 22 PM" src="https://github.com/user-attachments/assets/33cc9ba8-06b3-45a9-9e5b-49608dd25a05" />

---

**Security Recommendations**

| Area             | Action |
|------------------|--------|
| Default Apps     | Remove `/webapps/docs`, `/webapps/examples` |
| Manager Access   | Restrict by IP + strong credentials; consider placing behind a reverse proxy with additional HTTP auth |
| TLS              | Prefer a reverse proxy (Nginx/HAProxy) for TLS termination; Tomcat's native NIO/APR connectors also support SSL directly |
| Headers          | Add security headers (CSP, HSTS, X-Frame-Options) via Tomcat Filters or the proxy layer |
| JMX              | Bind JMX to localhost; protect with a password file and SSL, or disable remote JMX entirely if not needed |
| Users            | Manage roles in `tomcat-users.xml` for simple setups; prefer an external Realm (LDAP/OIDC) in enterprise environments |
| Logging          | Configure `logrotate` to prevent disk exhaustion from growing log files |
| File Permissions | The `tomcat` user should have read-only access to binaries and write access only to `logs/`, `temp/`, and `work/` |
| Updates          | Track Tomcat and Java CVEs; apply security patches promptly |
| AJP Connector    | Disabled by default since Tomcat 9.0.31 / 8.5.51 (CVE-2020-1938 "Ghostcat"). Leave disabled unless you specifically need AJP with a front-end connector like mod_jk |
| Shutdown Port    | The default `server.xml` uses port 8005 with the plain-text command `SHUTDOWN`. Change the command to a random string or set `port="-1"` to disable the shutdown port entirely if you manage lifecycle through systemd |
| Session Security | Set session cookies with `HttpOnly` and `Secure` flags; configure an appropriate session timeout |

- Example minimal `tomcat-users.xml` entry:
```xml
<role rolename="manager-status"/>
<user username="statususer" password="StrongPass123!" roles="manager-status"/>
```
Restrict full GUI admin access to the internal network only.

---

**Performance & Tuning**

| Parameter          | Description | Strategy |
|--------------------|-------------|----------|
| maxThreads         | Maximum concurrent worker threads | Start around 200; tune upward based on throughput testing and thread dump analysis |
| acceptCount        | Queue depth when all threads are busy | Set above your typical spike volume (e.g., 200–500) to avoid premature connection refusal |
| connectionTimeout  | Socket read timeout in milliseconds | 20,000 ms is the default; reduce for APIs that should respond quickly |
| Executor           | Shared thread pool across connectors | Enables centralised min/max thread configuration and monitoring |
| JVM Heap           | `-Xms` / `-Xmx` sizing | Size based on application profiling; monitor GC pause time and frequency |
| GC Strategy        | G1GC (default in JDK 9+), ZGC for large heaps | Validate with representative load testing; ZGC targets sub-millisecond pauses |
| Compression        | `compression="on"` for text responses | Reduces bandwidth but adds CPU overhead; exclude binary and already-compressed formats |
| KeepAlive          | Controls HTTP connection reuse | Improves efficiency for HTTP/1.1 clients; HTTP/2 uses multiplexing instead |
| HTTP/2             | Request multiplexing over a single connection | Requires the `Http2Protocol` upgrade protocol added to the connector in `server.xml` |

Add to `$CATALINA_HOME/bin/setenv.sh` (create if it does not exist):
```bash
export JAVA_OPTS="-Xms512m -Xmx1024m -XX:+UseG1GC -XX:MaxGCPauseMillis=200 -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/opt/tomcat/logs"
```

---

**Monitoring**
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

**Deployment & Lifecycle**

| Step          | Action |
|---------------|--------|
| Build         | Produce a WAR via Maven or Gradle |
| Scan          | Run SAST/DAST and dependency vulnerability checks (e.g., OWASP Dependency-Check) |
| Stage         | Copy WAR to `webapps/` or use the `/manager/text/deploy` endpoint |
| Validate      | Check a health endpoint (`/health` or a custom servlet) after deployment |
| Traffic Shift | Use a reverse proxy or load balancer to drain the old instance before cutting over |
| Rollback      | Keep the previous WAR versioned (e.g., `app-1.4.2.war`) for quick rollback |

CLI Manager (requires `manager-script` role):
```bash
curl -u admin:devops "http://10.10.5.4:5080/manager/text/list"
curl -u admin:devops "http://10.10.5.4:5080/manager/text/deploy?path=/app&war=file:/opt/releases/app-1.4.2.war"
curl -u admin:devops "http://10.10.5.4:5080/manager/text/undeploy?path=/app"
```

Zero-Downtime Strategy:
- **Blue/green:** Run `app-v1` and `app-v2` as separate context paths behind a proxy that rewrites the route at cutover.
- **Rolling instance replacement:** Pre-deploy to a new Tomcat instance, then deregister the old instance from the load balancer once the new one is healthy.

---

**Logging & Diagnostics**
- Default log files:
  - `catalina.out`   JVM stdout/stderr; rotate externally (it does not self-rotate)
  - `localhost_access_log*.txt`   access log
  - `localhost.yyyy-MM-dd.log`   per-host application log
  - `manager.yyyy-MM-dd.log`   Manager App activity

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

Heap dump (triggered automatically on OOM with the JVM flag `-XX:+HeapDumpOnOutOfMemoryError`):
Analyse the resulting `.hprof` file with Eclipse MAT or VisualVM.

---

**Reverse Proxy Integration**
- Nginx sample:
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

For Tomcat to trust the forwarded headers and issue correct redirects and secure cookie flags, add `RemoteIpValve` inside `<Engine>` or `<Host>` in `server.xml`:
```xml
<Valve className="org.apache.catalina.valves.RemoteIpValve"
       internalProxies="127\.0\.0\.1"
       remoteIpHeader="X-Forwarded-For"
       protocolHeader="X-Forwarded-Proto" />
```

---

**Session Management & Scalability**

| Strategy            | Description | Trade-offs |
|---------------------|-------------|------------|
| Sticky Sessions     | Load balancer always routes a user to the same node | Simple; session is lost if that node fails |
| Session Replication | Delta or full session replication between cluster nodes | Higher memory and network overhead; built into Tomcat clustering |
| External Store      | Redis / Memcached via a custom session Manager | Decouples session state from the JVM; adds network latency per request |
| Stateless (Token)   | JWT/OAuth2 tokens; minimal or no server-side session | Cleanest approach for scaling; requires refactoring legacy session-based apps |

For horizontal scaling, prefer an external session store or a fully stateless design.

---

**Comparison: Tomcat vs Alternatives**

| Feature          | Tomcat | Jetty | Undertow | Full EE (WildFly) |
|------------------|--------|-------|----------|-------------------|
| Footprint        | Small  | Smaller | Very small | Larger |
| Async Support    | Yes (Servlet 3.1+) | Strong | Strong | Yes |
| WebSocket        | Yes    | Yes   | Yes      | Yes |
| HTTP/2           | Yes (config required) | Yes | Yes | Yes |
| Jakarta EE Full  | No     | No    | No       | Yes |
| Embedded Mode    | Yes (native `tomcat-embed-core` API; also via Spring Boot) | Native | Native | Not typical |
| Startup Speed    | Fast   | Faster | Very fast | Moderate |

---
