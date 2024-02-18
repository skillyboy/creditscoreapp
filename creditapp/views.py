
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import Loan, Customer

import pandas as pd
from django.http import HttpResponse




from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.http import JsonResponse

from rest_framework.parsers import JSONParser

from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from django.views.decorators.csrf import csrf_exempt

from django.db.models import Sum

from rest_framework.views import APIView
from creditapp.utils import *

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.utils import IntegrityError


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import Loan, Customer

# {
#   "first_name": "John",
#   "last_name": "Doe",
#   "email": "john.doe@example.com",
#   "phone_number": "1234567890",
#   "age": 35,
#   "monthly_income": 5000.0
# }

class RegisterCustomerView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]

    def post(self, request):
        # Your existing code...

        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            # Extract and process data
            validated_data = serializer.validated_data
            age = validated_data.get('age')
            monthly_income = validated_data.get('monthly_income')
            phone_number = validated_data.get('phone_number')

            # Convert age to integer if not None
            age = int(age) if age is not None else None

            # Calculate approved_limit if monthly_income is provided
            approved_limit = None
            if monthly_income is not None:
                approved_limit = 36 * monthly_income

            # Save customer to database
            customer = Customer.objects.create(
                first_name=validated_data.get('first_name'),
                last_name=validated_data.get('last_name'),
                age=age,
                monthly_income=int(monthly_income) if monthly_income is not None else None,
                phone_number=int(phone_number) if phone_number is not None else None,
                approved_limit=approved_limit
            )

            # Prepare response data
            response_data = {
                'customer_id': customer.id,
                'name': f"{customer.first_name} {customer.last_name}",
                'age': customer.age,
                'monthly_income': customer.monthly_income,
                'approved_limit': customer.approved_limit,
                'phone_number': customer.phone_number
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)









{
  "customer_id": 123,
  "loan_amount": 10000.0,
  "interest_rate": 10.0,
  "tenure": 12
}
class LoanEligibilityCheckView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]

    def post(self, request):
        data = request.data
        customer_id = data.get('customer_id')

        # Check if customer_id is provided
        if customer_id is None:
            response_data = {
                'error': 'Customer ID is not provided.'
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        # Check for the presence of other required fields
        required_fields = ['loan_amount', 'tenure', 'interest_rate']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            response_data = {
                'error': f'Missing fields: {", ".join(missing_fields)}.'
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        # Validate and handle missing loan_amount and tenure fields
        try:
            loan_amount = int(data['loan_amount'])
            tenure = int(data['tenure'])
            interest_rate = float(data['interest_rate'])
        except (ValueError, TypeError):
            response_data = {
                'error': 'Invalid data types for loan_amount, tenure, or interest_rate.'
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        # Calculate monthly installment
        monthly_installment = calculate_monthly_repayment(loan_amount, tenure, interest_rate)

        # Calculate credit rating
        credit_rating = calculate_credit_score(customer_id)

        # Construct response data
        response_data = {
            'customer_id': customer_id,
            'loan_amount': loan_amount,
            'tenure': tenure,
            'interest_rate': interest_rate,
            'monthly_installment': monthly_installment,
            'credit_rating': credit_rating
        }

        # Check loan approval based on credit rating (similar to your existing logic)

        return Response(response_data)





# {
#     "customer_id": 123,
#     "loan_amount": 5000.0,
#     "interest_rate": 8.5,
#     "tenure": 12
# }
class CreateLoanView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]

    def post(self, request):
        # Retrieve data from request body
        data = request.data
        customer_id = data.get('customer_id')
        loan_amount = data.get('loan_amount')
        interest_rate = data.get('interest_rate')
        tenure = data.get('tenure')

        # Validate input data
        if any(field not in data or data[field] is None for field in ['customer_id', 'loan_amount', 'interest_rate', 'tenure']):
            return Response({'error': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Convert loan_amount and interest_rate to float, tenure to integer
        try:
            loan_amount = float(loan_amount)
            interest_rate = float(interest_rate)
            tenure = int(tenure)
        except ValueError:
            return Response({'error': 'Invalid data types for loan_amount, interest_rate, or tenure.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if customer exists
        try:
            customer = Customer.objects.get(id=customer_id)
        except ObjectDoesNotExist:
            return Response({'error': 'Customer does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        # Calculate monthly installment
        monthly_installment = calculate_monthly_repayment(loan_amount, tenure, interest_rate)

        # Calculate credit score
        credit_score = calculate_credit_score(customer_id)

        # Determine loan approval based on credit score
        loan_approved = False
        message = ""

        if credit_score > 50:
            loan_approved = True
            if interest_rate > 12:
                message = "Loan approved with corrected interest rate."
            else:
                message = "Loan approved."
        elif 30 < credit_score <= 50:
            if interest_rate > 12:
                loan_approved = True
                message = "Loan approved with corrected interest rate."
            else:
                message = "Loan not approved due to low credit rating and interest rate."
        else:
            message = "Loan not approved due to low credit rating."

        # Create loan record if approved
        if loan_approved:
            try:
                loan = Loan.objects.create(
                    customer=customer,
                    loan_amount=loan_amount,
                    interest_rate=interest_rate,
                    tenure=tenure,
                    monthly_installment=monthly_installment
                )
                loan_id = loan.id
            except IntegrityError:
                return Response({'error': 'Error creating loan.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            loan_id = None

        # Construct response body
        response_data = {
            'loan_id': loan_id,
            'customer_id': customer_id,
            'loan_approved': loan_approved,
            'message': message,
            'monthly_installment': monthly_installment
        }

        return Response(response_data, status=status.HTTP_200_OK)



class ViewLoanDetails(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]
    def get(self, request, loan_id):
        # Retrieve loan details
        loan = get_object_or_404(Loan, pk=loan_id)

        # Retrieve customer details associated with the loan
        customer = loan.customer

        # Construct customer JSON
        customer_json = {
            'id': customer.id,
            'first_name': customer.first_name,
            'last_name': customer.last_name,
            'phone_number': customer.phone_number,
            'age': customer.age
        }

        # Construct response body
        response_data = {
            'loan_id': loan.id,
            'customer': customer_json,
            'loan_amount': loan.loan_amount,
            'interest_rate': loan.interest_rate,
            'monthly_installment': loan.monthly_installment,
            'tenure': loan.tenure
        }

        return Response(response_data)


class ViewLoansByCustomer(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]
    def get(self, request, customer_id):
        # Retrieve loans associated with the customer
        loans = Loan.objects.filter(customer_id=customer_id)

        # Construct list of loan items
        loan_items = []
        for loan in loans:
            loan_item = {
                'loan_id': loan.id,
                'loan_amount': loan.loan_amount,
                'interest_rate': loan.interest_rate,
                'monthly_installment': loan.monthly_installment,
            }
            loan_items.append(loan_item)

        return Response(loan_items)

