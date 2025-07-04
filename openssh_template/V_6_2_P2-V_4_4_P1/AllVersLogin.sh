#!/usr/bin/expect

#Usage sshsudologin.expect <host> <ssh user> <ssh password> <su user> <su password>

set timeout 60

spawn ssh -p2222 -o HostKeyAlgorithms=+ssh-rsa,ssh-dss [lindex $argv 1]@[lindex $argv 0] {
  echo "kex:";
  strings /usr/local/sbin/sshd |
  tr ',' '\n' |
  grep -Ei 'diffie|curve|ecdh|sntrup|mlkem|x25519|4591761|kexguess|rsa[0-9]+-sha|kex-strict' |
  grep -E '^[a-z0-9\-]+(@[a-z0-9.\-]+)?$' |
  grep -vEi 'hmac|aes|cbc|gcm|ctr|zlib|none|chacha20|arcfour|blowfish|cast128|twofish|umac|ssh-dss|ecdsa|ssh-rsa' |
  tr -d '\r"' | sed 's/^"//;s/"$//' | sort -u ;
  echo "cipher:";
  strings /usr/local/sbin/sshd |
  tr ',' '\n' |
  grep -Ei 'aes|3des|arcfour|blowfish|cast128|twofish|chacha20|rijndael' |
  grep -E '^[a-z0-9\-]+(@[a-z0-9.\-]+)?$' |
  grep -viE 'diffie|curve|ecdh|sntrup|mlkem|x25519|kex|hmac|sha|zlib|none' |
  tr -d '\r"' | sed 's/^"//;s/"$//' | sort -u;
  echo "mac:";
  strings /usr/local/sbin/sshd | 
  tr ',' '\n' | 
  grep -Ei 'hmac|umac' | 
  grep -E '^[a-z0-9\-]+(@[a-z0-9.\-]+)?$' | 
  grep -vEi 'aes|cbc|gcm|ctr|zlib|none|chacha20|arcfour|blowfish|cast128|twofish|diffie|curve|ecdh|sntrup|mlkem|x25519|4591761|kexguess|rsa[0-9]+-sha|kex-strict' | 
  tr -d '\r"' | sed 's/^"//;s/"$//' |  sort -u;
  echo "compression:";
  strings /usr/local/sbin/sshd | 
  tr ',' '\n' | 
  grep -Ei 'none|zlib' | 
  grep -E '^[a-z0-9@.\-]+$' | 
  grep -vEi 'aes|cbc|gcm|ctr|chacha20|arcfour|blowfish|cast128|twofish|umac|hmac|diffie|curve|ecdh|sntrup|mlkem|x25519|rsa|kex|ssh-dss|ecdsa|ssh-rsa' | 
  tr -d '\r"' | sed 's/^"//;s/"$//' |  sort -u ;
  echo "key:";
  strings /usr/local/sbin/sshd | 
  tr ',' '\n' | 
  grep -Ei 'ecdsa-sha2|rsa-sha2|ssh-dss|ssh-ed25519|ssh-rsa' |
  grep -E '^[a-z0-9\-]+(@[a-z0-9.\-]+)?$' |
  grep -vEi 'hmac|aes|cbc|gcm|ctr|zlib|none|chacha20|arcfour|blowfish|cast128|twofish|umac|diffie|curve|ecdh|sntrup|mlkem|x25519|kexguess' |
  tr -d '\r"' | sed 's/^"//;s/"$//' |  sort -u ;
}


expect "yes/no" { 
	send "yes\r"
	expect "*?assword" { send "[lindex $argv 2]\r" }
	} "*?assword" { send "[lindex $argv 2]\r" }

#expect "# " { send "su - [lindex $argv 3]\r" }
#expect ": " { send "[lindex $argv 4]\r" }
#expect "# " { send "ls -ltr\r" }
interact