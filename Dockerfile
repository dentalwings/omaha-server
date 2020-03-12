FROM python:3.7.1
WORKDIR /usr/src/app

RUN mkdir -p ./requirements
ADD Pipfile Pipfile.lock ./

RUN pip install pipenv && pipenv install --system --dev

ADD omaha_server/ ./

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]
