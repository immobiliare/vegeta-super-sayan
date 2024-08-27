<div align="center">
  <a href="https://labs.immobiliare.it/">
    <img src="https://media.licdn.com/dms/image/C5612AQH5XfKKTDIHPA/article-cover_image-shrink_600_2000/0/1520090560612?e=2147483647&v=beta&t=D-q0EPV6gZ3Pnly83XskVKf01Z52bAesnOISbwxVQsU" width="650" height="auto"/>
  </a>


# Vegeta Super Sayan

> Vegeta System for Universal Performance Evaluation and Resilience Studies with Automated Yield and Analysis for Networks using Vegeta

![Test](https://github.com/immobiliare/vegeta-super-sayan/actions/workflows/ci.yaml/badge.svg)
![Python 3.9](https://img.shields.io/badge/Python-3.9+-blue)

</div>

This project is a versatile load testing tool designed to evaluate the performance and resilience of web services and APIs. Using the [Vegeta](https://github.com/tsenart/vegeta) load testing framework as its core, this tool written in python provides a user-friendly interface for conducting load tests on a variety of target endpoints with different configurations. It allows users to define test parameters such as request rate, duration, and latency upper bounds, and then systematically explores different request rates to find the optimal performance point or identify breaking points where the system starts to degrade under load.

<div align="center">

![Example](.github/example_images/vegeta_example.gif)
</div>

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)

## Introduction

Key features of this project include:

1. **Configurability**: Users can define multiple target endpoints, each with its own set of HTTP method, URL, headers, and request bodies.

2. **Dynamic Rate Adjustment**: The tool automatically adjusts the request rate during testing to efficiently find the maximum sustainable request rate or detect failure points.

3. **Result Analysis**: Detailed test results are collected and analyzed, including success rates and latency statistics, which are then saved in a structured CSV format for further analysis.

4. **Ease of Use**: The project offers a simple configuration file for defining test scenarios and parameters, making it accessible to both beginners and experienced users.

By leveraging this load testing tool, you can gain insights into how your web services or APIs perform under different levels of traffic, helping you optimize performance, identify bottlenecks, and ensure your system can handle real-world usage scenarios.


## Installation

### Install vegeta

Install [vegeta](https://github.com/tsenart/vegeta):

#### macOS

You can install Vegeta using the [Homebrew](https://github.com/Homebrew/homebrew/):

```shell
$ brew update && brew install vegeta
```

#### Arch Linux

```shell
$ pacman -S vegeta
```
#### Source

```shell
git clone https://github.com/tsenart/vegeta
cd vegeta
make vegeta
mv vegeta ~/bin # Or elsewhere, up to you.
```

### Clone Vegeta Super Sayan

```shell
git clone https://github.com/immobiliare/vegeta-super-sayan
cd vegeta-super-sayan
```

### Create virtualenv and install requirements

In order to create a clean environment for the execution of the application, a new virtualenv should be created inside the current folder, using the command

```console
python3 -m venv venv
```

A new folder named `venv` will be created in `.`

In order to activate the virtualenv, execute

```console
source venv/bin/activate
```

and install python requirements executing

```console
pip install -r requirements.txt
```
A different approach consists in using the Makefile by running from the project root the command

```console
make
source venv/bin/activate
```

This operation will:

- create the venv;
- update pip to the latest version;
- install the requirements;
- activate the venv.



## Configuration

The project's configuration is defined using a YAML file, making it easy to customize and adapt to specific testing scenarios. Here's an example YAML configuration:

```yaml
targets:
  - name: "service-post"
    url: "https://jsonplaceholder.typicode.com/posts"
    method: "POST"
    body_file: "payloads/example_payload.json"
    headers:
      Content-Type: "application/json"

  - name: "service-post-2"
    url: "https://reqres.in/api/users"
    method: "POST"
    body_file: "payloads/example_payload.json"
    headers:
      Content-Type: "application/json"

  - name: "service-get"
    url: "https://jsonplaceholder.typicode.com/posts/1"
    method: "GET"

experiment_parameters:
  # Name used to help organizing and keeping different experiments results, which will be saved in results/experiments
  experiment_name: experiment_i
  # Maximum rate of request per second that will be tried
  max_req_sec: 50
  # Minimum rate of request per second that will be tried
  min_req_sec: 10
  # Time in seconds of each attack
  experiment_duration_sec: 10
  # Accepted maximum latency to consider the trail for a given rate successful
  max_latency_upper_bound_msec: 2000
  # Accepted average latency to consider the trail for a given rate successful
  avg_latency_upper_bound_msec: 600
  # Sleep time between trials (important to allow the services to go back to a clean situation
  sleep_time_between_trials_sec: 10
  # Seconds before a given http call is considered failed due to timeout
  vegeta_timeout_sec: 5
  # Whether to save plots in .html format of each trial in results/plots
  save_plots: True
  # Whether to print histograms of distribution of latencies for each trial
  print_histograms: True
  # Hist bins for latencies distribution (list of int, in ms)
  hist_bins: [0, 200, 400, 600]
```

This configuration can be obtained locally by running:

```console
cp vegeta_ss/config/config.yaml.example vegeta_ss/config/config.yaml
```

In this way you'll have a git-ignored config file (to avoid undesired url sharing).
In this configuration, you can define multiple target endpoints, each with its own characteristics such as the URL, HTTP method, request body file, and headers. The `experiment_parameters` section allows you to set global parameters for the load testing experiments, including the maximum request rate to be tested, experiment duration, latency bounds, and timeout settings.

By adjusting these configuration settings, you can tailor the load testing tool to your specific use case, helping you assess the performance and reliability of your web services or APIs under various conditions.

## Usage

After running the script using the provided command:

```console
python -m vegeta_ss
```

The script will conduct a series of load tests on the defined target endpoints, systematically varying the request rate to assess performance. Once the testing is complete, the script will save several important results for your analysis:

1. **CSV Files**: For each target, a CSV file will be generated containing comprehensive test results. These files will be saved in a directory named "results" within the project's directory. The CSV files will include information on request rates, success rates, maximum latency, and average latency for each trial.

   Example CSV file location:
   ```
   results/service-post.csv
   ```


<div align="center">

![Example](.github/example_images/vegeta_csv_result_example.png)
</div>

2. **Plots**: For each target, for each rate, a plot will be generated (if this is not disabled by config file) showing the latency evolution throughout the execution time.

<div align="center">

![Example](.github/example_images/vegeta_plot_example.png)
</div>

3. **Logging Information**: Detailed log messages will be printed to the console during the script's execution, providing real-time insights into the progress of each trial. These logs include success rates, maximum and average latencies, and the trial's outcome (success or failure).

By analyzing the CSV files and log messages, you can gain valuable insights into how your web services or APIs perform under different load conditions. This information can be used to optimize your services, set appropriate rate limits, and ensure they can handle traffic effectively and reliably.

If you are trying heavy load tests, you may incur in the error: "socket: too many open files".
In this case, make sure open file descriptor and process limits are set to a high number for your user on each machine using the ulimit command.



## Changelog

See [changelog](./CHANGELOG.md).

## Contributing
We appreciate all contributions. If you are planning to contribute back bug-fixes, please do so without any further discussion.

If you plan to contribute new features, utility functions, or extensions to the core, please first open an issue and discuss the feature with us.
Sending a PR without discussion might end up resulting in a rejected PR because we might be taking the core in a different direction than you might be aware of.

To learn more about making a contribution, please see our [Contribution page](./CONTRIBUTING.md).

## Powered apps

Vegeta Super Sayan was created by ImmobiliareLabs, the technology department of [Immobiliare.it](https://www.immobiliare.it), the #1 real estate company in Italy.

**If you are using Vegeta Super Sayan [drop us a message](mailto:opensource@immobiliare.it)**.

## Support

Made with ❤️ by [ImmobiliareLabs](https://github.com/immobiliare) and all the [contributors](./CONTRIBUTING.md#contributors)

If you have any question on how to use vegeta super sayan, bugs and enhancement please feel free to reach us out by opening a [GitHub Issue](https://github.com/immobiliare/vegeta-super-sayan/issues).

<div align="center"s>
   <img src="https://wallpapers.com/images/hd/super-saiyan-blue-vegeta-dbz-4k-9mpdcke0rjcik7xw.jpg" width="800" height="auto"/>
</div>
