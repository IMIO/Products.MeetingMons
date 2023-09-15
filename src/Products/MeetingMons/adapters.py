# -*- coding: utf-8 -*-
#
# GNU General Public License (GPL)
#

from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from appy.gen import No
from collections import OrderedDict
from collective.contact.plonegroup.utils import get_all_suffixes
from Products.CMFCore.permissions import ReviewPortalContent
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from Products.MeetingMons.config import FINANCE_ADVICES_COLLECTION_ID
from Products.PloneMeeting.config import MEETING_REMOVE_MOG_WFA
from Products.MeetingMons.interfaces import IMeetingCollegeMonsWorkflowActions
from Products.MeetingMons.interfaces import IMeetingCollegeMonsWorkflowConditions
from Products.MeetingMons.interfaces import IMeetingItemCollegeMonsWorkflowActions
from Products.MeetingMons.interfaces import IMeetingItemCollegeMonsWorkflowConditions
from Products.MeetingCommunes.adapters import CustomMeeting as MCMeeting
from Products.MeetingCommunes.adapters import CustomMeetingConfig as MCMeetingConfig
from Products.MeetingCommunes.adapters import CustomMeetingItem as MCMeetingItem
from Products.MeetingCommunes.adapters import CustomToolPloneMeeting as MCToolPloneMeeting
from Products.MeetingCommunes.adapters import MeetingCommunesWorkflowActions
from Products.MeetingCommunes.adapters import MeetingCommunesWorkflowConditions
from Products.MeetingCommunes.adapters import MeetingItemCommunesWorkflowActions
from Products.MeetingCommunes.adapters import MeetingItemCommunesWorkflowConditions
from Products.MeetingMons.config import FINANCE_ADVICES_COLLECTION_ID
from Products.MeetingMons.interfaces import IMeetingCollegeMonsWorkflowActions
from Products.MeetingMons.interfaces import IMeetingCollegeMonsWorkflowConditions
from Products.MeetingMons.interfaces import IMeetingItemCollegeMonsWorkflowActions
from Products.MeetingMons.interfaces import IMeetingItemCollegeMonsWorkflowConditions
from Products.PloneMeeting.adapters import ItemPrettyLinkAdapter
from Products.PloneMeeting.config import MEETING_REMOVE_MOG_WFA
from Products.PloneMeeting.MeetingConfig import MeetingConfig
from Products.PloneMeeting.adapters import ItemPrettyLinkAdapter
from Products.PloneMeeting.config import PMMessageFactory as _
from Products.PloneMeeting.interfaces import IMeetingConfigCustom
from Products.PloneMeeting.interfaces import IMeetingCustom
from Products.PloneMeeting.interfaces import IMeetingItemCustom
from Products.PloneMeeting.interfaces import IToolPloneMeetingCustom
from Products.PloneMeeting.MeetingConfig import MeetingConfig
from Products.PloneMeeting.model import adaptations
from Products.PloneMeeting.model.adaptations import _addIsolatedState


from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from AccessControl.class_init import InitializeClass
from Products.CMFCore.permissions import ReviewPortalContent, ModifyPortalContent
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from appy.gen import No
from collective.contact.plonegroup.utils import get_all_suffixes
from imio.helpers.xhtml import xhtmlContentIsEmpty
from plone import api
from plone.memoize import ram
from zope.i18n import translate
from zope.interface import implements


customWfAdaptations = (
    'item_validation_shortcuts',
    'item_validation_no_validate_shortcuts',
    'only_creator_may_delete',
    # first define meeting workflow state removal
    'no_freeze',
    'no_publication',
    'no_decide',
    # then define added item decided states
    'accepted_but_modified',
    'postpone_next_meeting',
    'mark_not_applicable',
    'removed',
    'removed_and_duplicated',
    'refused',
    'delayed',
    'pre_accepted',
    "mons_budget_reviewer",
    "return_to_proposing_group",
    "return_to_proposing_group_with_last_validation",
    'hide_decisions_when_under_writing',
    MEETING_REMOVE_MOG_WFA,
)
MeetingConfig.wfAdaptations = customWfAdaptations

# states taken into account by the 'no_global_observation' wfAdaptation
noGlobalObsStates = ('itempublished', 'itemfrozen', 'accepted', 'refused',
                     'delayed', 'accepted_but_modified', 'pre_accepted')
adaptations.noGlobalObsStates = noGlobalObsStates

adaptations.RETURN_TO_PROPOSING_GROUP_FROM_ITEM_STATES = ('presented', 'itemfrozen',)


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

    security.declarePublic('mayEditValidateByBudget')

    def mayEditValidateByBudget(self):
        tool = getToolByName(self.context, 'portal_plonemeeting')
        cfg = tool.getMeetingConfig(self.context)
        return self.context.attribute_is_used('budgetInfos') and \
            (tool.userIsAmong(['extraordinarybudget', 'budgetimpactreviewers']) or tool.isManager(cfg))

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

    def get_item_custom_suffix_roles(self, item, item_state):
        '''See doc in interfaces.py.'''
        suffix_roles = {}
        if item_state == 'proposed_to_budgetimpact_reviewer':
            for suffix in get_all_suffixes(item.getProposingGroup()):
                suffix_roles[suffix] = ['Reader']
                if suffix == 'budgetimpactreviewers':
                    suffix_roles[suffix] += ['Reader', 'Contributor', 'Editor', 'Reviewer']
        elif item_state == 'proposed_to_extraordinarybudget':
            for suffix in get_all_suffixes(item.getProposingGroup()):
                suffix_roles[suffix] = ['Reader']
                if suffix == 'extraordinarybudget':
                    suffix_roles[suffix] += ['Reader', 'Contributor', 'Editor', 'Reviewer']
        return True, suffix_roles


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
        self.update_meeting_number()
        # Set the firstItemNumber
        self.context.update_first_item_number()
        if cfg.getInitItemDecisionIfEmptyOnDecide():
            for item in self.context.get_items():
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
        super(MeetingItemCollegeMonsWorkflowConditions, self).__init__(item)
        self.context = item  # Implements IMeetingItem

    security.declarePublic('is_validated_by_budget_reviewer')

    def is_validated_by_budget_reviewer(self):
        tool = self.context.portal_plonemeeting
        meetingConfig = tool.getMeetingConfig(
            self.context)
        return not self.context.getBudgetRelated() or self.context.getValidateByBudget() or \
            tool.isManager(meetingConfig)

    security.declarePublic('mayWaitAdvices')

    def mayWaitAdvices(self):
        """
          Check that the user has the 'Review portal content'
        """
        res = False
        if _checkPermission(ReviewPortalContent, self.context):
            res = True
        return res

    security.declarePublic('mayProposeToNextValidationLevel')

    def mayProposeToNextValidationLevel(self, destinationState):
        if destinationState == "proposed_to_servicehead" and not self.is_validated_by_budget_reviewer():
            return No(_('required_isValidatedByBudget_ko'))

        return super(MeetingItemCollegeMonsWorkflowConditions, self).mayProposeToNextValidationLevel(destinationState)

    def _mayShortcutToValidationLevel(self, destinationState):
        if not self.is_validated_by_budget_reviewer():
            return No(_('required_isValidatedByBudget_ko'))
        return super(MeetingItemCollegeMonsWorkflowConditions, self)._mayShortcutToValidationLevel(destinationState)

    def mayValidate(self):
        if not self.is_validated_by_budget_reviewer():
            return No(_('required_isValidatedByBudget_ko'))
        return super(MeetingItemCollegeMonsWorkflowConditions, self).mayValidate()

    security.declarePublic('mayRemove')

    def mayRemove(self):
        """
          We may remove an item if the linked meeting is in the 'decided'
          state.  For now, this is the same behaviour as 'mayDecide'
        """
        res = False
        meeting = self.context.getMeeting()
        if _checkPermission(ReviewPortalContent, self.context) and \
                meeting and (meeting.query_state() in ['decided', 'closed']):
            res = True
        return res

    security.declarePublic('mayValidateByBudgetImpactReviewer')

    def mayValidateByBudgetImpactReviewer(self):
        """
          Check that the user has the 'Review portal content'
        """
        # Check if there are category and groupsInCharge, if applicable
        msg = self._check_required_data("validatedByBudgetImpactReviewer")
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
        msg = self._check_required_data("proposedToBudgetImpactReviewer")
        if msg is not None:
            return msg

        res = False
        if _checkPermission(ReviewPortalContent, self.context):
            res = True
        return res

    security.declarePublic('mayValidateByExtraordinaryBudget')

    def mayValidateByExtraordinaryBudget(self):
        """
          Check that the user has the 'Review portal content'
        """
        # Check if there are category and groupsInCharge, if applicable
        msg = self._check_required_data("validatedByExtraordinaryBudget")
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
        msg = self._check_required_data('proposedByExtraordinaryBudget')
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

    def performCustomWFAdaptations(
            self, meetingConfig, wfAdaptation, logger, itemWorkflow, meetingWorkflow):
        ''' '''
        if wfAdaptation == 'mons_budget_reviewer' and "itemcreated" in itemWorkflow.states:
            _addIsolatedState(
                new_state_id='proposed_to_budgetimpact_reviewer',
                origin_state_id='itemcreated',
                origin_transition_id='proposeToBudgetImpactReviewer',
                origin_transition_title=translate("proposeToBudgetImpactReviewer", "plone"),
                origin_transition_guard_expr_name='mayProposeToBudgetImpactReviewer()',
                back_transition_guard_expr_name="mayValidateByBudgetImpactReviewer()",
                back_transition_id='validateByBudgetImpactReviewer',
                back_transition_title=translate("validateByBudgetImpactReviewer", "plone"),
                itemWorkflow=itemWorkflow)
            proposed_to_extraordinarybudget = _addIsolatedState(
                new_state_id='proposed_to_extraordinarybudget',
                origin_state_id='proposed_to_budgetimpact_reviewer',
                origin_transition_id='proposeToExtraordinaryBudget',
                origin_transition_title=translate("proposeToExtraordinaryBudget", "plone"),
                origin_transition_guard_expr_name='mayProposeToExtraordinaryBudget()',
                back_transition_guard_expr_name="mayCorrect()",
                back_transition_id='backToItemBudgetImpactReviewers',
                back_transition_title=translate("backToItemBudgetImpactReviewers", "plone"),
                itemWorkflow=itemWorkflow)
            itemWorkflow.transitions.addTransition("validateByExtraordinaryBudget")
            transition = itemWorkflow.transitions["validateByExtraordinaryBudget"]
            transition.setProperties(
                title="validateByExtraordinaryBudget",
                new_state_id="itemcreated", trigger_type=1, script_name='',
                actbox_name="itemcreated", actbox_url='',
                actbox_icon='%(portal_url)s/{0}.png'.format("itemcreated"),
                actbox_category='workflow',
                props={'guard_expr': 'python:here.wfConditions().{0}'.format("mayValidateByExtraordinaryBudget()")})

            proposed_to_extraordinarybudget.transitions = \
                proposed_to_extraordinarybudget.transitions + ("validateByExtraordinaryBudget",)
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

        itemState = self.context.query_state()
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

        return icons
