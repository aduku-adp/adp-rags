from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pendulum
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG


def run_load_embeddings() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "tools" / "load_embeddings.py"

    python_bin = os.getenv("EMBEDDINGS_PYTHON_BIN", "python3")
    command = [python_bin, str(script_path)]

    subprocess.run(command, check=True, cwd=str(repo_root))


with DAG(
    dag_id="load_embeddings_daily",
    description="Run load_embeddings.py daily",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="@daily",
    catchup=False,
    max_active_runs=1,
    tags=["embeddings", "resto"],
) as dag:
    run_embeddings = PythonOperator(
        task_id="run_load_embeddings",
        python_callable=run_load_embeddings,
    )

    run_embeddings
