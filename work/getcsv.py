import pandas as pd

df = pd.read_json("20170801-0808.txt")

df.to_csv("data.csv")
