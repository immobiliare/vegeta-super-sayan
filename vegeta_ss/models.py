from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class AttackReport(BaseModel):
    latencies: dict
    bytes_in: dict
    bytes_out: dict
    earliest: str
    latest: str
    end: str
    duration: int
    wait: int
    requests: int
    rate: float
    throughput: float
    success: float
    status_codes: dict
    errors: list


class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    CONNECT = "CONNECT"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    PATCH = "PATCH"
    TRACE = "TRACE"


class Target(BaseModel):
    name: str
    url: str
    method: HTTPMethod = Field(HTTPMethod.GET, description="HTTP method")
    headers: Optional[Dict[str, str]] = Field({}, description="HTTP headers")
    body_file: Optional[str] = Field(None, description="File path for the request body")


class ExperimentParameters(BaseModel):
    experiment_name: str
    min_req_sec: int
    max_req_sec: int
    experiment_duration_sec: int
    max_latency_upper_bound_msec: int
    avg_latency_upper_bound_msec: int
    sleep_time_between_trials_sec: int
    vegeta_timeout_sec: int
    save_plots: bool
    print_histograms: bool
    hist_bins: List[int]
