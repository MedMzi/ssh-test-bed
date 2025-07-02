#!/usr/bin/expect

#Usage sshsudologin.expect <host> <ssh user> <ssh password> <su user> <su password>

set timeout 60

#changed to use ssh-rsa and ssh-dss algorithms as the default algorithms are not supported by the OpenSSH versions in the Docker images
spawn ssh -p2222 -o HostKeyAlgorithms=+ssh-rsa,ssh-dss [lindex $argv 1]@[lindex $argv 0] ssh -V

expect "yes/no" { 
	send "yes\r"
	expect "*?assword" { send "[lindex $argv 2]\r" }
	} "*?assword" { send "[lindex $argv 2]\r" }

#expect "# " { send "su - [lindex $argv 3]\r" }
#expect ": " { send "[lindex $argv 4]\r" }
#expect "# " { send "ls -ltr\r" }
interact