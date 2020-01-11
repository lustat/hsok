import datetime
import pandas as pd
from base_utils import rel2fullpath
from dateutil.relativedelta import relativedelta


if __name__ == '__main__':
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    input_file = rel2fullpath('data/members/ExportedPersons_2019.xlsx')
    print(input_file)
    df = pd.read_excel(input_file, sheet_name='Data')
    original_columns = df.columns
    new_columns = [column.lower().replace('.', '').replace(' ', '_').replace('/', '_').replace(':', '')
                  for column in df.columns]
    df.columns = [column.lower().replace('å', 'a').replace('ä', 'a').replace('ö', 'o')
                  for column in new_columns]

    df = df.assign(birth_date=[datetime.datetime.strptime(day, '%Y-%m-%d') for day in df.fodelsedat_personnr])
    today = datetime.datetime(2019, 12, 31)
    df = df.assign(age=[relativedelta(today, birth).years for birth in df.birth_date])

    # Binned age
    age_splits = [-1, 7, 12, 16, 20, 25, 100000]
    labels = ['0-7', '8-12', '13-16', '17-20', '21-25', '26+']
    df = df.assign(binned=pd.cut(df['age'], bins=age_splits, labels=labels))

    print(df)

    count_df = df[['kon', 'binned', 'fornamn']].groupby(by=['kon', 'binned']).count()
    count_df = count_df.reset_index()
    count_df.columns = ['Kön', 'Ålder', 'Antal']

    print(count_df)
    print('Finished')

    # Create output Excel

