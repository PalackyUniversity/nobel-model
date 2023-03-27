from urllib import request
from typing import Union
from common import *
from glob import glob
from tqdm import tqdm
import pandas as pd
import os

VACCINATION_URL = "https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovani-demografie.csv"
COUNTS_URL = "https://www.czso.cz/documents/142154812/176236044/sldb2021_pv_vek_pohlavi.xlsx"

URLS = [
    VACCINATION_URL,
    COUNTS_URL,
    "https://www.czso.cz/documents/10180/179851740/demomigr_2005_2021_komplet.zip",
    "https://www.czso.cz/documents/10180/191186413/demomigr_2022_predbezna_2023t04.zip"
]


def get_age_group(age: Union[str, int]) -> str:
    """
    Get age group from age in different formats
    :param age: 0-7, 41-43, 44, 80 a více, 100+, Y_GE90, Y70T72
    :return: predefined groups in forma x-y
    """

    # Sčítání lidu
    if isinstance(age, int) or (isinstance(age, str) and age.isdigit()):
        age = [age, age]

    # DEMOMIGR
    elif "Y" in age:
        age = age.replace("Y_GE90", f"Y90T{MAX_AGE}")
        age = age.lstrip("Y").split("T")

    # Ockovani-demografie
    elif "-" in age or " a více" in age or "+" in age:
        age = age.replace(" a více", f"-{MAX_AGE}")
        age = age.replace("+", f"-{MAX_AGE}")
        age = age.split("-")

    for a1, a2 in AGE_CATEGORIES:
        if int(age[0]) >= a1 and int(age[1]) <= a2:
            return f"{a1}-{a2}"


def get_week(date: str) -> str:
    """
    Get week in form like DEMOMIGR from date from ockovani-demografie
    :param date: YYYY-MM-DD
    :return:
    """
    date = datetime.strptime(date, "%Y-%m-%d").isocalendar()
    return f"{date.year}-W{date.week:02d}"


def process_vaccination() -> None:
    """
    Process and "normalize" vaccination dataframe
    :return:
    """

    filename = os.path.join(DATA_FOLDER, VACCINATION_URL.split("/")[-1])
    df = pd.read_csv(filename)
    df = df.drop(columns=["id", "vakcina", "vakcina_kod", "pohlavi"])
    df = df.rename(columns={"datum": "tyden", "vekova_skupina": "vek"})
    df["vek"] = df["vek"].apply(get_age_group)
    df["tyden"] = df["tyden"].apply(get_week)
    df = df.groupby(["tyden", "vek", "poradi_davky"]).sum().reset_index()
    df = df.sort_values(by=["tyden"])
    df.to_csv(VACCINATION_FILE, index=False)
    os.remove(filename)


def process_counts() -> None:
    """
    Process and "normalize" counts dataframe
    :return:
    """

    counts_filename_xlsx = os.path.join(DATA_FOLDER, COUNTS_URL.split("/")[-1])
    counts_filename_csv = counts_filename_xlsx.replace(".xlsx", ".csv")
    pd.read_excel(counts_filename_xlsx).to_csv(counts_filename_csv, index=False)

    with open(counts_filename_csv) as f:
        lines = f.read().splitlines()
        lines = lines[5:-1]
        lines.pop(1)
        lines.pop(1)

    with open(counts_filename_csv, "w") as f:
        f.write("\n".join(lines))

    df = pd.read_csv(counts_filename_csv)
    df = df.iloc[:, [0, -3]]  # Select last celkem column and věk column
    df.columns = ["vek", "celkem"]
    df["vek"] = df["vek"].apply(get_age_group)
    df = df.groupby(["vek"]).sum().reset_index()
    df.to_csv(COUNTS_FILE, index=False)
    os.remove(counts_filename_xlsx)
    os.remove(counts_filename_csv)


def process_deaths() -> None:
    """
    Process and "normalize" deaths dataframe
    :return:
    """

    df_total = None
    for i in glob(os.path.join(DATA_FOLDER, "DEMOMIGR_*.csv")):
        df = pd.read_csv(i)
        df = df[df["pohlavi"] == "T"]  # We want just the sum, not sum + males + females
        df = df[df["uzemi"] == "CZ"]  # We want just the sum, not sum + regions
        df = df.drop(columns=["status", "uzemi_text", "vek_text", "pohlavi", "pohlavi_text", "status", "status_text"])

        if df_total is None:
            df_total = df
        else:
            df_total = pd.concat([df_total, df])

        os.remove(i)

    df_total["vek"] = df_total["vek"].apply(get_age_group)
    df_total = df_total.groupby(["tyden", "vek"]).sum().reset_index()
    df_total = df_total.sort_values(by=["tyden"])
    df_total = df_total.rename(columns={"hodnota": "umrti"})
    df_total.to_csv(DEATHS_FILE, index=False)


def download() -> None:
    """
    Download all files from URLS, unzip zip files and remove zip files
    :return:
    """

    os.makedirs(DATA_FOLDER, exist_ok=True)

    for url in tqdm(URLS, desc="Downloading files..."):
        filename = os.path.join(DATA_FOLDER, url.split("/")[-1])
        request.urlretrieve(url, filename)

        if ".zip" in filename:
            # Unzip and remove zip file
            os.system(f"unzip {filename} -d {DATA_FOLDER} && rm {filename}")


def delete_unwanted_data() -> None:
    """
    Delete data from files that are not in both files
    :return:
    """

    df_deaths = pd.read_csv(DEATHS_FILE)
    df_vaccination = pd.read_csv(VACCINATION_FILE)

    df_deaths = df_deaths[min(df_deaths[df_deaths["tyden"] == df_vaccination["tyden"][0]].index):]
    df_vaccination = df_vaccination[:max(df_vaccination[df_vaccination["tyden"] == df_deaths["tyden"].iloc[-1]].index) + 1]

    df_deaths.to_csv(DEATHS_FILE, index=False)
    df_vaccination.to_csv(VACCINATION_FILE, index=False)


if __name__ == "__main__":
    download()

    process_vaccination()
    process_counts()
    process_deaths()
    delete_unwanted_data()
