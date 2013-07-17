# -*- coding: utf-8 -*-
from plone.testing import z2, zca
from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import FunctionalTesting
import Products.MeetingMons


MC_ZCML = zca.ZCMLSandbox(filename="testing.zcml",
                          package=Products.MeetingMons,
                          name='MC_ZCML')

MC_Z2 = z2.IntegrationTesting(bases=(z2.STARTUP, MC_ZCML),
                              name='MC_Z2')

MC_TEST_PROFILE = PloneWithPackageLayer(
    zcml_filename="testing.zcml",
    zcml_package=Products.MeetingMons,
    additional_z2_products=('Products.MeetingMons',
                            'Products.PloneMeeting',
                            'Products.CMFPlacefulWorkflow'),
    gs_profile_id='Products.MeetingMons:testing',
    name="MC_TEST_PROFILE")

MC_TEST_PROFILE_FUNCTIONAL = FunctionalTesting(
    bases=(MC_TEST_PROFILE,), name="MC_TEST_PROFILE_FUNCTIONAL")
