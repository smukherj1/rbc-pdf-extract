import glob
import os

if __name__ == "__main__":
  files = glob.glob("rbc_cc_pdfs/**/*.Identifier", recursive=True) + glob.glob(
      "rbc_pdfs/**/*.Identifier", recursive=True)
  print("Found {} junk files.".format(len(files)))
  for f in files:
    print("Removing {}".format(f))
    os.remove(f)
