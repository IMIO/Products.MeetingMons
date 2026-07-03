# -*- coding: utf-8 -*-
#
# File: testMeetingConfig.py
#
# GNU General Public License (GPL)
#

from Products.MeetingCommunes.tests.testSearches import testSearches as mcts
from Products.MeetingMons.tests.MeetingMonsTestCase import MeetingMonsTestCase
from Products.PloneMeeting.tests.PloneMeetingTestCase import pm_logger


class testSearches(MeetingMonsTestCase, mcts):
    """Test searches."""

    def test_pm_SearchItemsToCorrectToValidateOfHighestHierarchicLevel(self):
        '''Not used yet...'''
        pm_logger.info("Bypassing , {0} not used in MeetingMons".format(
            self._testMethodName))

    def test_pm_SearchItemsToCorrectToValidateOfEveryReviewerGroups(self):
        '''Not used yet...'''
        pm_logger.info("Bypassing , {0} not used in MeetingMons".format(
            self._testMethodName))

    def test_pm_SearchItemsToValidateOfHighestHierarchicLevelReturnsEveryLevels(self):
        '''Not used yet...'''
        pm_logger.info("Bypassing , {0} not used in MeetingMons".format(
            self._testMethodName))

    def test_pm_SearchItemsToValidateOfHighestHierarchicLevel(self):
        '''Not used yet...'''
        pm_logger.info("Bypassing , {0} not used in MeetingMons".format(
            self._testMethodName))

    def test_pm_SearchAllItemsToValidateOfHighestHierarchicLevel(self):
        '''Not used yet...'''
        pm_logger.info("Bypassing , {0} not used in MeetingMons".format(
            self._testMethodName))

    def test_pm_SearchAllItemsToValidateOfEveryReviewerGroups(self):
        pass


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testSearches, prefix='test_pm_'))
    return suite
