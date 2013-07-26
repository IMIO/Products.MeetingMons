# -*- coding: utf-8 -*-
#
# File: setuphandlers.py
#
# Copyright (c) 2013 by CommunesPlone
# Generator: ArchGenXML Version 2.7
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Andre NUYENS <andre@imio.be>"""
__docformat__ = 'plaintext'


import logging
logger = logging.getLogger('MeetingMons: setuphandlers')
from Products.MeetingMons.config import PROJECTNAME
from Products.MeetingMons.config import DEPENDENCIES
import os
from Products.CMFCore.utils import getToolByName
import transaction
##code-section HEAD
from DateTime import DateTime
from Products.PloneMeeting.exportimport.content import ToolInitializer
from Products.PloneMeeting.model.adaptations import performWorkflowAdaptations
from Products.PloneMeeting.config import TOPIC_TYPE, TOPIC_SEARCH_SCRIPT, TOPIC_TAL_EXPRESSION
from Products.MeetingMons.config import COUNCIL_COMMISSION_IDS, COMMISSION_EDITORS_SUFFIX
##/code-section HEAD

def isNotMeetingMonsProfile(context):
    return context.readDataFile("MeetingMons_marker.txt") is None

def updateRoleMappings(context):
    """after workflow changed update the roles mapping. this is like pressing
    the button 'Update Security Setting' and portal_workflow"""
    if isNotMeetingMonsProfile(context): return
    wft = getToolByName(context.getSite(), 'portal_workflow')
    wft.updateRoleMappings()

def postInstall(context):
    """Called as at the end of the setup process. """
    # the right place for your custom code
    if isNotMeetingMonsProfile(context):
        return
    logStep("postInstall", context)
    site = context.getSite()
    addCommissionEditorGroups(context, site)
    # Add some more topics
    addSearches(context, site)
    addCouncilSearches(context, site)
    # Set a default value for each MeetingConfig.defaultMeetingItemDecision
    setDefaultMeetingItemDecisions(context, site)
    # Set a default value for each MeetingConfig.preMeetingAssembly_default
    setDefaultPreMeetingsAssembly(context, site)
    #need to reinstall PloneMeeting after reinstalling MC workflows to re-apply wfAdaptations
    reinstallPloneMeeting(context, site)
    showHomeTab(context, site)
    reinstallPloneMeetingSkin(context, site)

##code-section FOOT

def isMeetingMonsConfigureProfile(context):
    return context.readDataFile("MeetingMons_examples_fr_marker.txt") or \
            context.readDataFile("MeetingMons_testing_marker.txt") or \
            context.readDataFile("MeetingMons_Mons_marker.txt") or \
            context.readDataFile("MeetingMons_cpas_marker.txt")

def isMeetingMonsTestingProfile(context):
    return context.readDataFile("MeetingMons_tests_marker.txt")
  
def addSearches(context, portal):
    '''
       Add additional searches to the all MeetingConfig except meeting-config-council
    '''
    if isNotMeetingMonsProfile(context): return

    logStep("add_college_Searches", context)
    topicsInfo = (
    # Items in state 'proposed_to_budgetimpact_reviewer'
    ( 'searchbudgetimpactreviewersitems',
    (  ('Type', 'ATPortalTypeCriterion', 'MeetingItem'),
    ), ('proposed_to_budgetimpact_reviewer', ), '', 'python: here.portal_plonemeeting.userIsAmong("budgetimpactreviewers")',
    ),
    # Items in state 'proposed_to_extraordinarybudget'
    ( 'searchextraordinarybudgetsitems',
    (  ('Type', 'ATPortalTypeCriterion', 'MeetingItem'),
    ), ('proposed_to_extraordinarybudget', ), '', 'python: here.portal_plonemeeting.userIsAmong("extraordinarybudget")',
    ),
    # Items in state 'proposed_to_servicehead'
    ( 'searchserviceheaditems',
    (  ('Type', 'ATPortalTypeCriterion', 'MeetingItem'),
    ), ('proposed_to_servicehead', ), '', 'python: here.portal_plonemeeting.userIsAmong("serviceheads")',
    ),  
    # Items in state 'proposed_to_officemanager'
    ( 'searchofficemanageritems',
    (  ('Type', 'ATPortalTypeCriterion', 'MeetingItem'),
    ), ('proposed_to_officemanager', ), '', 'python: here.portal_plonemeeting.userIsAmong("officemanagers")',
    ),
    # Items in state 'proposed_to_divisionhead
    ( 'searchdivisionheaditems',
    (  ('Type', 'ATPortalTypeCriterion', 'MeetingItem'),
    ), ('proposed_to_divisionhead', ), '', 'python: here.portal_plonemeeting.userIsAmong("divisionheads")',
    ),
    # Items in state 'proposed_to_director'
    ( 'searchdirectoritems',
    (  ('Type', 'ATPortalTypeCriterion', 'MeetingItem'),
    ), ('proposed_to_director', ), '', 'python: here.isAReviewer()',
    ),
    # Items in state 'validated'
    ( 'searchvalidateditems',
    (  ('Type', 'ATPortalTypeCriterion', 'MeetingItem'),
    ), ('validated', ), '', '',
    ),    
    # All 'decided' items
    ( 'searchdecideditems',
    (  ('Type', 'ATPortalTypeCriterion', 'MeetingItem'),
    ), ('accepted', 'refused', 'delayed', 'accepted_but_modified'), '', '',
    ),
    )

    mcs = portal.portal_plonemeeting.objectValues("MeetingConfig")
    if not mcs:
        return

    #Add these searches by meeting config
    for meetingConfig in mcs:
        if not meetingConfig.getId() != 'meeting-config-council':
            continue
        for topicId, topicCriteria, stateValues, topicSearchScript, topicTalExpr in topicsInfo:
            #if reinstalling, we need to check if the topic does not already exist
            if hasattr(meetingConfig.topics, topicId):
                continue
            meetingConfig.topics.invokeFactory('Topic', topicId)
            topic = getattr(meetingConfig.topics, topicId)
            topic.setExcludeFromNav(True)
            topic.setTitle(topicId)
            for criterionName, criterionType, criterionValue in topicCriteria:
                criterion = topic.addCriterion(field=criterionName,
                                                criterion_type=criterionType)
                topic.manage_addProperty(TOPIC_TYPE, criterionValue, 'string')
                criterionValue = '%s%s' % (criterionValue, meetingConfig.getShortName())
                criterion.setValue([criterionValue])

            stateCriterion = topic.addCriterion(field='review_state', criterion_type='ATListCriterion')
            stateCriterion.setValue(stateValues)
            topic.manage_addProperty(TOPIC_SEARCH_SCRIPT, topicSearchScript, 'string')
            topic.manage_addProperty(TOPIC_TAL_EXPRESSION, topicTalExpr, 'string')
            topic.setLimitNumber(True)
            topic.setItemCount(20)
            topic.setSortCriterion('created', True)
            topic.setCustomView(True)
            topic.setCustomViewFields(['Title', 'CreationDate', 'Creator', 'review_state'])
            topic.reindexObject()

def logStep(method, context):
    logger.info("Applying '%s' in profile '%s'" %
                (method, '/'.join(context._profile_path.split(os.sep)[-3:])))


def isNotMeetingMonsMonsProfile(context):
    return context.readDataFile("MeetingMons_Mons_marker.txt") is None

def installMeetingMons(context):
    """ Run the default profile before bing able to run the mons profile"""
    if isNotMeetingMonsMonsProfile(context):
        return

    logStep("installMeetingMons", context)
    portal = context.getSite()
    portal.portal_setup.runAllImportStepsFromProfile('profile-Products.MeetingMons:default')

def initializeTool(context):
    '''Initialises the PloneMeeting tool based on information from the current
       profile.'''
    if isNotMeetingMonsMonsProfile(context): return

    logStep("initializeTool", context)
    return ToolInitializer(context, PROJECTNAME).run()

def addCommissionEditorGroups(context, portal):
    '''
       Add groups for council commissions that will contain MeetingCommissionEditors
    '''
    if isNotMeetingMonsProfile(context): return

    logStep("addCommissionEditorGroups", context)
    existingPloneGroupIds = portal.portal_groups.getGroupIds()
    for commissionId in COUNCIL_COMMISSION_IDS:
        groupId = commissionId + COMMISSION_EDITORS_SUFFIX
        if not groupId in existingPloneGroupIds:
            #add the Plone group
            groupTitle = groupId.replace('-', ' ').capitalize() + u' (Rédacteurs PV)'.encode('utf-8')
            portal.portal_groups.addGroup(groupId, title=groupTitle)

def addCouncilSearches(context, portal):
    '''
       Add additional searches to the 'meeting-config-council' MeetingConfig
    '''
    if isNotMeetingMonsProfile(context): return

    logStep("addCouncilSearches", context)
    topicsInfo = (
    # Items in state 'proposed_to_officemanager'
    ( 'searchproposeditems',
    (  ('Type', 'ATPortalTypeCriterion', 'MeetingItem'),
    ), ('proposed_to_officemanager', ), '', 'python: not here.portal_plonemeeting.userIsAmong("officemanagers")',
    ),
    # Items in state 'proposed_to_director'
    # Used in the "todo" portlet
    ( 'searchitemstovalidate',
    (  ('Type', 'ATPortalTypeCriterion', 'MeetingItem'),
    ), ('proposed_to_director', ), '', 'python: here.portal_plonemeeting.userIsAmong("directors")',
    ),
    # Items in state 'validated'
    ( 'searchvalidateditems',
    (  ('Type', 'ATPortalTypeCriterion', 'MeetingItem'),
    ), ('validated', ), '', '',
    ),
    # Items in state 'returned_to_service
    ( 'searchreturnedtoserviceitems',
    (  ('Type', 'ATPortalTypeCriterion', 'MeetingItem'),
    ), ('returned_to_service', ), '', 'python: here.portal_plonemeeting.userIsAmong("officemanagers") or here.portal_plonemeeting.userIsAmong("creators")',
    ),
    # Items returned to secretary after corrections
    ( 'searchcorrecteditems',
    (  ('Type', 'ATPortalTypeCriterion', 'MeetingItem'),
    ), (), 'searchCorrectedItems', 'python: here.portal_plonemeeting.isManager()',
    ),
    # Items of my commissions
    ( 'searchitemsofmycommissions',
    (  ('Type', 'ATPortalTypeCriterion', 'MeetingItem'),
    ), (), 'searchItemsOfMyCommissions', 'python: here.portal_plonemeeting.userIsAmong("commissioneditors")',
    ),
    # Items of my commissions I can edit
    ( 'searchitemsofmycommissionstoedit',
    (  ('Type', 'ATPortalTypeCriterion', 'MeetingItem'),
    ), (), 'searchItemsOfMyCommissionsToEdit', 'python: here.portal_plonemeeting.userIsAmong("commissioneditors")',
    ),
    # All 'decided' items
    ( 'searchdecideditems',
    (  ('Type', 'ATPortalTypeCriterion', 'MeetingItem'),
    ), ('accepted', 'refused', 'delayed', 'accepted_but_modified'), '', '',
    ),
    )

    mcs = portal.portal_plonemeeting.objectValues("MeetingConfig")
    if not mcs:
        return

    #Add these searches by meeting config
    for meetingConfig in mcs:
        if not meetingConfig.getId() == 'meeting-config-council':
            continue
        for topicId, topicCriteria, stateValues, topicSearchScript, topicTalExpr in topicsInfo:
            #if reinstalling, we need to check if the topic does not already exist
            if hasattr(meetingConfig.topics, topicId):
                continue
            meetingConfig.topics.invokeFactory('Topic', topicId)
            topic = getattr(meetingConfig.topics, topicId)
            topic.setExcludeFromNav(True)
            topic.setTitle(topicId)
            for criterionName, criterionType, criterionValue in topicCriteria:
                criterion = topic.addCriterion(field=criterionName,
                                                criterion_type=criterionType)
                topic.manage_addProperty(TOPIC_TYPE, criterionValue, 'string')
                criterionValue = '%s%s' % (criterionValue, meetingConfig.getShortName())
                criterion.setValue([criterionValue])

            stateCriterion = topic.addCriterion(field='review_state', criterion_type='ATListCriterion')
            stateCriterion.setValue(stateValues)
            topic.manage_addProperty(TOPIC_SEARCH_SCRIPT, topicSearchScript, 'string')
            topic.manage_addProperty(TOPIC_TAL_EXPRESSION, topicTalExpr, 'string')
            topic.setLimitNumber(True)
            topic.setItemCount(20)
            topic.setSortCriterion('created', True)
            topic.setCustomView(True)
            topic.setCustomViewFields(['Title', 'CreationDate', 'Creator', 'review_state'])
            topic.reindexObject()

    
        # define some parameters for 'meeting-config-council'
        mc_council = getattr(portal.portal_plonemeeting, 'meeting-config-council')
        # add some topcis to the portlet_todo
        mc_council.setToDoListTopics([getattr(mc_council.topics, 'searchdecideditems'),
                              getattr(mc_council.topics, 'searchitemstovalidate'),
                              getattr(mc_council.topics, 'searchreturnedtoserviceitems'),
                              getattr(mc_council.topics, 'searchcorrecteditems'),
                              getattr(mc_council.topics, 'searchitemsofmycommissionstoedit'),
                              getattr(mc_council.topics, 'searchallitemstoadvice'),
                              getattr(mc_council.topics, 'searchallitemsincopy'),
                             ])

def setDefaultMeetingItemDecisions(context, portal):
    '''
       Define the MeetingConfig.defaultItemDecision for 'meeting-config-college'
       and 'meeting-config-council
    '''
    if isNotMeetingMonsProfile(context): return

    logStep("setDefaultMeetingItemDecisions", context)

    data = {'meeting-config-college':"""<p>Vu l'arrêté du Gouvernement Wallon du 22 avril 2004 portant codification de la législation relative aux pouvoirs locaux; dit le code de la démocratie locale et de la décentralisation;</p>
<p>Vu le décret du 27 mai 2004 portant confirmation dudit arrêté du gouvernement Wallon du 22 avril 2004;</p>
<p>Vu la nouvelle Loi communale;</p>
<p>Vu l'article 123 de la nouvelle Loi communale;</p>
<p>Vu l'article L1123-23 du code de la Démocratie locale et de la Décentralisation;</p>""",
    'meeting-config-council':"""<p>Vu, d'une part, l'arrêté du Gouvernement Wallon du 22 avril 2004 portant codification de la législation relative aux pouvoirs locaux et d'autre part, le décret du 27 mai 2004 portant confirmation dudit arrêté;</p>
<p>Vu l'article 117 de la nouvelle Loi Communale;</p>
<p>Vu l'article L 1122-30 du Code de Démocratie Locale et de la Décentralisation;</p>""",
}

    for mc in portal.portal_plonemeeting.objectValues("MeetingConfig"):
        defaultMeetingItemDecision = mc.getDefaultMeetingItemDecision()
        #only update values for 'college' and 'council' if the field is empty
        if not mc.getId() in ['meeting-config-council', 'meeting-config-college',] \
           or defaultMeetingItemDecision:
            continue
        mc.setDefaultMeetingItemDecision(data[mc.getId()])

def setDefaultPreMeetingsAssembly(context, portal):
    '''
       Define a default value for each MeetingConfig.preMeetingAssembly_default
    '''
    if isNotMeetingMonsProfile(context): return

    logStep("setDefaultPreMeetingsAssembly", context)

    mc = getattr(portal.portal_plonemeeting, 'meeting-config-council', None)
    if not mc:
        return
    # Commission Travaux
    data = """M.P.WATERLOT, Président,
Mme T.ROTOLO, M.J.CHRISTIAENS, Vice-présidents,
MM.Y.DRUGMAND, G.MAGGIORDOMO, Mme O.ZRIHEN, M.R.ROMEO,Mme M.HANOT,
M.J.KEIJZER, Mmes C.BOULANGIER, F.VERMEER, L.BACCARELLA, M.C.LICATA,
Mme M.ROLAND, Conseillers communaux"""
    mc.setPreMeetingAssembly_default(data)
    # Commission Enseignement
    data="""M.A.GAVA, Président,
MM.L.WIMLOT, V.LIBOIS, Vice-présidents,
MM.M.DUBOIS, M.DI MATTIA, J.KEIJZER, A.FAGBEMI, Mme F.RMILI,
M.A.BUSCEMI, Mme A-M.MARIN, MM.A.GOREZ, J-P.MICHIELS, C.DELPLANCQ,
Mme L.BACCARELLA, Conseillers communaux"""
    mc.setPreMeetingAssembly_2_default(data)
    # Commission Cadre de vie
    data = """Mme I.VAN STEEN, Présidente,
M.F.ROMEO, Vice-président,
MM.B.LIEBIN, M.DUBOIS, J.KEIJZER, A.FAGBEMI, A.GAVA, L.DUVAL,
L.WIMLOT, V.LIBOIS, J-P.MICHIELS, Mme L.BACCARELLA, M.C.LICATA,
Mme M.ROLAND, Conseillers communaux"""
    mc.setPreMeetingAssembly_3_default(data)
    # Commission AG
    data = """M.M.DI MATTIA, Président,
Mme C.BOULANGIER, Vice-présidente,
M.B.LIEBIN, Mme C.BURGEON, M.G.MAGGIORDOMO, Mmes T.ROTOLO, M.HANOT,
MM.J.KEIJZER, J.CHRISTIAENS, M.VAN HOOLAND, Mme F.RMILI, MM.P.WATERLOT,
A.BUSCEMI, Mme F.VERMEER, Conseillers communaux
"""
    mc.setPreMeetingAssembly_4_default(data)
    # Commission Finances
    data = """M.J.CHRISTIAENS, Président,
M.M.VAN HOOLAND, Mme F.RMILI, Vice-président,
MM.B.LIEBIN, Y.DRUGMAND, Mme T.ROTOLO, M.F.ROMEO, Mme M.HANOT,
MM.J.KEIJZER, A.BUSCEMI, Mme C.BOULANGIER, MM.V.LIBOIS,
C.DELPLANCQ, Mme M.ROLAND, Conseillers communaux
"""
    mc.setPreMeetingAssembly_5_default(data)
    # Commission Police
    data = """M.A.FAGBEMI, Président,
Mme A-M.MARIN, Vice-présidente,
Mme C.BURGEON, M.M.DI MATTIA, Mme I.VAN STEEN, MM.J.KEIJZER,
A.GAVA, L.DUVAL, P.WATERLOT, L.WIMLOT, A.GOREZ, J-P.MICHIELS
Mme L.BACCARELLA, M.C.LICATA, Conseillers communaux
    """
    mc.setPreMeetingAssembly_6_default(data)

def reinstallPloneMeeting(context, site):
    '''Reinstall PloneMeeting so after install methods are called and applied,
       like performWorkflowAdaptations for example.'''

    if isNotMeetingMonsProfile(context):
        return

    logStep("reinstallPloneMeeting", context)
    _installPloneMeeting(context)


def _installPloneMeeting(context):
    site = context.getSite()
    profileId = u'profile-Products.PloneMeeting:default'
    site.portal_setup.runAllImportStepsFromProfile(profileId)


def showHomeTab(context, site):
    """
       Make sure the 'home' tab is shown...
    """
    if isNotMeetingMonsProfile(context):
        return

    logStep("showHomeTab", context)

    index_html = getattr(site.portal_actions.portal_tabs, 'index_html', None)
    if index_html:
        index_html.visible = True
    else:
        logger.info("The 'Home' tab does not exist !!!")


def reinstallPloneMeetingSkin(context, site):
    """
       Reinstall Products.plonemeetingskin as the reinstallation of MeetingMons
       change the portal_skins layers order
    """
    if isNotMeetingMonsProfile(context) and not isMeetingMonsConfigureProfile:
        return

    logStep("reinstallPloneMeetingSkin", context)
    try:
        site.portal_setup.runAllImportStepsFromProfile(u'profile-plonetheme.imioapps:default')
        site.portal_setup.runAllImportStepsFromProfile(u'profile-plonetheme.imioapps:plonemeetingskin')
    except KeyError:
        # if the Products.plonemeetingskin profile is not available
        # (not using plonemeetingskin or in testing?) we pass...
        pass


def finalizeExampleInstance(context):
    """
       Some parameters can not be handled by the PloneMeeting installation,
       so we handle this here
    """
    if not isMeetingMonsConfigureProfile(context):
        return

    # finalizeExampleInstance will behave differently if on
    # a Commune instance or CPAS instance
    specialUserId = 'bourgmestre'
    meetingConfig1Id = 'meeting-config-college'
    meetingConfig2Id = 'meeting-config-council'
    if context.readDataFile("MeetingMons_cpas_marker.txt"):
        specialUserId = 'president'
        meetingConfig1Id = 'meeting-config-bp'
        meetingConfig2Id = 'meeting-config-cas'

    site = context.getSite()

    logStep("finalizeExampleInstance", context)
    # add the test user 'bourgmestre' to every '_powerobservers' groups
    member = site.portal_membership.getMemberById(specialUserId)
    if member:
        site.portal_groups.addPrincipalToGroup(member.getId(), '%s_powerobservers' % meetingConfig1Id)
        site.portal_groups.addPrincipalToGroup(member.getId(), '%s_powerobservers' % meetingConfig2Id)
    # add the test user 'conseiller' to only the every 'meeting-config-council_powerobservers' groups
    member = site.portal_membership.getMemberById('conseiller')
    if member:
        site.portal_groups.addPrincipalToGroup(member.getId(), '%s_powerobservers' % meetingConfig2Id)

    # define some parameters for 'meeting-config-college'
    # items are sendable to the 'meeting-config-council'
    mc_college_or_bp = getattr(site.portal_plonemeeting, meetingConfig1Id)
    mc_college_or_bp.setMeetingConfigsToCloneTo([meetingConfig2Id, ])
    # add some topcis to the portlet_todo
    mc_college_or_bp.setToDoListTopics(
        [getattr(mc_college_or_bp.topics, 'searchdecideditems'),
         getattr(mc_college_or_bp.topics, 'searchitemstovalidate'),
         getattr(mc_college_or_bp.topics, 'searchallitemsincopy'),
         getattr(mc_college_or_bp.topics, 'searchallitemstoadvice'),
         ])
    # call updateCloneToOtherMCActions inter alia
    mc_college_or_bp.at_post_edit_script()

    # define some parameters for 'meeting-config-council'
    mc_council_or_cas = getattr(site.portal_plonemeeting, meetingConfig2Id)
    # add some topcis to the portlet_todo
    mc_council_or_cas.setToDoListTopics(
        [getattr(mc_council_or_cas.topics, 'searchdecideditems'),
         getattr(mc_council_or_cas.topics, 'searchitemstovalidate'),
         getattr(mc_council_or_cas.topics, 'searchallitemsincopy'),
         ])

    # finally, re-launch plonemeetingskin and MeetingMons skins step
    # because PM has been installed before the import_data profile and messed up skins layers
    site.portal_setup.runImportStepFromProfile(u'profile-Products.MeetingMons:default', 'skins')
    site.portal_setup.runImportStepFromProfile(u'profile-plonetheme.imioapps:default', 'skins')
    site.portal_setup.runImportStepFromProfile(u'profile-plonetheme.imioapps:plonemeetingskin', 'skins')
    # define default workflowAdaptations for council
    # due to some weird problems, the wfAdaptations can not be defined
    # thru the import_data...
    mc_council_or_cas.setWorkflowAdaptations(['no_global_observation', 'no_publication'])
    performWorkflowAdaptations(site, mc_council_or_cas, logger)


def reorderCss(context):
    """
       Make sure CSS are correctly reordered in portal_css so things
       work as expected...
    """
    if isNotMeetingMonsProfile(context) and not isMeetingMonsConfigureProfile(context):
        return

    site = context.getSite()

    logStep("reorderCss", context)

    portal_css = site.portal_css
    css = ['plonemeeting.css',
           'meeting.css',
           'meetingitem.css',
           'meetingmons.css',
           'imioapps.css',
           'plonemeetingskin.css',
           'imioapps_IEFixes.css',
           'ploneCustom.css']
    for resource in css:
        portal_css.moveResourceToBottom(resource)

def onMeetingItemTransition(obj, event):
    '''Called whenever a transition has been fired on a meetingItem.
       Reindex the previous_review_state index.'''
    if not event.transition or (obj != event.object): return
    obj.reindexObject(idxs=['previous_review_state', ])
    
def addAldermanGroup(context):
    """
      Add a Plone group configured to receive MeetingAlderman
      These users can modify Motivation and Decision field's items
      This group recieved the MeetingAldermanRôle
    """
    if isNotMeetingMonsProfile(context): return
    logStep("addAldermanGroup", context)
    portal = context.getSite()
    groupId = "meetingalderman"
    if not groupId in portal.portal_groups.listGroupIds():
        portal.portal_groups.addGroup(groupId, title=portal.utranslate("aldermanGroupTitle", domain='PloneMeeting'))
        portal.portal_groups.setRolesForGroup(groupId, ('MeetingObserverGlobal','MeetingPowerObserver','MeetingAlderman'))

##/code-section FOOT
