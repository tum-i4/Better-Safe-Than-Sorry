# Simulation

## Idea

Simulates the execution of tests that would be broken by the rules given in the *breaking_rules.json*.

The breaking rules are in DNF (disjunctive normal form) represented by arrays (or single rules) in an array.
The outer array is so to say the *or*-layer whereas each inner-array is the *and*-layer.

For example, `2_2_1.json`:

```json
[
	["R1_1_1", "R1_1_2"],
	"R1_1_3"
]
```

`2_2_1.json` has two breaking rule sets, namely (`R1_1_1` and `R1_1_2`) and (`R1_1_3`).

If at least one of the rule sets exists in a profile, the simulated tests fail.
In this case if $$ R1\textunderscore{}1\textunderscore{}1 \wedge R1\textunderscore{}1\textunderscore{}2 \vee R1\textunderscore{}1\textunderscore{}3 $$ are present, the tests will fail for the profile.


## Simulate the Application of Breaking Rules

```shell
$ better-safe-than-sorry simulation simulate-the-application-of-breaking-rules --help
Usage: simulate-the-application-of-breaking-rules [OPTIONS]
                                                  [BREAKING_RULES_FILE]

  Simulate the execution of tests with given profiles and given breaking rules

Arguments:
  [BREAKING_RULES_FILE]  Specify path to file with breaking rules to be
                         simulated.  [default: breaking_rules.json]

Options:
  -s, --sfera FILE                Specify path to sfera_automation.json to
                                  which the new profiles should be added.
                                  [default: sfera_automation.json]
  -p, --prefix TEXT               Specify prefix for generated profiles.
                                  Naming scheme is <prefix>{1...n}.  [default:
                                  custom_]
  -o, --output TEXT               Specify path where to store the results.
                                  [default: simulation_results.json]
  --override                      Override output file if it already exists.
```

### Example

```shell
better-safe-than-sorry simulation simulate-the-application-of-breaking-rules --sfera custom_sfera_automation.json rsc/breaking_rules/1_11_r1.json
```

## Automation: Analyze decision tree performance

Automatically analyze the performance of the decision tree finding the minimal amount of rules to be removed.

The tool automatically simulates all breaking_rules specified in the *solution.json* and compares the result of the decision tree with all valid results.

```
usage: analyze.py [-h] -i sfera_automation.json [-p profile_prefix] -b breaking_rules_dir [-o OUTPUT] [--override] [--loglevel {debug,info,warning,error,critical}]

arguments:
  -h, --help            show the help message and exit
  -i sfera_automation.json, --input sfera_automation.json
                        Specify path to (custom) sfera_automation.json for the test profiles to be simulated.
  -p profile_prefix, --prefix profile_prefix
                        Specify prefix for custom profiles. Naming scheme is <prefix>{1...n}. (default: custom_)
  -b breaking_rules_dir, --breaking breaking_rules_dir
                        Specify path to directory containing breaking rules to be simulated. Must include solution.json
  -o OUTPUT, --output OUTPUT
                        Specify path where to store the resulting json. (default: analysis_results.json)
  --override            Override output file if it already exists.
  --loglevel {debug,info,warning,error,critical}
                        Specify the desired loglevel. (choices: debug, info, warning, error, critical)
```

## Breaking Rules Randomizer
The tool randomly generates variants of existing breaking_rulesets.

It is a simple replace method that takes a Rule and literally replaces it with another one. It then adds the newly generated variant the the suffix _rn where n is the numbering.

This tool can be used to increase the number of breaking_rulesets. This can help to determine whether certain rulesets are always calculated correctly or if it is just by chance.

```
usage: breaking_rules_randomizer.py [-h] -s sfera_automation.json [-b breaking_rules_dir] -r RULESET [-n N] [--override] [--loglevel {debug,info,warning,error,critical}]

arguments:
  -h, --help            show the help message and exit
  -s sfera_automation.json, --sfera sfera_automation.json
                        Specify path to sfera_automation.json for the all_rules profile.
  -b breaking_rules_dir, --breaking breaking_rules_dir
                        Specify path to directory with the breaking_rulesets. (default: breaking_rules)
  -r RULESET, --ruleset RULESET
                        Specify the breaking_ruleset for which the variant should be generated. E.g. 1_1
  -n N                  Number of random variants to be generated (default: 1)
  --override            Override output file if it already exists.
  --loglevel {debug,info,warning,error,critical}
                        Specify the desired loglevel. (choices: debug, info, warning, error, critical)
```