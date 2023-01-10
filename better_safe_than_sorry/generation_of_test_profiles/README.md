# Generate Profiles based on Covering Arrays

## Combinatorial Testing / Covering Arrays

Calculate covering arrays using the [Automated Combinatorial Testing for Software](https://www.nist.gov/programs-projects/automated-combinatorial-testing-software-acts) (ACTS) tool from the National Institute of Standards and Technology (NIST).
From the NIST's website:

> To obtain the ACTS tool, please send a request to Rick Kuhn - [kuhn@nist.gov](mailto:kuhn@nist.gov) including your name and the name of your organization. No other information is required, but we like to have a list of organizations to show our management where the software is being used. We will send you a download link.


### Convert a profile from the sfera_automation.json to valid input for ACTS

Use `convert-a-profile-into-acts-input` command to convert the input in the `sfera_automation.json`.


```shell
$ better-safe-than-sorry generate-profiles-based-on-covering-arrays convert-a-profile-into-acts-input --help
Usage: sfera-to-acts [OPTIONS] [INPUT_FILE]

  Converts a sfera_automation profile to an ACTS model.

Arguments:
  [INPUT_FILE]  Specify path to sfera_automation.json which should be
                converted.  [default: sfera_automation.json]

Options:
  -p, --profile TEXT              Specify which profile from the
                                  sfera_automation.json should be converted to
                                  the ACTS model.  [default: all_rules]
  -o, --output FILE               Specify path where to store the ACTS model
                                  output.  [default:
                                  sfera_automation_acts.txt]
  --override                      Override output file if it already exists.
```

#### Usage Example

```shell
better-safe-than-sorry generate-profiles-based-on-covering-arrays convert-a-profile-into-acts-input rsc/sfera_automation_jsons/sfera_automation.json
```

### Use ACTS to calculate the n-way covering arrays

We can use ACTS to calculate the (n-way) covering arrays.

1. ACTS only **requires java** to be installed on the system.
Thus, you have to install java.
2. Get the ACTS from NIST
3. Execute the ACTS tool.

```shell
usage: java -Dalgo=<algorithm> -Ddoi=<n> -Doutput=csv -Dchandler=no -Dprogress=on -jar [-Xmx<space>] acts_3.2.jar <input> <output>

with:
- algorithm: ipog | ipog_d | ipof | ipof2 | basechoice | null, relevant for us are ipog and ipog_d
- n: [2-6], n-way covering arrays to be calculated
- input: path to the input file for ACTS, in out case the output of step 1
- output: path to store the output of ACTS (as .csv)

- space: set amount of heap space that can be allocated. E.g. -Xmx64g allocated 64 GB of memory for the heap.
```

#### Example: Calculate all 5-way covering arrays using IPOG-D

```shell
java -Dalgo=ipog_d -Ddoi=5 -Doutput=csv -Dchandler=no -Dprogress=on -jar -Xmx320g acts_3.2.jar sfera_automation_acts.txt 5_way.csv
```

### Convert the covering arrays to profiles for sfera_automation.json

```shell
$ better-safe-than-sorry generate-profiles-based-on-covering-arrays convert-acts-covering-arrays-into-sfera-profiles --help
Usage: convert-acts-covering-arrays-into-sfera-profiles [OPTIONS] [INPUT_FILE]

  Adds the output of an ACTS model as new profiles to a sfera_automation.json

Arguments:
  [INPUT_FILE]  Specify path to output.csv of ACTS.  [default:
                acts_output.csv]

Options:
  -s, --sfera FILE                Specify path to sfera_automation.json to
                                  which the new profiles should be added.
                                  [default: sfera_automation.json]
  -p, --prefix TEXT               Specify prefix for generated profiles.
                                  Naming scheme is <prefix>{1...n}.  [default:
                                  custom_]
  -o, --output FILE               Specify path where to store the resulting
                                  json.  [default:
                                  custom_sfera_automation.json]
```

#### Usage Example

```shell
better-safe-than-sorry generate-profiles-based-on-covering-arrays convert-acts-covering-arrays-into-sfera-profiles -s rsc/sfera_automation_jsons/sfera_automation.json 5_way.csv
```

## Random test profile generation
Alternative approach to generate test profiles by random generation. *N* profiles are created and in each profile a rule is included with the given *probability*.

```
usage: random_test_generator.py [-h] -i sfera_automation.json [-p PROFILE] [--prefix profile_prefix] [-o OUTPUT] [--override] -n N [--probability PROBABILITY] [--loglevel {debug,info,warning,error,critical}]

arguments:
  -h, --help            show the help message and exit
  -i sfera_automation.json, --input sfera_automation.json
                        Specify path to sfera_automation.json to retrieve the input profile.
  -p PROFILE, --profile PROFILE
                        Specify which profile from the sfera_automation.json should be should be used as basis. (default: all_rules)
  --prefix profile_prefix
                        Specify prefix for generated profiles. Naming scheme is <prefix>{1...n}. (default: custom_)
  -o OUTPUT, --output OUTPUT
                        Specify path where to store the resulting json. (default: custom_sfera_automation.json)
  --override            Override output file if it already exists.
  -n N, --number_of_tests N
                        Number of tests/profiles that should be generated.
  --probability PROBABILITY
                        Probability of a single rule being included in the output.(default: 0.3)
  --loglevel {debug,info,warning,error,critical}
                        Specify the desired loglevel. (choices: debug, info, warning, error, critical)
```