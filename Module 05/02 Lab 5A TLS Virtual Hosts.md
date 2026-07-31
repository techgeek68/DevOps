# Lab 5A. Two Sites, One Machine, Both on HTTPS

One Apache server can host several websites at once and hand each of them its own certificate. Here you bring up two of them, `alpha.local` and `bravo.local`, both answering on HTTPS. The certificates are ones you sign yourself, using a small certificate authority you build first. Each site also gets its own access log with a timing column, so a slow request shows up the moment you look.

Building your own authority is worth the few extra minutes. A throwaway certificate makes the browser complain every time. An authority is different: once the machine trusts it, it trusts every certificate that authority signs, silently. That is exactly how a company runs its internal PKI, and once you have done it once the idea sticks.

## 1. Install Apache and open the firewall

```bash
sudo dnf install -y httpd mod_ssl openssl
sudo systemctl enable --now httpd

sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

httpd -v
```

The two names need to resolve somewhere. On a lab box, the hosts file is the quickest way:

```bash
echo "127.0.0.1  alpha.local bravo.local" | sudo tee -a /etc/hosts
```

## 2. Build a local certificate authority

Do the crypto work in a scratch folder, then copy the finished files into place.

```bash
mkdir -p ~/localca && cd ~/localca

# The authority's private key and its root certificate, good for ten years
openssl req -x509 -nodes -newkey rsa:4096 -sha256 -days 3650 \
    -keyout ca.key -out ca.crt \
    -subj "/C=NP/ST=Bagmati/L=Kathmandu/O=DevOps Lab/CN=DevOps Lab Local Root CA"
```

Now tell the system to trust it. After this step, anything the authority signs is accepted without a warning:

```bash
sudo cp ca.crt /etc/pki/ca-trust/source/anchors/devops-lab-local-ca.crt
sudo update-ca-trust
```

## 3. Issue a certificate for each site

For each site you make a key, then a signing request that carries the hostname in its Subject Alternative Name, then you sign that request with the authority. Browsers stopped trusting the old Common Name field years ago, so the SAN is not optional.

```bash
# ---- alpha.local ----
openssl req -nodes -newkey rsa:2048 -sha256 \
    -keyout alpha.key -out alpha.csr \
    -subj "/C=NP/ST=Bagmati/L=Kathmandu/O=DevOps Lab/CN=alpha.local" \
    -addext "subjectAltName=DNS:alpha.local"

openssl x509 -req -in alpha.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
    -out alpha.crt -days 825 -sha256 \
    -extfile <(printf "subjectAltName=DNS:alpha.local\nextendedKeyUsage=serverAuth\n")

# ---- bravo.local ----
openssl req -nodes -newkey rsa:2048 -sha256 \
    -keyout bravo.key -out bravo.csr \
    -subj "/C=NP/ST=Bagmati/L=Kathmandu/O=DevOps Lab/CN=bravo.local" \
    -addext "subjectAltName=DNS:bravo.local"

openssl x509 -req -in bravo.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
    -out bravo.crt -days 825 -sha256 \
    -extfile <(printf "subjectAltName=DNS:bravo.local\nextendedKeyUsage=serverAuth\n")
```

Copy the keys and certificates where Apache expects to find them, and lock the keys down:

```bash
sudo cp alpha.crt bravo.crt /etc/pki/tls/certs/
sudo cp alpha.key bravo.key /etc/pki/tls/private/
sudo chmod 600 /etc/pki/tls/private/alpha.key /etc/pki/tls/private/bravo.key
```

Why 825 days? That is the longest a browser will accept for a leaf certificate. The authority itself can live much longer, which is why its root runs for ten years above.

## 4. Give each site something to serve

```bash
for site in alpha bravo; do
  sudo mkdir -p /var/www/${site}.local
  echo "<!DOCTYPE html><html><head><meta charset=\"UTF-8\">
<title>${site}.local</title></head>
<body><h1>${site}.local</h1><p>Served over HTTPS by Apache.</p></body></html>" \
    | sudo tee /var/www/${site}.local/index.html >/dev/null
  sudo chown -R apache:apache /var/www/${site}.local
  sudo chcon -R -t httpd_sys_content_t /var/www/${site}.local
done
```

## 5. Define one log format you can reuse

Declare the format once, globally, then point each site at it by name. This one adds `%D`, the number of microseconds Apache spent on the request. When a page feels slow, that column is where you look first. Put it in `/etc/httpd/conf.d/00-logformat.conf`:

```apache
# Combined fields plus %D, the request duration in microseconds
LogFormat "%h %l %u %t \"%r\" %>s %b %D \"%{Referer}i\" \"%{User-Agent}i\"" timed_combined
```

The `00-` in the filename is deliberate. Apache reads its config files in order, so this one loads before the site files that mention `timed_combined`.

## 6. Write the two site configurations

Create `/etc/httpd/conf.d/alpha.local-ssl.conf`:

```apache
<VirtualHost *:443>
    ServerName alpha.local
    DocumentRoot /var/www/alpha.local

    SSLEngine on
    SSLCertificateFile    /etc/pki/tls/certs/alpha.crt
    SSLCertificateKeyFile /etc/pki/tls/private/alpha.key
    SSLProtocol           all -SSLv3 -TLSv1 -TLSv1.1

    <Directory "/var/www/alpha.local">
        Options -Indexes +FollowSymLinks
        Require all granted
    </Directory>

    ErrorLog  /var/log/httpd/alpha.local_error.log
    CustomLog /var/log/httpd/alpha.local_access.log timed_combined
</VirtualHost>

# Bounce plain HTTP for this site over to HTTPS
<VirtualHost *:80>
    ServerName alpha.local
    Redirect permanent / https://alpha.local/
</VirtualHost>
```

Create `/etc/httpd/conf.d/bravo.local-ssl.conf` the same way, swapping every `alpha` for `bravo`:

```apache
<VirtualHost *:443>
    ServerName bravo.local
    DocumentRoot /var/www/bravo.local

    SSLEngine on
    SSLCertificateFile    /etc/pki/tls/certs/bravo.crt
    SSLCertificateKeyFile /etc/pki/tls/private/bravo.key
    SSLProtocol           all -SSLv3 -TLSv1 -TLSv1.1

    <Directory "/var/www/bravo.local">
        Options -Indexes +FollowSymLinks
        Require all granted
    </Directory>

    ErrorLog  /var/log/httpd/bravo.local_error.log
    CustomLog /var/log/httpd/bravo.local_access.log timed_combined
</VirtualHost>

<VirtualHost *:80>
    ServerName bravo.local
    Redirect permanent / https://bravo.local/
</VirtualHost>
```

Both HTTPS blocks listen on the same `*:443`. Apache tells them apart by the hostname the client sends during the TLS handshake, a feature called SNI. One address, one port, two certificates.

## 7. Check the syntax, then reload

```bash
sudo apachectl configtest      # you want to see: Syntax OK
sudo httpd -S                  # lists both sites bound to port 443
sudo systemctl restart httpd
```

## 8. Prove it works

Because the machine trusts your authority now, `curl` needs no `-k` flag. If it did, something in the trust step went wrong.

```bash
curl https://alpha.local/
curl https://bravo.local/

# Read the certificate straight off the socket and confirm who signed it
echo | openssl s_client -connect alpha.local:443 -servername alpha.local 2>/dev/null \
  | openssl x509 -noout -issuer -subject -ext subjectAltName
```

Then confirm each site is writing to its own log in the format you defined. The long number sitting just before the quoted referrer is `%D`, the microseconds:

```bash
sudo tail -n 2 /var/log/httpd/alpha.local_access.log
sudo tail -n 2 /var/log/httpd/bravo.local_access.log
```

By the end you have two sites on one host, each on HTTPS, each trusting a certificate your own authority signed, and each keeping a separate timed log. Keep the `~/localca` folder. When you put Nginx in front of an application later, the same authority can sign that certificate too.

> Ports 80 and 443 are now held by Apache. Before you start Lab 5B, free them with `sudo systemctl stop httpd`.
