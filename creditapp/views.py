from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from django.urls import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.utils import IntegrityError
from decimal import Decimal

from .serializers import *
from .models import Loan, Customer
import pandas as pd
from creditapp.utils import *


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



# {
#   "customer_id": 123,
#   "loan_amount": 10000.0,
#   "interest_rate": 10.0,
#   "tenure": 12
# }


class LoanEligibilityCheckView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]

    def post(self, request):
        data = request.data
        customer_id = data.get('customer_id')

        if customer_id is None:
            return Response({'error': 'Customer ID is not provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        loan_amount = Decimal(data.get('loan_amount'))
        interest_rate = Decimal(data.get('interest_rate'))
        tenure = int(data.get('tenure'))

        loans = Loan.objects.filter(customer_id=customer_id)
        credit_score = calculate_credit_score(customer, loans)

        if credit_score <= 10:
            return Response({'customer_id': customer_id, 'approval': False, 'interest_rate': None, 'corrected_interest_rate': None, 'tenure': None, 'monthly_installment': None})

        approved_limit = customer.monthly_income * Decimal('36')
        total_current_loan_amount = loans.aggregate(Sum('loan_amount'))['loan_amount__sum'] or Decimal('0')

        if total_current_loan_amount > approved_limit:
            return Response({'customer_id': customer_id, 'approval': False, 'interest_rate': None, 'corrected_interest_rate': None, 'tenure': None, 'monthly_installment': None})

        monthly_installment = calculate_monthly_repayment(loan_amount, interest_rate, tenure)

        if monthly_installment > customer.monthly_income * Decimal('0.5'):
            return Response({'customer_id': customer_id, 'approval': False, 'interest_rate': None, 'corrected_interest_rate': None, 'tenure': None, 'monthly_installment': None})

        approval_status = None
        corrected_interest_rate = None

        if credit_score > 50:
            approval_status = True
            interest_rate = interest_rate
            corrected_interest_rate = interest_rate
        elif 30 < credit_score <= 50:
            approval_status = True
            if interest_rate < 12:
                corrected_interest_rate = 12
        elif 10 < credit_score <= 30:
            approval_status = True
            if interest_rate < 16:
                corrected_interest_rate = 16
        else:
            approval_status = False

        return Response({
            'customer_id': customer_id,
            'approval': approval_status,
            'interest_rate': float(interest_rate),
            'corrected_interest_rate': float(corrected_interest_rate) if corrected_interest_rate else None,
            'tenure': tenure,
            'monthly_installment': float(monthly_installment)
        })


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
        monthly_installment = calculate_monthly_repayment(loan_amount, interest_rate, tenure)

        # Calculate credit score
        loans = Loan.objects.filter(customer_id=customer_id)
        credit_score = calculate_credit_score(customer, loans)

        # Determine loan approval and interest rate based on credit score
        if credit_score > 50:
            approval_status = True
            corrected_interest_rate = interest_rate
            message = "Loan approved."
        elif 30 < credit_score <= 50:
            approval_status = True
            corrected_interest_rate = max(12, interest_rate)
            message = "Loan approved with corrected interest rate."
        else:
            approval_status = False
            corrected_interest_rate = None
            message = "Loan not approved due to low credit rating."

        # Create loan record if approved
        loan_id = None
        if approval_status:
            try:
                loan = Loan.objects.create(
                    customer=customer,
                    loan_amount=loan_amount,
                    interest_rate=corrected_interest_rate,
                    tenure=tenure,
                    monthly_installment=monthly_installment
                )
                loan_id = loan.id
            except IntegrityError:
                return Response({'error': 'Error creating loan.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Construct response body
        response_data = {
            'loan_id': loan_id,
            'customer_id': customer_id,
            'loan_approved': approval_status,
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

