import os.path
import sys
import tempfile
from testlinkapi import TestlinkAPIClient


class testlink():
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self, build_version='', project_name):
        self.tlink = TestlinkAPIClient()
        self.projectname = project_name
        self.build_version = build_version

        pid = self.tlink.get_project_id_by_name(project_name)
        if not pid:
            sys.stderr.write(
                '\nFailed to get TL project ID {}\n'.format(project_name)
            )
        else:
            if os.environ.get('TVERBOSE'):
                sys.stderr.write('\nPROJECT ID: {}\n'.format(pid))

        self.projectid = pid
        self.testplanid = None
        self.testplanname = None
        self.testcaseid = None
        self.testcaseexternalid = None
        self.testcaseversion = None
        self.testprojectid = None

        # Since currently get_test_suite_id is broken, use temporary
        # hardcoded ID for your suite
        self.testsuiteid = 1
        self.tpid = None

    def start_suite(self, name, attrs):
        '''
        In case Testlink test plan does not exists,
        Tonat should create it

        '''
        tplan = self.tlink.get_test_plan_by_name(self.projectname, name)
        if 'code' in tplan[0]:
            data = {
                'testplanname': name,
                'testprojectname': self.projectname,
            }
            rtp = self.tlink.create_test_plan(**data)
            if 'code' in rtp[0]:
                if os.environ.get('TVERBOSE'):
                    sys.stderr.write(
                        'Failed to create Test Plan [{}] with [{}]'.format(
                            name, rtp[0]['message']
                        )
                    )
                return False
            # Save test plan id for later use
            self.testplanid = rtp[0]['id']
            self.testprojectid = rtp[0]['testproject_id']
            b = {'testplanid': self.testplanid,
                 'buildname': self.build_version}
            if os.environ.get('TVERBOSE'):
                sys.stderr.write('\nADD BUILD ARGS: {}\n'.format(b))
            self._add_build(**b)
            return True
        self.testplanid = tplan[0]['id']
        self.testprojectid = tplan[0]['testproject_id']
        self.testplanname = name
        b = {'testplanid': self.testplanid,
             'buildname': self.build_version}
        if os.environ.get('TVERBOSE'):
            sys.stderr.write('\nADD BUILD ARGS: {}\n'.format(b))
        self._add_build(**b)
        return True

    def start_test(self, name, attrs):
        '''
        Search for test case with "name" in Testlink
        and if not found creat it and add to the
        'Tonat' Testlink Suite

        If not found:
        1. Create new Test Case to suite 'Tonat'
        2. Add Test Case to Test Plan

        If found
        1. Add Test Case to Test Plan
        '''

        tc = self.tlink.get_test_case_by_name(name)
        if os.environ.get('TVERBOSE'):
            sys.stderr.write('\nGET TEST CASE RESPONSE: {}\n'.format(tc))
        if not tc:
            if os.environ.get('TVERBOSE'):
                sys.stderr.write(
                    '\nDid not found test case [{}]\n'.format(name)
                )
            data = {
                'testprojectid': self.projectid,
                'testsuiteid': self.testsuiteid,
                'testcasename': name,
                'summary': attrs['doc']
            }
            ntc = self.tlink.create_test_case(**data)
            if not 'status' in ntc[0]:
                if os.environ.get('TVERBOSE'):
                    sys.stderr.write(
                        '\nFailed to create test case {}\n'.format(name)
                    )
                return False
            self.testcaseid = ntc[0]['id']
            self.testcaseexternalid = 'EON-{}'.format(ntc[0]['external_id'])
            self.testcaseversion = ntc[0]['version_number']
        else:
            self.testcaseid = tc[0]['testcase_id']
            self.testcaseexternalid = 'EON-{}'.format(tc[0]['tc_external_id'])
            self.testcaseversion = int(tc[0]['version'])

        data = {
            'testprojectid': self.testprojectid,
            'testplanid': self.testplanid,
            'testcaseexternalid': self.testcaseexternalid,
            'version': self.testcaseversion,
        }
        if os.environ.get('TVERBOSE'):
            sys.stderr.write('\nADD TEST CASE TO PLAN ARGS: {}\n'.format(data))

        add_tc = ''
        try:
            add_tc = self.tlink.add_test_case_to_test_plan(**data)
        except:
            if os.environ.get('TVERBOSE'):
                sys.stderr.write('\nFAILED TO ADD TEST CASE TO TEST PLAN\n')

        if os.environ.get('TVERBOSE'):
            sys.stderr.write(
                'ADD TEST CASE TO PLAN RESPONSE: {}'.format(add_tc)
            )

        return True

    def end_test(self, name, attrs):
        '''
        Report Test Case result

        1. Get test plan id
        2. Get test case id
        3. Update test case result

        '''
        planid = self.testplanid
        caseid = self.testcaseid
        data = {
            'testcaseid': caseid,
            'testplanid': planid,
        }
        if attrs['status'] == 'PASS':
            data['status'] = 'p'
        else:
            data['status'] = 'f'
        if os.environ.get('TVERBOSE'):
            sys.stderr.write('\nREPORT RESULT ARGS: {}\n'.format(data))
        tr = self.tlink.report_test_case_result(**data)
        if os.environ.get('TVERBOSE'):
            sys.stderr.write('\nTEST CASE RESULT RESPONSE: {}\n'.format(tr))

    def end_suite(self, name, attrs):
        pass

    def _add_build(self, **bdata):
        '''
        Add build to the given test plan, in case such
        does not exists already

        Args (dict):
            testplanid
            buildname

        '''
        tb = self.tlink.create_build(**bdata)
        return True

