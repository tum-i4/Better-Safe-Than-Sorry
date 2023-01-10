"""
Analyze the test results with decision trees and Dijkstra's algorithm.
"""
from heapq import heappop, heappush
from json import loads
from logging import getLogger
from math import inf
from pathlib import Path
from typing import (
    List,
    MutableMapping,
    MutableSequence,
    Optional,
    Sequence,
    Tuple,
    Union,
)

from better_safe_than_sorry.shared import (
    OVERRIDE_OPTION,
    PROFILE_OPTION,
    SFERA_OPTION,
    Profile,
    Rule,
    TestResults,
)
from better_safe_than_sorry.utils.custom_export import export_to_json
from pyeda.boolalg import espresso
from sklearn import tree
from typer import Argument, Option, Typer, echo

# Define logger for the module
logger = getLogger(__name__)

app = Typer(help="Analyze the test results using decision trees.")


def calculate_decision_tree(
    profile: Profile, test_results: TestResults
) -> tree.DecisionTreeClassifier:
    """
    Calculate a decision tree.
    :param profile:
    :param test_results:
    :return:
    """
    echo(f"Prepare datasets for the decision tree")
    data: List[List[bool]] = []
    target: List[bool] = []

    for test_result in test_results:
        test_result_data = []
        for rule in profile:
            test_result_data.append(rule in test_result["rules"])

        data.append(test_result_data)
        target.append(test_result["breaking"])

    echo("Build the decision tree")
    decision_tree = tree.DecisionTreeClassifier()
    decision_tree = decision_tree.fit(data, target)
    echo("Decision tree done!")
    return decision_tree


def calculate_rules_to_remove(profile: Profile, graph: tree) -> Sequence[Rule]:
    """
    Use dijkstra's algorithm to calculate a shortest path in the decision tree.
    We model paths to the right child with path cost of 0 (because then we do not remove the rule).
    Paths to the left child are modeled with a cost of 1 because they essentially remove that rule.
    Hence, the shortest path is the path that removes the least amount of rules.
    """

    distance: MutableMapping[int, float] = {}  # distance from startnode
    predecessor: MutableMapping[int, Optional[int]] = {}  # parent to find shortest path
    priority_queue: List[
        Tuple[Union[int, float], Union[int, float]]
    ] = []  # priority queue for dijkstras
    goal_node = None  # ID of Non-Breaking leaf with shortest distance

    # Initialize distances with infinity
    for i in range(0, graph.node_count):
        distance[i] = inf

    # Set distance of startnode/root to 0 and add it to the priority queue
    distance[0] = 0
    predecessor[0] = None
    heappush(priority_queue, (0, 0))  # Syntax for priority queue is (priority, index)

    while priority_queue:  # Check that there is still something in the priority queue
        node: Optional[int] = heappop(priority_queue)[
            1
        ]  # Get node with minimal distance

        # Check if is leaf_node
        if graph.children_left[node] == -1:
            # Get values of leaf node
            value = graph.value[node].T
            if len(value) == 1 or value[1] == 0:
                logger.debug("Leaf: Non-Breaking")
                goal_node = node
                break
            elif value[0] == 0:
                logger.debug("Leaf: Breaking")
                continue
            else:
                logger.debug("Leaf: Inconclusive (" + str(value) + ")")
                # TODO: We might want to stop here if the majority is non-breaking (value[0] > value[1])
                continue

        # Calculate right neighbor
        right_neighbor = graph.children_right[node]
        distance_right_neighbor = (
            distance[node] + 0
        )  # We do not add any distance because we do not remove any rule

        if distance_right_neighbor < distance[right_neighbor]:
            distance[right_neighbor] = distance_right_neighbor  # Update distance
            heappush(
                priority_queue, (distance_right_neighbor, right_neighbor)
            )  # Add to prio-queue
            predecessor[right_neighbor] = node  # Set parent

        # Calculate left neighbor
        left_neighbor = graph.children_left[node]
        distance_left_neighbor = (
            distance[node] + 1
        )  # Add 1 to the distance for removing this rule

        if distance_left_neighbor < distance[left_neighbor]:
            distance[left_neighbor] = distance_left_neighbor  # Update distance
            heappush(
                priority_queue, (distance_left_neighbor, left_neighbor)
            )  # Add to prio-queue
            predecessor[left_neighbor] = node  # Set parent

    # Now we have the shortest path, defined by the goal_node and the predecessor values up to the startnode/root

    # Analyze shortest path to find rules to be removed
    removed_rules: MutableSequence[Rule] = []

    node = goal_node  # Start with leaf node
    while (
        node is not None and node > 0
    ):  # Check if we reached the startnode/root already
        parent = predecessor[node]  # Get parent

        # Check if node is left_child because that means it was removed
        if graph.children_left[parent] == node:
            removed_rules.append(profile[graph.feature[parent]])

        node = parent  # Move up to the parent node

    return removed_rules


@app.command(name="analyze-the-test-results-with-decision-trees-dijkstra")
def analyze_the_test_results_with_decision_trees_dijkstra(
    input_file: Path = Argument(
        "results.json",
        dir_okay=False,
        exists=True,
        help="Specify path to file with outputs of the tests.",
    ),
    sfera_automation_file: Path = SFERA_OPTION,
    profile_name: str = PROFILE_OPTION,
    output_file: Path = Option(
        "results.json",
        "-o",
        "--output",
        dir_okay=False,
        help="Specify path where to store the results. (default: %(default)s)",
    ),
    override: bool = OVERRIDE_OPTION,
    graphviz: bool = Option(
        False,
        "-g",
        "--graphviz",
        is_flag=True,
        help="Print graphviz representation of decision tree to console and output.",
    ),
) -> None:
    """
    Build a decision tree from a given test-output.
    """
    # Prepare output
    output = {}

    echo(f"Load {sfera_automation_file}")
    sfera_json = loads(sfera_automation_file.read_text())
    profiles = sfera_json["profiles"]

    # Check if selected profile exists
    if profile_name not in profiles:
        echo(f"Could not find profile '{profile_name}' in the input!\nAborting.")
        return

    echo(f'Get selected profile "{profile_name}"')
    profile = sfera_json["profiles"][profile_name]

    echo(f"Get test results from {input_file}")
    test_results = loads(input_file.read_text())

    # ========== DECISION TREE ==========
    decision_tree = calculate_decision_tree(profile, test_results)

    # Add the decision tree to the output
    if graphviz:
        output["decision_tree"] = tree.export_graphviz(
            decision_tree,
            feature_names=profile,
            class_names=["Non-Breaking", "Breaking"],
            filled=True,
        )
        echo(output["decision_tree"])

    # ========== DIJKSTRA'S ALGORITHM ==========
    # Use dijkstra's algorithm to calculate the least amount of rules to be excluded based on the decision tree
    removed_rules = calculate_rules_to_remove(profile, decision_tree.tree_)

    # Sort removed rules (obviously optional, but for better readability)
    removed_rules = sorted(removed_rules)

    # Add removed rules to the output
    output["removed_rules"] = removed_rules
    echo(f"Rules to be removed: {removed_rules}")

    # Calculate rules
    output["rules"] = []
    for rule in profile:
        if rule not in removed_rules:
            output["rules"].append(rule)

    # Write output to file
    export_to_json(output_file, output, override)


def calculate_rules_to_remove_tests(profile: Profile, graph: tree) -> Sequence[Rule]:
    """
    Find path towards the leaf that is non-breaking and has the highest number of cases
    """
    predecessor: MutableMapping[int, Optional[int]] = {}  # parent for backtracking
    max_leaf: Optional[int] = None  # Leaf with the (currently) highest number of cases
    max_leaf_value: int = 0  # Number of cases of the max_leaf

    # Set predecessor of startnode to None
    predecessor[0] = None

    # Stack for the DFS traversal
    stack = [0]

    while stack:
        node: Optional[int] = stack.pop()

        # Check if is leaf_node
        if graph.children_left[node] == -1:
            # Get values of leaf node
            value = graph.value[node].T[0]

            # Check if this leaf is the new maximum
            if value > max_leaf_value:
                # Update max leaf
                max_leaf = node
                max_leaf_value = value

        else:
            # Get children
            left_child = graph.children_left[node]
            right_child = graph.children_right[node]

            # Set predecessor for children
            predecessor[left_child] = node
            predecessor[right_child] = node

            # Add children to the stack
            stack.append(left_child)
            stack.append(right_child)

    # Analyze path to find rules to be removed
    removed_rules = []

    node = max_leaf  # Start with leaf node
    while (
        node is not None and node > 0
    ):  # Check if we reached the startnode/root already
        parent: Optional[int] = predecessor[node]  # Get parent

        # Check if node is left_child because that means it was removed
        if graph.children_left[parent] == node:
            removed_rules.append(profile[graph.feature[parent]])

        node = parent  # Move up to the parent node

    return removed_rules


@app.command(name="analyze-the-test-results-with-decision-trees-most-tests")
def analyze_the_test_results_with_decision_trees_most_tests(
    input_file: Path = Argument(
        "results.json",
        dir_okay=False,
        exists=True,
        help="Specify path to file with outputs of the tests.",
    ),
    sfera_automation_file: Path = SFERA_OPTION,
    profile_name: str = PROFILE_OPTION,
    output_file: Path = Option(
        "results.json",
        "-o",
        "--output",
        dir_okay=False,
        help="Specify path where to store the results. (default: %(default)s)",
    ),
    override: bool = OVERRIDE_OPTION,
    graphviz: bool = Option(
        False,
        "-g",
        "--graphviz",
        is_flag=True,
        help="Print graphviz representation of decision tree to console and output.",
    ),
) -> None:

    # Prepare output
    output = {}

    echo(f"Load {sfera_automation_file}")
    sfera_json = loads(sfera_automation_file.read_text())
    profiles = sfera_json["profiles"]

    # Check if selected profile exists
    if profile_name not in profiles:
        echo(f"Could not find profile '{profile_name}' in the input!\nAborting.")
        return

    echo(f'Get selected profile "{profile_name}"')
    profile = sfera_json["profiles"][profile_name]

    echo(f"Get test results from {input_file}")
    test_results = loads(input_file.read_text())

    # ========== DECISION TREE ==========
    decision_tree = calculate_decision_tree(profile, test_results)

    # Add the decision tree to the output
    if graphviz:
        output["decision_tree"] = tree.export_graphviz(
            decision_tree,
            feature_names=profile,
            class_names=["Non-Breaking", "Breaking"],
            filled=True,
        )
        echo(output["decision_tree"])

    # Calculate rules to be removed
    removed_rules = calculate_rules_to_remove_tests(profile, decision_tree.tree_)

    # Sort removed rules (obviously optional, but for better readability)
    removed_rules = sorted(removed_rules)

    # Add removed rules to the output
    output["removed_rules"] = removed_rules
    echo(f"Rules to be removed: {removed_rules}")

    # Calculate rules
    output["rules"] = []
    for rule in profile:
        if rule not in removed_rules:
            output["rules"].append(rule)

    # Write output to file
    export_to_json(output_file, output, override)


# Define Custom Types
EspressoResult = Sequence[tuple]


# Prepare the data for usage with espresso. Requires the used rules (Profile) and the TestResults (JSON)
def _prepare_data(rules: Sequence[Rule], test_results: TestResults) -> set:
    data = set()
    for test_result in test_results:
        # Input: Values of variables in the test set. Espresso wants value 2 if set (true) and 1 if not set (false)
        test_input = tuple((2 if rule in test_result["rules"] else 1) for rule in rules)

        # Output: 1 if test was breaking and 0 if it was not.
        test_output = tuple([1 if test_result["breaking"] else 0])

        # Add tuple to the data
        data.add((test_input, test_output))

    return data


def use_espresso(profile: Profile, test_results: TestResults) -> EspressoResult:
    """
    Set up espresso
    :param profile:
    :param test_results:
    :return:
    """
    espresso.set_config(
        single_expand=False,
        remove_essential=True,
        force_irredundant=True,
        unwrap_onset=True,
        recompute_onset=False,
        use_super_gasp=False,
    )

    # Prepare data
    data = _prepare_data(profile, test_results)

    # Let Espresso calculate the result
    result = espresso.espresso(len(profile), 1, data, espresso.FTYPE | espresso.RTYPE)
    return result


# Transforms the output of Espresso into a more readable format.
def calculate_breaking_rules(
    profile: Profile, espresso_result: EspressoResult
) -> Sequence[Sequence[Rule]]:
    breaking_rulesets: MutableSequence[Sequence[Rule]] = []
    for c_input, output in espresso_result:
        # We only care about breaking outputs
        if output[0] == 1:
            breaking_rules = []

            for i in range(0, len(c_input)):
                # Check the value of every rule. If it was set (2), we add it to the breaking_rules
                # We could also check for don't care values
                if c_input[i] == 2:
                    breaking_rules.append(profile[i])

            breaking_rulesets.append(breaking_rules)

    return breaking_rulesets


@app.command("analyze-the-test-results-with-logic-minimization")
def main(
    input_file: Path = Argument(
        "results.json",
        dir_okay=False,
        exists=True,
        help="Specify path to file with outputs of the tests.",
    ),
    sfera_automation_file: Path = SFERA_OPTION,
    profile_name: str = PROFILE_OPTION,
) -> None:
    """
    Use Espresso to find breaking rules.
    """

    echo(f"Load {sfera_automation_file}")
    sfera_json = loads(sfera_automation_file.read_text())
    profiles = sfera_json["profiles"]

    # Check if selected profile exists
    if profile_name not in profiles:
        echo(f"Could not find profile '{profile_name}' in the input!\nAborting.")
        return

    echo(f'Get selected profile "{profile_name}"')
    profile = sfera_json["profiles"][profile_name]

    echo(f"Get test results from {input_file}")
    test_results = loads(input_file.read_text())

    # ========== ESPRESSO ==========
    result = use_espresso(profile, test_results)

    # Output result
    for breaking_rules in calculate_breaking_rules(profile, result):
        echo(breaking_rules)


if __name__ == "__main__":
    app()
