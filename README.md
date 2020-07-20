Uses `goaccess` to generate pretty, **monthly** and **yearly** access logs for a few sites I have deployed in S3/CloudFront. Currently runs in a FreeNAS Jail.

Involves two separate buckets:

1. One that collects all the logs across all sites and has a 60-day expiration rule on all objects.
2. Another that [simply hosts the reports](https://reports.nikhil.io/) 🗂

Requires `goaccess` v1.4+

### Setup

On FreeBSD 11.2. FreshPorts' package is not compiled with support for Tokyo Cabinet. A bit more [involved](https://github.com/allinurl/goaccess/issues/1467) than that I thought it would be.

```bash
# Install deps
pkg install \
    tcb \
    gettext \
    libmaxminddb \
    automake \
    python3.7 \
    geoipupdate \
    awscli

# Compile goaccess
git clone https://github.com/allinurl/goaccess.git
cd goaccess
autoreconf -fiv
./configure \
    --enable-utf8 \
    --enable-geoip=mmdb \
    --enable-tcb=btree \
    CFLAGS="-I/usr/local/include" \
    LDFLAGS="-L/usr/local/lib"

make
make install

# Folder setup
mkdir -p $LOG_ROOT/geoip/
```

### Crontab

```
# Update the free GeoIP2 databases
0  0 * * * /usr/local/bin/geoipupdate -d $LOG_ROOT/geoip/ >> /dev/null 2>&1

# Generate access reports
10 0 * * * $LOG_ROOT && python3 generate.py >> $LOG_ROOT/debug.log 2>&1
```
