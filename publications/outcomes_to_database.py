# Run this script as a "standalone" script (terminology from the Django
# documentation) that uses the Djano ORM to get data from the database.
# This requires django.setup(), which requires the settings for this project.
# Appending the root directory to the system path also prevents errors when
# importing the models from the app.
if __name__ == '__main__':
    import sys
    import os
    import django
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
        os.path.pardir))
    sys.path.append(parent_dir)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "metadataset.settings")
    django.setup()


import pandas as pd
from publications.models import Outcome

# Load a csv file with the list to be added to the database.
csv = "publications/data/outcomes.csv"
df = pd.read_csv(csv, encoding="utf-8")

for row in df.itertuples():
    code = str(row.Code1) + '.'
    level1 = row.Level1
    level1, created = Outcome.objects.get_or_create(outcome=level1, code=code)
    code = code + str(row.Code2) + '.'
    level2 = row.Level2
    if not pd.isnull(level2):
        level2, created = Outcome.objects.get_or_create(outcome=level2, code=code, parent=level1)
    code = code + str(row.Code3) + '.'
    level3 = row.Level3
    if not pd.isnull(level3):
        level3, created = Outcome.objects.get_or_create(outcome=level3, code=code, parent=level2)
    level4 = row.Level4
    if not pd.isnull(level4):
        level4, created = Outcome.objects.get_or_create(outcome=level4, code='', parent=level3)
    level5 = row.Level5
    if not pd.isnull(level5):
        level5, created = Outcome.objects.get_or_create(outcome=level5, code='', parent=level4)
    level6 = row.Level6
    if not pd.isnull(level6):
        level6, created = Outcome.objects.get_or_create(outcome=level6, code='', parent=level5)
    level7 = row.Level7
    if not pd.isnull(level7):
        level7, created = Outcome.objects.get_or_create(outcome=level7, code='', parent=level6)
