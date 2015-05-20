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
collegeDelibTemplate = PodTemplateDescriptor('college-deliberation', 'Délibération')
collegeDelibTemplate.podTemplate = 'college_delibe.odt'
collegeDelibTemplate.podCondition = 'python:(here.meta_type=="MeetingItem") and ' \
                              'here.queryState() in ["accepted", "refused", "delayed", "accepted_but_modified",]'

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
collegeOJTemplate = PodTemplateDescriptor('college-oj', 'Ordre du jour')
collegeOJTemplate.podTemplate = 'college_oj.odt'
collegeOJTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here)'
collegePVTemplate = PodTemplateDescriptor('college-pv', 'Procès verbal')
collegePVTemplate.podTemplate = 'college_pv.odt'
collegePVTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here)'
councilOJExplanatoryTemplate = PodTemplateDescriptor('conseil-oj-notes-explicatives', 'OJ (notes explicatives)')
councilOJExplanatoryTemplate.podTemplate = 'conseil_oj_notes_explicatives.odt'
councilOJExplanatoryTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here)'
councilFardesTemplate = PodTemplateDescriptor('conseil-fardes', 'Fardes')
councilFardesTemplate.podTemplate = 'conseil_fardes.odt'
councilFardesTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here)'
councilAvisTemplate = PodTemplateDescriptor('conseil-avis', 'Avis')
councilAvisTemplate.podTemplate = 'conseil_avis_affiche_aux_valves.odt'
councilAvisTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here)'
councilOJConvPresseTemplate = PodTemplateDescriptor('conseil-convocation-presse', 'Convocation presse')
councilOJConvPresseTemplate.podTemplate = 'conseil_convocation_presse.odt'
councilOJConvPresseTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here)'
councilOJConvConsTemplate = PodTemplateDescriptor('conseil-convocation-conseillers', 'Convocation conseillers')
councilOJConvConsTemplate.podTemplate = 'conseil_convocation_conseillers.odt'
councilOJConvConsTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here)'
councilOJConvConsPremSupplTemplate = PodTemplateDescriptor('conseil-convocation-conseillers-1er-supplement', 'Convocation conseillers (1er supplément)')
councilOJConvConsPremSupplTemplate.podTemplate = 'conseil_convocation_conseillers_1er_supplement.odt'
councilOJConvConsPremSupplTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here)'
councilOJConvConsDeuxSupplTemplate = PodTemplateDescriptor('conseil-convocation-conseillers-2eme-supplement', 'Convocation conseillers (2ème supplément)')
councilOJConvConsDeuxSupplTemplate.podTemplate = 'conseil_convocation_conseillers_2eme_supplement.odt'
councilOJConvConsDeuxSupplTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here)'
councilOJConvCommTravTemplate = PodTemplateDescriptor('conseil-oj-commission-travaux', 'Comm. Trav.')
councilOJConvCommTravTemplate.podTemplate = 'conseil_oj_commission_travaux.odt'
councilOJConvCommTravTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here)'
councilOJConvCommEnsTemplate = PodTemplateDescriptor('conseil-oj-commission-enseignement', 'Comm. Ens.')
councilOJConvCommEnsTemplate.podTemplate = 'conseil_oj_commission_enseignement.odt'
councilOJConvCommEnsTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here)'
councilOJConvCommLogTemplate = PodTemplateDescriptor('conseil-oj-commission-logement', 'Comm. Log.')
councilOJConvCommLogTemplate.podTemplate = 'conseil_oj_commission_logement.odt'
councilOJConvCommLogTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here)'
councilOJConvCommAGTemplate = PodTemplateDescriptor('conseil-oj-commission-ag', 'Comm. AG.')
councilOJConvCommAGTemplate.podTemplate = 'conseil_oj_commission_ag.odt'
councilOJConvCommAGTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here)'
councilOJConvCommAGSupplTemplate = PodTemplateDescriptor('conseil-oj-commission-ag-suppl', 'Comm. AG. (Suppl.)')
councilOJConvCommAGSupplTemplate.podTemplate = 'conseil_oj_commission_ag_supplement.odt'
councilOJConvCommAGSupplTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here)'
councilOJConvCommFinTemplate = PodTemplateDescriptor('conseil-oj-commission-finances', 'Comm. Fin.')
councilOJConvCommFinTemplate.podTemplate = 'conseil_oj_commission_finances.odt'
councilOJConvCommFinTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here)'
councilOJConvCommPolTemplate = PodTemplateDescriptor('conseil-oj-commission-police', 'Comm. Pol.')
councilOJConvCommPolTemplate.podTemplate = 'conseil_oj_commission_police.odt'
councilOJConvCommPolTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here)'
councilOJConvCommSpecTemplate = PodTemplateDescriptor('conseil-oj-commission-speciale', 'Comm. Spec.')
councilOJConvCommSpecTemplate.podTemplate = 'conseil_oj_commission_speciale.odt'
councilOJConvCommSpecTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here)'
councilPVConvCommTravTemplate = PodTemplateDescriptor('conseil-pv-commission-travaux', 'PV Comm. Trav.')
councilPVConvCommTravTemplate.podTemplate = 'conseil_pv_commission_travaux.odt'
councilPVConvCommTravTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here)'
councilPVConvCommEnsTemplate = PodTemplateDescriptor('conseil-pv-commission-enseignement', 'PV Comm. Ens.')
councilPVConvCommEnsTemplate.podTemplate = 'conseil_pv_commission_enseignement.odt'
councilPVConvCommEnsTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here)'
councilPVConvCommLogTemplate = PodTemplateDescriptor('conseil-pv-commission-logement', 'PV Comm. Log.')
councilPVConvCommLogTemplate.podTemplate = 'conseil_pv_commission_logement.odt'
councilPVConvCommLogTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here)'
councilPVConvCommAgTemplate = PodTemplateDescriptor('conseil-pv-commission-ag', 'PV Comm. AG.')
councilPVConvCommAgTemplate.podTemplate = 'conseil_pv_commission_ag.odt'
councilPVConvCommAgTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here)'
councilPVConvCommFinTemplate = PodTemplateDescriptor('conseil-pv-commission-fin', 'PV Comm. Fin.')
councilPVConvCommFinTemplate.podTemplate = 'conseil_pv_commission_finances.odt'
councilPVConvCommFinTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here)'
councilPVConvCommPolTemplate = PodTemplateDescriptor('conseil-pv-commission-police', 'PV Comm. Pol.')
councilPVConvCommPolTemplate.podTemplate = 'conseil_pv_commission_police.odt'
councilPVConvCommPolTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here)'
councilPVConvCommSpecTemplate = PodTemplateDescriptor('conseil-pv-commission-speciale', 'PV Comm. Spec.')
councilPVConvCommSpecTemplate.podTemplate = 'conseil_pv_commission_speciale.odt'
councilPVConvCommSpecTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here)'
councilPVTemplate = PodTemplateDescriptor('conseil-pv', 'PV')
councilPVTemplate.podTemplate = 'conseil_pv.odt'
councilPVTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here)'

collegeTemplates = [collegeDelibTemplate,collegeOJTemplate,collegePVTemplate]
councilTemplates = [councilOJExplanatoryTemplate, councilFardesTemplate,
                    councilAvisTemplate, councilOJConvPresseTemplate,
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
secretaire = UserDescriptor('secretaire', ['MeetingManager'], email="test@test.be")
agentInfo = UserDescriptor('agentInfo', [], email="test@test.be")
agentCompta = UserDescriptor('agentCompta', [], email="test@test.be")
agentPers = UserDescriptor('agentPers', [], email="test@test.be")
agentTrav = UserDescriptor('agentTrav', [], email="test@test.be")
chefPers = UserDescriptor('chefPers', [], email="test@test.be")
chefCompta = UserDescriptor('chefCompta', [], email="test@test.be")
chefBureauCompta = UserDescriptor('chefBureauCompta', [], email="test@test.be")
echevinPers = UserDescriptor('echevinPers', [], email="test@test.be")
emetteuravisPers = UserDescriptor('emetteuravisPers', [], email="test@test.be")

groups = [
           GroupDescriptor('secretariat', 'Secretariat communal', 'Secr', asCopyGroupOn="python: item.getProposingGroup()=='informatique' and ['reviewers',] or []"),
           GroupDescriptor('informatique', 'Service informatique', 'Info'),
           GroupDescriptor('personnel', 'Service du personnel', 'Pers'),
           GroupDescriptor('comptabilite', 'Service comptabilité', 'Compt', givesMandatoryAdviceOn='python:True'),
           GroupDescriptor('travaux', 'Service travaux', 'Trav'),
           GroupDescriptor('conseillers', 'Conseillers', 'Conseillers'),           
           GroupDescriptor('secretaire-communal', 'Secrétaire communal', 'SecrComm'),
           GroupDescriptor('secretaire-communal-adj', 'Secrétaire communal ADJ', 'SecrCommAdj'),
         ]

# MeetingManager
groups[0].creators.append(secretaire)
groups[0].officemanagers.append(secretaire)
groups[0].observers.append(secretaire)
groups[0].advisers.append(secretaire)

groups[1].creators.append(agentInfo)
groups[1].creators.append(secretaire)
groups[1].officemanagers.append(agentInfo)
groups[1].officemanagers.append(secretaire)
groups[1].observers.append(agentInfo)
groups[1].advisers.append(agentInfo)

groups[2].creators.append(agentPers)
groups[2].observers.append(agentPers)
groups[2].creators.append(secretaire)
groups[2].officemanagers.append(secretaire)
groups[2].creators.append(chefPers)
groups[2].officemanagers.append(chefPers)
groups[2].observers.append(chefPers)
groups[2].observers.append(echevinPers)
groups[2].advisers.append(emetteuravisPers)

groups[3].creators.append(agentCompta)
groups[3].creators.append(chefCompta)
groups[3].creators.append(chefBureauCompta)
groups[3].creators.append(secretaire)
groups[3].serviceheads.append(chefCompta)
groups[3].officemanagers.append(chefBureauCompta)
groups[3].officemanagers.append(secretaire)
groups[3].observers.append(agentCompta)
groups[3].advisers.append(chefCompta)
groups[3].advisers.append(chefBureauCompta)

groups[4].creators.append(agentTrav)
groups[4].creators.append(secretaire)
groups[4].reviewers.append(agentTrav)
groups[4].reviewers.append(secretaire)
groups[4].observers.append(agentTrav)
groups[4].advisers.append(agentTrav)

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
collegeMeeting.itemAdviceEditStates = ('validated',)
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
collegeMeeting.selectableCopyGroups = [groups[0].getIdSuffixed('reviewers'), groups[1].getIdSuffixed('reviewers'), groups[2].getIdSuffixed('reviewers'), groups[4].getIdSuffixed('reviewers')]
collegeMeeting.podTemplates = collegeTemplates
collegeMeeting.sortingMethodOnAddItem = 'on_proposing_groups'
collegeMeeting.useGroupsAsCategories = True
collegeMeeting.recurringItems = []
collegeMeeting.meetingUsers = []

# Conseil communal
# Categories -------------------------------------------------------------------
categories = [
              CategoryDescriptor('recurrent', 'Point récurrent', usingGroups=('secretaire-communal', 'secretaire-communal-adj', 'secretariat', )),
              CategoryDescriptor('commission-travaux', 'Commission Travaux'),
              CategoryDescriptor('commission-enseignement', 'Commission Enseignement'),
              CategoryDescriptor('commission-cadre-de-vie-et-logement', 'Commission Cadre de Vie et Logement'),
              CategoryDescriptor('commission-ag', 'Commission AG'),
              CategoryDescriptor('commission-finances-et-patrimoine', 'Commission Finances et Patrimoine'),
              CategoryDescriptor('commission-police', 'Commission Police'),
              CategoryDescriptor('commission-speciale', 'Commission Spéciale', usingGroups=('secretaire-communal', 'secretaire-communal-adj', 'secretariat', )),
              CategoryDescriptor('commission-travaux-1er-supplement', 'Commission Travaux (1er supplément)', usingGroups=('secretaire-communal', 'secretaire-communal-adj', 'secretariat', )),
              CategoryDescriptor('commission-enseignement-1er-supplement', 'Commission Enseignement (1er supplément)', usingGroups=('secretaire-communal', 'secretaire-communal-adj', 'secretariat', )),
              CategoryDescriptor('commission-cadre-de-vie-et-logement-1er-supplement', 'Commission Cadre de Vie et Logement (1er supplément)', usingGroups=('secretaire-communal', 'secretaire-communal-adj', 'secretariat', )),
              CategoryDescriptor('commission-ag-1er-supplement', 'Commission AG (1er supplément)', usingGroups=('secretaire-communal', 'secretaire-communal-adj', 'secretariat', )),
              CategoryDescriptor('commission-finances-et-patrimoine-1er-supplement', 'Commission Finances et Patrimoine (1er supplément)', usingGroups=('secretaire-communal', 'secretaire-communal-adj', 'secretariat', )),
              CategoryDescriptor('commission-police-1er-supplement', 'Commission Police (1er supplément)', usingGroups=('secretaire-communal', 'secretaire-communal-adj', 'secretariat', )),
              CategoryDescriptor('commission-speciale-1er-supplement', 'Commission Spéciale (1er supplément)', usingGroups=('secretaire-communal', 'secretaire-communal-adj', 'secretariat', )),
              CategoryDescriptor('points-conseillers-2eme-supplement', 'Points conseillers (2ème supplément)', usingGroups=('secretaire-communal', 'secretaire-communal-adj', 'secretariat', )),
             ]

councilMeeting = MeetingConfigDescriptor(
    'meeting-config-council', 'Conseil Communal',
    'Conseil Communal')
councilMeeting.assembly = """M.J.GOBERT, Bourgmestre-Président
Mme A.SABBATINI, MM.J.GODIN, O.DESTREBECQ, G.HAINE,
Mmes A.DUPONT, F.GHIOT, M.J.C.WARGNIE, Echevins
Mme D.STAQUET, Présidente du CPAS
M.B.LIEBIN, Mme C.BURGEON, MM.M.DUBOIS, Y.DRUGMAND,
G.MAGGIORDOMO, O.ZRIHEN, M.DI MATTIA, Mme T.ROTOLO, M.F.ROMEO,
Mmes M.HANOT, I.VAN STEEN, MM.J.KEIJZER, A.FAGBEMI,
A.GAVA, A.POURBAIX, L.DUVAL, J.CHRISTIAENS, M.VAN HOOLAND,
Mme F.RMILI, MM.P.WATERLOT, A.BUSCEMI, L.WIMLOT,
Mme C.BOULANGIER, M.V.LIBOIS, Mme A.M.MARIN, MM.A.GOREZ,
J.P.MICHIELS, C.DELPLANCQ, Mmes F.VERMEER, L.BACCARELLA D'URSO,
M.C.LICATA et Mme M.ROLAND, Conseillers communaux
M.R.ANKAERT, Secrétaire
En présence de M.L.DEMOL, Chef de Corps, en ce qui concerne les points « Police »"""
councilMeeting.signatures = """Le Secrétaire,
R.ANKAERT
Le Président,
J.GOBERT"""
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
councilMeeting.itemAdviceStates = ('itemcreated',)
councilMeeting.itemAdviceEditStates = ('itemcreated',)
councilMeeting.recordItemHistoryStates = ['',]
councilMeeting.maxShownMeetings = 5
councilMeeting.maxDaysDecisions = 60
councilMeeting.meetingAppDefaultView = 'topic_searchmyitems'
councilMeeting.itemDocFormats = ('odt', 'pdf')
councilMeeting.meetingDocFormats = ('odt', 'pdf')
councilMeeting.useAdvices = True
councilMeeting.enforceAdviceMandatoriness = False
councilMeeting.enableAdviceInvalidation = False
councilMeeting.useCopies = True
councilMeeting.selectableCopyGroups = [groups[0].getIdSuffixed('reviewers'), groups[1].getIdSuffixed('reviewers'), groups[2].getIdSuffixed('reviewers'), groups[4].getIdSuffixed('reviewers')]
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
        proposingGroup='secretariat',
        decision='',
        meetingTransitionInsertingMe='setInCouncil'),
    RecurringItemDescriptor(
        id='recurrent-questions-actualite',
        title='Questions d\'actualités',
        description='',
        category='recurrent',
        proposingGroup='secretariat',
        decision='',
        meetingTransitionInsertingMe='setInCouncil'),
]

data = PloneMeetingConfiguration(
           meetingFolderTitle='Mes séances',
           meetingConfigs=(collegeMeeting, councilMeeting),
           groups=groups)
data.unoEnabledPython='/usr/bin/python'
data.usedColorSystem='state_color'
# ------------------------------------------------------------------------------
