from fabric.api import env, sudo, require, lcd, cd, run, local, prompt, put
from fabric.colors import cyan, red
from fabric.decorators import runs_once
import sys, os, base64, tempfile
import time

project_root = os.path.dirname(__file__)
sys.path.append(project_root)

# these settings generally don't need to be changed
env.server_owner = 'crimson'
env.server_group = 'www-data'
env.wsgi_script = 'crimson.wsgi'
env.virtualenv_bin = '/usr/local/bin/virtualenv'
env.gitsource = 'git@github.com:harvard-crimson/hackfest.git'
env.release_subpath = '/hackserver'

# Deployment Environments

def prod():
    # host or hosts for this environment
    env.hosts = ['ec2-75-101-226-205.compute-1.amazonaws.com']
    env.cache_host = 'aws-cache1.thecrimson.com'
    # path on disk
    env.path = '/srv/crimson'
    # path to repo - typically env.path + '/repo'
    env.gitpath = env.path + '/repo'



def _get_remote_hosts(load_balancer_name):
    sys.path.append('.')  # not 100% on why I need this just yet, but working on that next
    # Doing settings like we should is annoying b/c logging
    # from fabric.contrib.django import settings_module
    # settings_module('crimsononline.settings')
    # from django.conf import settings
    from crimsononline import settings
    import boto.ec2.elb
    import boto.ec2
    ec2_conn = boto.ec2.connect_to_region('us-east-1', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    conn = boto.ec2.elb.connect_to_region('us-east-1', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    lbs = conn.get_all_load_balancers(load_balancer_names=[load_balancer_name])
    hosts = []
    for inst in lbs[0].instances:  # only one dev LB
        # have to get the reservation/instance from ec2 not elb
        try:
            reservations = ec2_conn.get_all_instances(instance_ids=[inst.id])
            if len(reservations) > 0:
                instance = reservations[0].instances[0]
                if instance.public_dns_name != '':
                    hosts.append(instance.public_dns_name)  # and now we have the hosts
        except boto.exception.EC2ResponseError:
            pass # this must not be a connected instance
    return hosts

def _attach_to_lb(load_balancer_name=''):
    if not load_balancer_name:
        load_balancer_name = env.load_balancer_name
    sys.path.append('.')  # not 100% on why I need this just yet, but working on that next
    # Doing settings like we should is annoying b/c logging
    # from fabric.contrib.django import settings_module
    # settings_module('crimsononline.settings')
    # from django.conf import settings
    from crimsononline import settings
    import boto.ec2.elb
    conn = boto.ec2.elb.connect_to_region('us-east-1', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    my_id = local('curl http://169.254.169.254/latest/meta-data/instance-id', capture=True)
    conn.register_instances(load_balancer_name, [my_id])


# Commands - you shouldn't need to alter these unless you need to change how the app is deployed


def ec2_spinup():
    """
    Runs from rc.local when an ec2 instance is spun up from our AMI
    We need to do a quick deploy to get the most up-to-date code
    It is a modified deploy scenario that only does a code checkout locally
    """
    env.release = time.strftime('%Y%m%d%H%M%S')
    require('gitpath')
    require('release')
    require('app_path')
    require('server_owner')
    require('release_subpath')
    local('mkdir %(app_path)s/releases/%(release)s' % env)
    with lcd(env.gitpath):
        local('git pull --rebase' % env)
        local('git archive --format=tar HEAD | tar -x -C %(app_path)s/releases/%(release)s' % env)
    local('cp -r %(app_path)s/conf/* %(app_path)s/releases/%(release)s%(release_subpath)s' % env)
    try:
        local('%(app_path)s/venv/bin/python %(app_path)s/venv/bin/pip install --use-mirrors --log=%(app_path)s/log/pip.log -r %(app_path)s/releases/%(release)s/requirements.txt' % env)
    except:
        pass
    try:
        local('%(app_path)s/venv/bin/python %(app_path)s/releases/%(release)s/manage.py compile_pyc --path=%(app_path)s/releases/%(release)s' % env)
    except:
        pass
    # all the "if" stuff in case there *is* no current or prev release
    with cd(''.join([env.path, '/releases'])):
        try:
            local('if [ -e %(app_path)s/releases/previous ]; then rm -rf `readlink %(app_path)s/releases/previous`; fi;' % env)
        except:
            # OK if removing previous doesn't work - might be _init, owned by root
            pass
        local('rm -f %(app_path)s/releases/previous' % env)
        local('if [ -e %(app_path)s/releases/current ]; then mv %(app_path)s/releases/current %(app_path)s/releases/previous; fi;' % env)
        try:
            local('rm -f %(app_path)s/releases/current' % env)
        except:
            # OK if removing current doesn't work - might be _init, owned by root
            pass
        local('ln -s %(release)s %(app_path)s/releases/current' % env)
    _attach_to_lb()


def deploy(branch=None, first_time=False):
    """
    Full deploy: pull code as specified, run migrations, and reload.
    """
    env.release = time.strftime('%Y%m%d%H%M%S')

    if branch is not None:
        git_checkout(branch)
    update_from_git()
    # sudo('%(path)s/venv/bin/supervisorctl stop celeryworker' % env)
    install_site()
    apply_local_config()
    install_requirements()
    # this is an optimization that depends on having django-extensions installed - so don't blow up if there's a problem
    try:
        compile_pyc()
    except:
        pass
        
    deploy_static()
    symlink_current_release()
    sync(first_time=first_time)
    migrate(first_time=first_time)
    reload_app()
    # sudo('%(path)s/venv/bin/supervisorctl start celeryworker' % env)


def setup():
    """
    Setup a fresh virtualenv as well as a few useful directories, install the requirements.
    """
    require('path')
    require('gitpath')
    require('gitsource')
    require('server_owner')
    require('server_group')
    
    with cd(env.path):
        run_or_sudo('if ! [ -e %(path)s/releases ]; then mkdir releases; else rm -r %(path)s/releases/*; fi;' % env)
        run_or_sudo('if ! [ -e %(path)s/conf ]; then mkdir conf; fi;' % env)
        run_or_sudo('if ! [ -e %(path)s/log ]; then mkdir log; fi;' % env)
        run_or_sudo('if ! [ -e %(path)s/log/django.log ]; then touch %(path)s/log/django.log; fi;' % env)
        run_or_sudo('if ! [ -e %(path)s/static ]; then mkdir static; fi;' % env)
        run_or_sudo('if ! [ -e %(path)s/uploads ]; then mkdir uploads; fi;' % env)
        run_or_sudo('if ! [ -e %(path)s/uploads/photos ]; then mkdir uploads/photos; fi;' % env)
        run_or_sudo('if ! [ -e %(path)s/uploads/thumbnails ]; then mkdir uploads/thumbnails; fi;' % env)
        run_or_sudo('if ! [ -e %(path)s/apache ] && ! [ -L %(path)s/apache ]; then ln -s %(path)s/releases/current/wsgi %(path)s/apache; fi;' % env)
    
    # first checkout of repo
    setup_git_repo()
    
    # install virtualenv
    setup_virtualenv()
    
    # create EGG_CACHE, set permissions
    run_or_sudo('if ! [ -e %(path)s/EGG_CACHE ]; then mkdir %(path)s/EGG_CACHE; fi;' % env)
    run_or_sudo('chmod -R 775 %(path)s/EGG_CACHE' % env)

    sudo('chown -R vagrant:www-data %(path)s' % env)
    
    # install requirements into virtualenv
    # (can't install requirements until we have a release)
    import time
    env.release = time.strftime('%Y%m%d%H%M%S')
    update_from_git()
    install_site()
    apply_local_config()
    install_requirements()

    deploy(first_time=True)
    restart_webserver()


def setup_git_repo():
    "First checkout of repo - check if it exists first (so that the method is idempotent)"
    require('gitpath')
    require('gitsource')

    if env.gitpath and env.gitsource:
        run_or_sudo('if ! [ -e %(gitpath)s ]; then mkdir %(gitpath)s; fi;' % env)
        with cd(env.gitpath):
            run_or_sudo('if ! [ -e %(gitpath)s/.git ]; then git clone %(gitsource)s .; fi;' % env)

def setup_virtualenv():
    with cd(env.path):
        run_or_sudo('if ! [ -e %(path)s/venv ]; then mkdir venv; fi;' % env)
        run_or_sudo('if ! [ -e %(path)s/venv/bin/python ]; then %(virtualenv_bin)s %(path)s/venv; fi;' % env)


def update_from_git():
    require('gitpath')

    if env.gitpath:
        with cd(env.gitpath):
            run_or_sudo('git pull --rebase' % env)
    else:
        sudo('ln -s /vagrant %(path)s/releases/%(release)s' % env, user=env.server_owner)


def git_checkout(branch):
    require('gitpath')
    with cd(env.gitpath):
        try:
            run_or_sudo('/usr/bin/git pull --rebase')
        except: # the branch was deleted from origin
            run_or_sudo('/usr/bin/git checkout master')
            run_or_sudo('/usr/bin/git pull --rebase')

        run_or_sudo('/usr/bin/git checkout %(branch)s' % {'branch': branch})


def apply_local_config():
    """
    Copies server-local configuration files to deployed app.
    """
    require('path')
    require('release_subpath')
    run_or_sudo('cp -r %(path)s/conf/* %(path)s/releases/%(release)s%(release_subpath)s' % env, warn_only=True)


def compile_pyc():
    "Pre-compile the .py files for a faster startup"
    require('path')
    require('release')
    require('server_owner')
    run_or_sudo('%(path)s/venv/bin/python %(path)s/releases/%(release)s/manage.py compile_pyc --path=%(path)s/releases/%(release)s' % env)


def install_requirements(current=False):
    "Install the required packages from the requirements file using pip"
    require('path')
    if current:
        env.release = 'current'
    else:
        require('release')
    require('server_owner')
    require('release_subpath')
    run_or_sudo('%(path)s/venv/bin/python %(path)s/venv/bin/pip install --use-mirrors --log=%(path)s/log/pip.log -r %(path)s/releases/%(release)s/requirements.txt' % env)


def install_site():
    require('release')
    require('gitpath')
    require('path')
    require('server_owner')
    
    if env.gitpath:
        run_or_sudo('mkdir %(path)s/releases/%(release)s' % env)
        
        # TODO: HEAD or tag (argument?)
        with cd(env.gitpath):
            run_or_sudo('git archive --format=tar HEAD | tar -x -C %(path)s/releases/%(release)s' % env)

def manage(cmd=""):
    """Run a management command in the app directory."""
    require('path')
    if not cmd:
        sys.stdout.write(cyan("Command to run: "))
        cmd = raw_input().strip()
        
    if cmd:
        cmd_args = dict(env)
        cmd_args.update({'cmd': cmd})
        run_or_sudo('%(path)s/venv/bin/python %(path)s/releases/current/manage.py %(cmd)s' % cmd_args)


def loaddata(fixture):
    """Usage: fab [devl|test|prod] loaddata:fixture=[fixture]"""
    require('path')
    require('server_owner')
    run_or_sudo('%(path)s/venv/bin/python %(path)s/releases/current/manage.py loaddata %(fixture)s' % env)


def symlink_current_release():
    "Symlink our current release"
    require('path')
    require('release')
    require('server_owner')
    # all the "if" stuff in case there *is* no current or prev release
    with cd(''.join([env.path, '/releases'])):
        try:
            run_or_sudo('if [ -e %(path)s/releases/previous ]; then rm -rf `readlink %(path)s/releases/previous`; fi;' % env)
        except:
            # OK if removing previous doesn't work - might be _init, owned by root
            pass
        run_or_sudo('rm -f %(path)s/releases/previous' % env)
        run_or_sudo('if [ -e %(path)s/releases/current ]; then mv %(path)s/releases/current %(path)s/releases/previous; fi;' % env)
        try:
            run_or_sudo('rm -f %(path)s/releases/current' % env)
        except:
            # OK if removing current doesn't work - might be _init, owned by root
            pass
        run_or_sudo('ln -s %(release)s %(path)s/releases/current' % env)


def migrate(first_time=False):
    "Update the database"
    require('path')
    if first_time:
        try:
            run_or_sudo('%(path)s/venv/bin/python %(path)s/releases/%(release)s/manage.py migrate --fake' % env)
        except KeyError:
            run_or_sudo('%(path)s/venv/bin/python %(path)s/releases/current/manage.py migrate --fake' % env)
    else:
        try:
            run_or_sudo('%(path)s/venv/bin/python %(path)s/releases/%(release)s/manage.py migrate' % env)
        except KeyError:
            run_or_sudo('%(path)s/venv/bin/python %(path)s/releases/current/manage.py migrate' % env)


def sync(first_time=False):
    "Sync the database"
    require('path')
    require('server_owner')
    if first_time:
        try:
            run_or_sudo('%(path)s/venv/bin/python %(path)s/releases/%(release)s/manage.py syncdb --all' % env)
        except KeyError:
            run_or_sudo('%(path)s/venv/bin/python %(path)s/releases/current/manage.py syncdb --all' % env)
    else:
        try:
            run_or_sudo('%(path)s/venv/bin/python %(path)s/releases/%(release)s/manage.py syncdb' % env)
        except KeyError:
            run_or_sudo('%(path)s/venv/bin/python %(path)s/releases/current/manage.py syncdb' % env)


def create_superuser():
    "Calls the django_extensions create_superuser command"
    require('path')
    run_or_sudo('%(path)s/venv/bin/python %(path)s/releases/current/manage.py createsuperuser' % env)


@runs_once
def deploy_static():
    require('path')
    try:
        run_or_sudo('%(path)s/venv/bin/python %(path)s/releases/%(release)s/manage.py collectstatic --noinput' % env)
    except KeyError:
        run_or_sudo('%(path)s/venv/bin/python %(path)s/releases/current/manage.py collectstatic --noinput' % env)

    if env.get('compress_offline', True):
        try:
            run_or_sudo('%(path)s/venv/bin/python %(path)s/releases/%(release)s/manage.py compress' % env)
        except KeyError:
            run_or_sudo('%(path)s/venv/bin/python %(path)s/releases/current/manage.py compress' % env)


def clear_cache():
    require('cache_host')
    run_or_sudo('echo -e "flush_all\nquit" | nc %(cache_host)s 11211' % env)


def restart_webserver():
    "Restart the web server"
    sudo('/usr/sbin/apache2ctl graceful') 


def reload_app():
    """Reload application code without restarting the web server"""
    require('path')
    require('wsgi_script')
    require('server_owner')
    run_or_sudo('touch %(path)s/apache/%(wsgi_script)s' % env)


def run_or_sudo(cmd, *args, **kwargs):
    """run or sudo the specified command depending on who's running the script"""
    if env.user == env.server_owner:
        run(cmd % env, *args, **kwargs)
    else:
        sudo(cmd, user=env.server_owner, *args, **kwargs)


def random_string(length):
    # Make sure we only return safe characters
    return base64.b64encode(os.urandom(length)).replace('=', 'x').replace('/', 'y').replace('+', '-')[:length]


def get_database():
    """ Pull down a new database """
    sudo('wget -O /tmp/crimson-prod.sql.gz --http-user=crimson --http-password=Plympton http://dbdump.thecrimson.com/nightly.sql.gz && gunzip /tmp/crimson-prod.sql.gz')


def update_database(fetch=True):
    """ Drop current database and pull down a new one """
    if env.server_owner == 'vagrant':
        if fetch:
            get_database()
        sudo('echo "DROP DATABASE crimson;CREATE DATABASE crimson;" | mysql -uroot')
        sudo('mysql -uroot crimson < /tmp/crimson-prod.sql')
