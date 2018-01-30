# -*- coding: utf-8 -*-
from plone.testing import z2, zca
from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import FunctionalTesting
import Products.MeetingMons
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE

MC_ZCML = zca.ZCMLSandbox(filename="testing.zcml",
                          package=Products.MeetingMons,
                          name='MC_ZCML')

MC_Z2 = z2.IntegrationTesting(bases=(z2.STARTUP, MC_ZCML),
                              name='MC_Z2')

MC_TESTING_PROFILE = PloneWithPackageLayer(
    zcml_filename="testing.zcml",
    zcml_package=Products.MeetingMons,
    additional_z2_products=('imio.dashboard',
                            'Products.MeetingMons',
                            'Products.PloneMeeting',
                            'Products.CMFPlacefulWorkflow',
                            'Products.PasswordStrength'),
    gs_profile_id='Products.MeetingMons:testing',
    name="MC_TESTING_PROFILE")

MC_TESTING_PROFILE_FUNCTIONAL = FunctionalTesting(
    bases=(MC_TESTING_PROFILE,), name="MC_TESTING_PROFILE_FUNCTIONAL")

MC_DEMO_TESTING_PROFILE = PloneWithPackageLayer(
    zcml_filename="testing.zcml",
    zcml_package=Products.MeetingMons,
    additional_z2_products=('imio.dashboard',
                            'Products.MeetingMons',
                            'Products.PloneMeeting',
                            'Products.CMFPlacefulWorkflow',
                            'Products.PasswordStrength'),
    gs_profile_id='Products.MeetingMons:demo',
    name="MC_TESTING_PROFILE")

MC_TESTING_ROBOT = FunctionalTesting(
    bases=(
        MC_DEMO_TESTING_PROFILE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="MC_TESTING_ROBOT",
)
