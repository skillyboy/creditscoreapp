from django.urls import path, include
from .views import *
from creditapp.views import *
from creditapp.utils import *






urlpatterns = [



    path('extractcustomer/', extract_and_customer_data),
    path('extractloan/', extract_and_loan_data),

    path('register/', RegisterCustomerView.as_view(), name='register_customer'),
    path('eheck-eligibility/', LoanEligibilityCheckView.as_view(), name='check_loan_eligibility'),
    path('create-loan/', CreateLoanView.as_view(), name='create_loan'),
    path('view-loan/<int:loan_id>/', ViewLoanDetails.as_view(), name='view_loan_details'),
    path('view-loans/<int:customer_id>/', ViewLoansByCustomer.as_view(), name='view_loans_by_customer'),
]
