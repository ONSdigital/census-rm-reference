FROM python:3.9-slim

RUN pip install pipenv

RUN groupadd --gid 1000 printfile && \
    useradd --create-home --system --uid 1000 --gid printfile printfile
WORKDIR /home/printfile
CMD ["python3", "run.py"]

COPY Pipfile* /home/printfile/
RUN pipenv install --deploy --system
USER printfile

COPY --chown=printfile . /home/printfile
