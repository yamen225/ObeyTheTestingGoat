from selenium import webdriver
import unittest


class NewVisitorTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_can_start_a_list_and_retrieve_it_later(self):

        # Edith checks her homepage

        self.browser.get('http://localhost:8000')

        # notice page title mention to do lists
        self.assertIn('To-Do', self.browser.title)
        self.fail('Finish the test!')
        # Invited to enter a to do item

        # Types "Buy peacock feathers" in a text box

        # hits enter, the page lists
        # " 1: Buy peacock feathers" as an item

        # there's still a text box to add a new item

        # enters "Use peacock fweathers to make a fly"

        # page reloads and lists both items

        # Edith wonders whether the site will remember her list. Then she sees
        # that the site has generated a unique URL for her -- there is some
        # explanatory text to that effect.

        # She visits that URL - her to-do list is still there.

        # Satisfied, she goes back to sleep


if __name__ == '__main__':
    unittest.main(warnings='ignore')
