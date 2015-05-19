# -*- coding: utf-8 -*-
#
# File: setuphandlers.py
#
# Copyright (c) 2015 by IMIO
# Generator: ArchGenXML Version 2.7
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Andre NUYENS <andre.nuyens@imio.be>"""
__docformat__ = 'plaintext'


import logging
logger = logging.getLogger('MeetingMons: setuphandlers')
from Products.MeetingMons.config import PROJECTNAME
from Products.MeetingMons.config import DEPENDENCIES
import os
from Products.CMFCore.utils import getToolByName
import transaction
##code-section HEAD
from Products.PloneMeeting.exportimport.content import ToolInitializer
from Products.PloneMeeting.model.adaptations import performWorkflowAdaptations
from Products.PloneMeeting.config import TOPIC_TYPE, TOPIC_SEARCH_SCRIPT, TOPIC_TAL_EXPRESSION
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
    # Add some more topics
    addSearches(context, site)
    #need to reinstall PloneMeeting after reinstalling MC workflows to re-apply wfAdaptations
    reinstallPloneMeeting(context, site)
    showHomeTab(context, site)
    reorderSkinsLayers(context, site)



##code-section FOOT


def isMeetingMonsConfigureProfile(context):
    return context.readDataFile("MeetingMons_examples_fr_marker.txt") or \
        context.readDataFile("MeetingMons_testing_marker.txt") or \
        context.readDataFile("MeetingMons_Mons_marker.txt") or \
        context.readDataFile("MeetingMons_cpas_marker.txt")


def addSearches(context, portal):
    '''
       Add additional searches to the all MeetingConfig except meeting-config-council
    '''
    if isNotMeetingMonsProfile(context):
        return

    logStep("add_college_Searches", context)
    topicsInfo = (
        # Items in state 'proposed_to_budgetimpact_reviewer'
        ('searchbudgetimpactreviewersitems',
        (('Type', 'ATPortalTypeCriterion', 'MeetingItem'),),
        ('proposed_to_budgetimpact_reviewer', ), '',
        'python: here.portal_plonemeeting.userIsAmong("budgetimpactreviewers")',),
        # Items in state 'proposed_to_extraordinarybudget'
        ('searchextraordinarybudgetsitems',
        (('Type', 'ATPortalTypeCriterion', 'MeetingItem'),), ('proposed_to_extraordinarybudget', ), '',
        'python: here.portal_plonemeeting.userIsAmong("extraordinarybudget")',),
        # Items in state 'proposed_to_servicehead'
        ('searchserviceheaditems',
        (('Type', 'ATPortalTypeCriterion', 'MeetingItem'),), ('proposed_to_servicehead', ), '',
        'python: here.portal_plonemeeting.userIsAmong("serviceheads")',),
        # Items in state 'proposed_to_officemanager'
        ('searchofficemanageritems',
        (('Type', 'ATPortalTypeCriterion', 'MeetingItem'),), ('proposed_to_officemanager', ), '',
        'python: here.portal_plonemeeting.userIsAmong("officemanagers")',),
        # Items in state 'proposed_to_divisionhead
        ('searchdivisionheaditems',
        (('Type', 'ATPortalTypeCriterion', 'MeetingItem'),), ('proposed_to_divisionhead', ), '',
        'python: here.portal_plonemeeting.userIsAmong("divisionheads")',),
        # Items in state 'proposed_to_director'
        ('searchdirectoritems',
        (('Type', 'ATPortalTypeCriterion', 'MeetingItem'),), ('proposed_to_director', ), '',
        'python: here.isAReviewer()',),
        # Items in state 'validated'
        ('searchvalidateditems',
        (('Type', 'ATPortalTypeCriterion', 'MeetingItem'),), ('validated', ), '', '',),
        # All 'decided' items
        ('searchdecideditems',
        (('Type', 'ATPortalTypeCriterion', 'MeetingItem'),),
        ('accepted', 'refused', 'delayed', 'accepted_but_modified'), '', '',),
        # Items for cdld synthesis
        ('searchcdlditems',
        (('Type', 'ATPortalTypeCriterion', ('MeetingItem',)),
         ),
        'created',
        'searchCDLDItems',
        "python: '%s_budgetimpacteditors' % here.portal_plonemeeting.getMeetingConfig(here)"
        ".getId() in member.getGroups() or here.portal_plonemeeting.isManager(here)", ),)

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
                criterion = topic.addCriterion(field=criterionName, criterion_type=criterionType)
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


def installMeetingMons(context):
    """ Run the default profile before bing able to run the mons profile"""
    if not isMeetingMonsConfigureProfile(context):
        return

    logStep("installMeetingMons", context)
    portal = context.getSite()
    portal.portal_setup.runAllImportStepsFromProfile('profile-Products.MeetingMons:default')


def initializeTool(context):
    '''Initialises the PloneMeeting tool based on information from the current
       profile.'''
    if not isMeetingMonsConfigureProfile(context):
        return

    logStep("initializeTool", context)
    #PloneMeeting is no more a dependency to avoid
    #magic between quickinstaller and portal_setup
    #so install it manually
    _installPloneMeeting(context)

    return ToolInitializer(context, PROJECTNAME).run()


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


def reorderSkinsLayers(context, site):
    """
       Re-apply MeetingMons skins.xml step
       as the reinstallation of MeetingMons and PloneMeeting changes the portal_skins layers order
    """
    if isNotMeetingMonsProfile(context) and not isMeetingMonsConfigureProfile(context):
        return

    logStep("reorderSkinsLayers", context)
    try:
        site.portal_setup.runImportStepFromProfile(u'profile-Products.MeetingMons:default', 'skins')
        site.portal_setup.runAllImportStepsFromProfile(u'profile-plonetheme.imioapps:default')
        site.portal_setup.runAllImportStepsFromProfile(u'profile-plonetheme.imioapps:plonemeetingskin')
    except KeyError:
        # if the Products.MeetingMons profile is not available
        # (not using MeetingMons or in testing?) we pass...
        pass


def finalizeInstance(context):
    """
      Called at the very end of the installation process (after PloneMeeting).
    """
    if not isMeetingMonsConfigureProfile(context):
        return

    reorderSkinsLayers(context, context.getSite())
    reorderCss(context)


def reorderCss(context):
    """
       Make sure CSS are correctly reordered in portal_css so things
       work as expected...
    """
    if isNotMeetingMonsProfile(context) and isMeetingMonsConfigureProfile(context):
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


def addAldermanGroup(context):
    """
      Add a Plone group configured to receive MeetingAlderman
      These users can modify Motivation and Decision field's items
      This group recieved the MeetingAldermanRôle
    """
    if isNotMeetingMonsProfile(context):
        return
    logStep("addAldermanGroup", context)
    portal = context.getSite()
    groupId = "meetingalderman"
    if not groupId in portal.portal_groups.listGroupIds():
        portal.portal_groups.addGroup(groupId, title=portal.utranslate("aldermanGroupTitle", domain='PloneMeeting'))
        portal.portal_groups.setRolesForGroup(groupId, ('MeetingObserverGlobal', 'MeetingPowerObserver',
                                                        'MeetingAlderman'))

##/code-section FOOT
