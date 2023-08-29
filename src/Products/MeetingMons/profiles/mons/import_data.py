# -*- coding: utf-8 -*-

from copy import deepcopy

from Products.MeetingMons.config import MONS_ITEM_WF_VALIDATION_LEVELS
from Products.PloneMeeting.profiles.testing import import_data as pm_import_data
from Products.MeetingCommunes.profiles.testing import import_data as mc_import_data
from Products.PloneMeeting.profiles import UserDescriptor


data = deepcopy(mc_import_data.data)

# Users and groups -------------------------------------------------------------
pmCreator1 = UserDescriptor(
    "pmCreator1", [], email="pmcreator1@plonemeeting.org", fullname="M. PMCreator One"
)
pmCreator1b = UserDescriptor(
    "pmCreator1b",
    [],
    email="pmcreator1b@plonemeeting.org",
    fullname="M. PMCreator One bee",
)
pmObserver1 = UserDescriptor(
    "pmObserver1",
    [],
    email="pmobserver1@plonemeeting.org",
    fullname="M. PMObserver One",
)
pmServiceHead1 = UserDescriptor("pmServiceHead1", [])
pmOfficeManager1 = UserDescriptor("pmOfficeManager1", [])
pmDivisionHead1 = UserDescriptor("pmDivisionHead1", [])
pmDirector1 = UserDescriptor("pmDirector1", [])
pmCreator2 = UserDescriptor("pmCreator2", [])
pmAdviser1 = UserDescriptor("pmAdviser1", [])
voter1 = UserDescriptor("voter1", [], fullname="M. Voter One")
voter2 = UserDescriptor("voter2", [], fullname="M. Voter Two")


# Inherited users
pmReviewer1 = deepcopy(pm_import_data.pmReviewer1)
pmReviewer2 = deepcopy(pm_import_data.pmReviewer2)
pmReviewerLevel1 = deepcopy(pm_import_data.pmReviewerLevel1)
pmReviewerLevel2 = deepcopy(pm_import_data.pmReviewerLevel2)
pmManager = deepcopy(pm_import_data.pmManager)


developers = data.orgs[0]
developers.creators.append(pmCreator1)
developers.creators.append(pmCreator1b)
developers.creators.append(pmManager)
developers.observers.append(pmObserver1)
developers.observers.append(pmReviewer1)
developers.observers.append(pmManager)
developers.advisers.append(pmAdviser1)
developers.advisers.append(pmManager)
developers.serviceheads.append(pmServiceHead1)
developers.serviceheads.append(pmReviewerLevel1)
developers.serviceheads.append(pmManager)
developers.officemanagers.append(pmOfficeManager1)
developers.officemanagers.append(pmReviewerLevel2)
developers.officemanagers.append(pmManager)
developers.divisionheads.append(pmDivisionHead1)
developers.divisionheads.append(pmManager)
developers.reviewers.append(pmDirector1)
developers.reviewers.append(pmReviewer1)
developers.reviewers.append(pmManager)
developers.budgetimpactreviewers.append(pmManager)
developers.extraordinarybudget.append(pmManager)

setattr(developers, "signatures", "developers signatures")
setattr(developers, "echevinServices", "developers")


vendors = data.orgs[1]
vendors.creators.append(pmCreator2)
vendors.reviewers.append(pmReviewer2)
vendors.observers.append(pmReviewer2)
vendors.advisers.append(pmReviewer2)
vendors.advisers.append(pmManager)
setattr(vendors, "signatures", "")


vendors = data.orgs[1]
vendors.creators.append(pmCreator2)
vendors.reviewers.append(pmReviewer2)
vendors.observers.append(pmReviewer2)
vendors.advisers.append(pmReviewer2)
vendors.advisers.append(pmManager)
setattr(vendors, "signatures", "")

# Meeting configurations -------------------------------------------------------
# Meeting configurations -------------------------------------------------------
# college
collegeMeeting = deepcopy(mc_import_data.collegeMeeting)
collegeMeeting.workflowAdaptations = ['no_publication', 'pre_accepted', 'accepted_but_modified', 'delayed', 'refused']
collegeMeeting.itemWFValidationLevels = deepcopy(MONS_ITEM_WF_VALIDATION_LEVELS)
collegeMeeting.transitionsForPresentingAnItem = (
    "proposeToServiceHead",
    "proposeToOfficeManager",
    "proposeToDivisionHead",
    "propose",
    "validate",
    "present",
)
collegeMeeting.itemConditionsInterface = (
    "Products.MeetingMons.interfaces.IMeetingItemCollegeMonsWorkflowConditions"
)
collegeMeeting.itemActionsInterface = (
    "Products.MeetingMons.interfaces.IMeetingItemCollegeMonsWorkflowActions"
)
collegeMeeting.meetingConditionsInterface = (
    "Products.MeetingMons.interfaces.IMeetingCollegeMonsWorkflowConditions"
)
collegeMeeting.meetingActionsInterface = (
    "Products.MeetingMons.interfaces.IMeetingCollegeMonsWorkflowActions"
)
collegeMeeting.transitionsForPresentingAnItem = (
    "proposeToServiceHead",
    "proposeToOfficeManager",
    "proposeToDivisionHead",
    "proposeToDirector",
    "validate",
    "present",
)
collegeMeeting.itemAdviceStates = [
    "proposed_to_director",
]
collegeMeeting.itemAdviceEditStates = ["proposed_to_director", "validated"]
collegeMeeting.itemAdviceViewStates = [
    "presented",
]
collegeMeeting.transitionsReinitializingDelays = ("backToItemCreated",)
collegeMeeting.enforceAdviceMandatoriness = False
collegeMeeting.itemPowerObserversStates = (
    "itemcreated",
    "presented",
    "accepted",
    "delayed",
    "refused",
)
collegeMeeting.itemDecidedStates = [
    "accepted",
    "refused",
    "delayed",
    "accepted_but_modified",
    "pre_accepted",
]
collegeMeeting.insertingMethodsOnAddItem = (
    {"insertingMethod": "on_proposing_groups", "reverse": "0"},
)
collegeMeeting.meetingPowerObserversStates = ("frozen", "decided", "closed")
collegeMeeting.selectableCopyGroups = [
    developers.getIdSuffixed("reviewers"),
    vendors.getIdSuffixed("reviewers"),
]


# Conseil communal
councilMeeting = deepcopy(mc_import_data.councilMeeting)
councilMeeting.workflowAdaptations = ['delayed', 'no_publication']
councilMeeting.itemWFValidationLevels = deepcopy(MONS_ITEM_WF_VALIDATION_LEVELS)
councilMeeting.itemConditionsInterface = (
    "Products.MeetingMons.interfaces.IMeetingItemCollegeMonsWorkflowConditions"
)
councilMeeting.itemActionsInterface = (
    "Products.MeetingMons.interfaces.IMeetingItemCollegeMonsWorkflowActions"
)
councilMeeting.meetingConditionsInterface = (
    "Products.MeetingMons.interfaces.IMeetingCollegeMonsWorkflowConditions"
)
councilMeeting.meetingActionsInterface = (
    "Products.MeetingMons.interfaces.IMeetingCollegeMonsWorkflowActions"
)
councilMeeting.transitionsToConfirm = []
councilMeeting.itemCopyGroupsStates = []
councilMeeting.transitionsForPresentingAnItem = (
    "proposeToServiceHead",
    "proposeToOfficeManager",
    "proposeToDivisionHead",
    "proposeToDirector",
    "validate",
    "present",
)


data.meetingConfigs = (collegeMeeting, councilMeeting)
