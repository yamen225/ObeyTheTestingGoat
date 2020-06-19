import re
from fabric.api import run, env, local, hosts
from fabric.context_managers import settings, shell_env


@hosts(['superlists-staging.ottg.eu'])
def _get_vagrant_instance_connection_data(fn, *args, **kwargs):
    result = local('cd ~/vag_OTG_stg; vagrant ssh-config',
                   capture=True)
    hostname = re.findall(r'HostName\s+([^\n]+)', result)[0]
    port = re.findall(r'Port\s+([^\n]+)', result)[0]
    env.hosts = ['%s:%s' % (hostname, port)]
    env.user = re.findall(r'User\s+([^\n]+)', result)[0]
    env.key_filename = re.findall(
        r'IdentityFile\s+([^\n]+)', result)[0].lstrip("\"").rstrip("\"")
    return fn(host_string=env.hosts[0])


def _get_manage_dot_py(host):
    return f'~/sites/{host}/virtualenv/bin/python ~/sites/{host}/manage.py'


def reset_database(host):
    manage_dot_py = _get_manage_dot_py(host)
    with _get_vagrant_instance_connection_data(settings):
        run(f'{manage_dot_py} flush --noinput')


def _get_server_env_vars(host):
    env_lines = run(f'cat ~/sites/{host}/.env').splitlines()
    return dict(l.split('=') for l in env_lines if l)


def create_session_on_server(host, email):
    manage_dot_py = _get_manage_dot_py(host)
    with _get_vagrant_instance_connection_data(settings):
        env_vars = _get_server_env_vars(host)
        with shell_env(**env_vars):
            session_key = run(f'{manage_dot_py} create_session {email}')
            return session_key.strip()
