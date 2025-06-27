#!/usr/bin/expect

#Usage sshsudologin.expect <host> <ssh user> <ssh password> <su user> <su password>

set timeout 60

spawn ssh -p2222 [lindex $argv 1]@[lindex $argv 0]

expect {
    "yes/no" {
        send "yes\r"
        expect "*?assword" { send "[lindex $argv 2]\r" }
    }
    "*?assword" {
        send "[lindex $argv 2]\r"
    }
}

# After authentication, send the echo command
expect {
    "*# " {
        send "echo version \"\$(pkg-config --modversion libssh)\"\r"
		send "exit\r"
    }
}

# Allow user to continue interacting
interact