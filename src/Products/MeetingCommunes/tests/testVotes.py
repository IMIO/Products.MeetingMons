# -*- coding: utf-8 -*-
#
# File: testVotes.py
#
# Copyright (c) 2012-2013 by PloneGov
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

from Products.PloneMeeting.tests.testVotes import testVotes as pmtv
from Products.MeetingCommunes.tests.MeetingCommunesTestCase import \
    MeetingCommunesTestCase


class testVotes(MeetingCommunesTestCase, pmtv):
    '''Tests various aspects of votes management.
       Advices are enabled for PloneMeeting Assembly, not for PloneGov Assembly.
       By default, vote are encoded by 'theVoterHimself'.'''

    def test_subproduct_call_MayConsultVotes(self):
        """
           Run the testMayConsultVotes from PloneMeeting
        """
        # votes are only enabled for the meeting-config-council
        self.setMeetingConfig(self.meetingConfig2.getId())
        self.test_pm_MayConsultVotes()

    def test_subproduct_call_MayEditVotes(self):
        """
           Run the testMayEditVotes from PloneMeeting
        """
        # votes are only enabled for the meeting-config-council
        self.setMeetingConfig(self.meetingConfig2.getId())
        self.test_pm_MayEditVotes()

    def test_subproduct_call_OnSaveItemPeopleInfos(self):
        """
           Run the testOnSaveItemPeopleInfos from PloneMeeting
        """
        # votes are only enabled for the meeting-config-council
        self.setMeetingConfig(self.meetingConfig2.getId())
        self.test_pm_OnSaveItemPeopleInfos()

    def test_subproduct_call_SecretVotes(self):
        """
           Run the testSecretVotes from PloneMeeting
        """
        # votes are only enabled for the meeting-config-council
        self.setMeetingConfig(self.meetingConfig2.getId())
        self.test_pm_SecretVotes()


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testVotes, prefix='test_subproduct_'))
    return suite
