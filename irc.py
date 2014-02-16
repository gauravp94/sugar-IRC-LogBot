#!/usr/bin/python

'''
  To run the program there are three arguments that are needed
  Presently it requires run like <python ircBot.py>
  It saves the log in log_<date>.html
  Made by Gaurav Parida (gp94 on IRC)

  Code is inspired from these links 
  -- https://github.com/ignaciouy/Google-Code-In-Bot
  -- https://github.com/aviraldg/gcibot
  -- https://github.com/sant0sh/PyBot
'''


from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log
import time
import sys
import os

class MessageLogger:
    """
    An independent logger class (because separation of application
    and protocol logic is a good thing).
    """
    def __init__(self, file):
        self.file = file
    
    def log(self, message):
        """Write a message to the file."""
        timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
        self.file.write('%s %s\n' % (timestamp, message))
        self.file.flush()
    
    def close(self):
        self.file.close()


class LogBot(irc.IRCClient):
    """A logging IRC bot."""
    
    nickname = "sugarLog"
    
    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        if os.path.isfile(self.factory.filename):
                self.logger = MessageLogger(open(self.factory.filename, "a"))
        else:
                self.logger = MessageLogger(open(self.factory.filename, "w"))
        self.logger.log("[connected at %s]" %time.asctime(time.localtime(time.time())))
    
    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.logger.log("[disconnected at %s]" % 
                        time.asctime(time.localtime(time.time())))
        self.logger.close()
    
    # callbacks for events
    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.join(self.factory.channel)
    
    def joined(self, channel):
        """This will get called when the bot joins the channel."""
        self.logger.log("[I have joined %s]" % channel)
    
    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]
        self.logger.log("<%s> %s" % (user, msg))
        # Check to see if they're sending me a private message
        if channel == self.nickname:
            msg = "Private Chat doesnt interest me!"
            self.msg(user, msg)
            return
        # Otherwise check to see if it is a message directed at me
        if msg.startswith(self.nickname + ":"):
            msg = "%s: Hello, I am an automated bot made to keep the logs of the sugar IRC Channel" % user
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))
    
    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""
        user = user.split('!', 1)[0]
        self.logger.log("* %s %s" % (user, msg))
    
    # irc callbacks
    def irc_NICK(self, prefix, params):
        """Called when an IRC user changes their nickname."""
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        self.logger.log("%s is now known as %s" % (old_nick, new_nick))
    
    # For fun, override the method that determines how a nickname is changed on
    # collisions. The default method appends an underscore.
    def alterCollidedNick(self, nickname):
        """
        Generate an altered version of a nickname that caused a collision in an
        effort to create an unused related name for subsequent registration.
        """
        return nickname + '^'


class LogBotFactory(protocol.ClientFactory):
    """A factory for LogBots.

    A new protocol instance will be created each time we connect to the server.
    """
    
    def __init__(self, channel, filename):
        self.channel = channel
        #generating the absolute path
        dirPath = os.path.dirname(os.path.abspath(__file__))
        self.filename = os.path.join(dirPath,filename)
    
    def buildProtocol(self, addr):
        p = LogBot()
        p.factory = self
        return p
    
    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()
    
    def clientConnectionFailed(self, connector, reason):
        print "Connection failed:", reason
        reactor.stop()


if __name__ == '__main__':
    # Generating the name of the file
    filename_prefix = "log"
    filename_middle = time.strftime("%d_%m_%Y")
    filename_end = ".html"
    filename = filename_prefix + filename_middle + filename_end
    # initialize logging
    log.startLogging(sys.stdout)
    # create factory protocol and application
    f = LogBotFactory("sugar", filename)
    # connect factory to this host and port
    reactor.connectTCP("irc.freenode.net", 6667, f)
    # run bot
    reactor.run()
