# -*- coding: utf-8 -*-
#
# File: testCustomMeeting.py
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

from Products.MeetingMons.tests.MeetingMonsTestCase import \
    MeetingMonsTestCase

from DateTime import DateTime


class testCustomMeeting(MeetingMonsTestCase):
    """
        Tests the Meeting adapted methods
    """

    def test_getAvailableItems(self):
        '''
          Already tested in MeetingMons.tests.testMeeting.py
        '''
        pass

    def test_GetPrintableItems(self):
        meetingConfigCollege = self.meetingConfig.getId()
        self.changeUser('pmManager')

        #makes the college meeting
        self.setMeetingConfig(meetingConfigCollege)
        meetingDate = DateTime('2019/09/09 19:19:19')
        collegeMeeting = self._createMeetingWithItems(meetingDate=meetingDate)

        #create another point in the development category to help the enum test
        item5 = self.create('MeetingItem')
        item5.setProposingGroup('vendors')
        item5.setPrivacy('public')
        item5.setCategory('development')
        item5.setDecision('<p>A decision</p>')
        self.presentItem(item5)

        #build the list of uids
        collegeItemUids = []
        for item in collegeMeeting.getItems(ordered=True):
            collegeItemUids.append(item.UID())

        items = collegeMeeting.adapted().getPrintableItems(
            itemUids=collegeItemUids
        )
        #Are all the categories there?
        self.assertTrue([item.getId() for item in items] ==
                        ['recItem1', 'recItem2', 'o3', 'o5', 'o2', 'o4', 'o6', 'o7'])

    def test_GetPrintableItemsByCategory(self):
        meetingConfigCollege = self.meetingConfig.getId()
        self.changeUser('pmManager')

        #makes the college meeting
        self.setMeetingConfig(meetingConfigCollege)
        meetingDate = DateTime('2019/09/09 19:19:19')
        collegeMeeting = self._createMeetingWithItems(meetingDate=meetingDate)

        #create another point in the development category to help the enum test
        item5 = self.create('MeetingItem')
        item5.setProposingGroup('vendors')
        item5.setPrivacy('public')
        item5.setCategory('development')
        item5.setDecision('<p>A decision</p>')
        self.presentItem(item5)

        #build the list of uids
        collegeItemUids = []
        for item in collegeMeeting.getItems(ordered=True):
            collegeItemUids.append(item.UID())

        sub_list = collegeMeeting.adapted().getPrintableItemsByCategory(
            itemUids=collegeItemUids
        )
        #Are all the categories there?
        self.assertTrue(sub_list[0][0].getId() == 'developers')
        self.assertTrue([item.getId() for item in sub_list[0][1:]] == ['recItem1', 'recItem2', 'o3', 'o5'])
        self.assertTrue(sub_list[1][0].getId() == 'vendors')
        self.assertTrue([item.getId() for item in sub_list[1][1:]] == ['o2', 'o4', 'o6', 'o7'])
