import os
import datetime
import pandas as pd
from base_utils import rel2fullpath
import matplotlib.pyplot as plt


def anonymize(df):
    df = df.drop(columns=['born', 'name'])
    return df


def pick_youths(df: pd.DataFrame, born_column: str, this_year: int):
    df = df.assign(age=this_year - df[born_column])
    df = df.loc[df.age <= 16]
    df = df.drop(columns=['age'])
    return df


def pick_day(df: pd.DataFrame, chosen_days: list, year: int):
    date_columns = [column for column in df.columns if column.startswith(str(year))]

    remove_columns = []
    for column in date_columns:
        day = datetime.datetime.strptime(column, '%Y-%m-%d').strftime('%A')
        if day not in chosen_days:
            remove_columns.append(column)

    df = df.drop(columns=remove_columns)
    return df


def get_thursday_stats(relative_excel_path: str, year: int):
    input_file = rel2fullpath(relative_excel_path)

    df = pd.read_excel(input_file, sheet_name='Aktiviteter per person och dag')
    original_columns = df.columns
    new_columns = [column.lower().replace('.', '').replace(' ', '_').replace('/', '_').replace(':', '')
                  for column in df.columns]
    df.columns = [column.lower().replace('å', 'a').replace('ä', 'a').replace('ö', 'o')
                  for column in new_columns]

    orig_to_cleaned = {'1(0)': 0,
                       '2(0)': 0,
                       '1(1)': 1,
                       '2(1)': 1}

    df = df.replace(orig_to_cleaned).fillna(0)
    df = df.rename(columns={'namn': 'name', 'fodd': 'born'})

    df = pick_youths(df, 'born', year)
    df = pick_day(df, ['Thursday'], year)
    df = anonymize(df)

    daily_total = df.sum(axis=0)
    daily_total = daily_total[daily_total > 12]

    figure_file = os.path.join(os.path.split(input_file)[0], 'stats_' + str(year) + '.png')
    fig, ax = plt.subplots(1, 1, figsize=(14, 6))
    plt.subplots_adjust(bottom=0.25)
    plt.bar(daily_total.index, daily_total)
    plt.ylabel('Antal ungdomar')
    plt.xticks(rotation=45, ha='right')
    # xticklabels = ax.get_xticklabels()
    # ax.set_xticklabels(xticklabels, rotation=45, ha='right')
    plt.title('Statistik för torsdagsträningar, medel = ' + str(round(daily_total.mean(), 1)))
    plt.savefig(figure_file)
    plt.close(fig)

    return df


if __name__ == '__main__':
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    excel_file = 'data/Aktiviteter_ per_person_och_dag_2020.xlsx'
    # output_excel = rel2fullpath(os.path.join(os.path.split(excel_file)[0], 'PersonAges_2019.xlsx'))
    df0 = get_thursday_stats(excel_file, year=2020)
