# -*- coding: utf-8 -*-
#
# File: config.py
#
# Copyright (c) 2016 by Imio.be
# Generator: ArchGenXML Version 2.7
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#
from collections import OrderedDict

__author__ = (
    """Gauthier Bastien <g.bastien@imio.be>, Stephan Geulette <s.geulette@imio.be>"""
)
__docformat__ = "plaintext"

# Product configuration.
#
# The contents of this module will be imported into __init__.py, the
# workflow configuration and every content type module.
#
# If you wish to perform custom configuration, you may put a file
# AppConfig.py in your product's root directory. The items in there
# will be included (by importing) in this file if found.

from Products.CMFCore.permissions import setDefaultRoles
from Products.PloneMeeting import config as PMconfig

PROJECTNAME = "MeetingMons"

PMconfig.EXTRA_GROUP_SUFFIXES = [
    {
        "fct_title": u"divisionheads",
        "fct_id": u"divisionheads",
        "fct_orgs": [],
        "fct_management": False,
        "enabled": True,
    },
    {
        "fct_title": u"officemanagers",
        "fct_id": u"officemanagers",
        "fct_orgs": [],
        "fct_management": False,
        "enabled": True,
    },
    {
        "fct_title": u"serviceheads",
        "fct_id": u"serviceheads",
        "fct_orgs": [],
        "fct_management": False,
        "enabled": True,
    },
    {
        "fct_title": u"extraordinarybudget",
        "fct_id": u"extraordinarybudget",
        "fct_orgs": [],
        "fct_management": False,
        "enabled": True,
    },
    {
        "fct_title": u"budgetimpactreviewers",
        "fct_id": u"budgetimpactreviewers",
        "fct_orgs": [],
        "fct_management": False,
        "enabled": True,
    },
]

MONS_ITEM_WF_VALIDATION_LEVELS = (
    {
        "state": "itemcreated",
        "state_title": "itemcreated",
        "leading_transition": "-",
        "leading_transition_title": "-",
        "back_transition": "backToItemCreated",
        "back_transition_title": "backToItemCreated",
        "suffix": "creators",
        # only creators may manage itemcreated item
        "extra_suffixes": [],
        "enabled": "1",
    },
    {
        "state": "proposed_to_servicehead",
        "state_title": "proposed_to_servicehead",
        "leading_transition": "proposeToServiceHead",
        "leading_transition_title": "proposeToServiceHead",
        "back_transition": "backToProposedToServiceHead",
        "back_transition_title": "backToProposedToServiceHead",
        "suffix": "serviceheads",
        "extra_suffixes": [],
        "enabled": "1",
    },
    {
        "state": "proposed_to_officemanager",
        "state_title": "proposed_to_officemanager",
        "leading_transition": "proposeToOfficeManager",
        "leading_transition_title": "proposeToOfficeManager",
        "back_transition": "backToProposedToOfficeManager",
        "back_transition_title": "backToProposedToOfficeManager",
        "suffix": "officemanagers",
        "enabled": "1",
        "extra_suffixes": [],
    },
    {
        "state": "proposed_to_divisionhead",
        "state_title": "proposed_to_divisionhead",
        "leading_transition": "proposeToDivisionHead",
        "leading_transition_title": "proposeToDivisionHead",
        "back_transition": "backToProposedToDivisionHead",
        "back_transition_title": "backToProposedToDivisionHead",
        "suffix": "divisionheads",
        "enabled": "1",
        "extra_suffixes": [],
    },
    {
        "state": "proposed_to_director",
        "state_title": "proposed_to_director",
        "leading_transition": "proposeToDirector",
        "leading_transition_title": "proposeToDirector",
        "back_transition": "backToProposedToDirector",
        "back_transition_title": "backToProposedToDirector",
        "suffix": "reviewers",
        "extra_suffixes": [],
        "enabled": "1",
    },
)

# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ("Manager", "Owner", "Contributor"))

product_globals = globals()

# Dependencies of Products to be installed by quick-installer
# override in custom configuration
DEPENDENCIES = []

# Dependend products - not quick-installed - used in testcase
# override in custom configuration
PRODUCT_DEPENDENCIES = []

# extra suffixes while using 'meetingadvicefinances_workflow'
FINANCE_GROUP_SUFFIXES = (
    "financialcontrollers",
    "financialeditors",
    "financialreviewers",
    "financialmanagers",
)
FINANCE_STATE_TO_GROUPS_MAPPINGS = {
    "proposed_to_financial_controller": "financialcontrollers",
    "proposed_to_financial_editor": "financialeditors",
    "proposed_to_financial_reviewer": "financialreviewers",
    "proposed_to_financial_manager": "financialmanagers",
}

# states in which the finance advice may be given
FINANCE_WAITING_ADVICES_STATES = ["prevalidated_waiting_advices"]

# the id of the collection querying finance advices
FINANCE_ADVICES_COLLECTION_ID = "searchitemswithfinanceadvice"

# if True, a positive finances advice may be signed by a finances reviewer
# if not, only the finances manager may sign advices
POSITIVE_FINANCE_ADVICE_SIGNABLE_BY_REVIEWER = False

# text about FD advice used in templates
FINANCE_ADVICE_LEGAL_TEXT_PRE = (
    "<p>Attendu la demande d'avis adressée sur "
    "base d'un dossier complet au Directeur financier en date du {0};<br/></p>"
)

FINANCE_ADVICE_LEGAL_TEXT = (
    "<p>Attendu l'avis {0} du Directeur financier "
    "rendu en date du {1} conformément à l'article L1124-40 du Code de la "
    "démocratie locale et de la décentralisation;</p>"
)

FINANCE_ADVICE_LEGAL_TEXT_NOT_GIVEN = (
    "<p>Attendu l'absence d'avis du "
    "Directeur financier rendu dans le délai prescrit à l'article L1124-40 "
    "du Code de la démocratie locale et de la décentralisation;</p>"
)

STYLESHEETS = [{"id": "MeetingMons.css", "title": "MeetingMons CSS styles"}]
