# -*- coding: utf-8 -*-
from plone.app.testing import FunctionalTesting
from plone.testing import z2
from plone.testing import zca
from Products.MeetingCommunes.testing import MCLayer

import Products.MeetingMons

MM_ZCML = zca.ZCMLSandbox(filename="testing.zcml",
                          package=Products.MeetingMons,
                          name='MM_ZCML')

MM_Z2 = z2.IntegrationTesting(bases=(z2.STARTUP, MM_ZCML),
                              name='MM_Z2')

MM_TESTING_PROFILE = MCLayer(
    zcml_filename="testing.zcml",
    zcml_package=Products.MeetingMons,
    additional_z2_products=('imio.dashboard',
                            'Products.MeetingMons',
                            'Products.MeetingCommunes',
                            'Products.PloneMeeting',
                            'Products.CMFPlacefulWorkflow',
                            'Products.PasswordStrength'),
    gs_profile_id='Products.MeetingMons:testing',
    name="MM_TESTING_PROFILE")

MM_TESTING_PROFILE_FUNCTIONAL = FunctionalTesting(
    bases=(MM_TESTING_PROFILE,), name="MM_TESTING_PROFILE_FUNCTIONAL")
