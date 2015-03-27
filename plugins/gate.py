#!/usr/bin/env python
# -*- coding: utf-8 -*-

def on_hg_message(coord, ev):
    CONF_ID = coord.config['hgrooms'][0]
    conv = coord.channels['HG']._conv_list.get(ev.conversation_id)
    user = conv.get_user(ev.user_id)
    if ev.conversation_id in CONF_ID and not ev.text.startswith('j:('):
       coord.channels['XMPP'].send_message(mto=coord.config['room'],
                              mbody='({}): {}'.format(user.full_name,ev.text),
                              mtype='groupchat')    
    if ev.conversation_id in CONF_ID and ev.text.startswith('%help'):
       conversation = coord.channels['HG']._conv_list.get(coord.config['hgrooms'][0])
       text = 'j:(\nHello i am bot - you can fork me https://github.com/demmsnt/enlbot '
       coord.channels['HG'].send_message(conversation , text)
    
           
def on_xmpp_start(coord):
    room = coord.config['room']
    nick = coord.config['nick']
    room_password = coord.config['room_password']
    coord.channels['XMPP'].room_connect(room, nick, room_password)

        
def on_xmpp_message(coord, msg):
    if msg['mucnick'] != coord.config['nick']:
            text=str(msg['body'])
            if text.startswith('#'):
               conversation = coord.channels['HG']._conv_list.get(coord.config['hgrooms'][0])
               coord.channels['HG'].send_message(conversation , 'j:({}): {}'.format(str(msg['mucnick']), text[1:]))
            if text.startswith('%hglist'):
               text = []
               for c in coord.channels['HG']._conv_list.get_all():
                   text.append('({}) {}'.format(c.id_, c.name))
               coord.channels['XMPP'].send_message(mto=coord.config['room'],
                              mbody='\n{}'.format('\n'.join(text)),
                              mtype='groupchat')    

