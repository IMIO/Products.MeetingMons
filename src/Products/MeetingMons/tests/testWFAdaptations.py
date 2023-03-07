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
                'mons_budget_reviewer',
                "return_to_proposing_group",
                "return_to_proposing_group_with_last_validation",
                'hide_decisions_when_under_writing'
            }
        )

    def test_pm_Validate_workflowAdaptations_dependencies(self):
        pass

    def test_pm_Validate_workflowAdaptations_removed_return_to_proposing_group_with_last_validation(self):
        pass

    def test_pm_WFA_return_to_proposing_group_with_hide_decisions_when_under_writing(self):
        pass

    def test_pm_MeetingNotClosableIfItemStillReturnedToProposingGroup(self):
        pass

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testWFAdaptations, prefix='test_pm_'))
    return suite
