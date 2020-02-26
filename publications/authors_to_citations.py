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


import re
from ast import literal_eval
from publications.models import Publication, Subject

#for publication in Publication.objects.all():
subject = Subject.objects.get(subject="spartina")
for publication in Publication.objects.filter(subject=subject):
    #if (publication.citation == ""):

    citation = ""

    # Authors should be stored as a Python list in this format: ['Darwin, C.', 'Wallace, A. R.']
    try:
        authors = literal_eval(publication.authors)
    except:
        authors = "NA"
    year = publication.year
    if (year == ""):
        year = "[YEAR]"

    # Uncomment one of these lines to test different cases.
    #authors = ['Darwin, C.', 'Wallace, A. R.']
    #authors = ['Darwin, C', 'Wallace, A R']
    #authors = ['Darwin, C', 'Wallace, AR']
    #authors = ['C., Darwin', 'A. R., Wallace']
    #authors = ['C, Darwin', 'A R, Wallace']
    #authors = ['C, Darwin', 'AR, Wallace']
    #authors = ['C Darwin', 'AR Wallace']
    #authors = ['van Bruggen, A.', 'Darwin, C.', 'Wallace, A.R.']
    #authors = ['A., van Bruggen', 'Darwin, C.', 'Wallace, A.R.']
    #authors = ["O'Hara, S."]
    #authors = "O'Hara"

    n = len(authors)
    if (n == 2):
        i = 2     # If there are two authors, get the last names of both.
    else:
        i = 1     # If there is one author, or there are more than two, get the last name of the first author only.

    for j in range(i):
        if (citation != ""):
            citation = citation + " & "
        # Author j
        author = authors[j]
        if (re.search(",", author)):         # If the string includes a comma (e.g., "Darwin, C.")
            author = re.split(",", author)   # Split the string (at commas) into a list of words (could be more than one comma if there are errors).
            # Some names are not in the correct format (e.g., the initials come before the last name; e.g., "A. R., Wallace" or "A. R. Wallace").
            # Check if each string is likely to be a last name.
            # We assume a last name does not include a period, and is not one letter by itself, one letter followed by a space and then one letter, two capital letters, or two lowercase letters.
            # For example, we assume "O.", "O. H.", "O", "o", "O H", and "OH" are not last names (but we assume "O'Hara" and "O Hara" are last names).
            last_name = ""
            for name in author:
                if (last_name == ""):
                    if (re.search("\.", name) is None):  # If the name does not include a period
                        if ((re.search("^\s*[a-zA-Z]\s*$", name) is None) and              # If the name is not one letter, with or without spaces around it (e.g., "C" or " C ")
                            (re.search("^\s*[a-zA-Z]+\s+[a-zA-Z]\s*$", name) is None) and  # If the name is not one or more letters followed by one or more spaces and then one letter (e.g., "A R", "A  R", or "Alfred R")
                            (re.search("^\s*[A-Z]{2}\s*$", name) is None)):                # If the name is not two capital letters (e.g., "AR") (could be a problem for two-letter last names, such as "Ng", if they are entered in all capitals)
                                last_name = last_name + name.strip()
            citation = citation + last_name
        else:
            name = re.sub("\\b[A-Z]{1}\\b", "", author)     # Remove isolated letters
            name = re.sub("\.", "", name)        # Remove periods
            name = re.sub("\\b[A-Z]{2}\\b", "", name)  # Remove two capitals in a row
            if (re.sub(" ", "", name) != ""):
                citation = citation + name.strip()
    if (n > 2):
        if (citation != ""):
            citation = citation + " et al."
    if (citation == ""):
        citation = "[AUTHOR]"
    citation = citation + ", " + year
    print(citation)
    try:
        publication.citation = citation
        publication.save()
    except:
        pass
