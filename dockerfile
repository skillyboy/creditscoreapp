FROM python:3.11.4
ENV PYTHONUNBUFFERED=1
WORKDIR /project/creditapp
COPY .requirements.txt /code/
RUN pip install -r requirements.txt

# Run the Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
