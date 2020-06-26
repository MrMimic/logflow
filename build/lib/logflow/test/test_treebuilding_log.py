from logflow.treebuilding.Log import Log
from unittest.mock import mock_open, patch, Mock
import unittest

def parser_function(line):
    message_split = line.strip().split()
    return message_split[9:]

def parser_function_2(line):
    message_split = line.strip().split()
    return message_split[10:]


class UtilTest(unittest.TestCase):
    def test_create(self):
        log = Log("test")
        self.assertFalse(log.usable)

        log = Log("1530388399 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123")
        self.assertTrue(log.usable)
        self.assertListEqual(log.message, ["pam_unix(sshd:session):","session","closed,", "for1", "User", "Root/1", "123"])

        log = Log("1530388399a 2018 Jun 30 21:53:19 m21205 authpriv")
        self.assertFalse(log.usable)

        print(log)
        log = Log("1530388399a 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123", parser_function=parser_function)
        self.assertListEqual(log.message, ["pam_unix(sshd:session):","session","closed,", "for1", "User", "Root/1", "123"])

        log = Log("1530388399a 2018 Jun 30 21:53:19 m21205 authpriv info sshd pam_unix(sshd:session): session closed, for1 User Root/1 123", parser_function=parser_function_2)
        self.assertListEqual(log.message, ["session","closed,", "for1", "User", "Root/1", "123"])