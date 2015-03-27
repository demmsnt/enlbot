#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Channel based on SleekXMPP
"""

import sys
import logging
import time
import asyncio
import slixmpp


# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')


class MUCBot(slixmpp.ClientXMPP):

    """
    A simple SleekXMPP bot that will greets those
    who enter the room, and acknowledge any messages
    that mentions the bot's nickname.
    """

    def __init__(self, jid, password, on_online, on_message, on_start):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        self.add_event_handler("session_start", self.start)
        self.add_event_handler("groupchat_message", self.muc_message)
        self.connected = False
        self.on_online = on_online
        self.on_message = on_message
        self.on_start = on_start

    def start(self, event):
        """
        Process the session_start event.

        Typical actions for the session_start event are
        requesting the roster and broadcasting an intial
        presence stanza.

        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
        self.send_presence()
        self.get_roster()
        self.connected = True
        #self.send_message(mto=CONNDATA['room'],
        #                      mbody="Hello, All",
        #                      mtype='groupchat')
        self.on_start()
            
    def room_connect(self, room, nick, room_password=None):
        if room_password is None:
            self.plugin['xep_0045'].joinMUC(room, 
                                        nick, 
                                        wait=True)
        else:
            self.plugin['xep_0045'].joinMUC(room, 
                                        nick, 
                                        # If a room password is needed, use:
                                        password=room_password,
                                        wait=True)
        self.add_event_handler("muc::%s::got_online" % room,
                               self.muc_online)
        
    def muc_message(self, msg):
        """
        Process incoming message stanzas from any chat room. Be aware 
        that if you also have any handlers for the 'message' event,
        message stanzas may be processed by both handlers, so check
        the 'type' attribute when using a 'message' event handler.

        Whenever the bot's nickname is mentioned, respond to
        the message.

        IMPORTANT: Always check that a message is not from yourself,
                   otherwise you will create an infinite loop responding
                   to your own messages.

        This handler will reply to messages that mention 
        the bot's nickname.

        Arguments:
            msg -- The received message stanza. See the documentation
                   for stanza objects and the Message stanza to see
                   how it may be used.
        """
        #if msg['mucnick'] != self.nick: # and self.nick in msg['body']:
        #    #self.send_message(mto=msg['from'].bare,
        #    #                  mbody="I heard that, %s." % msg['mucnick'],
        #    #                  mtype='groupchat')
        #    #self.send2hg('j:({}): {}'.format(str(msg['mucnick']), str(msg['body'])))
        #    #
        #    #print("MSG=",msg['body'], type(msg), msg.keys())
        #    #self.send2hg('j:({}): {}'.format(str(msg['mucnick']), str(msg['body'])))
        #    #print('-'*80)
        #    #print(">>>>>>",msg['body'])
        #    text=str(msg['body'])
        #    #print('Text:',text, text.startswith('`'), self.send2hg)
        #    if text.startswith('`') and self.send2hg is not None:
        #        self.send2hg('j:({}): {}'.format(str(msg['mucnick']), text))
        #    pass
        self.on_message(msg)


    def muc_online(self, presence):
        """
        Process a presence stanza from a chat room. In this case,
        presences from users that have just come online are 
        handled by sending a welcome message that includes
        the user's nickname and role in the room.

        Arguments:
            presence -- The received presence stanza. See the 
                        documentation for the Presence stanza
                        to see how else it may be used.
        """
        self.on_online(presence)
#        if presence['muc']['nick'] != self.nick:
#            self.send_message(mto=presence['from'].bare,
#                              mbody="Hello, %s %s" % (presence['muc']['role'],
#                                                      presence['muc']['nick']),
#                              mtype='groupchat')

def get_xmpp(jid, password, on_message, on_online, on_start):
    xmpp = MUCBot(jid, 
                  password, 
                  on_message, 
                  on_online,
                  on_start)
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0045') # Multi-User Chat
    xmpp.register_plugin('xep_0199') # XMPP Ping
    return xmpp
        


