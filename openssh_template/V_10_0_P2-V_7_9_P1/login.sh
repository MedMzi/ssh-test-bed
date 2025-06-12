#!/usr/bin/expect

#Usage sshsudologin.expect <host> <ssh user> <ssh password> <su user> <su password>

set timeout 60

spawn ssh -p2222 [lindex $argv 1]@[lindex $argv 0] ssh -V

expect "yes/no" { 
	send "yes\r"
	expect "*?assword" { send "[lindex $argv 2]\r" }
	} "*?assword" { send "[lindex $argv 2]\r" }

#expect "# " { send "su - [lindex $argv 3]\r" }
#expect ": " { send "[lindex $argv 4]\r" }
#expect "# " { send "ls -ltr\r" }
interact