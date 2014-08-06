# -*- coding: utf-8 -*-
#
# File: testMeeting.py
#
# Copyright (c) 2007-2012 by CommunesPlone.org
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

from Products.MeetingMons.tests.MeetingMonsTestCase import MeetingMonsTestCase
from Products.MeetingCommunes.tests.testMeeting import testMeeting as mctm

from plone.app.testing import login
from AccessControl import Unauthorized


class testMeeting(MeetingMonsTestCase, mctm):
    """Tests the Meeting class methods."""

    def test_subproduct_call_RemoveOrDeleteLinkedItem(self):
        """Run the test_pm_RemoveOrDeleteLinkedItem from PloneMeeting.
           See docstring in PloneMeeting."""
        self._removeOrDeleteLinkedItem()

    def _removeOrDeleteLinkedItem(self):
        '''Test that removing or deleting a linked item works.'''
        login(self.portal, 'pmManager')
        meeting = self._createMeetingWithItems()
        self.assertEquals([item.id for item in meeting.getItemsInOrder()],
                          ['recItem1', 'recItem2', 'o3', 'o5', 'o2', 'o4', 'o6'])
        #remove an item
        item5 = getattr(meeting, 'o5')
        meeting.removeItem(item5)
        self.assertEquals([item.id for item in meeting.getItemsInOrder()],
                          ['recItem1', 'recItem2', 'o3', 'o2', 'o4', 'o6'])
        #delete a linked item
        item4 = getattr(meeting, 'o4')
        self.assertRaises(Unauthorized, self.portal.restrictedTraverse('@@delete_givenuid'), item4.UID())
        self.changeUser('admin')
        meeting.restrictedTraverse('@@delete_givenuid')(item4.UID())
        self.assertEquals([item.id for item in meeting.getItemsInOrder()],
                          ['recItem1', 'recItem2', 'o3', 'o2', 'o6'])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testMeeting, prefix='test_subproduct_'))
    return suite
