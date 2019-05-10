FROM python:3.7
WORKDIR /usr/src/app

RUN mkdir -p ./requirements
ADD Pipfile Pipfile.lock ./

RUN pip install pipenv && pipenv install --system --dev

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]
