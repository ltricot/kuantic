import pandas as pd
import os


cdir = os.path.dirname(__file__)
specpath = os.path.join(
    os.path.split(cdir)[0],
    'data', 'dataspecparis.csv'
)


spec = pd.read_csv(specpath)
errs = spec.Tags.str.contains('((Failure)|(Warning))',
regex=True).fillna(False)

events = list(spec['Fields Name'][errs])


if __name__ == '__main__':
    print('\n'.join(events))

