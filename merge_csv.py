import pandas as pd
from pandas.api.types import is_float_dtype
import glob
from datetime import datetime


def canon_date(d: str) -> str:
  try:
    return datetime.strptime(d, "%Y/%m/%d").strftime("%Y/%m/%d")
  except ValueError:
    pass
  try:
    return datetime.strptime(d, "%B %d, %Y").strftime("%Y/%m/%d")
  except ValueError:
    pass
  try:
    return datetime.strptime(d, "%Y-%m-%d").strftime("%Y/%m/%d")
  except ValueError:
    pass
  raise ValueError("unsupported date format: {}".format(d))


def clean_date_column(df: pd.DataFrame, column: str):
  d = pd.to_datetime(df[column], format="%Y/%m/%d", errors="coerce").min()
  if pd.isna(d):
    raise RuntimeError("no valid dates in column {}".format(column))
  for i in range(len(df)):
    cur = df.loc[i, column]
    if pd.isna(cur):
      df.loc[i, column] = d
      continue
    try:
      d = canon_date(cur)
    except ValueError:
      pass
    df.loc[i, column] = d


def from_csv(csv_file):
  print("Reading {}".format(csv_file))
  df = pd.read_csv(csv_file)
  clean_date_column(df, "Date")
  df["Withdrawals"] = df["Withdrawals"].astype(float)
  df["Deposit"] = df["Deposit"].astype(float)
  df.fillna(value={"Withdrawals": 0.0, "Deposit": 0.0}, inplace=True)
  df["Description"] = df["Description"].apply(lambda d: d.replace("\n", " "))
  return df


def from_cc_csv(csv_file):
  print("Reading {}".format(csv_file))
  df = pd.read_csv(csv_file)
  clean_date_column(df, "Transaction Date")
  clean_date_column(df, "Posting Date")
  df["Amount"] = df["Amount"].astype(float)
  return df


def rbc_chequing():
  csv_files = glob.glob("rbc_pdfs/**/*.csv", recursive=True)
  dfs = [from_csv(f) for f in csv_files]
  df = pd.concat(dfs, ignore_index=True)
  df["Amount"] = (df["Withdrawals"] * -1.0) + df["Deposit"]
  df.drop(columns=["Withdrawals", "Deposit"], inplace=True)
  df = df[["Date", "Description", "Amount", "Balance"]]
  df.sort_values(by=["Date"], ascending=True, kind="mergesort", inplace=True)
  df.to_csv("rbc_chequing.csv", index=False)


def rbc_mastercard():
  cc_csv_files = glob.glob("rbc_cc_pdfs/**/*.csv", recursive=True)
  dfs = [from_cc_csv(f) for f in cc_csv_files]
  df = pd.concat(dfs, ignore_index=True)
  # Make purchases on credit card negative, credits positive.
  df["Amount"] = df["Amount"] * -1
  # Filter out automatic payment to pay off credit card balance.
  df = df[df["Activity Description"] != "AUTOMATIC PAYMENT - THANK YOU"]
  df.sort_values(by=["Transaction Date"],
                 ascending=True,
                 kind="mergesort",
                 inplace=True)
  df.rename(columns={"Activity Description": "Description"}, inplace=True)
  df.to_csv("rbc_mastercard.csv", index=False)


if __name__ == "__main__":
  rbc_chequing()
  rbc_mastercard()
