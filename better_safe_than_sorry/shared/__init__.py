# Define Custom Types
import typing
from typing import Sequence, Union

from typer import Option

Rule = str
Profile = Sequence[Rule]
RuleSet = Union[Rule, Sequence[Rule]]


class TestResult(typing.TypedDict):
    """
    Test result.
    """
    rules: Sequence[Rule]
    breaking: bool

TestResults = Sequence[TestResult]


PREFIX_OPTION = Option(
    "custom_",
    "-p",
    "--prefix",
    help="Specify prefix for generated profiles. Naming scheme is <prefix>{1...n}.",
)
SFERA_OPTION = Option(
    "sfera_automation.json",
    "-s",
    "--sfera",
    exists=True,
    dir_okay=False,
    help="Specify path to sfera_automation.json to which the new profiles should be added.",
)
CUSTOM_SFERA_OPTION = Option(
    None,
    "-c",
    "--custom-sfera",
    dir_okay=False,
    help="Specify path to sfera_automation.json with custom profiles. This file will be used in the output directories and overrides existing sfera_automation.json inside the vagrant directory. If no path is given, the sfera_automation.json from the vagrant directory will be used according to the test_configuration.",
)
OVERRIDE_OPTION = Option(
    False,
    "--override",
    is_flag=True,
    help="Override output file if it already exists.",
)
PROFILE_OPTION = Option(
    "all_rules",
    "-p",
    "--profile",
    help="Specify which profile from the sfera_automation.json should be converted to the ACTS model.",
)
