# Apache Maven

---

Maven is an open source build automation and project management tool originally designed for Java projects, though it has since been adopted across many JVM-based ecosystems. At its core, Maven revolves around something called the **Project Object Model** (POM); an XML file that describes your project, its dependencies, and how it should be built.

One of the things that makes Maven stand out is its philosophy of **"convention over configuration."** Rather than forcing you to spell out every detail of your build, Maven assumes a standard project layout and provides sensible defaults. If you follow its conventions, you can get a working build with very little configuration. Here's what Maven brings to the table:

- **Reproducible builds**:

  Given the same source and configuration, Maven produces the same output every time. No more "it works on my machine" surprises.

- **A standard lifecycle**:

  Maven defines a clear sequence of phases: `validate`, `compile`, `test`, `package`, `verify`, `install`, and `deploy`. Every Maven project follows this flow.

- **Automatic dependency resolution**:

  You declare what libraries you need, and Maven figures out the rest, including transitive dependencies (the libraries your libraries depend on).

- **Plugin based architecture**:

  Compilation, testing, packaging, reporting, and even site generation are all handled by plugins. If Maven doesn't do something out of the box, there's likely a plugin for it.

- **Smooth CI/CD integration**:

  Maven plays well with Jenkins, GitLab CI, GitHub Actions, and artifact repositories like Nexus and Artifactory. It also integrates with quality and security scanners without much fuss.

---

> **Mnemonic**: Maven = Model + Lifecycle + Plugins + Dependencies

---

### Why Maven?

To appreciate what Maven does, it helps to think about what life looked like before it existed.


**Complex build processes** were the norm. Developers had to manually compile source files, manage classpaths, and package everything together. Each project had its own ad hoc build scripts, which were often fragile and hard to maintain.


**Dependency management was a nightmare.** Teams would check JAR files directly into version control or pass them around on shared drives. Figuring out which version of a library a project actually needed and whether it conflicted with another library was a tedious, error prone exercise. People called it "dependency hell" for good reason.


**There was no standardization.** Walk into a new project, and you'd find a completely different directory structure, a different build tool, and a different set of conventions. Onboarding took longer than it should have.


Maven addressed all of this by providing Java developers with a common project structure, a declarative way to specify dependencies, and a single, consistent command line interface for building any project. Once you learn Maven, you can walk into almost any Maven based project and know where things are and how to build it.

---

### Concepts & Terminology

Before diving deeper, let's get comfortable with the vocabulary Maven uses. These terms come up constantly.

**POM (pom.xml)**:

This is the heart of every Maven project. The POM is an XML file that sits at the root of your project and tells Maven everything it needs to know: what your project is called, what it depends on, which plugins to use, and how to build it. Think of it as the single source of truth for your project's build configuration.

**Coordinates (GAV)**:

Three pieces of information identify every artifact in the Maven ecosystem, often referred to as GAV coordinates:

- **GroupId**:
  
    Identifies the organization or group that created the project. It typically follows reverse domain naming, like `com.company.project`.
  
- **ArtifactId**:
  
    The name of the specific project or module, such as `data-service`.
  
- **Version**:
  
    The version number, like `1.0.0` or `1.0.0-SNAPSHOT` (where SNAPSHOT indicates a development version that's still in progress).

Together, these three values uniquely identify any artifact in the Maven universe.



**Dependencies**:

These are the external libraries your project needs. Instead of downloading JARs manually and dropping them into a `lib/` folder, you declare them in your POM. Maven takes care of downloading them, storing them locally, and making them available on your classpath. It even resolves transitive dependencies; if library A depends on library B, Maven will pull in both.



**Dependency Scopes**:

Not all dependencies are needed at the same time. Maven uses scopes to control when a dependency is available on the classpath and whether it gets packaged into the final artifact:


| Scope | Available at compile | Available at test | Packaged in artifact | Example use case |
|-------|---------------------|------------------|----------------------|-----------------|
| `compile` (default) | Yes | Yes | Yes | Core libraries like Apache Commons |
| `provided` | Yes | Yes | No | Servlet API: the app server provides it |
| `runtime` | No | Yes | Yes | JDBC drivers: only needed at runtime |
| `test` | No | Yes | No | JUnit, Mockito: test only |
| `system` | Yes | Yes | No | JARs on the local filesystem (rarely used) |




**Repositories**:

Maven uses a layered repository system:

- **Local repository**: A folder on your machine, usually at `~/.m2/repository`. Every artifact Maven downloads gets cached here, so it doesn't have to fetch it again.
  
- **Central repository**: The default public repository maintained by the Maven community. It hosts the vast majority of open source Java libraries.
  
- **Remote repository**: A private or corporate repository, often running Sonatype Nexus or JFrog Artifactory. Companies use these to host proprietary artifacts and to proxy the central repository for better control and performance.


---

**Build Lifecycle and Goals**:

A lifecycle is a predefined sequence of phases that Maven executes in order. A goal is a specific task, like compiling code or running tests, that gets bound to a phase and executed by a plugin. When you run `mvn test`, Maven walks through every phase up to and including `test`, executing the goals bound to each one along the way.


**Maven Build Lifecycle**


Maven defines three built-in lifecycles, but the one you'll use most often is the default lifecycle. Here are its phases, in order:

1. **validate**: Checks that the project is set up correctly and the POM is valid.

2. **compile**: Compiles the project's source code into bytecode.

3. **test**: Runs unit tests against the compiled code using a framework like JUnit. The code doesn't need to be packaged for this step.

4. **package**: Takes the compiled code and bundles it into a distributable format, typically a JAR or WAR file.

5. **verify**: Runs integration tests and other checks to make sure the package meets quality standards.

6. **install**: Copies the package into your local Maven repository (`~/.m2/repository`), making it available as a dependency for other projects on the same machine.

7. **deploy**: Uploads the final package to a remote repository so that other developers and projects can use it.



**There are two other lifecycles worth knowing about:**


- **Clean lifecycle**: `pre clean` > `clean` > `post clean`. The `clean` phase deletes the `target/` directory, wiping out previous build outputs. You'll often run `mvn clean` before a fresh build.

- **Site lifecycle**: `pre site` > `site` > `post site` > `site deploy`. This generates project documentation and can publish it to a web server.

One thing that catches newcomers off guard: running a later phase automatically triggers all earlier phases. So `mvn package` doesn't just package your code, it first runs `validate`, then `compile`, then `test`, and only then `package`. This is by design and ensures nothing gets skipped.


---


### Fundamental Maven Commands

Here are the commands you'll reach for most often.

**Core Build Commands**
```
mvn clean                        # Delete the target/ directory (previous build outputs)
mvn compile                      # Compile the source code
mvn test                         # Run unit tests
mvn package                      # Build the artifact (JAR or WAR)
mvn verify                       # Run integration tests and quality checks
mvn install                      # Install the artifact to your local ~/.m2/ repository
mvn deploy                       # Upload the artifact to a remote repository
```

Flags:
```
mvn -DskipTests package          # Skip running tests, but still compile them
mvn -DskipITs verify             # Skip integration tests specifically
mvn -T 1C clean package          # Run a parallel build using 1 thread per CPU core
mvn -U clean package             # Force Maven to check for updated SNAPSHOT dependencies
mvn -Pprod package               # Activate a profile named 'prod'
mvn -Denv=prod package           # Pass a system property for property-based profile activation
```


**Maven Wrapper**:

The Maven Wrapper lets you pin a specific Maven version to your project, so everyone on the team (and your CI server) uses the same version regardless of what's installed globally. The official command to add it to your project is:

```bash
mvn wrapper:wrapper              # Generate the ./mvnw script using the current Maven version
```
```bash
./mvnw clean package             # Build using the project pinned Maven version
```


> The older `mvn -N io.takari:maven:wrapper` command was from the Takari wrapper plugin, which is no longer actively maintained. The `mvn wrapper:wrapper` command from the official Apache Maven Wrapper Plugin is the current approach.



**Utility Commands**:
```
mvn dependency:tree                       # Print the full dependency graph
mvn help:effective-pom                    # Show the fully resolved POM (including inherited settings)
mvn versions:display-dependency-updates   # Check if any dependencies have newer versions
mvn versions:display-plugin-updates       # Check if any plugins have newer versions
```

---

> Prerequisites: Create a new Virtual Machine named `Java Developer`

---

### Installation & Configuration

These instructions are written for **Fedora, RHEL, or CentOS** using the `dnf` package manager. If you're on a different distribution, the package names and commands may vary slightly, but the overall process is the same.

**Prerequisites: Java (JDK 11+)**

**Step 1: Install Java**

Maven requires a JDK (Java Development Kit) to run. Version 11 or higher is required, though JDK 21 is a solid choice for modern projects.

```bash
sudo dnf -y install java-*-openjdk java-*-openjdk-devel
```
```
java --version
```
---

<img width="865" height="116" alt="Screenshot 2026-03-12 at 12 02 24 PM" src="https://github.com/user-attachments/assets/0dc63bb8-f596-4331-bae0-f6f59d23b818" />

---

### Step 2: Find the JDK Path and Set `JAVA_HOME`

After installation, you need to figure out where the JDK was installed so you can set the `JAVA_HOME` environment variable. Maven (and many other tools) rely on this variable to locate the JDK.

```bash
cd /usr/lib/jvm
```
```bash
ls
```
```bash
cd java-21-openjdk
```
```bash
pwd
```
> You should see something like: `/usr/lib/jvm/java-21-openjdk`

---
<img width="801" height="75" alt="Screenshot 2026-03-19 at 8 42 21 AM" src="https://github.com/user-attachments/assets/7d14aead-fdab-447d-8635-403bdd479454" />

---

```bash
cd
```

Now set it system wide by editing `/etc/profile` (or use `~/.bashrc` if you only want it for your user):

```bash
sudo vim /etc/profile
```

Add these lines at the end:

```bash
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk
export PATH="$PATH:$JAVA_HOME/bin"
```

Apply the changes and verify:

```bash
source /etc/profile
```
```bash
echo $JAVA_HOME
```
```bash
which java
```
---
<img width="865" height="266" alt="Screenshot 2026-03-12 at 12 05 21 PM" src="https://github.com/user-attachments/assets/a696d2eb-0523-4163-bbcf-4b172715923b" />

---

### Step 3: Install Maven

You have two options here.

**Option A: Use the package manager.** 

This is the simplest approach, though you may not get the latest version.

```bash
sudo dnf info maven
```
```bash
sudo dnf -y install maven
```
```bash
mvn --version
```
---
<img width="745" height="117" alt="Screenshot 2026-03-19 at 9 22 21 AM" src="https://github.com/user-attachments/assets/aebd5f13-283f-46f2-9ab1-8ced3e4c11dc" />

---

Then set the environment variables by adding these lines to `/etc/profile`:

```bash
sudo vim /etc/profile
```

```bash
export M2_HOME=/usr/share/maven
export PATH="$PATH:$M2_HOME/bin"
```

```bash
source /etc/profile
```

```bash
echo $M2_HOME
```
---
<img width="744" height="76" alt="Screenshot 2026-03-19 at 9 27 52 AM" src="https://github.com/user-attachments/assets/e1b8cfbd-98e6-4ecc-8b51-7e476e36b263" />

---

**Option B: Download the latest binary directly.** 

This is the recommended approach if you want a specific or the most recent version. Check [Maven's download page](https://maven.apache.org/download.cgi) for the latest link.

---
<img width="1137" height="383" alt="Screenshot 2026-03-20 at 11 35 32 AM" src="https://github.com/user-attachments/assets/9a667597-f632-481c-af1f-16c7d55809b3" />

> Copy Link Address
---

```bash
cd /tmp
```
```bash
sudo wget https://dlcdn.apache.org/maven/maven-3/3.9.15/binaries/apache-maven-3.9.15-bin.tar.gz
```
```bash
sudo tar -zxvf apache-maven-*-bin.tar.gz
```
```bash
sudo mv apache-maven-3.9.* /opt/maven
```

---
<img width="827" height="138" alt="Screenshot 2026-03-12 at 12 11 05 PM" src="https://github.com/user-attachments/assets/eef57b9c-6b4c-4ef8-8ae7-1e75a90fb933" />

---

```
cd
```

Then set the environment variables by adding these lines to 

`sudo vim /etc/profile`

```bash
export M2_HOME=/opt/maven
export PATH="$PATH:$M2_HOME/bin"
```

Apply and confirm everything is working:

```bash
source /etc/profile
```
```bash
mvn --version
```
If you see Maven's version info along with the Java version and OS details, you're good to go.

---
<img width="860" height="156" alt="Screenshot 2026-03-12 at 12 14 01 PM" src="https://github.com/user-attachments/assets/7dfca661-9b75-4bb0-b55b-a91b4457771e" />

---

Optionally, you can create a dedicated system user to own the Maven installation. This is a good practice for shared servers:

```bash
sudo groupadd maven
```
```bash
sudo useradd -g maven -d /opt/maven -s /sbin/nologin maven
```
```bash
sudo chown -R maven:maven /opt/maven
```


> **Note:** The `mvn` file inside Maven's `bin/` directory isn't a compiled binary — it's a shell script. It sets up the necessary environment variables and classpath, then launches Maven's core Java class. This is why `JAVA_HOME` needs to be set correctly.

---

### Configuring Maven's Global Settings: `settings.xml` for Enterprise and CI/CD Environments

`settings.xml` is Maven's machine wide preferences file, it controls how Maven behaves across every project on that machine, unlike `pom.xml` which travels with a specific project.

Its most common enterprise use is redirecting dependency downloads away from the public Maven Central to an internal Nexus or Artifactory server, giving you faster downloads, security vetted libraries, and protection against dependencies disappearing upstream.

It lives in two places: user level at `~/.m2/settings.xml` and global at `${M2_HOME}/conf/settings.xml`. The user level file takes precedence, and you simply create it if it doesn't exist.

In CI/CD pipelines, each build server gets its own `settings.xml` with its own credentials and routing rules,  completely separate from a developer's local setup.

- **User Specific**: `~/.m2/settings.xml` (applies only to you)
```
sudo cat ~/.m2/settings.xml
```
- **Global**: `${M2_HOME}/conf/settings.xml` (applies to all users on the machine)
```
sudo cat ${M2_HOME}/conf/settings.xml
```


Here's a practical `settings.xml` that covers the most common DevOps needs:

```xml
<settings xmlns="http://maven.apache.org/SETTINGS/1.2.0"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.2.0
                              https://maven.apache.org/xsd/settings-1.2.0.xsd">

  <!-- Where Maven stores downloaded artifacts locally -->
  <localRepository>/opt/maven-repo</localRepository>

  <!-- Mirror: intercepts ALL repository requests and routes to internal Nexus -->
  <mirrors>
    <mirror>
      <id>nexus</id>
      <mirrorOf>*</mirrorOf>
      <url>https://nexus.company.com/repository/maven-public/</url>
    </mirror>
  </mirrors>

  <!-- Server credentials for deploying to private repositories -->
  <!-- BEST PRACTICE: Never store plaintext passwords here.    -->
  <!-- Use Maven password encryption (`mvn --encrypt-password`)-->
  <!-- or inject via CI/CD environment variables at build time -->
  <servers>
    <server>
      <id>nexus-releases</id>
      <username>deployer</username>
      <password>${env.NEXUS_PASSWORD}</password>  <!-- injected at runtime -->
    </server>
    <server>
      <id>nexus-snapshots</id>
      <username>deployer</username>
      <password>${env.NEXUS_PASSWORD}</password>  <!-- injected at runtime -->
    </server>
  </servers>

  <!-- Profile defining your internal release and snapshot repositories -->
  <profiles>
    <profile>
      <id>nexus</id>
      <repositories>
        <repository>
          <id>nexus-releases</id>
          <url>https://nexus.company.com/repository/maven-releases/</url>
          <releases><enabled>true</enabled></releases>
          <snapshots><enabled>false</enabled></snapshots>
        </repository>
        <repository>
          <id>nexus-snapshots</id>
          <url>https://nexus.company.com/repository/maven-snapshots/</url>
          <releases><enabled>false</enabled></releases>
          <snapshots><enabled>true</enabled></snapshots>
        </repository>
      </repositories>
    </profile>
  </profiles>

  <!-- Automatically activate the nexus profile for all builds -->
  <activeProfiles>
    <activeProfile>nexus</activeProfile>
  </activeProfiles>

</settings>
```

> In CI environments like Jenkins, place this file at `~/.m2/settings.xml` on the build server, or inject it as a managed file using the Config File Provider plugin.

---

### Project Structure & Creation

**The Default Directory Layout**

One of Maven's biggest advantages is its standardized directory structure. Every Maven project follows the same layout, which means once you've seen one, you can navigate any of them:

```
project-root/
├── pom.xml                                # The project's build configuration: dependencies, plugins, and metadata
├── src/
│   ├── main/
│   │   ├── java/                          # Your production source code goes here: compiled into the final artifact
│   │   ├── resources/                     # Configuration files, properties, etc.: copied as-is to the classpath
│   │   └── webapp/                        # Web assets (JSPs, HTML, WEB-INF): for WAR projects only, not in JARs
│   └── test/
│       ├── java/                          # Your test source code goes here: compiled and run by Maven's test phase, excluded from final artifact
│       └── resources/                     # Test specific configuration files: available on classpath during testing only
└── target/                                # Maven's output directory: generated at build time, never committed to source control
    ├── classes/                           # Compiled .class files from src/main/java and copied resources from src/main/resources
    ├── test-classes/                      # Compiled .class files from src/test/java and copied resources from src/test/resources
    └── <artifact>.jar or <artifact>.war   # The final packaged artifact: ready for deployment or distribution
```

The `target/` directory is where Maven puts everything it generates: compiled classes, test results, and the final artifact. You should never check this directory into version control.

---

## Maven Archetypes

A Maven archetype is a project template that generates a ready to use project structure so you don't have to create folders and boilerplate files manually. It enforces a consistent project structure across teams, saves setup time, and one command gives you a working skeleton

- Basic usage
```bash
mvn archetype:generate
```

Maven will prompt you to pick a template and fill in your project details (groupId, artifactId, version).

- Common archetypes:

| Archetype | What it generates |
|---|---|
| `maven-archetype-quickstart` | Basic Java project with `src/main` and `src/test` |
| `maven-archetype-webapp` | Java web application with `WEB-INF` and `web.xml` |
| `maven-archetype-site` | Project documentation site |

---

### Creating a New Project

Maven provides archetypes, essentially project templates, to framework new projects quickly.

**Creating a Web Application**

**Example 1:**

```bash
mkdir -p ~/sampleapp
```
```bash
cd ~/sampleapp
```
```
mvn archetype:generate \
  -DgroupId=com.devopsclass \
  -DartifactId=sample-app \
  -DarchetypeArtifactId=maven-archetype-webapp \
  -DinteractiveMode=false
```
Let's break down what each parameter does:
- `-DgroupId=com.devopsclass`: Sets the base package name using reverse domain notation
- `-DartifactId=sample-app`: Names the project and creates the root directory
- `-DarchetypeArtifactId=maven-archetype-webapp`: Tells Maven to use the web application template
- `-DinteractiveMode=false`: Skips the interactive prompts and uses the provided values directly

This creates a basic web application structure with a `pom.xml` configured for WAR packaging. You can inspect what was generated:
```bash
tree sample-app
```

<img width="856" height="238" alt="Screenshot 2026-03-12 at 12 22 26 PM" src="https://github.com/user-attachments/assets/91d09a6b-70ba-41e7-abf1-103cc9f170dd" />

```bash
cd sample-app
```
```bash
ls
```
> You'll see: pom.xml  src/

> **`pom.xml`**: The project's brain. It tells Maven what dependencies to download, what plugins to use, and how to build the project

> **`src/`**: The project's source. It holds all your production code under `main/` and test code under `test/`

```bash
ls src/main/webapp
```
> You'll see: index.jsp — your code lives in this file.
```bash
sudo vim index.jsp
```
```html
<html>
<body>
<h2>DevOps: Breaking Down Silos!</h2>
</body>
</html>
```
```
cd
```

We will compile, package, and test this code locally later.

---

**Traditional Spring vs Spring Boot**

| Feature              | Traditional Spring Framework | Spring Boot                       |
| -------------------- | ---------------------------- | --------------------------------- |
| Configuration        | Manual XML/Java config       | Auto configured                   |
| Server setup         | External (Tomcat, JBoss)     | Embedded (Tomcat, Jetty)          |
| Startup complexity   | High                         | Minimal                           |
| Production readiness | Manual setup                 | Built in (metrics, health checks) |


---
**Spring Boot**

Spring Boot is a Java framework that simplifies building production ready applications, designed to eliminate the complex XML configuration and boilerplate setup that traditional Spring required.

Plain Spring requires manual configuration for everything: beans, servers, and data sources. Spring Boot uses auto configuration and sensible defaults, so you get a working application with minimal setup. It embeds the server (Tomcat by default) directly into the JAR, so there's nothing extra to deploy.

**Why it matters for DevOps?**

It packages as a single runnable JAR, includes built in health and metrics endpoints, supports Docker and Kubernetes well, and benefits from a large enterprise ecosystem.

**Creating a Spring Boot Application**

Spring Boot projects aren't typically created through Maven archetypes. Instead, the community uses Spring Initializr, which you can access through a web browser or the command line:

**Example 2:**

```
mkdir -p ~/myproject
```

```
cd ~/myproject
```

Download a Spring Boot starter project from the Spring Initializr web service:

```
curl -sSL --fail \
  "https://start.spring.io/starter.zip?type=maven-project&language=java&groupId=com.example&artifactId=demo&name=demo&packaging=jar&javaVersion=21&dependencies=web" \
  -o demo.zip
```

The `-sSL --fail` flags tell `curl` to run in silent mode, follow redirects, and return an error if something goes wrong, rather than silently downloading an error page.

```
unzip demo.zip -d .
```

```
rm demo.zip
```

```
cd
```

```
tree myproject
```
---
<img width="802" height="486" alt="Screenshot 2026-03-12 at 12 37 11 PM" src="https://github.com/user-attachments/assets/5c8163bd-fdc9-437d-bdeb-04f239353736" />

---

>`pom.xml`: The project's brain. It tells Maven what dependencies to download, what plugins to use, and how to build the project.

>`src/`: The project's source. It holds all your production code under `main/` and test code under `test/`.

```
ls myproject/src/main/java/com/example/demo
```

> You'll see: `DemoApplication.java`, your application's entry point. This is where Spring Boot starts.

```
cat myproject/src/main/java/com/example/demo/DemoApplication.java
```

```java
package com.example.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
```

`@SpringBootApplication`: Marks this as the entry point and enables Spring Boot's auto-configuration.

`SpringApplication.run()`: Bootstraps the application, starts the embedded Tomcat server, and begins listening for requests.


**Add a simple REST controller:**

```bash
cd myproject
```

```bash
vim src/main/java/com/example/demo/HelloController.java
```

```java
package com.example.demo;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloController {

    @GetMapping("/")
    public String home() {
        return "<h2>Example 2: DevOps-Breaking Down Silos!</h2>";
    }
}
```

>`@RestController`: Marks this class as a web controller that returns data directly to the browser.

>`@GetMapping("/")`: Maps HTTP GET requests on `/` to this method.


```
cd ~/myproject
```

- Compile and package:
```
./mvnw clean package -DskipTests
```

- Run
```
java -jar target/demo-0.0.1-SNAPSHOT.jar
```

Now open the browser and visiting `http://localhost:8080` will return:

---
<img width="1017" height="296" alt="Screenshot 2026-05-15 at 12 18 17 PM" src="https://github.com/user-attachments/assets/2861906a-2dd6-4f93-b6db-b73758403c37" />

---

- Stop
```
Ctrl + C
```

---

**Example 3:** 

Downloads a preconfigured Spring Boot project as a ZIP file from Spring Initializr, specifying a particular Spring Boot version:

```bash
mkdir -p ~/myproject3
```

```bash
cd ~/myproject3
```

```bash
curl -sSL \
  "https://start.spring.io/starter.zip?type=maven-project&language=java&bootVersion=3.5.0&groupId=com.example&artifactId=demo&name=demo&packaging=jar&javaVersion=21&dependencies=web" \
  -o demo.zip
```

>Explanation:
>
>curl https://start.spring.io/starter.zip   # Spring Initializr API: generates and downloads a zipped project
>
>  -d type=maven-project                    # Build tool: use Maven (alternatively: gradle-project)
>
>  -d language=java                         # Language: Java (alternatively: kotlin, groovy)
>
>  -d bootVersion=3.5.0                     # Spring Boot version to use
>
>  -d groupId=com.example                   # Your organization's namespace (reverse domain)
>
>  -d artifactId=demo                       # Your project's name and folder name
>
>  -d name=demo                             # Display name of the application
>
>  -d packaging=jar                         # Output format: jar (runnable) or war (for app servers)
>
>  -d javaVersion=21                        # Java version to compile against
>
>  -d dependencies=web                      # Starter dependencies: web adds Spring MVC + embedded Tomcat
>
>  -o demo.zip                              # Save the downloaded zip as demo.zip locally


```bash
unzip demo.zip -d .
```

```bash
rm demo.zip
```

```bash
tree .
```

You'll see:

---
<img width="798" height="521" alt="Screenshot 2026-05-15 at 12 39 28 PM" src="https://github.com/user-attachments/assets/f98d61e5-4777-4b88-979d-11ea6867bf3e" />


---

**Add a REST controller:**

```bash
vim src/main/java/com/example/demo/HelloController.java
```

```java
package com.example.demo;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloController {

    @GetMapping("/")
    public String home() {
        return "<h2>Example 3: DevOps - Breaking Down Silos!</h2>";
    }
}
```

- Build and run

```bash
./mvnw clean package -DskipTests
```

```bash
java -jar target/demo-0.0.1-SNAPSHOT.jar
```

Now open the browser and visiting `http://localhost:8080` will return:

---
<img width="770" height="276" alt="Screenshot 2026-05-15 at 12 41 06 PM" src="https://github.com/user-attachments/assets/bbec38ef-f937-433a-9039-ad09b4413449" />

---

- Stop:
```
Ctrl + C
```

---

**Differences:**

| Aspect | Example 2 (GET) | Example 3 (POST) |
|--------|-----------------|------------------|
| **HTTP Method** | GET | POST |
| **Parameters** | URL query string | Form data (-d flags) |
| **Flags** | `-sSL --fail` | None |
| **Spring Boot Version** | Default/latest | Specific: 3.3.4 |
| **URL Length** | Very long | Short and clean |
| **Error Handling** | `--fail` (fail on HTTP errors) | Default behavior |
| **Silent Mode** | `-s` (silent) | Shows progress |
| **Redirects** | `-L` (follow redirects) | Default behavior |


**Which to use:**

Example 2: When you want the latest Spring Boot version
  
Example 3: When you need a specific Spring Boot version (better for reproducible builds in DevOps)

> Both produce the same project structure, just potentially different Spring Boot versions.

---

**Quarkus**

Quarkus is a Java framework built for containers and cloud native environments, designed to solve Java's two biggest pain points in modern infrastructure: slow startup times and high memory consumption.

Traditional frameworks like Spring Boot do heavy lifting at runtime (classpath scanning, bean wiring, config loading). Quarkus shifts most of that work to build time, so apps start in milliseconds and use far less memory.

**Why it matters for DevOps?**

Run Java apps more efficiently with smaller containers, near instant pod startup, lower cloud spend, and familiar enterprise standards.

**Creating a Quarkus Application**

Quarkus has its own Maven plugin for project generation:

```bash
mkdir -p ~/NewProject
```

```bash
cd ~/NewProject
```

```bash
mvn io.quarkus:quarkus-maven-plugin:3.15.0:create \
  -DprojectGroupId=com.NewProject \
  -DprojectArtifactId=quarkus-app \
  -DclassName="com.NewProject.GreetingResource" \
  -Dpath="/hello"
```

Let's break down what each parameter does:

- `io.quarkus:quarkus-maven-plugin:3.15.0:create`: Runs Quarkus's project generation plugin at version 3.15.0
- `-DprojectGroupId=com.NewProject`: Your organization's namespace
- `-DprojectArtifactId=quarkus-app`: Project name and root directory
- `-DclassName="com.NewProject.GreetingResource"`: Generates a sample REST resource class at this fully qualified name
- `-Dpath="/hello"`: Maps the generated REST endpoint to `/hello`

This generates a ready-to-run Quarkus project with a sample REST endpoint at `/hello`.

```bash
cd
```

```bash
tree NewProject
```
---
<img width="801" height="420" alt="Screenshot 2026-05-15 at 12 51 06 PM" src="https://github.com/user-attachments/assets/80554c01-2116-464c-af52-33991104107e" />

---

```bash
cat NewProject/quarkus-app/src/main/java/com/NewProject/GreetingResource.java
```

You'll see:

```java
package com.NewProject;

import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;

@Path("/hello")
public class GreetingResource {

    @GET
    @Produces(MediaType.TEXT_PLAIN)
    public String hello() {
        return "Hello from Quarkus REST";
    }
}
```

>`@Path("/hello")`: Maps this class to the `/hello` endpoint.

>`@GET`: Handles HTTP GET requests.

>`@Produces(MediaType.TEXT_PLAIN)`: Returns plain text response.

**Build and run:**

```bash
cd NewProject/quarkus-app
```
```bash
./mvnw clean package -DskipTests
```
```bash
java -jar target/quarkus-app/quarkus-run.jar
```

**Test:**

Now open the browser and visiting `http://localhost:8080/hello` will return:

---
<img width="772" height="227" alt="Screenshot 2026-05-15 at 12 55 35 PM" src="https://github.com/user-attachments/assets/ddbca718-b35c-421d-9659-95ee77ee1d5a" />

---

- Stop:

```
Ctrl + C
```

> Note: Unlike Spring Boot, which packages into a single fat JAR, Quarkus outputs a `quarkus-app/` directory containing `quarkus-run.jar` and supporting libraries.


**Spring Boot vs Quarkus:**

| | Spring Boot | Quarkus |
|---|---|---|
| Startup time | Seconds | Milliseconds |
| Memory usage | Higher | Significantly lower |
| Native compilation | Limited | First-class via GraalVM |
| Best for | Enterprise & monoliths | Microservices & serverless |

---
---

**Multi Module Projects**

In real enterprise environments, applications aren't built as a single module. You'll typically encounter a multi module Maven project, where a parent POM coordinates several sub projects (modules) that may depend on each other.

This is an important DevOps concept because your CI/CD pipeline must understand the module structure to build and deploy components independently or together.

**Typical structure:**
```
my-app/
├── pom.xml                   # Parent POM: defines shared dependencies, versions, and plugins inherited by all child modules
├── my-app-api/               # Shared interfaces/models: contracts and data structures used across all modules
│   └── pom.xml               # Module POM: declares this as a child of the parent and defines API specific dependencies
├── my-app-service/           # Business logic: core application logic, depends on my-app-api for interfaces and models
│   └── pom.xml               # Module POM: declares this as a child of the parent and defines service-specific dependencies
└── my-app-web/               # Web layer: handles HTTP requests and responses, depends on my-app-service for business logic
    └── pom.xml               # Module POM: declares this as a child of the parent and defines web-specific dependencies
```

**Parent POM** (at the root):

```xml
<project>
  <modelVersion>4.0.0</modelVersion>                        <!-- Maven POM schema version, always 4.0.0 -->
  <groupId>com.devopsclass</groupId>                        <!-- Organization namespace in reverse domain notation -->
  <artifactId>my-app</artifactId>                           <!-- Root project name, becomes the parent identifier -->
  <version>1.0.0</version>                                  <!-- Project version, inherited by all child modules -->
  <packaging>pom</packaging>                                <!-- Must be 'pom' for parent: no JAR/WAR is built here -->

  <modules>                                                 <!-- Declares all child modules Maven will build -->
    <module>my-app-api</module>                             <!-- Shared interfaces/models module -->
    <module>my-app-service</module>                         <!-- Business logic module -->
    <module>my-app-web</module>                             <!-- Web layer module -->
  </modules>

  <properties>                                              <!-- Shared properties inherited by all child modules -->
    <maven.compiler.release>21</maven.compiler.release>                          <!-- Compile all modules targeting Java 21 -->
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>           <!-- Ensures consistent file encoding across all modules -->
  </properties>

  <dependencyManagement>                                    <!-- Locks dependency versions centrally without pulling them in -->
    <dependencies>
      <dependency>
        <groupId>org.junit.jupiter</groupId>                <!-- JUnit Jupiter: the standard Java testing framework -->
        <artifactId>junit-jupiter</artifactId>              <!-- Child modules declare this without specifying a version -->
        <version>5.12.1</version>                           <!-- Version defined once here, enforced across all modules -->
        <scope>test</scope>                                 <!-- Only available during testing, excluded from final artifact -->
      </dependency>
    </dependencies>
  </dependencyManagement>
</project>
```

**Child POM** (e.g., my-app-service/pom.xml):

```xml
<project>
  <modelVersion>4.0.0</modelVersion>                       <!-- Maven POM schema version, always 4.0.0 -->

  <parent>                                                  <!-- Declares this module as a child of the parent POM -->
    <groupId>com.devopsclass</groupId>                      <!-- Must match the parent's groupId exactly -->
    <artifactId>my-app</artifactId>                         <!-- Must match the parent's artifactId exactly -->
    <version>1.0.0</version>                                <!-- Must match the parent's version exactly -->
  </parent>

  <artifactId>my-app-service</artifactId>                  <!-- This module's name: inherits groupId and version from parent -->

  <dependencies>                                            <!-- Dependencies specific to this module -->
    <dependency>
      <groupId>com.devopsclass</groupId>                    <!-- Same organization: this is an internal module dependency -->
      <artifactId>my-app-api</artifactId>                   <!-- Depends on the api module for shared interfaces and models -->
      <version>${project.version}</version>                 <!-- Reuses parent's version: keeps all modules in sync automatically -->
    </dependency>
  </dependencies>
</project>
```

**Build everything from the root:**

Runs the full build across all modules in the correct order: `my-app-api` first, then `my-app-service`, then `my-app-web`. Maven resolves the dependency chain automatically, so each module is built only after what it depends on is ready.

```bash
cd my-app
```
```bash
mvn clean package
```

**Build a single module and its dependencies:**



```bash
mvn clean package -pl my-app-service -am
```
**Build everything from the root:**
```bash
cd my-app
mvn clean package
```
Runs the full build across all modules in the correct order — `my-app-api` first, then `my-app-service`, then `my-app-web`. Maven resolves the dependency chain automatically so each module is built only after what it depends on is ready.


**Build a single module and its dependencies:**
```bash
mvn clean package -pl my-app-service -am
```
  - `-pl my-app-service`-Project List: tells Maven to build only this specific module
    
  - `-am`-Also Make: automatically builds any modules that `my-app-service` depends on (in this case `my-app-api`) before building it

> So instead of rebuilding the entire project, you're saying: *"Build only `my-app-service`, but first build anything it needs."* Useful during development when you're working on a specific module and don't want to wait for the full build.

---
---

## The pom.xml

The `pom.xml` is the file that ties everything together. It's where you declare your project's identity, list its dependencies, configure plugins, and define how the project should be built. Every Maven project has one, and understanding it is essential.

**A Minimal Web Application POM**

Here's a clean, working POM for a simple web application:

**Example 1 Continue:**

```bash
cd ~/sampleapp/sample-app
```

```bash
sudo vim pom.xml
```

```xml
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
                             http://maven.apache.org/xsd/maven-4.0.0.xsd">  <!-- XML schema: validates POM structure -->
  <modelVersion>4.0.0</modelVersion>                        <!-- Maven POM schema version, always 4.0.0 -->

  <!-- Project coordinates: uniquely identify this project in any Maven repository -->
  <groupId>com.devopsclass</groupId>                        <!-- Organization namespace in reverse domain notation -->
  <artifactId>sample-app</artifactId>                       <!-- Project name, becomes the final artifact filename -->
  <version>1.0.0</version>                                  <!-- Project version, appended to the artifact filename -->
  <packaging>war</packaging>                                <!-- Output format: WAR for web applications deployed to a server -->

  <name>sample-app</name>                                   <!-- Human readable display name -->
  <description>Sample web application built with Maven</description>  <!-- Brief project description -->

  <!-- Build settings: compiler and encoding applied to all source files -->
  <properties>
    <maven.compiler.release>21</maven.compiler.release>                        <!-- Compile source code targeting Java 21 -->
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>         <!-- Ensures consistent file encoding across all source files -->
  </properties>

  <dependencies>
    <!-- Servlet API: provided by Tomcat at runtime, excluded from the WAR to avoid conflicts -->
    <dependency>
      <groupId>jakarta.servlet</groupId>                    <!-- Jakarta namespace: the modern replacement for javax.servlet -->
      <artifactId>jakarta.servlet-api</artifactId>          <!-- Provides HttpServlet, HttpRequest, HttpResponse interfaces -->
      <version>6.1.0</version>                              <!-- Compatible with Tomcat 11 and Jakarta EE 11 -->
      <scope>provided</scope>                               <!-- Available at compile time but excluded from final WAR -->
    </dependency>

    <!-- JUnit 5: unit testing framework, only needed during the test phase -->
    <dependency>
      <groupId>org.junit.jupiter</groupId>                  <!-- JUnit Jupiter: modern JUnit 5 testing engine -->
      <artifactId>junit-jupiter</artifactId>                <!-- All-in-one JUnit 5 dependency: API, engine, and params -->
      <version>5.12.1</version>                             <!-- Latest stable JUnit 5 version -->
      <scope>test</scope>                                   <!-- Only available during testing, excluded from final WAR -->
    </dependency>
  </dependencies>

  <build>
    <plugins>
      <!-- Surefire: runs unit tests during the test phase -->
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-surefire-plugin</artifactId>      <!-- Default Maven test runner, requires explicit JUnit 5 support -->
        <version>3.5.5</version>                            <!-- Latest stable version with full JUnit 5 compatibility -->
        <configuration>
          <useModulePath>false</useModulePath>              <!-- Disables Java module path to avoid classpath conflicts with JUnit 5 -->
        </configuration>
      </plugin>

      <!-- Jetty: runs the app locally without a full Tomcat install -->
      <plugin>
        <groupId>org.eclipse.jetty.ee10</groupId>           <!-- ee10 namespace: targets Jakarta EE 10 spec -->
        <artifactId>jetty-ee10-maven-plugin</artifactId>    <!-- Embeds Jetty server directly into the Maven build -->
        <version>12.1.8</version>                           <!-- Latest stable Jetty 12 version -->
        <configuration>
          <webApp>
            <contextPath>/sample-app</contextPath>          <!-- URL path to access the app: http://localhost:8080/sample-app -->
          </webApp>
        </configuration>
      </plugin>
    </plugins>
  </build>
</project>
```

---

**Advanced POM Features**

As your projects grow, you'll likely encounter these patterns.

**Parent POM and Dependency Management**

Large organizations often define a parent POM that establishes company-wide standards — compiler settings, plugin versions, coding conventions, and so on. Individual projects inherit from it:

```xml
<parent>
    <groupId>com.mycompany</groupId>
    <artifactId>company-parent-pom</artifactId>
    <version>1.0.0</version>
</parent>
```

**Profiles for Environment-Specific Configuration**

Profiles let you customize the build for different environments — development, staging, production — without maintaining separate POM files:

```xml
<profiles>
  <profile>
    <id>prod</id>
    <properties>
      <app.env>production</app.env>
    </properties>
    <activation>
      <property>
        <name>env</name>
        <value>prod</value>
      </property>
    </activation>
  </profile>
</profiles>
```

You'd activate this profile by running `mvn -Denv=prod package` or `mvn -Pprod package`.

---

**Build & Deployment Workflow**

**Where Maven Fits in the Software Development Lifecycle**

If you think about the typical SDLC — requirements, design, implementation, testing, deployment, and maintenance — Maven primarily supports the implementation through deployment stages. It gives you a consistent, repeatable way to compile code, run tests, produce artifacts, and push them to where they need to go.

**Compiling and Packaging**

All Maven commands should be run from the directory containing your `pom.xml`. The first time you build a project, Maven will download any plugins and dependencies it needs and cache them in `~/.m2/repository`. Subsequent builds are much faster.

**Example 1 Continue:**
```bash
cd ~/sampleapp/sample-app
```

Compile the source code:
```bash
mvn compile
```
Run tests and produce the packaged artifact:
```bash
mvn package
```

Check what was generated:
```bash
ls target/
```

<img width="871" height="87" alt="Screenshot 2026-03-12 at 1 17 18 PM" src="https://github.com/user-attachments/assets/12b4620c-ec2a-4f7c-9847-938f9c44334e" />

**Testing Locally**

For quick local testing without setting up a full Tomcat server, you can use the Jetty plugin (if it's configured in your POM):

```bash
mvn jetty:run
```
Then open http://localhost:8080/sample-app/ in your browser.

<img width="799" height="243" alt="Screenshot 2026-03-20 at 1 03 08 PM" src="https://github.com/user-attachments/assets/0dc9583a-418d-43bf-8221-8d761040c600" />

---

**Deploying the WAR to Tomcat**

Assumptions:
- Tomcat server is powered on and accessible.
- Developer machine has built `target/sample-app.war`.
- Tomcat's `webapps/` directory is on the remote host.
- The default Tomcat HTTP connector is 8080 unless you reconfigure.

```bash
# Copy WAR to remote Tomcat
cd target/
scp sample-app.war cnode@10.10.5.9:~/apache-tomcat-9.0.106/webapps
```

Access the app in a browser (adjust port/context path if configured differently):
```
http://10.10.5.9:8080/sample-app/
# If your Tomcat uses port 5080 per your setup:
# http://10.10.5.9:5080/sample-app/
```

Make changes and redeploy:

```bash
# On developer machine
cd /home/cnode/javaapp/sample-app/src/main/webapp

sudo vim index.jsp
# ...change the content...

cd ../../../
mvn package
cd target
scp sample-app.war cnode@10.10.5.9:~/apache-tomcat-9.0.106/webapps
```

---

**Deploying Artifacts to Nexus/Artifactory**

In a DevOps pipeline, after a successful build you typically push the artifact to a binary repository (Nexus or Artifactory) so other teams and environments can consume it. This is what the `deploy` phase does.

To configure Maven deployment, add a `<distributionManagement>` section to your `pom.xml`:

```xml
<distributionManagement>
  <repository>
    <id>nexus-releases</id>   <!-- Must match the server id in settings.xml -->
    <url>https://nexus.company.com/repository/maven-releases/</url>
  </repository>
  <snapshotRepository>
    <id>nexus-snapshots</id>
    <url>https://nexus.company.com/repository/maven-snapshots/</url>
  </snapshotRepository>
</distributionManagement>
```

Then deploy with:
```bash
mvn clean deploy
```

Maven will use the credentials from your `settings.xml` that match the `<id>` values above.

> **Convention**: SNAPSHOT versions (`1.0.0-SNAPSHOT`) always go to the snapshot repository. Release versions (`1.0.0`) always go to the release repository. This is enforced automatically.

---

**Maven in CI/CD Pipelines**

This is where Maven becomes a core DevOps tool. CI/CD pipelines automate the entire build-test-deploy cycle, and Maven is the engine that drives the Java portion of it.

**Jenkins Declarative Pipeline**

Here's a practical Jenkins pipeline that covers the full lifecycle — from checkout to deployment:

```groovy
pipeline {
    agent any

    tools {
        maven 'Maven-3.9'   // Name configured in Jenkins Global Tool Configuration
        jdk   'JDK-21'
    }

    environment {
        NEXUS_URL = 'https://nexus.company.com'
        APP_NAME  = 'sample-app'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/your-org/sample-app.git'
            }
        }

        stage('Build & Test') {
            steps {
                sh 'mvn clean verify'
            }
            post {
                always {
                    junit '**/target/surefire-reports/*.xml'   // Publish test results
                }
            }
        }

        stage('Code Quality') {
            steps {
                // SonarQube analysis — requires SonarQube plugin in Jenkins
                withSonarQubeEnv('SonarQube') {
                    sh 'mvn sonar:sonar'
                }
            }
        }

        stage('Package') {
            steps {
                sh 'mvn package -DskipTests'
                archiveArtifacts artifacts: 'target/*.war', fingerprint: true
            }
        }

        stage('Deploy to Nexus') {
            when {
                branch 'main'   // Only deploy from main branch
            }
            steps {
                sh 'mvn deploy -DskipTests'
            }
        }

        stage('Deploy to Server') {
            when {
                branch 'main'
            }
            steps {
                sshPublisher(
                    publishers: [sshPublisherDesc(
                        configName: 'tomcat-server',
                        transfers: [sshTransfer(
                            sourceFiles: 'target/*.war',
                            removePrefix: 'target',
                            remoteDirectory: '/apache-tomcat/webapps'
                        )]
                    )]
                )
            }
        }
    }

    post {
        failure {
            mail to: 'team@company.com',
                 subject: "Build Failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                 body: "Check Jenkins: ${env.BUILD_URL}"
        }
    }
}
```

**Key concepts from this pipeline:**

- `mvn clean verify` — runs the full lifecycle through integration tests, giving you the most confidence before deploying.
- `junit '**/target/surefire-reports/*.xml'` — Maven's Surefire plugin writes test results as XML that Jenkins can parse and display.
- `sonar:sonar` — Maven integrates directly with SonarQube for static analysis without extra configuration.
- `mvn deploy -DskipTests` — the `-DskipTests` flag avoids running tests a second time since they already passed in the Build & Test stage.

**GitHub Actions equivalent:**

```yaml
name: Build and Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 21
        uses: actions/setup-java@v4
        with:
          java-version: '21'
          distribution: 'temurin'
          cache: maven          # Caches ~/.m2/repository between runs

      - name: Build and Test
        run: mvn clean verify

      - name: Deploy to Nexus
        if: github.ref == 'refs/heads/main'
        run: mvn deploy -DskipTests
        env:
          MAVEN_USERNAME: ${{ secrets.NEXUS_USERNAME }}
          MAVEN_PASSWORD: ${{ secrets.NEXUS_PASSWORD }}
```

> The `cache: maven` option in GitHub Actions caches your local `.m2` repository between workflow runs, which can cut build times significantly for large projects.

---

**Maven in Docker**

Running Maven builds inside Docker containers gives you a clean, reproducible build environment regardless of what's installed on the host. This is a common pattern in modern DevOps workflows.

**Single-stage build** (simple, straightforward):

```dockerfile
FROM maven:3.9.15-eclipse-temurin-21

WORKDIR /app

# Copy POM first so Docker can cache the dependency layer
COPY pom.xml .
RUN mvn dependency:go-offline -q

# Copy source and build
COPY src ./src
RUN mvn package -DskipTests

CMD ["java", "-jar", "target/sample-app.jar"]
```

**Multi-stage build** (recommended for production — keeps the final image small):

```dockerfile
# Stage 1: Build
FROM maven:3.9.15-eclipse-temurin-21 AS build

WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline -q

COPY src ./src
RUN mvn package -DskipTests

# Stage 2: Runtime — only the JRE, no Maven or source code
FROM eclipse-temurin:21-jre-alpine

WORKDIR /app
COPY --from=build /app/target/sample-app.war ./app.war

EXPOSE 8080
CMD ["java", "-jar", "app.war"]
```

Build and run:
```bash
docker build -t sample-app:1.0 .
docker run -p 8080:8080 sample-app:1.0
```

Why multi-stage? The Maven image is several hundred MB. The JRE Alpine image is under 100 MB. Shipping the smaller image to production is faster and reduces the attack surface.

---

**Troubleshooting**

These are the issues you'll run into most often.

**Build fails on first run with "plugin not found"**

Maven couldn't reach Maven Central or your configured mirror. Check your `settings.xml`, make sure your network can reach the repository, and verify any proxy settings.

```bash
mvn clean package -X 2>&1 | grep "Could not resolve"
```

**"JAVA_HOME is not set" error**

Maven found `java` on your PATH but couldn't find the JDK. Run:
```bash
echo $JAVA_HOME
which java
java -version
```
If `JAVA_HOME` is empty, set it as described in the Installation section and run `source /etc/profile`.

**Dependency conflicts**

Two libraries require different versions of the same transitive dependency. Start by visualizing the tree:
```bash
mvn dependency:tree
```
Use `<exclusion>` to drop the unwanted version and declare the correct version directly in your POM.

**Tests fail only in CI**

The most common cause is environment-specific configuration — file paths, environment variables, or ports that are available locally but not in the CI container. Check `target/surefire-reports/` for the full test output, and run the same Maven command locally with the same environment variables your CI uses.

**"Repository is blocked" in Nexus/Artifactory**

Your artifact repository is blocking access to a dependency. Either the repository isn't proxying Maven Central, or the specific version is on a blocklist. Check your Nexus/Artifactory admin configuration or switch to a version that's available in the repository.

**Out of memory during build**

Large projects with many modules can exhaust Maven's default heap. Set:
```bash
export MAVEN_OPTS="-Xms512m -Xmx2g"
```
Or in CI, pass it as an environment variable in the pipeline definition.
