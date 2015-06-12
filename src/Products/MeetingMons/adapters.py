# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Copyright (c) 2011 by IMIO.be
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
from appy.gen import No
from AccessControl import getSecurityManager
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from zope.interface import implements
from zope.i18n import translate
from Products.CMFCore.permissions import ReviewPortalContent
from Products.CMFCore.utils import getToolByName
from imio.helpers.xhtml import xhtmlContentIsEmpty
from Products.Archetypes.atapi import DisplayList
from Products.PloneMeeting.MeetingItem import MeetingItem, \
    MeetingItemWorkflowConditions, MeetingItemWorkflowActions
from Products.PloneMeeting.utils import checkPermission, sendMail, getLastEvent
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
from Products.PloneMeeting.utils import prepareSearchValue
from Products.PloneMeeting.model import adaptations
from DateTime import DateTime
from Products.PloneMeeting.interfaces import IAnnexable


# Names of available workflow adaptations.
customWfAdaptations = ('return_to_proposing_group', 'hide_decisions_when_under_writing', )
MeetingConfig.wfAdaptations = customWfAdaptations
# configure parameters for the returned_to_proposing_group wfAdaptation
# we keep also 'itemfrozen' and 'itempublished' in case this should be activated for meeting-config-college...
RETURN_TO_PROPOSING_GROUP_FROM_ITEM_STATES = ('presented', 'itemfrozen', )
adaptations.RETURN_TO_PROPOSING_GROUP_FROM_ITEM_STATES = RETURN_TO_PROPOSING_GROUP_FROM_ITEM_STATES
RETURN_TO_PROPOSING_GROUP_CUSTOM_PERMISSIONS = {
    # view permissions
    'Access contents information':
    ('Manager', 'MeetingManager', 'MeetingMember', 'MeetingServiceHead', 'MeetingOfficeManager',
     'MeetingDivisionHead', 'MeetingReviewer', 'MeetingObserverLocal', 'Reader', ),
    'View':
    ('Manager', 'MeetingManager', 'MeetingMember', 'MeetingServiceHead', 'MeetingOfficeManager',
     'MeetingDivisionHead', 'MeetingReviewer', 'MeetingObserverLocal', 'Reader', ),
    'PloneMeeting: Read decision':
    ('Manager', 'MeetingManager', 'MeetingMember', 'MeetingServiceHead', 'MeetingOfficeManager',
     'MeetingDivisionHead', 'MeetingReviewer', 'MeetingObserverLocal', 'Reader', ),
    'PloneMeeting: Read optional advisers':
    ('Manager', 'MeetingManager', 'MeetingMember', 'MeetingServiceHead', 'MeetingOfficeManager',
     'MeetingDivisionHead', 'MeetingReviewer', 'MeetingObserverLocal', 'Reader', ),
    'PloneMeeting: Read decision annex':
    ('Manager', 'MeetingManager', 'MeetingMember', 'MeetingServiceHead', 'MeetingOfficeManager',
     'MeetingDivisionHead', 'MeetingReviewer', 'MeetingObserverLocal', 'Reader', ),
    'PloneMeeting: Read item observations':
    ('Manager', 'MeetingManager', 'MeetingMember', 'MeetingServiceHead', 'MeetingOfficeManager',
     'MeetingDivisionHead', 'MeetingReviewer', 'MeetingObserverLocal', 'Reader', ),
    'PloneMeeting: Read budget infos':
    ('Manager', 'MeetingManager', 'MeetingMember', 'MeetingServiceHead', 'MeetingOfficeManager',
     'MeetingDivisionHead', 'MeetingReviewer', 'MeetingObserverLocal', 'MeetingBudgetImpactReviewer', 'Reader', ),
    # edit permissions
    'Modify portal content':
    ('Manager', 'MeetingMember', 'MeetingServiceHead', 'MeetingOfficeManager',
     'MeetingDivisionHead', 'MeetingReviewer', 'MeetingManager', ),
    'PloneMeeting: Write decision':
    ('Manager', 'MeetingMember', 'MeetingServiceHead', 'MeetingOfficeManager',
     'MeetingDivisionHead', 'MeetingReviewer', 'MeetingManager', ),
    'Review portal content':
    ('Manager', 'MeetingMember', 'MeetingServiceHead', 'MeetingOfficeManager',
     'MeetingDivisionHead', 'MeetingReviewer', 'MeetingManager', ),
    'Add portal content':
    ('Manager', 'MeetingMember', 'MeetingServiceHead', 'MeetingOfficeManager',
     'MeetingDivisionHead', 'MeetingReviewer', 'MeetingManager', ),
    'PloneMeeting: Add annex':
    ('Manager', 'MeetingMember', 'MeetingServiceHead', 'MeetingOfficeManager',
     'MeetingDivisionHead', 'MeetingReviewer', 'MeetingManager', ),
    'PloneMeeting: Add MeetingFile':
    ('Manager', 'MeetingMember', 'MeetingServiceHead', 'MeetingOfficeManager',
     'MeetingDivisionHead', 'MeetingReviewer', 'MeetingManager', ),
    'PloneMeeting: Write decision annex':
    ('Manager', 'MeetingMember', 'MeetingServiceHead', 'MeetingOfficeManager',
     'MeetingDivisionHead', 'MeetingReviewer', 'MeetingManager', ),
    'PloneMeeting: Write optional advisers':
    ('Manager', 'MeetingMember', 'MeetingServiceHead', 'MeetingOfficeManager',
     'MeetingDivisionHead', 'MeetingReviewer', 'MeetingManager', ),
    'PloneMeeting: Write optional advisers':
    ('Manager', 'MeetingMember', 'MeetingServiceHead', 'MeetingOfficeManager',
     'MeetingDivisionHead', 'MeetingReviewer', 'MeetingManager', ),
    'PloneMeeting: Write budget infos':
    ('Manager', 'MeetingMember', 'MeetingOfficeManager', 'MeetingManager', 'MeetingBudgetImpactReviewer', ),
    # MeetingManagers edit permissions
    'Delete objects':
    ['Manager', 'MeetingManager', ],
    'PloneMeeting: Write item observations':
    ('Manager', 'MeetingManager', ),
}

adaptations.RETURN_TO_PROPOSING_GROUP_CUSTOM_PERMISSIONS = RETURN_TO_PROPOSING_GROUP_CUSTOM_PERMISSIONS


class CustomMeeting(Meeting):
    '''Adapter that adapts a meeting implementing IMeeting to the
       interface IMeetingCustom.'''

    implements(IMeetingCustom)
    security = ClassSecurityInfo()

    def __init__(self, meeting):
        self.context = meeting

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
                          privacy='*', oralQuestion='both', toDiscuss='both', categories=[],
                          excludedCategories=[], firstNumber=1, renumber=False):
        '''Returns a list of items.
           An extra list of review states to ignore can be defined.
           A privacy can also be given, and the fact that the item is an
           oralQuestion or not (or both). Idem with toDiscuss.
           Some specific categories can be given or some categories to exchude.
           These 2 parameters are exclusive.  If renumber is True, a list of tuple
           will be returned with first element the number and second element, the item.
           In this case, the firstNumber value can be used.'''
        # We just filter ignore_review_states here and privacy and call
        # getItemsInOrder(uids), passing the correct uids and removing empty
        # uids.
        # privacy can be '*' or 'public' or 'secret'
        # oralQuestion can be 'both' or False or True
        # toDiscuss can be 'both' or 'False' or 'True'
        for elt in itemUids:
            if elt == '':
                itemUids.remove(elt)
        #no filtering, returns the items ordered
        if not categories and not ignore_review_states and privacy == '*' and \
           oralQuestion == 'both' and oralQuestion == 'both' and toDiscuss == 'both':
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
            elif not (toDiscuss == 'both' or obj.getToDiscuss() == toDiscuss):
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

    security.declarePublic('getNumberOfItems')

    def getNumberOfItems(self, itemUids, privacy='*', categories=[], late=False):
        '''Returns the number of items depending on parameters.
           This is used in templates to know how many items of a particular kind exist and
           often used to determine the 'firstNumber' parameter of getPrintableItems/getPrintableItemsByCategory.'''
        # sometimes, some empty elements are inserted in itemUids, remove them...
        itemUids = [itemUid for itemUid in itemUids if itemUid != '']
        #no filtering, return the items ordered
        if not categories and privacy == '*':
            return len(self.context.getItemsInOrder(late=late, uids=itemUids))
        # Either, we will have to filter (privacy, categories, late)
        filteredItemUids = []
        uid_catalog = getToolByName(self.context, 'uid_catalog')
        for itemUid in itemUids:
            obj = uid_catalog(UID=itemUid)[0].getObject()
            if not (privacy == '*' or obj.getPrivacy() == privacy):
                continue
            elif not (categories == [] or obj.getCategory() in categories):
                continue
            elif not obj.isLate() == late:
                continue
            filteredItemUids.append(itemUid)
        return len(filteredItemUids)

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


# ------------------------------------------------------------------------------
class CustomMeetingItem(MeetingItem):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingItemCustom.'''
    implements(IMeetingItemCustom)
    security = ClassSecurityInfo()

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

    def __init__(self, item):
        self.context = item

    security.declarePublic('getDefaultDecision')

    def getDefaultDecision(self):
        '''Returns the default item decision content from the MeetingConfig.'''
        mc = self.portal_plonemeeting.getMeetingConfig(self)
        return mc.getDefaultMeetingItemDecision()
    MeetingItem.getDefaultDecision = getDefaultDecision

    security.declarePublic('getIcons')

    def getIcons(self, inMeeting, meeting):
        '''Check docstring in PloneMeeting interfaces.py.'''
        item = self.getSelf()
        itemState = item.queryState()
        # Default PM item icons
        res = MeetingItem.getIcons(item, inMeeting, meeting)
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

    def getEchevinsForProposingGroup(self):
        '''Returns all echevins defined for the proposing group'''
        res = []
        tool = getToolByName(self.context, 'portal_plonemeeting')
        for group in tool.getMeetingGroups():
            if self.context.getProposingGroup() in group.getEchevinServices():
                res.append(group.id)
        return res

    def _initDecisionFieldIfEmpty(self):
        '''
          If decision field is empty, it will be initialized
          with data coming from title and description.
        '''
        # set keepWithNext to False as it will add a 'class' and so
        # xhtmlContentIsEmpty will never consider it empty...
        if xhtmlContentIsEmpty(self.getDeliberation(keepWithNext=False)):
            self.setDecision("<p>%s</p>%s" % (self.Title(),
                                              self.Description()))
            self.reindexObject()
    MeetingItem._initDecisionFieldIfEmpty = _initDecisionFieldIfEmpty

    security.declarePublic('printAllAnnexes')

    def printAllAnnexes(self):
        ''' Printing Method use in templates :
            return all viewable annexes for item '''
        res = []
        annexesByType = IAnnexable(self.context).getAnnexesByType('item')
        for annexes in annexesByType:
            for annex in annexes:
                title = annex['Title'].replace('&', '&amp;')
                url = getattr(self.context, annex['id']).absolute_url()
                res.append('<a href="%s">%s</a><br/>' % (url, title))
        return ('\n'.join(res))

    security.declarePublic('printFormatedAdvice ')

    def printFormatedAdvice(self):
        ''' Printing Method use in templates :
            return formated advice'''
        res = []
        meetingItem = self.context
        keys = meetingItem.getAdvicesByType().keys()
        for key in keys:
            for advice in meetingItem.getAdvicesByType()[key]:
                if advice['type'] == 'not_given':
                    continue
                comment = ''
                if advice['comment']:
                    comment = advice['comment']
                res.append({'type': meetingItem.i18n(key).encode('utf-8'), 'name': advice['name'].encode('utf-8'),
                            'comment': comment})
        return res

    def getExtraFieldsToCopyWhenCloning(self, cloned_to_same_mc):
        '''
          Keep some new fields when item is cloned (to another mc or from itemtemplate).
        '''
        res = ['validateByBudget']
        if cloned_to_same_mc:
            res = res + []
        return res

    def getCreatorAndValidator(self):
        res = {'creator': self.context.portal_membership.getMemberInfo(str(self.context.Creator()))['fullname'],
               'validator': ''}
        if self.context.queryState() not in ('itemcreated', 'proposed'):
            events = self.context.getHistory()['events']
            for event in events[::-1]:  # parcours inverse
                if event['action'] == 'validate':
                    res['validator'] = self.context.portal_membership.getMemberInfo(event['actor'])['fullname']
                    break
        return res


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
        tool = getToolByName(self, 'portal_plonemeeting')
        # Get every Plone group related to a MeetingGroup
        for group in tool.getMeetingGroups():
            res.append((group.id, group.getProperty('title')))

        return DisplayList(tuple(res))
    MeetingGroup.listEchevinServices = listEchevinServices


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
            realPMGroup = False
            for reviewSuffix in reviewSuffixes:
                if group.endswith(reviewSuffix):
                    realPMGroup = True
                    break
            if not realPMGroup:
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
            params = {'Type': unicode(self.getItemTypeName(), 'utf-8'),
                      'getProposingGroup': foundGroup,
                      'review_state': statesMapping[foundGroups[foundGroup]],
                      'sort_on': sortKey,
                      'sort_order': sortOrder}
            # Manage filter
            if filterKey:
                params[filterKey] = prepareSearchValue(filterValue)
            # update params with kwargs
            params.update(kwargs)
            # Perform the query in portal_catalog
            catalog = getToolByName(self, 'portal_catalog')
            brains = catalog(**params)
            res.extend(brains)
        return res
    MeetingConfig.searchReviewableItems = searchReviewableItems

    security.declarePublic('listCdldProposingGroup')

    def listCdldProposingGroup(self):
        '''Returns a list of groups that can be selected for cdld synthesis field
        '''
        tool = getToolByName(self, 'portal_plonemeeting')
        res = []
        # add delay-aware optionalAdvisers
        customAdvisers = self.getSelf().getCustomAdvisers()
        for customAdviser in customAdvisers:
            groupId = customAdviser['group']
            groupDelay = customAdviser['delay']
            groupDelayLabel = customAdviser['delay_label']
            group = getattr(tool, groupId, None)
            groupKey = '%s__%s__(%s)' % (groupId, groupDelay, groupDelayLabel)
            groupValue = '%s - %s (%s)' % (group.Title(), groupDelay, groupDelayLabel)
            if group:
                res.append((groupKey, groupValue))
        # only let select groups for which there is at least one user in
        nonEmptyMeetingGroups = tool.getMeetingGroups(notEmptySuffix='advisers')
        if nonEmptyMeetingGroups:
            for mGroup in nonEmptyMeetingGroups:
                res.append(('%s____' % mGroup.getId(), mGroup.getName()))
        res = DisplayList(res)
        return res
    MeetingConfig.listCdldProposingGroup = listCdldProposingGroup

    security.declarePublic('searchCDLDItems')

    def searchCDLDItems(self, sortKey='', sortOrder='', filterKey='', filterValue='', **kwargs):
        '''Queries all items for cdld synthesis'''
        groups = []
        cdldProposingGroups = self.getSelf().getCdldProposingGroup()
        for cdldProposingGroup in cdldProposingGroups:
            groupId = cdldProposingGroup.split('__')[0]
            delay = ''
            if cdldProposingGroup.split('__')[1]:
                delay = 'delay__'
            groups.append('%s%s' % (delay, groupId))
        # advised items are items that has an advice in a particular review_state
        # just append every available meetingadvice state: we want "given" advices.
        # this search will only return 'delay-aware' advices
        wfTool = getToolByName(self, 'portal_workflow')
        adviceWF = wfTool.getWorkflowsFor('meetingadvice')[0]
        adviceStates = adviceWF.states.keys()
        groupIds = []
        advice_index__suffixs = ('advice_delay_exceeded', 'advice_not_given', 'advice_not_giveable')
        # advice given
        for adviceState in adviceStates:
            groupIds += [g + '_%s' % adviceState for g in groups]
        #advice not given
        for advice_index__suffix in advice_index__suffixs:
            groupIds += [g + '_%s' % advice_index__suffix for g in groups]
        # Create query parameters
        fromDate = DateTime(2013, 01, 01)
        toDate = DateTime(2014, 12, 31, 23, 59)
        params = {'portal_type': self.getItemTypeName(),
                  # KeywordIndex 'indexAdvisers' use 'OR' by default
                  'indexAdvisers': groupIds,
                  'created': {'query': [fromDate, toDate], 'range': 'minmax'},
                  'sort_on': sortKey,
                  'sort_order': sortOrder, }
        # Manage filter
        if filterKey:
            params[filterKey] = prepareSearchValue(filterValue)
        # update params with kwargs
        params.update(kwargs)
        # Perform the query in portal_catalog
        brains = self.portal_catalog(**params)
        res = []
        fromDate = DateTime(2014, 01, 01)  # redefine date to get advice in 2014
        for brain in brains:
            obj = brain.getObject()
            if obj.getMeeting() and obj.getMeeting().getDate() >= fromDate and obj.getMeeting().getDate() <= toDate:
                res.append(brain)
        return res
    MeetingConfig.searchCDLDItems = searchCDLDItems

    security.declarePublic('printCDLDItems')

    def printCDLDItems(self):
        '''
        Returns a list of advice for synthesis document (CDLD)
        '''
        meetingConfig = self.getSelf()
        brains = meetingConfig.context.searchCDLDItems()
        res = []
        groups = []
        cdldProposingGroups = meetingConfig.getCdldProposingGroup()
        for cdldProposingGroup in cdldProposingGroups:
            groupId = cdldProposingGroup.split('__')[0]
            delay = False
            if cdldProposingGroup.split('__')[1]:
                delay = True
            if not (groupId, delay) in groups:
                groups.append((groupId, delay))
        for brain in brains:
            item = brain.getObject()
            advicesIndex = item.adviceIndex
            for groupId, delay in groups:
                if groupId in advicesIndex:
                    advice = advicesIndex[groupId]
                    if advice['delay'] and not delay:
                        continue
                    if not (advice, item) in res:
                        res.append((advice, item))
        return res


# ------------------------------------------------------------------------------
class MeetingCollegeMonsWorkflowActions(MeetingWorkflowActions):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingCollegeWorkflowActions'''

    implements(IMeetingCollegeMonsWorkflowActions)
    security = ClassSecurityInfo()

    security.declarePrivate('doDecide')

    def doDecide(self, stateChange):
        '''We pass every item that is 'presented' in the 'itemfrozen'
           state.  It is the case for late items. '''
        wfTool = getToolByName(self.context, 'portal_workflow')
        for item in self.context.getAllItems(ordered=True):
            if item.queryState() == 'presented':
                wfTool.doActionFor(item, 'itemfreeze')


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
                res = No(translate('item_required_to_publish', domain='PloneMeeting', context=self.context.REQUEST))
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
        if checkPermission(ReviewPortalContent, self.context):
            res = True
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
        '''After cloned item, we validate this item'''
        MeetingItemWorkflowActions(self.context).doDelay(stateChange)
        clonedItem = self.context.getBRefs('ItemPredecessor')[0]
        self.context.portal_workflow.doActionFor(clonedItem, 'validate')


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

    def mayDecide(self):
        '''We may decide an item if the linked meeting is in relevant state.'''
        res = False
        meeting = self.context.getMeeting()
        if checkPermission(ReviewPortalContent, self.context) and \
           meeting and meeting.adapted().isDecided():
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
        if not self.context.getCategory():
            return No(translate('required_category_ko',
                                domain="PloneMeeting",
                                context=self.context.REQUEST))
        user = self.context.portal_membership.getAuthenticatedMember()
        #first of all, the use must have the 'Review portal content permission'
        if checkPermission(ReviewPortalContent, self.context) and \
                (user.has_role('MeetingReviewer', self.context) or user.has_role('Manager', self.context)):
            res = True
            #if the current item state is 'itemcreated', only the MeetingManager can validate
            if self.context.queryState() in ('itemcreated',) and \
                    not self.context.portal_plonemeeting.isManager(self.context):
                res = False
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
        if not self.context.getCategory():
            return No(translate('required_category_ko',
                                domain="PloneMeeting",
                                context=self.context.REQUEST))
        #if item have budget info, budget reviewer must validate it
        isValidateByBudget = not self.context.getBudgetRelated() or self.context.getValidateByBudget() or \
            self.context.portal_plonemeeting.isManager(self.context)
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
        if not self.context.getCategory():
            return No(translate('required_category_ko',
                                domain="PloneMeeting",
                                context=self.context.REQUEST))
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

    security.declarePrivate('doSetInCouncil')

    def doSetInCouncil(self, stateChange):
        '''When setting the meeting in council, every items must be automatically
           set to "item_in_council".'''
        for item in self.context.getAllItems(ordered=True):
            if item.queryState() == 'presented':
                self.context.portal_workflow.doActionFor(item, 'setItemInCommittee')
            if item.queryState() == 'item_in_committee':
                self.context.portal_workflow.doActionFor(item, 'setItemInCouncil')

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
        self.transitionsForPresentingAnItem = ('proposeToServiceHead',
                                               'proposeToOfficeManager',
                                               'proposeToDivisionHead',
                                               'proposeToDirector',
                                               'validate',
                                               'present')

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
InitializeClass(CustomMeeting)
InitializeClass(CustomMeetingItem)
InitializeClass(CustomMeetingGroup)
InitializeClass(CustomMeetingConfig)
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
