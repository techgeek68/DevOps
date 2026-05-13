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

- **GroupId**: Identifies the organization or group that created the project. It typically follows reverse domain naming, like `com.company.project`.
  
- **ArtifactId**: The name of the specific project or module, such as `data-service`.
  
- **Version**: The version number, like `1.0.0` or `1.0.0-SNAPSHOT` (where SNAPSHOT indicates a development version that's still in progress).

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


**Common Maven Commands**

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
./mvnw clean package             # Build using the project pinned Maven version
```


> **Note**: The older `mvn -N io.takari:maven:wrapper` command was from the Takari wrapper plugin, which is no longer actively maintained. The `mvn wrapper:wrapper` command from the official Apache Maven Wrapper Plugin is the current approach.



**Utility Commands**:
```
mvn dependency:tree                       # Print the full dependency graph
mvn help:effective-pom                    # Show the fully resolved POM (including inherited settings)
mvn versions:display-dependency-updates   # Check if any dependencies have newer versions
mvn versions:display-plugin-updates       # Check if any plugins have newer versions
```

---

> Prerequisites:
> Create a new Virtual Machine named `Java Developer`

---

**Installation & Configuration**

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

**Step 2: Find the JDK Path and Set `JAVA_HOME`**

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

**Step 3: Install Maven**

You have two options here.

**Option A: Use the package manager.** This is the simplest approach, though you may not get the latest version.

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

**Option B: Download the latest binary directly.** This is the recommended approach if you want a specific or the most recent version. Check [Maven's download page](https://maven.apache.org/download.cgi) for the latest link.

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

Then set the environment variables by adding these lines to `/etc/profile`:

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

**Global Configuration: settings.xml**

While `pom.xml` is project specific, `settings.xml` is where you configure Maven's global behavior; things that apply to all projects on a machine. There are two locations:

- **User level**: `~/.m2/settings.xml` (applies only to you)
  
- **Global**: `${M2_HOME}/conf/settings.xml` (applies to all users on the machine)

The user level file takes precedence. You'll create it if it doesn't already exist.


**Why this matters for DevOps**: In enterprise environments, you almost always need to point Maven at an internal Nexus or Artifactory instance instead of Maven Central. This is where you do that.


Here's a practical `settings.xml` that covers the most common DevOps needs:

```xml
<settings xmlns="http://maven.apache.org/SETTINGS/1.2.0"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.2.0
                              https://maven.apache.org/xsd/settings-1.2.0.xsd">

  <!-- Where Maven stores downloaded artifacts -->
  <localRepository>/opt/maven-repo</localRepository>

  <!-- Mirror: redirect all Central requests to your internal Nexus -->
  <mirrors>
    <mirror>
      <id>nexus</id>
      <mirrorOf>*</mirrorOf>
      <url>https://nexus.company.com/repository/maven-public/</url>
    </mirror>
  </mirrors>

  <!-- Server credentials for deploying to private repositories -->
  <servers>
    <server>
      <id>nexus-releases</id>
      <username>deployer</username>
      <password>your-password</password>
    </server>
    <server>
      <id>nexus-snapshots</id>
      <username>deployer</username>
      <password>your-password</password>
    </server>
  </servers>

  <!-- Profile to activate your internal repository -->
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

  <activeProfiles>
    <activeProfile>nexus</activeProfile>
  </activeProfiles>

</settings>
```

> In CI environments like Jenkins, place this file at `~/.m2/settings.xml` on the build server, or inject it as a managed file using the Config File Provider plugin.

---

**Project Structure & Creation**

**The Default Directory Layout**

One of Maven's biggest advantages is its standardized directory structure. Every Maven project follows the same layout, which means once you've seen one, you can navigate any of them:

```
project-root/
├── pom.xml                              # The project's build configuration
├── src/
│   ├── main/
│   │   ├── java/                        # Your production source code goes here
│   │   ├── resources/                   # Configuration files, properties, etc.
│   │   └── webapp/                      # Web assets (JSPs, HTML, WEB-INF): for WAR projects
│   └── test/
│       ├── java/                        # Your test source code goes here
│       └── resources/                   # Test-specific configuration files
└── target/                              # Maven's output directory (generated, not checked in)
    ├── classes/
    ├── test-classes/
    └── <artifact>.jar or <artifact>.war
```

The `target/` directory is where Maven puts everything it generates: compiled classes, test results, and the final artifact. You should never check this directory into version control.

---

**Creating a New Project**

Maven provides archetypes — essentially project templates — to scaffold new projects quickly.

**Creating a Web Application**

**Example 1:**

```bash
mkdir -p ~/sampleapp
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
> We will compile, package, and test this code locally later.


The two most common archetypes are:
- `maven-archetype-quickstart`: A simple Java project that produces a JAR
- `maven-archetype-webapp`: A web application that produces a WAR

---

**Creating a Spring Boot Application**

Spring Boot projects aren't typically created through Maven archetypes. Instead, the community uses **Spring Initializr**, which you can access through a web browser or the command line:

**Example 2:**

```
mkdir -p ~/myproject
cd ~/myproject
```

Download a Spring Boot starter project from the Spring Initializr web service:
```bash
curl -sSL --fail \
  "https://start.spring.io/starter.zip?type=maven-project&language=java&groupId=com.example&artifactId=demo&name=demo&packaging=jar&javaVersion=21&dependencies=web" \
  -o demo.zip
```
> The `-sSL --fail` flags tell `curl` to run in silent mode, follow redirects, and return an error if something goes wrong — rather than silently downloading an error page.

```bash
unzip demo.zip -d .
```
```bash
rm demo.zip
```
```bash
cd
```
```bash
tree myproject
```
<img width="802" height="486" alt="Screenshot 2026-03-12 at 12 37 11 PM" src="https://github.com/user-attachments/assets/5c8163bd-fdc9-437d-bdeb-04f239353736" />


**Example 3:** Downloads a pre-configured Spring Boot project as a ZIP file from Spring Initializr, specifying a particular Spring Boot version:
```bash
curl https://start.spring.io/starter.zip -d type=maven-project \
  -d language=java -d bootVersion=3.3.4 -d groupId=com.example \
  -d artifactId=demo -d name=demo -d packaging=jar -d javaVersion=21 \
  -d dependencies=web -o demo.zip
```
```bash
unzip demo.zip -d .
```


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


Which to use:
- Example 2: When you want the latest Spring Boot version
- Example 3: When you need a specific Spring Boot version (better for reproducible builds in DevOps)

> Both produce the same project structure — just potentially different Spring Boot versions.

---

**Creating a Quarkus Application**

Quarkus has its own Maven plugin for project generation:

```
mkdir -p ~/NewProject
cd ~/NewProject
```
```
mvn io.quarkus:quarkus-maven-plugin:3.15.0:create \
  -DprojectGroupId=com.NewProject \
  -DprojectArtifactId=quarkus-app \
  -DclassName="com.NewProject.GreetingResource" \
  -Dpath="/hello"
```
This generates a ready-to-run Quarkus project with a sample REST endpoint at `/hello`.
```bash
cd
```
```bash
tree NewProject
```
<img width="776" height="610" alt="Screenshot 2026-03-20 at 11 51 01 AM" src="https://github.com/user-attachments/assets/ecf30072-9493-42bc-86d5-c82dbc35c9bb" />

---

**Multi-Module Projects**

In real enterprise environments, applications aren't built as a single module. You'll typically encounter a multi-module Maven project, where a parent POM coordinates several sub-projects (modules) that may depend on each other.

This is an important DevOps concept because your CI/CD pipeline must understand the module structure to build and deploy components independently or together.

**Typical structure:**
```
my-app/
├── pom.xml                   # Parent POM
├── my-app-api/               # Shared interfaces/models
│   └── pom.xml
├── my-app-service/           # Business logic (depends on api)
│   └── pom.xml
└── my-app-web/               # Web layer (depends on service)
    └── pom.xml
```

**Parent POM** (at the root):
```xml
<project>
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.devopsclass</groupId>
  <artifactId>my-app</artifactId>
  <version>1.0.0</version>
  <packaging>pom</packaging>   <!-- Must be 'pom' for parent -->

  <modules>
    <module>my-app-api</module>
    <module>my-app-service</module>
    <module>my-app-web</module>
  </modules>

  <!-- Versions defined here are inherited by all child modules -->
  <properties>
    <maven.compiler.release>21</maven.compiler.release>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
  </properties>

  <!-- dependencyManagement locks versions without pulling them in -->
  <dependencyManagement>
    <dependencies>
      <dependency>
        <groupId>org.junit.jupiter</groupId>
        <artifactId>junit-jupiter</artifactId>
        <version>5.12.1</version>
        <scope>test</scope>
      </dependency>
    </dependencies>
  </dependencyManagement>
</project>
```

**Child POM** (e.g., my-app-service/pom.xml):
```xml
<project>
  <modelVersion>4.0.0</modelVersion>

  <parent>
    <groupId>com.devopsclass</groupId>
    <artifactId>my-app</artifactId>
    <version>1.0.0</version>
  </parent>

  <artifactId>my-app-service</artifactId>

  <dependencies>
    <dependency>
      <groupId>com.devopsclass</groupId>
      <artifactId>my-app-api</artifactId>
      <version>${project.version}</version>
    </dependency>
  </dependencies>
</project>
```

To build everything from the root:
```bash
cd my-app
mvn clean package
```

To build a single module and its dependencies:
```bash
mvn clean package -pl my-app-service -am
```

---

**The pom.xml**

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
                             http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>

  <!-- Project coordinates -->
  <groupId>com.devopsclass</groupId>
  <artifactId>sample-app</artifactId>
  <version>1.0.0</version>
  <packaging>war</packaging>

  <name>sample-app</name>
  <description>Sample web application built with Maven</description>

  <!-- Build settings -->
  <properties>
    <maven.compiler.release>21</maven.compiler.release>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
  </properties>

  <dependencies>
    <!-- The Servlet API — provided by Tomcat at runtime, so we don't package it -->
    <dependency>
      <groupId>jakarta.servlet</groupId>
      <artifactId>jakarta.servlet-api</artifactId>
      <version>6.1.0</version>
      <scope>provided</scope>
    </dependency>

    <!-- JUnit 5 for testing — only needed during the test phase -->
    <dependency>
      <groupId>org.junit.jupiter</groupId>
      <artifactId>junit-jupiter</artifactId>
      <version>5.12.1</version>
      <scope>test</scope>
    </dependency>
  </dependencies>

  <build>
    <plugins>
      <!-- Surefire runs unit tests and supports JUnit 5 -->
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-surefire-plugin</artifactId>
        <version>3.5.5</version>
        <configuration>
          <useModulePath>false</useModulePath>
        </configuration>
      </plugin>

      <!-- Jetty plugin lets you run the app locally without a full Tomcat install -->
      <plugin>
        <groupId>org.eclipse.jetty.ee10</groupId>
        <artifactId>jetty-ee10-maven-plugin</artifactId>
        <version>12.1.8</version>
        <configuration>
          <webApp>
            <contextPath>/sample-app</contextPath>
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

The most common cause is environment-specific configuration — file paths, environment variables, or ports that are available locally but not in the CI container. Check `target/surefire-reports/` for the full test output, and run the exact same Maven command locally with the same environment variables your CI uses.

**"Repository is blocked" in Nexus/Artifactory**

Your artifact repository is blocking access to a dependency. Either the repository isn't proxying Maven Central, or the specific version is on a blocklist. Check your Nexus/Artifactory admin configuration or switch to a version that's available in the repository.

**Out of memory during build**

Large projects with many modules can exhaust Maven's default heap. Set:
```bash
export MAVEN_OPTS="-Xms512m -Xmx2g"
```
Or in CI, pass it as an environment variable in the pipeline definition.
