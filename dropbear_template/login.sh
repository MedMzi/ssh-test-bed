#!/usr/bin/expect

#Usage sshsudologin.expect <host> <ssh user> <ssh password> <su user> <su password>

set timeout 60

spawn ssh -i id_rsa_testuser \
	-oKexAlgorithms=diffie-hellman-group1-sha1,diffie-hellman-group14-sha256,curve25519-sha256 \
	-oHostKeyAlgorithms=ssh-dss,ssh-rsa,ecdsa-sha2-nistp256,rsa-sha2-256 \
	-oPubkeyAcceptedAlgorithms=+ssh-rsa \
	-oCiphers=aes128-cbc,chacha20-poly1305@openssh.com,aes256-ctr,aes128-ctr \
	-oMACs=hmac-sha1 \
	-p2222 [lindex $argv 1]@[lindex $argv 0] \
	/usr/local/bin/dbclient

expect "yes/no" { 
	send "yes\r"
	expect "*?assword" { send "[lindex $argv 2]\r" }
	} "*?assword" { send "[lindex $argv 2]\r" }

#expect "# " { send "su - [lindex $argv 3]\r" }
#expect ": " { send "[lindex $argv 4]\r" }
#expect "# " { send "ls -ltr\r" }
interact