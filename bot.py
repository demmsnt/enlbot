#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import xmppch
import hgch
from config import CONNDATA
import logging
import sys

class Coordinator():
        def __init__(self):
            logging.getLogger('asyncio').setLevel(logging.WARNING)
            self.config = CONNDATA
            self.channels = {}
            self.channels['XMPP'] = xmppch.get_xmpp(CONNDATA['jid'], 
                                                    CONNDATA['password'], 
                                                    self.on_xmpp_online, 
                                                    self.on_xmpp_message, 
                                                    self.on_xmpp_start)
            self.channels['XMPP'].connect()
            self.channels['XMPP'].init_plugins()
            self.channels['HG'] = hgch.HgBot(CONNDATA['hgcookies'], 
                                        on_message=self.on_hg_message, 
                                        on_member_change=self.on_hg_member_change, 
                                        on_rename=self.on_hg_rename)
            self.plugins = {}
            for name in CONNDATA['plugins']:
                self.load_plugin(name)

        def load_plugin(self, name):
            logging.info('load plugin {}'.format(name))
            pl_name = 'plugins.%s' % name
            __import__(pl_name)
            self.plugins[name]=sys.modules[pl_name]

            
        def on_hg_message(self, ev):
            for k, v in self.plugins.items():
                if hasattr(v,'on_hg_message'):
                    v.on_hg_message(self, ev)


        def on_hg_member_change(self, ev):
            for k, v in self.plugins.items():
                if hasattr(v,'on_hg_member_change'):
                    v.on_hg_member_change(self, ev)

        def on_hg_rename(self, ev):
            for k, v in self.plugins.items():
                if hasattr(v,'on_hg_rename'):
                    v.on_hg_rename(self, ev)

        
        def on_xmpp_online(self, presence):
            for k, v in self.plugins.items():
                if hasattr(v,'on_xmpp_online'):
                    v.on_xmpp_online(self, presence)

            
        def on_xmpp_start(self):
            for k, v in self.plugins.items():
                if hasattr(v,'on_xmpp_start'):
                    v.on_xmpp_start(self)

        
        def on_xmpp_message(self, msg):
            for k, v in self.plugins.items():
                if hasattr(v,'on_xmpp_message'):
                    v.on_xmpp_message(self, msg)
            
        def run(self):
            self.channels['HG'].run()
            
if __name__ == '__main__':
    c = Coordinator() 
    c.run()
