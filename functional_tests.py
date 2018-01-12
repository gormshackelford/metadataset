from selenium import webdriver
import unittest


class NewVisitorTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    # The user loads the home page and finds the site name in the title.
    def test_can_load_home(self):
        self.browser.get('http://localhost:8000')
        self.assertIn('MetaDataSet', self.browser.title)

    # She signs in.

    # She creates a new systematic review.

    # She uploads a bibliography as an ris file.

    # She user creates a list of populations (the "P" in a "PICO" experiment).

    # She creates a list of interventions (the "I" in a "PICO" experiment).

    # She creates a list of outcomes (the "O" in a "PICO" experiment) for each population.

    # She creates a list of comparisons (the "C" in a "PICO" experiment).

    # She tags each publication as relevant or not relevant to her systematic review (if she creates new systematic reviews, these are added to the dropdown list, any of her publications can be tagged as relevant to any of her reviews).

    # She enters the PICO metadata and statitical data for each publication.

    # Other users can see her work, but cannot edit it unless she gives them permission.

    # Other users can aggregate data from multiple reviews, based on their metadata.


    def test_can_enter_data_for_a_publication(self):
        self.browser.get('http://localhost:8000')
        # The user finds a table in which to enter data.
        data_entry_table = self.browser.find_element_by_tag_name('table')
        data_entry_table = self.browser.find_element_by_id('publication')

if __name__ == '__main__':
    unittest.main()
