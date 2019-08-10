from collections import defaultdict
from glob import glob
import os
import re
import shlex
import shutil
import subprocess

LOGS_BUCKET = "logs.nikhil.io"
PUBLIC_TARGET = "reports.nikhil.io"
SITES = {
    "freeorange.net": {"type": "AWSS3"},
    "log.nikhil.io": {"type": "CLOUDFRONT"},
    "nikhil.io": {"type": "AWSS3"},
    "public.nikhil.io": {"type": "AWSS3"},
    "sorry.nikhil.io": {"type": "CLOUDFRONT"},
}


def clean_logs(site_name):
    try:
        shutil.rmtree(f"{site_name}/logs")
    except FileNotFoundError:
        pass


def prepare_site_folder(site_name):
    try:
        os.makedirs(f"{site_name}/logs")
        os.makedirs(f"{site_name}/db")
    except FileExistsError:
        pass


def prepare_report_folder(site_name, year, month):
    try:
        os.makedirs(f"./reports/{site_name}/{year}/{month}")
    except FileExistsError:
        pass


def sync_logs(site_name, bucket=LOGS_BUCKET):
    subprocess.run(
        shlex.split(f'aws s3 sync "s3://{bucket}/{site_name}/" "./{site_name}/logs/"')
    )


def sync_reports(bucket=LOGS_BUCKET):
    subprocess.run(shlex.split(f"aws s3 sync reports/ s3://{PUBLIC_TARGET}/"))


def generate_report(site_name, log_type, year, month=None):
    # Yearly vs monthly report
    the_glob = f"*{year}-{month}*"
    report_path = f"./reports/{site_name}/{year}/{month}/index.html"
    if month is None:
        the_glob = f"*{year}*"
        report_path = f"./reports/{site_name}/{year}/index.html"

    # Handle S3 and CloudFront logs
    stream_command = f"cat ./{site_name}/logs/{the_glob}"
    if log_type == "CLOUDFRONT":
        stream_command = f"gunzip -c ./{site_name}/logs/{the_glob}.gz"

    report_command = f"""
        goaccess \
            --log-format {log_type} - \
            --geoip-database=./geoip/GeoLite2-City.mmdb \
            --agent-list \
            --ignore-crawlers \
            --real-os \
            --exclude-ip $(curl --silent "https://api.ipify.org") \
            --with-output-resolver \
            --json-pretty-print \
            --db-path=./{site_name}/db/ \
            --keep-db-files \
            --output={report_path} \
            --html-prefs='{{"theme":"bright"}}'\
            --html-custom-css=./custom.css
        """

    process_stream = subprocess.Popen(
        stream_command, shell=True, stdout=subprocess.PIPE
    )
    process_logs = subprocess.Popen(
        report_command, shell=True, stdin=process_stream.stdout
    )
    process_logs.communicate()[0]


def unique_years_and_months(site_name):
    d = defaultdict(list)
    ret = {}

    for path in glob(f"./{site_name}/logs/*"):
        s = re.search(r".*(\d{4})-(\d{2}).*", path)
        d[s.group(1)].append(s.group(2))

    for year, months in d.items():
        ret[year] = set(months)

    return ret


if __name__ == "__main__":
    for site_name in SITES.keys():
        # clean_logs(site_name)
        prepare_site_folder(site_name)

        print(">>>", site_name)
        sync_logs(site_name)

        for year, months in unique_years_and_months(site_name).items():
            print(f"Generating report for {site_name} for {year}")
            generate_report(site_name, SITES[site_name]["type"], year)

            for month in months:
                prepare_report_folder(site_name, year, month)

                print(f"Generating report for {site_name} for {year}/{month}")
                generate_report(site_name, SITES[site_name]["type"], year, month)

    sync_reports()
