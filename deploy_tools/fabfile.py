import random
import re
import os
from fabric.contrib.files import append, exists
from fabric.api import cd, env, local, run, hosts

REPO_URL = 'https://github.com/yamen225/ObeyTheTestingGoat'


def _get_vagrant_instance_connection_data(fn, *args, **kwargs):
    local('cd ~/vag_OTG_stg; vagrant up')
    result = local('cd ~/vag_OTG_stg; vagrant ssh-config',
                   capture=True)
    hostname = re.findall(r'HostName\s+([^\n]+)', result)[0]
    port = re.findall(r'Port\s+([^\n]+)', result)[0]
    env.hosts = ['%s:%s' % (hostname, port)]
    env.user = re.findall(r'User\s+([^\n]+)', result)[0]
    env.key_filename = re.findall(
        r'IdentityFile\s+([^\n]+)', result)[0].lstrip("\"").rstrip("\"")
    fn()


@hosts(['superlists-staging.ottg.eu'])
def get_vagrant_staging_connection():
    local('cd ~/vag_OTG_stg; vagrant up')
    result = local('cd ~/vag_OTG_stg; vagrant ssh-config',
                   capture=True)
    hostname = re.findall(r'HostName\s+([^\n]+)', result)[0]
    port = re.findall(r'Port\s+([^\n]+)', result)[0]
    env.hosts = ['%s:%s' % (hostname, port)]
    env.user = re.findall(r'User\s+([^\n]+)', result)[0]
    env.key_filename = re.findall(
        r'IdentityFile\s+([^\n]+)', result)[0].lstrip("\"").rstrip("\"")
    deploy()
    # _restart_stg_services()


@hosts(['superlists.ottg.eu'])
def get_vagrant_production_connection():
    local('cd ~/vag_OTG_stg; vagrant up')
    result = local('cd ~/vag_OTG_stg; vagrant ssh-config',
                   capture=True)
    hostname = re.findall(r'HostName\s+([^\n]+)', result)[0]
    port = re.findall(r'Port\s+([^\n]+)', result)[0]
    env.hosts = ['%s:%s' % (hostname, port)]
    env.user = re.findall(r'User\s+([^\n]+)', result)[0]
    env.key_filename = re.findall(
        r'IdentityFile\s+([^\n]+)', result)[0].lstrip("\"").rstrip("\"")
    deploy()
    # _restart_prod_services()


def deploy():
    site_folder = f'/home/{env.user}/sites/{env.host}'
    run(f'mkdir -p {site_folder}')
    with cd(site_folder):
        _get_latest_source()
        _update_virtualenv()
        _create_or_update_dotenv()
        _update_static_files()
        _update_database()


def _get_latest_source():
    if exists('.git'):
        run('git fetch')
    else:
        run(f'git clone {REPO_URL} .')
    current_commit = local("git log -n 1 --format=%H", capture=True)
    run(f'git reset --hard {current_commit}')


def _update_virtualenv():
    if not exists('virtualenv/bin/pip'):
        run(f'python3.6 -m venv virtualenv')
    run('./virtualenv/bin/pip install -r requirements.txt')


def _create_or_update_dotenv():
    append('.env', 'DJANGO_DEBUG_FALSE=y')
    append('.env', f'SITENAME={env.host}')
    current_contents = run('cat .env')
    if 'DJANGO_SECRET_KEY' not in current_contents:
        new_secret = ''.join(random.SystemRandom().choices(
            'abcdefghijklmnopqrstuvwxyz0123456789', k=50
        ))
        append('.env', f'DJANGO_SECRET_KEY={new_secret}')
    email_password = os.environ['EMAIL_PASSWORD']
    append('.env', f'EMAIL_PASSWORD={email_password}')

def _update_static_files():
    run('./virtualenv/bin/python manage.py collectstatic --noinput')


def _update_database():
    run('./virtualenv/bin/python manage.py migrate --noinput')
