package terraform
import future.keywords.in
import input as tfplan


#IAM password policy requires min length of 14 or greater
#IAM password policy expires passwords within 365 days
#IAM password policy prevents password reuse


#Policy to enforce password complexity requirements
#default allow_password = false

allow_password {
    input.planned_values.root_module.child_modules[_].resources[_].type == "oci_identity_user"
    instance := input.planned_values.root_module.child_modules[_].resources[_].instances[_].attributes
    password := instance.password

    count(password) >= 12
    password_contains_upper_case(password)
    password_contains_lower_case(password)
    password_contains_digit(password)
    password_contains_special_char(password)
    instance.name != password
}

password_contains_upper_case(password) {
    char := [c | c = password[_]; c >= "A" && c <= "Z"]
    count(char) > 0
}

password_contains_lower_case(password) {
    char := [c | c = password[_]; c >= "a" && c <= "z"]
    count(char) > 0
}

password_contains_digit(password) {
    char := [c | c = password[_]; c >= "0" && c <= "9"]
    count(char) > 0
}

password_contains_special_char(password) {
    char := [c | c = password[_]; c == "!" || c == "@" || c == "#" || c == "$" || c == "%" || c == "^" || c == "&" || c == "*"]
    count(char) > 0
}

#Policy to enforce the use of multi-factor authentication (MFA):
#default enforce_mfa = false
enforce_mfa {
    user := input.planned_values.root_module.child_modules[_].resources[_].instances[_].attributes
    user.type == "oci_identity_user"

    user.lifecycle != "delete"
    user.is_mfa_activated
}

deny[msg] {
     allow_password
     enforce_mfa
     allow := false

     msg := sprintf("%-10s: IAM passwd policy/user mfa not alligned with CIS benchmarks",[allow])
}