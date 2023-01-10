# Load test-configuration
$test_config = Get-Content .\$tests_dir\test_configuration.json | Out-String | ConvertFrom-Json

# Function to check if a rule is currently applied or not
# Can be used for dummy-tests
function checkRule{
	param([string]$rule)
	$status = Check-Rule "$PSScriptRoot\..\$($test_config.sfera_directory)\sfera_automation.json" $rule
	
	if ( $status -eq "compliant" ){
		return $true
	} else {
		return $false
	}
}

# "Impossible test": Can be used to check the pre-tests
$impossible_test = $false

# Dummy-Tests that simply check if a rule has been applied (is compliant).
# The assumption would be that e.g. Rule 1.1.1 would break a certain functionality if applied.
$rule_111 = -not (checkRule "R1_1_1")
$rule_113 = -not (checkRule "R1_1_3")
$rule_114 = -not (checkRule "R1_1_4")
$rule_115 = -not (checkRule "R1_1_5") # R1.1.5 is always compliant on the Vagrant Box => Would lead to error in pre-tests


# Check account creation with short password
$test_acc_creation = & "$PSScriptRoot\test_account_creation.ps1"


return $test_acc_creation