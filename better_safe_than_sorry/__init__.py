"""
Single entry point.
"""
from pkg_resources import DistributionNotFound, get_distribution

from better_safe_than_sorry.analysis.main import app as analysis_app
from better_safe_than_sorry.generation_of_test_profiles.main import (
    app as generation_of_test_profiles,
)
from better_safe_than_sorry.simulation.simulate import app as simulation_app
from better_safe_than_sorry.vagrant_deployment.main import app as vagrant_app
from typer import Exit, Option, Typer, echo

try:
    dist_name = "better-safe-than-sorry"
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = "unknown"
finally:
    del get_distribution, DistributionNotFound

app = Typer()


def _version_callback(value: bool) -> None:
    if value:
        echo(f"better-safe-than-sorry {__version__}")
        raise Exit()


@app.callback()
def _call_back(
    _: bool = Option(
        None,
        "--version",
        is_flag=True,
        callback=_version_callback,
        expose_value=False,
        is_eager=True,
        help="Version",
    )
) -> None:
    """

    :return:
    """


app.add_typer(
    generation_of_test_profiles, name="generate-profiles-based-on-covering-arrays"
)
app.add_typer(simulation_app, name="simulation")
app.add_typer(vagrant_app, name="test-execution-with-vagrant")
app.add_typer(analysis_app, name="analysis")

if __name__ == "__main__":
    app()
