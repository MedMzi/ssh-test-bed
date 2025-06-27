#include <libssh/libssh.h>
#include <libssh/server.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#define USERNAME "testuser"
#define PASSWORD "root"

int main() {
    ssh_bind sshbind = ssh_bind_new();
    ssh_session session = ssh_new();
    ssh_message message;
    ssh_channel channel = NULL;
    int auth = 0;

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

    // You can respond to shell/exec requests here if needed
    const char *version = ssh_version(0);
    char msg[128];
    
    snprintf(msg, sizeof(msg), "libssh version: %s\n", version);
    ssh_channel_write(channel, msg, strlen(msg));
    
    ssh_channel_send_eof(channel);
    ssh_channel_close(channel);
    ssh_channel_free(channel);    

    ssh_disconnect(session);
    ssh_free(session);
    ssh_bind_free(sshbind);

    return 0;
}
