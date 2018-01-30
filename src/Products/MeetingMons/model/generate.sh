#!/bin/sh
/srv/archgenxml/bin/archgenxml --cfg generate.conf MeetingMons.zargo -o tmp

# only keep workflows
cp -rf tmp/profiles/default/workflows/meetingcollegemons_workflow ../profiles/default/workflows
cp -rf tmp/profiles/default/workflows/meetingitemcollegemons_workflow ../profiles/default/workflows
rm -rf tmp
