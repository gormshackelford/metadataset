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
from publications.models import Publication


# Load a csv file with the bibliography (exported from Zotero).
csv = "publications/data/bibliography.csv"
df = pd.read_csv(csv, encoding='utf-8')
df = df.rename(columns={
    'Abstract Note': 'Abstract',
    'Publication Title': 'Publication',
})

for result in df.itertuples():
    title = result.Title
    abstract = result.Abstract
    authors = result.Authors
    year = result.Date
    journal = result.Publication
    volume = result.Volume
    issue = result.Issue
    pages = result.Pages
    doi = result.DOI
    url = result.Url
    publisher = result.Publisher
    place = result.Place

    # Check that the data do not exceed the maximum lengths in the database. They should not, except in the case of errors in the data (or metadata in the same field). If the length is exceeded, delete the excess.
    if len(title) > 510:
        title = title[0:510]
    if len(str(year)) > 30:
        year = year[0:30]
    if len(journal) > 510:
        journal = journal[0:510]
    if len(str(issue)) > 30:
        issue = issue[0:30]
    if len(str(volume)) > 30:
        volume = volume[0:30]
    if len(pages) > 30:
        pages = pages[0:30]
    if len(doi) > 510:
        doi = ''  # A broken DOI will not work, whereas truncated data in the the other fields could be informative.

    record = Publication(
        title=title,
        abstract=abstract,
        author=author_string,
        year=year,
        journal=journal,
        volume=volume,
        issue=issue,
        pages=pages,
        doi=doi,
        url=url,
        publisher=publisher,
        place=place
    )
    record.save()
