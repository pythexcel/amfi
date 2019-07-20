from amc.jobs.util import download_path, aum_path, ter_path, portfolio_path
import os
import zipfile
import shutil
import pandas as pd

from amc.jobs.util import ExcelFile


def organize_download():
    process_zip_file()
    organize_files()
    pass


def organize_files():
    for (dirpath, dirnames, filenames) in os.walk(download_path):
        for f in filenames:
            if ".xls" in f.lower() or ".xlsx" in f.lower():
                print(os.path.join(dirpath, f))

                if "aum" in f.lower() or "asset" in f.lower() or "annexure" in f.lower() or "SEBI_Additional_MI_Requirement" in f or "MCR" in f or "SEBI Additional MI Requirement" in f:
                    os.rename(os.path.join(download_path, f),
                              os.path.join(aum_path, f))
                    continue

                if "portfolio" in f.lower() or "fact" in f.lower() or "equity" in f.lower() or "debt" in f.lower() or "isin" in f.lower() or "port" in f.lower() or "fof" in f.lower() or "hybrid" in f.lower() or "gold" in f.lower():

                    os.rename(os.path.join(download_path, f),
                              os.path.join(portfolio_path, f))

                    continue

                if "expense" in f.lower() or "ter" in f.lower() or "ratio" in f.lower():
                    os.rename(os.path.join(download_path, f),
                              os.path.join(ter_path, f))

                    continue

                try:
                    xls = ExcelFile(os.path.join(download_path, f))

                    df = pd.read_excel(xls, 0)

                    df.loc[-1] = df.columns
                    df.index = df.index + 1
                    df = df.sort_index()

                    df = df.head()

                    if "aum" in df.to_string().lower():
                        os.rename(os.path.join(download_path, f),
                                  os.path.join(aum_path, f))
                        continue

                    if "ter" in df.to_string().lower():
                        os.rename(os.path.join(download_path, f),
                                  os.path.join(ter_path, f))
                        continue

                    if "portfolio" in df.to_string().lower():
                        os.rename(os.path.join(download_path, f),
                                  os.path.join(portfolio_path, f))
                        continue
                        
                except Exception as e:
                    print(e)
                    pass

        break  # this break is important to prevent further processing of sub directories


def process_zip_file():
    # many mf have portfolio as zip files so first we need to extract them

    for (dirpath, dirnames, filenames) in os.walk(download_path):
        for f in filenames:
            if ".zip" in f:

                print("processing file ", f)
                with zipfile.ZipFile(os.path.join(download_path, f)) as zip_file:
                    for member in zip_file.namelist():
                        filename = os.path.basename(member)
                        # skip directories
                        if not filename:
                            continue

                        # copy file (taken from zipfile's extract)
                        source = zip_file.open(member)
                        target = open(os.path.join(
                            download_path, filename), "wb")
                        with source, target:
                            shutil.copyfileobj(source, target)

                with zipfile.ZipFile(os.path.join(download_path, f), "r") as zip_ref:
                    print(download_path)
                    zip_ref.extractall(download_path)
                # os.remove(os.path.join(path, f))
                try:
                    os.mkdir(os.path.join(download_path, "processed"))
                except FileExistsError:
                    pass

                os.rename(os.path.join(download_path, f), os.path.join(
                    os.path.join(download_path, "processed"), f))

        break  # this break is important to prevent further processing of sub directories
