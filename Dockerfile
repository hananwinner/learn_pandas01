FROM continuumio/miniconda3

WORKDIR .

# Create the environment:
COPY environment.yml environment.yml

RUN conda env create -f environment.yml

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "learn_pandas_01", "/bin/bash", "-c"]

COPY . .
ENV PYTHONPATH=${PYTHONPATH}:/
ENV AWS_DEFAULT_REGION=eu-west-1
# echo ${PYTHONPATH}

WORKDIR /mymovie/aggregator

# The code to run when container is started:
ENTRYPOINT ["conda", "run", "-n", "learn_pandas_01", "python", "mymovie_find_bookings.py"]
