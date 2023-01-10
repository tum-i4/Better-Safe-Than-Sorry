# Analysis of the Test Runs to find the Breaking Rules

## Dijkstra on Decision Trees

### Idea

The idea is to build a decision tree on the results of the tests.
Then, we want to find the minimum amount of rules to be removed in order to make all tests run without breaking.
In order to achieve this goal, we run Dijkstra's shortest path algorithm on the decision tree.
We model each arc where no rule is removed with costs of 0 and each arc that removes a rule with costs of 1.
Then, the shortest path with the least cost will also remove the minimum number of rules.

For example, for the breaking rules in `2_2_1.json`

```json
[
	["R1_1_1", "R1_1_2"],
	"R1_1_3"
]
```

the result should be either `["R1_1_1", "R1_1_3"]` or `["R1_1_2", "R1_1_3"]`.
One of the two rules from the first ruleset has to be removed and R1_1_3 has to be removed, as well.

However, for `2_2_3.json`

```json
[
	["R1_1_1", "R1_1_2"],
	["R1_1_1", "R1_1_3"]
]
```

there is only one valid result of minimum length, namely `[R1_1_1]`.

### Usage

Uses [scikit-learn](https://scikit-learn.org/stable/) to build the decision tree.

```shell
$ better-safe-than-sorry analysis analyze-the-test-results-with-decision-trees-dijkstra --help
Usage: analyze-the-test-results-with-decision-trees-dijkstra [OPTIONS] [INPUT_FILE]

  Build a decision tree from a given test-output.

Arguments:
  [INPUT_FILE]  Specify path to file with outputs of the tests.  [default:
                results.json]

Options:
  -s, --sfera FILE                Specify path to sfera_automation.json to
                                  which the new profiles should be added.
                                  [default: sfera_automation.json]
  -p, --profile TEXT              Specify which profile from the
                                  sfera_automation.json should be converted to
                                  the ACTS model.  [default: all_rules]
  -o, --output FILE               Specify path where to store the results.
                                  (default: %(default)s)  [default:
                                  results.json]
  --override                      Override output file if it already exists.
  -g, --graphviz                  Print graphviz representation of decision
                                  tree to console and output.
```

#### Usage Example

```shell
better-safe-than-sorry analysis analyze-the-test-results-with-decision-trees-dijkstra --sfera custom_sfera_automation.json
```

## Most Tests on Decision Trees

### Idea

The idea is to build a decision tree on the results of the tests.
Then, we find the leaf node that contains the largest amount of test that were non-breaking.
From this leaf node we determine the path to reach it and use the decisions along the way.

### Usage

Uses [scikit-learn](https://scikit-learn.org/stable/) to build the decision tree.

```shell
$ better-safe-than-sorry analysis analyze-the-test-results-with-decision-trees-most-tests --help
Usage: analyze-the-test-results-with-decision-trees-most-tests
           [OPTIONS] [INPUT_FILE]

Arguments:
  [INPUT_FILE]  Specify path to file with outputs of the tests.  [default:
                results.json]

Options:
  -s, --sfera FILE                Specify path to sfera_automation.json to
                                  which the new profiles should be added.
                                  [default: sfera_automation.json]
  -p, --profile TEXT              Specify which profile from the
                                  sfera_automation.json should be converted to
                                  the ACTS model.  [default: all_rules]
  -o, --output FILE               Specify path where to store the results.
                                  (default: %(default)s)  [default:
                                  results.json]
  --override                      Override output file if it already exists.
  -g, --graphviz                  Print graphviz representation of decision
                                  tree to console and output.
```

#### Usage Example

```shell
better-safe-than-sorry analysis analyze-the-test-results-with-decision-trees-most-tests --sfera custom_sfera_automation.json
```

## Logic Minimization

Heuristic Logic Minimizer.

Idea is to use the results of the execution of the tests which build essentially a truth table that can be minimized.
The optimal output would be the breaking rules.

We use [pyeda](https://pypi.org/project/pyeda/) which implements a python-wrapper for the original espresso.

### Analyze the Test Results with Logic Minimization

```shell
$ poetry run better-safe-than-sorry analysis analyze-the-test-results-with-logic-minimization --help
Usage: analyze-the-test-results-with-logic-minimization [OPTIONS] [INPUT_FILE]

  Use Espresso to find breaking rules.

Arguments:
  [INPUT_FILE]  Specify path to file with outputs of the tests.  [default:
                results.json]

Options:
  -s, --sfera FILE                Specify path to sfera_automation.json to
                                  which the new profiles should be added.
                                  [default: sfera_automation.json]
  -p, --profile TEXT              Specify which profile from the
                                  sfera_automation.json should be converted to
                                  the ACTS model.  [default: all_rules]
```

#### Usage Example

```shell
better-safe-than-sorry analysis analyze-the-test-results-with-logic-minimization --sfera custom_sfera_automation.json
```
