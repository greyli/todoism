# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
import os
import time
import unittest

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


class UserInterfaceTestCase(unittest.TestCase):

    def setUp(self):
        os.environ['MOZ_HEADLESS'] = '1'
        # or use this:
        # options = webdriver.FirefoxOptions()
        # options.add_argument('headless')
        self.client = webdriver.Firefox()
        time.sleep(1)

        if not self.client:
            self.skipTest('Web browser not available.')

    def tearDown(self):
        if self.client:
            self.client.quit()

    def login(self):
        self.client.get('http://localhost:5000')
        time.sleep(2)
        # navigate to login page
        self.client.find_element_by_link_text('Get Started').click()
        time.sleep(1)
        self.client.find_element_by_name('username').send_keys('grey')
        self.client.find_element_by_name('password').send_keys('123')
        self.client.find_element_by_id('login-btn').click()
        time.sleep(1)

    def test_index(self):
        self.client.get('http://localhost:5000')  # navigate to home page
        time.sleep(2)
        self.assertIn('We are todoist, we use todoism.', self.client.page_source)

    def test_login(self):
        self.login()
        self.assertIn('What needs to be done?', self.client.page_source)

    def test_new_item(self):
        self.login()
        all_item_count = self.client.find_element_by_id('all-count')
        before_count = int(all_item_count.text)

        item_input = self.client.find_element_by_id('item-input')
        item_input.send_keys('Hello, World')
        item_input.send_keys(Keys.RETURN)
        time.sleep(1)

        after_count = int(all_item_count.text)
        self.assertIn('Hello, World', self.client.page_source)
        self.assertEqual(after_count, before_count + 1)

    def test_delete_item(self):
        self.login()
        all_item_count = self.client.find_element_by_id('all-count')
        before_count = int(all_item_count.text)

        item1 = self.client.find_element_by_xpath("//span[text()='test item 1']")
        hover_item1 = ActionChains(self.client).move_to_element(item1)
        hover_item1.perform()
        delete_button = self.client.find_element_by_class_name('delete-btn')
        delete_button.click()

        after_count = int(all_item_count.text)
        self.assertNotIn('test item 1', self.client.page_source)
        self.assertIn('test item 2', self.client.page_source)
        self.assertEqual(after_count, before_count - 1)

    def test_edit_item(self):
        self.login()
        time.sleep(1)

        try:
            item = self.client.find_element_by_xpath("//span[text()='test item 1']")
            item_body = 'test item 1'
        except NoSuchElementException:
            item = self.client.find_element_by_xpath("//span[text()='test item 2']")
            item_body = 'test item 2'

        hover_item = ActionChains(self.client).move_to_element(item)
        hover_item.perform()
        edit_button = self.client.find_element_by_class_name('edit-btn')
        edit_button.click()
        edit_item_input = self.client.find_element_by_id('edit-item-input')
        edit_item_input.send_keys(' edited')
        edit_item_input.send_keys(Keys.RETURN)
        time.sleep(1)
        self.assertIn('%s edited' % item_body, self.client.page_source)

    def test_get_test_account(self):
        self.client.get('http://localhost:5000')
        time.sleep(2)
        self.client.find_element_by_link_text('Get Started').click()
        time.sleep(1)
        self.client.find_element_by_id('register-btn').click()
        self.client.find_element_by_id('login-btn').click()
        time.sleep(1)
        self.assertIn('What needs to be done?', self.client.page_source)

    def test_change_language(self):
        self.skipTest(reason='skip for materialize toast div overlay issue')
        self.login()
        self.assertIn('What needs to be done?', self.client.page_source)

        self.client.find_element_by_id('locale-dropdown-btn').click()
        # ElementClickInterceptedException: Message: Element <a class="lang-btn"> is not clickable at point
        # (1070.4000244140625,91.75) because another element <div id="toast-container"> obscures it
        self.client.find_element_by_link_text(u'简体中文').click()

        time.sleep(1)
        self.assertNotIn('What needs to be done?', self.client.page_source)
        self.assertNotIn(u'你要做些什么？', self.client.page_source)

    def test_toggle_item(self):
        self.skipTest(reason='wait for fix')

        self.login()
        all_item_count = self.client.find_element_by_id('all-count')
        active_item_count = self.client.find_element_by_id('active-count')
        before_all_count = int(all_item_count.text)
        before_active_count = int(active_item_count.text)

        self.client.find_element_by_xpath("//a[@class='done-btn'][1]").click()
        time.sleep(1)

        after_all_count = int(all_item_count.text)
        after_active_count = int(active_item_count.text)
        self.assertEqual(after_all_count, before_all_count - 1)
        self.assertEqual(after_active_count, before_active_count + 1)

    def test_clear_item(self):
        self.login()
        all_item_count = self.client.find_element_by_id('all-count')
        before_all_count = int(all_item_count.text)

        self.client.find_element_by_id('clear-btn').click()

        after_all_count = int(all_item_count.text)
        self.assertEqual(after_all_count, before_all_count - 1)
