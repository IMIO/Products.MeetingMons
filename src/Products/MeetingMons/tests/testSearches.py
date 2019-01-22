# -*- coding: utf-8 -*-
#
# File: testMeetingConfig.py
#
# Copyright (c) 2015 by Imio.be
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
from Products.PloneMeeting.tests.testSearches import testSearches as pmts

from DateTime import DateTime
from Products.CMFCore.permissions import ModifyPortalContent
from collective.compoundcriterion.interfaces import ICompoundCriterionFilter
from imio.helpers.cache import cleanRamCacheFor
from zope.component import getAdapter


class testSearches(MeetingMonsTestCase, pmts):
    """Test searches."""

    def test_pm_SearchItemsToCorrect(self):
        '''Test the 'items-to-correct' CompoundCriterion adapter.  This should return
           a list of items in state 'returned_to_proposing_group' the current user is able to edit.'''
        # specify that copyGroups can see the item when it is proposed
        cfg = self.meetingConfig

        itemTypeName = cfg.getItemTypeName()
        self.changeUser('siteadmin')
        # first test the generated query
        adapter = getAdapter(cfg, ICompoundCriterionFilter, name='items-to-correct-mons')
        # wfAdaptation 'return_to_proposing_group' is not enabled
        self.assertEquals(adapter.query, {'review_state': {'query': ['unknown_review_state']}})

        self.changeUser('pmManager')
        cleanRamCacheFor('Products.MeetingMons.adapters.query_itemstocorrect')

        self.assertEquals(adapter.query, {
            'portal_type': {'query': itemTypeName},
            'reviewProcessInfo': {'query': ['developers__reviewprocess__itemcreated',
                                            'developers__reviewprocess__proposed_to_servicehead',
                                            'developers__reviewprocess__proposed_to_officemanager',
                                            'developers__reviewprocess__proposed_to_divisionhead',
                                            'developers__reviewprocess__proposed_to_director']},
            'toCorrect': {'query': True}})

        collection = cfg.searches.searches_items.searchitemstocorrect
        # it returns only items the current user is able to correct
        # create an item for developers and one for vendors and 'return' it to proposingGroup
        self.create('Meeting', date=DateTime())
        developersItem = self.create('MeetingItem')
        self.assertEquals(developersItem.getProposingGroup(), 'developers')
        cleanRamCacheFor('Products.MeetingMons.adapters.query_itemstocorrect')
        self.failIf(collection.getQuery())
        self.presentItem(developersItem)
        self.changeUser('pmCreator2')
        vendorsItem = self.create('MeetingItem')
        self.assertEquals(vendorsItem.getProposingGroup(), 'vendors')
        cleanRamCacheFor('Products.MeetingMons.adapters.query_itemstocorrect')
        self.failIf(collection.getQuery())

        self.changeUser('pmManager')
        self.presentItem(vendorsItem)

        cleanRamCacheFor('Products.MeetingMons.adapters.query_itemstocorrect')
        self.failIf(collection.getQuery())

        self.do(vendorsItem, 'backToValidated')
        self.changeUser('pmCreator2')
        cleanRamCacheFor('Products.MeetingMons.adapters.query_itemstocorrect')
        self.failIf(collection.getQuery())

        self.changeUser('pmManager')
        self.do(developersItem, 'backToValidated')
        self.changeUser('pmCreator1')
        cleanRamCacheFor('Products.MeetingMons.adapters.query_itemstocorrect')
        self.failIf(collection.getQuery())

        self.changeUser('pmManager')
        self.do(vendorsItem, 'backToItemCreated')
        self.changeUser('pmCreator2')
        # pmManager may only edit developersItem
        self.assertTrue(self.hasPermission(ModifyPortalContent, vendorsItem))
        cleanRamCacheFor('Products.MeetingMons.adapters.query_itemstocorrect')
        res = collection.getQuery()
        self.failUnless(len(res) == 1)
        self.failUnless(res[0].UID == vendorsItem.UID())

        self.changeUser('pmManager')
        self.do(developersItem, 'backToItemCreated')
        self.changeUser('pmCreator1')
        # pmManager may only edit developersItem
        self.assertTrue(self.hasPermission(ModifyPortalContent, developersItem))
        cleanRamCacheFor('Products.MeetingMons.adapters.query_itemstocorrect')
        res = collection.getQuery()
        self.failUnless(len(res) == 1)
        self.failUnless(res[0].UID == developersItem.UID())

    def test_pm_SearchCorrectedItemsMons(self):
        cfg = self.meetingConfig

        itemTypeName = cfg.getItemTypeName()
        self.changeUser('pmManager')
        # first test the generated query
        adapter = getAdapter(cfg, ICompoundCriterionFilter, name='corrected-items-mons')
        cleanRamCacheFor('Products.MeetingMons.adapters.query_correcteditems')
        self.assertEquals(adapter.query, {
            'corrected': {'query': True},
            'portal_type': {'query': itemTypeName}})

        collection = cfg.searches.searches_items.searchcorrecteditems
        meeting = self.create('Meeting', date=DateTime())
        recurring_item = meeting.getItems()[0]
        cleanRamCacheFor('Products.MeetingMons.adapters.query_correcteditems')
        res = collection.getQuery()
        self.failIf(res)
        self.do(recurring_item, 'backToValidated')
        cleanRamCacheFor('Products.MeetingMons.adapters.query_correcteditems')
        res = collection.getQuery()
        self.failIf(res)
        self.do(recurring_item, 'backToItemCreated')
        cleanRamCacheFor('Products.MeetingMons.adapters.query_correcteditems')
        res = collection.getQuery()
        self.failIf(res)
        self.do(recurring_item, 'proposeToServiceHead')
        cleanRamCacheFor('Products.MeetingMons.adapters.query_correcteditems')
        res = collection.getQuery()
        self.failIf(res)
        self.do(recurring_item, 'proposeToOfficeManager')
        cleanRamCacheFor('Products.MeetingMons.adapters.query_correcteditems')
        res = collection.getQuery()
        self.failIf(res)
        self.do(recurring_item, 'proposeToDivisionHead')
        cleanRamCacheFor('Products.MeetingMons.adapters.query_correcteditems')
        res = collection.getQuery()
        self.failIf(res)
        self.do(recurring_item, 'proposeToDirector')
        cleanRamCacheFor('Products.MeetingMons.adapters.query_correcteditems')
        res = collection.getQuery()
        self.failIf(res)
        self.do(recurring_item, 'validate')
        cleanRamCacheFor('Products.MeetingMons.adapters.query_correcteditems')
        res = collection.getQuery()
        self.assertEqual(len(res), 1)
        self.assertEqual(res[-1].UID, recurring_item.UID())
        self.do(recurring_item, 'present')
        cleanRamCacheFor('Products.MeetingMons.adapters.query_correcteditems')
        res = collection.getQuery()
        self.failIf(res)

        new_item = self.create('MeetingItem')
        cleanRamCacheFor('Products.MeetingMons.adapters.query_correcteditems')
        res = collection.getQuery()
        self.failIf(res)
        self.do(new_item, 'proposeToServiceHead')
        cleanRamCacheFor('Products.MeetingMons.adapters.query_correcteditems')
        res = collection.getQuery()
        self.failIf(res)
        self.do(new_item, 'proposeToOfficeManager')
        cleanRamCacheFor('Products.MeetingMons.adapters.query_correcteditems')
        res = collection.getQuery()
        self.failIf(res)
        self.do(new_item, 'proposeToDivisionHead')
        cleanRamCacheFor('Products.MeetingMons.adapters.query_correcteditems')
        res = collection.getQuery()
        self.failIf(res)
        self.do(new_item, 'proposeToDirector')
        cleanRamCacheFor('Products.MeetingMons.adapters.query_correcteditems')
        res = collection.getQuery()
        self.failIf(res)
        self.do(new_item, 'validate')
        cleanRamCacheFor('Products.MeetingMons.adapters.query_correcteditems')
        res = collection.getQuery()
        self.failIf(res)
        self.do(new_item, 'backToProposedToDirector')
        cleanRamCacheFor('Products.MeetingMons.adapters.query_correcteditems')
        res = collection.getQuery()
        self.failIf(res)
        self.do(new_item, 'validate')
        cleanRamCacheFor('Products.MeetingMons.adapters.query_correcteditems')
        res = collection.getQuery()
        self.assertEqual(len(res), 1)
        self.assertEqual(res[-1].UID, new_item.UID())
        self.do(new_item, 'backToProposedToDirector')
        cleanRamCacheFor('Products.MeetingMons.adapters.query_correcteditems')
        res = collection.getQuery()
        self.failIf(res)
        self.do(new_item, 'validate')
        cleanRamCacheFor('Products.MeetingMons.adapters.query_correcteditems')
        res = collection.getQuery()
        self.assertEqual(len(res), 1)
        self.assertEqual(res[-1].UID, new_item.UID())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testSearches, prefix='test_pm_'))
    return suite
