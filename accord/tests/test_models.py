
from .fixtures import model_returns
from unittest import TestCase


from accord import exceptions
from accord import models


import subprocess
import logging
import tarfile
import shutil
import mock
import glob
import os


class TestModels(TestCase):
    def setUp(self):
        logging.disable(logging.ERROR)

    def tearDown(self):
        logging.disable(logging.NOTSET)
        temp_files = [
            'restore',
            'accord.log',
            'test.tar.gz',
            'test.txt',
            'ae5_backup_TEST.tar.gz',
            'repos_db_backup_TEST.tar.gz'
        ]
        for tf in temp_files:
            if os.path.isfile(tf):
                os.remove(tf)

        if os.path.exists('anaconda_backup'):
            os.rmdir('anaconda_backup')

        try:
            shutil.rmtree('testing_tar')
        except Exception:
            pass

    def setup_args_backup_default(self, repos_only=False, sync=False,
                                  sync_node=None, sync_user='root',
                                  start_deployments=False,
                                  directory='/opt/anaconda_backup',
                                  archive=False, ingress=False):
        class MockArgs(object):
            def __init__(self):
                self.action = 'backup'
                self.directory = directory
                self.no_config = False
                self.override = False
                self.repos_only = repos_only
                self.archive = archive
                self.start_deployments = start_deployments
                self.sync = sync
                self.sync_node = sync_node
                self.sync_user = sync_user
                self.ingress = ingress

        return MockArgs()

    def setup_args_restore_default(self, override=False, repos_only=False,
                                   no_config=False, start_deployments=False,
                                   directory='/opt/anaconda_backup',
                                   restore_file=None, ingress=False):
        class MockArgs(object):
            def __init__(self):
                self.action = 'restore'
                self.directory = directory
                self.no_config = no_config
                self.override = override
                self.repos_only = repos_only
                self.restore_file = restore_file
                self.start_deployments = start_deployments
                self.ingress = ingress

        return MockArgs()

    def setup_temp_restore_file(self, temp_path):
        open(temp_path, 'a').close()

    def setup_valid_tar_archive(self):
        try:
            os.mkdir('testing_tar')
        except Exception:
            pass

        self.setup_temp_restore_file('testing_tar/test.txt')
        with tarfile.open('test.tar.gz', 'w:gz') as tar:
            tar.add(
                'testing_tar',
                arcname=os.path.basename('testing_tar')
            )

        shutil.move('test.tar.gz', 'testing_tar/test.tar.gz')

    def setup_testing_dir(self):
        try:
            os.mkdir('testing_tar')
        except Exception:
            pass

        self.setup_temp_restore_file('testing_tar/test.txt')
        with tarfile.open('ae5_backup_TEST.tar.gz', 'w:gz') as tar:
            tar.add(
                'testing_tar',
                arcname=os.path.basename('testing_tar')
            )
        shutil.move(
            'ae5_backup_TEST.tar.gz',
            'testing_tar/ae5_backup_TEST.tar.gz'
        )

        with tarfile.open('repos_db_backup_TEST.tar.gz', 'w:gz') as tar:
            tar.add(
                'testing_tar',
                arcname=os.path.basename('testing_tar')
            )
        shutil.move(
            'repos_db_backup_TEST.tar.gz',
            'testing_tar/repos_db_backup_TEST.tar.gz'
        )

    @mock.patch('sh.Command')
    def test_init_class_backup_default(self, Command):
        expected_secrets = {
            'kube-system': ['cluster-tls'],
            'default': ['anaconda-enterprise-certs', 'anaconda-config-files']
        }
        expected_cms = {
            'default': ['anaconda-enterprise-anaconda-platform.yml']
        }

        with mock.patch('accord.models.Accord.setup_backup_directory'):
            with mock.patch('accord.models.Accord.remove_signal_restore_file'):
                test = models.Accord(self.setup_args_backup_default())

        self.assertEqual(test.backup_directory, '/opt/anaconda_backup')
        self.assertEqual(test.action, 'backup')
        self.assertEqual(
            test.var_lib_gravity_backup_name,
            'var_lib_gravity_backup.tar.gz'
        )
        self.assertEqual(test.postgres_backup_name, 'full_postgres_backup.sql')
        self.assertEqual(test.storage_backup_name, 'storage_backup.tar.gz')
        self.assertEqual(test.repository_db_name, 'all_repositories.tar')
        self.assertEqual(
            test.postgres_container_backup,
            '/var/lib/postgresql/data'
        )
        self.assertEqual(
            test.postgres_system_backup,
            '/opt/anaconda/storage/pgdata'
        )
        self.assertEqual(
            test.postgres_system_backup_path,
            '/opt/anaconda/storage/pgdata/full_postgres_backup.sql'
        )
        self.assertEqual(
            test.postgres_container_backup_path,
            '/var/lib/postgresql/data/full_postgres_backup.sql'
        )
        self.assertEqual(
            test.repository,
            '/opt/anaconda/storage/object/anaconda-repository'
        )
        self.assertEqual(test.signal_file, '/opt/anaconda_backup/restore')
        self.assertEqual(test.sync_files, False)
        self.assertEqual(test.start_deployments, False)
        self.assertEqual(test.no_config, False)
        self.assertEqual(test.repos_only, False)
        self.assertEqual(test.namespace, 'default')
        self.assertEqual(test.secret_files, expected_secrets)
        self.assertEqual(test.config_maps, expected_cms)

    @mock.patch('sh.Command')
    def test_init_class_restore_defaults(self, Command):
        with mock.patch('accord.models.Accord.check_for_restore'):
            test = models.Accord(self.setup_args_restore_default())

        self.assertEqual(test.action, 'restore')

    def test_init_class_restore_exception_file(self):
        with mock.patch('accord.models.Accord.check_for_restore') as restore:
            restore.return_value = False
            try:
                models.Accord(self.setup_args_restore_default())
            except exceptions.RestoreSignal:
                pass
            except Exception:
                assert False, 'Did not catch the proper exception'

    @mock.patch('sh.Command')
    def test_init_class_restore_force(self, Command):
        test = models.Accord(
            self.setup_args_restore_default(override=True)
        )

        self.assertEqual(test.override, True)
        self.assertEqual(test.action, 'restore')

    @mock.patch('sh.Command')
    def test_init_class_backup_sync_user(self, Command):
        with mock.patch('accord.models.Accord.setup_backup_directory'):
            with mock.patch('accord.models.Accord.remove_signal_restore_file'):
                with mock.patch('accord.models.Accord.test_sync_to_backup'):
                    test = models.Accord(
                        self.setup_args_backup_default(
                            sync=True,
                            sync_user='billdo',
                            sync_node='1.2.3.4'
                        )
                    )

        self.assertEqual(test.sync_files, True)
        self.assertEqual(test.sync_user, 'billdo')
        self.assertEqual(test.sync_node, '1.2.3.4')

    def test_init_class_backup_sync_no_node(self):
        with mock.patch('accord.models.Accord.setup_backup_directory'):
            with mock.patch('accord.models.Accord.remove_signal_restore_file'):
                try:
                    models.Accord(
                        self.setup_args_backup_default(
                            sync=True,
                            sync_user='billdo'
                        )
                    )
                except exceptions.MissingSyncNode:
                    pass
                except Exception:
                    assert False, 'Did not catch expected exception'

    @mock.patch('sh.Command')
    def test_init_class_restore_file_check(self, Command):
        self.setup_temp_restore_file('restore')
        test_args = self.setup_args_restore_default(override=True)
        test_class = models.Accord(test_args)

        # Change path of file
        test_class.signal_file = 'restore'
        check_return = test_class.check_for_restore()

        self.assertEqual(check_return, True)

    @mock.patch('sh.Command')
    def test_add_restore_file(self, Command):
        with mock.patch('accord.models.Accord.setup_backup_directory'):
            with mock.patch('accord.models.Accord.remove_signal_restore_file'):
                test_class = models.Accord(self.setup_args_backup_default())

        test_class.signal_file = 'restore'
        test_class.add_signal_for_restore()

        if os.path.isfile('restore'):
            pass
        else:
            assert False, 'Did not find restore file'

    @mock.patch('sh.Command')
    def test_cleanup_restore_file(self, Command):
        self.setup_temp_restore_file('restore')
        with mock.patch('accord.models.Accord.setup_backup_directory'):
            with mock.patch('accord.models.Accord.remove_signal_restore_file'):
                test_class = models.Accord(self.setup_args_backup_default())

        test_class.signal_file = 'restore'
        test_class.remove_signal_restore_file()

        if os.path.isfile('restore'):
            assert False, 'restore file was not cleaned up'

    def test_check_for_ssh_sudo_access_exception(self):
        raise_exception = mock.Mock()
        raise_exception.side_effect = subprocess.CalledProcessError
        with mock.patch('accord.models.Accord.setup_backup_directory'):
            with mock.patch('accord.models.Accord.remove_signal_restore_file'):
                with mock.patch(
                    'accord.models.Accord.run_su_command',
                    side_effect=raise_exception
                ):
                    try:
                        models.Accord(
                            self.setup_args_backup_default(
                                sync=True,
                                sync_user='Billdo',
                                sync_node='1.2.3.4'
                            )
                        )
                        assert False, 'Exception was not raised'
                    except exceptions.UnableToSync:
                        pass
                    except Exception:
                        assert False, 'Did not catch proper exception'

    @mock.patch('sh.Command')
    def test_setup_backup_directory(self, Command):
        with mock.patch('accord.models.Accord.setup_backup_directory'):
            with mock.patch('accord.models.Accord.remove_signal_restore_file'):
                test_class = models.Accord(self.setup_args_backup_default())

        test_class.backup_directory = 'anaconda_backup'
        test_class.setup_backup_directory()

        if not os.path.exists('anaconda_backup'):
            assert False, 'Backup directory was not created'

    @mock.patch('sh.Command')
    def test_setup_backup_directory_restore(self, Command):
        with mock.patch('accord.models.Accord.setup_backup_directory'):
            with mock.patch('accord.models.Accord.remove_signal_restore_file'):
                with mock.patch('accord.models.Accord.run_su_command'):
                    test_class = models.Accord(
                        self.setup_args_backup_default(
                            sync=True,
                            sync_user='Billdo',
                            sync_node='1.2.3.4'
                        )
                    )

        test_class.backup_directory = 'anaconda_backup'
        with mock.patch('accord.models.Accord.run_su_command'):
            test_class.setup_backup_directory()

        if not os.path.exists('anaconda_backup'):
            assert False, 'Backup directory was not created'

    @mock.patch('sh.Command')
    def test_grabbing_postgres_docker_container(self, Command):
        mock_response = mock.Mock()
        mock_response.side_effect = [
            model_returns.GET_PODS,
            model_returns.DESCRIBE_POD
        ]
        with mock.patch('accord.models.Accord.setup_backup_directory'):
            with mock.patch('accord.models.Accord.remove_signal_restore_file'):
                test_class = models.Accord(self.setup_args_backup_default())

        Command().side_effect = mock_response
        test_class.get_postgres_docker_container()

        self.assertEqual(
            test_class.postgres_pod,
            'anaconda-enterprise-postgres-58857557d-ctbfs',
            'Did not get expected return value'
        )
        self.assertEqual(
            test_class.docker_cont_id,
            'fd234fad0a538a302ac68d0f260a155950b4b8c7afca3176fcb25d1d799b045e',
            'Did not get expected return value'
        )

    @mock.patch('sh.Command')
    def test_gravity_backup(self, Command):
        with mock.patch('accord.models.Accord.setup_backup_directory'):
            with mock.patch('accord.models.Accord.remove_signal_restore_file'):
                test_class = models.Accord(self.setup_args_backup_default())

        try:
            test_class.gravity_backup_restore('backup')
        except Exception:
            assert False, "Exception occurred"

    @mock.patch('sh.Command')
    def test_gravity_restore(self, Command):
        test_class = models.Accord(
            self.setup_args_restore_default(override=True)
        )

        try:
            test_class.gravity_backup_restore('restore')
        except Exception:
            assert False, "Exception occurred"

    @mock.patch('sh.Command')
    def test_gather_secrets(self, Command):
        expected_output = {
            'kube-system': ['cluster-tls'],
            'default': [
                'anaconda-enterprise-certs',
                'anaconda-config-files',
            ],
            'test_namespace': [
                'anaconda-credentials-user-creds-anaconda-enterprise-3ggji6dp'
            ]
        }
        with mock.patch('accord.models.Accord.setup_backup_directory'):
            with mock.patch('accord.models.Accord.remove_signal_restore_file'):
                test_class = models.Accord(self.setup_args_backup_default())

        Command().return_value = model_returns.GET_SECRETS
        test_class.namespace = 'test_namespace'
        test_class.get_all_secrets()

        self.assertEqual(
            test_class.secret_files,
            expected_output,
            'Returned value is not expected value'
        )

    @mock.patch('sh.Command')
    def test_container_command_exception(self, Command):
        test_class = models.Accord(
            self.setup_args_restore_default(override=True)
        )
        container = 'test_container'
        command = 'ls'
        mock_response = mock.Mock()
        mock_response.side_effect = subprocess.CalledProcessError(1, 'ls')
        with mock.patch(
            'accord.models.subprocess.run',
            side_effect=mock_response
        ):
            with mock.patch('accord.models.sys.exit'):
                test_class.run_command_on_container(container, command)

    @mock.patch('sh.Command')
    def test_container_command_success_return(self, Command):
        test_class = models.Accord(
            self.setup_args_restore_default(override=True)
        )
        container = 'test_container'
        command = 'ls'
        try:
            with mock.patch('accord.models.subprocess.run') as r:
                r.return_value.stdout = 'Success'
                results = test_class.run_command_on_container(
                    container,
                    command,
                    True
                )
        except Exception:
            assert False, "Exception occurred"

        self.assertEqual(results, 'Success', 'Did not receive expected value')

    @mock.patch('sh.Command')
    def test_container_command_success_no_return(self, Command):
        test_class = models.Accord(
            self.setup_args_restore_default(override=True)
        )
        container = 'test_container'
        command = 'ls'
        try:
            with mock.patch('accord.models.subprocess.run'):
                test_class.run_command_on_container(
                    container,
                    command,
                    False
                )
        except Exception:
            assert False, "Exception occurred"

    @mock.patch('sh.Command')
    def test_su_command_exception(self, Command):
        test_class = models.Accord(
            self.setup_args_restore_default(override=True)
        )
        container = 'test_container'
        command = 'ls'
        mock_response = mock.Mock()
        mock_response.side_effect = subprocess.CalledProcessError(1, 'ls')
        with mock.patch(
            'accord.models.subprocess.run',
            side_effect=mock_response
        ):
            with mock.patch('accord.models.sys.exit'):
                test_class.run_su_command(container, command)

    @mock.patch('sh.Command')
    def test_su_command_success(self, Command):
        test_class = models.Accord(
            self.setup_args_restore_default(override=True)
        )
        container = 'test_container'
        command = 'ls'
        try:
            with mock.patch('accord.models.subprocess.run'):
                test_class.run_su_command(container, command)
        except Exception:
            assert False, "Exception occurred"

    @mock.patch('sh.Command')
    def test_authenticate_api(self, Command):
        test_class = models.Accord(
            self.setup_args_restore_default(override=True)
        )

        try:
            test_class.authenticate_api()
        except Exception:
            assert False, "Exception occurred"

    @mock.patch('sh.Command')
    def test_launch_deployment(self, Command):
        test_class = models.Accord(
            self.setup_args_restore_default(override=True)
        )

        try:
            test_class.launch_deployment()
        except Exception:
            assert False, "Exception occurred"

    @mock.patch('sh.Command')
    def test_create_tar_archive_repos(self, Command):
        self.setup_testing_dir()
        with mock.patch('accord.models.Accord.setup_backup_directory'):
            with mock.patch('accord.models.Accord.remove_signal_restore_file'):
                test_class = models.Accord(self.setup_args_backup_default())

        test_class.backup_directory = 'testing_tar'
        test_class.repos_only = True
        test_class.create_tar_archive()

        temp_archive = glob.glob('testing_tar/*.tar.gz')
        self.assertEqual(len(temp_archive), 3, 'Did not find tar archive')
        found_new_repo = False
        for repo in temp_archive:
            if 'testing_tar/repos_db_backup_20' in repo:
                found_new_repo = True

        assert found_new_repo, 'Name of archive not repos'
        use_archive = None
        for repo in temp_archive:
            if (
                'ae5_backup_TEST.tar.gz' not in repo and
                'repos_db_backup_TEST.tar.gz' not in repo
            ):
                use_archive = repo

        with tarfile.open(use_archive) as tar:
            success = False
            for f in tar.getmembers():
                if 'test.txt' in f.name:
                    success = True

                if 'ae5_backup_TEST.tar.gz' in f.name:
                    assert False, (
                        'File added to tar file that should not have been'
                    )

                if 'repos_db_backup_TEST.tar.gz' in f.name:
                    assert False, (
                        'File added to tar file that should not have been'
                    )

            assert success, 'File not found in archive'

    @mock.patch('sh.Command')
    def test_create_tar_archive_full(self, Command):
        self.setup_testing_dir()
        with mock.patch('accord.models.Accord.setup_backup_directory'):
            with mock.patch('accord.models.Accord.remove_signal_restore_file'):
                test_class = models.Accord(self.setup_args_backup_default())

        test_class.backup_directory = 'testing_tar'
        test_class.create_tar_archive()

        temp_archive = glob.glob('testing_tar/*.tar.gz')
        self.assertEqual(len(temp_archive), 3, 'Did not find tar archive')
        found_archive = False
        for archive in temp_archive:
            if 'ae5_backup_' in archive:
                found_archive = True

        assert found_archive, 'Could not find valid archive after create'
        use_archive = None
        for repo in temp_archive:
            if (
                'ae5_backup_TEST.tar.gz' not in repo and
                'repos_db_backup_TEST.tar.gz' not in repo
            ):
                use_archive = repo

        with tarfile.open(use_archive) as tar:
            success = False
            for f in tar.getmembers():
                if 'test.txt' in f.name:
                    success = True

                if 'ae5_backup_TEST.tar.gz' in f.name:
                    assert False, (
                        'File added to tar file that should not have been'
                    )

                if 'repos_db_backup_TEST.tar.gz' in f.name:
                    assert False, (
                        'File added to tar file that should not have been'
                    )

            assert success, 'File not found in archive'

    @mock.patch('sh.Command')
    def test_create_tar_archive_failure(self, Command):
        self.setup_testing_dir()
        with mock.patch('accord.models.Accord.setup_backup_directory'):
            with mock.patch('accord.models.Accord.remove_signal_restore_file'):
                test_class = models.Accord(self.setup_args_backup_default())

        test_class.backup_directory = 'testing_tar'
        self.setup_temp_restore_file('testing_tar/test.tar.gz')
        with mock.patch('accord.models.tarfile.is_tarfile') as tar:
            tar.return_value = False
            try:
                test_class.create_tar_archive()
            except exceptions.NotValidTarfile:
                pass
            except Exception:
                assert False, 'Incorrect exception was thrown'

    @mock.patch('sh.Command')
    def test_extract_tar_archive_success(self, Command):
        self.setup_valid_tar_archive()
        os.remove('testing_tar/test.txt')
        test_class = models.Accord(
            self.setup_args_restore_default(
                override=True,
                restore_file='testing_tar/test.tar.gz',
                directory='testing_tar'
            )
        )
        test_class.extract_tar_archive('.')
        if os.path.isfile('testing_tar/test.txt'):
            pass
        else:
            assert False, 'Did not extract the archive as expected'

    @mock.patch('sh.Command')
    def test_extract_tar_archive_failure(self, Command):
        self.setup_temp_restore_file('test.tar.gz')
        test_class = models.Accord(
            self.setup_args_restore_default(
                override=True,
                restore_file='test.tar.gz',
                directory='.'
            )
        )
        try:
            test_class.extract_tar_archive('.')
            assert False, 'Exception should have occured'
        except exceptions.NotValidTarfile:
            pass
        except Exception:
            assert False, 'Exception was not caught'

    @mock.patch('sh.awk')
    @mock.patch('sh.grep')
    @mock.patch('sh.Command')
    def test_get_all_ingress(self, awk, grep, Command):
        expected_return = [
            'anaconda-enterprise-ingress-master',
            'anaconda-enterprise-ingress-minion',
            'anaconda-enterprise-ingress-minion-intercept-errors',
            'weave-ingress'
        ]
        with mock.patch('accord.models.Accord.setup_backup_directory'):
            with mock.patch('accord.models.Accord.remove_signal_restore_file'):
                test_class = models.Accord(self.setup_args_backup_default())

        Command.return_value = model_returns.GET_INGRESS
        ingress_list = test_class.get_all_ingress()

        self.assertEqual(len(ingress_list), 4, 'Incorrect length of ingress')
        self.assertEqual(
            ingress_list,
            expected_return,
            'Ingress was list was not expected value'
        )
