
from accord import exceptions
from accord import common


import subprocess
import pathlib
import tarfile
import shlex
import time
import sys
import os
import re
import sh


log = common.define_logging_facility()


class Accord(object):
    def __init__(self, args):
        # Where to the backup files will be by default
        self.backup_directory = args.directory.rstrip('/')

        # Action to perform
        self.action = args.action.lower()

        if self.action == 'backup':
            self.archive = args.archive

        if self.action == 'restore':
            # Allow user to chose tar archive to restore from
            self.restore_file = args.restore_file

        # Backup file names
        self.var_lib_gravity_backup_name = "var_lib_gravity_backup.tar.gz"
        self.postgres_backup_name = "full_postgres_backup.sql"
        self.storage_backup_name = "storage_backup.tar.gz"
        self.repository_db_name = "all_repositories.tar"

        # AE5 default locations for data - DO NOT CHANGE
        self.postgres_container_backup = "/var/lib/postgresql/data"
        self.postgres_system_backup = "/opt/anaconda/storage/pgdata"

        # Generate some paths to make things easier in the code
        self.postgres_system_backup_path = "{0}/{1}".format(
            self.postgres_system_backup,
            self.postgres_backup_name
        )
        self.postgres_container_backup_path = "{0}/{1}".format(
            self.postgres_container_backup,
            self.postgres_backup_name
        )
        self.postgres_system_repo_backup_path = "{0}/{1}".format(
            self.postgres_system_backup,
            self.repository_db_name
        )
        self.postgres_container_repo_backup_path = "{0}/{1}".format(
            self.postgres_container_backup,
            self.repository_db_name
        )

        # Repository location
        self.repository = (
            "/opt/anaconda/storage/object/anaconda-repository"
        )
        # Signal file for restore
        if self.backup_directory != '':
            self.signal_file = f'{self.backup_directory}/restore'
        else:
            self.signal_file = 'restore'

        # Sync settings
        self.repos_only = args.repos_only
        if self.repos_only:
            # If only doing the repos then assume sync
            self.sync_files = True

        if self.action == 'restore':
            self.sync_files = False
            self.override = args.override
        else:
            self.sync_files = args.sync

        if self.action == 'backup' and self.sync_files:
            # Set the sync user and node
            self.sync_user = args.sync_user
            self.sync_node = args.sync_node

            if not self.sync_node:
                log.error('Node to sync files to not provided')
                raise exceptions.MissingSyncNode(
                    'Node to rsync files to was not provided. Please provide '
                    'the --sync-node switch with the node name'
                )

        # Secret files with namespaces
        self.secret_files = {
            'kube-system': [
                'cluster-tls',
            ],
            'default': [
                'anaconda-enterprise-certs',
                'anaconda-config-files'
            ]
        }
        # Config maps
        self.config_maps = {
            'default': [
                'anaconda-enterprise-anaconda-platform.yml',
            ],
        }

        # Running some checks to ensure that things are successful
        if (
            self.action == 'restore' and not
            self.override and
            self.restore_file is None
        ):
            if not self.check_for_restore():
                log.error('Restore signal not found')
                raise exceptions.RestoreSignal(
                    'Restore signal file not found, closing application'
                )

        if self.sync_files:
            self.test_sync_to_backup()

        if self.action == 'backup':
            self.setup_backup_directory()
            self.remove_signal_restore_file()

        # Always setting this to False since the option is not implemented
        # self.start_deployments = args.start_deployments
        self.start_deployments = False

        self.start_username = None
        self.start_password = None
        self.to_start = []

        self.no_config = args.no_config
        self.ingress = args.ingress

        self.namespace = 'default'
        self.postgres_pod = None
        self.docker_cont_id = None

        self.kubectl = sh.Command('kubectl')

    def check_for_restore(self):
        return os.path.isfile(self.signal_file)

    def test_sync_to_backup(self):
        test_sync_success = (
            f'/bin/ssh -t -q {self.sync_user}@{self.sync_node}'
            f' \'sudo cd /opt/anaconda\''
        )
        try:
            self.run_su_command(self.sync_user, test_sync_success)
        except Exception as e:
            log.error('Not able to connect to sync node')
            raise exceptions.UnableToSync(
                'Not able to connect connect and sudo as rsync user'
                f' {self.sync_user} to {self.sync_node}: {e}'
            )

    def add_signal_for_restore(self):
        open(self.signal_file, 'a').close()

    def remove_signal_restore_file(self):
        if os.path.exists(self.signal_file):
            os.remove(self.signal_file)

    def setup_backup_directory(self):
        if not os.path.exists(self.backup_directory):
            pathlib.Path(self.backup_directory).mkdir(parents=True)

        # Ensure that the backup directory on both clusters is setup
        if self.sync_files:
            setup_sync_folder = (
                f'/bin/ssh -t -q {self.sync_user}@{self.sync_node}'
                f' \'sudo mkdir -p {self.backup_directory}\''
            )
            self.run_su_command(self.sync_user, setup_sync_folder)

            set_permissions = (
                f'/bin/ssh -t -q {self.sync_user}@{self.sync_node}'
                f' \'sudo chown -R {self.sync_user}:{self.sync_user} '
                f'{self.backup_directory}\''
            )
            self.run_su_command(self.sync_user, set_permissions)

    def get_postgres_docker_container(self):
        temp_pods = self.kubectl('get', 'pods', '-n', self.namespace)
        for line in temp_pods:
            if 'postgres' in line:
                temp = (re.sub(r'\s+', ' ', line)).split(' ')
                self.postgres_pod = temp[0]
                break

        temp_container = self.kubectl(
            'describe',
            'pod',
            self.postgres_pod,
            '-n',
            self.namespace
        )
        for line in temp_container:
            if 'docker://' in line:
                temp = line.split('docker://')
                self.docker_cont_id = temp[1]
                break

        return

    def gravity_backup_restore(self, action):
        run_command = None
        gravity = sh.Command('gravity')
        if action == 'backup':
            run_command = (
                'backup', '{0}/{1}'.format(
                    self.backup_directory,
                    self.var_lib_gravity_backup_name
                )
            )
        elif action == 'restore':
            run_command = (
                'restore', '{0}/{1}'.format(
                    self.backup_directory,
                    self.var_lib_gravity_backup_name
                )
            )

        if run_command:
            gravity(run_command)

        return

    def get_all_secrets(self):
        if not self.secret_files.get(self.namespace):
            self.secret_files[self.namespace] = []

        temp_secrets = self.kubectl(
            'get',
            'secrets',
            '-n',
            self.namespace
        )
        for line in temp_secrets:
            if 'anaconda-credentials-' in line:
                temp = (re.sub(r'\s+', ' ', line)).split(' ')
                self.secret_files[self.namespace].append(temp[0])

    def get_all_ingress(self):
        backup_ingress = []
        all_ingress = sh.awk(
            sh.grep(
                self.kubectl('get', 'ingress', '-n', self.namespace),
                'ingress'
            ),
            '{print $1}'
        )
        for ingress in all_ingress.split('\n'):
            if not (
                'anaconda-session-ingress-' in ingress or
                'anaconda-app-ingress-' in ingress or
                ingress == ''
            ):
                backup_ingress.append(ingress)

        return backup_ingress

    def run_command_on_container(self, container, command, return_value=False):
        try:
            command_build = (
                'gravity exec docker exec -i {0} /bin/bash -c "{1}"'.format(
                    container,
                    command
                )
            )
            formatted_command = shlex.split(command_build)
            results = subprocess.run(
                formatted_command,
                stdout=subprocess.PIPE
            )
        except Exception as e:
            log.error(f'An exception {e} occurred running command: {command}')
            sys.exit(1)

        if return_value:
            return results.stdout

        return

    def run_su_command(self, user, command):
        try:
            command_build = (
                'su - {0} -c "{1}"'.format(user, command)
            )
            formatted_command = shlex.split(command_build)
            subprocess.run(formatted_command)
        except Exception as e:
            log.error(f'An exception {e} occurred running command: {command}')
            sys.exit(1)

        return

    def create_tar_archive(self):
        def filter_tar(tar_file):
            if (
                'repos_db_backup_' in tar_file.name or
                'ae5_backup_' in tar_file.name
            ):
                return None
            else:
                return tar_file

        if self.repos_only:
            archive_file = (
                f'repos_db_backup_{time.strftime("%Y%m%d-%H%M")}.tar.gz'
            )
        else:
            archive_file = (
                f'ae5_backup_{time.strftime("%Y%m%d-%H%M")}.tar.gz'
            )

        with tarfile.open(
            f'{self.backup_directory}/{archive_file}', 'w:gz'
        ) as tar:
            tar.add(
                self.backup_directory,
                arcname=os.path.basename(self.backup_directory),
                filter=filter_tar
            )

        if not tarfile.is_tarfile(f'{self.backup_directory}/{archive_file}'):
            raise exceptions.NotValidTarfile(
                'tar archive file was not able to create successfully'
            )

    def extract_tar_archive(self, to_directory='/opt'):
        if self.backup_directory != '/opt/anaconda_backup':
            temp_path = pathlib.Path(self.backup_directory)
            to_directory = temp_path.parent

        if not tarfile.is_tarfile(self.restore_file):
            raise exceptions.NotValidTarfile(
                'tar archive file is not a valid tar file'
            )

        # Ensure the backup is extracted to the right place
        sh.tar('-xzvf', self.restore_file, '-C', to_directory)

    def authenticate_api(self):
        pass

    def launch_deployment(self):
        pass
