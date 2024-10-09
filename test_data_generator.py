from datetime import datetime, timedelta
from unittest import TestCase

from faker import Faker

from scripts.data_generator import FileBasedOrgProvider, make_datetime


class FileBasedOrgProviderTests(TestCase):
    """Tests the custom provider"""

    def setUp(self):
        self.faker = Faker("en_UK")
        self.faker.add_provider(FileBasedOrgProvider)

    def test_selects_valid_org(self):
        """Test a valid org id returns the right data"""
        test_id = 3
        expected_name = "GenoMap"
        expected_description = (
            "Navigating the landscape of genetic " "information."
        )

        self.assertEqual(expected_name, self.faker.org_name(test_id))
        self.assertEqual(
            expected_description, self.faker.org_description(test_id)
        )

    def test_org_name_when_invalid_org_index(self):
        """org_name with an invalid org id returns a useful exception"""
        test_id = -1
        expected_message_negative = "Org ids must be positive integers"
        with self.assertRaises(IndexError) as context:
            self.faker.org_name(test_id)
        actual_message = str(context.exception)
        self.assertEqual(actual_message, expected_message_negative)

        new_test_id = 51
        expected_message_over = (
            "There are only 50 organisations so pass "
            "an org_id between 1 and 50"
        )
        with self.assertRaises(IndexError) as context:
            self.faker.org_name(new_test_id)
        actual_message = str(context.exception)
        self.assertEqual(actual_message, expected_message_over)

    def test_org_description_when_invalid_org_index(self):
        """org_description with an invalid org id returns a useful
        exception"""
        test_id = -1
        expected_message_negative = "Org ids must be positive integers"
        with self.assertRaises(IndexError) as context:
            self.faker.org_description(test_id)
        actual_message = str(context.exception)
        self.assertEqual(actual_message, expected_message_negative)

        new_test_id = 51
        expected_message_over = (
            "There are only 50 organisations so pass "
            "an org_id between 1 and 50"
        )
        with self.assertRaises(IndexError) as context:
            self.faker.org_description(new_test_id)
        actual_message = str(context.exception)
        self.assertEqual(actual_message, expected_message_over)


class MakeDateTimeTests(TestCase):
    """Tests the make_datetime function"""

    def setUp(self):
        self.faker = Faker("en_UK")
        self.faker.add_provider(FileBasedOrgProvider)

    def test_make_datetime_returns_date_within_last_year(self):
        """Test make_datetime returns date < 1 year"""
        new_date = make_datetime(self.faker)
        new_date_date = new_date.date()

        today = datetime.today().date()
        # ignore leap years!
        last_year_yesterday = today + timedelta(days=-365)
        self.assertTrue(last_year_yesterday <= new_date_date <= today)
