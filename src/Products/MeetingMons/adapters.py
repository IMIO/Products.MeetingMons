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

    security.declarePublic('getDefaultDecision')

    def getDefaultDecision(self):
        '''Returns the default item decision content from the MeetingConfig.'''
        mc = self.portal_plonemeeting.getMeetingConfig(self)
        return mc.getDefaultMeetingItemDecision()

    MeetingItem.getDefaultDecision = getDefaultDecision

    def getExtraFieldsToCopyWhenCloning(self, cloned_to_same_mc, cloned_from_item_template):
        '''
          Keep some new fields when item is cloned (to another mc or from itemtemplate).
        '''
        return ['validateByBudget']

    def showDuplicateItemAction(self):
        '''Condition for displaying the 'duplicate' action in the interface.
           Returns True if the user can duplicate the item.'''
        # Conditions for being able to see the "duplicate an item" action:
        # - the user is not Plone-disk-aware;
        # - the user is creator in some group;
        # - the user must be able to see the item if it is private.
        # - the item isn't delayed
        # The user will duplicate the item in his own folder.
        tool = getToolByName(self, 'portal_plonemeeting')
        cfg = tool.getMeetingConfig(self)
        if not cfg.getEnableItemDuplication() or self.isDefinedInTool() or not tool.userIsAmong(
                ['creators']) or not self.adapted().isPrivacyViewable() or self.queryState() == 'delayed':
            return False
        return True

    MeetingItem.showDuplicateItemAction = showDuplicateItemAction

    def getFinanceAdviceId(self):
        """ """
        tool = api.portal.get_tool('portal_plonemeeting')
        cfg = tool.getMeetingConfig(self.context)
        usedFinanceGroupIds = cfg.adapted().getUsedFinanceGroupIds(self.context)
        adviserIds = self.context.adviceIndex.keys()
        financeAdvisersIds = set(usedFinanceGroupIds).intersection(set(adviserIds))
        if financeAdvisersIds:
            return list(financeAdvisersIds)[0]
        else:
            return None

    def _initDecisionFieldIfEmpty(self):
        '''
          If decision field is empty, it will be initialized
          with data coming from title and description.
        '''
        # set keepWithNext to False as it will add a 'class' and so
        # xhtmlContentIsEmpty will never consider it empty...
        if xhtmlContentIsEmpty(self.getDecision(keepWithNext=False)):
            self.setDecision("<p>%s</p>%s" % (self.Title(),
                                              self.Description()))
            self.reindexObject()

    MeetingItem._initDecisionFieldIfEmpty = _initDecisionFieldIfEmpty

    def adviceDelayIsTimedOutWithRowId(self, groupId, rowIds=[]):
        ''' Check if advice with delay from a certain p_groupId and with
            a row_id contained in p_rowIds is timed out.
        '''
        self = self.getSelf()
        if self.getAdviceDataFor(self) and groupId in self.getAdviceDataFor(self):
            adviceRowId = self.getAdviceDataFor(self, groupId)['row_id']
        else:
            return False

        if not rowIds or adviceRowId in rowIds:
            return self._adviceDelayIsTimedOut(groupId)
        else:
            return False

    def showFinanceAdviceTemplate(self):
        """ """
        item = self.getSelf()
        tool = api.portal.get_tool('portal_plonemeeting')
        cfg = tool.getMeetingConfig(item)
        return bool(set(cfg.adapted().getUsedFinanceGroupIds(item)).
                    intersection(set(item.adviceIndex.keys())))


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
                         "python: '%s_budgetimpacteditors' % cfg.getId() in member.getGroups() or "
                         "tool.isManager(here)",
                     'roles_bypassing_talcondition': ['Manager', ]
                 }
                 ),
                # Items in state under 'validated' and not modified since 60 days
                ('searchblockeditems', {
                    'subFolderId': 'searches_items',
                    'active': True,
                    'query':
                        [
                            {'i': 'CompoundCriterion',
                             'o': 'plone.app.querystring.operation.compound.is',
                             'v': 'blocked-items'},
                        ],
                    'sort_on': u'modified',
                    'sort_reversed': False,
                    'showNumberOfItems': True,
                    'tal_condition': '',
                    'roles_bypassing_talcondition': ['Manager', ]
                }),
            ]
        )
        infos.update(extra_infos)

        # disable FINANCE_ADVICES_COLLECTION_ID excepted for 'meeting-config-college' and 'meeting-config-bp'
        if cfg.getId() not in ('meeting-config-college', 'meeting-config-bp'):
            infos[FINANCE_ADVICES_COLLECTION_ID]['active'] = False

        # add some specific searches while using 'meetingadvicefinances'
        typesTool = api.portal.get_tool('portal_types')
        if 'meetingadvicefinances' in typesTool and cfg.getUseAdvices():
            financesadvice_infos = OrderedDict(
                [
                    # Items in state 'proposed_to_finance' for which
                    # completeness is not 'completeness_complete'
                    ('searchitemstocontrolcompletenessof',
                     {
                         'subFolderId': 'searches_items',
                         'active': True,
                         'query':
                             [
                                 {'i': 'CompoundCriterion',
                                  'o': 'plone.app.querystring.operation.compound.is',
                                  'v': 'items-to-control-completeness-of'},
                             ],
                         'sort_on': u'created',
                         'sort_reversed': True,
                         'tal_condition': "python: (here.REQUEST.get('fromPortletTodo', False) and "
                                          "tool.userIsAmong(['financialcontrollers'])) "
                                          "or (not here.REQUEST.get('fromPortletTodo', False) and "
                                          "tool.adapted().isFinancialUser())",
                         'roles_bypassing_talcondition': ['Manager', ]
                     }
                     ),
                    # Items having advice in state 'proposed_to_financial_controller'
                    ('searchadviceproposedtocontroller',
                     {
                         'subFolderId': 'searches_items',
                         'active': True,
                         'query':
                             [
                                 {'i': 'CompoundCriterion',
                                  'o': 'plone.app.querystring.operation.compound.is',
                                  'v': 'items-with-advice-proposed-to-financial-controller'},
                             ],
                         'sort_on': u'created',
                         'sort_reversed': True,
                         'tal_condition': "python: (here.REQUEST.get('fromPortletTodo', False) and "
                                          "tool.userIsAmong(['financialcontrollers'])) "
                                          "or (not here.REQUEST.get('fromPortletTodo', False) and "
                                          "tool.adapted().isFinancialUser())",
                         'roles_bypassing_talcondition': ['Manager', ]
                     }
                     ),
                    # Items having advice in state 'proposed_to_financial_editor'
                    ('searchadviceproposedtoeditor',
                     {
                         'subFolderId': 'searches_items',
                         'active': True,
                         'query':
                             [
                                 {'i': 'CompoundCriterion',
                                  'o': 'plone.app.querystring.operation.compound.is',
                                  'v': 'items-with-advice-proposed-to-financial-editor'},
                             ],
                         'sort_on': u'created',
                         'sort_reversed': True,
                         'tal_condition': "python: (here.REQUEST.get('fromPortletTodo', False) and "
                                          "tool.userIsAmong(['financialeditors'])) "
                                          "or (not here.REQUEST.get('fromPortletTodo', False) and "
                                          "tool.adapted().isFinancialUser())",
                         'roles_bypassing_talcondition': ['Manager', ]
                     }
                     ),
                    # Items having advice in state 'proposed_to_financial_reviewer'
                    ('searchadviceproposedtoreviewer',
                     {
                         'subFolderId': 'searches_items',
                         'active': True,
                         'query':
                             [
                                 {'i': 'CompoundCriterion',
                                  'o': 'plone.app.querystring.operation.compound.is',
                                  'v': 'items-with-advice-proposed-to-financial-reviewer'},
                             ],
                         'sort_on': u'created',
                         'sort_reversed': True,
                         'tal_condition': "python: (here.REQUEST.get('fromPortletTodo', False) and "
                                          "tool.userIsAmong(['financialreviewers'])) "
                                          "or (not here.REQUEST.get('fromPortletTodo', False) and "
                                          "tool.adapted().isFinancialUser())",
                         'roles_bypassing_talcondition': ['Manager', ]
                     }
                     ),
                    # Items having advice in state 'proposed_to_financial_manager'
                    ('searchadviceproposedtomanager',
                     {
                         'subFolderId': 'searches_items',
                         'active': True,
                         'query':
                             [
                                 {'i': 'CompoundCriterion',
                                  'o': 'plone.app.querystring.operation.compound.is',
                                  'v': 'items-with-advice-proposed-to-financial-manager'},
                             ],
                         'sort_on': u'created',
                         'sort_reversed': True,
                         'tal_condition': "python: (here.REQUEST.get('fromPortletTodo', False) and "
                                          "tool.userIsAmong(['financialmanagers'])) "
                                          "or (not here.REQUEST.get('fromPortletTodo', False) and "
                                          "tool.adapted().isFinancialUser())",
                         'roles_bypassing_talcondition': ['Manager', ]
                     }
                     ),
                ]
            )
            infos.update(financesadvice_infos)
        return infos

    def extraAdviceTypes(self):
        '''See doc in interfaces.py.'''
        typesTool = api.portal.get_tool('portal_types')
        if 'meetingadvicefinances' in typesTool:
            return ['positive_finance', 'positive_with_remarks_finance',
                    'cautious_finance', 'negative_finance', 'not_given_finance',
                    'not_required_finance']
        return []


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

    security.declarePrivate('doBackToPublished')

    def doBackToPublished(self, stateChange):
        '''We do not impact items while going back from decided.'''
        pass


class MeetingCollegeMonsWorkflowConditions(MeetingCommunesWorkflowConditions):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingCollegeMonsWorkflowConditions'''

    implements(IMeetingCollegeMonsWorkflowConditions)
    security = ClassSecurityInfo()

    security.declarePublic('mayCorrect')

    def mayDecide(self, destinationState=None):
        '''Override to avoid call to _decisionsWereConfirmed.'''
        if not _checkPermission(ReviewPortalContent, self.context):
            return
        return True

    security.declarePublic('mayDecide')

    def mayDecide(self):
        res = False
        if _checkPermission(ReviewPortalContent, self.context):
            res = True
        return res


class MeetingItemCollegeMonsWorkflowActions(MeetingItemCommunesWorkflowActions):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingItemCollegeMonsWorkflowActions'''

    implements(IMeetingItemCollegeMonsWorkflowActions)
    security = ClassSecurityInfo()

    security.declarePrivate('doAccept_but_modify')

    def doAccept_but_modify(self, stateChange):
        pass

    security.declarePrivate('doPre_accept')

    def doPre_accept(self, stateChange):
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


class MeetingItemCollegeMonsWorkflowConditions(MeetingItemCommunesWorkflowConditions):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingItemCollegeMonsWorkflowConditions'''

    implements(IMeetingItemCollegeMonsWorkflowConditions)
    security = ClassSecurityInfo()

    def __init__(self, item):
        self.context = item  # Implements IMeetingItem

    security.declarePublic('mayDecide')

    def mayDecide(self):
        '''We may decide an item if the linked meeting is in relevant state.'''
        res = False
        meeting = self.context.getMeeting()
        if _checkPermission(ReviewPortalContent, self.context) and \
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

    def isFinancialUser_cachekey(method, self, brain=False):
        '''cachekey method for self.isFinancialUser.'''
        return str(self.context.REQUEST._debug), self.context.REQUEST['AUTHENTICATED_USER']

    security.declarePublic('isFinancialUser')

    @ram.cache(isFinancialUser_cachekey)
    def isFinancialUser(self):
        '''Is current user a financial user, so in groups FINANCE_GROUP_SUFFIXES.'''
        member = api.user.get_current()
        for groupId in member.getGroups():
            for suffix in FINANCE_GROUP_SUFFIXES:
                if groupId.endswith('_%s' % suffix):
                    return True
        return False

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

    security.declarePublic('getSpecificAssemblyFor')

    def getSpecificAssemblyFor(self, assembly, startTxt=''):
        ''' Return the Assembly between two tag.
            This method is used in templates.
        '''
        # Pierre Dupont - Bourgmestre,
        # Charles Exemple - 1er Echevin,
        # Echevin Un, Echevin Deux excusé, Echevin Trois - Echevins,
        # Jacqueline Exemple, Responsable du CPAS
        # Absentes:
        # Mademoiselle x
        # Excusés:
        # Monsieur Y, Madame Z
        res = []
        tmp = ['<p class="mltAssembly">']
        splitted_assembly = assembly.replace('<p>', '').replace('</p>', '').split('<br />')
        start_text = startTxt == ''
        for assembly_line in splitted_assembly:
            assembly_line = assembly_line.strip()
            # check if this line correspond to startTxt (in this cas, we can begin treatment)
            if not start_text:
                start_text = assembly_line.startswith(startTxt)
                if start_text:
                    # when starting treatment, add tag (not use if startTxt=='')
                    res.append(assembly_line)
                continue
            # check if we must stop treatment...
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

    def initializeProposingGroupWithGroupInCharge(self):
        """Initialize every items of MeetingConfig for which
           'proposingGroupWithGroupInCharge' is in usedItemAttributes."""
        tool = self.getSelf()
        catalog = api.portal.get_tool('portal_catalog')
        logger.info('Initializing proposingGroupWithGroupInCharge...')
        for cfg in tool.objectValues('MeetingConfig'):
            if 'proposingGroupWithGroupInCharge' in cfg.getUsedItemAttributes():
                brains = catalog(portal_type=cfg.getItemTypeName())
                logger.info('Updating MeetingConfig {0}'.format(cfg.getId()))
                len_brains = len(brains)
                i = 1
                for brain in brains:
                    logger.info('Updating item {0}/{1}'.format(i, len_brains))
                    i = i + 1
                    item = brain.getObject()
                    proposingGroup = item.getProposingGroup(theObject=True)
                    groupsInCharge = proposingGroup.getGroupsInCharge()
                    groupInCharge = groupsInCharge and groupsInCharge[0] or ''
                    value = '{0}__groupincharge__{1}'.format(proposingGroup.getId(),
                                                             groupInCharge)
                    item.setProposingGroupWithGroupInCharge(value)
                    if cfg.getItemGroupInChargeStates():
                        item._updateGroupInChargeLocalRoles()
                        item.reindexObjectSecurity()
                    item.reindexObject(idxs=['getGroupInCharge'])
        logger.info('Done.')


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


class ItemsToControlCompletenessOfAdapter(CompoundCriterionBaseAdapter):

    def itemstocontrolcompletenessof_cachekey(method, self):
        '''cachekey method for every CompoundCriterion adapters.'''
        return str(self.request._debug)

    @property
    @ram.cache(itemstocontrolcompletenessof_cachekey)
    def query_itemstocontrolcompletenessof(self):
        '''Queries all items for which there is completeness to evaluate, so where completeness
           is not 'completeness_complete'.'''
        groupIds = []
        member = api.user.get_current()
        userGroups = member.getGroups()
        tool = api.portal.get_tool('portal_plonemeeting')
        cfg = tool.getMeetingConfig(self.context)
        for financeGroup in cfg.adapted().getUsedFinanceGroupIds():
            # only keep finance groupIds the current user is controller for
            if '%s_financialcontrollers' % financeGroup in userGroups:
                # advice not given yet
                groupIds.append('delay__%s_advice_not_giveable' % financeGroup)
                # advice was already given once and come back to the finance
                groupIds.append('delay__%s_proposed_to_financial_controller' % financeGroup)
        return {'portal_type': {'query': self.cfg.getItemTypeName()},
                'getCompleteness': {'query': ('completeness_not_yet_evaluated',
                                              'completeness_incomplete',
                                              'completeness_evaluation_asked_again')},
                'indexAdvisers': {'query': groupIds},
                'review_state': {'query': FINANCE_WAITING_ADVICES_STATES}}

    # we may not ram.cache methods in same file with same name...
    query = query_itemstocontrolcompletenessof


class ItemsWithAdviceProposedToFinancialControllerAdapter(CompoundCriterionBaseAdapter):

    def itemswithadviceproposedtofinancialcontroller_cachekey(method, self):
        '''cachekey method for every CompoundCriterion adapters.'''
        return str(self.request._debug)

    @property
    @ram.cache(itemswithadviceproposedtofinancialcontroller_cachekey)
    def query_itemswithadviceproposedtofinancialcontroller(self):
        '''Queries all items for which there is an advice in state 'proposed_to_financial_controller'.
           We only return items for which completeness has been evaluated to 'complete'.'''
        groupIds = []
        member = api.user.get_current()
        userGroups = member.getGroups()
        tool = api.portal.get_tool('portal_plonemeeting')
        cfg = tool.getMeetingConfig(self.context)
        for financeGroup in cfg.adapted().getUsedFinanceGroupIds():
            # only keep finance groupIds the current user is controller for
            if '%s_financialcontrollers' % financeGroup in userGroups:
                groupIds.append('delay__%s_proposed_to_financial_controller' % financeGroup)
        # Create query parameters
        return {'portal_type': {'query': self.cfg.getItemTypeName()},
                'getCompleteness': {'query': 'completeness_complete'},
                'indexAdvisers': {'query': groupIds}}

    # we may not ram.cache methods in same file with same name...
    query = query_itemswithadviceproposedtofinancialcontroller


class ItemsWithAdviceProposedToFinancialEditorAdapter(CompoundCriterionBaseAdapter):

    def itemswithadviceproposedtofinancialeditor_cachekey(method, self):
        '''cachekey method for every CompoundCriterion adapters.'''
        return str(self.request._debug)

    @property
    @ram.cache(itemswithadviceproposedtofinancialeditor_cachekey)
    def query_itemswithadviceproposedtofinancialeditor(self):
        '''Queries all items for which there is an advice in state 'proposed_to_financial_editor'.
           We only return items for which completeness has been evaluated to 'complete'.'''
        groupIds = []
        member = api.user.get_current()
        userGroups = member.getGroups()
        tool = api.portal.get_tool('portal_plonemeeting')
        cfg = tool.getMeetingConfig(self.context)
        for financeGroup in cfg.adapted().getUsedFinanceGroupIds():
            # only keep finance groupIds the current user is controller for
            if '%s_financialeditors' % financeGroup in userGroups:
                groupIds.append('delay__%s_proposed_to_financial_editor' % financeGroup)
        # Create query parameters
        return {'portal_type': {'query': self.cfg.getItemTypeName()},
                'getCompleteness': {'query': 'completeness_complete'},
                'indexAdvisers': {'query': groupIds}}

    # we may not ram.cache methods in same file with same name...
    query = query_itemswithadviceproposedtofinancialeditor


class ItemsWithAdviceProposedToFinancialReviewerAdapter(CompoundCriterionBaseAdapter):

    def itemswithadviceproposedtofinancialreviewer_cachekey(method, self):
        '''cachekey method for every CompoundCriterion adapters.'''
        return str(self.request._debug)

    @property
    @ram.cache(itemswithadviceproposedtofinancialreviewer_cachekey)
    def query_itemswithadviceproposedtofinancialreviewer(self):
        '''Queries all items for which there is an advice in state 'proposed_to_financial_reviewer'.'''
        groupIds = []
        member = api.user.get_current()
        userGroups = member.getGroups()
        tool = api.portal.get_tool('portal_plonemeeting')
        cfg = tool.getMeetingConfig(self.context)
        for financeGroup in cfg.adapted().getUsedFinanceGroupIds():
            # only keep finance groupIds the current user is reviewer for
            if '%s_financialreviewers' % financeGroup in userGroups:
                groupIds.append('delay__%s_proposed_to_financial_reviewer' % financeGroup)
        return {'portal_type': {'query': self.cfg.getItemTypeName()},
                'indexAdvisers': {'query': groupIds}}

    # we may not ram.cache methods in same file with same name...
    query = query_itemswithadviceproposedtofinancialreviewer


class ItemsWithAdviceProposedToFinancialManagerAdapter(CompoundCriterionBaseAdapter):

    def itemswithadviceproposedtofinancialmanager_cachekey(method, self):
        '''cachekey method for every CompoundCriterion adapters.'''
        return str(self.request._debug)

    @property
    @ram.cache(itemswithadviceproposedtofinancialmanager_cachekey)
    def query_itemswithadviceproposedtofinancialmanager(self):
        '''Queries all items for which there is an advice in state 'proposed_to_financial_manager'.'''
        groupIds = []
        member = api.user.get_current()
        userGroups = member.getGroups()
        tool = api.portal.get_tool('portal_plonemeeting')
        cfg = tool.getMeetingConfig(self.context)
        for financeGroup in cfg.adapted().getUsedFinanceGroupIds():
            # only keep finance groupIds the current user is manager for
            if '%s_financialmanagers' % financeGroup in userGroups:
                groupIds.append('delay__%s_proposed_to_financial_manager' % financeGroup)
        return {'portal_type': {'query': self.cfg.getItemTypeName()},
                'indexAdvisers': {'query': groupIds}}

    # we may not ram.cache methods in same file with same name...
    query = query_itemswithadviceproposedtofinancialmanager


class BlockedItemsAdapter(CompoundCriterionBaseAdapter):

    def blockeditems_cachekey(method, self):
        '''cachekey method for every CompoundCriterion adapters.'''
        return str(self.request._debug)

    @property
    @ram.cache(blockeditems_cachekey)
    def query_blockeditems(self):
        '''Queries all items for which there is an advice in state 'proposed_to_financial_manager'.'''
        reference = DateTime() - 60

        return {'portal_type': {'query': self.cfg.getItemTypeName()},
                # before reference
                'modified': {'query': reference, 'range': 'max'},
                'review_state': {'query': ['itemcreated',
                                           'proposed_to_budgetimpact_reviewer',
                                           'proposed_to_extraordinarybudget',
                                           'proposed_to_servicehead',
                                           'proposed_to_officemanager',
                                           'proposed_to_divisionhead',
                                           'proposed_to_director']}}

    # we may not ram.cache methods in same file with same name...
    query = query_blockeditems


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
