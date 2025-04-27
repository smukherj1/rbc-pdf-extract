import json
import base64
import requests
import os
import mysecrets
import glob


def pdf_to_csv(prompt: str, file_path: str, force: bool = False):
  out_csv = file_path.removesuffix(".pdf") + ".csv"
  if not force and os.path.exists(out_csv):
    return False
  model = "gemini-2.0-flash"
  api_url = "https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent?key={}".format(
      model, mysecrets.GEMINI_API_KEY)
  parts = [{"text": prompt}]
  with open(file_path, "rb") as fp:
    data = str(base64.b64encode(fp.read()), "utf-8")
    parts.append({"inlineData": {"mimeType": "application/pdf", "data": data}})
  body = {
      "contents": [{
          "parts": parts,
      }],
  }
  resp = requests.post(api_url, json=body)
  resp = json.loads(resp.text)
  texts = []
  for candidate in resp.get("candidates", []):
    for part in candidate.get("content", {}).get("parts", []):
      texts.append(part.get("text", "").strip())
  text = "\n".join(texts).removeprefix("```csv").removesuffix("```")
  with open(out_csv, "w") as ofp:
    ofp.write(text)
  return True


def acct_pdf2csv(force: bool = False):
  files = glob.glob("rbc_pdfs/**/*.pdf", recursive=True)
  prompt = """Extract transactions from the given monthly bank statement as a CSV with the following columns:
- "Date" with values in the format yyyy/mm/dd. Get the year from the line "Your opening balance on".
- "Description" with values inside double quotes.
- "Withdrawals" with values formatted as float with two decimal places. Do not put $ or , in the value.
- "Deposit" with values formatted as float with two decimal places. Do not put $ or , in the value.
- "Balance" with values formatted as float with two decimal places. Do not put $ or , in the value.
Only output the CSV and no other explanations."""
  for i, pdf in enumerate(files):
    print("Processing {}/{}: {}.".format(i + 1, len(files), pdf))
    if pdf_to_csv(prompt=prompt, file_path=pdf, force=force):
      print("-- Ok")
    else:
      print("-- Skipped")


def cc_pdf2csv(force: bool = False):
  files = glob.glob("rbc_cc_pdfs/**/*.pdf", recursive=True)
  prompt = """Extract transactions from the given monthly credit card statement as a CSV with the following columns:
- "Transaction Date" with values in the format yyyy/mm/dd. Get the year from the line "Statement from month day to month day, year".
- "Posting Date" with values in the format yyyy/mm/dd. Get the year from the line "Statement from month day to month day, year".
- "Activity Description" with values inside double quotes.
- "Amount" with values formatted as float with two decimal places. Do not put $ or , in the value.
Only output the CSV and no other explanations."""
  for i, pdf in enumerate(files):
    print("Processing {}/{}: {}.".format(i + 1, len(files), pdf))
    if pdf_to_csv(prompt=prompt, file_path=pdf, force=force):
      print("-- Ok")
    else:
      print("-- Skipped")


if __name__ == "__main__":
  force = False
  acct_pdf2csv(force=force)
  cc_pdf2csv(force=force)
