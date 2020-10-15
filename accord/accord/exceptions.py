class RestoreSignal(Exception):
    pass


class NoPostgresBackup(Exception):
    pass


class MissingSyncNode(Exception):
    pass


class InvalidReplicaCount(Exception):
    pass


class UnableToSync(Exception):
    pass


class ConfigMapNotFound(Exception):
    pass


class SecretNotFound(Exception):
    pass


class NotValidTarfile(Exception):
    pass


class IngressError(Exception):
    pass
