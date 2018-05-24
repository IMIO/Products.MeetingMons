
from Products.MeetingMons.tests.MeetingMonsTestCase import MeetingMonsTestCase

from DateTime import DateTime
from collective.compoundcriterion.interfaces import ICompoundCriterionFilter
from zope.component import getAdapter


class testCustomSearches(MeetingMonsTestCase):

    def test_SearchBlockedItems(self):
        '''Test the 'items-of-my-groups' adapter that returns items using proposingGroup
           the current user is in.'''
        cfg = self.meetingConfig
        itemTypeName = cfg.getItemTypeName()

        adapter = getAdapter(cfg, ICompoundCriterionFilter, name='blocked-items')
        self.changeUser('siteadmin')

        datetime = adapter.query['modified']['query']

        self.assertEqual((DateTime() - 60).Date() , datetime.Date())

        self.assertEqual(adapter.query,
                         {'modified': {'query': datetime,
                                       'range': 'max'},
                          'portal_type': {'query': itemTypeName},
                          'review_state': {'query': ['itemcreated',
                                                     'proposed_to_budgetimpact_reviewer',
                                                     'proposed_to_extraordinarybudget',
                                                     'proposed_to_servicehead',
                                                     'proposed_to_officemanager',
                                                     'proposed_to_divisionhead',
                                                     'proposed_to_director']}})

