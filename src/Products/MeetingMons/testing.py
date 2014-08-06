# -*- coding: utf-8 -*-
from plone.testing import z2, zca
from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import FunctionalTesting
import Products.MeetingMons


MM_ZCML = zca.ZCMLSandbox(filename="testing.zcml",
                          package=Products.MeetingMons,
                          name='MC_ZCML')

MM_Z2 = z2.IntegrationTesting(bases=(z2.STARTUP, MM_ZCML),
                              name='MM_Z2')

MM_TEST_PROFILE = PloneWithPackageLayer(
    zcml_filename="testing.zcml",
    zcml_package=Products.MeetingMons,
    additional_z2_products=('Products.MeetingMons',
                            'Products.PloneMeeting',
                            'Products.CMFPlacefulWorkflow'),
    gs_profile_id='Products.MeetingMons:testing',
    name="MM_TEST_PROFILE")

MM_TEST_PROFILE_FUNCTIONAL = FunctionalTesting(
    bases=(MM_TEST_PROFILE,), name="MM_TEST_PROFILE_FUNCTIONAL")
