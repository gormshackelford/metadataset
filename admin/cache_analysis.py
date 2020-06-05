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

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from publications.models import Subject, Intervention, Outcome, Analysis


# To get selenium to work on pythonanywhere.com, use this version of selenium:
# pip3.6 install selenium==2.53.6
# To run this script from the console, use this command (in the venv):
# xvfb-run -a python cache_analysis.py


try:
    subject = Subject.objects.get(subject = "Cover crops")
    driver = webdriver.Firefox()
    driver.implicitly_wait(60)
    driver.get('https://www.metadataset.com/subject/cover-crops/browse-by-outcome/data/')
    #driver.get('http://127.0.0.1:8000/subject/cover-crops/browse-by-outcome/data/')

    link_text = "Expand all"
    link = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable((By.LINK_TEXT, link_text))
    )
    link.click()  # Expand all

    root_node = driver.find_element_by_css_selector("ul.root")
    nodes = root_node.find_elements_by_tag_name("li")  # All outcomes
    n_nodes = len(nodes)  # Number of outcomes

    for i in range(n_nodes):  # For each outcome
        # Elements in the DOM need to be found again each time the web page is reloaded.
        link_text = "Expand all"
        link = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.LINK_TEXT, link_text))
        )
        link.click()  # Expand all

        root_node = driver.find_element_by_css_selector("ul.root")
        nodes = root_node.find_elements_by_tag_name("li")  # All outcomes
        node = nodes[i]  # This outcome
        links = node.find_elements_by_tag_name("a")
        link = links[1]  # Link for "filter by intervention"
        link.click()  # Filter by intervention.

        link_text = "Expand all"
        link = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.LINK_TEXT, link_text))
        )
        link.click()  # Expand all

        root_node = driver.find_element_by_css_selector("ul.root")
        nodes = root_node.find_elements_by_tag_name("li")  # All interventions for this outcome
        n_nodes = len(nodes)  # Number of interventions

        for j in range(n_nodes):  # For each intervention
            # Elements in the DOM need to be found again each time the web page is reloaded.
            link_text = "Expand all"
            link = WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable((By.LINK_TEXT, link_text))
            )
            link.click()  # Expand all

            root_node = driver.find_element_by_css_selector("ul.root")
            nodes = root_node.find_elements_by_tag_name("li")  # All interventions for this outcome
            node = nodes[j]  # This intervention
            links = node.find_elements_by_tag_name("a")
            link = links[0]  # Link to launch the Shiny app for this data (this intervention and this outcome)
            href = link.get_attribute("href")  # link.click() does not work here (the driver does not go to the new tab).
            href = href + "&refresh"  # Refresh the data to delete and recreate the cache.
            driver.get(href)  # Launch the Shiny app.

            wait_for_data_to_load = WebDriverWait(driver, 600).until(         # Wait for up to 10 minutes for the data to load.
                EC.element_to_be_clickable((By.XPATH, "//*[@id='column_names']"))
            )
            time.sleep(2)
            button = WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable((By.ID, "go"))       # Button for "Start your analysis"
            )
            button.click()  # Start your analysis.
            try:
                effect_size = WebDriverWait(driver, 600).until(     # Wait for up to 10 minutes for the analysis to finish.
                    EC.presence_of_element_located((By.XPATH, "//*[@id='effect_size']"))
                )
                effect_size = float(effect_size.get_attribute("innerHTML"))
                pval = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.XPATH, "//*[@id='pval']"))
                )
                pval = float(pval.get_attribute("innerHTML"))
                lb = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.XPATH, "//*[@id='lb']"))
                )
                lb = float(lb.get_attribute("innerHTML"))
                ub = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.XPATH, "//*[@id='ub']"))
                )
                ub = float(ub.get_attribute("innerHTML"))
                there_was_an_error = False
            except:
                there_was_an_error = True
            intervention_pk = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='intervention_pk']"))
            )
            try:
                intervention_pk = int(intervention_pk.get_attribute("innerHTML"))
                intervention = Intervention.objects.get(pk=intervention_pk)
            except:
                intervention = subject.intervention  # The root intervention for this subject (if no intervention was specified)
            outcome_pk = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='outcome_pk']"))
            )
            try:
                outcome_pk = int(outcome_pk.get_attribute("innerHTML"))
                outcome = Outcome.objects.get(pk=outcome_pk)
            except:
                outcome = subject.outcome  # The root outcome for this subject (if no outcome was specified)
            api_query_string = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='api_query_string']"))
            )
            api_query_string = api_query_string.get_attribute("textContent")
            user_settings = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='user_settings']"))
            )
            user_settings = user_settings.get_attribute("textContent")
            button = WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable((By.ID, "make_bookmark"))  # Button for "Bookmark your analysis"
            )
            button.click()
            shiny_bookmark = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.ID, "shiny_bookmark"))
            )
            shiny_bookmark = shiny_bookmark.get_attribute("textContent")
            obj, created = Analysis.objects.get_or_create(
                subject = subject,
                intervention = intervention,
                outcome = outcome,
                api_query_string = api_query_string,
                user_settings = user_settings
            )
            obj.effect_size = float(effect_size)
            obj.pval = float(pval)
            obj.lb = float(lb)
            obj.ub = float(ub)
            obj.shiny_bookmark = shiny_bookmark
            obj.there_was_an_error = there_was_an_error
            obj.save()
            print(api_query_string)
            driver.back()
        driver.back()
finally:
    driver.quit()
