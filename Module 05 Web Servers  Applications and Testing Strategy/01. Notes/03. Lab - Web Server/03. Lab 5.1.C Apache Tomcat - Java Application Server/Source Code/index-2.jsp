<%@ page contentType="text/html; charset=UTF-8" session="false" trimDirectiveWhitespaces="true" %>
<%@ page import="java.time.LocalDateTime" %>
<%@ page import="java.time.format.DateTimeFormatter" %>
<%@ page import="java.util.ArrayDeque" %>
<%@ page import="java.util.ArrayList" %>
<%@ page import="java.util.Deque" %>
<%@ page import="java.util.List" %>
<%@ page import="java.util.concurrent.atomic.AtomicLong" %>
<%!
    private static final int MAX_ROWS = 10;
    private static final DateTimeFormatter CLOCK = DateTimeFormatter.ofPattern("HH:mm:ss");
    private static final AtomicLong POSTED = new AtomicLong();
    private static final Deque<Hit> LEDGER = new ArrayDeque<Hit>();
 
    private static final class Hit {
        final long seq;
        final String at;
        final String client;
        final String scheme;
        final String xff;
        Hit(long seq, String at, String client, String scheme, String xff) {
            this.seq = seq;
            this.at = at;
            this.client = client;
            this.scheme = scheme;
            this.xff = xff;
        }
    }
 
    private static void post(Hit h) {
        synchronized (LEDGER) {
            LEDGER.addFirst(h);
            while (LEDGER.size() > MAX_ROWS) {
                LEDGER.removeLast();
            }
        }
    }
 
    private static List<Hit> page() {
        synchronized (LEDGER) {
            return new ArrayList<Hit>(LEDGER);
        }
    }
 
    private static String esc(String raw) {
        if (raw == null || raw.isEmpty()) {
            return "none";
        }
        StringBuilder out = new StringBuilder(raw.length() + 16);
        for (int i = 0; i < raw.length(); i++) {
            char c = raw.charAt(i);
            if (c == '&')       { out.append("&amp;"); }
            else if (c == '<')  { out.append("&lt;"); }
            else if (c == '>')  { out.append("&gt;"); }
            else if (c == '"')  { out.append("&quot;"); }
            else if (c == '\'') { out.append("&#39;"); }
            else if (c < 0x20)  { out.append('?'); }
            else                { out.append(c); }
        }
        return out.toString();
    }
%>
<%
    post(new Hit(POSTED.incrementAndGet(),
                 LocalDateTime.now().format(CLOCK),
                 request.getRemoteAddr(),
                 request.getScheme(),
                 request.getHeader("X-Forwarded-For")));
    List<Hit> rows = page();
%>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Request Ledger</title>
<style>
  :root{
    --ink:#1d2127; --faded:#8c8371; --rule:#c2d2df;
    --margin:#a4362a; --paper:#f8f4e9; --desk:#ded8c9;
  }
  *{box-sizing:border-box}
  body{
    margin:0; padding:44px 14px 72px;
    background:var(--desk);
    color:var(--ink);
    font:15px/1.5 "Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
    -webkit-font-smoothing:antialiased;
  }
  .book{
    position:relative;
    max-width:760px; margin:0 auto;
    padding:26px 30px 30px 74px;
    background:var(--paper);
    background-image:repeating-linear-gradient(to bottom,
      transparent 0 31px, var(--rule) 31px 32px);
    background-repeat:no-repeat;
    background-size:100% 320px;
    background-position:0 133px;
    border:1px solid #cec5b0;
    box-shadow:0 1px 0 rgba(255,255,255,.7) inset, 0 12px 26px rgba(40,32,16,.20);
  }
  .book::before,.book::after{
    content:""; position:absolute; top:0; bottom:0;
    border-left:1px solid var(--margin);
  }
  .book::before{left:54px; opacity:.5}
  .book::after {left:58px; opacity:.22}
 
  .folio{
    display:flex; align-items:baseline; justify-content:space-between;
    border-bottom:2px solid var(--ink); padding-bottom:9px;
  }
  h1{margin:0; font-size:18px; font-weight:600; letter-spacing:.15em; text-transform:uppercase}
  .folio span{
    font:11px/1 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
    letter-spacing:.1em; color:var(--faded); text-transform:uppercase;
  }
  .legend{margin:9px 0 17px; font-size:12.5px; color:var(--faded)}
 
  table{width:100%; border-collapse:collapse}
  thead th{
    font:11px/1 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
    letter-spacing:.12em; text-transform:uppercase; color:var(--faded);
    text-align:left; padding:0 8px 9px 0; border-bottom:1px solid var(--ink);
  }
  tbody td{
    height:32px; line-height:32px; padding:0 8px 0 0;
    border:0; vertical-align:bottom; font-variant-numeric:tabular-nums;
  }
  td.seq{width:58px; color:var(--margin); font:600 13px/32px ui-monospace,Menlo,Consolas,monospace}
  td.at {width:92px; font:13px/32px ui-monospace,Menlo,Consolas,monospace}
  td.ip {width:158px; font:13px/32px ui-monospace,Menlo,Consolas,monospace}
  td.sc {width:64px; font-size:12.5px; color:var(--faded); text-transform:uppercase; letter-spacing:.06em}
  td.via{font-size:12px; color:var(--faded); word-break:break-all}
  tbody tr:first-child td{color:#000}
  tbody tr:first-child td.seq{color:var(--margin)}
  tbody tr:first-child td.seq::before{content:"\203A\00a0"}
 
  .rule-off{
    margin-top:24px; padding-top:10px; border-top:2px solid var(--ink);
    display:flex; justify-content:space-between; gap:20px; flex-wrap:wrap;
    font:12px/1.7 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
    color:var(--faded);
  }
  .rule-off b{color:var(--ink); font-weight:600; font-variant-numeric:tabular-nums}
  @media (max-width:560px){
    .book{padding-left:56px}
    .book::before{left:38px} .book::after{left:42px}
    td.via{display:none} thead th:last-child{display:none}
  }
</style>
</head>
<body>
  <div class="book">
 
    <div class="folio">
      <h1>Request Ledger</h1>
      <span>Folio 01 &nbsp;/&nbsp; Volatile</span>
    </div>
 
    <p class="legend">
      Postings are held in the servlet instance and are lost on restart or redeploy.
      The <em>client</em> column is whatever <code>getRemoteAddr()</code> reports after the
      valve chain has run.
    </p>
 
    <table>
      <thead>
        <tr>
          <th>No.</th><th>Time</th><th>Client</th><th>Scheme</th><th>X-Forwarded-For</th>
        </tr>
      </thead>
      <tbody>
<% for (Hit h : rows) { %>
        <tr>
          <td class="seq"><%= h.seq %></td>
          <td class="at"><%= esc(h.at) %></td>
          <td class="ip"><%= esc(h.client) %></td>
          <td class="sc"><%= esc(h.scheme) %></td>
          <td class="via"><%= esc(h.xff) %></td>
        </tr>
<% } %>
      </tbody>
    </table>
 
    <div class="rule-off">
      <span>Posted since start &nbsp;<b><%= POSTED.get() %></b></span>
      <span>Retained &nbsp;<b><%= rows.size() %></b> of <%= MAX_ROWS %></span>
      <span>HEAD requests are posted too</span>
    </div>
 
  </div>
</body>
</html>
