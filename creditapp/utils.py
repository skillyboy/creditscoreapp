from creditapp.views import *


def extract_and_customer_data(file_path):
    file_path = "customer_data.xlsx"
    try:
        df = pd.read_excel(file_path)
        for index, row in df.iterrows():
            Customer.objects.create(
                customer_id=row['Customer ID'],

                first_name=row['First Name'],
                last_name=row['Last Name'],
                phone_number=row['Phone Number'],
                monthly_income=row['Monthly Salary'],
                approved_limit=row['Approved Limit'],
                age=row['Age'] if 'Age' in df.columns else None  # Set age to None if 'Age' column doesn't exist
            )
        return HttpResponse("Data extraction and saving completed.")
    except Exception as e:
        error_message = f"Error extracting and saving data from Excel file: {e}"
        return HttpResponse(error_message, status=500)



def extract_and_loan_data(file_path):
    file_path = "loan_data.xlsx"
    try:
        df = pd.read_excel(file_path)
        for index, row in df.iterrows():
            # Search for Customer with the same customer_id
            customer = get_object_or_404(Customer, id=row['Customer ID'])
            Loan.objects.create(
                customer=customer,  # Use the retrieved Customer object
                loan_id=row['Loan ID'],
                loan_amount=row['Loan Amount'],
                tenure=row['Tenure'],
                interest_rate=row['Interest Rate'],
                monthly_installment=row['Monthly payment'],
                emis_paid_on_time=row['EMIs paid on Time'],
                start_date=row['Date of Approval'],
                end_date=row['End Date']
            )
        return HttpResponse("Loan data extraction and saving completed.")
    except Exception as e:
        error_message = f"Error extracting and saving loan data from Excel file: {e}"
        return HttpResponse(error_message, status=500)



def calculate_credit_score(customer_id):
    # Retrieve customer's monthly income
    customer = Customer.objects.get(id=customer_id)
    monthly_income = customer.monthly_income

    # Filter loan data for the given customer_id
    customer_loans = Loan.objects.filter(customer_id=customer_id)

    # Calculate credit score based on the components
    credit_score = 0

    # Component i: Past Loans paid on time
    paid_on_time_count = customer_loans.filter(emis_paid_on_time=True).count()
    credit_score += paid_on_time_count * 10  # Assuming each paid on time loan adds 10 to credit score

    # Component ii: No of loans taken in past
    num_loans_taken = customer_loans.count()
    credit_score += min(num_loans_taken, 5) * 5  # Assuming each loan taken adds 5 to credit score, capped at 5 loans

    # Component iii: Loan activity in current year
    current_year = pd.Timestamp.now().year
    loans_current_year = customer_loans.filter(start_date__year=current_year)
    activity_current_year = loans_current_year.count()  # Number of loans in current year
    credit_score += activity_current_year * 5  # Assuming each loan in current year adds 5 to credit score

    # Component iv: Loan approved volume
    approved_volume = customer_loans.aggregate(Sum('loan_amount'))['loan_amount__sum']
    if approved_volume:
        credit_score += min(approved_volume // 1000, 10) * 5  # Assuming each 1000 units of approved volume adds 5 to credit score, capped at 10 units

    # Component v: If sum of current loans > approved limit, credit score = 0
    approved_limit = monthly_income * 36  # Calculate approved limit based on monthly income
    current_loan_amount = approved_volume  # total loan amount for the customer
    if current_loan_amount and approved_limit and current_loan_amount > approved_limit:
        credit_score = 0

    return credit_score




def calculate_monthly_repayment(loan_amount, interest_rate, tenure):
    # Convert interest rate to monthly rate and tenure to months
    monthly_interest_rate = interest_rate / 12 / 100
    months = tenure * 12

    # Calculate monthly repayment using the formula for loan repayment
    monthly_repayment = (loan_amount * monthly_interest_rate) / (1 - (1 + monthly_interest_rate) ** -months)

    return monthly_repayment