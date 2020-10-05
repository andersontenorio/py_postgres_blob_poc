## Run Postgres

- `cd /infra`
- `docker-compose down`
- `docker-compose up --build`

## Run Python Code

- `conda env create -f requirements.yml`
- `conda activate py_postgres_blob_poc`
- `python src/run.py`