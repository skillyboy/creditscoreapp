import pandas as pd

file_path = "customer_data.xlsx"

def print_excel_head(file_path):
    try:
        df = pd.read_excel(file_path)
        print("Head of the DataFrame:")
        print(df.head())
    except Exception as e:
        error_message = f"Error extracting and printing data from Excel file: {e}"
        print(error_message)

# Call the function
print_excel_head(file_path)
