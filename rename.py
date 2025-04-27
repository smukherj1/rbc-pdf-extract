import glob
import os

if __name__ == "__main__":
  files = glob.glob("rbc_cc_pdfs/**", recursive=True) + glob.glob(
      "rbc_pdfs/**", recursive=True)
  print("{} files.".format(len(files)))
  for f in files:
    o = f.replace(" ", "-")
    if o == f:
      continue
    print("{} -> {}".format(f, o))
    os.rename(f, o)
