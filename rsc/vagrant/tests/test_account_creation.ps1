# Is broken e.g. by R1_1_4 which enforces a password length of at least 14.

$test_passed = $true

try {
	# Create new account for user 'testUser' with password 'Geh3!m'
	New-LocalUser -Name testUser -Password (ConvertTo-SecureString -String 'Geh3!m' -AsPlainText -Force) -ErrorAction Stop | Out-Null

} catch {
	# The test failed if an exception occured
	$test_passed = $false
}

# Remove created account
Remove-LocalUser -Name testUser

return $test_passed