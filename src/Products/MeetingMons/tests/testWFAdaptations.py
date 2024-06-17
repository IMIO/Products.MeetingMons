# -*- coding: utf-8 -*-
#
# GNU General Public License (GPL)
#

from imio.helpers.content import get_vocab_values
from Products.MeetingCommunes.tests.testWFAdaptations import testWFAdaptations as mctwfa
from Products.MeetingMons.tests.MeetingMonsTestCase import MeetingMonsTestCase
from Products.PloneMeeting.config import MEETING_REMOVE_MOG_WFA


class testWFAdaptations(MeetingMonsTestCase, mctwfa):
    '''See doc string in PloneMeeting.tests.testWFAdaptations.'''

    def test_pm_WFA_availableWFAdaptations(self):
        '''Test what are the available wfAdaptations.'''
        # we removed the 'archiving' and 'creator_initiated_decisions' wfAdaptations
        self.assertEqual(
            sorted(get_vocab_values(self.meetingConfig, 'WorkflowAdaptations')),
            ['accepted_but_modified',
             'delayed',
             'hide_decisions_when_under_writing',
             'hide_decisions_when_under_writing__po__powerobservers',
             'hide_decisions_when_under_writing__po__restrictedpowerobservers',
             'item_validation_no_validate_shortcuts',
             'item_validation_shortcuts',
             'mark_not_applicable',
             MEETING_REMOVE_MOG_WFA,
             # custom WFA
             'mons_budget_reviewer',
             'no_decide',
             'no_freeze',
             'no_publication',
             'only_creator_may_delete',
             'postpone_next_meeting',
             'pre_accepted',
             'refused',
             'removed',
             'removed_and_duplicated',
             'return_to_proposing_group',
             'return_to_proposing_group_with_last_validation']
        )

    def test_pm_Validate_workflowAdaptations_dependencies(self):
        pass

    def test_pm_Validate_workflowAdaptations_removed_return_to_proposing_group_with_last_validation(self):
        pass

    def test_pm_WFA_return_to_proposing_group_with_hide_decisions_when_under_writing(self):
        pass

    def test_pm_MeetingNotClosableIfItemStillReturnedToProposingGroup(self):
        pass

    def _process_transition_for_correcting_item(self, item, all):
        # all parameter if for custom profiles
        if all:
            # do custom WF steps
            pass
        self.changeUser('pmCreator1')
        self.do(item, 'goTo_returned_to_proposing_group_proposed_to_director')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testWFAdaptations, prefix='test_pm_'))
    return suite
