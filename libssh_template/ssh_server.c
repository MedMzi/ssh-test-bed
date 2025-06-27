#include <libssh/libssh.h>
#include <libssh/server.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <pty.h>
#include <unistd.h>
#include <sys/select.h>
#include <sys/wait.h>
#include <signal.h>
#include <fcntl.h>

#define USERNAME "testuser"
#define PASSWORD "root"

int main() {
    ssh_bind sshbind = ssh_bind_new();
    ssh_session session = ssh_new();
    ssh_message message;
    ssh_channel channel = NULL;
    int auth = 0;
    pid_t pid;
    int pty_fd;


    ssh_bind_options_set(sshbind, SSH_BIND_OPTIONS_BINDPORT_STR, "2222");
    ssh_bind_options_set(sshbind, SSH_BIND_OPTIONS_HOSTKEY, "ssh-rsa");
    ssh_bind_options_set(sshbind, SSH_BIND_OPTIONS_RSAKEY, "/etc/ssh/ssh_host_rsa_key");

    if (ssh_bind_listen(sshbind) < 0) {
        fprintf(stderr, "Error listening: %s\n", ssh_get_error(sshbind));
        return 1;
    }

    if (ssh_bind_accept(sshbind, session) != SSH_OK) {
        fprintf(stderr, "Error accepting connection: %s\n", ssh_get_error(sshbind));
        return 1;
    }

    if (ssh_handle_key_exchange(session)) {
        fprintf(stderr, "Key exchange failed: %s\n", ssh_get_error(session));
        return 1;
    }

    // Authentication loop
    do {
        message = ssh_message_get(session);
        if (!message) break;

        if (ssh_message_type(message) == SSH_REQUEST_AUTH &&
            ssh_message_subtype(message) == SSH_AUTH_METHOD_PASSWORD &&
            strcmp(ssh_message_auth_user(message), USERNAME) == 0 &&
            strcmp(ssh_message_auth_password(message), PASSWORD) == 0) {
            ssh_message_auth_reply_success(message, 0);
            auth = 1;
            ssh_message_free(message);
            break;
        } else {
            ssh_message_auth_set_methods(message, SSH_AUTH_METHOD_PASSWORD);
            ssh_message_reply_default(message);
        }

        ssh_message_free(message);
    } while (!auth);

    if (!auth) {
        fprintf(stderr, "Authentication failed.\n");
        ssh_disconnect(session);
        ssh_free(session);
        return 1;
    }

    printf("Authentication successful! libssh version: %s\n", ssh_version(0));

    // Wait for channel request
    do {
        message = ssh_message_get(session);
        if (!message)
            break;

        if (ssh_message_type(message) == SSH_REQUEST_CHANNEL_OPEN &&
            ssh_message_subtype(message) == SSH_CHANNEL_SESSION) {
            channel = ssh_message_channel_request_open_reply_accept(message);
            ssh_message_free(message);
            break;
        }

        ssh_message_reply_default(message);
        ssh_message_free(message);
    } while (!channel);

    if (!channel) {
        fprintf(stderr, "Channel opening failed.\n");
        ssh_disconnect(session);
        ssh_free(session);
        return 1;
    }


    
    
    if ((pid = forkpty(&pty_fd, NULL, NULL, NULL)) == -1) {
        perror("forkpty failed");
    } else if (pid == 0) {
        // Child: execute shell
        execl("/bin/bash", "/bin/bash", NULL);
        perror("execl failed");
        exit(1);
    } else {
        // Parent: bridge PTY <-> SSH channel
        fd_set fds;
        char buf[256];
        int len;
    
        // Make SSH channel non-blocking
        ssh_channel_set_blocking(channel, 0);
    
        while (ssh_channel_is_open(channel)) {
            FD_ZERO(&fds);
            FD_SET(pty_fd, &fds);
            int maxfd = pty_fd;
    
            struct timeval timeout = {1, 0}; // 1 second timeout
            if (select(maxfd + 1, &fds, NULL, NULL, &timeout) > 0) {
                if (FD_ISSET(pty_fd, &fds)) {
                    len = read(pty_fd, buf, sizeof(buf));
                    if (len <= 0) break;
                    ssh_channel_write(channel, buf, len);
                }
            }
    
            // Non-blocking read from SSH channel
            len = ssh_channel_read_nonblocking(channel, buf, sizeof(buf), 0);
            if (len > 0) {
                write(pty_fd, buf, len);
            } else if (len == SSH_ERROR) {
                break;
            }
        }
    
        kill(pid, SIGHUP);
        waitpid(pid, NULL, 0);
        ssh_channel_send_eof(channel);
        ssh_channel_close(channel);
        ssh_channel_free(channel);
    }

    ssh_disconnect(session);
    ssh_free(session);
    ssh_bind_free(sshbind);
    return 0;
}


    
