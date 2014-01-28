import logging
import xmpp
from utils import logerrors, randomstr
from jabberbot import botcmd
import re
from datetime import datetime

class SweetieAdmin():
    mods = [
        'Blighty', 'Nyctef', 'Princess Luna', 'Luna', 'LunaNet', 'Princess Cadence',
        'Rainbow Dash', 'Twilight Sparkle', 'Big Macintosh', 'Fluttershard', 'Rainbow Dash', 'Spike']

    def __init__(self, bot, chatroom):
        self.bot = bot
        self.bot.load_commands_from(self)
        self.chatroom = chatroom

    def get_sender_username(self, message):
        return self.bot.get_sender_username(message)

    def _ban(self, room, nick=None, jid=None, reason=None, ban=True):
        """Kicks user from muc
        Works only with sufficient rights."""
        logging.debug('rm:{} nk{} jid{} rsn{} isBan{}'.format(
            room, nick, jid, reason, ban))
        NS_MUCADMIN = 'http://jabber.org/protocol/muc#admin'
        item = xmpp.simplexml.Node('item')
        if nick is not None:
            item.setAttr('nick', nick)
        if jid is not None:
            item.setAttr('jid', jid)
        item.setAttr('affiliation', 'outcast' if ban else 'none')
        iq = xmpp.Iq(typ='set', queryNS=NS_MUCADMIN, xmlns=None, to=room,
                     payload=set([item]))
        if reason is not None:
            item.setTagData('reason', reason)
        self.bot.connect().send(iq)

    def get_nick_reason(self, args):
        nick = None
        reason = None
        match = re.match("\s*'([^']*)'(.*)", args) or\
            re.match("\s*\"([^\"]*)\"(.*)", args) or\
            re.match("\s*(\S*)(.*)", args)
        if match:
            nick = match.group(1)
            reason = match.group(2).strip()
        return nick, reason

    def chat(self, message):
        self.bot.send(self.chatroom, message, message_type='groupchat')

    @botcmd
    @logerrors
    def listbans(self, mess, args):
        """List the current bans. Requires admin"""
        id = 'banlist'+randomstr()
        NS_MUCADMIN = 'http://jabber.org/protocol/muc#admin'
        item = xmpp.simplexml.Node('item')
        item.setAttr('affiliation', 'outcast')
        iq = xmpp.Iq(
            typ='get', attrs={"id": id}, queryNS=NS_MUCADMIN, xmlns=None, to=self.chatroom,
            payload=set([item]))

        def handleBanlist(session, response):
            if response is None:
                return "timed out waiting for banlist"
            res = ""
            items = response.getChildren()[0].getChildren()
            for item in items:
                if item.getAttr('jid') is not None:
                    res += "\n" + item.getAttr('jid') + ": "+str(item.getChildren()[0].getData())
            self.chat(res)

        self.bot.connect().SendAndCallForResponse(iq, handleBanlist)

    @botcmd(name='ban')
    @logerrors
    def ban(self, mess, args):
        '''bans user. Requires admin and a reason

        nick can be wrapped in single or double quotes'''

        nick, reason = self.get_nick_reason(args)

        if not len(reason):
            return "A reason must be provided"

        sender = self.get_sender_username(mess)
        if sender in self.mods:
            print("trying to ban "+nick+" with reason "+reason)
            self._ban(self.chatroom, nick, None, 'Banned by '+sender +
                      ': ['+reason+'] at '+datetime.now().strftime("%I:%M%p on %B %d, %Y"))
        else:
            return "noooooooope."

    @botcmd(name='unban')
    @logerrors
    def un(self, mess, args):
        '''unbans a user. Requires admin and a jid (check listbans)

        nick can be wrapped in single or double quotes'''

        jid = args

        sender = self.get_sender_username(mess)
        if sender in self.mods:
            print("trying to unban "+jid)
            self._ban(self.chatroom, jid=jid, ban=False)
        else:
            return "noooooooope."

    @botcmd(name='kick')
    @logerrors
    def remove(self, mess, args):
        '''kicks user. Requires admin and a reason

        nick can be wrapped in single or double quotes'''

        nick, reason = self.get_nick_reason(args)

        if not len(reason):
            return "A reason must be provided"

        sender = self.get_sender_username(mess)
        if sender in self.mods:
            print("trying to kick "+nick+" with reason "+reason)
            self.bot.kick(self.chatroom, nick, 'Kicked by '+sender + ': '+reason)
        else:
            return "noooooooope."
