# -*- coding: utf-8 -*-
from plone.testing import z2, zca
from plone.app.testing import FunctionalTesting
from Products.PloneMeeting.testing import PloneMeetingLayer
import Products.MeetingMons
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE


MM_ZCML = zca.ZCMLSandbox(filename="testing.zcml",
                          package=Products.MeetingMons,
                          name='MM_ZCML')

MM_Z2 = z2.IntegrationTesting(bases=(z2.STARTUP, MM_ZCML),
                              name='MM_Z2')

MM_TESTING_PROFILE = PloneMeetingLayer(
    zcml_filename="testing.zcml",
    zcml_package=Products.MeetingMons,
    additional_z2_products=('Products.MeetingMons',
                            'Products.MeetingCommunes',
                            'Products.PloneMeeting',
                            'Products.CMFPlacefulWorkflow',
                            'Products.PasswordStrength'),
    gs_profile_id='Products.MeetingMons:testing',
    name="MM_TESTING_PROFILE")

MM_TESTING_PROFILE_FUNCTIONAL = FunctionalTesting(
    bases=(MM_TESTING_PROFILE,), name="MM_TESTING_PROFILE_FUNCTIONAL")


MM_TESTING_ROBOT = FunctionalTesting(
    bases=(
        MM_TESTING_PROFILE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="MM_TESTING_ROBOT",
)
