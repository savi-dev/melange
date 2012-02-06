# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import gettext
import os
import subprocess

from setuptools import find_packages
from setuptools.command.sdist import sdist
from setuptools import setup

gettext.install('melange', unicode=1)

from melange.openstack.common.setup import parse_mailmap, str_dict_replace
from melange import version


def run_git_command(cmd):
    output = subprocess.Popen(["/bin/sh", "-c", cmd],
                              stdout=subprocess.PIPE)
    return output.communicate()[0].strip()


if os.path.isdir('.git'):
    branch_nick_cmd = 'git branch | grep -Ei "\* (.*)" | cut -f2 -d" "'
    branch_nick = run_git_command(branch_nick_cmd)
    revid_cmd = "git --no-pager log --max-count=1 | cut -f2 -d' ' | head -1"
    revid = run_git_command(revid_cmd)
    revno_cmd = "git --no-pager log --oneline | wc -l"
    revno = run_git_command(revno_cmd)
    with open("melange/vcsversion.py", 'w') as version_file:
        version_file.write("""
# This file is automatically generated by setup.py, So don't edit it. :)
version_info = {
    'branch_nick': '%s',
    'revision_id': '%s',
    'revno': %s
}
""" % (branch_nick, revid, revno))


class local_sdist(sdist):
    """Customized sdist hook - builds the ChangeLog file from VC first"""
    def run(self):
        if os.path.isdir('.git'):
            git_log_gnu = 'git log --format="%ai %aN %n%n%x09* %s%d%n"'
            changelog = run_git_command(git_log_gnu)
            mailmap = parse_mailmap()
            with open("ChangeLog", "w") as changelog_file:
                changelog_file.write(str_dict_replace(changelog, mailmap))
        sdist.run(self)


cmdclass = {'sdist': local_sdist}


try:
    from sphinx.setup_command import BuildDoc

    class local_BuildDoc(BuildDoc):
        def run(self):
            for builder in ['html', 'man']:
                self.builder = builder
                self.finalize_options()
                BuildDoc.run(self)
    cmdclass['build_sphinx'] = local_BuildDoc

except:
    pass


try:
    from babel.messages import frontend as babel
    cmdclass['compile_catalog'] = babel.compile_catalog
    cmdclass['extract_messages'] = babel.extract_messages
    cmdclass['init_catalog'] = babel.init_catalog
    cmdclass['update_catalog'] = babel.update_catalog
except:
    pass


setup(name='melange',
      version=version.canonical_version_string(),
      description='IPAM mangement service for Openstack',
      author='OpenStack',
      author_email='openstack@lists.launchpad.net',
      url='http://www.openstack.org/',
      cmdclass=cmdclass,
      packages=find_packages(exclude=['bin']),
      include_package_data=True,
      test_suite='nose.collector',
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 2.6',
          'Environment :: No Input/Output (Daemon)',
      ],
      scripts=['bin/melange-server',
               'bin/melange-manage',
               'bin/melange-delete-deallocated-ips',
               ],
      py_modules=[])
