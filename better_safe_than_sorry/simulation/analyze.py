import argparse
import json
import os
import logging

from better_safe_than_sorry.utils.custom_logging import add_loglevel_argument, get_log_level
from better_safe_than_sorry.utils.custom_export import export_to_json
from better_safe_than_sorry.simulation.simulate import simulate
from better_safe_than_sorry.analysis.decision_tree import calculate_decision_tree, calculate_rules_to_remove
#from breaking_rules_detection.analysis.decision_tree2 import calculate_decision_tree, calculate_rules_to_remove

# Define logger for the module
logger = logging.getLogger(__name__)


# Definition for argparse type
def dir_path(path):  # See https://stackoverflow.com/questions/38834378/path-to-a-directory-as-argparse-argument
	if os.path.isdir(path):
		return path
	else:
		raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


def _filter_profiles(sfera_profiles, prefix: str):
	# Get all profiles from sfera_automation.json starting with the given prefix
	profiles = {}
	current_profile = 0

	while True:
		current_profile += 1
		profile_name = prefix + str(current_profile)  # Profile naming scheme: prefix + counter

		# Check if profile exists. If it does not exist, we can stop assuming there are no gaps in the numbering.
		if profile_name not in sfera_profiles:
			break

		# Add profile in order to be simulated
		profiles[profile_name] = sfera_profiles[profile_name]

	return profiles


def main() -> None:
	parser = argparse.ArgumentParser(
		description='Analyze the decision tree module using the simulation module and breaking rules.'
	)

	parser.add_argument(
		'-i',
		'--input',
		metavar="sfera_automation.json",
		required=True,
		type=argparse.FileType('r', encoding='UTF-8'),
		help="Specify path to (custom) sfera_automation.json for the test profiles to be simulated."
	)

	parser.add_argument(
		'-p',
		'--prefix',
		metavar="profile_prefix",
		default="custom_",
		help="Specify prefix for custom profiles. Naming scheme is <prefix>{1...n}. (default: %(default)s)"
	)

	parser.add_argument(
		'-b',
		'--breaking',
		metavar="breaking_rules_dir",
		required=True,
		type=dir_path,
		help="Specify path to directory containing breaking rules to be simulated. Must include solution.json"
	)

	parser.add_argument(
		'-o',
		'--output',
		default="analysis_results.json",
		help="Specify path where to store the resulting json. (default: %(default)s)"
	)

	parser.add_argument(
		'--override',
		action='store_true',
		help="Override output file if it already exists."
	)

	# Add argument for loglevel to argparse
	add_loglevel_argument(parser, default_loglevel="info")

	args = parser.parse_args()

	# Set global loglevel
	logging.basicConfig(level=get_log_level(args))

	# Reduced loglevel for simulation and decision_tree
	logging.getLogger(simulate.__module__).setLevel(logging.ERROR)
	logging.getLogger(calculate_decision_tree.__module__).setLevel(logging.ERROR)

	# Load profiles from given sfera_automation.json
	sfera_data = json.load(args.input)
	sfera_profiles = sfera_data['profiles']

	# Filter profiles to be analyzed
	profiles = _filter_profiles(sfera_profiles, args.prefix)

	# Load solutions for breaking rules
	breaking_rules_solutions = json.load(open(args.breaking + "/solution.json"))

	# Initiate output
	output = {'valid': [], 'invalid': []}

	# Check simulation and decision tree result for each breaking-rules-set
	for breaking_rules_name in breaking_rules_solutions.keys():
		logger.info("Checking " + breaking_rules_name + ":")

		# Load breaking rules
		with open(args.breaking + "/" + breaking_rules_name + ".json", 'r') as f:
			breaking_rules = json.load(f)

		# Simulate execution of tests with given profiles and breaking rules
		simulation_results = simulate(profiles, breaking_rules)

		# Analyze the simulation results with the decision tree
		decision_tree = calculate_decision_tree(sfera_profiles['all_rules'], simulation_results)
		results = calculate_rules_to_remove(sfera_profiles['all_rules'], decision_tree.tree_)
		logger.debug("  Output: " + str(sorted(results)))

		# Check if the result is valid or not
		if sorted(results) in (sorted(r) for r in breaking_rules_solutions[breaking_rules_name]):
			logger.info("  Valid result")
			output['valid'].append(breaking_rules_name)
		else:
			logger.info("  Invalid result!")
			output['invalid'].append(breaking_rules_name)

	logger.info("\nValid results: " + str(len(output['valid'])))
	logger.info("\nInvalid results: " + str(len(output['invalid'])))

	export_to_json(args.output, output, args.override)


if __name__ == '__main__':
	main()
