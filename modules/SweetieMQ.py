from azure.servicebus import ServiceBusService, Message
import logging

log = logging.getLogger(__name__)

class SweetieMQ(object):

    bus_service = None
    topic = None

    def __init__(self, config):
        account_key = getattr(config, 'sb_account_key', None)
        issuer = getattr(config, 'sb_issuer', None)
        if issuer is None:
            issuer = 'owner'
        if account_key is None:
            return

        self.bus_service = ServiceBusService(service_namespace='jabber-fimsquad',\
                account_key=account_key, issuer=issuer)
        self.topic = 'chat-general'

    def send(self, message):
        if self.bus_service is None:
            return
        log.debug('Sending message '+str(message))
        msg = Message(message)
        try:
            self.bus_service.send_topic_message(self.topic, msg)
        except Exception as e:
            log.error("MESSAGE DELIVERY FAILED: "+str(e))
