#!/usr/bin/expect

set timeout 60

# Read script contents into a variable
set f [open "dropbearQ.sh" r]
set script_data [read $f]
close $f

# Spawn SSH session WITHOUT 'sh -s'
spawn ssh -i id_rsa_testuser \
	-oKexAlgorithms=diffie-hellman-group1-sha1,diffie-hellman-group14-sha256,curve25519-sha256 \
	-oHostKeyAlgorithms=ssh-dss,ssh-rsa,ecdsa-sha2-nistp256,rsa-sha2-256 \
	-oPubkeyAcceptedAlgorithms=+ssh-rsa \
	-oCiphers=aes128-cbc,chacha20-poly1305@openssh.com,aes256-ctr,aes128-ctr \
	-oMACs=hmac-sha1 \
	-p2222 [lindex $argv 1]@[lindex $argv 0] \

expect {
    "yes/no" {
        send "yes\r"
        expect "*?assword" { send "[lindex $argv 2]\r" }
    }
    "*?assword" {
        send "[lindex $argv 2]\r"
    }
}

# Wait for shell prompt
expect -re {[\$#] $}

# Send script contents line by line with delays
foreach line [split $script_data "\n"] {
    send -- "$line\r"
    sleep 0.05
}

# Add small buffer before exit
sleep 0.5
send -- "exit\r"

interact
