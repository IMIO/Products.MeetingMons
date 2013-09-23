# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Copyright (c) 2011 by CommunesPlone.org
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
# ------------------------------------------------------------------------------
import re
from DateTime import DateTime
from appy.gen import No
from appy.gen.utils import Keywords
from AccessControl import getSecurityManager, ClassSecurityInfo
from Globals import InitializeClass
from zope.interface import implements
from Products.CMFCore.permissions import ReviewPortalContent, ModifyPortalContent, View
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.atapi import DisplayList
from Products.PloneMeeting.MeetingItem import MeetingItem, \
    MeetingItemWorkflowConditions, MeetingItemWorkflowActions
from Products.PloneMeeting.utils import checkPermission, sendMail, getLastEvent, spanifyLink
from Products.PloneMeeting.config import ITEM_NO_PREFERRED_MEETING_VALUE
from Products.PloneMeeting.Meeting import MeetingWorkflowActions, \
    MeetingWorkflowConditions, Meeting
from Products.PloneMeeting.MeetingConfig import MeetingConfig
from Products.PloneMeeting.ToolPloneMeeting import ToolPloneMeeting
from Products.PloneMeeting.MeetingGroup import MeetingGroup
from Products.PloneMeeting.interfaces import IMeetingCustom, IMeetingItemCustom, \
    IMeetingConfigCustom, IMeetingGroupCustom, IToolPloneMeetingCustom
from Products.MeetingMons.interfaces import \
    IMeetingItemCollegeMonsWorkflowConditions, IMeetingItemCollegeMonsWorkflowActions,\
    IMeetingCollegeMonsWorkflowConditions, IMeetingCollegeMonsWorkflowActions, \
    IMeetingItemCouncilMonsWorkflowConditions, IMeetingItemCouncilMonsWorkflowActions,\
    IMeetingCouncilMonsWorkflowConditions, IMeetingCouncilMonsWorkflowActions
from Products.PloneMeeting import PloneMeetingError
from Products.MeetingMons.config import COUNCIL_COMMISSION_IDS


class CustomMeeting(Meeting):
    '''Adapter that adapts a meeting implementing IMeeting to the
       interface IMeetingCustom.'''

    implements(IMeetingCustom)
    security = ClassSecurityInfo()

    def __init__(self, item):
        self.context = item

    # Implements here methods that will be used by templates
    security.declarePublic('getItemsInOrder')
    def getItemsInOrder(self, itemuids, late=False, toDiscuss=True):
        ''' Return a list of items, depending of todiscuss state'''
        res = []
        items = self.getSelf().getItemsInOrder(late=late, uids=itemuids)
        for item in items:
            if item.getToDiscuss() == toDiscuss:
                res.append(item)
        return res

    security.declarePublic('getPrintableItems')
    def getPrintableItems(self, itemUids, late=False, ignore_review_states=[],
                          privacy='*', oralQuestion='both', categories=[],
                          excludedCategories=[], firstNumber=1, renumber=False):
        '''Returns a list of items.
           An extra list of review states to ignore can be defined.
           A privacy can also be given, and the fact that the item is an
           oralQuestion or not (or both).
           Some specific categories can be given or some categories to exchude.
           These 2 parameters are exclusive.  If renumber is True, a list of tuple
           will be returned with first element the number and second element, the item.
           In this case, the firstNumber value can be used.'''
        # We just filter ignore_review_states here and privacy and call
        # getItemsInOrder(uids), passing the correct uids and removing empty
        # uids.
        # privacy can be '*' or 'public' or 'secret'
        # oralQuestion can be 'both' or False or True
        for elt in itemUids:
            if elt == '':
                itemUids.remove(elt)
        #no filtering, returns the items ordered
        if not categories and not ignore_review_states and privacy == '*' and oralQuestion == 'both':
            return self.context.getItemsInOrder(late=late, uids=itemUids)
        # Either, we will have to filter the state here and check privacy
        filteredItemUids = []
        uid_catalog = self.context.uid_catalog
        for itemUid in itemUids:
            obj = uid_catalog(UID=itemUid)[0].getObject()
            if obj.queryState() in ignore_review_states:
                continue
            elif not (privacy == '*' or obj.getPrivacy() == privacy):
                continue
            elif not (oralQuestion == 'both' or obj.getOralQuestion() == oralQuestion):
                continue
            elif categories and not obj.getCategory() in categories:
                continue
            elif excludedCategories and obj.getCategory() in excludedCategories:
                continue
            filteredItemUids.append(itemUid)
        #in case we do not have anything, we return an empty list
        if not filteredItemUids:
            return []
        else:
            items = self.context.getItemsInOrder(late=late, uids=filteredItemUids)
            if renumber:
                #returns a list of tuple with first element the number
                #and second element the item itself
                i = firstNumber
                res = []
                for item in items:
                    res.append((i, item))
                    i = i + 1
                items = res
            return items

    security.declarePublic('getAvailableItems')
    def getAvailableItems(self):
        '''Items are available to the meeting no matter the meeting state (except 'closed').
           In the 'created' state, every validated items are availble, in other states, only items
           for wich the specific meeting is selected as preferred will appear.'''
        meeting = self.getSelf()
        if meeting.queryState() not in ('created', 'frozen', 'in_committee', 'in_council', 'decided'):
            return []
        meetingConfig = meeting.portal_plonemeeting.getMeetingConfig(meeting)
        # First, get meetings accepting items for which the date is lower or
        # equal to the date of this meeting (self)
        meetings = meeting.portal_catalog(
            portal_type=meetingConfig.getMeetingTypeName(),
            getDate={'query': meeting.getDate(), 'range': 'max'},)
        meetingUids = [b.getObject().UID() for b in meetings]
        # if the meeting is 'in_committee' or 'in_council'
        # we only accept items for wich the preferredMeeting is the current meeting
        if not meeting.queryState() in ('in_committee', 'in_council', ):
            meetingUids.append(ITEM_NO_PREFERRED_MEETING_VALUE)
        # Then, get the items whose preferred meeting is None or is among
        # those meetings.
        itemsUids = meeting.portal_catalog(
            portal_type=meetingConfig.getItemTypeName(),
            review_state='validated',
            getPreferredMeeting=meetingUids,
            sort_on="modified")
        if meeting.queryState() in ('frozen', 'decided'):
            # Oups. I can only take items which are "late" items.
            res = []
            for uid in itemsUids:
                if uid.getObject().wfConditions().isLateFor(meeting):
                    res.append(uid)
        else:
            res = itemsUids
        return res

    #helper methods used in templates
    security.declarePublic('getNormalCategories')
    def getNormalCategories(self):
        '''Returns the 'normal' categories'''
        mc = self.portal_plonemeeting.getMeetingConfig(self)
        categories = mc.getCategories(onlySelectables=False)
        res = []
        firstSupplCatIds = self.getFirstSupplCategories()
        secondSupplCatIds = self.getSecondSupplCategories()
        thirdSupplCatIds = self.getThirdSupplCategories()
        for cat in categories:
            catId = cat.getId()
            if not catId in firstSupplCatIds and \
               not catId in secondSupplCatIds and \
               not catId in thirdSupplCatIds:
                res.append(catId)
        return res
    Meeting.getNormalCategories = getNormalCategories

    security.declarePublic('getFirstSupplCategories')
    def getFirstSupplCategories(self):
        '''Returns the '1er-supplement' categories'''
        mc = self.portal_plonemeeting.getMeetingConfig(self)
        categories = mc.getCategories(onlySelectables=False)
        res = []
        for cat in categories:
            catId = cat.getId()
            if catId.endswith('1er-supplement'):
                res.append(catId)
        return res
    Meeting.getFirstSupplCategories = getFirstSupplCategories

    security.declarePublic('getSecondSupplCategories')
    def getSecondSupplCategories(self):
        '''Returns the '2eme-supplement' categories'''
        mc = self.portal_plonemeeting.getMeetingConfig(self)
        categories = mc.getCategories(onlySelectables=False)
        res = []
        for cat in categories:
            catId = cat.getId()
            if catId.endswith('2eme-supplement'):
                res.append(catId)
        return res
    Meeting.getSecondSupplCategories = getSecondSupplCategories

    security.declarePublic('getThirdSupplCategories')
    def getThirdSupplCategories(self):
        '''Returns the '3eme-supplement' categories'''
        mc = self.portal_plonemeeting.getMeetingConfig(self)
        categories = mc.getCategories(onlySelectables=False)
        res = []
        for cat in categories:
            catId = cat.getId()
            if catId.endswith('3eme-supplement'):
                res.append(catId)
        return res
    Meeting.getThirdSupplCategories = getThirdSupplCategories

    security.declarePublic('getNumberOfItems')
    def getNumberOfItems(self, itemUids, privacy='*', categories=[], late=False):
        '''Returns the number of items depending on parameters.
           This is used in templates'''
        for elt in itemUids:
            if elt == '':
                itemUids.remove(elt)
        #no filtering, return the items ordered
        if not categories and privacy == '*':
            return self.getItemsInOrder(late=late, uids=itemUids)
        # Either, we will have to filter the state here and check privacy
        filteredItemUids = []
        uid_catalog = self.uid_catalog
        for itemUid in itemUids:
            obj = uid_catalog(UID=itemUid)[0].getObject()
            if not (privacy == '*' or obj.getPrivacy() == privacy):
                continue
            elif not (categories == [] or obj.getCategory() in categories):
                continue
            filteredItemUids.append(itemUid)
        return len(filteredItemUids)
    Meeting.getNumberOfItems = getNumberOfItems

    def getItemsFirstSuppl(self, itemUids, privacy='public'):
        '''Returns the items presented as first supplement'''
        normalCategories = self.getNormalCategories()
        firstSupplCategories = self.getFirstSupplCategories()
        firstNumber = self.getNumberOfItems(itemUids, privacy=privacy, categories=normalCategories) + 1
        return self.adapted().getPrintableItems(itemUids,
                                                privacy=privacy,
                                                categories=firstSupplCategories,
                                                firstNumber=firstNumber,
                                                renumber=True)
    Meeting.getItemsFirstSuppl = getItemsFirstSuppl

    def getItemsSecondSuppl(self, itemUids, privacy='public'):
        '''Returns the items presented as second supplement'''
        normalCategories = self.getNormalCategories()
        firstSupplCategories = self.getFirstSupplCategories()
        secondSupplCategories = self.getSecondSupplCategories()
        firstNumber = self.getNumberOfItems(itemUids, privacy=privacy,
                                            categories=normalCategories+firstSupplCategories) + 1
        return self.adapted().getPrintableItems(itemUids,
                                                privacy=privacy,
                                                categories=secondSupplCategories,
                                                firstNumber=firstNumber,
                                                renumber=True)
    Meeting.getItemsSecondSuppl = getItemsSecondSuppl

    def getItemsThirdSuppl(self, itemUids, privacy='public'):
        '''Returns the items presented as third supplement'''
        normalCategories = self.getNormalCategories()
        firstSupplCategories = self.getFirstSupplCategories()
        secondSupplCategories = self.getSecondSupplCategories()
        thirdSupplCategories = self.getThirdSupplCategories()
        firstNumber = self.getNumberOfItems(itemUids,
                                            privacy=privacy,
                                            categories=normalCategories+firstSupplCategories+secondSupplCategories) + 1
        return self.adapted().getPrintableItems(itemUids,
                                                privacy=privacy,
                                                categories=thirdSupplCategories,
                                                firstNumber=firstNumber,
                                                renumber=True)
    Meeting.getItemsThirdSuppl = getItemsThirdSuppl

    security.declarePublic('getLabelDescription')
    def getLabelDescription(self):
        '''Returns the label to use for field MeetingItem.description
          The label is different between college and council'''
        if self.portal_type == 'MeetingItemCouncil':
            return self.utranslate("MeetingMons_label_councildescription", domain="PloneMeeting")
        else:
            return self.utranslate("PloneMeeting_label_description", domain="PloneMeeting")
    MeetingItem.getLabelDescription = getLabelDescription

    security.declarePublic('getLabelDecision')
    def getLabelDecision(self):
        '''Returns the label to use for field MeetingItem.decision
          The label is different between college and council'''
        if self.portal_type == 'MeetingItemCouncil':
            return self.utranslate("MeetingMons_label_councildecision", domain="PloneMeeting")
        else:
            return self.utranslate("PloneMeeting_label_decision", domain="PloneMeeting")
    MeetingItem.getLabelDecision = getLabelDecision

    security.declarePublic('getLabelCategory')
    def getLabelCategory(self):
        '''Returns the label to use for field MeetingItem.category
          The label is different between college and council'''
        if self.portal_type == 'MeetingItemCouncil':
            return self.utranslate("MeetingMons_label_councilcategory", domain="PloneMeeting")
        else:
            return self.utranslate("PloneMeeting_label_category", domain="PloneMeeting")
    MeetingItem.getLabelCategory = getLabelCategory

    security.declarePublic('getLabelObservations')
    def getLabelObservations(self):
        '''Returns the label to use for field Meeting.observations
           The label is different between college and council'''
        if self.portal_type == 'MeetingCouncil':
            return self.utranslate("MeetingMons_label_meetingcouncilobservations", domain="PloneMeeting")
        else:
            return self.utranslate("PloneMeeting_label_meetingObservations", domain="PloneMeeting")
    Meeting.getLabelObservations = getLabelObservations

    security.declarePublic('getCommissionTitle')
    def getCommissionTitle(self, commissionNumber=1):
        '''
          Given a commissionNumber, return the commission title depending on corresponding categories
        '''
        meeting = self.getSelf()
        commissionCategories = meeting.getCommissionCategories()
        if not len(commissionCategories) >= commissionNumber:
            return ''
        commissionCat = commissionCategories[commissionNumber-1]
        # build title
        if isinstance(commissionCat, tuple):
            res = 'Commission ' + '/'.join([subcat.Title().replace('Commission ', '') for subcat in commissionCat])
        else:
            res = commissionCat.Title()
        return res

    security.declarePublic('getCommissionCategories')
    def getCommissionCategories(self, theObjects=False):
        '''Returns the list of categories used for Commissions'''
        mc = self.portal_plonemeeting.getMeetingConfig(self)
        categories = mc.getCategories()
        commissionCategoryIds = COUNCIL_COMMISSION_IDS

        if not theObjects:
            return commissionCategoryIds
        res = []
        for category in categories:
            if category.getId() in commissionCategoryIds:
                res.append(category)
        return res

    Meeting.getCommissionCategories = getCommissionCategories

    security.declarePublic('getStrikedAssembly')
    def getStrikedAssembly(self):
        '''The text between [[xxx]] is striked. Used to mark absents.
           You can define mltAssembly to customize your assembly (bold, italics, ...).'''
        return self.getStrikedField(self.context.getAssembly())

    security.declarePublic('showAllItemsAtOnce')
    def showAllItemsAtOnce(self):
        """
          Monkeypatch for hiding the allItemsAtOnce field
        """
        return False
    Meeting.showAllItemsAtOnce = showAllItemsAtOnce

    security.declarePrivate('validate_preMeetingDate')
    def validate_preMeetingDate(self, value):
        '''Checks that the preMeetingDate comes before the meeting date.'''
        if not value:
            return
        # Get the meeting date from the request
        try:
            meetingDate = DateTime(self.REQUEST['date'])
        except DateTime.DateError:
            meetingDate = None
        except DateTime.SyntaxError:
            meetingDate = None
        # Compare meeting and pre-meeting dates
        if meetingDate and (DateTime(value) >= meetingDate):
            label = 'pre_date_after_meeting_date'
            return self.utranslate(label, domain='PloneMeeting')
    Meeting.validate_preMeetingDate = validate_preMeetingDate

    security.declarePrivate('getDefaultPreMeetingAssembly')
    def getDefaultPreMeetingAssembly(self):
        '''Returns the default value for field 'preMeetingAssembly.'''
        if self.attributeIsUsed('preMeetingAssembly'):
            return self.portal_plonemeeting.getMeetingConfig(self).getPreMeetingAssembly_default()
        return ''
    Meeting.getDefaultPreMeetingAssembly = getDefaultPreMeetingAssembly

    security.declarePrivate('getDefaultPreMeetingAssembly_2')
    def getDefaultPreMeetingAssembly_2(self):
        '''Returns the default value for field 'preMeetingAssembly.'''
        if self.attributeIsUsed('preMeetingAssembly'):
            return self.portal_plonemeeting.getMeetingConfig(self).getPreMeetingAssembly_2_default()
        return ''
    Meeting.getDefaultPreMeetingAssembly_2 = getDefaultPreMeetingAssembly_2

    security.declarePrivate('getDefaultPreMeetingAssembly_3')
    def getDefaultPreMeetingAssembly_3(self):
        '''Returns the default value for field 'preMeetingAssembly.'''
        if self.attributeIsUsed('preMeetingAssembly'):
            return self.portal_plonemeeting.getMeetingConfig(self).getPreMeetingAssembly_3_default()
        return ''
    Meeting.getDefaultPreMeetingAssembly_3 = getDefaultPreMeetingAssembly_3

    security.declarePrivate('getDefaultPreMeetingAssembly_4')
    def getDefaultPreMeetingAssembly_4(self):
        '''Returns the default value for field 'preMeetingAssembly.'''
        if self.attributeIsUsed('preMeetingAssembly'):
            return self.portal_plonemeeting.getMeetingConfig(self).getPreMeetingAssembly_4_default()
        return ''
    Meeting.getDefaultPreMeetingAssembly_4 = getDefaultPreMeetingAssembly_4

    security.declarePrivate('getDefaultPreMeetingAssembly_5')
    def getDefaultPreMeetingAssembly_5(self):
        '''Returns the default value for field 'preMeetingAssembly.'''
        if self.attributeIsUsed('preMeetingAssembly'):
            return self.portal_plonemeeting.getMeetingConfig(self).getPreMeetingAssembly_5_default()
        return ''
    Meeting.getDefaultPreMeetingAssembly_5 = getDefaultPreMeetingAssembly_5

    security.declarePrivate('getDefaultPreMeetingAssembly_6')
    def getDefaultPreMeetingAssembly_6(self):
        '''Returns the default value for field 'preMeetingAssembly.'''
        if self.attributeIsUsed('preMeetingAssembly'):
            return self.portal_plonemeeting.getMeetingConfig(self).getPreMeetingAssembly_6_default()
        return ''
    Meeting.getDefaultPreMeetingAssembly_6 = getDefaultPreMeetingAssembly_6

    security.declarePrivate('getDefaultPreMeetingAssembly_7')
    def getDefaultPreMeetingAssembly_7(self):
        '''Returns the default value for field 'preMeetingAssembly.'''
        if self.attributeIsUsed('preMeetingAssembly'):
            return self.portal_plonemeeting.getMeetingConfig(self).getPreMeetingAssembly_7_default()
        return ''
    Meeting.getDefaultPreMeetingAssembly_7 = getDefaultPreMeetingAssembly_7

    security.declarePublic('isDecided')
    def isDecided(self):
        meeting = self.getSelf()
        return meeting.queryState() in ('published', 'closed')


# ------------------------------------------------------------------------------
class CustomMeetingItem(MeetingItem):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingItemCustom.'''
    implements(IMeetingItemCustom)
    security = ClassSecurityInfo()

    customItemPositiveDecidedStates = ('accepted', 'accepted_but_modified', )
    MeetingItem.itemPositiveDecidedStates = customItemPositiveDecidedStates
    customItemDecidedStates = ('accepted', 'refused', 'delayed', 'accepted_but_modified', 'removed', )
    MeetingItem.itemDecidedStates = customItemDecidedStates
    customBeforePublicationStates = ('itemcreated',
                                     'proposed_to_servicehead',
                                     'proposed_to_officemanager',
                                     'proposed_to_divisionhead',
                                     'proposed_to_director',
                                     'validated', )
    MeetingItem.beforePublicationStates = customBeforePublicationStates
    #this list is used by doPresent defined in PloneMeeting
    #for the Council, there is no "frozen" functionnality
    customMeetingAlreadyFrozenStates = ('frozen', 'decided', )
    MeetingItem.meetingAlreadyFrozenStates = customMeetingAlreadyFrozenStates

    customMeetingNotClosedStates = ('frozen', 'in_committee', 'in_council', 'decided', )
    MeetingItem.meetingNotClosedStates = customMeetingNotClosedStates

    customMeetingTransitionsAcceptingRecurringItems = ('_init_', 'freeze', 'setInCommittee', 'setInCouncil', )
    MeetingItem.meetingTransitionsAcceptingRecurringItems = customMeetingTransitionsAcceptingRecurringItems

    def __init__(self, item):
        self.context = item

    security.declarePublic('listFollowUps')
    def listFollowUps(self):
        '''List available values for vocabulary of the 'followUp' field.'''
        d = 'PloneMeeting'
        u = self.utranslate
        res = DisplayList((
            ("follow_up_no", u('follow_up_no', domain=d)),
            ("follow_up_yes", u('follow_up_yes', domain=d)),
            ("follow_up_provided", u('follow_up_provided', domain=d)),
            ("follow_up_provided_not_printed", u('follow_up_provided_not_printed', domain=d)),
        ))
        return res
    MeetingItem.listFollowUps = listFollowUps

    security.declarePublic('mayBeLinkedToTasks')
    def mayBeLinkedToTasks(self):
        '''See doc in interfaces.py.'''
        item = self.getSelf()
        res = False
        if (item.queryState() in ('accepted', 'refused', 'delayed', 'accepted_but_modified', )):
            res = True
        return res

    def getMeetingDate(self):
        '''Returns the meeting date if any (used for portal_catalog metadata getMeetingDate).'''
        if not self.portal_type in ['MeetingItemCollege', 'MeetingItemCouncil', ]:
            return ''
        else:
            return self.hasMeeting() and self.getMeeting().getDate() or ''
    MeetingItem.getMeetingDate = getMeetingDate

    security.declarePublic('activateFollowUp')
    def activateFollowUp(self):
        '''Activate follow-up by setting followUp to 'follow_up_yes'.'''
        self.setFollowUp('follow_up_yes')
        #initialize the neededFollowUp field with the available content of the 'decision' field
        if not self.getNeededFollowUp():
            self.setNeededFollowUp(self.getDecision())
        self.reindexObject(idxs=['getFollowUp', ])
        return self.REQUEST.RESPONSE.redirect(self.absolute_url() + '#followup')
    MeetingItem.activateFollowUp = activateFollowUp

    security.declarePublic('deactivateFollowUp')
    def deactivateFollowUp(self):
        '''Deactivate follow-up by setting followUp to 'follow_up_no'.'''
        self.setFollowUp('follow_up_no')
        self.reindexObject(idxs=['getFollowUp', ])
        return self.REQUEST.RESPONSE.redirect(self.absolute_url() + '#followup')
    MeetingItem.deactivateFollowUp = deactivateFollowUp

    security.declarePublic('confirmFollowUp')
    def confirmFollowUp(self):
        '''Confirm follow-up by setting followUp to 'follow_up_provided'.'''
        self.setFollowUp('follow_up_provided')
        self.reindexObject(idxs=['getFollowUp', ])
        return self.REQUEST.RESPONSE.redirect(self.absolute_url() + '#followup')
    MeetingItem.confirmFollowUp = confirmFollowUp

    security.declarePublic('followUpNotPrinted')
    def followUpNotPrinted(self):
        '''While follow-up is confirmed, we may specify that we do not want it printed in the dashboard.'''
        self.setFollowUp('follow_up_provided_not_printed')
        self.reindexObject(idxs=['getFollowUp', ])
        return self.REQUEST.RESPONSE.redirect(self.absolute_url() + '#followup')
    MeetingItem.followUpNotPrinted = followUpNotPrinted

    security.declarePublic('onDuplicatedFromConfig')
    def onDuplicatedFromConfig(self, usage):
        '''Hook when a recurring item is added to a meeting'''
        # Recurring items added when the meeting is 'in_council' need
        # to be set in council also.  By default they are just 'presented'
        if not self.context.portal_type == 'MeetingItemCouncil':
            return
        if usage == 'as_recurring_item' and self.context.getMeeting().queryState() == 'in_committee':
            item = self.getSelf()
            if item.queryState() == 'presented':
                self.context.portal_workflow.doActionFor(item, 'setItemInCommittee')
            if item.queryState() == 'item_in_committee':
                self.context.portal_workflow.doActionFor(item, 'setItemInCouncil')

    security.declarePublic('onDuplicated')
    def onDuplicated(self, original):
        '''Hook when a item is duplicated (called by MeetingItem.clone).'''
        # while an item is cloned to the meeting-config-council,
        # add the council specific 'motivation' at the top of existing 'motivation'
        item = self.getSelf()
        # only apply if we are actually creating a MeetingItemCouncil from another MeetingConfig
        if not (item.portal_type == 'MeetingItemCouncil' and original.portal_type != 'MeetingItemCouncil'):
            return
        existingMotivation = item.getMotivation()
        defaultCouncilMotivation = item.Schema()['motivation'].getDefault(item)
        item.setMotivation(defaultCouncilMotivation + '<p>&nbsp;</p><p>&nbsp;</p>' + existingMotivation)

    security.declarePublic('getCertifiedSignatures')
    def getCertifiedSignatures(self):
        '''Returns certified signatures taking delegations into account.'''
        tool = getToolByName(self, 'portal_plonemeeting')
        mc = tool.getMeetingConfig(self)
        globalCertifiedSignatures = mc.getCertifiedSignatures().split('\n')
        # we need to return 6 values but by default, certifiedSignatures contains 4 values...
        if len(globalCertifiedSignatures) == 4:
            globalCertifiedSignatures = globalCertifiedSignatures[0:1] + ['', ] + \
                globalCertifiedSignatures[1:3] + ['', ] + globalCertifiedSignatures[3:4]
        specificSignatures = self.getProposingGroup(theObject=True).getSignatures().split('\n')
        specificSignaturesLength = len(specificSignatures)
        # just take specific/delegation signatures into account if there are 3 (just redefined the first signatory)
        #or 6 (redefined at least second signatory) available values
        if not specificSignaturesLength == 12:
            return globalCertifiedSignatures
        else:
            res = []
            for elt in enumerate(specificSignatures):
                index = elt[0]
                line = elt[1]
                if not line.strip() == '-':
                    res.append(line)
                else:
                    if index > 5:
                        index = index - 6
                    res.append(globalCertifiedSignatures[index])
            return res
    MeetingItem.getCertifiedSignatures = getCertifiedSignatures

    security.declarePublic('getCollegeItem')
    def getCollegeItem(self):
        '''Returns the predecessor item that was in the college.'''
        item = self.getSelf()
        predecessor = item.getPredecessor()
        collegeItem = None
        while predecessor:
            if predecessor.portal_type == 'MeetingItemCollege':
                collegeItem = predecessor
                break
        return collegeItem

    security.declarePublic('isPrivacyViewable')
    def isPrivacyViewable(self):
        '''Override so privacy is not taken into account while accessing an item.
           We just need privacy to be an information here, not an access management.'''
        return True
    MeetingItem.isPrivacyViewable = isPrivacyViewable

    security.declarePublic('getDefaultMotivation')
    def getDefaultDetailledDescription(self):
        '''Returns the default item motivation content from the MeetingConfig.'''
        mc = self.portal_plonemeeting.getMeetingConfig(self)
        return mc.getDefaultMeetingItemDetailledDescription()
    MeetingItem.getDefaultDetailledDescription = getDefaultDetailledDescription

    security.declarePublic('getDefaultDecision')
    def getDefaultDecision(self):
        '''Returns the default item decision content from the MeetingConfig.'''
        mc = self.portal_plonemeeting.getMeetingConfig(self)
        return mc.getDefaultMeetingItemDecision()
    MeetingItem.getDefaultDecision = getDefaultDecision

    security.declarePublic('getMeetingsAcceptingItems')
    def getMeetingsAcceptingItems(self):
        '''Overrides the default method so we only display meetings that are
           in the 'created' or 'frozen' state.'''
        pmtool = getToolByName(self.context, "portal_plonemeeting")
        catalogtool = getToolByName(self.context, "portal_catalog")
        meetingPortalType = pmtool.getMeetingConfig(self.context).getMeetingTypeName()
        # If the current user is a meetingManager (or a Manager),
        # he is able to add a meetingitem to a 'decided' meeting.
        review_state = ['created', 'frozen', ]
        member = self.context.portal_membership.getAuthenticatedMember()
        if member.has_role('MeetingManager') or member.has_role('Manager'):
            review_state.extend(('decided', 'in_committee', 'in_council', ))
        res = catalogtool.unrestrictedSearchResults(
            portal_type=meetingPortalType,
            review_state=review_state,
            sort_on='getDate')
        # Frozen meetings may still accept "late" items.
        return res

    security.declarePublic('getPredecessors')
    def getPredecessors(self):
        '''Adapted method getPredecessors showing informations about every linked items'''
        pmtool = getToolByName(self.context, "portal_plonemeeting")
        predecessor = self.context.getPredecessor()
        predecessors = []
        #retrieve every predecessors
        while predecessor:
            predecessors.append(predecessor)
            predecessor = predecessor.getPredecessor()

        #keep order
        predecessors.reverse()

        #retrieve backrefs too
        brefs = self.context.getBRefs('ItemPredecessor')
        while brefs:
            predecessors = predecessors + brefs
            brefs = brefs[0].getBRefs('ItemPredecessor')

        res = []
        for predecessor in predecessors:
            showColors = pmtool.showColorsForUser()
            coloredLink = pmtool.getColoredLink(predecessor, showColors=showColors)
            #extract title from coloredLink that is HTML and complete it
            originalTitle = re.sub('<[^>]*>', '', coloredLink).strip()
            #remove '&nbsp;' left at the beginning of the string
            originalTitle = originalTitle.lstrip('&nbsp;')
            title = originalTitle
            meeting = predecessor.getMeeting()
            #display the meeting date if the item is linked to a meeting
            if meeting:
                title = "%s (%s)" % (title, pmtool.formatDate(meeting.getDate()).encode('utf-8'))
            #show that the linked item is not of the same portal_type
            if not predecessor.portal_type == self.context.portal_type:
                title = title + '*'
            #only replace last occurence because title appear in the "title" tag,
            #could be the same as the last part of url (id), ...
            splittedColoredLink = coloredLink.split(originalTitle)
            splittedColoredLink[-2] = splittedColoredLink[-2] + title + splittedColoredLink[-1]
            splittedColoredLink.pop(-1)
            coloredLink = originalTitle.join(splittedColoredLink)
            if not checkPermission(View, predecessor):
                coloredLink = spanifyLink(coloredLink)
            res.append(coloredLink)
        return res

    security.declarePublic('getIcons')
    def getIcons(self, inMeeting, meeting):
        '''Check docstring in PloneMeeting interfaces.py.'''
        item = self.getSelf()
        res = []
        itemState = item.queryState()
        #add some icons specific for dashboard if we are actually on the dashboard...
        if itemState in item.itemDecidedStates and \
           item.REQUEST.form.get('topicId', '') == 'searchitemsfollowupdashboard':
            itemFollowUp = item.getFollowUp()
            if itemFollowUp == 'follow_up_yes':
                res.append(('follow_up_yes.png', 'follow_up_needed_icon_title'))
            elif itemFollowUp == 'follow_up_provided':
                res.append(('follow_up_provided.png', 'follow_up_provided_icon_title'))
        # Default PM item icons
        res = res + MeetingItem.getIcons(item, inMeeting, meeting)
        # Add our icons for accepted_but_modified and pre_accepted
        if itemState == 'accepted_but_modified':
            res.append(('accepted_but_modified.png', 'accepted_but_modified'))
        elif itemState == 'pre_accepted':
            res.append(('pre_accepted.png', 'pre_accepted'))
        elif itemState == 'proposed_to_director':
            res.append(('proposeToDirector.png', 'proposed_to_director'))
        elif itemState == 'proposed_to_divisionhead':
            res.append(('proposeToDivisionHead.png', 'proposed_to_divisionhead'))
        elif itemState == 'proposed_to_officemanager':
            res.append(('proposeToOfficeManager.png', 'proposed_to_officemanager'))
        elif itemState == 'item_in_council':
            res.append(('item_in_council.png', 'item_in_council'))
        elif itemState == 'item_in_committee':
            res.append(('item_in_committee.png', 'item_in_committee'))
        elif itemState == 'proposed_to_servicehead':
            res.append(('proposeToServiceHead.png', 'proposed_to_servicehead'))
        elif itemState == 'proposed_to_budgetimpact_reviewer':
            res.append(('proposeToBudgetImpactReviewer.png', 'proposed_to_budgetimpact_reviewer'))
        elif itemState == 'proposed_to_extraordinary_budget':
            res.append(('proposeToExtraordinaryBudget.png', 'proposed_to_extraordinary_budget'))
        elif itemState == 'itemcreated_waiting_advices':
            res.append(('ask_advices_by_itemcreator.png', 'itemcreated_waiting_advices'))
        elif itemState == 'returned_to_service':
            res.append(('return_to_service.png', 'returned_to_service'))
        return res

    security.declarePublic('getStrikedField')
    def getStrikedField(self, plaintext):
        '''Format the given plaintext to be striked when rendered in HTML.
           The text between [[xxx]] is striked. Used to mark absents.
           You can define mltAssembly to customize your assembly (bold, italics, ...).'''
        return plaintext.replace('[[', '<strike>').replace(']]', '</strike>').replace('<p>', '<p class="mltAssembly">')
    MeetingItem.getStrikedField = getStrikedField
    Meeting.getStrikedField = getStrikedField

    security.declarePublic('getStrikedItemAssembly')
    def getStrikedItemAssembly(self):
        '''The text between [[xxx]] is striked. Used to mark absents.
           You can define mltAssembly to customize your assembly (bold, italics, ...).'''
        return self.getStrikedField(self.context.getItemAssembly())

    security.declarePublic('getDeliberation')
    def getDeliberation(self):
        '''Returns the entire deliberation depending on fields used.'''
        return self.getMotivation() + self.getDecision()
    MeetingItem.getDeliberation = getDeliberation

    security.declarePublic('getExtraFieldsToCopyWhenCloning')
    def getExtraFieldsToCopyWhenCloning(self):
        '''See doc in PloneMeeting.interfaces.py.'''
        return ['motivation', ]
    security.declarePublic('getDecision')
    def getDecision(self, keepWithNext=False):
        '''Overridden version of 'decision' field accessor. It allows to specify
           p_keepWithNext=True. In that case, the last paragraph of bullet in
           field "decision" will get a specific CSS class that will keep it with
           next paragraph. Useful when including the decision in a document
           template and avoid having the signatures, just below it, being alone
           on the next page. And d'on't show decision for no-meeting manager if meeting state is 'decided'''
        item = self.getSelf()
        res = self.getField('decision').get(self)
        if keepWithNext:
            res = self.signatureNotAlone(res)
        if item.getMeeting() and item.getMeeting().queryState() == 'decided' and \
                not item.portal_plonemeeting.isManager():
            return '<p> La décision est actuellement en cours de rédaction </p>'
        return res
    MeetingItem.getDecision = getDecision
    MeetingItem.getRawDecision = getDecision

    def getEchevinsForProposingGroup(self):
        '''Returns all echevins defined for the proposing group'''
        res = []
        pmtool = getToolByName(self.context, "portal_plonemeeting")
        for group in pmtool.getActiveGroups():
            if self.context.getProposingGroup() in group.getEchevinServices():
                res.append(group.id)
        return res

    security.declarePublic('printAdvicesInfos')
    def printAdvicesInfos(self):
        '''Helper method to have a printable version of advices.'''
        item = self.getSelf()
        itemAdvicesByType = item.getAdvicesByType()
        res = "<p><u>%s :</u></p>" % item.utranslate('advices', domain='PloneMeeting')
        if itemAdvicesByType:
            res = res + "<p>"
        for adviceType in itemAdvicesByType:
            for advice in itemAdvicesByType[adviceType]:
                res = res + "<u>%s : %s</u><br />" % (advice['name'], item.utranslate([advice['type']][0],
                            domain='PloneMeeting'))
                if 'comment' in advice:
                    res = res + "%s<br />" % advice['comment']
        if itemAdvicesByType:
            res = res + "</p>"
        if not itemAdvicesByType:
            return "<p><u>%s : -</u></p>" % item.utranslate('advices', domain='PloneMeeting')
        return res


class CustomMeetingConfig(MeetingConfig):
    '''Adapter that adapts a meetingConfig implementing IMeetingConfig to the
       interface IMeetingConfigCustom.'''

    implements(IMeetingConfigCustom)
    security = ClassSecurityInfo()

    def __init__(self, item):
        self.context = item

    #we need to be able to give an advice in the initial_state for Council...
    from Products.PloneMeeting.MeetingConfig import MeetingConfig
    MeetingConfig.listItemStatesInitExcepted = MeetingConfig.listItemStates

    security.declarePublic('searchReviewableItems')
    def searchReviewableItems(self, sortKey, sortOrder, filterKey, filterValue, **kwargs):
        '''Returns a list of items that the user could review.'''
        member = self.portal_membership.getAuthenticatedMember()
        groups = self.portal_groups.getGroupsForPrincipal(member)
        #the logic is :
        #a user is reviewer for his level of hierarchy and every levels below in a group
        #so find the different groups (a user could be divisionhead in groupA and director in groupB)
        #and find the different states we have to search for this group (proposingGroup of the item)
        reviewSuffixes = ('_reviewers', '_divisionheads', '_officemanagers', '_serviceheads', )
        statesMapping = {'_reviewers': ('proposed_to_servicehead', 'proposed_to_officemanager',
                                        'proposed_to_divisionhead', 'proposed_to_director'),
                         '_divisionheads': ('proposed_to_servicehead', 'proposed_to_officemanager',
                                            'proposed_to_divisionhead'),
                         '_officemanagers': ('proposed_to_servicehead', 'proposed_to_officemanager'),
                         '_serviceheads': 'proposed_to_servicehead'}
        foundGroups = {}
        #check that we have a real PM group, not "echevins", or "Administrators"
        for group in groups:
            isOK = False
            for reviewSuffix in reviewSuffixes:
                if group.endswith(reviewSuffix):
                    isOK = True
                    break
            if not isOK:
                continue
            #remove the suffix
            groupPrefix = '_'.join(group.split('_')[:-1])
            if not groupPrefix in foundGroups:
                foundGroups[groupPrefix] = ''
        #now we have the differents services (equal to the MeetingGroup id) the user is in
        strgroups = str(groups)
        for foundGroup in foundGroups:
            for reviewSuffix in reviewSuffixes:
                if "%s%s" % (foundGroup, reviewSuffix) in strgroups:
                    foundGroups[foundGroup] = reviewSuffix
                    break
        #now we have in the dict foundGroups the group the user is in in the key and the highest level in the value
        res = []
        for foundGroup in foundGroups:
            params = {'portal_type': 'MeetingItemCollege',
                      'getProposingGroup': foundGroup,
                      'review_state': statesMapping[foundGroups[foundGroup]],
                      'sort_on': sortKey,
                      'sort_order': sortOrder}
            # Manage filter
            if filterKey:
                params[filterKey] = Keywords(filterValue).get()
            # update params with kwargs
            params.update(kwargs)
            # Perform the query in portal_catalog
            brains = self.portal_catalog(**params)
            res.extend(brains)
        return res
    MeetingConfig.searchReviewableItems = searchReviewableItems

    security.declarePublic('searchItemsForDashboard')
    def searchItemsForDashboard(self, sortKey, sortOrder, filterKey, filterValue, **kwargs):
        '''Returns a list of items that will be used for the dashboard.'''
        params = {'portal_type': self.getItemTypeName(),
                  'review_state': ['accepted', 'refused', 'delayed', 'accepted_but_modified', ],
                  'getFollowUp': ['follow_up_yes', 'follow_up_provided', ],
                  'sort_on': sortKey,
                  'sort_order': sortOrder
                  }
        # Manage filter
        if filterKey:
            params[filterKey] = Keywords(filterValue).get()
        # update params with kwargs
        params.update(kwargs)
        # Perform the query in portal_catalog
        brains = self.portal_catalog(**params)
        # sort elements by proposing-group keeping order from MeetingGroups
        existingGroupIds = self.portal_plonemeeting.objectIds('MeetingGroup')
        def sortBrainsByMeetingDate(x, y):
            '''First sort by meetingDate.'''
            return cmp(y.getMeetingDate, x.getMeetingDate)
        def sortBrainsByProposingGroup(x, y):
            '''Second sort by proposing group (of the same meetingDate).'''
            if not x.getMeetingDate == y.getMeetingDate:
                return 0
            else:
                return cmp(existingGroupIds.index(x.getProposingGroup), existingGroupIds.index(y.getProposingGroup))
        brains = list(brains)
        # sort first by meeting date
        brains.sort(sortBrainsByMeetingDate)
        # then by proposing group
        brains.sort(sortBrainsByProposingGroup)
        return brains
    MeetingConfig.searchItemsForDashboard = searchItemsForDashboard


class CustomMeetingGroup(MeetingGroup):
    '''Adapter that adapts a meetingGroup implementing IMeetingGroup to the
       interface IMeetingGroupCustom.'''

    implements(IMeetingGroupCustom)
    security = ClassSecurityInfo()

    def __init__(self, item):
        self.context = item

    security.declarePrivate('validate_signatures')
    def validate_signatures(self, value):
        '''Validate the MeetingGroup.signatures field.'''
        if value.strip() and not len(value.split('\n')) == 12:
            return self.utranslate('signatures_length_error', domain='PloneMeeting')
    MeetingGroup.validate_signatures = validate_signatures

    security.declarePublic('listEchevinServices')
    def listEchevinServices(self):
        '''Returns a list of groups that can be selected on an group (without isEchevin).'''
        res = []
        pmtool = getToolByName(self, "portal_plonemeeting")
        # Get every Plone group related to a MeetingGroup
        for group in pmtool.getActiveGroups():
            res.append((group.id, group.getProperty('title')))

        return DisplayList(tuple(res))
    MeetingGroup.listEchevinServices = listEchevinServices


# ------------------------------------------------------------------------------
class MeetingCollegeMonsWorkflowActions(MeetingWorkflowActions):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingCollegeWorkflowActions'''

    implements(IMeetingCollegeMonsWorkflowActions)
    security = ClassSecurityInfo()

    security.declarePrivate('doClose')
    def doClose(self, stateChange):
        # Every item that is "presented" will be automatically set to "accepted"
        for item in self.context.getAllItems():
            if item.queryState() == 'presented':
                self.context.portal_workflow.doActionFor(item, 'itemfreeze')
            if item.queryState() in ['itemfrozen', 'pre_accepted', ]:
                self.context.portal_workflow.doActionFor(item, 'accept')
        # For this meeting, what is the number of the first item ?
        meetingConfig = self.context.portal_plonemeeting.getMeetingConfig(
            self.context)
        self.context.setFirstItemNumber(meetingConfig.getLastItemNumber()+1)
        # Update the item counter which is global to the meeting config
        meetingConfig.setLastItemNumber(meetingConfig.getLastItemNumber() +
                                        len(self.context.getItems()) +
                                        len(self.context.getLateItems()))

    security.declarePrivate('doDecide')
    def doDecide(self, stateChange):
        '''We pass every item that is 'presented' in the 'itemfrozen'
           state.  It is the case for late items. '''
        for item in self.context.getAllItems(ordered=True):
            if item.queryState() == 'presented':
                self.context.portal_workflow.doActionFor(item, 'itemfreeze')

    security.declarePrivate('doFreeze')
    def doFreeze(self, stateChange):
        '''When freezing the meeting, every items must be automatically set to
           "itemfrozen".'''
        for item in self.context.getAllItems(ordered=True):
            if item.queryState() == 'presented':
                self.context.portal_workflow.doActionFor(item, 'itemfreeze')
        #manage meeting number
        self.initSequenceNumber()

    security.declarePrivate('doBackToCreated')
    def doBackToCreated(self, stateChange):
        '''When a meeting go back to the "created" state, for example the
           meeting manager wants to add an item, we do not do anything.'''
        pass

    security.declarePrivate('doPublish')
    def doPublish(self, stateChange):
        '''We passe every item that is 'itemfrozen' in the 'accept' state.'''
        for item in self.context.getAllItems(ordered=True):
            if item.queryState() == 'presented':
                self.context.portal_workflow.doActionFor(item, 'itemfreeze')
            if item.queryState() == 'itemfrozen':
                self.context.portal_workflow.doActionFor(item, 'accept')


class MeetingCollegeMonsWorkflowConditions(MeetingWorkflowConditions):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingCollegeWorkflowConditions'''

    implements(IMeetingCollegeMonsWorkflowConditions)
    security = ClassSecurityInfo()

    security.declarePublic('mayFreeze')
    def mayFreeze(self):
        res = False
        if checkPermission(ReviewPortalContent, self.context):
            res = True  # At least at present
            if not self.context.getRawItems():
                res = No(self.context.utranslate('item_required_to_publish'))
        return res

    security.declarePublic('mayClose')
    def mayClose(self):
        res = False
        # The user just needs the "Review portal content" permission on the
        # object to close it.
        if checkPermission(ReviewPortalContent, self.context):
            res = True
        return res

    security.declarePublic('mayDecide')
    def mayDecide(self):
        res = False
        if checkPermission(ReviewPortalContent, self.context) and \
           (not self._allItemsAreDelayed()):
            res = True
        return res

    security.declarePublic('mayChangeItemsOrder')
    def mayChangeItemsOrder(self):
        '''We can change the order if the meeting is not closed'''
        res = False
        if checkPermission(ModifyPortalContent, self.context) and \
           self.context.queryState() not in ('closed'):
            res = True
        return res

    def mayCorrect(self):
        '''Take the default behaviour except if the meeting is frozen
           we still have the permission to correct it.'''
        from Products.PloneMeeting.Meeting import MeetingWorkflowConditions
        res = MeetingWorkflowConditions.mayCorrect(self)
        currentState = self.context.queryState()
        if res is not True and currentState == "frozen":
            # Change the behaviour for being able to correct a frozen meeting
            # back to created.
            if checkPermission(ReviewPortalContent, self.context):
                return True
        return res


class MeetingItemCollegeMonsWorkflowActions(MeetingItemWorkflowActions):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingItemCollegeWorkflowActions'''

    implements(IMeetingItemCollegeMonsWorkflowActions)
    security = ClassSecurityInfo()

    security.declarePrivate('doAccept_but_modify')
    def doAccept_but_modify(self, stateChange):
        pass

    security.declarePrivate('doPreAccept')
    def doPre_accept(self, stateChange):
        pass

    security.declarePrivate('doRemove')
    def doRemove(self, stateChange):
        pass

    security.declarePrivate('doProposeToServiceHead')
    def doProposeToServiceHead(self, stateChange):
        pass

    security.declarePrivate('doProposeToDirector')
    def doProposeToDirector(self, stateChange):
        pass

    security.declarePrivate('doProposeToOfficeManager')
    def doProposeToOfficeManager(self, stateChange):
        pass

    security.declarePrivate('doProposeToDivisionHead')
    def doProposeToDivisionHead(self, stateChange):
        pass

    security.declarePrivate('doValidateByBudgetImpactReviewer')
    def doValidateByBudgetImpactReviewer(self, stateChange):
        pass

    security.declarePrivate('doProposeToBudgetImpactReviewer')
    def doProposeToBudgetImpactReviewer(self, stateChange):
        pass

    security.declarePrivate('doValidateByExtraordinaryBudget')
    def doValidateByExtraordinaryBudget(self, stateChange):
        pass

    security.declarePrivate('doProposeToExtraordinaryBudget')
    def doProposeToExtraordinaryBudget(self, stateChange):
        pass

    security.declarePrivate('doAsk_advices_by_itemcreator')
    def doAsk_advices_by_itemcreator(self, stateChange):
        pass

    security.declarePrivate('doDelay')
    def doDelay(self, stateChange):
        '''When an item is delayed, we will duplicate it: the copy is back to
           the initial state and will be linked to this one.
           After, we replace decision for initial items'''
        creator = self.context.Creator()
        # We create a copy in the initial item state, in the folder of creator.
        clonedItem = self.context.clone(copyAnnexes=False, newOwnerId=creator,
                                        cloneEventAction='create_from_predecessor')
        clonedItem.setPredecessor(self.context)
        # Send, if configured, a mail to the person who created the item
        clonedItem.sendMailIfRelevant('itemDelayed', 'Owner', isRole=True)
        meetingConfig = self.context.portal_plonemeeting.getMeetingConfig(self.context)
        itemDecisionReportText = meetingConfig.getItemDecisionReportText()
        if itemDecisionReportText.strip():
            from Products.CMFCore.Expression import Expression, createExprContext
            portal = self.context.portal_url.getPortalObject()
            ctx = createExprContext(self.context.getParentNode(), portal, self.context)
            try:
                res = Expression(itemDecisionReportText)(ctx)
            except Exception, e:
                self.context.portal_plonemeeting.plone_utils.addPortalMessage(PloneMeetingError('%s' % str(e)))
                return
            self.context.setDecision(res)
        self.context.portal_workflow.doActionFor(clonedItem, 'validate')

    security.declarePrivate('doRefuse')
    def doRefuse(self, stateChange):
        '''When an item is refused, the decision will be change'''
        meetingConfig = self.context.portal_plonemeeting.getMeetingConfig(self.context)
        itemDecisionRefuseText = meetingConfig.getItemDecisionRefuseText()
        if itemDecisionRefuseText.strip():
            from Products.CMFCore.Expression import Expression, createExprContext
            portal = self.context.portal_url.getPortalObject()
            ctx = createExprContext(self.context.getParentNode(), portal, self.context)
            try:
                res = Expression(itemDecisionRefuseText)(ctx)
            except Exception, e:
                self.context.portal_plonemeeting.plone_utils.addPortalMessage(PloneMeetingError('%s' % str(e)))
                return
            self.context.setDecision(res)


# ------------------------------------------------------------------------------
class MeetingItemCollegeMonsWorkflowConditions(MeetingItemWorkflowConditions):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingItemCollegeWorkflowConditions'''

    implements(IMeetingItemCollegeMonsWorkflowConditions)
    security = ClassSecurityInfo()

    def __init__(self, item):
        self.context = item  # Implements IMeetingItem
        self.sm = getSecurityManager()
        self.useHardcodedTransitionsForPresentingAnItem = True
        self.transitionsForPresentingAnItem = ('proposeToServiceHead',
                                               'proposeToOfficeManager',
                                               'proposeToDivisionHead',
                                               'proposeToDirector',
                                               'validate',
                                               'present')

    security.declarePublic('mayDecide')
    def mayDecide(self):
        '''We may decide an item if the linked meeting is in the 'decided'
           state.'''
        res = False
        meeting = self.context.getMeeting()
        if checkPermission(ReviewPortalContent, self.context) and \
           meeting and (meeting.queryState() in ['decided', 'closed']):
            res = True
        return res

    security.declarePublic('isLateFor')
    def isLateFor(self, meeting):
        res = False
        if meeting and (meeting.queryState() in MeetingItem.meetingAlreadyFrozenStates) and \
           (meeting.UID() == self.context.getPreferredMeeting()):
            itemValidationDate = self._getDateOfAction(self.context, 'validate')
            meetingFreezingDate = self._getDateOfAction(meeting, 'freeze')
            if itemValidationDate and meetingFreezingDate:
                if itemValidationDate > meetingFreezingDate:
                    res = True
        return res

    security.declarePublic('mayValidate')
    def mayValidate(self):
        """
          Either the Director or the MeetingManager can validate
          The MeetingManager can bypass the validation process and validate an item
          that is in the state 'itemcreated'
        """
        res = False
        user = self.context.portal_membership.getAuthenticatedMember()
        #first of all, the use must have the 'Review portal content permission'
        if checkPermission(ReviewPortalContent, self.context) and \
                (user.has_role('MeetingReviewer', self.context) or user.has_role('Manager')):
            res = True
            #if the current item state is 'itemcreated', only the MeetingManager can validate
            if self.context.queryState() in ('itemcreated',) and not self.context.portal_plonemeeting.isManager():
                res = False
        return res

    security.declarePublic('mayFreeze')
    def mayFreeze(self):
        res = False
        if checkPermission(ReviewPortalContent, self.context):
            if self.context.hasMeeting() and \
               (self.context.getMeeting().queryState() in ('frozen', 'decided', 'closed')):
                res = True
        return res

    security.declarePublic('mayCorrect')
    def mayCorrect(self):
        # Check with the default PloneMeeting method and our test if res is
        # False. The diffence here is when we correct an item from itemfrozen to
        # presented, we have to check if the Meeting is in the "created" state
        # and not "published".
        res = MeetingItemWorkflowConditions.mayCorrect(self)
        # Manage our own behaviour now when the item is linked to a meeting,
        # a MeetingManager can correct anything except if the meeting is closed
        if res is not True:
            if checkPermission(ReviewPortalContent, self.context):
                # Get the meeting
                meeting = self.context.getMeeting()
                if meeting:
                    # Meeting can be None if there was a wf problem leading
                    # an item to be in a "presented" state with no linked
                    # meeting.
                    meetingState = meeting.queryState()
                    # A user having ReviewPortalContent permission can correct
                    # an item in any case except if the meeting is closed.
                    if meetingState != 'closed':
                        res = True
                else:
                    res = True
        return res

    security.declarePublic('mayWaitAdvices')
    def mayWaitAdvices(self):
        """
          Check that the user has the 'Review portal content'
        """
        res = False
        if checkPermission(ReviewPortalContent, self.context):
            res = True
        return res

    security.declarePublic('mayProposeToServiceHead')
    def mayProposeToServiceHead(self):
        """
          Check that the user has the 'Review portal content'
        """
        res = False
        #if item have budget info, budget reviewer must validate it
        isValidateByBudget = not self.context.getBudgetRelated() or self.context.getValidateByBudget() or \
            self.context.portal_plonemeeting.isManager()
        if checkPermission(ReviewPortalContent, self.context) and isValidateByBudget:
            res = True
        return res

    security.declarePublic('mayProposeToOfficeManager')
    def mayProposeToOfficeManager(self):
        """
          Check that the user has the 'Review portal content'
        """
        res = False
        if checkPermission(ReviewPortalContent, self.context):
                res = True
        return res

    security.declarePublic('mayProposeToDivisionHead')
    def mayProposeToDivisionHead(self):
        """
          Check that the user has the 'Review portal content'
        """
        res = False
        if checkPermission(ReviewPortalContent, self.context):
                res = True
        return res

    security.declarePublic('mayProposeToDirector')
    def mayProposeToDirector(self):
        """
          Check that the user has the 'Review portal content'
        """
        res = False
        if checkPermission(ReviewPortalContent, self.context):
                res = True
        return res

    security.declarePublic('mayRemove')
    def mayRemove(self):
        """
          We may remove an item if the linked meeting is in the 'decided'
          state.  For now, this is the same behaviour as 'mayDecide'
        """
        res = False
        meeting = self.context.getMeeting()
        if checkPermission(ReviewPortalContent, self.context) and \
           meeting and (meeting.queryState() in ['decided', 'closed']):
            res = True
        return res

    security.declarePublic('mayValidateByBudgetImpactReviewer')
    def mayValidateByBudgetImpactReviewer(self):
        """
          Check that the user has the 'Review portal content'
        """
        res = False
        if checkPermission(ReviewPortalContent, self.context):
                res = True
        return res

    security.declarePublic('mayProposeToBudgetImpactReviewer')
    def mayProposeToBudgetImpactReviewer(self):
        """
          Check that the user has the 'Review portal content'
        """
        res = False
        if checkPermission(ReviewPortalContent, self.context):
                res = True
        return res

    security.declarePublic('mayValidateByExtraordinaryBudget')
    def mayValidateByExtraordinaryBudget(self):
        """
          Check that the user has the 'Review portal content'
        """
        res = False
        if checkPermission(ReviewPortalContent, self.context):
                res = True
        return res

    security.declarePublic('mayProposeToExtraordinaryBudget')
    def mayProposeToExtraordinaryBudget(self):
        """
          Check that the user has the 'Review portal content'
        """
        res = False
        if checkPermission(ReviewPortalContent, self.context):
                res = True
        return res


class MeetingCouncilMonsWorkflowActions(MeetingWorkflowActions):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingCouncilWorkflowActions'''

    implements(IMeetingCouncilMonsWorkflowActions)
    security = ClassSecurityInfo()

    security.declarePrivate('doSetInCommittee')
    def doSetInCommittee(self, stateChange):
        '''When setting the meeting in committee, every items must be automatically
           set to "item_in_committee".'''
        for item in self.context.getAllItems(ordered=True):
            if item.queryState() == 'presented':
                self.context.portal_workflow.doActionFor(item, 'setItemInCommittee')
        #manage meeting number
        self.initSequenceNumber()

    security.declarePrivate('doSetInCouncil')
    def doSetInCouncil(self, stateChange):
        '''When setting the meeting in council, every items must be automatically
           set to "item_in_council".'''
        for item in self.context.getAllItems(ordered=True):
            if item.queryState() == 'presented':
                self.context.portal_workflow.doActionFor(item, 'setItemInCommittee')
            if item.queryState() == 'item_in_committee':
                self.context.portal_workflow.doActionFor(item, 'setItemInCouncil')

    security.declarePrivate('doClose')
    def doClose(self, stateChange):
        # Every item that is "presented" will be automatically set to "accepted"
        for item in self.context.getAllItems():
            if item.queryState() == 'presented':
                self.context.portal_workflow.doActionFor(item, 'itemfreeze')
            if item.queryState() == 'itemfrozen':
                self.context.portal_workflow.doActionFor(item, 'setItemInCommittee')
            if item.queryState() == 'item_in_committee':
                self.context.portal_workflow.doActionFor(item, 'setItemInCouncil')
            if item.queryState() == 'itemfrozen':
                self.context.portal_workflow.doActionFor(item, 'setItemInCommittee')
            if item.queryState() == 'item_in_council':
                self.context.portal_workflow.doActionFor(item, 'accept')
        # For this meeting, what is the number of the first item ?
        meetingConfig = self.context.portal_plonemeeting.getMeetingConfig(
            self.context)
        self.context.setFirstItemNumber(meetingConfig.getLastItemNumber()+1)
        # Update the item counter which is global to the meeting config
        meetingConfig.setLastItemNumber(meetingConfig.getLastItemNumber() +
                                        len(self.context.getItems()) +
                                        len(self.context.getLateItems()))

    security.declarePrivate('doBackToCreated')
    def doBackToCreated(self, stateChange):
        '''When a meeting go back to the "created" state, for example the
           meeting manager wants to add an item, we do not do anything.'''
        pass

    security.declarePrivate('doBackToInCommittee')
    def doBackToInCommittee(self, stateChange):
        '''When a meeting go back to the "in_committee" we set every items 'in_council' back to 'in_committee'.'''
        for item in self.context.getAllItems():
            if item.queryState() == 'item_in_council':
                self.context.portal_workflow.doActionFor(item, 'backToItemInCommittee')

    security.declarePrivate('doBackToInCouncil')
    def doBackToInCouncil(self, stateChange):
        '''When a meeting go back to the "in_council" we do not do anything.'''
        pass


class MeetingCouncilMonsWorkflowConditions(MeetingWorkflowConditions):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingCouncilWorkflowConditions'''

    implements(IMeetingCouncilMonsWorkflowConditions)
    security = ClassSecurityInfo()

    def __init__(self, meeting):
        self.context = meeting
        customAcceptItemsStates = ('created', 'in_committee', 'in_council', )
        self.acceptItemsStates = customAcceptItemsStates

    security.declarePublic('maySetInCommittee')
    def maySetInCommittee(self):
        res = False
        # The user just needs the "Review portal content" permission
        if checkPermission(ReviewPortalContent, self.context):
            res = True
        return res

    security.declarePublic('maySetInCouncil')
    def maySetInCouncil(self):
        # The user just needs the "Review portal content" permission
        if not checkPermission(ReviewPortalContent, self.context):
            return False
        return True

    security.declarePublic('mayClose')
    def mayClose(self):
        res = False
        # The user just needs the "Review portal content" permission on the
        # object to close it.
        if checkPermission(ReviewPortalContent, self.context):
            res = True
        # check that no item is returned to the service
        #for item in self.context.getItems():
        #    if item.queryState() == 'returned_to_service':
        #        return No(self.context.utranslate('some_item_still_in_service'))
        return res

    security.declarePublic('mayChangeItemsOrder')
    def mayChangeItemsOrder(self):
        '''We can change the order if the meeting is not closed'''
        res = False
        if checkPermission(ModifyPortalContent, self.context) and \
           self.context.queryState() not in ('closed', ):
            res = True
        return res

    def mayCorrect(self):
        '''Take the default behaviour except if the meeting is frozen
           we still have the permission to correct it.'''
        from Products.PloneMeeting.Meeting import MeetingWorkflowConditions
        res = MeetingWorkflowConditions.mayCorrect(self)
        currentState = self.context.queryState()
        if res is not True and currentState in ('in_committee', 'in_council', ):
            # Change the behaviour for being able to correct a frozen meeting
            # back to created.
            if checkPermission(ReviewPortalContent, self.context):
                return True
        return res


class MeetingItemCouncilMonsWorkflowActions(MeetingItemWorkflowActions):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingItemCouncilWorkflowActions'''

    implements(IMeetingItemCouncilMonsWorkflowActions)
    security = ClassSecurityInfo()

    security.declarePrivate('doProposeToDirector')
    def doProposeToDirector(self, stateChange):
        pass

    security.declarePrivate('doSetItemInCommittee')
    def doSetItemInCommittee(self, stateChange):
        pass

    security.declarePrivate('doSetItemInCouncil')
    def doSetItemInCouncil(self, stateChange):
        pass

    security.declarePrivate('doReturn_to_service')
    def doReturn_to_service(self, stateChange):
        '''Send an email to the creator and to the officemanagers'''
        recipients = []
        # Send to the creator
        creator = self.context.portal_membership.getMemberById(self.context.Creator())
        recipients.append(creator.getProperty('email'))
        # and to the officemanagers
        proposingMeetingGroup = getattr(self.context.portal_plonemeeting, self.context.getProposingGroup())
        reviewerGroupId = proposingMeetingGroup.getPloneGroupId('officemanagers')
        for userId in self.context.portal_groups.getGroupMembers(reviewerGroupId):
            user = self.context.portal_membership.getMemberById(userId)
            recipients.append(user.getProperty('email'))
        lastEvent = getLastEvent(self.context, 'return_to_service')
        enc = self.context.portal_properties.site_properties.getProperty('default_charset')

        sendMail(recipients, self.context, 'returnedToService',
                 mapping={'comments': lastEvent['comments'].decode(enc)})

    security.declarePrivate('doReturn_to_secretary')
    def doReturn_to_secretary(self, stateChange):
        pass

    security.declarePrivate('doReturn_to_secretary_in_committee')
    def doReturn_to_secretary_in_committee(self, stateChange):
        pass

    security.declarePrivate('doReturn_to_secretary_in_council')
    def doReturn_to_secretary_in_council(self, stateChange):
        pass

    security.declarePrivate('doBackToItemInCommittee')
    def doBackToItemInCommittee(self, stateChange):
        pass

    security.declarePrivate('doBackToItemInCouncil')
    def doBackToItemInCouncil(self, stateChange):
        pass

    security.declarePrivate('doAccept_but_modify')
    def doAccept_but_modify(self, stateChange):
        pass

    security.declarePrivate('doDelay')
    def doDelay(self, stateChange):
        '''When an item is delayed, by default it is duplicated but we do not
           duplicate it here'''
        pass


# ------------------------------------------------------------------------------
class MeetingItemCouncilMonsWorkflowConditions(MeetingItemWorkflowConditions):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingItemCouncilWorkflowConditions'''

    implements(IMeetingItemCouncilMonsWorkflowConditions)
    security = ClassSecurityInfo()

    def __init__(self, item):
        self.context = item  # Implements IMeetingItem
        self.sm = getSecurityManager()
        self.useHardcodedTransitionsForPresentingAnItem = True
        self.transitionsForPresentingAnItem = ('proposeToDirector', 'validate', 'present')

    security.declarePublic('mayProposeToDirector')
    def mayProposeToDirector(self):
        """
          Check that the user has the 'Review portal content'
          If the item comes from the college, check that it has a defined
          'category'
        """
        # In the case the item comes from the college
        if not self.context.getCategory():
            return False
        if checkPermission(ReviewPortalContent, self.context) and \
           (not self.context.isDefinedInTool()):
            return True
        return False

    security.declarePublic('isLateFor')
    def isLateFor(self, meeting):
        """
          No late functionnality for Council
        """
        return False

    security.declarePublic('maySetItemInCommittee')
    def maySetItemInCommittee(self):
        """
          Check that the user has the 'Review portal content'
          And that the linked meeting is in the correct state
        """
        res = False
        if checkPermission(ReviewPortalContent, self.context):
            if self.context.hasMeeting() and \
               (self.context.getMeeting().queryState() in
               ('in_committee', 'in_council', 'closed')):
                res = True
        return res

    security.declarePublic('maySetItemInCouncil')
    def maySetItemInCouncil(self):
        """
          Check that the user has the 'Review portal content'
          And that the linked meeting is in the correct state
        """
        res = False
        if checkPermission(ReviewPortalContent, self.context):
            if self.context.hasMeeting() and \
               (self.context.getMeeting().queryState() in
               ('in_council', 'closed')):
                res = True
        return res

    security.declarePublic('mayReturnToService')
    def mayReturnToService(self):
        """
          Check that the user has the 'Review portal content'
        """
        if checkPermission(ReviewPortalContent, self.context) and \
           (not self.context.isDefinedInTool()):
            return True
        return False

    security.declarePublic('mayReturnToSecretary')
    def mayReturnToSecretary(self):
        """
          Check that the user has the 'Review portal content'
          Check that an item send back to the service can be send back to the 'presented' state
        """
        if checkPermission(ReviewPortalContent, self.context) and \
           (not self.context.isDefinedInTool()) and self.context.getMeeting().queryState() == 'created':
            return True
        return False

    security.declarePublic('mayReturnToSecretaryInCommittee')
    def mayReturnToSecretaryInCommittee(self):
        """
          Check that the user has the 'Review portal content'
          Check that an item send back to the service can be send back to the 'item_in_committee' state
        """
        if checkPermission(ReviewPortalContent, self.context) and \
           (not self.context.isDefinedInTool()) and self.context.getMeeting().queryState() == 'in_committee':
            return True
        return False

    security.declarePublic('mayReturnToSecretaryInCouncil')
    def mayReturnToSecretaryInCouncil(self):
        """
          Check that the user has the 'Review portal content'
          Check that an item send back to the service can be send back to the 'item_in_council' state
        """
        if checkPermission(ReviewPortalContent, self.context) and \
           (not self.context.isDefinedInTool()) and self.context.getMeeting().queryState() == 'in_council':
            return True
        return False

    security.declarePublic('mayDecide')
    def mayDecide(self):
        '''We may decide an item if the linked meeting is in the 'decided'
           state.'''
        res = False
        meeting = self.context.getMeeting()
        if checkPermission(ReviewPortalContent, self.context) and \
           meeting and (meeting.queryState() in ['in_council', 'closed']):
            res = True
        return res

    security.declarePublic('mayCorrect')
    def mayCorrect(self):
        # Check with the default PloneMeeting method and our test if res is
        # False. The diffence here is when we correct an item from itemfrozen to
        # presented, we have to check if the Meeting is in the "created" state
        # and not "published".
        res = MeetingItemWorkflowConditions.mayCorrect(self)
        # Manage our own behaviour now when the item is linked to a meeting,
        # a MeetingManager can correct anything except if the meeting is closed
        if res is not True:
            if checkPermission(ReviewPortalContent, self.context):
                # Get the meeting
                meeting = self.context.getMeeting()
                if meeting:
                    # Meeting can be None if there was a wf problem leading
                    # an item to be in a "presented" state with no linked
                    # meeting.
                    meetingState = meeting.queryState()
                    # A user having ReviewPortalContent permission can correct
                    # an item in any case except if the meeting is closed.
                    if meetingState != 'closed':
                        res = True
                else:
                    res = True
        return res


class CustomToolPloneMeeting(ToolPloneMeeting):
    '''Adapter that adapts a tool implementing ToolPloneMeeting to the
       interface IToolPloneMeetingCustom'''

    implements(IToolPloneMeetingCustom)
    security = ClassSecurityInfo()

    security.declarePublic('getSpecificAssemblyFor')
    def getSpecificAssemblyFor(self, assembly, startTxt=''):
        ''' Return the Assembly between two tag.
            This method is use in template
        '''
        #Pierre Dupont - Bourgmestre,
        #Charles Exemple - 1er Echevin,
        #Echevin Un, Echevin Deux excusé, Echevin Trois - Echevins,
        #Jacqueline Exemple, Responsable du CPAS
        #Absentes:
        #Mademoiselle x
        #Excusés:
        #Monsieur Y, Madame Z
        res = []
        tmp = ['<p class="mltAssembly">']
        splitted_assembly = assembly.replace('<p>', '').replace('</p>', '').split('<br />')
        start_text = startTxt == ''
        for assembly_line in splitted_assembly:
            assembly_line = assembly_line.strip()
            #check if this line correspond to startTxt (in this cas, we can begin treatment)
            if not start_text:
                start_text = assembly_line.startswith(startTxt)
                if start_text:
                    #when starting treatment, add tag (not use if startTxt=='')
                    res.append(assembly_line)
                continue
            #check if we must stop treatment...
            if assembly_line.endswith(':'):
                break
            lines = assembly_line.split(',')
            cpt = 1
            my_line = ''
            for line in lines:
                if cpt == len(lines):
                    my_line = "%s%s<br />" % (my_line, line)
                    tmp.append(my_line)
                else:
                    my_line = "%s%s," % (my_line, line)
                cpt = cpt + 1
        if len(tmp) > 1:
            tmp[-1] = tmp[-1].replace('<br />', '')
            tmp.append('</p>')
        else:
            return ''
        res.append(''.join(tmp))
        return res
# ------------------------------------------------------------------------------
InitializeClass(CustomMeetingItem)
InitializeClass(CustomMeeting)
InitializeClass(CustomMeetingConfig)
InitializeClass(CustomMeetingGroup)
InitializeClass(MeetingCollegeMonsWorkflowActions)
InitializeClass(MeetingCollegeMonsWorkflowConditions)
InitializeClass(MeetingItemCollegeMonsWorkflowActions)
InitializeClass(MeetingItemCollegeMonsWorkflowConditions)
InitializeClass(MeetingCouncilMonsWorkflowActions)
InitializeClass(MeetingCouncilMonsWorkflowConditions)
InitializeClass(MeetingItemCouncilMonsWorkflowActions)
InitializeClass(MeetingItemCouncilMonsWorkflowConditions)
InitializeClass(CustomToolPloneMeeting)
# ------------------------------------------------------------------------------
