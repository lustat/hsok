import datetime
import os
import pandas as pd
from base_utils import rel2fullpath
from dateutil.relativedelta import relativedelta
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
import collections
import seaborn as sns


def load_member_data(relative_excel_path: str, year_to_sheet: collections.defaultdict):
    input_file = rel2fullpath(relative_excel_path)

    df = pd.read_excel(input_file, sheet_name=year_to_sheet[year])
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
    df = df.assign(binned=[str(age_bin) for age_bin in df.binned])
    return df


if __name__ == '__main__':
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    years = [2019, 2020]
    year_to_sheet_name = collections.defaultdict(lambda: 'SearchPersons')
    year_to_sheet_name[2019] = 'Data'
    excel_flag = False

    summary = pd.DataFrame()
    for year in years:
        excel_file = 'data/members/ExportedPersons_' + str(year) + '.xlsx'
        df = load_member_data(excel_file, year_to_sheet_name)

        count_df = df[['kon', 'binned', 'fornamn']].groupby(by=['kon', 'binned']).count()
        count_df = count_df.reset_index()
        count_df.columns = ['Kön', 'Ålder', 'Antal']
        count_df = count_df.assign(**{'År': year})
        summary = pd.concat([summary, count_df], axis=0)
        print(summary)

        if excel_flag:
            df_out = df[['fornamn', 'efternamn', 'fodelsedat_personnr', 'kon', 'age', 'binned']]
            print(df_out)

            output_excel = rel2fullpath(os.path.join(os.path.split(excel_file)[0], 'PersonAges_' + str(year) + '.xlsx'))
            wb = openpyxl.Workbook()
            worksheet = wb.create_sheet('Data')
            for r in dataframe_to_rows(df_out, index=False, header=True):
                worksheet.append(r)

            worksheet = wb.create_sheet('Stat')
            for r in dataframe_to_rows(count_df, index=False, header=True):
                worksheet.append(r)

            wb.save(output_excel)

    year_sex_total = summary.groupby(["Kön", 'År']).sum().reset_index(drop=False)

    g = sns.catplot(
        data=year_sex_total, kind="bar",
        x="År", y="Antal", hue="Kön",
        palette="dark", alpha=.6, height=6
    )
    g.despine(left=True)
    g.set_axis_labels("", "Antal")
    g.legend.set_title("")
    g.savefig('yearly_overview.png')

    this_year = summary.loc[summary['År'] == summary['År'].max()]

    g = sns.catplot(
        data=this_year, kind="bar",
        x="Ålder", y="Antal", hue="Kön",
        palette="dark", alpha=.6, height=6
    )
    g.despine(left=True)
    g.set_axis_labels("", "Antal")
    g.legend.set_title("")
    g.savefig('this_year.png')
    print('Finished')

