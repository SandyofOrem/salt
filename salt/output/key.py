# -*- coding: utf-8 -*-
'''
Display salt-key output
=======================

The ``salt-key`` command makes use of this outputter to format its output.
'''
from __future__ import absolute_import, unicode_literals

# Import salt libs
import salt.output
from salt.utils.locales import sdecode
import salt.utils.color


def output(data, **kwargs):  # pylint: disable=unused-argument
    '''
    Read in the dict structure generated by the salt key API methods and
    print the structure.
    '''
    color = salt.utils.color.get_colors(
            __opts__.get('color'),
            __opts__.get('color_theme'))
    strip_colors = __opts__.get('strip_colors', True)
    ident = 0
    if __opts__.get('__multi_key'):
        ident = 4
    if __opts__['transport'] in ('zeromq', 'tcp'):
        acc = 'minions'
        pend = 'minions_pre'
        den = 'minions_denied'
        rej = 'minions_rejected'

        cmap = {pend: color['RED'],
                acc: color['GREEN'],
                den: color['MAGENTA'],
                rej: color['BLUE'],
                'local': color['MAGENTA']}

        trans = {pend: u'{0}{1}Unaccepted Keys:{2}'.format(
                                    ' ' * ident,
                                    color['LIGHT_RED'],
                                    color['ENDC']),
                 acc: u'{0}{1}Accepted Keys:{2}'.format(
                                    ' ' * ident,
                                    color['LIGHT_GREEN'],
                                    color['ENDC']),
                 den: u'{0}{1}Denied Keys:{2}'.format(
                                    ' ' * ident,
                                    color['LIGHT_MAGENTA'],
                                    color['ENDC']),
                 rej: u'{0}{1}Rejected Keys:{2}'.format(
                                    ' ' * ident,
                                    color['LIGHT_BLUE'],
                                    color['ENDC']),
                 'local': u'{0}{1}Local Keys:{2}'.format(
                                    ' ' * ident,
                                    color['LIGHT_MAGENTA'],
                                    color['ENDC'])}
    else:
        acc = 'accepted'
        pend = 'pending'
        rej = 'rejected'

        cmap = {pend: color['RED'],
                acc: color['GREEN'],
                rej: color['BLUE'],
                'local': color['MAGENTA']}

        trans = {pend: u'{0}{1}Unaccepted Keys:{2}'.format(
                                    ' ' * ident,
                                    color['LIGHT_RED'],
                                    color['ENDC']),
                 acc: u'{0}{1}Accepted Keys:{2}'.format(
                                    ' ' * ident,
                                    color['LIGHT_GREEN'],
                                    color['ENDC']),
                 rej: u'{0}{1}Rejected Keys:{2}'.format(
                                    ' ' * ident,
                                    color['LIGHT_BLUE'],
                                    color['ENDC']),
                 'local': u'{0}{1}Local Keys:{2}'.format(
                                    ' ' * ident,
                                    color['LIGHT_MAGENTA'],
                                    color['ENDC'])}

    ret = ''

    for status in sorted(data):
        ret += u'{0}\n'.format(trans[status])
        for key in sorted(data[status]):
            key = sdecode(key)
            skey = salt.output.strip_esc_sequence(key) if strip_colors else key
            if isinstance(data[status], list):
                ret += u'{0}{1}{2}{3}\n'.format(
                        ' ' * ident,
                        cmap[status],
                        skey,
                        color['ENDC'])
            if isinstance(data[status], dict):
                ret += u'{0}{1}{2}:  {3}{4}\n'.format(
                        ' ' * ident,
                        cmap[status],
                        skey,
                        data[status][key],
                        color['ENDC'])
    return ret
