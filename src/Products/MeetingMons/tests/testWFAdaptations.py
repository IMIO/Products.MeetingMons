# -*- coding: utf-8 -*-
#
# File: testWFAdaptations.py
#
# Copyright (c) 2013 by Imio.be
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

from Products.MeetingCommunes.tests.testWFAdaptations import testWFAdaptations as mctwfa
from Products.MeetingMons.tests.MeetingMonsTestCase import MeetingMonsTestCase
from Products.PloneMeeting.model.adaptations import RETURN_TO_PROPOSING_GROUP_CUSTOM_PERMISSIONS


class testWFAdaptations(MeetingMonsTestCase, mctwfa):
    '''See doc string in PloneMeeting.tests.testWFAdaptations.'''

    def test_pm_WFA_availableWFAdaptations(self):
        '''Test what are the available wfAdaptations.'''
        # we removed the 'archiving' and 'creator_initiated_decisions' wfAdaptations
        self.assertSetEqual(
            set(self.meetingConfig.listWorkflowAdaptations().keys()),
            {
                'item_validation_shortcuts',
                'item_validation_no_validate_shortcuts',
                'only_creator_may_delete',
                'no_freeze',
                'no_publication',
                'no_decide',
                'accepted_but_modified',
                'postpone_next_meeting',
                'mark_not_applicable',
                'removed',
                'removed_and_duplicated',
                'refused',
                'delayed',
                'pre_accepted',
                "return_to_proposing_group",
                "return_to_proposing_group_with_last_validation",
                'hide_decisions_when_under_writing'
            }
        )

    def _return_to_proposing_group_active_state_to_clone(self):
        '''Helper method to test 'return_to_proposing_group' wfAdaptation regarding the
           RETURN_TO_PROPOSING_GROUP_STATE_TO_CLONE defined value.
           In our usecase, this is Nonsense as we use RETURN_TO_PROPOSING_GROUP_CUSTOM_PERMISSIONS.'''
        return

    def _return_to_proposing_group_active_custom_permissions(self):
        '''Helper method to test 'return_to_proposing_group' wfAdaptation regarding the
           RETURN_TO_PROPOSING_GROUP_CUSTOM_PERMISSIONS defined value.
           In our use case, just test that permissions of 'returned_to_proposing_group' state
           are the one defined in RETURN_TO_PROPOSING_GROUP_CUSTOM_PERMISSIONS.'''
        itemWF = self.wfTool.getWorkflowsFor(self.meetingConfig.getItemTypeName())[0]
        returned_to_proposing_group_state_permissions = itemWF.states['returned_to_proposing_group'].permission_roles
        for permission in returned_to_proposing_group_state_permissions:
            self.assertEquals(returned_to_proposing_group_state_permissions[permission],
                              RETURN_TO_PROPOSING_GROUP_CUSTOM_PERMISSIONS[self.meetingConfig.getItemWorkflow()][permission])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testWFAdaptations, prefix='test_pm_'))
    return suite
