"""
Collect results from the different Vagrant directories.
"""
from json import dumps, loads
from logging import debug, getLogger
from multiprocessing import Process
from pathlib import Path
from shutil import copyfile, copytree, rmtree
from subprocess import call
from sys import stdout
from typing import Mapping, MutableMapping, MutableSequence, Optional, Sequence

from better_safe_than_sorry.shared import (
    CUSTOM_SFERA_OPTION,
    OVERRIDE_OPTION,
    PREFIX_OPTION,
)
from better_safe_than_sorry.utils.custom_export import export_to_json
from typer import Argument, Exit, Option, Typer, confirm, echo

app = Typer(help="Use Vagrant to execute the tests.")
_LOGGER = getLogger(__name__)


@app.command(name="collect-the-test-results-from-the-vagrant-directories")
def main(
    input_directory: Path = Argument(
        "instances",
        help="Specify path to directory with the vagrant instances.",
        file_okay=False,
        exists=True,
    ),
    output_file: Path = Option(
        "results.json",
        "-o",
        "--output",
        dir_okay=False,
        help="Specify path where to store the results.",
    ),
    override: bool = OVERRIDE_OPTION,
) -> None:
    """
    Collects and combines the results of the vagrant instances into a single results.json
    """

    # Prepare results.json
    results = []

    # Find all vagrant instances
    for instance_path in input_directory.glob("vagrant_*"):
        echo(f"Collection results from {instance_path}")

        # Get the results.json from the instance
        instance_results = loads(instance_path.joinpath("results.json").read_text())
        results.extend(instance_results)

    # Export results.json
    export_to_json(output_file, results, override)


class VagrantProcess(Process):
    directory: Path

    def __init__(self, directory: Path) -> None:
        super().__init__()
        self.directory = directory

    def run(self) -> None:
        """
        Call vagrant in directory.
        :return:
        """
        call(["vagrant", "up"], cwd=str(self.directory), stdout=stdout)


@app.command(name="start-vagrant-instances")
def main(
    input_directory: Path = Argument(
        "instances",
        help="Specify path to directory with the vagrant instances.",
        file_okay=False,
        exists=True,
    ),
    parallel: bool = Option(
        False,
        "--parallel",
        "-p",
        is_flag=True,
        help="If this flag is set, we will start the instances in parallel.",
    ),
) -> None:
    """
    Start the vagrant instances.
    """

    sub_directories = input_directory.glob("vagrant_*")
    if parallel:
        processes = [VagrantProcess(p) for p in sub_directories]
        for p in processes:
            echo(f"Start process in {p.directory}")
            p.start()
        for p in processes:
            echo(f"Wait for process in {p.directory}")
            p.join()
    else:
        # Find all vagrant instances
        for instance_path in sorted(sub_directories):
            echo(f"Start vagrant in {instance_path}")
            call(["vagrant", "up"], cwd=str(instance_path), stdout=stdout)


@app.command(name="prepare-vagrant-directories-for-the-test-execution")
def main(
    sfera_automation_file: Optional[Path] = CUSTOM_SFERA_OPTION,
    vagrant_path: Path = Argument(
        "vagrant_dir",
        exists=True,
        file_okay=False,
        help="Specify path to vagrant directory including the necessary base configuration.",
    ),
    number_of_vagrant_instances: int = Option(
        4,
        "-n",
        "--number_vagrant_instances",
        help="Specify number of vagrant instances to be created.",
    ),
    prefix=PREFIX_OPTION,
    prefix_n: int = Option(
        -1,
        "--prefix-n",
        help="Specify n to be used with the prefix. Default is to automatically find the maximum value for n.",
    ),
    all_profiles: bool = Option(
        False,
        "-a",
        "--all_profiles",
        is_flag=True,
        help="Use all profiles from the given sfera_automation.json. Overrides --prefix option.",
    ),
    target_path: Path = Option(
        "instances",
        "-t",
        "--target_dir",
        file_okay=False,
        help="Specify path to directory to store the vagrant instances.",
    ),
) -> None:
    """
    Creates multiple instances for automatic testing of the configurations within vagrant.
    """
    echo(f"Load test_configuration.json from '{vagrant_path}'")
    config_path = vagrant_path.joinpath("tests").joinpath("test_configuration.json")
    if not config_path.is_file():
        echo(f"We could not find {config_path}")
        raise Exit(1)
    test_configuration = loads(config_path.read_text())

    echo(
        "Check if a path for the sfera_automation.json was given or check for the default and use it if possible"
    )
    if sfera_automation_file is None:
        sfera_path = vagrant_path.joinpath(
            test_configuration["sfera_directory"]
        ).joinpath("sfera_automation.json")
        if not sfera_path.is_file():
            echo(
                "Could not find sfera_automation.json automatically. Please use the --sfera parameter or check the file-structure. Aborting!"
            )
            raise Exit(1)
    else:
        sfera_path = sfera_automation_file

    echo(f"Load profiles from {sfera_path}")
    sfera_data = loads(sfera_path.read_text())
    sfera_profiles: Mapping[str, Sequence[str]] = sfera_data["profiles"]

    # Specify which profiles should be used
    profiles: MutableSequence[str] = []

    # Find profiles
    if all_profiles:
        profiles = list(sfera_profiles.keys())
    else:
        current_profile = 1
        while True:
            if prefix_n != -1 and prefix_n < current_profile:
                break

            profile_name = prefix + str(
                current_profile
            )  # Profile naming scheme: prefix + counter

            # Check if profile exists. If it does not exist, we can stop assuming there are no gaps in the numbering.
            if profile_name not in sfera_profiles:
                break

            # Add profile in order to be simulated
            profiles.append(profile_name)

            current_profile += 1
    debug(
        "Handle edge case when there are less profiles than vagrant instances defined in the parameter"
    )
    n: int = min(len(profiles), number_of_vagrant_instances)

    if n == 0:
        echo(
            "No profiles selected, therefore not creating any vagrant instances. Please recheck the inputs!"
        )
        raise Exit(1)
    elif n < number_of_vagrant_instances:
        echo(
            f"There are not enough profiles ({n}) for {number_of_vagrant_instances} vagrant instances. Will be creating {n} instances only."
        )

    echo(f"Create {n} profile_assignments, one for each vagrant instance")
    profile_assignment: MutableMapping[int, MutableSequence[str]] = {}

    # Initialize lists
    for i in range(n):
        profile_assignment[i] = []

    echo(f"Assign profiles to the {n} instances")
    for i, profile in enumerate(profiles):
        profile_assignment[(i % n)].append(profile)

    echo(
        f"Check if directory '{target_path}' already exists and if it can be deleted in that case."
    )
    _check_target_directory(target_path)

    echo(f"Create the {n} output directories")
    for i in range(n):
        copytree(vagrant_path, target_path.joinpath(f"vagrant_{i}"))

    echo("Save testing configurations in output directories")
    for i in range(n):
        test_configuration["profiles"] = profile_assignment[i]

        target_path.joinpath(f"vagrant_{i}").joinpath("tests").joinpath(
            "test_configuration.json"
        ).write_text(dumps(test_configuration, ensure_ascii=False, indent=4))

    echo("Override sfera_automation.json in output directories")
    for i in range(n):
        copyfile(
            sfera_path.resolve(),
            target_path.joinpath(f"vagrant_{i}")
            .joinpath(test_configuration["sfera_directory"])
            .joinpath("sfera_automation.json"),
        )


def _check_target_directory(directory: Path) -> None:
    if directory.exists():
        if confirm("Output directory already exists. Delete it?"):
            rmtree(directory)
        else:
            echo("Aborting.")
            raise Exit(1)


if __name__ == "__main__":
    app()
