#!/usr/bin/python
"""
Testlink API client
"""
import xmlrpclib


class TestlinkAPIClient():
    def __init__(self, devKey="put your key here"):
        self.server = xmlrpclib.Server('http://put your testlink URL|IP here/lib/api/xmlrpc.php')
        self.devKey = devKey

    def get_test_plan_by_name(self, testprojectname, testplanname):
        data = {
            "devKey": self.devKey,
            "testprojectname": testprojectname,
            "testplanname": testplanname
        }
        return self.server.tl.getTestPlanByName(data)

    def create_test_plan(self, **data):
        '''
        Create Test Plan on demand

        Args:
            'testprojectname'  test project name,
            'testplanname'     test plan name,
            'notes'            test plan notes, default value is:
                "This Test Plan was generated automatically"

        Returns dict on success:
        [{
            'additionalInfo': '',
            'id': '41',
            'message': 'Success!',
            'operation': 'createTestPlan',
            'status': True,
        }]

        Returns dict on failure (for example - test plan exists already):
        [{
            'code': 3034,
            'message': '(createTestPlan) - Test Plan (name:Temporary test \
                plan) Already EXITS on Test Project (name:Tonian Eon).'
        }]
        '''
        data['devKey'] = self.devKey
        if not 'notes' in data:
            data['notes'] = "This Test Plan was generated automatically"
        return self.server.tl.createTestPlan(data)

    def create_build(self, **data):
        data['devKey'] = self.devKey
        data['buildnotes'] = 'This build was automatically generated'
        return self.server.tl.createBuild(data)

    def create_test_case(self, **data):
        '''
        Create new test case in Testlink

        Args: (dict)
            testprojectid
            testsuiteid
            testcasename
            summary
            steps (optional, default: '')

        '''
        data['devKey'] = self.devKey
        if not 'steps' in data:
            data['steps'] = ''
        data['actiononduplicatedname'] = 'block'
        data['checkduplicatedname'] = 'true'
        data['authorlogin'] = 'jean'

        return self.server.tl.createTestCase(data)

    def get_project_id_by_name(self, projectname):
        '''
        Get Project id by its name

        Args:
            project name

        '''
        data = {
            'devKey': self.devKey
        }
        for tmp_project in self.server.tl.getProjects(data):
            if (tmp_project['name'] == projectname):
                return tmp_project['id']
        return False

    def get_test_suite_id(self, testplanid, testsuitename):
        '''
        Get Test Suite ID

        Args:
            testplanid
            testsuitename

        BUG: 'getTestSuitesForTestPlan' in xmlrpc.php returns
             nothing.

        '''
        data = {
            'devKey': self.devKey,
            'testplanid': testplanid
        }
        '''
        suites = self.getTestSuitesForTestPlanByName(
            testprojectname, testplanname
        )
        for tmp_suite in self.getTestSuitesForTestPlanByName(
            testprojectname, testplanname
        ):
            if (tmp_suite['name'] == testsuitename):
                return tmp_suite['id']
        # Return None if no matching projects found
        '''

    def add_test_case_to_test_plan(self, **data):
        '''
        Add existing test case into given Test Plan

        Args (dict):
            testprojectid
            testplanid
            testcaseexternalid
            version
        '''

        data['devKey'] = self.devKey
        return self.server.tl.addTestCaseToTestPlan(data)

    def get_test_case_by_name(self, tcname):
        '''
        Get test case detailes by its name

        Args:
            test case name

        '''
        tc_byname = {
            "devKey": self.devKey,
            "testcasename": tcname
        }

        tc = self.server.tl.getTestCaseIDByName(tc_byname)
        if not 'id' in tc[0]:
            return False

        tc_byid = {
            'devKey': self.devKey,
            'testcaseid': tc[0]['id'],
        }
        return self.server.tl.getTestCase(tc_byid)
