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
from publications.models import Intervention

# Load a csv file with the list to be added to the database.
csv = "publications/data/interventions 2.0.csv"
df = pd.read_csv(csv, encoding="utf-8")

for row in df.itertuples():
    level1 = row.Level1
    level1, created = Intervention.objects.get_or_create(intervention=level1)
    level2 = row.Level2
    if not pd.isnull(level2):
        level2, created = Intervention.objects.get_or_create(intervention=level2, parent=level1)
    level3 = row.Level3
    if not pd.isnull(level3):
        level3, created = Intervention.objects.get_or_create(intervention=level3, parent=level2)
    level4 = row.Level4
    if not pd.isnull(level4):
        level4, created = Intervention.objects.get_or_create(intervention=level4, parent=level3)
    level5 = row.Level5
    if not pd.isnull(level5):
        level5, created = Intervention.objects.get_or_create(intervention=level5, parent=level4)
    level6 = row.Level6
    if not pd.isnull(level6):
        level6, created = Intervention.objects.get_or_create(intervention=level6, parent=level5)
    level7 = row.Level7
    if not pd.isnull(level7):
        level7, created = Intervention.objects.get_or_create(intervention=level7, parent=level6)
