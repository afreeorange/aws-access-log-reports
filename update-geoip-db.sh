rm -rf geoip
mkdir geoip
wget -O - https://geolite.maxmind.com/download/geoip/database/GeoLite2-City.tar.gz | tar -xvzf -
mv GeoLite2-City*/GeoLite2-City.mmdb geoip/
rm -rf GeoLite2-City*
