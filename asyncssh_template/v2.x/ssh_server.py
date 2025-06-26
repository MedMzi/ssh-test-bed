import asyncio
import asyncssh
import os
import sys

class MySSHServer(asyncssh.SSHServer):
    def connection_made(self, conn):
        print('SSH connection received from', conn.get_extra_info('peername'))

    def begin_auth(self, username):
        return True

    def password_auth_supported(self):
        return True

    def validate_password(self, username, password):
        return username == 'testuser' and password == 'root'



async def bridge_str_to_bytes(reader, writer):
    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            if isinstance(data, str):
                data = data.encode('utf-8')
            writer.write(data)
            await writer.drain()
    except Exception as e:
        print(f"Bridge error: {e}")
    finally:
        try:
            writer.write_eof()
        except Exception:
            pass

async def bridge_bytes_to_str(reader, writer):
    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            if isinstance(data, bytes):
                data = data.decode('utf-8', errors='ignore')
            writer.write(data)
            await writer.drain()
    except Exception as e:
        print(f"Bridge error: {e}")
    finally:
        try:
            writer.write_eof()
        except Exception:
            pass

async def start_bash_shell(process):
    bash = await asyncio.create_subprocess_shell(
    '/bin/bash -i',
    stdin=asyncio.subprocess.PIPE,
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE,
    # Use a PTY:
    # AsyncSSH will provide process.stdin/stdout as PTY
    )


    await asyncio.gather(
        bridge_str_to_bytes(process.stdin, bash.stdin),   # SSH input (str) -> bash stdin (bytes)
        bridge_bytes_to_str(bash.stdout, process.stdout), # bash stdout (bytes) -> SSH output (str)
        bridge_bytes_to_str(bash.stderr, process.stderr), # bash stderr (bytes) -> SSH output (str)
        bash.wait()
    )

    process.exit(0)


async def start_server():
    # Generate a server key if needed
    if not os.path.exists('ssh_host_key'):
        print('[+] Generating SSH server host key...')
        private_key = asyncssh.generate_private_key('ssh-rsa')
        with open('ssh_host_key', 'wb') as f:
            f.write(private_key.export_private_key())

    print('[+] Starting AsyncSSH server on port 8022...')
    await asyncssh.create_server(
        MySSHServer,
        '',
        8022,
        server_host_keys=['ssh_host_key'],
        process_factory=start_bash_shell
    )

    print('[+] Server is running. Waiting for connections...')
    await asyncio.Event().wait()  # keep alive forever

if __name__ == '__main__':
    try:
        asyncio.run(start_server())
    except (OSError, asyncssh.Error) as exc:
        print(f'[!] Error starting server: {exc}', file=sys.stderr)
        sys.exit(1)

