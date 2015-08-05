import sys
import sh
import yaml

from fabric import api as fab

TRAVIS_YAML = 'travis.yml'
WARNING = """
#############################################################
# WARNING: .travis.yml is automatically generated by fabric.
# Please modify travis.yml if you want your changes to stick.
#############################################################
"""


def is_dirty():
    return "" != sh.git.status(porcelain=True).strip()


def generate_yaml(language, channel):
    with open(TRAVIS_YAML, "r") as f:
        travis = yaml.load(f)
    travis['language'] = language
    travis['env']['global'].append('ANACONDA_CHANNEL={}'.format(channel))
    with open('.travis.yml', 'w') as f:
        current = yaml.dump(travis)
        f.write(WARNING + current)


def _release(language, message, channel):
    if is_dirty():
        sys.exit("Repo must be in clean state before deploying. Please commit changes.")
    generate_yaml(language, channel)

    if is_dirty():
        sh.git.add('.travis.yml')
    sh.git.commit(m=message, allow_empty=True)
    sh.git.pull(rebase=True)
    sh.git.push()


@fab.task
def update():
    if is_dirty():
        sys.exit("Repo must be in clean state before deploying. Please commit changes.")
    sh.git.submodule.update(remote=True, rebase=True)
    if is_dirty():
        print "Updated repositories:"
        print sh.git.status(porcelain=True).strip()
        sh.git.add(all=True)
        sh.git.commit(m="Update submodules to origin")
    else:
        sys.exit('Nothing to update.')


@fab.task
def release_all(channel="main"):
    release_osx(channel)
    release_linux(channel)


@fab.task
def release_osx(channel="main"):
    _release('objective-c', "Release OS X", channel)


@fab.task
def release_linux(channel="main"):
    _release('objective-c', "Release OS X", channel)
