import paramiko
import os

class NavigateSFTP:
    def __init__(self, host, username, private_key_path):
        self.host = host
        self.username = username
        self.private_key_path = private_key_path
        self.client = None
        self.sftp = None

    def connect(self):
        """ Connect to the SFTP server """
        try:
            # Load private key
            key = paramiko.RSAKey(filename=self.private_key_path)

            # Create SSH client
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect to SFTP server
            self.client.connect(self.host, username=self.username, pkey=key)
            self.sftp = self.client.open_sftp()
            print("Connection successfully established.")
        except Exception as e:
            print(f"Failed to connect: {str(e)}")

    def list_files(self, remote_path='.'):
        """ List files in a remote directory """
        try:
            files = self.sftp.listdir(remote_path)
            return files
        except Exception as e:
            print(f"Failed to list files: {str(e)}")
            return []

    def download_file(self, remote_file, local_file):
        """ Download a file from the SFTP server """
        try:
            self.sftp.get(remote_file, local_file)
            print(f"Successfully downloaded {remote_file} to {local_file}.")
        except Exception as e:
            print(f"Failed to download file: {str(e)}")

    def upload_file(self, local_file, remote_file):
        """ Upload a file to the SFTP server """
        try:
            self.sftp.put(local_file, remote_file)
            print(f"Successfully uploaded {local_file} to {remote_file}.")
        except Exception as e:
            print(f"Failed to upload file: {str(e)}")

    def close(self):
        """ Close the SFTP connection """
        if self.sftp:
            self.sftp.close()
        if self.client:
            self.client.close()
        print("Connection closed.")
