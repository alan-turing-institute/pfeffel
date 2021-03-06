import logging
import os
import shutil
import time
import zipfile
from typing import List
from urllib.parse import urlparse

import pandas as pd
import requests
import yaml
from tqdm.auto import tqdm

try:
    import xlrd  # noqa: F401
except Exception as e:
    msg = (
        "Please install the package xlrd: `pip install --user xlrd`"
        "It's an optional requirement for pandas, and we'll be needing it."
    )
    print(msg)
    raise e


logging.basicConfig(level=logging.DEBUG)


PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
)
CONFIG_FPATH = os.path.join(PROJECT_ROOT, "config.yaml")


def download_file(output_dir: str, url: str, sleep_seconds: float = 0) -> str:
    """Download the data from the given URL into the datafolder, unless it's
    already there. Return path to downloaded file.
    """
    os.makedirs(output_dir, exist_ok=True)

    a = urlparse(url)
    filename = os.path.basename(a.path)
    filepath = os.path.join(output_dir, filename)
    # Don't redownload if we already have this file.
    if os.path.exists(filepath):
        logging.debug("Already have {}".format(filename))
    else:
        logging.info("Downloading {}".format(filename))
        rqst = requests.get(url)
        rqst.raise_for_status()
        with open(filepath, "wb") as f:
            f.write(rqst.content)
        time.sleep(sleep_seconds)
    return filepath


def download_urls(
    urls: List[str], output_dir: str, sleep_seconds: float = 0.2
) -> List[str]:
    downloaded_fpaths = list()
    for url in tqdm(urls):
        # ensure that we're doing a small sleep between
        #  calls so we don't overload API
        downloaded_fpaths.append(
            download_file(
                output_dir=output_dir, url=url, sleep_seconds=sleep_seconds
            )
        )

    return downloaded_fpaths


def extract_zips(zip_fpaths: List[str], csv_dir: str) -> None:
    # get filenames currently in csv_dir
    current_csvs = os.listdir(csv_dir)
    for fpath in zip_fpaths:
        with zipfile.ZipFile(fpath, "r") as z:
            namelist = z.namelist()
            has_been_extracted = any(
                name not in current_csvs for name in namelist
            )
            if has_been_extracted:
                logging.info(f"Unzipping {fpath}")
                z.extractall(csv_dir)
                # add to already existing list
                current_csvs.extend(namelist)
            else:
                logging.debug(f"{fpath} has already been extracted.")
    return


def xlsx_to_csv(csv_dir: str, xlsx_archive_dir: str) -> int:

    xlsx_files = [
        os.path.join(csv_dir, fname)
        for fname in os.listdir(csv_dir)
        if fname.endswith(".zip")
    ]
    for xlsxfile in xlsx_files:
        csvfile = xlsxfile.replace(".xlsx", ".csv")
        if not os.path.exists(csvfile):
            logging.info("Converting .xlsx to .csv.")
            pd.read_excel(xlsxfile).to_csv(
                csvfile, date_format="%d/%m/%Y %H:%M:%S"
            )
        else:
            logging.debug("Already have {}".format(csvfile))

        shutil.move(
            xlsxfile,
            os.path.join(xlsx_archive_dir, os.path.basename(xlsxfile)),
        )

    logging.info(f"moved {len(xlsx_files)} files")
    return len(xlsx_files)


if __name__ == "__main__":

    # load config with data locations
    with open(CONFIG_FPATH, "r") as f:
        config = yaml.safe_load(f)

    data_root_dir = os.path.join(PROJECT_ROOT, config["data"]["root_dir"])

    urls_fpath = os.path.join(
        data_root_dir, config["data"]["relative_paths"]["urls_file"]
    )
    with open(urls_fpath, "r") as f:
        urls = f.read().splitlines()

    # split out csv and zip files from list (using extensions)
    csv_urls = [url for url in urls if url.endswith(".csv")]
    zip_urls = [url for url in urls if url.endswith(".zip")]

    csv_dir = os.path.join(
        data_root_dir, config["data"]["relative_paths"]["csvs_dir"]
    )
    zip_dir = os.path.join(
        data_root_dir, config["data"]["relative_paths"]["zips_dir"]
    )
    xlsx_dir = os.path.join(
        data_root_dir, config["data"]["relative_paths"]["xlsx_archive_dir"]
    )

    # download csvs
    csv_fpaths = download_urls(urls=csv_urls, output_dir=csv_dir)
    # download zips
    zip_fpaths = download_urls(urls=zip_urls, output_dir=zip_dir)
    # extract zips
    extract_zips(zip_fpaths=zip_fpaths, csv_dir=csv_dir)

    # convert any xlsx files
    xlsx_to_csv(csv_dir=csv_dir, xlsx_archive_dir=xlsx_dir)

    logging.info("done!")
