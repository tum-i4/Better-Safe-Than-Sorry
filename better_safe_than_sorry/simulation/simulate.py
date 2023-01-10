"""
Simulate the Application of Breaking Rules.
"""
from json import loads
from logging import getLogger
from pathlib import Path
from typing import Dict, Sequence

from better_safe_than_sorry.shared import (
    OVERRIDE_OPTION,
    PREFIX_OPTION,
    SFERA_OPTION,
    Profile,
    RuleSet,
)
from better_safe_than_sorry.utils.custom_export import export_to_json
from typer import Argument, Option, Typer, echo

# Define logger for the module
logger = getLogger(__name__)


def is_breaking(rule: RuleSet, profile: Profile) -> bool:
    """

    :param rule:
    :param profile:
    :return:
    """
    # Check if rule is a list of rules
    if isinstance(rule, list):
        # Check if all rules are contained in the profile
        return set(rule).issubset(set(profile))
    else:
        # Check if the (single) rule is contained in the profile
        return rule in profile


def simulate(
    profiles: Dict[str, Profile], breaking_rules: Sequence[RuleSet]
) -> Sequence[dict]:
    """
    Simulate.
    :param profiles:
    :param breaking_rules:
    :return:
    """
    if len(profiles) == 0:
        echo("No profiles to be simulated")
        return []

    # Prepare output
    output = []

    # Count breaking profiles
    breaking_profiles_count = 0

    echo("Iterate over all profiles and simulate the outcome")
    for profile_name in profiles:
        logger.info("Simulating " + profile_name)

        # Load the profile
        profile: Profile = profiles[profile_name]

        # Check if the profile contains breaking rules
        breaking = False
        for breaking_rule in breaking_rules:
            if is_breaking(breaking_rule, profile):
                logger.info("Breaking: " + str(breaking_rule))
                breaking = True
                break

        if breaking:
            breaking_profiles_count += 1

        # Build output
        output_profile = {"name": profile_name, "breaking": breaking, "rules": profile}

        # Add to output
        output.append(output_profile)

    echo("Simulated " + str(len(profiles)) + " profiles.")
    echo(
        "Breaking profiles: "
        + str(breaking_profiles_count)
        + " ("
        + "{:.2%}".format(breaking_profiles_count / len(profiles))
        + ")"
    )

    return output


app = Typer(help="Simulate the test execution with defined breaking rules.")


@app.command(name="simulate-the-application-of-breaking-rules")
def main(
    breaking_rules_file: Path = Argument(
        "breaking_rules.json",
        dir_okay=False,
        exists=True,
        help="Specify path to file with breaking rules to be simulated.",
    ),
    sfera_file: Path = SFERA_OPTION,
    prefix=PREFIX_OPTION,
    output_file: Path = Option(
        "simulation_results.json",
        "-o",
        "--output",
        dir_okay=False,
        help="Specify path where to store the results.",
    ),
    override: bool = OVERRIDE_OPTION,
) -> None:
    """
    Simulate the execution of tests with given profiles and given breaking rules
    """

    echo(f"Load profiles from {sfera_file}")
    sfera_data = loads(sfera_file.read_text())
    sfera_profiles = sfera_data["profiles"]

    echo(f"Load breaking rules from {breaking_rules_file}")
    breaking_rules: Sequence[RuleSet] = loads(breaking_rules_file.read_text())

    echo(
        f'Get all profiles from sfera_automation.json starting with the prefix "{prefix}"'
    )
    profiles = {}
    current_profile = 0

    while True:
        current_profile += 1
        profile_name = prefix + str(current_profile)

        # Check if profile exists. If it does not exist, we can stop assuming there are no gaps in the numbering.
        if profile_name not in sfera_profiles:
            break

        # Add profile in order to be simulated
        profiles[profile_name] = sfera_profiles[profile_name]
    echo(f"We found {len(profiles.keys())} profiles")

    # Simulate the selected profiles
    result = simulate(profiles, breaking_rules)

    # Write result to file
    export_to_json(output_file, result, override)


if __name__ == "__main__":
    app()
