import pandas as pd

df = pd.read_csv("intern_dataset.csv")
df.to_excel("interns.xlsx", index=False)
print("Done! interns.xlsx created with", len(df), "interns.")