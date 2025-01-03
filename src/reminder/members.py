import pandas as pd
from definitions import SOURCE_DIR

member_file = f'{SOURCE_DIR}/reminder/ExportedPersons_20240421.xlsx'
not_paid_file = f'{SOURCE_DIR}/reminder/not_paid.xlsx'
remind_file = f'{SOURCE_DIR}/reminder/remind.csv'


members = pd.read_excel(member_file)
members.columns = ['first_name', 'last_name', 'idrotts_id', 'email']

not_paid = pd.read_excel(not_paid_file)
not_paid.columns = ['email']

print(members)
print(not_paid)

member_email = set(members.email.str.lower())
not_paid_email = set(not_paid.email.str.lower())

remind = list(member_email & not_paid_email)
df = pd.DataFrame(data={'remind': remind})
df.to_csv(remind_file, index=False)
