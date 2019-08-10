Use `awscli` and `goaccess` to generate pretty, monthly reports of a few sites I have deployed in S3/CloudFront. Runs in a FreeNAS Jail. Uploads reports to an S3 bucket when done.

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
0  0 * * * /usr/local/bin/geoipupdate -d $LOG_ROOT/geoip/ >> /dev/null 2>&1
10 0 * * * $LOG_ROOT && python3 generate.py >> $LOG_ROOT/debug.log 2>&1
```
