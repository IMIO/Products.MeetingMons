from Products.Archetypes.atapi import *
from Products.PloneMeeting.Meeting import Meeting
from Products.PloneMeeting.MeetingItem import MeetingItem
from Products.PloneMeeting.MeetingGroup import MeetingGroup
from Products.PloneMeeting.MeetingConfig import MeetingConfig


def update_config_schema(baseSchema):
    specificSchema = Schema((
        TextField(
            name='preMeetingAssembly_default',
            widget=TextAreaWidget(
                condition="python: 'preMeetingAssembly' in here.getUsedMeetingAttributes()",
                description="PreMeetingAssembly",
                description_msgid="premeeting_assembly_descr",
                label='Premeetingassembly',
                label_msgid='MeetingMons_label_preMeetingAssembly',
                i18n_domain='PloneMeeting',
                label_method='getLabelPreMeetingAssembly_default'
            ),
        ),
        TextField(
            name='preMeetingAssembly_2_default',
            widget=TextAreaWidget(
                condition="python: 'preMeetingAssembly_2' in here.getUsedMeetingAttributes()",
                description="PreMeetingAssembly_2",
                description_msgid="premeeting_assembly_2_descr",
                label='Premeetingassembly_2',
                label_msgid='MeetingMons_label_preMeetingAssembly_2',
                i18n_domain='PloneMeeting',
            ),
        ),
        TextField(
            name='preMeetingAssembly_3_default',
            widget=TextAreaWidget(
                condition="python: 'preMeetingAssembly_3' in here.getUsedMeetingAttributes()",
                description="PreMeetingAssembly_3",
                description_msgid="premeeting_assembly_3_descr",
                label='Premeetingassembly_3',
                label_msgid='MeetingMons_label_preMeetingAssembly_3',
                i18n_domain='PloneMeeting',
            ),
        ),
        TextField(
            name='preMeetingAssembly_4_default',
            widget=TextAreaWidget(
                condition="python: 'preMeetingAssembly_4' in here.getUsedMeetingAttributes()",
                description="PreMeetingAssembly_4",
                description_msgid="premeeting_assembly_4_descr",
                label='Premeetingassembly_4',
                label_msgid='MeetingMons_label_preMeetingAssembly_4',
                i18n_domain='PloneMeeting',
            ),
        ),
        TextField(
            name='preMeetingAssembly_5_default',
            widget=TextAreaWidget(
                condition="python: 'preMeetingAssembly_5' in here.getUsedMeetingAttributes()",
                description="PreMeetingAssembly_5",
                description_msgid="premeeting_assembly_5_descr",
                label='Premeetingassembly_5',
                label_msgid='MeetingMons_label_preMeetingAssembly_5',
                i18n_domain='PloneMeeting',
            ),
        ),
        TextField(
            name='preMeetingAssembly_6_default',
            widget=TextAreaWidget(
                condition="python: 'preMeetingAssembly_6' in here.getUsedMeetingAttributes()",
                description="PreMeetingAssembly_6",
                description_msgid="premeeting_assembly_6_descr",
                label='Premeetingassembly_6',
                label_msgid='MeetingMons_label_preMeetingAssembly_6',
                i18n_domain='PloneMeeting',
            ),
        ),
        TextField(
            name='preMeetingAssembly_7_default',
            widget=TextAreaWidget(
                condition="python: 'preMeetingAssembly_7' in here.getUsedMeetingAttributes()",
                description="PreMeetingAssembly_7",
                description_msgid="premeeting_assembly_7_descr",
                label='Premeetingassembly_7',
                label_msgid='MeetingMons_label_preMeetingAssembly_7',
                i18n_domain='PloneMeeting',
            ),
        ),

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
        )
    ),)

    completeConfigSchema = baseSchema + specificSchema.copy()
    completeConfigSchema.moveField('defaultMeetingItemDecision', after='budgetDefault')
    completeConfigSchema.moveField('defaultMeetingItemDetailledDescription', after='defaultMeetingItemDecision')
    completeConfigSchema.moveField('itemDecisionReportText', after='defaultMeetingItemDetailledDescription')
    completeConfigSchema.moveField('itemDecisionRefuseText', after='itemDecisionReportText')
    return completeConfigSchema
MeetingConfig.schema = update_config_schema(MeetingConfig.schema)


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
            widget=TextAreaWidget(
                label='Signatures',
                label_msgid='MeetingMons_label_signatures',
                description='Leave empty to use the signatures defined on the meeting',
                description_msgid='MeetingMons_descr_signatures',
                i18n_domain='PloneMeeting',
            ),
        ),
    ),)

    completeGroupSchema = baseSchema + specificSchema.copy()

    return completeGroupSchema
MeetingGroup.schema = update_group_schema(MeetingGroup.schema)


def update_meeting_schema(baseSchema):
    specificSchema = Schema((

        TextField(
            name='preMeetingAssembly',
            allowable_content_types="text/plain",
            optional=True,
            widget=TextAreaWidget(
                condition="python: here.attributeIsUsed('preMeetingAssembly')",
                description="PreMeetingAssembly",
                description_msgid="premeeting_assembly_descr",
                label='Premeetingassembly',
                label_msgid='MeetingMons_label_preMeetingAssembly',
                i18n_domain='PloneMeeting',
            ),
            default_output_type="text/html",
            default_method="getDefaultPreMeetingAssembly",
            default_content_type="text/plain",
        ),
        DateTimeField(
            name='preMeetingDate_2',
            widget=DateTimeField._properties['widget'](
                condition="python: here.attributeIsUsed('preMeetingDate_2')",
                label='Premeetingdate_2',
                label_msgid='PloneMeeting_label_preMeetingDate_2',
                i18n_domain='PloneMeeting',
            ),
            optional=True,
        ),
        StringField(
            name='preMeetingPlace_2',
            widget=StringField._properties['widget'](
                condition="python: here.attributeIsUsed('preMeetingPlace_2')",
                label='Premeetingplace_2',
                label_msgid='PloneMeeting_label_preMeetingPlace_2',
                i18n_domain='PloneMeeting',
            ),
            optional=True,
        ),
        TextField(
            name='preMeetingAssembly_2',
            allowable_content_types="text/plain",
            optional=True,
            widget=TextAreaWidget(
                condition="python: here.attributeIsUsed('preMeetingAssembly_2')",
                description="PreMeetingAssembly_2",
                description_msgid="premeeting_assembly_2_descr",
                label='Premeetingassembly_2',
                label_msgid='MeetingMons_label_preMeetingAssembly_2',
                i18n_domain='PloneMeeting',
            ),
            default_output_type="text/html",
            default_method="getDefaultPreMeetingAssembly_2",
            default_content_type="text/plain",
        ),
        DateTimeField(
            name='preMeetingDate_3',
            widget=DateTimeField._properties['widget'](
                condition="python: here.attributeIsUsed('preMeetingDate_3')",
                label='Premeetingdate_3',
                label_msgid='PloneMeeting_label_preMeetingDate_3',
                i18n_domain='PloneMeeting',
            ),
            optional=True,
        ),
        StringField(
            name='preMeetingPlace_3',
            widget=StringField._properties['widget'](
                condition="python: here.attributeIsUsed('preMeetingPlace_3')",
                label='Premeetingplace_3',
                label_msgid='PloneMeeting_label_preMeetingPlace_3',
                i18n_domain='PloneMeeting',
            ),
            optional=True,
        ),
        TextField(
            name='preMeetingAssembly_3',
            allowable_content_types="text/plain",
            optional=True,
            widget=TextAreaWidget(
                condition="python: here.attributeIsUsed('preMeetingAssembly_3')",
                description="PreMeetingAssembly_3",
                description_msgid="premeeting_assembly_3_descr",
                label='Premeetingassembly_3',
                label_msgid='MeetingMons_label_preMeetingAssembly_3',
                i18n_domain='PloneMeeting',
            ),
            default_output_type="text/html",
            default_method="getDefaultPreMeetingAssembly_3",
            default_content_type="text/plain",
        ),
        DateTimeField(
            name='preMeetingDate_4',
            widget=DateTimeField._properties['widget'](
                condition="python: here.attributeIsUsed('preMeetingDate_4')",
                label='Premeetingdate_4',
                label_msgid='PloneMeeting_label_preMeetingDate_4',
                i18n_domain='PloneMeeting',
            ),
            optional=True,
        ),
        StringField(
            name='preMeetingPlace_4',
            widget=StringField._properties['widget'](
                condition="python: here.attributeIsUsed('preMeetingPlace_4')",
                label='Premeetingplace_4',
                label_msgid='PloneMeeting_label_preMeetingPlace_4',
                i18n_domain='PloneMeeting',
            ),
            optional=True,
        ),
        TextField(
            name='preMeetingAssembly_4',
            allowable_content_types="text/plain",
            optional=True,
            widget=TextAreaWidget(
                condition="python: here.attributeIsUsed('preMeetingAssembly_4')",
                description="PreMeetingAssembly_4",
                description_msgid="premeeting_assembly_4_descr",
                label='Premeetingassembly_4',
                label_msgid='MeetingMons_label_preMeetingAssembly_4',
                i18n_domain='PloneMeeting',
            ),
            default_output_type="text/html",
            default_method="getDefaultPreMeetingAssembly_4",
            default_content_type="text/plain",
        ),
        DateTimeField(
            name='preMeetingDate_5',
            widget=DateTimeField._properties['widget'](
                condition="python: here.attributeIsUsed('preMeetingDate_5')",
                label='Premeetingdate_5',
                label_msgid='PloneMeeting_label_preMeetingDate_5',
                i18n_domain='PloneMeeting',
            ),
            optional=True,
        ),
        StringField(
            name='preMeetingPlace_5',
            widget=StringField._properties['widget'](
                condition="python: here.attributeIsUsed('preMeetingPlace_5')",
                label='Premeetingplace_5',
                label_msgid='PloneMeeting_label_preMeetingPlace_5',
                i18n_domain='PloneMeeting',
            ),
            optional=True,
        ),
        TextField(
            name='preMeetingAssembly_5',
            allowable_content_types="text/plain",
            optional=True,
            widget=TextAreaWidget(
                condition="python: here.attributeIsUsed('preMeetingAssembly_5')",
                description="PreMeetingAssembly_5",
                description_msgid="premeeting_assembly_5_descr",
                label='Premeetingassembly_5',
                label_msgid='MeetingMons_label_preMeetingAssembly_5',
                i18n_domain='PloneMeeting',
            ),
            default_output_type="text/html",
            default_method="getDefaultPreMeetingAssembly_5",
            default_content_type="text/plain",
        ),
        DateTimeField(
            name='preMeetingDate_6',
            widget=DateTimeField._properties['widget'](
                condition="python: here.attributeIsUsed('preMeetingDate_6')",
                label='Premeetingdate_6',
                label_msgid='PloneMeeting_label_preMeetingDate_6',
                i18n_domain='PloneMeeting',
            ),
            optional=True,
        ),
        StringField(
            name='preMeetingPlace_6',
            widget=StringField._properties['widget'](
                condition="python: here.attributeIsUsed('preMeetingPlace_6')",
                label='Premeetingplace_6',
                label_msgid='PloneMeeting_label_preMeetingPlace_6',
                i18n_domain='PloneMeeting',
            ),
            optional=True,
        ),
        TextField(
            name='preMeetingAssembly_6',
            allowable_content_types="text/plain",
            optional=True,
            widget=TextAreaWidget(
                condition="python: here.attributeIsUsed('preMeetingAssembly_6')",
                description="PreMeetingAssembly_6",
                description_msgid="premeeting_assembly_6_descr",
                label='Premeetingassembly_6',
                label_msgid='MeetingMons_label_preMeetingAssembly_6',
                i18n_domain='PloneMeeting',
            ),
            default_output_type="text/html",
            default_method="getDefaultPreMeetingAssembly_6",
            default_content_type="text/plain",
        ),
        DateTimeField(
            name='preMeetingDate_7',
            widget=DateTimeField._properties['widget'](
                condition="python: here.attributeIsUsed('preMeetingDate_7')",
                label='Premeetingdate_7',
                label_msgid='PloneMeeting_label_preMeetingDate_7',
                i18n_domain='PloneMeeting',
            ),
            optional=True,
        ),
        StringField(
            name='preMeetingPlace_7',
            widget=StringField._properties['widget'](
                condition="python: here.attributeIsUsed('preMeetingPlace_7')",
                label='Premeetingplace_7',
                label_msgid='PloneMeeting_label_preMeetingPlace_7',
                i18n_domain='PloneMeeting',
            ),
            optional=True,
        ),
        TextField(
            name='preMeetingAssembly_7',
            allowable_content_types="text/plain",
            optional=True,
            widget=TextAreaWidget(
                condition="python: here.attributeIsUsed('preMeetingAssembly_7')",
                description="PreMeetingAssembly_7",
                description_msgid="premeeting_assembly_7_descr",
                label='Premeetingassembly_7',
                label_msgid='MeetingMons_label_preMeetingAssembly_7',
                i18n_domain='PloneMeeting',
            ),
            default_output_type="text/html",
            default_method="getDefaultPreMeetingAssembly_7",
            default_content_type="text/plain",
        ),

    ),)

    baseSchema['assembly'].widget.description_msgid = "assembly_meeting_descr"
    baseSchema['observations'].widget.label_method = "getLabelObservations"

    completeMeetingSchema = baseSchema + specificSchema.copy()
    return completeMeetingSchema
Meeting.schema = update_meeting_schema(Meeting.schema)


def update_item_schema(baseSchema):

    specificSchema = Schema((

        #specific field for council added for MeetingManagers to transcribe interventions
        TextField(
            name='interventions',
            widget=RichWidget(
                condition="python: here.portal_type == 'MeetingItemCouncil' and here.portal_plonemeeting.isManager()",
                label='Interventions',
                label_msgid='MeetingMons_label_interventions',
                description='Transcription of interventions',
                description_msgid='MeetingMons_descr_interventions',
                i18n_domain='PloneMeeting',
            ),
            default_content_type="text/html",
            searchable=True,
            allowable_content_types=('text/html',),
            default_output_type="text/html",
        ),
        #specific field for council added for MeetingManagers to transcribe interventions
        TextField(
            name='commissionTranscript',
            widget=RichWidget(
                condition="python: here.portal_type == 'MeetingItemCouncil'",
                label='CommissionTranscript',
                label_msgid='MeetingMons_label_commissionTranscript',
                description='Transcription of commission',
                description_msgid='MeetingMons_descr_commissionTranscript',
                i18n_domain='PloneMeeting',
            ),
            default_content_type="text/html",
            default="<p>N&eacute;ant</p>",
            searchable=True,
            allowable_content_types=('text/html',),
            default_output_type="text/html",
            write_permission="MeetingMons: Write commission transcript",
            read_permission="MeetingMons: Read commission transcript",
        ),
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

    baseSchema['budgetInfos'].write_permission = "MeetingMons: Write budget infos"
    baseSchema['budgetInfos'].read_permission = "MeetingMons: Read budget infos"
    baseSchema['category'].widget.label_method = "getLabelCategory"
    baseSchema['privacy'].widget.condition = "python: here.attributeIsUsed('privacy') and \
    portal.portal_plonemeeting.isManager()"
    baseSchema['decision'].default_method = 'getDefaultDecision'
    baseSchema['decision'].widget.label_method = 'getLabelDecision'
    baseSchema['description'].widget.label = "projectOfDecision"
    baseSchema['description'].widget.label_msgid = "projectOfDecision_label"
    baseSchema['detailedDescription'].default_method = 'getDefaultDetailledDescription'
    baseSchema['detailedDescription'].widget.description = "item_motivation"
    baseSchema['detailedDescription'].widget.description_msgid = "item_motivation_descr"
    baseSchema['detailedDescription'].write_permission = "PloneMeeting: Write decision"
    baseSchema['detailedDescription'].read_permission = "PloneMeeting: Read decision"

    completeItemSchema = baseSchema + specificSchema.copy()
    return completeItemSchema
MeetingItem.schema = update_item_schema(MeetingItem.schema)


# Classes have already been registered, but we register them again here
# because we have potentially applied some schema adaptations (see above).
# Class registering includes generation of accessors and mutators, for
# example, so this is why we need to do it again now.
from Products.PloneMeeting.config import registerClasses
registerClasses()
