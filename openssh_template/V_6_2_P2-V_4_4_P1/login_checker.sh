#!/usr/bin/expect

#Usage sshsudologin.expect <host> <ssh user> <ssh password> <algtype> <algname>

set timeout 60

spawn ssh -oHostKeyAlgorithms=+ssh-rsa,ssh-dss -p2222 [lindex $argv 1]@[lindex $argv 0] ssh -o [lindex $argv 3]=[lindex $argv 4] betise

expect "yes/no" { 
	send "yes\r"
	expect "*?assword" { send "[lindex $argv 2]\r" }
	} "*?assword" { send "[lindex $argv 2]\r" }

#expect "# " { send "su - [lindex $argv 3]\r" }
#expect ": " { send "[lindex $argv 4]\r" }
#expect "# " { send "ls -ltr\r" }
expect eof