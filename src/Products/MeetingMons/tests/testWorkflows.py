# -*- coding: utf-8 -*-
#
# File: testWorkflows.py
#
# Copyright (c) 2007-2010 by PloneGov
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

from AccessControl import Unauthorized
from DateTime import DateTime
from Products.MeetingMons.tests.MeetingMonsTestCase import MeetingMonsTestCase
from Products.MeetingCommunes.tests.testWorkflows import testWorkflows as mctw


class testWorkflows(MeetingMonsTestCase, mctw):
    """Tests the default workflows implemented in MeetingMons.

       WARNING:
       The Plone test system seems to be bugged: it does not seem to take into
       account the write_permission and read_permission tags that are defined
       on some attributes of the Archetypes model. So when we need to check
       that a user is not authorized to set the value of a field protected
       in this way, we do not try to use the accessor to trigger an exception
       (self.assertRaise). Instead, we check that the user has the permission
       to do so (getSecurityManager().checkPermission)."""

    def test_subproduct_call_WholeDecisionProcess(self):
        """
            This test covers the whole decision workflow. It begins with the
            creation of some items, and ends by closing a meeting.
            This call 2 sub tests for each process : college and council
        """
        self._testWholeDecisionProcessCollege()
        self.setMeetingConfig(self.meetingConfig2.getId())

    def _testWholeDecisionProcessCollege(self):
        '''This test covers the whole decision workflow. It begins with the
           creation of some items, and ends by closing a meeting.'''
        # pmCreator1 creates an item with 1 annex and proposes it
        self.changeUser('pmCreator1')
        item1 = self.create('MeetingItem', title='The first item')
        annex1 = self.addAnnex(item1)
        self.addAnnex(item1, relatedTo='item_decision')
        self.do(item1, 'proposeToServiceHead')
        self.assertRaises(Unauthorized, self.addAnnex, item1, relatedTo='item_decision')
        self.failIf(self.transitions(item1))  # He may trigger no more action
        self.failIf(self.hasPermission('PloneMeeting: Add annex', item1))
        # the ServiceHead validation level
        self.changeUser('pmServiceHead1')
        self.failUnless(self.hasPermission('Modify portal content', (item1, annex1)))
        self.do(item1, 'proposeToOfficeManager')
        self.assertRaises(Unauthorized, self.addAnnex, item1, relatedTo='item_decision')
        self.failIf(self.transitions(item1))  # He may trigger no more action
        self.failIf(self.hasPermission('PloneMeeting: Add annex', item1))
        # the OfficeManager validation level
        self.changeUser('pmOfficeManager1')
        self.failUnless(self.hasPermission('Modify portal content', (item1, annex1)))
        self.do(item1, 'proposeToDivisionHead')
        self.assertRaises(Unauthorized, self.addAnnex, item1, relatedTo='item_decision')
        self.failIf(self.transitions(item1))  # He may trigger no more action
        self.failIf(self.hasPermission('PloneMeeting: Add annex', item1))
        # the DivisionHead validation level
        self.changeUser('pmDivisionHead1')
        self.failUnless(self.hasPermission('Modify portal content', (item1, annex1)))
        self.do(item1, 'proposeToDirector')
        self.assertRaises(Unauthorized, self.addAnnex, item1, relatedTo='item_decision')
        # The division Head can't modify items
        self.failIf(self.hasPermission('Modify portal content', (item1, annex1)))
        self.failIf(self.hasPermission('PloneMeeting: Add annex', item1))
        # the Director validation level
        self.changeUser('pmDirector1')
        self.failUnless(self.hasPermission('Modify portal content', (item1, annex1)))
        self.do(item1, 'validate')
        self.assertRaises(Unauthorized, self.addAnnex, item1, relatedTo='item_decision')
        self.failIf(self.transitions(item1))  # He may trigger no more action
        self.failIf(self.hasPermission('PloneMeeting: Add annex', item1))
        # pmManager creates a meeting
        self.changeUser('pmManager')
        meeting = self.create('Meeting', date='2007/12/11 09:00:00')
        self.addAnnex(item1, relatedTo='item_decision')
        # pmCreator2 creates and proposes an item
        self.changeUser('pmCreator2')
        item2 = self.create('MeetingItem', title='The second item',
                            preferredMeeting=meeting.UID())
        self.do(item2, 'proposeToServiceHead')
        # pmReviewer1 can not validate the item has not in the same proposing group
        self.changeUser('pmReviewer1')
        self.failIf(self.hasPermission('Modify portal content', item2))
        # even pmManagercan not see/validate an item in the validation queue
        self.changeUser('pmManager')
        self.failIf(self.hasPermission('Modify portal content', item2))
        # do the complete validation
        self.changeUser('admin')
        self.do(item2, 'proposeToOfficeManager')
        self.do(item2, 'proposeToDivisionHead')
        self.do(item2, 'proposeToDirector')
        # pmManager inserts item1 into the meeting but can't delete this (only manager can)
        managerAnnex = self.addAnnex(item1)
        self.changeUser('pmManager')
        self.portal.restrictedTraverse('@@delete_givenuid')(managerAnnex.UID())
        self.do(item1, 'present')
        # Now reviewers can't add annexes anymore
        self.changeUser('pmDirector1')
        self.assertRaises(Unauthorized, self.addAnnex, item2)
        # freeze the meeting
        self.changeUser('pmManager')
        self.do(meeting, 'freeze')
        # validate item2 after meeting freeze
        self.changeUser('pmReviewer2')
        self.do(item2, 'validate')
        self.changeUser('pmManager')
        self.do(item2, 'present')
        self.addAnnex(item2)
        # So now we should have 1 normal item and 2 recurring items; 1 late item in the meeting
        self.failUnless(len(meeting.getItems()) == 3)
        self.failUnless(len(meeting.getLateItems()) == 1)
        self.do(meeting, 'decide')
        self.do(item1, 'refuse')
        self.assertEquals(item1.queryState(), 'refused')
        self.assertEquals(item2.queryState(), 'itemfrozen')
        # every items without a decision are automatically accepted
        self.do(meeting, 'close')
        self.assertEquals(item2.queryState(), 'accepted')
        self.assertEquals(item1.queryState(), 'refused')

    def test_subproduct_FreezeMeeting(self):
        """
           When we freeze a meeting, every presented items will be frozen
           too and their state will be set to 'itemfrozen'.  When the meeting
           come back to 'created', every items will be corrected and set in the
           'presented' state
        """
        # First, define recurring items in the meeting config
        self.changeUser('pmManager')
        #create a meeting
        meeting = self.create('Meeting', date='2007/12/11 09:00:00')
        #create 2 items and present them to the meeting
        item1 = self.create('MeetingItem', title='The first item')
        item2 = self.create('MeetingItem', title='The second item')
        for item in (item1, item2,):
            self.presentItem(item)
        wftool = self.portal.portal_workflow
        #every presented items are in the 'presented' state
        self.assertEquals('presented', wftool.getInfoFor(item1, 'review_state'))
        self.assertEquals('presented', wftool.getInfoFor(item2, 'review_state'))
        #every items must be in the 'itemfrozen' state if we freeze the meeting
        self.do(meeting, 'freeze')
        self.assertEquals('itemfrozen', wftool.getInfoFor(item1, 'review_state'))
        self.assertEquals('itemfrozen', wftool.getInfoFor(item2, 'review_state'))
        #when correcting the meeting back to created, the items must be corrected
        #back to "presented"
        self.do(meeting, 'backToCreated')
        #when a point is in 'itemfrozen' it's must place in presented state
        self.assertEquals('presented', wftool.getInfoFor(item1, 'review_state'))
        self.assertEquals('presented', wftool.getInfoFor(item2, 'review_state'))

    def test_subproduct_CloseMeeting(self):
        """
           When we close a meeting, every items are set to accepted if they are still
           not decided...
        """
        # First, define recurring items in the meeting config
        self.changeUser('pmManager')
        #create a meeting (with 7 items)
        meetingDate = DateTime().strftime('%y/%m/%d %H:%M:00')
        meeting = self.create('Meeting', date=meetingDate)
        item1 = self.create('MeetingItem')  # id=o2
        item1.setProposingGroup('vendors')
        item1.setAssociatedGroups(('developers',))
        item2 = self.create('MeetingItem')  # id=o3
        item2.setProposingGroup('developers')
        item3 = self.create('MeetingItem')  # id=o4
        item3.setProposingGroup('vendors')
        item4 = self.create('MeetingItem')  # id=o5
        item4.setProposingGroup('developers')
        item5 = self.create('MeetingItem')  # id=o7
        item5.setProposingGroup('vendors')
        item6 = self.create('MeetingItem', title='The sixth item')
        item6.setProposingGroup('vendors')
        item7 = self.create('MeetingItem')  # id=o8
        item7.setProposingGroup('vendors')
        for item in (item1, item2, item3, item4, item5, item6, item7):
            self.presentItem(item)
        #we freeze the meeting
        self.do(meeting, 'freeze')
        #a MeetingManager can put the item back to presented
        self.do(item7, 'backToPresented')
        #we decide the meeting
        #while deciding the meeting, every items that where presented are frozen
        self.do(meeting, 'decide')
        #change all items in all different state (except first who is in good state)
        self.do(item7, 'backToPresented')
        self.do(item2, 'delay')
        self.do(item3, 'pre_accept')
        self.do(item4, 'accept_but_modify')
        self.do(item5, 'refuse')
        self.do(item6, 'accept')
        #we close the meeting
        self.do(meeting, 'close')
        #every items must be in the 'decided' state if we close the meeting
        wftool = self.portal.portal_workflow
        #itemfrozen change into accepted
        self.assertEquals('accepted', wftool.getInfoFor(item1, 'review_state'))
        #delayed rest delayed (it's already a 'decide' state)
        self.assertEquals('delayed', wftool.getInfoFor(item2, 'review_state'))
        #pre_accepted change into accepted
        self.assertEquals('accepted', wftool.getInfoFor(item3, 'review_state'))
        #accepted_but_modified rest accepted_but_modified (it's already a 'decide' state)
        self.assertEquals('accepted_but_modified', wftool.getInfoFor(item4, 'review_state'))
        #refused rest refused (it's already a 'decide' state)
        self.assertEquals('refused', wftool.getInfoFor(item5, 'review_state'))
        #accepted rest accepted (it's already a 'decide' state)
        self.assertEquals('accepted', wftool.getInfoFor(item6, 'review_state'))
        #presented change into accepted
        self.assertEquals('accepted', wftool.getInfoFor(item7, 'review_state'))

    def test_subproduct_call_RecurringItemsRespectSortingMethodOnAddItemPrivacy(self):
            '''No sense...'''
            pass

    def test_subproduct_call_RemoveObjects(self):
        """
            Tests objects removal (items, meetings, annexes...).
        """
        #we do the test for the college config
        self.meetingConfig = getattr(self.tool, 'meeting-config-college')
        self._RemoveObjects()

    def _RemoveObjects(self):
        '''Tests objects removal (items, meetings, annexes...).'''
        # Create an item with annexes
        self.changeUser('pmCreator1')
        item = self.create('MeetingItem')
        parentFolder = item.getParentNode()
        #test that we can remove an empty item...
        self.portal.restrictedTraverse('@@delete_givenuid')(item.UID())
        self.failIf(len(parentFolder.objectValues()) != 0)
        #test removal of an item with annexes
        item = self.create('MeetingItem')
        annex1 = self.addAnnex(item)
        self.changeUser('pmCreator1b')
        annex2 = self.addAnnex(item)
        self.failIf(len(item.objectValues()) != 2)
        self.changeUser('pmCreator1')
        self.portal.restrictedTraverse('@@delete_givenuid')(annex2.UID())
        self.failIf(len(item.objectValues()) != 1)
        # Propose the item
        self.do(item, item.wfConditions().transitionsForPresentingAnItem[0])
        # Remove the item with annexes
        self.changeUser('pmCreator1b')
        # Check that now MeetingMember(s) can't remove the item anymore
        self.assertRaises(Unauthorized, self.portal.restrictedTraverse('@@delete_givenuid'), item.UID())
        # a manager can't remove the item
        self.changeUser('pmManager')
        self.portal.restrictedTraverse('@@delete_givenuid')(annex1.UID())
        self.assertRaises(Unauthorized, self.portal.restrictedTraverse('@@delete_givenuid'), item.UID())
        self.failIf(len(parentFolder.objectValues()) != 1)
        # but super user (admin) could
        self.changeUser('admin')
        self.portal.restrictedTraverse('@@delete_givenuid')(item.UID())
        self.failIf(len(parentFolder.objectValues()) != 0)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testWorkflows, prefix='test_subproduct_'))
    return suite
