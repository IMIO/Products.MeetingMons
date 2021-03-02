# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Copyright (c) 2017 by Imio.be
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

from collections import OrderedDict

from Products.MeetingMons import logger
from Products.MeetingMons.config import FINANCE_ADVICES_COLLECTION_ID
from Products.MeetingMons.config import FINANCE_GROUP_SUFFIXES
from Products.MeetingMons.config import FINANCE_WAITING_ADVICES_STATES
from Products.MeetingMons.interfaces import IMeetingCollegeMonsWorkflowActions
from Products.MeetingMons.interfaces import IMeetingCollegeMonsWorkflowConditions
from Products.MeetingMons.interfaces import IMeetingItemCollegeMonsWorkflowActions
from Products.MeetingMons.interfaces import IMeetingItemCollegeMonsWorkflowConditions

from Products.MeetingCommunes.adapters import CustomMeeting as MCMeeting
from Products.MeetingCommunes.adapters import CustomMeetingItem as MCMeetingItem
from Products.MeetingCommunes.adapters import CustomMeetingConfig as MCMeetingConfig
from Products.MeetingCommunes.adapters import CustomToolPloneMeeting as MCToolPloneMeeting
from Products.MeetingCommunes.adapters import MeetingItemCommunesWorkflowActions
from Products.MeetingCommunes.adapters import MeetingItemCommunesWorkflowConditions
from Products.MeetingCommunes.adapters import MeetingCommunesWorkflowActions
from Products.MeetingCommunes.adapters import MeetingCommunesWorkflowConditions

from Products.PloneMeeting.MeetingConfig import MeetingConfig
from Products.PloneMeeting.MeetingItem import MeetingItem
from Products.PloneMeeting.adapters import CompoundCriterionBaseAdapter, ItemPrettyLinkAdapter
from Products.PloneMeeting.interfaces import IMeetingConfigCustom
from Products.PloneMeeting.interfaces import IMeetingCustom
from Products.PloneMeeting.interfaces import IMeetingItemCustom
from Products.PloneMeeting.interfaces import IToolPloneMeetingCustom
from Products.PloneMeeting.model import adaptations
from Products.PloneMeeting.model.adaptations import WF_APPLIED

from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from AccessControl.class_init import InitializeClass
from Products.CMFCore.permissions import ReviewPortalContent, ModifyPortalContent
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from appy.gen import No
from imio.helpers.xhtml import xhtmlContentIsEmpty
from plone import api
from plone.memoize import ram
from zope.i18n import translate
from zope.interface import implements

MeetingConfig.wfAdaptations = (
'return_to_proposing_group', 'hide_decisions_when_under_writing', 'postpone_next_meeting',)

# states taken into account by the 'no_global_observation' wfAdaptation
noGlobalObsStates = ('itempublished', 'itemfrozen', 'accepted', 'refused',
                     'delayed', 'accepted_but_modified', 'pre_accepted')
adaptations.noGlobalObsStates = noGlobalObsStates

adaptations.RETURN_TO_PROPOSING_GROUP_FROM_ITEM_STATES = ('presented', 'itemfrozen',)

adaptations.WF_NOT_CREATOR_EDITS_UNLESS_CLOSED = ('delayed', 'refused', 'accepted',
                                                  'pre_accepted', 'accepted_but_modified')

RETURN_TO_PROPOSING_GROUP_STATE_TO_CLONE = {
    'meetingitemcollegemons_workflow': 'meetingitemcollegemons_workflow.itemcreated'}
adaptations.RETURN_TO_PROPOSING_GROUP_STATE_TO_CLONE = RETURN_TO_PROPOSING_GROUP_STATE_TO_CLONE

RETURN_TO_PROPOSING_GROUP_CUSTOM_PERMISSIONS = {'meetingitemcollegemons_workflow':
    {
        # view permissions
        'Access contents information':
            ('Manager', 'MeetingManager', 'MeetingMember', 'MeetingServiceHead', 'MeetingOfficeManager',
             'MeetingDivisionHead', 'MeetingReviewer', 'MeetingObserverLocal', 'Reader',),
        'View':
            ('Manager', 'MeetingManager', 'MeetingMember', 'MeetingServiceHead', 'MeetingOfficeManager',
             'MeetingDivisionHead', 'MeetingReviewer', 'MeetingObserverLocal', 'Reader',),
        'PloneMeeting: Read decision':
            ('Manager', 'MeetingManager', 'MeetingMember', 'MeetingServiceHead', 'MeetingOfficeManager',
             'MeetingDivisionHead', 'MeetingReviewer', 'MeetingObserverLocal', 'Reader',),
        'PloneMeeting: Read optional advisers':
            ('Manager', 'MeetingManager', 'MeetingMember', 'MeetingServiceHead', 'MeetingOfficeManager',
             'MeetingDivisionHead', 'MeetingReviewer', 'MeetingObserverLocal', 'Reader',),
        'PloneMeeting: Read decision annex':
            ('Manager', 'MeetingManager', 'MeetingMember', 'MeetingServiceHead', 'MeetingOfficeManager',
             'MeetingDivisionHead', 'MeetingReviewer', 'MeetingObserverLocal', 'Reader',),
        'PloneMeeting: Read item observations':
            ('Manager', 'MeetingManager', 'MeetingMember', 'MeetingServiceHead', 'MeetingOfficeManager',
             'MeetingDivisionHead', 'MeetingReviewer', 'MeetingObserverLocal', 'Reader',),
        'PloneMeeting: Read budget infos':
            ('Manager', 'MeetingManager', 'MeetingMember', 'MeetingServiceHead', 'MeetingOfficeManager',
             'MeetingDivisionHead', 'MeetingReviewer', 'MeetingObserverLocal', 'MeetingBudgetImpactReviewer',
             'Reader',),
        # edit permissions
        'Modify portal content':
            ('Manager', 'MeetingMember', 'MeetingServiceHead', 'MeetingOfficeManager',
             'MeetingDivisionHead', 'MeetingReviewer', 'MeetingManager',),
        'PloneMeeting: Write decision':
            ('Manager', 'MeetingMember', 'MeetingServiceHead', 'MeetingOfficeManager',
             'MeetingDivisionHead', 'MeetingReviewer', 'MeetingManager',),
        'Review portal content':
            ('Manager', 'MeetingMember', 'MeetingServiceHead', 'MeetingOfficeManager',
             'MeetingDivisionHead', 'MeetingReviewer', 'MeetingManager',),
        'Add portal content':
            ('Manager', 'MeetingMember', 'MeetingServiceHead', 'MeetingOfficeManager',
             'MeetingDivisionHead', 'MeetingReviewer', 'MeetingManager',),
        'PloneMeeting: Add annex':
            ('Manager', 'MeetingMember', 'MeetingServiceHead', 'MeetingOfficeManager',
             'MeetingDivisionHead', 'MeetingReviewer', 'MeetingManager',),
        'PloneMeeting: Add annexDecision':
            ('Manager', 'MeetingMember', 'MeetingServiceHead', 'MeetingOfficeManager',
             'MeetingDivisionHead', 'MeetingReviewer', 'MeetingManager',),
        'PloneMeeting: Add MeetingFile':
            ('Manager', 'MeetingMember', 'MeetingServiceHead', 'MeetingOfficeManager',
             'MeetingDivisionHead', 'MeetingReviewer', 'MeetingManager',),
        'PloneMeeting: Write optional advisers':
            ('Manager', 'MeetingMember', 'MeetingServiceHead', 'MeetingOfficeManager',
             'MeetingDivisionHead', 'MeetingReviewer', 'MeetingManager',),
        'PloneMeeting: Write budget infos':
            ('Manager', 'MeetingMember', 'MeetingOfficeManager', 'MeetingManager', 'MeetingBudgetImpactReviewer',),
        'PloneMeeting: Write marginal notes':
            ('Manager', 'MeetingManager',),
        # MeetingManagers edit permissions
        'Delete objects':
            ('Manager', 'MeetingManager',),
        'PloneMeeting: Write item observations':
            ('Manager', 'MeetingManager',),
        'PloneMeeting: Write item MeetingManager reserved fields':
            ('Manager', 'MeetingManager',),
    }
}

adaptations.RETURN_TO_PROPOSING_GROUP_CUSTOM_PERMISSIONS = RETURN_TO_PROPOSING_GROUP_CUSTOM_PERMISSIONS


class CustomMeeting(MCMeeting):
    '''Adapter that adapts a meeting implementing IMeeting to the
       interface IMeetingCustom.'''

    implements(IMeetingCustom)
    security = ClassSecurityInfo()

    def __init__(self, meeting):
        self.context = meeting


class CustomMeetingItem(MCMeetingItem):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingItemCustom.'''
    implements(IMeetingItemCustom)
    security = ClassSecurityInfo()

    def __init__(self, item):
        self.context = item

    def getExtraFieldsToCopyWhenCloning(self, cloned_to_same_mc, cloned_from_item_template):
        '''
          Keep some new fields when item is cloned (to another mc or from itemtemplate).
        '''
        return ['validateByBudget']


class CustomMeetingConfig(MCMeetingConfig):
    '''Adapter that adapts a meetingConfig implementing IMeetingConfig to the
       interface IMeetingConfigCustom.'''

    implements(IMeetingConfigCustom)
    security = ClassSecurityInfo()

    def __init__(self, item):
        self.context = item

    def _extraSearchesInfo(self, infos):
        """Add some specific searches."""
        cfg = self.getSelf()
        itemType = cfg.getItemTypeName()
        extra_infos = OrderedDict(
            [
                # Items in state 'proposed_to_budgetimpact_reviewer'
                ('searchbudgetimpactreviewersitems',
                 {
                     'subFolderId': 'searches_items',
                     'active': True,
                     'query':
                         [
                             {'i': 'portal_type',
                              'o': 'plone.app.querystring.operation.selection.is',
                              'v': [itemType, ]},
                             {'i': 'review_state',
                              'o': 'plone.app.querystring.operation.selection.is',
                              'v': ['proposed_to_budgetimpact_reviewer']}
                         ],
                     'sort_on': u'created',
                     'sort_reversed': True,
                     'showNumberOfItems': False,
                     'tal_condition': 'python: here.portal_plonemeeting.userIsAmong("budgetimpactreviewers")',
                     'roles_bypassing_talcondition': ['Manager', ]
                 }),
                # Items in state 'proposed_to_extraordinarybudget'
                ('searchextraordinarybudgetsitems',
                 {
                     'subFolderId': 'searches_items',
                     'active': True,
                     'query':
                         [
                             {'i': 'portal_type',
                              'o': 'plone.app.querystring.operation.selection.is',
                              'v': [itemType, ]},
                             {'i': 'review_state',
                              'o': 'plone.app.querystring.operation.selection.is',
                              'v': ['proposed_to_extraordinarybudget']}
                         ],
                     'sort_on': u'created',
                     'sort_reversed': True,
                     'showNumberOfItems': False,
                     'tal_condition': 'python:  here.portal_plonemeeting.userIsAmong("extraordinarybudget")',
                     'roles_bypassing_talcondition': ['Manager', ]
                 }),
                # Items in state 'proposed_to_servicehead'
                ('searchserviceheaditems',
                 {
                     'subFolderId': 'searches_items',
                     'active': True,
                     'query':
                         [
                             {'i': 'portal_type',
                              'o': 'plone.app.querystring.operation.selection.is',
                              'v': [itemType, ]},
                             {'i': 'review_state',
                              'o': 'plone.app.querystring.operation.selection.is',
                              'v': ['proposed_to_servicehead']}
                         ],
                     'sort_on': u'created',
                     'sort_reversed': True,
                     'showNumberOfItems': False,
                     'tal_condition': 'python: here.portal_plonemeeting.userIsAmong("serviceheads")',
                     'roles_bypassing_talcondition': ['Manager', ]
                 }),
                # Items in state 'proposed_to_officemanager'
                ('searchofficemanageritems',
                 {
                     'subFolderId': 'searches_items',
                     'active': True,
                     'query':
                         [
                             {'i': 'portal_type',
                              'o': 'plone.app.querystring.operation.selection.is',
                              'v': [itemType, ]},
                             {'i': 'review_state',
                              'o': 'plone.app.querystring.operation.selection.is',
                              'v': ['proposed_to_officemanager']}
                         ],
                     'sort_on': u'created',
                     'sort_reversed': True,
                     'showNumberOfItems': False,
                     'tal_condition': 'python: here.portal_plonemeeting.userIsAmong("officemanagers")',
                     'roles_bypassing_talcondition': ['Manager', ]
                 }),
                # Items in state 'proposed_to_divisionhead
                ('searchdivisionheaditems',
                 {
                     'subFolderId': 'searches_items',
                     'active': True,
                     'query':
                         [
                             {'i': 'portal_type',
                              'o': 'plone.app.querystring.operation.selection.is',
                              'v': [itemType, ]},
                             {'i': 'review_state',
                              'o': 'plone.app.querystring.operation.selection.is',
                              'v': ['proposed_to_divisionhead']}
                         ],
                     'sort_on': u'created',
                     'sort_reversed': True,
                     'showNumberOfItems': False,
                     'tal_condition': 'python: here.portal_plonemeeting.userIsAmong("divisionheads")',
                     'roles_bypassing_talcondition': ['Manager', ]
                 }),
                # Items in state 'proposed_to_director'
                ('searchdirectoritems',
                 {
                     'subFolderId': 'searches_items',
                     'active': True,
                     'query':
                         [
                             {'i': 'portal_type',
                              'o': 'plone.app.querystring.operation.selection.is',
                              'v': [itemType, ]},
                             {'i': 'review_state',
                              'o': 'plone.app.querystring.operation.selection.is',
                              'v': ['proposed_to_director']}
                         ],
                     'sort_on': u'created',
                     'sort_reversed': True,
                     'showNumberOfItems': False,
                     'tal_condition': 'python: here.portal_plonemeeting.userIsAmong("reviewers")',
                     'roles_bypassing_talcondition': ['Manager', ]
                 }),
                # Items in state 'validated'
                ('searchvalidateditems',
                 {
                     'subFolderId': 'searches_items',
                     'active': True,
                     'query':
                         [
                             {'i': 'portal_type',
                              'o': 'plone.app.querystring.operation.selection.is',
                              'v': [itemType, ]},
                             {'i': 'review_state',
                              'o': 'plone.app.querystring.operation.selection.is',
                              'v': ['validated']}
                         ],
                     'sort_on': u'created',
                     'sort_reversed': True,
                     'showNumberOfItems': False,
                     'tal_condition': "",
                     'roles_bypassing_talcondition': ['Manager', ]
                 }
                 ),
                # Items for finance advices synthesis
                (FINANCE_ADVICES_COLLECTION_ID,
                 {
                     'subFolderId': 'searches_items',
                     'active': True,
                     'query':
                         [
                             {'i': 'portal_type',
                              'o': 'plone.app.querystring.operation.selection.is',
                              'v': [itemType, ]},
                             {'i': 'indexAdvisers',
                              'o': 'plone.app.querystring.operation.selection.is',
                              'v': ['delay_real_group_id__unique_id_002',
                                    'delay_real_group_id__unique_id_003',
                                    'delay_real_group_id__unique_id_004']}
                         ],
                     'sort_on': u'created',
                     'sort_reversed': True,
                     'showNumberOfItems': False,
                     'tal_condition':
                         "python: tool.userIsAmong(['budgetimpacteditors']) or tool.isManager(here)",
                     'roles_bypassing_talcondition': ['Manager', ]
                 }
                 ),
            ]
        )
        infos.update(extra_infos)

        # disable FINANCE_ADVICES_COLLECTION_ID excepted for 'meeting-config-college' and 'meeting-config-bp'
        if cfg.getId() not in ('meeting-config-college', 'meeting-config-bp'):
            infos[FINANCE_ADVICES_COLLECTION_ID]['active'] = False

        return infos


class MeetingCollegeMonsWorkflowActions(MeetingCommunesWorkflowActions):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingCollegeMonsWorkflowActions'''

    implements(IMeetingCollegeMonsWorkflowActions)
    security = ClassSecurityInfo()

    security.declarePrivate('doDecide')

    def doDecide(self, stateChange):
        '''We pass every item that is 'presented' in the 'itemfrozen'
           state.  It is the case for late items. Moreover, if
           MeetingConfig.initItemDecisionIfEmptyOnDecide is True, we
           initialize the decision field with content of Title+Description
           if decision field is empty.'''
        tool = getToolByName(self.context, 'portal_plonemeeting')
        cfg = tool.getMeetingConfig(self.context)
        if cfg.getInitItemDecisionIfEmptyOnDecide():
            for item in self.context.getItems():
                # If deliberation (motivation+decision) is empty,
                # initialize it the decision field
                item._initDecisionFieldIfEmpty()


class MeetingCollegeMonsWorkflowConditions(MeetingCommunesWorkflowConditions):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingCollegeMonsWorkflowConditions'''

    implements(IMeetingCollegeMonsWorkflowConditions)
    security = ClassSecurityInfo()


class MeetingItemCollegeMonsWorkflowActions(MeetingItemCommunesWorkflowActions):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingItemCollegeMonsWorkflowActions'''

    implements(IMeetingItemCollegeMonsWorkflowActions)
    security = ClassSecurityInfo()

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


class MeetingItemCollegeMonsWorkflowConditions(MeetingItemCommunesWorkflowConditions):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingItemCollegeMonsWorkflowConditions'''

    implements(IMeetingItemCollegeMonsWorkflowConditions)
    security = ClassSecurityInfo()

    def __init__(self, item):
        self.context = item  # Implements IMeetingItem

    security.declarePublic('mayValidate')

    def mayValidate(self):
        """
          Either the Director or the MeetingManager can validate
          The MeetingManager can bypass the validation process and validate an item
          that is in the state 'itemcreated'
        """
        res = False
        # Check if there are category and groupsInCharge, if applicable
        msg = self._check_required_data()
        if msg is not None:
            return msg
        user = self.context.portal_membership.getAuthenticatedMember()
        # first of all, the use must have the 'Review portal content permission'
        if _checkPermission(ReviewPortalContent, self.context) and \
                (user.has_role('MeetingReviewer', self.context) or self.context.portal_plonemeeting.isManager(self.context)):
            res = True
            # if the current item state is 'itemcreated', only the MeetingManager can validate
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
        if _checkPermission(ReviewPortalContent, self.context):
            res = True
        return res

    security.declarePublic('mayProposeToServiceHead')

    def mayProposeToServiceHead(self):
        """
          Check that the user has the 'Review portal content'
        """
        # Check if there are category and groupsInCharge, if applicable
        msg = self._check_required_data()
        if msg is not None:
            return msg

        res = False
        # if item have budget info, budget reviewer must validate it
        isValidateByBudget = not self.context.getBudgetRelated() or self.context.getValidateByBudget() or \
                             self.context.portal_plonemeeting.isManager(self.context)
        if _checkPermission(ReviewPortalContent, self.context) and isValidateByBudget:
            res = True
        return res

    security.declarePublic('mayProposeToOfficeManager')

    def mayProposeToOfficeManager(self):
        """
          Check that the user has the 'Review portal content'
        """
        # Check if there are category and groupsInCharge, if applicable
        msg = self._check_required_data()
        if msg is not None:
            return msg

        res = False
        if _checkPermission(ReviewPortalContent, self.context):
            res = True
        return res

    security.declarePublic('mayProposeToDivisionHead')

    def mayProposeToDivisionHead(self):
        """
          Check that the user has the 'Review portal content'
        """
        # Check if there are category and groupsInCharge, if applicable
        msg = self._check_required_data()
        if msg is not None:
            return msg

        res = False
        if _checkPermission(ReviewPortalContent, self.context):
            res = True
        return res

    security.declarePublic('mayProposeToDirector')

    def mayProposeToDirector(self):
        """
          Check that the user has the 'Review portal content'
        """
        # Check if there are category and groupsInCharge, if applicable
        msg = self._check_required_data()
        if msg is not None:
            return msg

        res = False
        if _checkPermission(ReviewPortalContent, self.context):
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
        if _checkPermission(ReviewPortalContent, self.context) and \
                meeting and (meeting.queryState() in ['decided', 'closed']):
            res = True
        return res

    security.declarePublic('mayValidateByBudgetImpactReviewer')

    def mayValidateByBudgetImpactReviewer(self):
        """
          Check that the user has the 'Review portal content'
        """
        # Check if there are category and groupsInCharge, if applicable
        msg = self._check_required_data()
        if msg is not None:
            return msg

        res = False
        if _checkPermission(ReviewPortalContent, self.context):
            res = True
        return res

    security.declarePublic('mayProposeToBudgetImpactReviewer')

    def mayProposeToBudgetImpactReviewer(self):
        """
          Check that the user has the 'Review portal content'
        """
        # Check if there are category and groupsInCharge, if applicable
        msg = self._check_required_data()
        if msg is not None:
            return msg

        res = False
        if not self.context.getCategory():
            return No(translate('required_category_ko',
                                domain="PloneMeeting",
                                context=self.context.REQUEST))
        if _checkPermission(ReviewPortalContent, self.context):
            res = True
        return res

    security.declarePublic('mayValidateByExtraordinaryBudget')

    def mayValidateByExtraordinaryBudget(self):
        """
          Check that the user has the 'Review portal content'
        """
        # Check if there are category and groupsInCharge, if applicable
        msg = self._check_required_data()
        if msg is not None:
            return msg

        res = False
        if _checkPermission(ReviewPortalContent, self.context):
            res = True
        return res

    security.declarePublic('mayProposeToExtraordinaryBudget')

    def mayProposeToExtraordinaryBudget(self):
        """
          Check that the user has the 'Review portal content'
        """
        # Check if there are category and groupsInCharge, if applicable
        msg = self._check_required_data()
        if msg is not None:
            return msg

        res = False
        if _checkPermission(ReviewPortalContent, self.context):
            res = True
        return res


class CustomToolPloneMeeting(MCToolPloneMeeting):
    '''Adapter that adapts a tool implementing ToolPloneMeeting to the
       interface IToolPloneMeetingCustom'''

    implements(IToolPloneMeetingCustom)
    security = ClassSecurityInfo()

    def __init__(self, item):
        self.context = item

    def performCustomWFAdaptations(self, meetingConfig, wfAdaptation, logger, itemWorkflow, meetingWorkflow):
        """ """
        if wfAdaptation == 'no_publication':
            # we override the PloneMeeting's 'no_publication' wfAdaptation
            # First, update the meeting workflow
            wf = meetingWorkflow
            # Delete transitions 'publish' and 'backToPublished'
            for tr in ('publish', 'backToPublished'):
                if tr in wf.transitions:
                    wf.transitions.deleteTransitions([tr])
            # Update connections between states and transitions
            wf.states['frozen'].setProperties(
                title='frozen', description='',
                transitions=['backToCreated', 'decide'])
            wf.states['decided'].setProperties(
                title='decided', description='', transitions=['backToFrozen', 'close'])
            # Delete state 'published'
            if 'published' in wf.states:
                wf.states.deleteStates(['published'])
            # Then, update the item workflow.
            wf = itemWorkflow
            # Delete transitions 'itempublish' and 'backToItemPublished'
            for tr in ('itempublish', 'backToItemPublished'):
                if tr in wf.transitions:
                    wf.transitions.deleteTransitions([tr])
            # Update connections between states and transitions
            wf.states['itemfrozen'].setProperties(
                title='itemfrozen', description='',
                transitions=['accept', 'accept_but_modify', 'refuse', 'delay', 'pre_accept', 'backToPresented'])
            for decidedState in ['accepted', 'refused', 'delayed', 'accepted_but_modified']:
                wf.states[decidedState].setProperties(
                    title=decidedState, description='',
                    transitions=['backToItemFrozen', ])
            wf.states['pre_accepted'].setProperties(
                title='pre_accepted', description='',
                transitions=['accept', 'accept_but_modify', 'backToItemFrozen'])
            # Delete state 'published'
            if 'itempublished' in wf.states:
                wf.states.deleteStates(['itempublished'])
            logger.info(WF_APPLIED % ("no_publication", meetingConfig.getId()))
            return True
        return False


# ------------------------------------------------------------------------------
InitializeClass(CustomMeeting)
InitializeClass(CustomMeetingItem)
InitializeClass(CustomMeetingConfig)
InitializeClass(MeetingCollegeMonsWorkflowActions)
InitializeClass(MeetingCollegeMonsWorkflowConditions)
InitializeClass(MeetingItemCollegeMonsWorkflowActions)
InitializeClass(MeetingItemCollegeMonsWorkflowConditions)
InitializeClass(CustomToolPloneMeeting)
# ------------------------------------------------------------------------------


class MMItemPrettyLinkAdapter(ItemPrettyLinkAdapter):
    """
      Override to take into account MeetingMons use cases...
    """

    def _leadingIcons(self):
        """
          Manage icons to display before the icons managed by PrettyLink._icons.
        """
        # Default PM item icons
        icons = super(MMItemPrettyLinkAdapter, self)._leadingIcons()

        if self.context.isDefinedInTool():
            return icons

        itemState = self.context.queryState()
        # Add our icons for some review states
        if itemState == 'proposed_to_budgetimpact_reviewer':
            icons.append(('proposeToBudgetImpactReviewer.png',
                          translate('icon_help_proposed',
                                    domain="PloneMeeting",
                                    context=self.request)))

        if itemState == 'proposed_to_extraordinarybudget':
            icons.append(('proposeToExtraordinaryBudget.png',
                          translate('icon_help_proposed',
                                    domain="PloneMeeting",
                                    context=self.request)))

        if itemState == 'proposed_to_servicehead':
            icons.append(('proposeToServiceHead.png',
                          translate('icon_help_proposed',
                                    domain="PloneMeeting",
                                    context=self.request)))

        if itemState == 'proposed_to_officemanager':
            icons.append(('proposeToOfficeManager.png',
                          translate('icon_help_proposed',
                                    domain="PloneMeeting",
                                    context=self.request)))

        if itemState == 'proposed_to_divisionhead':
            icons.append(('proposeToDivisionHead.png',
                          translate('icon_help_proposed',
                                    domain="PloneMeeting",
                                    context=self.request)))

        if itemState == 'proposed_to_director':
            icons.append(('proposeToDirector.png',
                          translate('icon_help_proposed',
                                    domain="PloneMeeting",
                                    context=self.request)))

        return icons
