FROM python:3.7.1
WORKDIR /usr/src/app

RUN mkdir -p ./requirements
ADD Pipfile Pipfile.lock ./

RUN pip install pipenv && \
    pip install setuptools==57.5.0 && \
    pipenv install --system --dev

ADD omaha_server/ ./

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]
