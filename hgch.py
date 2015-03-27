#!/usr/bin/python3
# -*- coding: utf8 -*-
""" logging bot """
#,"Ugz10p7YaqlMNWW8pil4AaABAQ","Ugx6b2zE3Dt8Aq0dggF4AaABAQ"]

import os, sys, argparse, logging, shutil, asyncio, time, signal, traceback
import os.path
import appdirs
import hangups
from hangups.ui.utils import get_conv_name


class HgBot(object):
    """Hangouts bot listening on all conversations"""
    def __init__(self, cookies_path, max_retries=5, on_message=None, on_member_change=None, on_rename=None):
        self._client = None
        self._cookies_path = cookies_path
        self._max_retries = max_retries
        self.on_message=on_message
        self.on_member_change=on_member_change
        self.on_rename=on_rename
        # These are populated by on_connect when it's called.
        self._conv_list = None        # hangups.ConversationList
        self._user_list = None        # hangups.UserList
        self._message_handler = None  # MessageHandler
        self.connected = False
        # Handle signals on Unix
        # (add_signal_handler is not implemented on Windows)
        try:
            loop = asyncio.get_event_loop()
            for signum in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(signum, lambda: self.stop())
        except NotImplementedError:
            pass

    def login(self, cookies_path):
        """Login to Google account"""
        # Authenticate Google user and save auth cookies
        # (or load already saved cookies)
        try:
            cookies = hangups.auth.get_auth_stdin(cookies_path)
            return cookies
        except hangups.GoogleAuthError as e:
            logging.error('Login failed ({})'.format(e))
            return False

    def run(self):
        """Connect to Hangouts and run bot"""
        cookies = self.login(self._cookies_path)
        if cookies:
            for retry in range(self._max_retries):
                try:
                    # Create Hangups client
                    self._client = hangups.Client(cookies)
                    self._client.on_connect.add_observer(self._on_connect)
                    self._client.on_disconnect.add_observer(self._on_disconnect)

                    # Start asyncio event loop and connect to Hangouts
                    # If we are forcefully disconnected, try connecting again
                    loop = asyncio.get_event_loop()
                    #asyncio.Task(asyncio.wait_for(self.sendFromJ(), 10.0))
                    #loop.run_until_complete(self.sendFromJ())
                    tasks = []
                    loop.run_until_complete(self._client.connect())
                    sys.exit(0)
                except Exception as e:
                    logging.error('Client unexpectedly disconnected:\n{}'.format(e))
                    logging.error(traceback.print_tb(sys.exc_info()[2]))
                    logging.info('Waiting {} seconds...'.format(5 + retry * 5))
                    time.sleep(5 + retry * 5)
                    logging.info('Trying to connect again (try {} of {})...'.format(retry + 1, self._max_retries))
            print('Maximum number of retries reached! Exiting...')
        sys.exit(1)

    def stop(self):
        """Disconnect from Hangouts"""
        asyncio.async(
            self._client.disconnect()
        ).add_done_callback(lambda future: future.result())


    def handle_chat_message(self, conv_event):
        """Handle chat messages"""
        self.on_message(conv_event)
        #conv = self._conv_list.get(conv_event.conversation_id)
        #user = conv.get_user(conv_event.user_id)
        #print(dir(conv_event))
        #print(user.full_name,':\t', conv_event.text)
        #print("CID:",conv_event.conversation_id)
        #if conv_event.conversation_id in CONF_ID and 'j:(' not in conv_event.text:
        #        self.xmpp.send_msg('({}): {}'.format(user.full_name,conv_event.text))
        #asyncio.async(self._message_handler.handle(conv_event))


    def handle_membership_change(self, conv_event):
        """Handle conversation membership change"""
        self.on_member_change(conv_event)
        # Generate list of added or removed users
        #event_users = [conv_event.conv.get_user(user_id) for user_id
        #               in conv_event.participant_ids]
        #names = ', '.join([user.full_name for user in event_users])
        #if conv_event.conversation_id not in CONF_ID:
        #        return

        # JOIN
        #if conv_event.type_ == hangups.MembershipChangeType.JOIN:
            #print("Join",names)
        #    self.xmpp.send_msg('[Join]: {}'.format(str(names)))
        # LEAVE
        #else:
        #    self.xmpp.send_msg('[Leave]: {}'.format(str(names)))

    def handle_rename(self, conv_event):
        """Handle conversation rename"""
        self.on_rename(conv_event)
        # Only print renames for now...
        #print("Conversation rename", conv_event.new_name)
        #if conv_event.conversation_id not in CONF_ID:
        #        return
        #self.xmpp.send_msg('[Rename]: {}</p>'.format(str(conv_event.new_name)))


    def _on_connect(self, initial_data):
        """Handle connecting for the first time"""
        logging.info('Connected!')
        #self._message_handler = hangupsbot.handlers.MessageHandler(self)
        self._user_list = hangups.UserList(self._client,
                                           initial_data.self_entity,
                                           initial_data.entities,
                                           initial_data.conversation_participants)
        self._conv_list = hangups.ConversationList(self._client,
                                                   initial_data.conversation_states,
                                                   self._user_list,
                                                   initial_data.sync_timestamp)
        self._conv_list.on_event.add_observer(self._on_event)
        self.connected=True


    def _on_event(self, conv_event):
        """Handle conversation events"""
        if isinstance(conv_event, hangups.ChatMessageEvent):
            self.handle_chat_message(conv_event)
        elif isinstance(conv_event, hangups.MembershipChangeEvent):
            self.handle_membership_change(conv_event)
        elif isinstance(conv_event, hangups.RenameEvent):
            self.handle_rename(conv_event)


    def _on_disconnect(self):
        """Handle disconnecting"""
        logging.info('Connection lost!')


    def send_message(self, conversation, text):
        """"Send simple chat message"""
        self.send_message_segments(conversation, [hangups.ChatMessageSegment(text)])


#    def sendtext(self, text):
#        conversation = self._conv_list.get(CONF_ID[0])
#        self.send_message(conversation, text)


    def send_message_segments(self, conversation, segments):
        """Send chat message segments"""
        # Ignore if the user hasn't typed a message.
        if len(segments) == 0:
            return
        # XXX: Exception handling here is still a bit broken. Uncaught
        # exceptions in _on_message_sent will only be logged.
        asyncio.async(
            conversation.send_message(segments)
        ).add_done_callback(self._on_message_sent)


    def _on_message_sent(self, future):
        """Handle showing an error if a message fails to send"""
        try:
            future.result()
        except hangups.NetworkError:
            logging.error('Failed to send message!')



