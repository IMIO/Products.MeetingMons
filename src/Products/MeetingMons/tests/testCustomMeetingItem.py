# -*- coding: utf-8 -*-
#
# File: testCustomMeetingItem.py
#
# Copyright (c) 2007-2013 by Imio.be
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

from DateTime import DateTime
from datetime import datetime
from Products.MeetingMons.config import FINANCE_ADVICES_COLLECTION_ID
from Products.MeetingMons.tests.MeetingMonsTestCase import MeetingMonsTestCase


class testCustomMeetingItem(MeetingMonsTestCase):
    """
        Tests the MeetingItem adapted methods
    """
    def test_GetEchevinsForProposingGroup(self):
        '''Check a meetingItem for developers group return an echevin (the Same group in our case)
           and a meetingItem for vendors return no echevin.'''
        # create an item for test
        self.changeUser('pmManager')
        meetingDate = DateTime('2008/06/12 08:00:00')
        self.create('Meeting', date=meetingDate)
        # create items
        self.changeUser('pmCreator1')
        i1 = self.create('MeetingItem')
        i1.setProposingGroup('vendors')
        # before present in meeting, certfiedSignatures must be empty
        res = i1.adapted().getEchevinsForProposingGroup()
        self.assertEquals(res, [])
        self.changeUser('pmCreator1')
        i2 = self.create('MeetingItem')
        i2.setProposingGroup('developers')
        # before present in meeting, certfiedSignatures must be empty
        res = i2.adapted().getEchevinsForProposingGroup()
        self.assertEquals(res, ['developers'])
        # disabled MeetingGroup are still taken into account
        self.changeUser('admin')
        self.do(self.tool.developers, 'deactivate')
        self.assertEquals(self.wfTool.getInfoFor(self.tool.developers, 'review_state'), 'inactive')
        # getMeetingGroups called by getEchevinsForProposingGroup is memoized
        self.cleanMemoize()
        self.assertEquals(i2.adapted().getEchevinsForProposingGroup(), ['developers'])

    def test_GetUsedFinanceGroupIds(self):
        '''Test the custom MeetingItem.getUsedFinanceGroupIds method
           that will return adviser ids used on the FINANCE_ADVICES_COLLECTION_ID
           collection, this is used in the adapted method 'showFinanceAdviceTemplate'.'''
        cfg = self.meetingConfig
        collection = getattr(cfg.searches.searches_items, FINANCE_ADVICES_COLLECTION_ID)
        collection.setQuery([
            {'i': 'portal_type',
             'o': 'plone.app.querystring.operation.selection.is',
             'v': [cfg.getItemTypeName(), ]},
            {'i': 'indexAdvisers',
             'o': 'plone.app.querystring.operation.selection.is',
             'v': ['delay_real_group_id__unique_id_001',
                   'delay_real_group_id__unique_id_002']}
        ], )
        today = DateTime().strftime('%Y/%m/%d')
        cfg.setCustomAdvisers([
            {'row_id': 'unique_id_001',
             'group': 'developers',
             'for_item_created_from': today,
             'delay': '10',
             'delay_left_alert': '4',
             'delay_label': 'Finance advice 1',
             'is_linked_to_previous_row': '0'},
            {'row_id': 'unique_id_002',
             'group': 'developers',
             'for_item_created_from': today,
             'delay': '20',
             'delay_left_alert': '4',
             'delay_label': 'Finance advice 2',
             'is_linked_to_previous_row': '1'},
            {'row_id': 'unique_id_003',
             'group': 'developers',
             'for_item_created_from': today,
             'delay': '20',
             'delay_left_alert': '4',
             'delay_label': 'Not a finance advice',
             'is_linked_to_previous_row': '0'}, ]
        )
        # create an item without finance advice
        self.changeUser('pmManager')
        item = self.create('MeetingItem')
        # there are financeGroupIds
        self.assertEquals(cfg.adapted().getUsedFinanceGroupIds(), ['developers'])
        # but not for item
        self.assertEquals(cfg.adapted().getUsedFinanceGroupIds(item), [])
        self.assertFalse(item.adapted().showFinanceAdviceTemplate())

        # ask advice of another group
        item.setOptionalAdvisers(('vendors', ))
        item.at_post_edit_script()
        # no usedFinanceGroupId
        self.assertEquals(cfg.adapted().getUsedFinanceGroupIds(item), [])
        self.assertFalse(item.adapted().showFinanceAdviceTemplate())

        # now ask advice of developers, considered as an non finance
        # advice as only customAdvisers are considered
        item.setOptionalAdvisers(('developers', ))
        item.at_post_edit_script()
        self.assertEquals(cfg.adapted().getUsedFinanceGroupIds(item), [])
        self.assertFalse(item.adapted().showFinanceAdviceTemplate())

        # right ask a custom advice that is not a finance advice this time
        item.setOptionalAdvisers(('developers__rowid__unique_id_003', ))
        item.at_post_edit_script()
        self.assertEquals(cfg.adapted().getUsedFinanceGroupIds(item), [])
        self.assertFalse(item.adapted().showFinanceAdviceTemplate())

        # finally ask a real finance advice, this time it will work
        item.setOptionalAdvisers(('developers__rowid__unique_id_001', ))
        item.at_post_edit_script()
        self.assertEquals(cfg.adapted().getUsedFinanceGroupIds(item), ['developers'])
        self.assertTrue(item.adapted().showFinanceAdviceTemplate())

        # if the collection does not exist, [] is returned
        self.deleteAsManager(collection.UID())
        self.assertEquals(cfg.adapted().getUsedFinanceGroupIds(item), [])
        self.assertFalse(item.adapted().showFinanceAdviceTemplate())

    def test_AdviceDelayIsTimedOutWithRowId(self):

        today = DateTime().strftime('%Y/%m/%d')
        # oneMonthAgo = DateTime() - 30
        self.meetingConfig.setCustomAdvisers([
            {'row_id': 'unique_id_001',
             'group': 'developers',
             'for_item_created_from': today,
             'delay': '10',
             'delay_left_alert': '4',
             'delay_label': 'Finance advice < 20000 euros',
             'is_linked_to_previous_row': '0'},
            {'row_id': 'unique_id_002',
             'group': 'developers',
             'for_item_created_from': today,
             'delay': '20',
             'delay_left_alert': '4',
             'delay_label': 'Finance advice > 20000 euros',
             'is_linked_to_previous_row': '1'},
            {'row_id': 'unique_id_003',
             'group': 'developers',
             'for_item_created_from': today,
             'delay': '20',
             'delay_left_alert': '4',
             'delay_label': 'Finance advice > 40000 euros',
             'is_linked_to_previous_row': '0'}, ]
        )

        # create an item without finance advice
        self.changeUser('pmManager')
        item = self.create('MeetingItem')
        self.assertEquals(item.adapted().adviceDelayIsTimedOutWithRowId(groupId='developers'), False)
        self.assertEquals(item.adapted().adviceDelayIsTimedOutWithRowId(groupId='developers',
                                                                        rowIds=['unique_id_002']), False)

        # ask advice to another group
        item.setOptionalAdvisers(('vendors', ))
        item.at_post_edit_script()
        self.assertEquals(item.adapted().adviceDelayIsTimedOutWithRowId(groupId='developers'), False)
        self.assertEquals(item.adapted().adviceDelayIsTimedOutWithRowId(groupId='developers',
                                                                        rowIds=['unique_id_002']), False)

        # ask advice without delay
        item.setOptionalAdvisers(('developers', ))
        item.at_post_edit_script()
        self.assertEquals(item.adapted().adviceDelayIsTimedOutWithRowId(groupId='developers'), False)
        self.assertEquals(item.adapted().adviceDelayIsTimedOutWithRowId(groupId='developers',
                                                                        rowIds=['unique_id_002']), False)

        # ask advice with delay but without the good RowId and not timed out
        item.setOptionalAdvisers(('developers__rowid__unique_id_003', ))
        item.at_post_edit_script()
        self.do(item, 'propose')
        self.assertEquals(item.adapted().adviceDelayIsTimedOutWithRowId(groupId='developers'), False)
        self.assertEquals(item.adapted().adviceDelayIsTimedOutWithRowId(groupId='developers',
                                                                        rowIds=['unique_id_002']), False)

        # ask advice with delay and good RowId but not timed out
        item.setOptionalAdvisers(('developers__rowid__unique_id_002', ))
        item.at_post_edit_script()
        self.assertEquals(item.adapted().adviceDelayIsTimedOutWithRowId(groupId='developers'), False)
        self.assertEquals(item.adapted().adviceDelayIsTimedOutWithRowId(groupId='developers',
                                                                        rowIds=['unique_id_002']), False)

        # ask advice with delay and time out but without the good RowId
        item.setOptionalAdvisers(('developers__rowid__unique_id_001', ))
        item.at_post_edit_script()
        item.adviceIndex['developers']['delay_started_on'] = datetime(2016, 01, 01)
        item.at_post_edit_script()
        self.assertEquals(item.adapted().adviceDelayIsTimedOutWithRowId(groupId='developers'), True)
        self.assertEquals(item.adapted().adviceDelayIsTimedOutWithRowId(groupId='developers',
                                                                        rowIds=['unique_id_002']), False)

        # ask advice with delay and time out but with a bunch of bad RowIds
        item.setOptionalAdvisers(('developers__rowid__unique_id_002', ))
        item.at_post_edit_script()
        item.adviceIndex['developers']['delay_started_on'] = datetime(2016, 01, 01)
        item.at_post_edit_script()
        self.assertEquals(item.adapted().adviceDelayIsTimedOutWithRowId(groupId='developers'), True)
        self.assertEquals(item.adapted().adviceDelayIsTimedOutWithRowId(
            groupId='developers',
            rowIds=['unique_id_001', 'unique_id_003']), False)
        # add the good row id in the list.
        self.assertEquals(item.adapted().adviceDelayIsTimedOutWithRowId(
            groupId='developers',
            rowIds=['unique_id_001', 'unique_id_002', 'unique_id_003']), True)
        # put the good row id alone in the list.
        self.assertEquals(item.adapted().adviceDelayIsTimedOutWithRowId(groupId='developers',
                                                                        rowIds=['unique_id_002']), True)
