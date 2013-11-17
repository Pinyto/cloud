from __future__ import division, print_function, unicode_literals

from sniffer.api import file_validator, runnable
import termstyle

# you can customize the pass/fail colors like this
pass_fg_color = termstyle.green
pass_bg_color = termstyle.bg_default
fail_fg_color = termstyle.red
fail_bg_color = termstyle.bg_default


# this gets invoked on every file that gets changed in the directory. Return
# True to invoke any runnable functions, False otherwise.
@file_validator
def py_files(filename):
    ## This is a hack to also catch changes done with Pycharm and Gedit
    ## I have no idea why they don't show up on themselves, but the version
    ## with '~' or '___jb_bak___' prepended shows up, so ....
    filename = filename.strip('~').strip('___jb_bak___')
    return filename.endswith('.py') and \
        not os.path.basename(filename).startswith('.')


@runnable
def execute_manage_test(*args):
    import os
    os.environ['DJANGO_SETTINGS_MODULE'] = 'findeco.settings'
    exit_code = os.system('./manage.py test --attr="!selenium"' + " ".join(args[1:]))
    return exit_code == 0