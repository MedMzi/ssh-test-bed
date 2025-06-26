#!/usr/bin/expect -f

set timeout 20
set host [lindex $argv 0]
set user [lindex $argv 1]
set password [lindex $argv 2]

log_user 1

spawn ssh -p 2222 $user@$host

expect {
    -re "Are you sure you want to continue connecting.*" {
        send "yes\r"
        exp_continue
    }
    -re {\(?\w+@[\w\.\-]+(\))? Password:} {
        send "$password\r"
        exp_continue
    }
    -re {root@[^#]+# } {
        send "python3 -c \"import asyncssh; print('AsyncSSH version', asyncssh.__version__)\"\r"
        expect {
            -re {\r\n(.*)\r\nroot@[^#]+# } {
                send "exit\r"
                exit
            }
            timeout {
                exit 1
            }
        }
    }
    timeout {
        puts "Timeout or unexpected prompt"
        exit 1
    }
}



