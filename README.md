# Better Safe Than Sorry

This repository is part of the paper *Better Safe Than Sorry! Automated Identification of Breaking Security-Configuration Rules* accepted at the [4th ACM/IEEE International Conference on Automation of Software Test (AST)](https://conf.researchr.org/home/ast-2023).

Institutions like the [Center for Internet Security](https://www.cisecurity.org/) publish security-configuration guides(also called benchmarks) that help us configure systems more securely.
This configuration hardening can mitigate the risk of successful attacks, which may cause damage to our systems and data.
A remaining problem with applying these guides are so-called "breaking rules."
Applying breaking rules on a production system will break at least one functionality with the corresponding ramifications.
We could safely apply the remaining rules if we identified all breaking rules and removed them from the guide.

Our new approach combines techniques from software testing, machine learning, and graph theory to automatically identify these breaking rules.
This repository includes our Python scripts to

1. generate the covering arrays from a given security-configuration guide
2. Test the different covering arrays
3. Analyze the results to find the breaking rules

One can redo all our experiments presented in the article using the code in this repository.

## Setup

### With PyPi

The easiest way to use the scrips in this repository is to install the package from PyPi

```shell
pip install better-safe-than-sorry
better-safe-than-sorry --version
```

### With Poetry

One can also use poetry to install the dependencies.

```shell
cd /path/to/better-safe-than-sorry/
poetry install
poetry run better-safe-than-sorry --version
```

## Steps

### Generate Profiles based on Covering Arrays

See [here](better_safe_than_sorry/generation_of_test_profiles/README.md).

### Test Execution

#### Simulation

See [here](better_safe_than_sorry/simulation/README.md).

#### Test Execution with Vagrant

See [here](better_safe_than_sorry/vagrant_deployment/README.md)

### Test Result Analysis

See [here](better_safe_than_sorry/analysis/README.md).

## Resources

### Sfera Automation files

The folder [rsc/sfera_automation_jsons](rsc/sfera_automation_jsons) contains variants of `sfera_automation.json` files based on the Windows 10 version 1909 guide by the Center for Internet Security.
`sfera_automation.json` is a JSON-based file format used at Siemens to automatically implement Windows-based security-configuration guides.
We generated the variants were generated using the IPOG and IPOG-D algorithms and include custom profiles for combinatorial testing of strength 2 to 5.

## Contact

If you have any questions, please create an issue or contact [Patrick Stöckle](mailto:patrick.stoeckle@tum.de?subject=GitHub%20Repository%20%22better-safe-than-sorry%22).
