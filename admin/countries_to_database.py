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
from publications.models import Country

# Load a csv file with the list to be added to the database.
csv = "./publications/data/un_m49_countries.csv"
df = pd.read_csv(csv, encoding="utf-8")

for result in df.itertuples():
    country = result.country
    un_m49 = result.un_m49
    iso_alpha_3 = result.iso_alpha_3
    record = Country(country=country, un_m49=un_m49, iso_alpha_3=iso_alpha_3)
    record.save()
