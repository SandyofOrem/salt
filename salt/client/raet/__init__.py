# -*- coding: utf-8 -*-
'''
The client libs to communicate with the salt master when running raet
'''
from __future__ import absolute_import, unicode_literals

# Import python libs
import os
import time
import logging

# Import Salt libs
import salt.config
import salt.client
import salt.utils.kinds as kinds
import salt.utils.versions
import salt.syspaths as syspaths

try:
    from raet import raeting, nacling
    from raet.lane.stacking import LaneStack
    from raet.lane.yarding import RemoteYard
    HAS_RAET_LIBS = True
except ImportError:
    HAS_RAET_LIBS = False

log = logging.getLogger(__name__)


class LocalClient(salt.client.LocalClient):
    '''
    The RAET LocalClient
    '''
    def __init__(self,
                 c_path=os.path.join(syspaths.CONFIG_DIR, 'master'),
                 mopts=None):

        salt.client.LocalClient.__init__(self, c_path, mopts)

    def pub(self,
            tgt,
            fun,
            arg=(),
            tgt_type='glob',
            ret='',
            jid='',
            timeout=5,
            **kwargs):
        '''
        Publish the command!
        '''
        if 'expr_form' in kwargs:
            salt.utils.versions.warn_until(
                'Fluorine',
                'The target type should be passed using the \'tgt_type\' '
                'argument instead of \'expr_form\'. Support for using '
                '\'expr_form\' will be removed in Salt Fluorine.'
            )
            tgt_type = kwargs.pop('expr_form')

        payload_kwargs = self._prep_pub(
                tgt,
                fun,
                arg=arg,
                tgt_type=tgt_type,
                ret=ret,
                jid=jid,
                timeout=timeout,
                **kwargs)

        kind = self.opts['__role']
        if kind not in kinds.APPL_KINDS:
            emsg = ("Invalid application kind = '{0}' for Raet LocalClient.".format(kind))
            log.error(emsg + "\n")
            raise ValueError(emsg)
        if kind in [kinds.APPL_KIND_NAMES[kinds.applKinds.master],
                    kinds.APPL_KIND_NAMES[kinds.applKinds.syndic]]:
            lanename = 'master'
        else:
            emsg = ("Unsupported application kind '{0}' for Raet LocalClient.".format(kind))
            log.error(emsg + '\n')
            raise ValueError(emsg)

        sockdirpath = self.opts['sock_dir']
        name = 'client' + nacling.uuid(size=18)
        stack = LaneStack(
                name=name,
                lanename=lanename,
                sockdirpath=sockdirpath)
        stack.Pk = raeting.PackKind.pack.value
        manor_yard = RemoteYard(
                stack=stack,
                lanename=lanename,
                name='manor',
                dirpath=sockdirpath)
        stack.addRemote(manor_yard)
        route = {'dst': (None, manor_yard.name, 'local_cmd'),
                 'src': (None, stack.local.name, None)}
        msg = {'route': route, 'load': payload_kwargs}
        stack.transmit(msg)
        stack.serviceAll()
        while True:
            time.sleep(0.01)
            stack.serviceAll()
            while stack.rxMsgs:
                msg, sender = stack.rxMsgs.popleft()
                ret = msg.get('return', {})
                if 'ret' in ret:
                    stack.server.close()
                    return ret['ret']
                stack.server.close()
                return ret
