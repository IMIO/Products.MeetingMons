# -*- coding: utf-8 -*-
#
# File: MeetingMons.py
#
# Copyright (c) 2016 by IMIO
# Generator: ArchGenXML Version 2.7
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Andre NUYENS <andre.nuyens@imio.be>"""
__docformat__ = 'plaintext'


# Product configuration.
#
# The contents of this module will be imported into __init__.py, the
# workflow configuration and every content type module.
#
# If you wish to perform custom configuration, you may put a file
# AppConfig.py in your product's root directory. The items in there
# will be included (by importing) in this file if found.

from Products.CMFCore.permissions import setDefaultRoles
##code-section config-head #fill in your manual code here
from collections import OrderedDict
##/code-section config-head


PROJECTNAME = "MeetingMons"

# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner', 'Contributor'))

product_globals = globals()

# Dependencies of Products to be installed by quick-installer
# override in custom configuration
DEPENDENCIES = []

# Dependend products - not quick-installed - used in testcase
# override in custom configuration
PRODUCT_DEPENDENCIES = []

##code-section config-bottom #fill in your manual code here
from Products.PloneMeeting import config as PMconfig
MONSROLES = {}
MONSROLES['budgetimpactreviewers'] = 'MeetingBudgetImpactReviewer'
MONSROLES['serviceheads'] = 'MeetingServiceHead'
MONSROLES['officemanagers'] = 'MeetingOfficeManager'
MONSROLES['extraordinarybudget'] = 'MeetingExtraordinaryBudget'
MONSROLES['divisionheads'] = 'MeetingDivisionHead'
PMconfig.MEETINGROLES.update(MONSROLES)
PMconfig.MEETING_GROUP_SUFFIXES = PMconfig.MEETINGROLES.keys()
#IN THE FUTURE : the divisionhead will use the default 'MeetingReviewer' role in replace to director

MONSMEETINGREVIEWERS = OrderedDict([('reviewers', 'proposed_to_director'),
                                    ('divisionheads', 'proposed_to_divisionhead'),
                                    ('officemanagers', 'proposed_to_officemanager'),
                                    ('serviceheads', 'proposed_to_servicehead'), ])
PMconfig.MEETINGREVIEWERS = MONSMEETINGREVIEWERS

# Define PloneMeeting-specific permissions
AddAnnex = 'PloneMeeting: Add annex'
setDefaultRoles(AddAnnex, ('Manager', 'Owner'))
# We need 'AddAnnex', which is a more specific permission than
# 'PloneMeeting: Add MeetingFile', because decision-related annexes, which are
# also MeetingFile instances, must be secured differently.
# There is no permission linked to annex deletion. Deletion of annexes is allowed
# if one has the permission 'Modify portal content' on the corresponding item.
ReadDecision = 'PloneMeeting: Read decision'
WriteDecision = 'PloneMeeting: Write decision'
setDefaultRoles(ReadDecision, ('Manager',))
setDefaultRoles(WriteDecision, ('Manager',))

STYLESHEETS = [{'id': 'meetingmons.css',
                'title': 'MeetingMons CSS styles'}]

# define some more value in MeetingConfig.topicsInfo so extra topics are created for each MeetingConfig
##/code-section config-bottom


# Load custom configuration not managed by archgenxml
try:
    from Products.MeetingMons.AppConfig import *
except ImportError:
    pass
