# Lab 5B. Nginx at the Edge: Files, Proxying, and a Pool of Backends

Nginx tends to be the first thing a request hits. In this lab it plays the three parts it usually plays in front of an application: it serves files off disk, it forwards traffic to a single backend, and it spreads traffic across a pool of backends and keeps going when one of them dies.

> Apache is still holding ports 80 and 443 from Lab 5A. Stop it first: `sudo systemctl stop httpd`.

## 1. Install Nginx and learn two commands

```bash
sudo dnf install -y nginx
sudo systemctl enable --now nginx
nginx -v

sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload
```

Two commands carry you through the whole lab. Test first, always, because a broken config refuses to load and can take the site down with it:

```bash
sudo nginx -t                 # check the config
sudo systemctl reload nginx   # apply it without dropping live connections
```

## 2. Serve files off disk

```bash
sudo mkdir -p /var/www/edge-static
echo "<!DOCTYPE html><html><head><meta charset=\"UTF-8\">
<title>Edge Static</title></head>
<body><h1>Static content</h1><p>Nginx served this straight from /var/www/edge-static.</p></body></html>" \
  | sudo tee /var/www/edge-static/index.html >/dev/null

sudo chown -R nginx:nginx /var/www/edge-static
sudo chcon -R -t httpd_sys_content_t /var/www/edge-static
```

Create `/etc/nginx/conf.d/static.conf`:

```nginx
server {
    listen 80;
    server_name static.local;

    root  /var/www/edge-static;
    index index.html;

    location ~ /\. {          # never serve dotfiles like .env or .git
        deny all;
    }

    access_log /var/log/nginx/static_access.log;
    error_log  /var/log/nginx/static_error.log;
}
```

```bash
echo "127.0.0.1  static.local proxy.local lb.local" | sudo tee -a /etc/hosts
sudo nginx -t && sudo systemctl reload nginx
curl -s http://static.local/
```

## 3. Forward to a single backend

Stand in for a real application with Python's built in server, then put Nginx in front of it:

```bash
python3 -m http.server 5000 --directory /var/www/edge-static &
```

Create `/etc/nginx/conf.d/proxy.conf`:

```nginx
server {
    listen 80;
    server_name proxy.local;

    location / {
        proxy_pass http://127.0.0.1:5000;

        # Hand the backend the real client details instead of Nginx's own
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_http_version 1.1;            # keep upstream connections alive
        proxy_set_header Connection "";
        proxy_read_timeout 30s;
    }

    access_log /var/log/nginx/proxy_access.log;
    error_log  /var/log/nginx/proxy_error.log;
}
```

```bash
sudo nginx -t && sudo systemctl reload nginx
curl -s http://proxy.local/          # the Python backend answers, through Nginx
```

That `X-Forwarded-Proto` header earns its keep once TLS lives at the edge. When Nginx terminates HTTPS and talks plain HTTP to the app, this header is how the app learns the original request was encrypted. The reference application you build in Lab 5C reads exactly this to decide whether a request arrived securely.

## 4. Spread traffic across a pool

Start three backends on three ports:

```bash
python3 -m http.server 5001 --directory /var/www/edge-static &
python3 -m http.server 5002 --directory /var/www/edge-static &
python3 -m http.server 5003 --directory /var/www/edge-static &
```

An `upstream` block names the pool; the server then proxies to the pool instead of to one host. Create `/etc/nginx/conf.d/loadbalancer.conf`:

```nginx
upstream app_pool {
    # No directive here means plain round robin
    server 127.0.0.1:5001 max_fails=2 fail_timeout=10s;
    server 127.0.0.1:5002 max_fails=2 fail_timeout=10s;
    server 127.0.0.1:5003 max_fails=2 fail_timeout=10s;
}

server {
    listen 80;
    server_name lb.local;

    location / {
        proxy_pass http://app_pool;

        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_http_version 1.1;
        proxy_set_header Connection "";

        # If one backend answers with a 5xx, quietly try the next one
        proxy_next_upstream error timeout http_502 http_503 http_504;
    }

    access_log /var/log/nginx/lb_access.log;
    error_log  /var/log/nginx/lb_error.log;
}
```

```bash
sudo nginx -t && sudo systemctl reload nginx
```

Round robin is the default, and it assumes every request costs about the same. When that assumption breaks, switch how the pool is chosen by changing only the top of the block. If some requests are quick and others drag, prefer whichever backend is least busy:

```nginx
upstream app_pool {
    least_conn;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
    server 127.0.0.1:5003;
}
```

If the app keeps a user's session in its own memory rather than in a shared store, pin each client to one backend so their session survives:

```nginx
upstream app_pool {
    ip_hash;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
    server 127.0.0.1:5003;
}
```

The `max_fails=2 fail_timeout=10s` on each server is a quiet health check. Miss twice inside ten seconds and Nginx pulls that backend out of rotation for ten seconds, then sends a single probe to see if it recovered.

## 5. Watch it balance, then watch it survive a failure

```bash
# Six requests, each answered by some member of the pool
for i in $(seq 1 6); do curl -s -o /dev/null -w "request $i: %{http_code}\n" http://lb.local/; done

# Kill one backend and confirm the site still answers from the other two
kill $(lsof -t -i:5002)
curl -s -o /dev/null -w "after failover: %{http_code}\n" http://lb.local/
```

If you want to see which backend served which request, add a log line to the `http {}` block of `/etc/nginx/nginx.conf` that records the upstream address:

```nginx
log_format upstream '$remote_addr [$time_local] "$request" '
                    '$status upstream=$upstream_addr rt=$request_time';
```

## 6. Clean up the fake backends

```bash
kill $(lsof -t -i:5000) $(lsof -t -i:5001) $(lsof -t -i:5002) $(lsof -t -i:5003) 2>/dev/null || true
```

By the end you have Nginx serving static files, forwarding to a backend, and load balancing a pool that keeps answering after you kill a member. This is the shape the reference application ships in: a small stateless service with Nginx out front. That is why Lab 5C builds the service to hold no session state of its own, so any member of a pool can answer any request.
