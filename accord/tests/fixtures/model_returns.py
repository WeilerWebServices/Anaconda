
GET_PODS = [
    'NAME                                                              '
    'READY     STATUS    RESTARTS   AGE',
    'anaconda-enterprise-ap-auth-68c4f864f8-x8trs                      '
    '1/1       Running   0          30m',
    'anaconda-enterprise-ap-auth-api-6cb6f9595d-9c774                  '
    '1/1       Running   0          30m',
    'anaconda-enterprise-ap-auth-escrow-7f597cfd7-kf4gs                '
    '1/1       Running   0          30m',
    'anaconda-enterprise-ap-deploy-58458665cf-lhc79                    '
    '1/1       Running   0          30m',
    'anaconda-enterprise-ap-docs-6d6cff47-6j7ld                        '
    '1/1       Running   0          30m',
    'anaconda-enterprise-ap-git-storage-56fcfc56b9-2ml4d               '
    '2/2       Running   0          30m',
    'anaconda-enterprise-ap-object-storage-586f97d7cf-mlzww            '
    '1/1       Running   0          30m',
    'anaconda-enterprise-ap-repository-86d44d6c84-5dtmj                '
    '1/1       Running   0          30m',
    'anaconda-enterprise-ap-storage-84946bc54d-lfxvk                   '
    '1/1       Running   0          30m',
    'anaconda-enterprise-ap-ui-798b4477cc-fk626                        '
    '1/1       Running   0          30m',
    'anaconda-enterprise-ap-workspace-68cf65df9f-97vx7                 '
    '1/1       Running   0          30m',
    'anaconda-enterprise-app-images-h8lkp                              '
    '3/3       Running   0          29m',
    'anaconda-enterprise-nginx-ingress-rc-4vgbc                        '
    '1/1       Running   0          29m',
    'anaconda-enterprise-postgres-58857557d-ctbfs                      '
    '1/1       Running   0          30m'
]


DESCRIBE_POD = [
    'Name:           anaconda-enterprise-postgres-58857557d-ctbfs',
    'Namespace:      default',
    'Containers:',
    '  postgres:',
    '    Container ID:   docker://fd234fad0a538a302ac68d0f260a155950b4'
    'b8c7afca3176fcb25d1d799b045e',
    '    Image:          leader.telekube.local:5000/postgres:9.6',
    '    Port:           5432/TCP',
    '    Host Port:      0/TCP',
    '    Environment:  <none>',
    '    Mounts:',
    '      /var/lib/postgresql/data from storage (rw)',
    '      /var/run/secrets/kubernetes.io/serviceaccount from '
    'anaconda-enterprise-token-wdgqn (ro)'
]


GET_SECRETS = [
    'NAME                                                           '
    'TYPE                                  DATA      AGE',
    'anaconda-credentials-user-creds-anaconda-enterprise-3ggji6dp   '
    'Opaque                                1         4s',
    'anaconda-enterprise-certs                                      '
    'Opaque                                6         50m',
    'anaconda-enterprise-keycloak                                   '
    'Opaque                                1         53m',
    'anaconda-enterprise-platform-token-secret                      '
    'Opaque                                1         50m',
    'anaconda-enterprise-token-svdlm                                '
    'kubernetes.io/service-account-token   3         50m',
    'default-token-ghz4l                                            '
    'kubernetes.io/service-account-token   3         1h'
]


GET_INGRESS = (
    'anaconda-app-ingress-12e9d1c6ac5148a59a27a13e0ab6ff6d\n'
    'anaconda-enterprise-ingress-master\n'
    'anaconda-enterprise-ingress-minion\n'
    'anaconda-enterprise-ingress-minion-intercept-errors\n'
    'anaconda-session-ingress-25a75b1a4d394ddeb865578fdfa2b996\n'
    'anaconda-session-ingress-312d73f825c845fcb12fd62dcf3894e7\n'
    'weave-ingress\n\n'
)
