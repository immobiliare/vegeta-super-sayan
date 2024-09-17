import csv
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import List

from omegaconf import OmegaConf

from vegeta_ss.models import AttackReport, Target, ExperimentParameters
from vegeta_ss.utils import format_time, logger

results_dir = Path("results")


class VegetaAttacker:
    def __init__(
        self,
        target: Target,
        experiment_name: str = "experiment_1",
        save_plots: bool = True,
        print_histograms: bool = False,
        hist_bins: tuple = (0, 100, 200, 300, 400, 500),
    ):
        self.target = target
        self.experiment_name = experiment_name
        self.result_dir = results_dir / self.experiment_name / self.target.name
        self.save_plots = save_plots
        self.print_histograms = print_histograms
        self.hist_bins = hist_bins
        self.target_file = tempfile.NamedTemporaryFile(delete=False)
        self.generate_target_file()

        os.makedirs(self.result_dir, exist_ok=True)

    def generate_target_file(self):
        with open(self.target_file.name, "w") as f:
            f.write(f"{self.target.method.name} {self.target.url}\n")
            for header, value in self.target.headers.items():
                f.write(f"{header}: {value}\n")
            if self.target.body_file:
                f.write(f"@{self.target.body_file}\n")
            f.write("\n")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.target_file.close()
        os.remove(self.target_file.name)

    def run_attack(self, rate: int, duration: int, timeout: int) -> AttackReport:
        temp_bin_filename = str(self.result_dir / "results_temp.bin")

        cmd = (
            f"cat {self.target_file.name} | "
            f"vegeta attack -rate={rate}/s -duration={duration}s -timeout={timeout}s| "
            f"tee {temp_bin_filename} |"
            f"vegeta report -type=json"
        )
        result = subprocess.run(cmd, capture_output=True, shell=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"Vegeta command failed with error: {result.stderr.decode()} | {result.stdout.decode()}"
            )

        try:
            json_report = json.loads(result.stdout.decode())
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to decode Vegeta output to JSON: {e}")

        if self.save_plots:
            os.makedirs(self.result_dir / "plots", exist_ok=True)
            filename = f"rate_{rate}.html"
            cmd = f"cat {temp_bin_filename} | vegeta plot > {str(self.result_dir / 'plots' / filename)}"
            subprocess.run(cmd, capture_output=True, shell=True)

        if self.print_histograms:
            hist_bins_str = "ms,".join(str(x) for x in self.hist_bins) + "ms"
            cmd = (
                f'cat {temp_bin_filename} | vegeta report -type="hist[{hist_bins_str}]"'
            )
            hist = subprocess.run(cmd, capture_output=True, shell=True).stdout.decode()
            logger.info(f"\n{hist}")

        Path(temp_bin_filename).unlink(missing_ok=True)
        return AttackReport(**json_report)


def evaluate_trial(
    trial: int,
    result: AttackReport,
    max_ub: int,
    avg_ub: int,
    max_found: int,
    breaking_point: int,
    sleep_time: int,
) -> tuple[int, int]:
    """Evaluate the results of a trial and return the new trial parameters.

    Args:
        trial (int): The current trial.
        result (AttackReport): The attack report.
        max_ub (int): The maximum latency upper bound in nanoseconds.
        avg_ub (int): The average latency upper bound in nanoseconds.
        max_found (int): The maximum rate found so far.
        breaking_point (int): The maximum rate that failed.
        sleep_time (int): The time to wait in order to allow all services to return to clear state when a trial fails

    Returns:
        tuple[int, int]: The new trial parameters.
    """

    success_rate, max_lat, avg_lat = (
        result.success,
        result.latencies["max"],
        result.latencies["mean"],
    )
    relative_status_codes = str(
        {
            k: str(round(v / result.requests * 100, 2)) + "%"
            for k, v in result.status_codes.items()
        }
    ).replace("'", "")
    status_codes_message = f"Status code percentages: {relative_status_codes}"
    logger.info(
        f"Rate: {trial}, Success Rate: {success_rate:.2%}, "
        f"Max Latency: {format_time(max_lat)}, Avg Latency: {format_time(avg_lat)}"
    )

    # Check if the trial meets success conditions and log specific failures if any

    if success_rate < 1.0:
        logger.info(
            f"Trial with {trial} req/s failed due to success rate {success_rate} being less than 100%."
        )
    elif max_lat > max_ub:
        logger.info(
            f"Trial with {trial} req/s failed due to max latency {format_time(max_lat)} exceeding upper bound {format_time(max_ub)}."
        )
    elif avg_lat > avg_ub:
        logger.info(
            f"Trial with {trial} req/s failed due to average latency {format_time(avg_lat)} exceeding upper bound {format_time(avg_ub)}."
        )

    # If any of the failure conditions are met, log additional information and sleep
    if any((max_lat > max_ub, avg_lat > avg_ub, success_rate < 1.0)):
        breaking_point = trial
        logger.info(
            f"{status_codes_message}. Errors detected: sleeping {sleep_time} seconds before performing next trial"
        )
        time.sleep(sleep_time)
    else:
        max_found = trial
        logger.info(f"Trial with {trial} req/s succeeded.")

    return max_found, breaking_point


def save_results(
    data: List[list], result_file_path: Path, result: AttackReport
) -> None:
    df_columns = ["req_s", "success_rate"] + list(result.latencies.keys())

    # Sort data by "req_s" (assuming it's the first element in each data list)
    data_sorted = sorted(data, key=lambda x: x[0])

    # Write to CSV
    with open(result_file_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(df_columns)
        writer.writerows(data_sorted)


def run_load_test(target: Target, experiment_params: ExperimentParameters) -> None:
    t0 = time.time()

    # Set up trial parameters
    max_ub = int(experiment_params.max_latency_upper_bound_msec * 1e6)
    avg_ub = int(experiment_params.avg_latency_upper_bound_msec * 1e6)
    rate, max_found, breaking_point = (
        experiment_params.max_req_sec,
        max(0, experiment_params.min_req_sec - 1),
        experiment_params.max_req_sec,
    )

    # Set up save results dir
    base_dir = results_dir / experiment_params.experiment_name / target.name
    file_name = "results.csv"
    base_dir.mkdir(parents=True, exist_ok=True)

    # Run trials
    data, solved = [], False
    while not solved:
        logger.info(f"Performing trial with rate {rate}")
        with VegetaAttacker(
            target,
            experiment_params.experiment_name,
            experiment_params.save_plots,
            experiment_params.print_histograms,
            experiment_params.hist_bins,
        ) as attacker:
            result = attacker.run_attack(
                rate,
                experiment_params.experiment_duration_sec,
                experiment_params.vegeta_timeout_sec,
            )
        max_found, breaking_point = evaluate_trial(
            rate,
            result,
            max_ub,
            avg_ub,
            max_found,
            breaking_point,
            experiment_params.sleep_time_between_trials_sec,
        )
        data.append(
            [rate, f"{result.success:.2%}"]
            + [format_time(t) for t in result.latencies.values()]
        )

        solved = breaking_point - max_found <= 1
        if not solved:
            rate = int((max_found + breaking_point) / 2)

        # Save results each iteration, to avoid losing them if process stops
        result_file_path = base_dir / file_name
        save_results(data, result_file_path, result)

    if max_found < experiment_params.min_req_sec:
        logger.info(
            f"Test completed in {round(time.time() - t0)}s. Unable to find a suitable rate. Try lowering min_req_seq parameter in config. Complete results at {result_file_path}"
        )
    else:
        logger.info(
            f"Test succeeded in {round(time.time() - t0)}s. Maximum load: {max_found} req/s. Complete results at {result_file_path}"
        )


def main(cfg_path="vegeta_ss/config/config.yaml"):
    cfg = OmegaConf.load(cfg_path)

    experiment_params = ExperimentParameters(**cfg.experiment_parameters)
    result_dir = results_dir / experiment_params.experiment_name

    try:
        os.makedirs(result_dir)
    except FileExistsError:
        logger.warning(
            f"Experiment folder with name {experiment_params.experiment_name} already existing, continuing will override. Continue? [Y/n]"
        )
        answer = input(
            "         --------> send n if you want to stop the experiment and exit, any other key to continue: "
        )
        if answer.lower() in ["n"]:
            raise SystemExit(0)
        else:
            logger.warning("Continuing. Results will override existing files.")

    for i, target_params in enumerate(cfg.targets):
        target = Target(**target_params)
        logger.info(
            f"Starting load test for Target {target.name}, {i + 1} of {len(cfg.targets)} targets"
        )
        run_load_test(target, experiment_params)


if __name__ == "__main__":
    main()
