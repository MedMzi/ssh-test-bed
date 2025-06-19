#!/usr/bin/expect

#Usage sshsudologin.expect <host> <ssh user> <ssh password> <su user> <su password>

set timeout 60

spawn ssh -p2222 [lindex $argv 1]@[lindex $argv 0] grep LIBWOLFSSH_VERSION_STRING /usr/local/include/wolfssh/version.h

expect "yes/no" { 
	send "yes\r"
	expect "*?assword" { send "[lindex $argv 2]\r" }
	} "*?assword" { send "[lindex $argv 2]\r" }

expect eof

#expect "# " { send "su - [lindex $argv 3]\r" }
#expect ": " { send "[lindex $argv 4]\r" }
#expect "# " { send "ls -ltr\r" }