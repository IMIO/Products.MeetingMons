# -*- coding: utf-8 -*-
from Products.PloneMeeting.profiles import *

# File types -------------------------------------------------------------------
annexe = MeetingFileTypeDescriptor('annexe', 'Annexe', 'attach.png', '')
annexeBudget = MeetingFileTypeDescriptor('annexeBudget', 'Article Budgétaire', 'budget.png', '')
annexeCahier = MeetingFileTypeDescriptor('annexeCahier', 'Cahier des Charges', 'cahier.gif', '')
annexeRemarks = MeetingFileTypeDescriptor('annexeRemarks', 'Remarques secrétaires', 'secretary_remarks.png', '')
annexeDecision = MeetingFileTypeDescriptor('annexeDecision', 'Annexe à la décision', 'attach.png', '', True, \
                                           active=False)

# Pod templates ----------------------------------------------------------------
# MeetingItem
councilDelibTemplate = PodTemplateDescriptor('conseil-deliberation', 'Délibération')
councilDelibTemplate.podTemplate = 'conseil_deliberation.odt'
councilDelibTemplate.podCondition = 'python:(here.meta_type=="MeetingItem") and ' \
                                    'here.queryState() in ["accepted", "refused", "delayed", "accepted_but_modified",]'
councilProjetDelibTemplate = PodTemplateDescriptor('conseil-projet-deliberation', 'Projet délibération')
councilProjetDelibTemplate.podTemplate = 'conseil_projet_deliberation.odt'
councilProjetDelibTemplate.podCondition = 'python:(here.meta_type=="MeetingItem")'

councilNoteExplTemplate = PodTemplateDescriptor('conseil-note-explicative', 'Note explicative')
councilNoteExplTemplate.podTemplate = 'conseil_note_explicative.odt'
councilNoteExplTemplate.podCondition = 'python:(here.meta_type=="MeetingItem")'

# Meeting
councilOJExplanatoryTemplate = PodTemplateDescriptor('conseil-oj-notes-explicatives', 'OJ (notes explicatives)')
councilOJExplanatoryTemplate.podTemplate = 'conseil_oj_notes_explicatives.odt'
councilOJExplanatoryTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                                            'here.portal_plonemeeting.isManager()'
councilFardesTemplate = PodTemplateDescriptor('conseil-fardes', 'Fardes')
councilFardesTemplate.podTemplate = 'conseil_fardes.odt'
councilFardesTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                                     'here.portal_plonemeeting.isManager()'
councilAvisTemplate = PodTemplateDescriptor('conseil-avis', 'Avis')
councilAvisTemplate.podTemplate = 'conseil_avis_affiche_aux_valves.odt'
councilAvisTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                                   'here.portal_plonemeeting.isManager()'
councilOJConvPresseTemplate = PodTemplateDescriptor('conseil-convocation-presse', 'Convocation presse')
councilOJConvPresseTemplate.podTemplate = 'conseil_convocation_presse.odt'
councilOJConvPresseTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                                           'here.portal_plonemeeting.isManager()'
councilOJConvConsTemplate = PodTemplateDescriptor('conseil-convocation-conseillers', 'Convocation conseillers')
councilOJConvConsTemplate.podTemplate = 'conseil_convocation_conseillers.odt'
councilOJConvConsTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                                         'here.portal_plonemeeting.isManager()'
councilOJConvConsPremSupplTemplate = PodTemplateDescriptor('conseil-convocation-conseillers-1er-supplement', 'Convocation conseillers (1er supplément)')
councilOJConvConsPremSupplTemplate.podTemplate = 'conseil_convocation_conseillers_1er_supplement.odt'
councilOJConvConsPremSupplTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                                                  'here.portal_plonemeeting.isManager()'
councilOJConvConsDeuxSupplTemplate = PodTemplateDescriptor('conseil-convocation-conseillers-2eme-supplement', 'Convocation conseillers (2ème supplément)')
councilOJConvConsDeuxSupplTemplate.podTemplate = 'conseil_convocation_conseillers_2eme_supplement.odt'
councilOJConvConsDeuxSupplTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager()'
councilOJConvCommTravTemplate = PodTemplateDescriptor('conseil-oj-commission-travaux', 'Comm. Trav.')
councilOJConvCommTravTemplate.podTemplate = 'conseil_oj_commission_travaux.odt'
councilOJConvCommTravTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager()'
councilOJConvCommEnsTemplate = PodTemplateDescriptor('conseil-oj-commission-enseignement', 'Comm. Ens.')
councilOJConvCommEnsTemplate.podTemplate = 'conseil_oj_commission_enseignement.odt'
councilOJConvCommEnsTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager()'
councilOJConvCommLogTemplate = PodTemplateDescriptor('conseil-oj-commission-logement', 'Comm. Log.')
councilOJConvCommLogTemplate.podTemplate = 'conseil_oj_commission_logement.odt'
councilOJConvCommLogTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager()'
councilOJConvCommAGTemplate = PodTemplateDescriptor('conseil-oj-commission-ag', 'Comm. AG.')
councilOJConvCommAGTemplate.podTemplate = 'conseil_oj_commission_ag.odt'
councilOJConvCommAGTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager()'
councilOJConvCommAGSupplTemplate = PodTemplateDescriptor('conseil-oj-commission-ag-suppl', 'Comm. AG. (Suppl.)')
councilOJConvCommAGSupplTemplate.podTemplate = 'conseil_oj_commission_ag_supplement.odt'
councilOJConvCommAGSupplTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager()'
councilOJConvCommFinTemplate = PodTemplateDescriptor('conseil-oj-commission-finances', 'Comm. Fin.')
councilOJConvCommFinTemplate.podTemplate = 'conseil_oj_commission_finances.odt'
councilOJConvCommFinTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager()'
councilOJConvCommPolTemplate = PodTemplateDescriptor('conseil-oj-commission-police', 'Comm. Pol.')
councilOJConvCommPolTemplate.podTemplate = 'conseil_oj_commission_police.odt'
councilOJConvCommPolTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager()'
councilOJConvCommSpecTemplate = PodTemplateDescriptor('conseil-oj-commission-speciale', 'Comm. Spec.')
councilOJConvCommSpecTemplate.podTemplate = 'conseil_oj_commission_speciale.odt'
councilOJConvCommSpecTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager()'
councilPVConvCommTravTemplate = PodTemplateDescriptor('conseil-pv-commission-travaux', 'PV Comm. Trav.')
councilPVConvCommTravTemplate.podTemplate = 'conseil_pv_commission_travaux.odt'
councilPVConvCommTravTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager()'
councilPVConvCommEnsTemplate = PodTemplateDescriptor('conseil-pv-commission-enseignement', 'PV Comm. Ens.')
councilPVConvCommEnsTemplate.podTemplate = 'conseil_pv_commission_enseignement.odt'
councilPVConvCommEnsTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager()'
councilPVConvCommLogTemplate = PodTemplateDescriptor('conseil-pv-commission-logement', 'PV Comm. Log.')
councilPVConvCommLogTemplate.podTemplate = 'conseil_pv_commission_logement.odt'
councilPVConvCommLogTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager()'
councilPVConvCommAgTemplate = PodTemplateDescriptor('conseil-pv-commission-ag', 'PV Comm. AG.')
councilPVConvCommAgTemplate.podTemplate = 'conseil_pv_commission_ag.odt'
councilPVConvCommAgTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager()'
councilPVConvCommFinTemplate = PodTemplateDescriptor('conseil-pv-commission-fin', 'PV Comm. Fin.')
councilPVConvCommFinTemplate.podTemplate = 'conseil_pv_commission_finances.odt'
councilPVConvCommFinTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager()'
councilPVConvCommPolTemplate = PodTemplateDescriptor('conseil-pv-commission-police', 'PV Comm. Pol.')
councilPVConvCommPolTemplate.podTemplate = 'conseil_pv_commission_police.odt'
councilPVConvCommPolTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager()'
councilPVConvCommSpecTemplate = PodTemplateDescriptor('conseil-pv-commission-speciale', 'PV Comm. Spec.')
councilPVConvCommSpecTemplate.podTemplate = 'conseil_pv_commission_speciale.odt'
councilPVConvCommSpecTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager()'
councilPVTemplate = PodTemplateDescriptor('conseil-pv', 'PV')
councilPVTemplate.podTemplate = 'conseil_pv.odt'
councilPVTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager()'

collegeTemplates = []
councilTemplates = [councilOJExplanatoryTemplate, councilFardesTemplate, councilOJConvPresseTemplate,
                    councilOJConvConsTemplate, councilOJConvConsPremSupplTemplate,
                    councilOJConvConsDeuxSupplTemplate, councilOJConvCommTravTemplate,
                    councilOJConvCommEnsTemplate, councilOJConvCommLogTemplate,
                    councilOJConvCommAGTemplate, councilOJConvCommFinTemplate,
                    councilOJConvCommPolTemplate, councilOJConvCommSpecTemplate,
                    councilPVConvCommTravTemplate, councilPVConvCommEnsTemplate,
                    councilPVConvCommLogTemplate, councilPVConvCommAgTemplate,
                    councilPVConvCommFinTemplate, councilPVConvCommPolTemplate,
                    councilPVConvCommSpecTemplate, councilPVTemplate,
                    councilNoteExplTemplate, councilProjetDelibTemplate, councilDelibTemplate]

# Users and groups -------------------------------------------------------------
test1 = UserDescriptor('test1',  [''], fullname='test 1', email="test1@Mons.be")
test2 = UserDescriptor('test2', [''], fullname='test 2', email="test2@Mons.be")
test3 = UserDescriptor('test3', [''], fullname='test 3', email="test3@Mons.be")

test1_mu = MeetingUserDescriptor('test1', duty='Bourgmestre', usages=['asker', ], active=False)
test2_mu = MeetingUserDescriptor('test2', gender='f', duty='1er Echevin', usages=['asker', ], active=False)
test3_mu = MeetingUserDescriptor('test3', gender='m', duty='2ème Echevin', usages=['asker', ], active=False)

pmManager = UserDescriptor('pmManager', ['MeetingManager'])
pmCreator1 = UserDescriptor('pmCreator1', [])
pmCreator1b = UserDescriptor('pmCreator1b', [])
pmReviewer1 = UserDescriptor('pmReviewer1', [])
pmCreator2 = UserDescriptor('pmCreator2', [])
pmReviewer2 = UserDescriptor('pmReviewer2', [])
pmAdviser1 = UserDescriptor('pmAdviser1', [])
pmServiceHead1 = UserDescriptor('pmServiceHead1', [])
pmOfficeManager1 = UserDescriptor('pmOfficeManager1', [])
pmDivisionHead1 = UserDescriptor('pmDivisionHead1', [])
pmDirector1 = UserDescriptor('pmDirector1', [])
pmDirector2 = UserDescriptor('pmDirector2', [])

groups = [
           GroupDescriptor('developers', 'Developers', 'Devel'),
           GroupDescriptor('vendors', 'Vendors', 'Devil'),
           GroupDescriptor('secretary', 'Secretary', 'Secr'),           
         ]
#developers-------------------------------------------------------------
groups[0].creators.append(pmCreator1)
groups[0].creators.append(pmCreator1b)
groups[0].reviewers.append(pmReviewer1)
groups[0].reviewers.append(pmDirector1)
groups[0].observers.append(pmReviewer1)
groups[0].advisers.append(pmAdviser1)
groups[0].serviceheads.append(pmServiceHead1)
groups[0].officemanagers.append(pmOfficeManager1)
groups[0].divisionheads.append(pmDivisionHead1)
#pmReviewer1 can validate every levels
groups[0].serviceheads.append(pmReviewer1)
groups[0].officemanagers.append(pmReviewer1)
groups[0].divisionheads.append(pmReviewer1)
#all role for pmManager
groups[0].creators.append(pmManager)
groups[0].serviceheads.append(pmManager)
groups[0].officemanagers.append(pmManager)
groups[0].divisionheads.append(pmManager)
groups[0].reviewers.append(pmManager)
groups[0].observers.append(pmManager)
groups[0].advisers.append(pmManager)
#add default signatures and echevins
setattr(groups[0], 'signatures', 'developers signatures')
setattr(groups[0], 'echevinServices', 'developers')
#vendors----------------------------------------------------------------
groups[1].creators.append(pmCreator2)
groups[1].reviewers.append(pmReviewer2)
groups[1].observers.append(pmReviewer2)
groups[1].advisers.append(pmReviewer2)
#secretary--------------------------------------------------------------
groups[2].creators.append(pmManager)
groups[2].serviceheads.append(pmManager)
groups[2].officemanagers.append(pmManager)
groups[2].divisionheads.append(pmManager)
groups[2].reviewers.append(pmManager)
groups[2].observers.append(pmManager)
groups[2].advisers.append(pmManager)


# Meeting configurations -------------------------------------------------------
# college
collegeMeeting = MeetingConfigDescriptor(
    'meeting-config-college', 'Collège Communal',
    'Collège communal', isDefault=True)
collegeMeeting.assembly = 'Pierre Dupont - Bourgmestre,\n' \
                          'Charles Exemple - 1er Echevin,\n' \
                          'Echevin Un, Echevin Deux, Echevin Trois - Echevins,\n' \
                          'Jacqueline Exemple, Responsable du CPAS'
collegeMeeting.signatures = 'Pierre Dupont, Bourgmestre - Charles Exemple, 1er Echevin'
collegeMeeting.categories = []
collegeMeeting.shortName = 'College'
collegeMeeting.meetingFileTypes = [annexe, annexeBudget, annexeCahier, annexeDecision]
collegeMeeting.xhtmlTransformFields = ('description', 'detailedDescription', 'decision', 'observations', 'interventions', 'commissionTranscript')
collegeMeeting.xhtmlTransformTypes = ('removeBlanks',)
collegeMeeting.itemWorkflow = 'meetingitemcollegemons_workflow'
collegeMeeting.meetingWorkflow = 'meetingcollegemons_workflow'
collegeMeeting.itemConditionsInterface = 'Products.MeetingMons.interfaces.IMeetingItemCollegeMonsWorkflowConditions'
collegeMeeting.itemActionsInterface = 'Products.MeetingMons.interfaces.IMeetingItemCollegeMonsWorkflowActions'
collegeMeeting.meetingConditionsInterface = 'Products.MeetingMons.interfaces.IMeetingCollegeMonsWorkflowConditions'
collegeMeeting.meetingActionsInterface = 'Products.MeetingMons.interfaces.IMeetingCollegeMonsWorkflowActions'
collegeMeeting.itemTopicStates = ('itemcreated', 'proposed_to_serviceHead', 'proposed_to_officeManager', 'proposed_to_DivisionHead', 'proposed_to_director', 'validated', 'presented', 'itemfrozen', 'accepted', 'refused', 'delayed', 'pre_accepted',)
collegeMeeting.meetingTopicStates = ('created', 'frozen')
collegeMeeting.decisionTopicStates = ('decided', 'closed')
collegeMeeting.itemAdviceStates = ('validated',)
collegeMeeting.recordItemHistoryStates = ['',]
collegeMeeting.maxShownMeetings = 5
collegeMeeting.maxDaysDecisions = 60
collegeMeeting.meetingAppDefaultView = 'topic_searchmyitems'
collegeMeeting.itemDocFormats = ('odt', 'pdf')
collegeMeeting.meetingDocFormats = ('odt', 'pdf')
collegeMeeting.useAdvices = True
collegeMeeting.enforceAdviceMandatoriness = False
collegeMeeting.enableAdviceInvalidation = False
collegeMeeting.useCopies = True
collegeMeeting.selectableCopyGroups = [groups[0].getIdSuffixed('reviewers'), groups[1].getIdSuffixed('reviewers'), groups[2].getIdSuffixed('reviewers'),]
collegeMeeting.podTemplates = collegeTemplates
collegeMeeting.sortingMethodOnAddItem = 'on_proposing_groups'
collegeMeeting.useGroupsAsCategories = True
collegeMeeting.recurringItems = []
collegeMeeting.meetingUsers = []

# Conseil communal
# Categories -------------------------------------------------------------------
categories = [
              CategoryDescriptor('recurrent', 'Point récurrent', usingGroups=('secretary', )),
              CategoryDescriptor('commission-travaux', 'Commission Travaux'),
              CategoryDescriptor('commission-enseignement', 'Commission Enseignement'),
              CategoryDescriptor('commission-cadre-de-vie-et-logement', 'Commission Cadre de Vie et Logement'),
              CategoryDescriptor('commission-ag', 'Commission AG'),
              CategoryDescriptor('commission-finances-et-patrimoine', 'Commission Finances et Patrimoine'),
              CategoryDescriptor('commission-police', 'Commission Police'),
              CategoryDescriptor('commission-speciale', 'Commission Spéciale', usingGroups=('secretary', )),
              CategoryDescriptor('commission-travaux-1er-supplement', 'Commission Travaux (1er supplément)', usingGroups=('secretary', )),
              CategoryDescriptor('commission-enseignement-1er-supplement', 'Commission Enseignement (1er supplément)', usingGroups=('secretary', )),
              CategoryDescriptor('commission-cadre-de-vie-et-logement-1er-supplement', 'Commission Cadre de Vie et Logement (1er supplément)', usingGroups=('secretary', )),
              CategoryDescriptor('commission-ag-1er-supplement', 'Commission AG (1er supplément)', usingGroups=('secretary', )),
              CategoryDescriptor('commission-finances-et-patrimoine-1er-supplement', 'Commission Finances et Patrimoine (1er supplément)', usingGroups=('secretary', )),
              CategoryDescriptor('commission-police-1er-supplement', 'Commission Police (1er supplément)', usingGroups=('secretary', )),
              CategoryDescriptor('commission-speciale-1er-supplement', 'Commission Spéciale (1er supplément)', usingGroups=('secretary', )),
              CategoryDescriptor('points-conseillers-2eme-supplement', 'Points conseillers (2ème supplément)', usingGroups=('secretary', )),
             ]

councilMeeting = MeetingConfigDescriptor(
    'meeting-config-council', 'Conseil Communal',
    'Conseil Communal')
councilMeeting.assembly = """M.TEST 1, Bourgmestre-Président
MM Echevin 1, Mme Echevin 2, MM.Echevin 3, MM Echevin 4, MM Echevin 5, Echevins
Mme Test 2, Présidente du CPAS
M.Test 3, Secrétaire
En présence de M.Test 4, Chef de Corps, en ce qui concerne les points « Police »"""
councilMeeting.signatures = """Le Secrétaire,
Test 1
Le Président,
Test 2"""
councilMeeting.categories = categories
councilMeeting.shortName = 'Council'
councilMeeting.meetingFileTypes = [annexe, annexeBudget, annexeCahier, annexeRemarks, annexeDecision]
councilMeeting.xhtmlTransformFields = ('description', 'detailedDescription', 'decision', 'observations', 'interventions', 'commissionTranscript')
councilMeeting.xhtmlTransformTypes = ('removeBlanks',)
councilMeeting.usedItemAttributes = ['oralQuestion', 'itemInitiator', 'observations', 'privacy', 'itemAssembly', ]
councilMeeting.usedMeetingAttributes = ('place', 'observations', 'signatures', 'assembly', 'preMeetingDate', 'preMeetingPlace', 'preMeetingAssembly', \
                                        'preMeetingDate_2', 'preMeetingPlace_2', 'preMeetingAssembly_2', 'preMeetingDate_3', 'preMeetingPlace_3', 'preMeetingAssembly_3', \
                                        'preMeetingDate_4', 'preMeetingPlace_4', 'preMeetingAssembly_4', 'preMeetingDate_5', 'preMeetingPlace_5', 'preMeetingAssembly_5', \
                                        'preMeetingDate_6', 'preMeetingPlace_6', 'preMeetingAssembly_6', 'preMeetingDate_7', 'preMeetingPlace_7', 'preMeetingAssembly_7',
                                        'startDate', 'endDate',
)
councilMeeting.recordMeetingHistoryStates = []
councilMeeting.itemWorkflow = 'meetingitemcouncilmons_workflow'
councilMeeting.meetingWorkflow = 'meetingcouncilmons_workflow'
councilMeeting.itemConditionsInterface = 'Products.MeetingMons.interfaces.IMeetingItemCouncilMonsWorkflowConditions'
councilMeeting.itemActionsInterface = 'Products.MeetingMons.interfaces.IMeetingItemCouncilMonsWorkflowActions'
councilMeeting.meetingConditionsInterface = 'Products.MeetingMons.interfaces.IMeetingCouncilMonsWorkflowConditions'
councilMeeting.meetingActionsInterface = 'Products.MeetingMons.interfaces.IMeetingCouncilMonsWorkflowActions'
#show every items states
councilMeeting.itemTopicStates = ('itemcreated', 'proposed_to_officemanager', 'validated', 'presented', 'itemfrozen', 'item_in_committee', 'item_in_council', 'returned_to_service', 'accepted', 'accepted_but_modified', 'refused', 'delayed')
councilMeeting.meetingTopicStates = ('created', 'frozen', 'in_committee')
councilMeeting.decisionTopicStates = ('in_council', 'closed')
councilMeeting.itemAdviceStates = ('validated',)
councilMeeting.recordItemHistoryStates = ['',]
councilMeeting.maxShownMeetings = 5
councilMeeting.maxDaysDecisions = 60
councilMeeting.meetingAppDefaultView = 'topic_searchmyitems'
councilMeeting.itemDocFormats = ('odt', 'pdf')
councilMeeting.meetingDocFormats = ('odt', 'pdf')
councilMeeting.useAdvices = False
councilMeeting.enforceAdviceMandatoriness = False
councilMeeting.enableAdviceInvalidation = False
councilMeeting.useCopies = True
councilMeeting.selectableCopyGroups = [groups[0].getIdSuffixed('reviewers'), groups[1].getIdSuffixed('reviewers'), groups[2].getIdSuffixed('reviewers'),]
councilMeeting.podTemplates = councilTemplates
councilMeeting.transitionsToConfirm = ['MeetingItem.return_to_service',]
councilMeeting.sortingMethodOnAddItem = 'on_privacy_then_categories'
councilMeeting.useGroupsAsCategories = False
councilMeeting.recurringItems = [
    RecurringItemDescriptor(
        id='recurrent-approuve-pv',
        title='Approbation du procès-verbal du Conseil communal du ...',
        description='',
        category='recurrent',
        proposingGroup='developers',
        decision='',
        meetingTransitionInsertingMe='setInCouncil'),
    RecurringItemDescriptor(
        id='recurrent-questions-actualite',
        title='Questions d\'actualités',
        description='',
        category='recurrent',
        proposingGroup='developers',
        decision='',
        meetingTransitionInsertingMe='setInCouncil'),
]
councilMeeting.meetingUsers = [test1_mu, test2_mu, test3_mu, ]

data = PloneMeetingConfiguration(
           meetingFolderTitle='Mes séances',
           meetingConfigs=(collegeMeeting, councilMeeting),
           groups=groups)
data.unoEnabledPython='/usr/bin/python'
data.usedColorSystem='state_color'
# ------------------------------------------------------------------------------
