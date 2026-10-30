# -*- coding: utf-8 -*-
#
# GNU General Public License (GPL)
#

from imio.helpers.content import get_vocab_values
from Products.MeetingCommunes.tests.testWFAdaptations import testWFAdaptations as mctwfa
from Products.MeetingMons.tests.MeetingMonsTestCase import MeetingMonsTestCase


class testWFAdaptations(MeetingMonsTestCase, mctwfa):
    '''See doc string in PloneMeeting.tests.testWFAdaptations.'''

    def test_pm_WFA_availableWFAdaptations(self):
        '''Test what are the available wfAdaptations.'''
        # we have an extra custom WFA named "mons_budget_reviewer"
        self.assertIn(
            "mons_budget_reviewer", get_vocab_values(self.meetingConfig, 'WorkflowAdaptations'))

    def test_pm_Validate_workflowAdaptations_dependencies(self):
        pass

    def _process_transition_for_correcting_item(self, item, all):
        # all parameter if for custom profiles
        if all:
            # do custom WF steps
            pass
        self.changeUser('pmCreator1')
        self.do(item, 'goTo_returned_to_proposing_group_proposed')

    def test_pm_ItemDecidedWithReturnToProposingGroup(self):
        pass

    def test_pm_Validate_workflowAdaptations_removed_waiting_advices(self):
        pass

    def test_pm_WFA_decide_item_when_back_to_meeting_from_returned_to_proposing_group(self):
        pass

    def test_pm_WFA_return_to_proposing_group_with_all_validations(self):
        pass

    def test_pm_WFA_return_to_proposing_group_with_hide_decisions_when_under_writing(self):
        pass

    def test_pm_Validate_workflowAdaptations_removed_return_to_proposing_group_with_all_validations(self):
        pass

    def test_pm_WFA_return_to_proposing_group_with_last_validation(self):
        pass

    def test_pm_Validate_workflowAdaptations_removed_return_to_proposing_group_with_before_last_validation(self):
        pass


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testWFAdaptations, prefix='test_pm_'))
    return suite
