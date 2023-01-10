# Directory inside the vagrant folder that contains the test-scenarios and test_configuration
$tests_dir = "tests"

# Name of the test_configuration file
$test_config_filename = "test_configuration.json"

# Path of the local directory to work inside the VM
$dir = "~\Desktop\Test"

# Directory location of the synced folder on the VM
$vbox_dir = "\\VBOXSVR\vagrant\"

# ========== START SETTING UP THE VM ==========

# Set-ExecutionPolicy in order to allow the execution of the scripts
Set-ExecutionPolicy -ExecutionPolicy Bypass

# Move all files to the VMs storage (e.g. Desktop).
# This is necessary because the files cannot be executed from the shared directory.
mkdir $dir
cp -r $vbox_dir\* $dir

# Change to the local directory
cd $dir


# Load the test-configuration
$test_config = Get-Content .\$tests_dir\$test_config_filename | Out-String | ConvertFrom-Json

# Use sfera directory defined in the test_configuration
$sfera_dir = $($test_config.sfera_directory)

# Load sfera_automation.json
$sfera_json = "$sfera_dir\sfera_automation.json" 
$sfera_automation_json = Get-Content $sfera_json | Out-String | ConvertFrom-Json


# Source the sfera_automation scripts
. .\$sfera_dir\sfera_automation.ps1

# Download LGPO
Download-Lgpo

# ========== SETUP COMPLETE ==========


# ========== START WITH INITIAL TESTS ==========

# Check whether pre-tests were set to true in the test-configuration
if ( -not $($test_config.execute_pretests) ){
	"Pre-Tests are disabled in the test-configuration. Skipping..."
} else {
	"Executing Pre-Tests..."

	# Execute tests to check whether they fail even though no rule has been applied yet.
	# This could indicate errors in the tests.
	$test_result = & .\$tests_dir\test.ps1
	# Check if the tests failed
	if ( -not $test_result ){
		"Tests failed before applying any rules!`nPlease check that the used tests are indeed working as expected."
		return
	}


	# Next up: Apply all rules in order to check whether maybe there are no breaking rules for the tests
	Apply-All-Rules .\$sfera_json -profile all_rules -path_to_black_list $sfera_dir\blacklist.json

	$test_result = & .\$tests_dir\test.ps1
	# Check if the tests failed
	if ( $test_result ){
		"The tests showed no failure after applying all rules.`nYou can apply the 'all_rules' profile with no conflicts."
		return
	}


	# Now undo all rules and check whether the tests still pass.
	# If they don't pass, then one of the rules that cannot be undone is a breaking rule.
	Revert-All-Rules .\$sfera_json -profile all_rules -path_to_black_list $sfera_dir\blacklist.json

	$test_result = & .\$tests_dir\test.ps1
	# Check if the tests failed
	if ( -not $test_result ){
		"After applying and then reverting all rules, the tests fail.`nThere seems to be a conflict with one of the rules that cannot be reverted."
		return
	}
}

# ========== INITIAL TESTS COMPLETE ==========


# ========== START TESTING WITH COVERING ARRAYS ==========

# Prepare results.json
$results = @()

$test_profiles = $($test_config.profiles)

foreach ($test_profile in $test_profiles)
{
	"Checking $test_profile"
	
	# Apply rules of the test-profile
	Apply-All-Rules .\$sfera_json -profile $test_profile -path_to_black_list $sfera_dir\blacklist.json
	
	# Execute the tests
	$test_result = & .\$tests_dir\test.ps1
	
	# Add the test-result to the results.json
	$result = @{name = $test_profile; breaking = !$test_result; rules = $sfera_automation_json.profiles.$test_profile}
	$results += $result

	# Export results.json and move it to the shared folder
	$results | ConvertTo-Json | Out-File "results.json" -Encoding ascii
	mv -Force results.json $vbox_dir
	
	# Revert all rules of the test-profile
	Revert-All-Rules .\$sfera_json -profile $test_profile -path_to_black_list $sfera_dir\blacklist.json
}
