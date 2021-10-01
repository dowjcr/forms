from django.test import TestCase
from django.shortcuts import reverse
from selenium import webdriver

from forms.models import *
from budget.models import *
from budget.forms import *

from .views import CreateBudgetView

class BudgetFormTest(TestCase):
    def setUp(self):
        self.test_student1 = Student.objects.create(user_id='student1', first_name="John", surname="Smith")
        self.test_student2 = Student.objects.create(user_id='student2', first_name="Jane", surname="Doe")

        self.test_organization = Organization.objects.create(
            organization_id=1,
            name='Test Organization',
            description='Test Organization Description'
        )

    def test_valid_budget_form(self):
        data = {
            'organization': self.test_organization.organization_id,
            'president': str(self.test_student1),
            'president_crsid': self.test_student1.user_id,
            'treasurer': str(self.test_student2),
            'treasurer_crsid': self.test_student2.user_id,
            'active_members': 10,
            'subscription_details': 'Details of subscription',

            'has_bank_account': True,
            'sort_code': '123456',
            'account_number': '12345678',
            'name_of_bank': 'Bank Name',
            'balance': 123.45,

            'comments': 'Long Comments ' + 'word ' * 200,
        }

        form = BudgetForm(data=data)
        self.assertTrue(form.is_valid())

    def test_valid_budget_form_missing_data(self):
        """Test that a budget form is valid with the minimum amount of data"""
        data = {
            'organization': self.test_organization.organization_id,
            'president': str(self.test_student1),
            'president_crsid': self.test_student1.user_id,
            'treasurer': str(self.test_student2),
            'treasurer_crsid': self.test_student2.user_id,
            'active_members': 10,
            'subscription_details': '',

            'has_bank_account': False,
            'sort_code': '',
            'account_number': '',
            'name_of_bank': '',
            'balance': '',

            'comments': 'Long Comments ' + 'word ' * 200,
        }

        form = BudgetForm(data=data)
        self.assertTrue(form.is_valid())


class BudgetFormAccessTest(TestCase):
    """Tests to assert whether a student has access to all+only the budgets they should be able to access"""
    def setUp(self):
        self.test_student1 = Student.objects.create(user_id='student1', first_name="John", surname="Smith")
        self.test_student2 = Student.objects.create(user_id='student2', first_name="Jane", surname="Doe")
        self.test_student3 = Student.objects.create(user_id='student3', first_name="Bob", surname="Dill")

        self.test_organization = Organization.objects.create(
            organization_id=1,
            name='Test Organization',
            description='Test Organization Description'
        )

        self.test_budget1 = Budget.objects.create(
            budget_id = 1,
            organization = self.test_organization,
            year = 2020,
            submitter = self.test_student1.user_id,
            president = str(self.test_student1),
            president_crsid = self.test_student1.user_id,
            treasurer = str(self.test_student2),
            treasurer_crsid = self.test_student2.user_id,
        )

        self.test_budget2 = Budget.objects.create(
            budget_id = 2,
            organization = self.test_organization,
            year = 2021,
            submitter = self.test_student3.user_id,
            president = str(self.test_student3),
            president_crsid = self.test_student3.user_id,
            treasurer = str(self.test_student2),
            treasurer_crsid = self.test_student2.user_id,
        )
    
    def test_student_can_view_all_past_budgets(self):
        """Test that a student who is the president for the current budget can view all previous budgets"""
        assert self.test_budget1.student_can_edit(self.test_student3.user_id)
        assert self.test_budget2.student_can_edit(self.test_student3.user_id)




# class BudgetFormViewTest(TestCase):
#     def setUp(self):
#         self.driver = webdriver.Firefox(executable_path='/opt/WebDriver/bin/geckodriver')

#     def test_create_budget_view(self):
#         # self.driver.get(reverse('budget-form'))
#         self.driver.get(reverse('dashboard'))
#         link = self.driver.find_element_by_partial_link_text('this link')
