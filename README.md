Use `awscli` and `goaccess` to generate pretty, monthly reports of a few sites I have deployed in S3/CloudFront. Runs in a FreeNAS Jail.

### FreeBSD Setup

```bash
# Install deps
pkg install awscli goaccess nginx python3.7
sysrc nginx_enable=YES

# Config is here
# /usr/local/etc/nginx/nginx.conf
service nginx start

# Get script
git clone https://github.com/afreeorange/aws-access-log-reports.git
cd aws-access-log-reports

# Update GeoIP Database
bash update-geoip-db.sh

# Cron job

```
