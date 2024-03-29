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
    return completeConfigSchema
MeetingConfig.schema = update_config_schema(MeetingConfig.schema)

def update_item_schema(baseSchema):

    specificSchema = Schema((

        #specific field for Mons added possibility to BudgetImpactReviewer to "validate item"
        BooleanField(
            name='validateByBudget',
            widget=BooleanField._properties['widget'](
                condition="python: here.adapted().mayEditValidateByBudget()",
                label='ValidateByBudget',
                label_msgid='MeetingMons_label_validateByBudget',
                description='Validated By Budget Impact Reviewer',
                description_msgid='MeetingMons_descr_validateByBudget',
                i18n_domain='PloneMeeting',
            ),
        ),
    ),)

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
