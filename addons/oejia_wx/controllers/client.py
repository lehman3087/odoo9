# coding=utf-8

from werobot.client import Client

wxclient = Client('wxd548cbdc841c83e9', '47aa81e196e4f73c25d4a0816c8eb159')

UUID_OPENID = {}

def send_text(openid,text):
    wxclient.send_text_message(openid, text)

def chat_send(db,uuid, msg):
    _dict = UUID_OPENID.get(db,None)
    if _dict:
        openid = _dict.get(uuid,None)
        if openid:
            send_text(openid, msg)
    return -1
