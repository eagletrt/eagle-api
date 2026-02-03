import paramiko


class ActiveDirAdmin:
    def __init__(self, ad_username: str, ad_password: str, ad_server: str):
        self._ad_username = ad_username
        self._ad_password = ad_password
        self._ad_server = ad_server

    def try_create_new_user(self, user: dict, temp_password: str) -> bool:
        command = (
            f'powershell -File C:\\API\\AddUser.ps1 '
            f"-FirstName \"{user['Name']}\" "
            f"-LastName \"{user['Surname']}\" "
            f"-Username \"{user['Team Email'].split('@')[0].lower()}\" "
            f"-InitialPassword '{temp_password}\" "
            f"-GroupName \"{user['AreaTag']}\""
        )

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                hostname=self._ad_server,
                username=self._ad_username,
                password=self._ad_password,
            )
            stdin, stdout, stderr = ssh.exec_command(command)
            exit_status = stdout.channel.recv_exit_status()
            ssh.close()

            return exit_status == 0
        except Exception as e:
            print(f"Error creating user: {e}")
            return False

    def enable_user(self, email: str) -> bool:
        pass

    def disable_user(self, email: str) -> bool:
        pass
