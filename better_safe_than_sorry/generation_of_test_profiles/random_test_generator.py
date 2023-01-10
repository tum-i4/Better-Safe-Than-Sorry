import argparse
import json
import random
import logging
from typing import Sequence

from better_safe_than_sorry.utils.custom_logging import add_loglevel_argument, get_log_level
from better_safe_than_sorry.utils.custom_export import export_to_json

# Define Custom Types
Rule = str
Profile = Sequence[Rule]

# Define logger for the module
logger = logging.getLogger(__name__)


def randomized_profile(rules: Sequence[Rule], probability: float) -> Profile:
	profile = []

	for rule in rules:
		if random.random() <= probability:
			profile.append(rule)

	return profile


def main():
	parser = argparse.ArgumentParser(
		description='Randomly generate test profiles for sfera_automation.'
	)

	parser.add_argument(
		'-i',
		'--input',
		metavar="sfera_automation.json", required=True,
		type=argparse.FileType('r', encoding='UTF-8'),
		help="Specify path to sfera_automation.json to retrieve the input profile."
	)

	parser.add_argument(
		'-p',
		'--profile',
		default="all_rules",
		help="Specify which profile from the sfera_automation.json should be should be used as basis. (default: %(default)s)"
	)

	parser.add_argument(
		'--prefix',
		metavar="profile_prefix",
		default="custom_",
		help="Specify prefix for generated profiles. Naming scheme is <prefix>{1...n}. (default: %(default)s)"
	)

	parser.add_argument(
		'-o',
		'--output',
		default="custom_sfera_automation.json",
		help="Specify path where to store the resulting json. (default: %(default)s)"
	)

	parser.add_argument(
		'--override',
		action='store_true',
		help="Override output file if it already exists."
	)

	parser.add_argument(
		'-n',
		'--number_of_tests',
		required=True,
		type=int,
		dest='n',
		help="Number of tests/profiles that should be generated."
	)

	parser.add_argument(
		'--probability',
		default=0.3,
		type=float,
		help="Probability of a single rule being included in the output.(default: %(default)s)"
	)

	# Add argument for loglevel to argparse
	add_loglevel_argument(parser)

	args = parser.parse_args()

	# Set global loglevel
	logging.basicConfig(level=get_log_level(args))

	# Load data from sfera_automation.json
	data = json.load(args.input)

	# Load all profiles
	profiles = data['profiles']

	# Check if selected profile exists
	if args.profile not in profiles:
		logger.critical("Could not find profile '" + args.profile + "' in the input!\nAborting.")
		return

	# Load selected profile
	selected_profile = profiles[args.profile]  # type: Profile

	# Generate n randomized custom profiles
	for i in range(0, args.n):
		profiles[args.prefix + str(i + 1)] = randomized_profile(selected_profile, args.probability)

	# Write sfera_automation.json with custom profiles to file
	export_to_json(args.output, data, args.override)


if __name__ == '__main__':
	main()
