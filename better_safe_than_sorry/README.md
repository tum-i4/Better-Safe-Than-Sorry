# breaking_rules_detection

Contains tools for the different steps of the breaking rules detection process.

## 1) Generation of test configurations

The first step of the approach is to generate the configurations to be tested using techniques from combinatorial testing.

The tools to generate the covering arrays can be found in the sub-directory `test_profiles_generation`.

## 2) Testing / Simulation

The second step of the approach is to test the generated configurations. There are multiple ways how this can be achieved. One possibility is to use virtual machines, e.g. with Vagrant. Tools to generate the Vagrant instances can be found in `../Vagrant Deployment`. For a theoretical analysis of the approach, we simulated the execution of test cases. The necessary tools can be found in the sub-directory `simulation`.

## 3) Analysis
The last step is to analyze the results of testing the configurations in order to find the breaking rules. We investigated two approaches: One using decision trees and shortest path search and another one using logic optimization with espresso. Both tools can be found in the sub-directory `analysis`.