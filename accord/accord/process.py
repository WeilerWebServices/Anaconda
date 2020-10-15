
from accord.models import Accord
from accord import exceptions
from accord import common


import argparse
import datetime
import pathlib
import json
import time
import yaml
import glob
import sys
import os
import sh


log = common.define_logging_facility()


def backup_postgres_database(process):
    process.get_postgres_docker_container()
    backup_command = (
        "su - postgres -c 'pg_dumpall -U postgres --clean -f "
        f"{process.postgres_container_backup_path}'"
    )
    # Check for existing sql file and if there remove it
    if os.path.isfile(process.postgres_system_backup_path):
        os.remove(process.postgres_system_backup_path)

    # Backup the repository
    process.run_command_on_container(process.docker_cont_id, backup_command)

    # Check for the file and ensure it is there
    if not os.path.isfile(process.postgres_system_backup_path):
        log.error('Could not find backup file for postgres')
        raise exceptions.NoPostgresBackup(
            'Could not find backup file for postgres'
        )

    # Move the backup to the backup directory
    sh.mv(
        process.postgres_system_backup_path,
        f'{process.backup_directory}/'
    )


def backup_repository_db(process):
    process.get_postgres_docker_container()
    backup_command = (
        "su - postgres -c 'pg_dump -U postgres -F t anaconda_repository > "
        f"{process.postgres_container_repo_backup_path}'"
    )
    # Check for existing backup file and if there remove it
    if os.path.isfile(f'{process.postgres_system_repo_backup_path}'):
        os.remove(f'{process.postgres_system_repo_backup_path}')

    # Backup the repository
    process.run_command_on_container(process.docker_cont_id, backup_command)

    # Check for file path and ensure that it created
    if not os.path.isfile(f'{process.postgres_system_repo_backup_path}'):
        log.error('Could not find backup file for postgres')
        raise exceptions.NoPostgresBackup(
            'Could not find backup file for postgres'
        )

    # Move the backup to the backup directory
    sh.mv(
        f'{process.postgres_system_repo_backup_path}',
        f'{process.backup_directory}/'
    )


def restore_postgres_database(process):
    process.get_postgres_docker_container()

    # Copy SQL backup to the DB directory so the container can see it
    sh.mv(
        f'{process.backup_directory}/{process.postgres_backup_name}',
        process.postgres_system_backup_path
    )

    # Change permissions on the backup
    sh.chown(
        'polkitd:input',
        process.postgres_system_backup_path
    )
    restore_command = (
        "su - postgres -c 'psql -U postgres < "
        f"{process.postgres_container_backup_path}'"
    )
    process.run_command_on_container(process.docker_cont_id, restore_command)


def file_backup_restore(process, action):
    if action == 'backup':
        with sh.pushd('/opt/anaconda'):
            sh.tar(
                "--exclude=storage/pgdata",
                "--exclude=storage/object/anaconda-repository",
                "-czvf",
                process.storage_backup_name,
                "storage"
            )

        sh.mv(
            f'/opt/anaconda/{process.storage_backup_name}',
            f'{process.backup_directory}/'
        )
    elif action == 'restore':
        sh.cp(
            f'{process.backup_directory}/{process.storage_backup_name}',
            '/opt/anaconda'
        )
        with sh.pushd('/opt/anaconda'):
            sh.tar(
                '-xzvf',
                f'/opt/anaconda/{process.storage_backup_name}'
            )
            sh.rm(f'{process.storage_backup_name}')


def backup_secrets_config_maps(process):
    secret_path = f'{process.backup_directory}/secrets'
    if not os.path.exists(secret_path):
        pathlib.Path(secret_path).mkdir(parents=True)

    process.get_all_secrets()
    for namespace, secrets in process.secret_files.items():
        for secret in secrets:
            temp_secret_path = f'{secret_path}/{secret}.yaml'
            try:
                with open(temp_secret_path, 'w') as fs:
                    process.kubectl(
                        'get',
                        'secrets',
                        secret,
                        '-n',
                        namespace,
                        '-o',
                        'yaml',
                        _out=fs
                    )
            except sh.ErrorReturnCode_1:
                log.error(f'Could not backup {secret} as it was not found')
                raise exceptions.SecretNotFound(
                    f'{secret} has been removed and cannot be backed up'
                )

    for namespace, config_maps in process.config_maps.items():
        for cm in config_maps:
            temp_cm_path = f'{secret_path}/{cm}.yaml'
            try:
                with open(temp_cm_path, 'w') as fcm:
                    process.kubectl(
                        'get',
                        'configmaps',
                        cm,
                        '-n',
                        namespace,
                        '-o',
                        'yaml',
                        _out=fcm
                    )
            except sh.ErrorReturnCode_1:
                log.error(f'Could not backup {cm} as it was not found')
                raise exceptions.ConfigMapNotFound(
                    f'{cm} has been removed and cannot be backed up'
                )

    return


def backup_ingress_definitions(process):
    ingress_path = f'{process.backup_directory}/ingress'
    if not os.path.exists(ingress_path):
        pathlib.Path(ingress_path).mkdir(parents=True)

    all_ingress = process.get_all_ingress()
    for ingress in all_ingress:
        if ingress not in ['', '\n']:
            temp_ingress_path = f'{ingress_path}/{ingress}.yaml'
            try:
                with open(temp_ingress_path, 'w') as fing:
                    process.kubectl(
                        'get',
                        'ingress',
                        ingress,
                        '-o',
                        'yaml',
                        _out=fing
                    )
            except sh.ErrorReturnCode_1:
                if os.path.isfile(temp_ingress_path):
                    os.remove(temp_ingress_path)
                log.error(f'Could not backup {ingress}')
                raise exceptions.IngressError(f'{ingress} cannot be backed up')


def sanitize_secrets_config_maps(process):

    def _remove_fields(temp_yaml, metadata_to_clear):
        """
        For now just create function for repetitive code that's only used here
        """
        with open(temp_yaml, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

        for label in metadata_to_clear:
            try:
                del data['metadata'][label]
            except Exception:
                # Means the key is not there which is ok if it is not
                pass


        with open(temp_yaml, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)

    # back to original function
    # f:type in managedFields is causing validation failure; for now just remove section
    metadata_to_clear = [
        "creationTimestamp",
        "resourceVersion",
        "generation",
        "selfLink",
        "uid",
        "managedFields"]

    for namespace, secrets in process.secret_files.items():
        for secret in secrets:
            temp_secret = f'{process.backup_directory}/secrets/{secret}.yaml'
            _remove_fields(temp_secret, metadata_to_clear)
            
    for namespace, config_maps in process.config_maps.items():
        for cm in config_maps:
            temp_cm = f'{process.backup_directory}/secrets/{cm}.yaml'
            _remove_fields(temp_cm, metadata_to_clear)
           
    ingress_files = glob.glob(f'{process.backup_directory}/ingress/*.yaml')
    for ingress in ingress_files:
        _remove_fields(ingress, metadata_to_clear)


def sync_files(process):
    # Set permissions to rsync user for all of the backup directory
    sh.chown(
        '-R',
        f'{process.sync_user}:{process.sync_user}',
        f'{process.backup_directory}'
    )

    # Run the rsync to the sync server
    rsync_command = (
        f'rsync -avrq {process.backup_directory}/ '
        f'{process.sync_user}@{process.sync_node}:{process.backup_directory}'
    )
    process.run_su_command(process.sync_user, rsync_command)


def sync_repositories(process):
    # Change permissions for the repo directories
    user_perms_command = (
        f'/bin/ssh -t -q {process.sync_user}@{process.sync_node}'
        f' \'sudo chown -R {process.sync_user}:{process.sync_user} '
        f'{process.repository}\''
    )
    process.run_su_command(process.sync_user, user_perms_command)

    # Run the rsync for all of the repository directories
    rsync_command = (
        f'rsync -avrq {process.repository}/ '
        f'{process.sync_user}@{process.sync_node}:{process.repository}'
    )
    process.run_su_command(process.sync_user, rsync_command)

    # Change the permissions back after the rsync
    root_perms_command = (
        f'/bin/ssh -t -q {process.sync_user}@{process.sync_node}'
        f' \'sudo chown -R root:root '
        f'{process.repository}\''
    )
    process.run_su_command(process.sync_user, root_perms_command)


def scale_postgres_pod(process, pod_number):
    if pod_number not in [1, 0]:
        log.error('Invalid replica count to scale for postgres')
        raise exceptions.InvalidReplicaCount(
            'Invalid replica count to scale for postgres'
        )

    process.kubectl(
        'scale',
        'deploy',
        f'--replicas={pod_number}',
        'anaconda-enterprise-postgres'
    )
    success = False
    while success is False:
        if pod_number == 1:
            try:
                sh.grep(
                    sh.grep(
                        process.kubectl('get', 'pods'),
                        'postgres'
                    ),
                    'Running'
                )
                success = True
            except sh.ErrorReturnCode_1:
                pass
                """
                Exception will be thrown as no results will be given and
                it is running then it will exit properly
                """
        else:
            try:
                sh.grep(process.kubectl('get', 'pods'), 'postgres')
            except sh.ErrorReturnCode_1:
                """
                Exception will be thrown as no results will be given which
                is the desired result on the scale down
                """
                success = True

        # Waiting for postgres pod to complete scale
        time.sleep(2)

    return


def cleanup_and_restore_files(process):
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H%M%S')
    # Compress and timestamp the existing files minus the repos
    with sh.pushd('/opt/anaconda'):
        sh.tar(
            "--exclude=storage/object/anaconda-repository",
            "-czvf",
            f"git_pgdata.snapshot_{timestamp}.tar.gz",
            "storage"
        )

    # Cleanup directories as things will get restored
    sh.rm('-Rf', '/opt/anaconda/storage/git')
    sh.rm('-Rf', '/opt/anaconda/storage/pgdata')
    sh.rm('-Rf', '/opt/anaconda/storage/object/anaconda-objects')
    sh.rm('-Rf', '/opt/anaconda/storage/object/anaconda-projects')

    # Restore the files
    file_backup_restore(process, 'restore')

    # Recreate the postgres directory and set permissions
    sh.mkdir(process.postgres_system_backup)
    sh.chown('999:root', f'{process.postgres_system_backup}')
    sh.chmod('700', f'{process.postgres_system_backup}')

    return


def restart_pods(process):
    # Restart all the pods after the restore
    process.kubectl('delete', '--all', 'pods')

    # Watch the pods and make sure they come back up
    success = False
    while success is False:
        try:
            sh.grep(
                sh.grep(
                    process.kubectl('get', 'pods'),
                    '-v',
                    'Running'
                ),
                '-v',
                'NAME'
            )
        except sh.ErrorReturnCode_1:
            """
            When sh throws exception it means nothing returned
            which is what we are waiting for
            """
            success = True

        # Waiting for postgres pod to complete scale
        time.sleep(2)


def cleanup_sessions_deployments(process):
    # Grab all sessions and deployments and remove them
    deployments = []
    try:
        deployments = sh.awk(
            sh.grep(
                process.kubectl('get', 'deployments'),
                'anaconda-app-\|anaconda-session-'  # noqa
            ),
            '{print $1}'
        )
    except Exception:
        # Ok if exception thrown as it means nothing was found
        pass

    for deploy in deployments:
        process.kubectl('delete', 'deployment', deploy.strip())

    return


def cleanup_postgres_database(process):
    # Get the docker container IDs
    process.get_postgres_docker_container()

    # Cleanup the sessions so there are no running sessions in the DB
    session_cleanup = (
        "su - postgres -c 'psql -U postgres -d "
        "anaconda_workspace -c \\\"delete from sessions;\\\"'"
    )
    process.run_command_on_container(process.docker_cont_id, session_cleanup)

    """
    After DB restore grab all deployments that are in a started state. This
    will allow for deployments to be started after everything has been
    restored properly
    """
    deployments_gather = (
        "su - postgres -c 'psql -t -U postgres -d anaconda_deploy "
        "-c \\\"select row_to_json(t) from(select * from deployments) t;\\\"'"
    )
    return_select = process.run_command_on_container(
        process.docker_cont_id,
        deployments_gather,
        return_value=True
    )
    rows = return_select.decode('utf-8').split('\n')
    for row in rows:
        if row not in ['', None] and 'FATAL' not in row:
            temp_row = json.loads(row)
            if temp_row.get('status_text', None) == 'Started':
                process.to_start.append(temp_row)

    # Cleanup the deployments so there are no running deployments in the DB
    deployments_cleanup = (
        "su - postgres -c 'psql -U postgres -d "
        "anaconda_deploy -c \\\"truncate deployments cascade;\\\"'"
    )
    process.run_command_on_container(
        process.docker_cont_id,
        deployments_cleanup
    )
    return


def restoring_files(process):
    # Grab all of the yaml files that were backed up and replace/create them
    # within the restore cluster

    def restore_resource(restore_file, action='replace'):
        # replace or create a resource
        replace_return = process.kubectl(action, '-f', restore_file)
        log.info(f'{action} resource {restore_file}')
        log.info(f'Command returned: {replace_return}')

    restore_files = glob.glob(f'{process.backup_directory}/secrets/*.yaml')
    for restore in restore_files:
        if (
            process.no_config and
            'anaconda-enterprise-anaconda-platform.yml' in restore
        ):
            log.info('Skipping platform config due to passed in option')
            continue

        try:
            restore_resource(restore)
        except sh.ErrorReturnCode_1:
            log.info(f'Failed to replace {restore}')
            try:
                restore_resource(restore, action='create')
            except sh.ErrorReturnCode_1:
                log.info(f'Failed to create {restore}')
                log.error(f'Resource {restore} not restored')


def restoring_ingress(process):
    # Grab all of the yaml files that were backed up and apply them
    # within the restore cluster
    if not process.ingress:
        log.info('Skipping ingress restore')
        return

    ingress_files = glob.glob(f'{process.backup_directory}/ingress/*.yaml')
    for ingress in ingress_files:
        applied = False
        try:
            replace_return = process.kubectl('apply', '-f', ingress)
            if 'configured' in replace_return:
                applied = True
        except sh.ErrorReturnCode_1:
            log.error(
                f'File {ingress} was not able to be applied'
            )

        if applied:
            log.info(f'File {ingress} was successfully applied')


def restore_repo_db(process):
    process.get_postgres_docker_container()

    # Copy backup to the DB directory so the container can see it
    sh.mv(
        f'{process.backup_directory}/{process.repository_db_name}',
        f'{process.postgres_system_backup}/{process.repository_db_name}'
    )

    # Change permissions on the backup
    sh.chown(
        'polkitd:input',
        f'{process.postgres_system_backup}/{process.repository_db_name}'
    )
    restore_command = (
        "su - postgres -c 'pg_restore -U postgres --clean -d "
        f"anaconda_repository {process.postgres_container_backup}/"
        f"{process.repository_db_name}'"
    )
    # Restore the repository DB
    process.run_command_on_container(process.docker_cont_id, restore_command)


def restore_deployments(process):
    """
    This is specific request and is not implemented in the general code
    """
    pass


def handle_arguments():
    description = 'Backup or restore your Anaconda Enterprise install'
    parser = argparse.ArgumentParser(description=description)
    sync_group = parser.add_argument_group(
        'Sync Files',
        'Options for file sync between two AE5 installs'
    )
    restore_group = parser.add_argument_group(
        'Restore Cluster',
        'Restore from backup options'
    )
    sync_group.add_argument(
        '-s',
        '--sync',
        required=False,
        default=False,
        action='store_true',
        help=(
            'Transfer backup files to another server. Uses rsync to do this'
            ' and will need to have SSH access and passwordless entry into the'
            ' restore server. Default value is False'
        )
    )
    sync_group.add_argument(
        '-u',
        '--sync-user',
        required=False,
        default='root',
        help=(
            'User to use when doing the sync. Required only if sync is being'
            ' used to transfer the backup files. Default user is root'
        )
    )
    sync_group.add_argument(
        '-n',
        '--sync-node',
        required=False,
        default=None,
        help=(
            'Node to sync the files to after the backup is complete. '
            'Required only if sync is being used to transfer files.'
        )
    )
    parser.add_argument(
        '-a',
        '--action',
        required=True,
        choices=['backup', 'restore'],
        help='Action to perform on the cluster.'
    )
    parser.add_argument(
        '-d',
        '--directory',
        required=False,
        default='/opt/anaconda_backup',
        help=(
            'Backup/Restore directory to use to save or pull files from. '
            'Default path is /opt/anaconda_backup'
        )
    )
    parser.add_argument(
        '--repos-only',
        required=False,
        default=False,
        action='store_true',
        help=(
            'Sync and backup repositories only. Requires sync options '
            'as arguments'
        )
    )
    parser.add_argument(
        '--archive',
        required=False,
        default=False,
        action='store_true',
        help='Create tar archive file that holds all backed up data'
    )
    restore_group.add_argument(
        '--override',
        required=False,
        default=False,
        action='store_true',
        help=(
            'Override restore checks and if the files are present do the '
            'restore anyway. Default is False'
        )
    )
    restore_group.add_argument(
        '--no-config',
        required=False,
        default=False,
        action='store_true',
        help='Do not restore the config files to the system. Default is False'
    )
    restore_group.add_argument(
        '--ingress',
        required=False,
        default=False,
        action='store_true',
        help=(
            'Restore the ingress configurations from the backup. '
            'Default is False'
        )
    )
    # restore_group.add_argument(
    #     '--start-deployments',
    #     required=False,
    #     default=False,
    #     action='store_true',
    #     help=(
    #         'Not Implemented: Start up deployments that are running on '
    #         'the restore destination'
    #     )
    # )
    restore_group.add_argument(
        '--restore-file',
        required=False,
        help='Specify the tar file to restore.'
    )
    args = parser.parse_args()
    return args


def main():
    arguments = handle_arguments()
    try:
        process = Accord(arguments)
    except exceptions.RestoreSignal:
        log.error(
            'Signal file for restore not found so not performing '
            'restore of AE5'
        )
        sys.exit(1)

    if process.action == 'backup':
        if process.repos_only:
            # Backup the repository database only
            log.info('Backing up repository database')
            backup_repository_db(process)
        else:
            # Backup the full database
            log.info('Backing up postgres database')
            backup_postgres_database(process)

            # Backup gravity
            log.info('Running gravity backup')
            process.gravity_backup_restore('backup')

            # tar up all of the files
            log.info('Packaging all of the files with tar')
            file_backup_restore(process, process.action)

            # Backup the secrets
            log.info('Backing up all secrets')
            backup_secrets_config_maps(process)

            # Backup the ingress definiton
            log.info('Backing up all ingress definitions')
            backup_ingress_definitions(process)

            # Clean all of the secrets
            log.info('Sanitizing yaml files')
            sanitize_secrets_config_maps(process)

        # Drop in signal file to indicate good to restore
        log.info('Adding signal for restore')
        process.add_signal_for_restore()

        if process.archive:
            log.info('Creating tar archive for backup')
            process.create_tar_archive()

        # Sync the files if requested
        if process.sync_files:
            # Sync the anaconda repositories
            log.info('Syncing up repositories to restore cluster')
            sync_repositories(process)
            # Sync the backup files
            log.info('Syncing all backup files to restore cluster')
            sync_files(process)

    elif process.action == 'restore':
        if process.restore_file is not None:
            process.extract_tar_archive()

            # After extract check for the restore signle file
            log.info('Checking for restore signal file')
            if not process.check_for_restore():
                raise exceptions.RestoreSignal(
                    'Restore signal file not found, closing application'
                )

        if process.repos_only:
            # Restore the repository database only
            log.info('Restoring repositories only')
            restore_repo_db(process)
        else:
            # Cleanup any existing deployments or sessions running
            log.info('Cleaning up sessions and deployments')
            cleanup_sessions_deployments(process)

            # Scale the postgres pod down to 0 so we can do some work
            log.info('Scaling down postgres pod for restore')
            scale_postgres_pod(process, 0)

            # Cleanup the existing files and restore the backup
            log.info('Cleanup and setup directories for restore')
            cleanup_and_restore_files(process)

            # Scale the postgres pod up to 1
            log.info('Scaling up postgres pod after restore')
            scale_postgres_pod(process, 1)

            # Restore the postgres database
            log.info('Restoring postgres database')
            restore_postgres_database(process)

            # Cleanup sessions and deployments
            log.info('Cleaning up postgres database')
            cleanup_postgres_database(process)

            # Restore secrets/configmaps for cluster
            log.info('Restoring files')
            restoring_files(process)
            restoring_ingress(process)

            # Restart the pods
            log.info('Restarting all pods')
            restart_pods(process)

            if process.start_deployments:
                # Restore deployments
                log.info('Starting up deployments that should be running')
                restore_deployments(process)

        log.info('Cleaning up restore file')
        process.remove_signal_restore_file()


if __name__ == '__main__':
    main()
