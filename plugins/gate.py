#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unidecode
import hangups

def on_hg_message(coord, ev):
    CONF_ID = coord.config['hgrooms'][0]
    conv = coord.channels['HG']._conv_list.get(ev.conversation_id)
    user = conv.get_user(ev.user_id)
    if ev.conversation_id in CONF_ID and not ev.text.startswith('j:('):
       coord.channels['XMPP'].send_message(mto=coord.config['room'],
                              mbody='({}): {}'.format(user.full_name,ev.text),
                              mtype='groupchat')    
    text = unidecode.unidecode(ev.text)
    if ev.conversation_id in CONF_ID and text.startswith('%h'):
       conversation = coord.channels['HG']._conv_list.get(coord.config['hgrooms'][0])
       segments = []
       segments.append(hangups.ChatMessageSegment('j:(\nHello i am bot - you can '))
       segments.append(hangups.ChatMessageSegment('fork me', link_target='https://github.com/demmsnt/enlbot'))
       segments.append(hangups.ChatMessageSegment('  '))
       segments.append(hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK))
       segments.append(hangups.ChatMessageSegment('Инфа об игре', link_target='http://networkglobal.ru:8090/%D0%9A%D0%B0%D0%BA%D0%98%D0%B3%D1%80%D0%B0%D1%82%D1%8C'))
       coord.channels['HG'].send_message_segments(conversation , segments)

    if ev.conversation_id in CONF_ID and text.startswith('InkReD'):
       conversation = coord.channels['HG']._conv_list.get(coord.config['hgrooms'][0])
       segments = []
       segments.append(hangups.ChatMessageSegment(' InkReD', link_target='https://lh3.googleusercontent.com/-V2xwgnVmS1k/VRVYUpXKAsI/AAAAAAAAABg/W0MgJyOfxak/s0/InkRed1.png'))
       coord.channels['HG'].send_message_segments(conversation , segments)
       
           
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

