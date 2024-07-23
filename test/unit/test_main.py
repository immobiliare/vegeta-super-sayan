import os
from pathlib import Path
from subprocess import CompletedProcess
from tempfile import TemporaryDirectory

import pandas as pd
import pytest

from vegeta_ss.__main__ import VegetaAttacker, evaluate_trial, save_results
from vegeta_ss.models import AttackReport, HTTPMethod, Target, TestParameters
from vegeta_ss.utils import format_time

test_target_get = Target(
    name="test_target_get", method=HTTPMethod("GET"), url="http://localhost"
)
test_target_post = Target(
    name="test_target_post",
    method=HTTPMethod("POST"),
    url="http://localhost",
    body_file="test_payload.txt",
    headers={"Content-Type": "application/json"},
)
test_target_put = Target(
    name="test_target_put",
    method=HTTPMethod("PUT"),
    url="http://localhost",
    body_file="test_payload.json",
    headers={"Content-Type": "application/json"},
)
test_target_patch = Target(
    name="test_target_patch",
    method=HTTPMethod("PATCH"),
    url="http://localhost",
    body_file="test_payload.xml",
    headers={"Content-Type": "application/xml"},
)
test_target_delete = Target(
    name="test_target_delete", method=HTTPMethod("DELETE"), url="http://localhost"
)
test_target_connect = Target(
    name="test_target_connect", method=HTTPMethod("CONNECT"), url="http://localhost"
)
test_target_head = Target(
    name="test_target_head", method=HTTPMethod("HEAD"), url="http://localhost"
)
test_target_options = Target(
    name="test_target_options", method=HTTPMethod("OPTIONS"), url="http://localhost"
)
test_target_trace = Target(
    name="test_target_trace", method=HTTPMethod("TRACE"), url="http://localhost"
)
test_target_params = TestParameters(
    experiment_name="test_experiment_name",
    min_req_sec=1,
    max_req_sec=100,
    experiment_duration_sec=10,
    max_latency_upper_bound_msec=1000,
    avg_latency_upper_bound_msec=1000,
    sleep_time_between_trials_sec=5,
    vegeta_timeout_sec=5,
    save_plots=False,
    print_histograms=False,
    hist_bins=[0, 200, 400, 600],
)
test_result = AttackReport(
    latencies={
        "max": 1000000,
        "mean": 1000000,
        "50th": 1000,
        "90th": 100,
        "95th": 100,
        "99th": 100,
        "min": 100,
    },
    bytes_in={},
    bytes_out={},
    earliest="",
    latest="",
    end="",
    duration=0,
    wait=0,
    requests=0,
    rate=0,
    throughput=0,
    success=1,
    status_codes={},
    errors=[],
)
sample_data = [
    {"req_s": 100, "success_rate": 0.95, "mean": 10, "max": 20},
    {"req_s": 200, "success_rate": 0.98, "mean": 15, "max": 25},
]


def test_generate_target_file_get():
    expected_content = "GET http://localhost\n\n"

    with VegetaAttacker(test_target_get) as attacker:
        file_path = attacker.target_file.name
        with open(file_path) as f:
            content = f.read()

    assert content == expected_content
    assert not os.path.exists(file_path)


def test_generate_target_file_post():
    expected_content = (
        "POST http://localhost\nContent-Type: application/json\n@test_payload.txt\n\n"
    )

    with VegetaAttacker(test_target_post) as attacker:
        file_path = attacker.target_file.name
        with open(file_path) as f:
            content = f.read()

    assert content == expected_content
    assert not os.path.exists(file_path)


def test_generate_target_file_put():
    expected_content = (
        "PUT http://localhost\nContent-Type: application/json\n@test_payload.json\n\n"
    )

    with VegetaAttacker(test_target_put) as attacker:
        file_path = attacker.target_file.name
        with open(file_path) as f:
            content = f.read()

    assert content == expected_content
    assert not os.path.exists(file_path)


def test_generate_target_file_patch():
    expected_content = (
        "PATCH http://localhost\nContent-Type: application/xml\n@test_payload.xml\n\n"
    )

    with VegetaAttacker(test_target_patch) as attacker:
        file_path = attacker.target_file.name
        with open(file_path) as f:
            content = f.read()

    assert content == expected_content
    assert not os.path.exists(file_path)


def test_generate_target_file_delete():
    expected_content = "DELETE http://localhost\n\n"

    with VegetaAttacker(test_target_delete) as attacker:
        file_path = attacker.target_file.name
        with open(file_path) as f:
            content = f.read()

    assert content == expected_content
    assert not os.path.exists(file_path)


def test_generate_target_file_connect():
    expected_content = "CONNECT http://localhost\n\n"

    with VegetaAttacker(test_target_connect) as attacker:
        file_path = attacker.target_file.name
        with open(file_path) as f:
            content = f.read()

    assert content == expected_content
    assert not os.path.exists(file_path)


def test_generate_target_file_head():
    expected_content = "HEAD http://localhost\n\n"

    with VegetaAttacker(test_target_head) as attacker:
        file_path = attacker.target_file.name
        with open(file_path) as f:
            content = f.read()

    assert content == expected_content
    assert not os.path.exists(file_path)


def test_generate_target_file_options():
    expected_content = "OPTIONS http://localhost\n\n"

    with VegetaAttacker(test_target_options) as attacker:
        file_path = attacker.target_file.name
        with open(file_path) as f:
            content = f.read()

    assert content == expected_content
    assert not os.path.exists(file_path)


def test_generate_target_file_trace():
    expected_content = "TRACE http://localhost\n\n"

    with VegetaAttacker(test_target_trace) as attacker:
        file_path = attacker.target_file.name
        with open(file_path) as f:
            content = f.read()

    assert content == expected_content
    assert not os.path.exists(file_path)


def test_run_attack_success(mocker):
    test_result = CompletedProcess(
        args="cat /var/folders/temp | vegeta attack -rate=10/s -duration=1s -timeout=5s| vegeta report -type=json",
        returncode=0,
        stdout=b'{"latencies":{"total":42,"mean":1,"50th":1,"90th":1,'
        b'"95th":1,"99th":1,"max":1,"min":1},'
        b'"bytes_in":{"total":20,"mean":2},'
        b'"bytes_out":{"total":0,"mean":0},"'
        b'earliest":"2023-09-27T18:37:23.094248208+02:00"'
        b',"latest":"2023-09-27T18:37:23.994276125+02:00",'
        b'"end":"2023-09-27T18:37:24.022638958+02:00",'
        b'"duration":900027917,"wait":28362833,'
        b'"requests":10,"rate":11.110766467480586,'
        b'"throughput":10.771326620822105,'
        b'"success":1,"status_codes":{"200":10},"errors":[]}',
        stderr=b"",
    )
    mocker.patch("subprocess.run", return_value=test_result)

    with VegetaAttacker(test_target_get, save_plots=False) as attacker:
        result = attacker.run_attack(10, 1, 5)

    assert isinstance(result, AttackReport)
    assert result.latencies["total"] == 42
    assert result.success == 1


def test_evaluate_trial_success():
    max_ub = 1000000
    avg_ub = 1000000
    trial = 100
    max_found = 0
    breaking_point = 100
    sleep_time = 0

    max_found, breaking_point = evaluate_trial(
        trial, test_result, max_ub, avg_ub, max_found, breaking_point, sleep_time
    )

    assert max_found == 100
    assert breaking_point == 100


def test_format_time():
    assert format_time(100) == "100ns"
    assert format_time(1000) == "1μs"
    assert format_time(1000000) == "1ms"
    assert format_time(1000000000) == "1.0s"
    assert format_time(12345) == "12μs"
    assert format_time(123456789) == "123ms"
    assert format_time(60 * 1e9) == "60.0s"  # 1 minute in nanoseconds
    assert format_time(3600 * 1e9) == "3600.0s"  # 1 hour in nanoseconds


@pytest.fixture
def temp_directory():
    with TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


def test_save_results(temp_directory):
    result_file_path = temp_directory / "test_results.csv"
    save_results(sample_data, result_file_path, test_result)

    # Check if the file was created
    assert result_file_path.exists()

    # Read the CSV file and check its contents
    result_df = pd.read_csv(result_file_path)
    assert list(result_df.columns) == [
        "req_s",
        "success_rate",
        "max",
        "mean",
        "50th",
        "90th",
        "95th",
        "99th",
        "min",
    ]
    assert len(result_df) == len(sample_data)
    # You can add more specific checks on the DataFrame if needed

    # Clean up the temporary file
    result_file_path.unlink()
