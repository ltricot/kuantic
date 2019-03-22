import pandas as pd
import sys


if __name__ == '__main__':
    df = pd.read_csv('data/Global Vehicle Description.csv')
    df.index = df.Kuantic_id
    print(df.loc[sys.argv[1]])

