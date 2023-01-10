# Test Execution with Vagrant

## Prepare Vagrant Directories for the Test Execution

### Usage

```shell
$ better-safe-than-sorry test-execution-with-vagrant prepare-vagrant-directories-for-the-test-execution --help
Usage: better-safe-than-sorry test-execution-with-vagrant prepare-vagrant-directories-for-the-test-execution [OPTIONS]
                                                          [VAGRANT_PATH]

  Creates multiple instances for automatic testing of the configurations
  within vagrant.

Arguments:
  [VAGRANT_PATH]  Specify path to vagrant directory including the necessary
                  base configuration.  [default: vagrant_dir]

Options:
  -c, --custom-sfera FILE         Specify path to sfera_automation.json with
                                  custom profiles. This file will be used in
                                  the output directories and overrides
                                  existing sfera_automation.json inside the
                                  vagrant directory. If no path is given, the
                                  sfera_automation.json from the vagrant
                                  directory will be used according to the
                                  test_configuration.
  -n, --number_vagrant_instances INTEGER
                                  Specify number of vagrant instances to be
                                  created.  [default: 4]
  -p, --prefix TEXT               Specify prefix for generated profiles.
                                  Naming scheme is <prefix>{1...n}.  [default:
                                  custom_]
  --prefix-n INTEGER              Specify n to be used with the prefix.
                                  Default is to automatically find the maximum
                                  value for n.  [default: -1]
  -a, --all_profiles              Use all profiles from the given
                                  sfera_automation.json. Overrides --prefix
                                  option.
  -t, --target_dir DIRECTORY      Specify path to directory to store the
                                  vagrant instances.  [default: instances]

```

#### Usage Example

```shell
better-safe-than-sorry test-execution-with-vagrant prepare-vagrant-directories-for-the-test-execution --custom-sfera custom_sfera_automation.json rsc/vagrant
```

## Start the Vagrant Instances

For this step, you need to install

- [Vagrant](https://www.vagrantup.com/)
- [VirtualBox](https://www.virtualbox.org/)

### Usage

```shell
$ better-safe-than-sorry test-execution-with-vagrant prepare-vagrant-directories-for-the-test-execution start-vagrant-instances --help
Usage: start-vagrant-instances [OPTIONS] [INPUT_DIRECTORY]

  Start the vagrant instances.

Arguments:
  [INPUT_DIRECTORY]  Specify path to directory with the vagrant instances.
                     [default: instances]

Options:
  -p, --parallel                  If this flag is set, we will start the
                                  instances in parallel.
```

#### Usage Example

```shell
better-safe-than-sorry test-execution-with-vagrant start-vagrant-instances
```

## Collect the Test Results from the Vagrant Directories

### Usage

```shell
$ better-safe-than-sorry test-execution-with-vagrant collect-the-test-results-from-the-vagrant-directories --help
Usage: collect-the-test-results-from-the-vagrant-directories
           [OPTIONS] [INPUT_DIRECTORY]

  Collects and combines the results of the vagrant instances into a single
  results.json

Arguments:
  [INPUT_DIRECTORY]  Specify path to directory with the vagrant instances.
                     (default: %(default)s)  [default: instances]

Options:
  -o, --output FILE               Specify path where to store the results.
                                  [default: results.json]
  --override                      Override output file if it already exists.
```

#### Usage Example

```shell
better-safe-than-sorry test-execution-with-vagrant collect-the-test-results-from-the-vagrant-directories
```
