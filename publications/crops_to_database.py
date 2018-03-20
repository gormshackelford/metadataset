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
from publications.models import Crop

# Load a csv file with the list to be added to the database.
csv = "publications/data/crops.csv"
df = pd.read_csv(csv, encoding="utf-8")

for row in df.itertuples():
    level1 = row.Level1
    level1, created = Crop.objects.get_or_create(crop=level1)
    level2 = row.Level2
    if not pd.isnull(level2):
        level2, created = Crop.objects.get_or_create(crop=level2, parent=level1)
    level3 = row.Level3
    if not pd.isnull(level3):
        level3, created = Crop.objects.get_or_create(crop=level3, parent=level2)
    level4 = row.Level4
    if not pd.isnull(level4):
        level4, created = Crop.objects.get_or_create(crop=level4, parent=level3)
