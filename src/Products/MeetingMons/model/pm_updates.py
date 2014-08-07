from Products.Archetypes.atapi import *
from Products.PloneMeeting.MeetingGroup import MeetingGroup
from Products.PloneMeeting.MeetingConfig import MeetingConfig
from Products.PloneMeeting.MeetingItem import MeetingItem


def update_group_schema(baseSchema):

    specificSchema = Schema((

        # field used to define list of services for echevin for a MeetingGroup
        LinesField(
            name='echevinServices',
            widget=MultiSelectionWidget(
                size=10,
                label='EchevinServices',
                label_msgid='MeetingMons_label_echevinServices',
                description='Leave empty if he is not an echevin',
                description_msgid='MeetingMons_descr_echevinServices',
                i18n_domain='PloneMeeting',
            ),
            enforceVocabulary=True,
            multiValued=1,
            vocabulary='listEchevinServices',
        ),

        # field used to define specific signatures for a MeetingGroup
        TextField(
            name='signatures',
            allowable_content_types=('text/plain',),
            widget=TextAreaWidget(
                label='Signatures',
                label_msgid='MeetingMons_label_signatures',
                description='Leave empty to use the signatures defined on the meeting',
                description_msgid='MeetingMons_descr_signatures',
                i18n_domain='PloneMeeting',
            ),
            default_content_type='text/plain',
        ),
    ),)

    completeGroupSchema = baseSchema + specificSchema.copy()

    return completeGroupSchema
MeetingGroup.schema = update_group_schema(MeetingGroup.schema)


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
        ),

        TextField(
            name='itemDecisionReportText',
            widget=TextAreaWidget(
                description="ItemDecisionReportText",
                description_msgid="item_decision_report_text_descr",
                label='ItemDecisionReportText',
                label_msgid='PloneMeeting_label_itemDecisionReportText',
                i18n_domain='PloneMeeting',
            ),
            allowable_content_types=('text/plain', 'text/html', ),
            default_output_type="text/plain",
        ),

        TextField(
            name='itemDecisionRefuseText',
            widget=TextAreaWidget(
                description="ItemDecisionRefuseText",
                description_msgid="item_decision_refuse_text_descr",
                label='ItemDecisionRefuseText',
                label_msgid='PloneMeeting_label_itemDecisionRefuseText',
                i18n_domain='PloneMeeting',
            ),
            allowable_content_types=('text/plain', 'text/html', ),
            default_output_type="text/plain",
        )
    ),)

    completeConfigSchema = baseSchema + specificSchema.copy()
    completeConfigSchema.moveField('defaultMeetingItemDecision', after='budgetDefault')
    completeConfigSchema.moveField('defaultMeetingItemDetailledDescription', after='defaultMeetingItemDecision')
    completeConfigSchema.moveField('itemDecisionReportText', after='defaultMeetingItemDetailledDescription')
    completeConfigSchema.moveField('itemDecisionRefuseText', after='itemDecisionReportText')
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
                            MeetingExtraordinaryBudget', here) or here.portal_plonemeeting.isManager())",
                label='ValidateByBudget',
                label_msgid='MeetingMons_label_validateByBudget',
                description='Validate By Budget Impact Reviwer',
                description_msgid='MeetingMons_descr_validateByBudget',
                i18n_domain='PloneMeeting',
            ),
            write_permission="MeetingMons: Write budget infos"
        ),

    ),)

    baseSchema['category'].widget.label_method = "getLabelCategory"
    baseSchema['decision'].default_method = 'getDefaultDecision'
    baseSchema['decision'].widget.label_method = 'getLabelDecision'
    baseSchema['description'].widget.label = "projectOfDecision"
    baseSchema['description'].widget.label_msgid = "projectOfDecision_label"
    baseSchema['motivation'].widget.description_msgid = "item_motivation_descr"

    completeItemSchema = baseSchema + specificSchema.copy()
    return completeItemSchema
MeetingItem.schema = update_item_schema(MeetingItem.schema)


# Classes have already been registered, but we register them again here
# because we have potentially applied some schema adaptations (see above).
# Class registering includes generation of accessors and mutators, for
# example, so this is why we need to do it again now.
from Products.PloneMeeting.config import registerClasses
registerClasses()
