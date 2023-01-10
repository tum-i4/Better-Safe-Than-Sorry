import argparse
import json
import os
import logging
import pathlib
import random
import re


def dir_path(path):  # See https://stackoverflow.com/questions/38834378/path-to-a-directory-as-argparse-argument
	if os.path.isdir(path):
		return path
	else:
		raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


parser = argparse.ArgumentParser(description='Generate randomized variants of a breaking_ruleset.')

parser.add_argument('-s', '--sfera', metavar="sfera_automation.json", required=True, type=argparse.FileType('r', encoding='UTF-8'), help="Specify path to sfera_automation.json for the all_rules profile.")
parser.add_argument('-b', '--breaking', default="breaking_rules", type=dir_path, metavar="breaking_rules_dir", help="Specify path to directory with the breaking_rulesets. (default: %(default)s)")
parser.add_argument('-r', '--ruleset', required=True, type=str, help="Specify the breaking_ruleset for which the variant should be generated. E.g. 1_1")
parser.add_argument("-n", default=1, type=int, help="Number of random variants to be generated (default: %(default)s)")
parser.add_argument('--override', action='store_true', help="Override output file if it already exists.")
parser.add_argument('--loglevel', default="info", choices=["debug", "info", "warning", "error", "critical"], help="Specify the desired loglevel. (choices: %(choices)s)")

args = parser.parse_args()

def exportJSON(filepath: str, output_json, override: bool):
	# Check if output-file already exists
	if os.path.exists(filepath) and not override:
		print(filepath + " already exists. Override? [y/n]")

		while True:
			user_input = input().lower()
			if user_input in {'y', 'yes'}:
				break
			elif user_input in {'n', 'no'}:
				logging.critical("Aborting.")
				return
			else:
				print("Please respond with yes or no [y/n]")

	# Write output to disk
	with open(filepath, "w") as file:
		json.dump(output_json, file, ensure_ascii=False, indent=4)

	logging.info("Saved output to " + filepath)


def export(filepath: str, output: str, override: bool):
	# Check if file already exists
	if os.path.exists(filepath) and not override:
		print(filepath + " already exists. Override? [y/n]")

		while True:
			user_input = input().lower()
			if user_input in {'y', 'yes'}:
				break
			elif user_input in {'n', 'no'}:
				logging.critical("Aborting.")
				return
			else:
				print("Please respond with yes or no [y/n]")

	# Write ACTS file to disk
	with open(filepath, "w") as file:
		file.write(output)

	logging.info("Saved output to " + filepath)


def main():
	# Define paths to directories and files
	breaking_rules_dir = pathlib.Path(args.breaking)

	solutions_file = breaking_rules_dir / "solution.json"
	breaking_rules_file = breaking_rules_dir / (args.ruleset + ".json")

	# Load sfera_automation.json and the all_rules profile
	sfera_json = json.load(args.sfera)
	all_rules = sfera_json['profiles']['all_rules']  # type: list[str]

	# Load the breaking_ruleset for which randomized variants should be generated
	breaking_rules_input = json.load(breaking_rules_file.open())
	breaking_rules_raw = breaking_rules_file.read_text()

	# Read the solutions.json as raw string (we will simply replace text in there)
	solutions_raw = solutions_file.read_text()

	# Regex for a ruleblock (the AND connection)
	ruleblock = "\[(?:\".+\",?)*\]"
	# Regex for potentially multiple lines of ruleblocks (the OR connections)
	multiruleblock = '\[' + ruleblock + '(?:,\n( |\t)*' + ruleblock + ')*\]'
	# Regex for a ruleset
	regex = '"' + args.ruleset + '": (' + multiruleblock + ',)'
	#print(regex)
	
	# Find the ruleset in the solutions by searching for the regex.
	# group(0) includes the whole string, group(1) only the multiruleblock
	subsolutions_raw0 = re.search(regex, solutions_raw).group(0)
	subsolutions_raw = re.search(regex, solutions_raw).group(1)

	# Get all rules used in the breaking_ruleset
	used_rules = set()
	for rules in breaking_rules_input:
		if isinstance(rules, list):
			for rule in rules:
				used_rules.add(rule)
		else:
			used_rules.add(rules)

	# Remove used rules from all_rules because we do not want to replace a rule by an already used rule.
	for rule in used_rules:
		all_rules.remove(rule)

	# Generate the n randomized variants
	for i in range(args.n, 0, -1):
		# Define the name of the new breaking_ruleset. It is the previous name with the suffix _ri with i in [1,n]
		new_ruleset_name = args.ruleset + "_r" + str(i)

		# Remove potentially already existing entries from the solution.
		# E.g. if you already generated random variants for 1_1, we do not want the previous 1_1_r1, 1_1_r2 etc. in the solutions
		entry = re.search("( |\t)*\"" + new_ruleset_name + "\": " + multiruleblock + ",\n", solutions_raw)
		if entry:
			solutions_raw = solutions_raw.replace(entry.group(0), '')

		# Copy the strings for local copies
		newsolutions_raw = subsolutions_raw
		newbreaking_rules_raw = breaking_rules_raw

		# Local copy of all_rules
		available_rules = all_rules.copy()

		# Replace every rule used in the breaking_ruleset by a random other rule
		for rule in used_rules:
			# Choose random rule
			random_rule = random.choice(available_rules)
			
			# Remove this rule from the available rule. We only want to use it once.
			available_rules.remove(random_rule)

			# Replace rule with the random rule both in the breaking_ruleset but also in the solution
			newbreaking_rules_raw = newbreaking_rules_raw.replace('"' + rule + '"', '"' + random_rule + '"')
			newsolutions_raw = newsolutions_raw.replace('"' + rule + '"', '"' + random_rule + '"')

		# Add the new gernerated solution to the solutions
		solutions_raw = solutions_raw.replace(
			subsolutions_raw0,
			subsolutions_raw0 + "\n\t\"" + new_ruleset_name + "\": " + newsolutions_raw
		)

		# Save the new random variant of the breaking_ruleset
		export(args.breaking + "/" + new_ruleset_name + ".json", newbreaking_rules_raw, args.override)

	# Save the new solutions
	export(args.breaking + "/solution.json", solutions_raw, args.override)


if __name__ == '__main__':
	# Set loglevel
	loglevel = {'debug': logging.DEBUG, 'info': logging.INFO, 'warning': logging.WARNING, 'error': logging.ERROR, 'critical': logging.CRITICAL}
	logging.basicConfig(level=loglevel[args.loglevel])

	main()
