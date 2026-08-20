<%@ page contentType="text/html; charset=UTF-8" session="false" trimDirectiveWhitespaces="true" %>
<%@ page import="java.lang.management.ManagementFactory" %>
<%@ page import="java.lang.management.MemoryMXBean" %>
<%@ page import="java.lang.management.MemoryUsage" %>
<%@ page import="java.net.InetAddress" %>
<%@ page import="java.time.ZonedDateTime" %>
<%@ page import="java.time.format.DateTimeFormatter" %>

<%!
    // Declaration block: these become servlet fields, initialized once at
    // class load rather than rebuilt on every request.

    private static final int SEGMENTS = 20;
    private static final long MB = 1024L * 1024L;

    // DateTimeFormatter is immutable and thread safe, unlike SimpleDateFormat,
    // which had to be reallocated per request to avoid corrupting output.
    private static final DateTimeFormatter STAMP =
            DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss Z");

    private static final MemoryMXBean MEMORY = ManagementFactory.getMemoryMXBean();

    // Values that cannot change for the life of the JVM. Resolving the
    // hostname is a blocking name-service call, so it is cached rather than
    // repeated on every hit.
    private static final String HOSTNAME = resolveHostname();
    private static final String JVM_VERSION = System.getProperty("java.version");
    private static final int CPUS = Runtime.getRuntime().availableProcessors();

    private static String resolveHostname() {
        try {
            return InetAddress.getLocalHost().getHostName();
        } catch (Exception e) {
            return "unknown-host";
        }
    }
%>

<%
    // Status pages must never be cached by a proxy or the browser.
    response.setHeader("Cache-Control", "no-store");

    MemoryUsage heap = MEMORY.getHeapMemoryUsage();
    long usedMem = heap.getUsed() / MB;
    long committedMem = heap.getCommitted() / MB;
    long maxMem = heap.getMax() > 0 ? heap.getMax() / MB : committedMem;

    int usedPercent = maxMem > 0 ? (int) (usedMem * 100L / maxMem) : 0;

    // Ceiling division without floating point.
    int litSegments = (usedPercent * SEGMENTS + 99) / 100;

    boolean warn = usedPercent >= 70;
    boolean critical = usedPercent >= 90;
    String accent = critical ? "#c4443a" : (warn ? "#d9a13b" : "#d9603b");

    String now = ZonedDateTime.now().format(STAMP);
%>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title><%= HOSTNAME %> / status</title>
<style>
:root{--bg:#12100e;--rule:#262220;--dim:#6b645c;--dimmer:#4a443e;--fg:#f0ebe4;--idle:#2b2724;--accent:<%= accent %>}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--fg);font:13px/1.4 ui-monospace,"SF Mono","JetBrains Mono",Menlo,Consolas,monospace;padding:48px 32px;-webkit-font-smoothing:antialiased}
.panel{max-width:720px;margin:0 auto}
.masthead{border-top:2px solid var(--accent);padding-top:14px;display:flex;justify-content:space-between;align-items:baseline;gap:16px;flex-wrap:wrap;margin-bottom:36px;font-size:11px;letter-spacing:2px}
.masthead .ref{color:var(--dim);letter-spacing:1px}
.masthead .state{color:var(--accent)}
.host{font-size:34px;line-height:1;margin-bottom:8px;word-break:break-all}
.stamp{font-size:12px;color:var(--dim);margin-bottom:40px}
.readout{display:flex;justify-content:space-between;gap:16px;font-size:11px;letter-spacing:1px;color:var(--dim);padding:10px 0;border-bottom:1px solid var(--rule)}
.readout b{color:var(--fg);font-weight:inherit;letter-spacing:0;font-variant-numeric:tabular-nums}
.gauge{display:flex;gap:3px;margin:28px 0 40px}
.gauge i{flex:1;height:28px;background:var(--idle)}
.gauge i.lit{background:var(--accent)}
.colophon{font-size:11px;letter-spacing:1px;color:var(--dimmer);border-top:1px solid var(--rule);padding-top:14px}
@media(max-width:480px){body{padding:32px 20px}.host{font-size:24px}.gauge i{height:20px}}
</style>
</head>
<body>
<div class="panel">

<div class="masthead">
<div class="state">STATUS / <%= critical ? "PRESSURE" : (warn ? "ELEVATED" : "NOMINAL") %></div>
<div class="ref">DVP-401 &middot; 5.1.C</div>
</div>

<div class="host"><%= HOSTNAME %></div>
<div class="stamp"><%= now %></div>

<div class="readout"><span>HEAP USED</span><b><%= usedMem %> MB</b></div>
<div class="readout"><span>HEAP COMMITTED</span><b><%= committedMem %> MB</b></div>
<div class="readout"><span>HEAP MAX</span><b><%= maxMem %> MB</b></div>
<div class="readout"><span>UTILIZATION</span><b><%= usedPercent %>%</b></div>
<div class="readout"><span>PROCESSORS</span><b><%= CPUS %></b></div>

<div class="gauge">
<%
    // Single buffered write instead of 20 template round trips through out.
    StringBuilder gauge = new StringBuilder(SEGMENTS * 22);
    for (int i = 0; i < SEGMENTS; i++) {
        gauge.append(i < litSegments ? "<i class=lit></i>" : "<i></i>");
    }
    out.write(gauge.toString());
%>
</div>

<div class="colophon">
<%= application.getServerInfo() %> &nbsp;/&nbsp; JVM <%= JVM_VERSION %> &nbsp;/&nbsp; SERVLET <%= application.getMajorVersion() %>.<%= application.getMinorVersion() %>
</div>

</div>
</body>
</html>
