from Products.Archetypes.atapi import BooleanField, TextField, RichWidget
from Products.Archetypes.atapi import LinesField
from Products.Archetypes.atapi import MultiSelectionWidget
from Products.Archetypes.atapi import Schema
from Products.PloneMeeting.config import WriteRiskyConfig
from Products.PloneMeeting.MeetingGroup import MeetingGroup
from Products.PloneMeeting.MeetingConfig import MeetingConfig
from Products.PloneMeeting.MeetingItem import MeetingItem



def update_config_schema(baseSchema):
    specificSchema = Schema((
        TextField(
            name='defaultMeetingItemDecision',
            widget=RichWidget(
                label='DefaultMeetingItemDecision',
                label_msgid='MeetingMons_label_defaultMeetingItemDecision',
                description='DefaultMeetingItemDecision',
                description_msgid='default_meetingitem_decision',
                i18n_domain='PloneMeeting',
            ),
            default_content_type="text/html",
            allowable_content_types=('text/html',),
            default_output_type="text/html",
            write_permission=WriteRiskyConfig,
        ),

        TextField(
            name='defaultMeetingItemDetailledDescription',
            widget=RichWidget(
                label='DefaultMeetingItemDetailledDescription',
                label_msgid='MeetingMons_label_defaultMeetingItemDetailledDescription',
                description='DefaultMeetingItemDetailledDescription',
                description_msgid='default_meetingitem_detailledDescription',
                i18n_domain='PloneMeeting',
            ),
            default_content_type="text/html",
            allowable_content_types=('text/html',),
            default_output_type="text/html",
            write_permission=WriteRiskyConfig,
        ),

        BooleanField(
            name='initItemDecisionIfEmptyOnDecide',
            default=True,
            widget=BooleanField._properties['widget'](
                description="InitItemDecisionIfEmptyOnDecide",
                description_msgid="init_item_decision_if_empty_on_decide",
                label='Inititemdecisionifemptyondecide',
                label_msgid='MeetingCommunes_label_initItemDecisionIfEmptyOnDecide',
                i18n_domain='PloneMeeting'),
            write_permission=WriteRiskyConfig,
        ),
    ),)

    completeConfigSchema = baseSchema + specificSchema.copy()
    completeConfigSchema.moveField('defaultMeetingItemDecision', after='budgetDefault')
    completeConfigSchema.moveField('defaultMeetingItemDetailledDescription', after='defaultMeetingItemDecision')
    return completeConfigSchema
MeetingConfig.schema = update_config_schema(MeetingConfig.schema)

def update_item_schema(baseSchema):

    specificSchema = Schema((

        #specific field for Mons added possibility to BudgetImpactReviewer to "validate item"
        BooleanField(
            name='validateByBudget',
            widget=BooleanField._properties['widget'](
                condition="python: here.attributeIsUsed('budgetInfos') and (\
                            here.portal_membership.getAuthenticatedMember().has_role('MeetingBudgetImpactReviewer', \
                            here) or here.portal_membership.getAuthenticatedMember().has_role(' \
                            MeetingExtraordinaryBudget', here) or here.portal_plonemeeting.isManager(here))",
                label='ValidateByBudget',
                label_msgid='MeetingMons_label_validateByBudget',
                description='Validate By Budget Impact Reviwer',
                description_msgid='MeetingMons_descr_validateByBudget',
                i18n_domain='PloneMeeting',
            ),
        ),
    ),)

    baseSchema['category'].widget.label_method = "getLabelCategory"
    baseSchema['decision'].default_method = 'getDefaultDecision'
    baseSchema['decision'].widget.label_method = 'getLabelDecision'
    baseSchema['description'].widget.label = "projectOfDecision"
    baseSchema['description'].widget.label_msgid = "projectOfDecision_label"
    baseSchema['motivation'].widget.description_msgid = "item_motivation_descr"
    baseSchema['observations'].write_permission = "Modify portal content"

    completeItemSchema = baseSchema + specificSchema.copy()
    return completeItemSchema
MeetingItem.schema = update_item_schema(MeetingItem.schema)

# Classes have already been registered, but we register them again here
# because we have potentially applied some schema adaptations (see above).
# Class registering includes generation of accessors and mutators, for
# example, so this is why we need to do it again now.
from Products.PloneMeeting.config import registerClasses
registerClasses()
