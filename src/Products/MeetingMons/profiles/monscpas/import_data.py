# -*- coding: utf-8 -*-
from Products.PloneMeeting.profiles import *

# File types -------------------------------------------------------------------
annexe = MeetingFileTypeDescriptor('annexe', 'Annexe', 'attach.png', '')
annexeBudget = MeetingFileTypeDescriptor('annexeBudget', 'Article Budgétaire', 'budget.png', '')
annexeCahier = MeetingFileTypeDescriptor('annexeCahier', 'Cahier des Charges', 'cahier.gif', '')
annexeRemarks = MeetingFileTypeDescriptor('annexeRemarks', 'Remarques secrétaires', 'secretary_remarks.png', '')
annexeDecision = MeetingFileTypeDescriptor('annexeDecision', 'Annexe à la décision', 'attach.png', '', True, active=False)

# Pod templates ----------------------------------------------------------------
# MeetingItem
bpDelibTemplate = PodTemplateDescriptor('bp-deliberation', 'Délibération')
bpDelibTemplate.podTemplate = 'bp_delibe.odt'
bpDelibTemplate.podCondition = 'python:(here.meta_type=="MeetingItem") and ' \
                              'here.queryState() in ["accepted", "refused", "delayed", "accepted_but_modified",]'

# Meeting
bpOJTemplate = PodTemplateDescriptor('bp-oj', 'Ordre du jour')
bpOJTemplate.podTemplate = 'bp_oj.odt'
bpOJTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager()'
bpPVTemplate = PodTemplateDescriptor('bp-pv', 'Procès verbal')
bpPVTemplate.podTemplate = 'bp_pv.odt'
bpPVTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager()'

bpTemplates = [bpDelibTemplate,bpOJTemplate,bpPVTemplate]

groups = []

# Meeting configurations -------------------------------------------------------
# bp
bpMeeting = MeetingConfigDescriptor(
    'meeting-config-bp', 'Bureau Permanent',
    'Bureau Permanent', isDefault=True)
bpMeeting.assembly = 'Pierre Dupont - Bourgmestre,\n' \
                          'Charles Exemple - 1er Echevin,\n' \
                          'Echevin Un, Echevin Deux, Echevin Trois - Echevins,\n' \
                          'Jacqueline Exemple, Responsable du CPAS'
bpMeeting.signatures = 'Pierre Dupont, Bourgmestre - Charles Exemple, 1er Echevin'
bpMeeting.categories = []
bpMeeting.shortName = 'bp'
bpMeeting.meetingFileTypes = [annexe, annexeBudget, annexeCahier, annexeDecision]
bpMeeting.xhtmlTransformFields = ('description', 'detailedDescription', 'decision', 'observations', 'interventions', 'commissionTranscript')
bpMeeting.xhtmlTransformTypes = ('removeBlanks',)
bpMeeting.itemWorkflow = 'meetingitemcollegemons_workflow'
bpMeeting.meetingWorkflow = 'meetingcollegemons_workflow'
bpMeeting.itemConditionsInterface = 'Products.MeetingMons.interfaces.IMeetingItemCollegeMonsWorkflowConditions'
bpMeeting.itemActionsInterface = 'Products.MeetingMons.interfaces.IMeetingItemCollegeMonsWorkflowActions'
bpMeeting.meetingConditionsInterface = 'Products.MeetingMons.interfaces.IMeetingCollegeMonsWorkflowConditions'
bpMeeting.meetingActionsInterface = 'Products.MeetingMons.interfaces.IMeetingCollegeMonsWorkflowActions'
bpMeeting.itemTopicStates = ('itemcreated', 'proposed_to_serviceHead', 'proposed_to_officeManager', 'proposed_to_DivisionHead', 'proposed_to_director', 'validated', 'presented', 'itemfrozen', 'accepted', 'refused', 'delayed', 'pre_accepted',)
bpMeeting.meetingTopicStates = ('created', 'frozen')
bpMeeting.decisionTopicStates = ('decided', 'closed')
bpMeeting.itemAdviceStates = ('validated',)
bpMeeting.itemAdviceEditStates = ('validated',)
bpMeeting.recordItemHistoryStates = ['',]
bpMeeting.maxShownMeetings = 5
bpMeeting.maxDaysDecisions = 60
bpMeeting.meetingAppDefaultView = 'topic_searchmyitems'
bpMeeting.itemDocFormats = ('odt', 'pdf')
bpMeeting.meetingDocFormats = ('odt', 'pdf')
bpMeeting.useAdvices = True
bpMeeting.enforceAdviceMandatoriness = False
bpMeeting.enableAdviceInvalidation = False
bpMeeting.useCopies = True
bpMeeting.selectableCopyGroups = []
bpMeeting.podTemplates = bpTemplates
bpMeeting.sortingMethodOnAddItem = 'on_proposing_groups'
bpMeeting.useGroupsAsCategories = True
bpMeeting.recurringItems = []
bpMeeting.meetingUsers = []
data = PloneMeetingConfiguration(
           meetingFolderTitle='Mes séances',
           meetingConfigs=(bpMeeting,),
           groups=groups)
data.unoEnabledPython='/usr/bin/python'
data.usedColorSystem='state_color'
# ------------------------------------------------------------------------------
