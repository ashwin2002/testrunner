
from remote.remote_util import RemoteMachineShellConnection
from .tuq import QueryTests
import time
from deepdiff import DeepDiff
from membase.api.exception import CBQError

class QueryAdvisorTests(QueryTests):

    def setUp(self):
        super(QueryAdvisorTests, self).setUp()
        self.log.info("==============  QueryAdvisorTests setup has started ==============")
        self.index_to_be_created = self.input.param("index_to_be_created", '')

        if self.load_sample:
            self.rest.load_sample("travel-sample")
            init_time = time.time()
            while True:
                next_time = time.time()
                query_response = self.run_cbq_query("SELECT COUNT(*) FROM `" + self.bucket_name + "`")
                if query_response['results'][0]['$1'] == 31591:
                    break
                if next_time - init_time > 600:
                    break
                time.sleep(1)

            self.wait_for_all_indexes_online()
            list_of_indexes = self.run_cbq_query(query="select raw name from system:indexes")

            for index in list_of_indexes['results']:
                if index.find("primary") > 0:
                    continue
                elif index.find("inventory") > 0:
                    name = index.split("_")
                    scope, collection = name[1], name[2]
                    self.run_cbq_query(query="drop index {0}.{1}".format(collection,index), query_context='default:`travel-sample`.{0}'.format(scope))
                else:
                    self.run_cbq_query(query="drop index `travel-sample`.{0}".format(index))

        self.purge_all_sessions()

        self.log.info("==============  QueryAdvisorTests setup has completed ==============")
        self.log_config_info()

    def suite_setUp(self):
        super(QueryAdvisorTests, self).suite_setUp()
        self.log.info("==============  QueryAdvisorTests suite_setup has started ==============")
        self.log.info("==============  QueryAdvisorTests suite_setup has completed ==============")

    def tearDown(self):
        self.log.info("==============  QueryAdvisorTests tearDown has started ==============")
        travel_sample = self.get_bucket_from_name("travel-sample")
        if travel_sample:
            self.delete_bucket(travel_sample)
        self.log.info("==============  QueryAdvisorTests tearDown has completed ==============")
        super(QueryAdvisorTests, self).tearDown()

    def suite_tearDown(self):
        self.log.info("==============  QueryAdvisorTests suite_tearDown has started ==============")
        self.log.info("==============  QueryAdvisorTests suite_tearDown has completed ==============")
        super(QueryAdvisorTests, self).suite_tearDown()

    def get_statements(self, advisor_results):
        indexes = []
        statements = []
        for index in advisor_results['results'][0]['$1']['recommended_indexes']:
            indexes.append(index['index'])
            statements.append(index['statements'])
        return indexes, statements

    def purge_all_sessions(self):
        try:
            self.log.info("Purging all previous sessions")
            results = self.run_cbq_query(query="SELECT ADVISOR({'action':'list'}) as List", server=self.master)
            for task in results['results'][0]['List']:
                session = task['tasks_cache']['name']
                purge = self.run_cbq_query(query="SELECT ADVISOR({{'action':'purge', 'session':'{0}'}}) as Purge".format(session), server=self.master)
        except Exception as e:
            self.log.error("List/Purge sessions failed: {0}".format(e))
            self.fail()

    # Advisor on update statement
    def test_query_string(self):
        try:
            advise = self.run_cbq_query(query="SELECT ADVISOR(\"UPDATE `{0}` SET city = 'San Francisco' WHERE lower(city) = 'sanfrancisco'\")".format(self.bucket_name), server=self.master)
            simple_indexes, statements = self.get_statements(advise)
        except Exception as e:
            self.log.error("Advisor statement failed: {0}".format(e))
            self.fail()
        for index in simple_indexes:
            self.run_cbq_query(query=index)
            self.wait_for_all_indexes_online()
            try:
                results_with_advise_index = self.run_cbq_query(query="UPDATE `{0}` SET city = 'SF' WHERE lower(city) = 'san francisco'".format(self.bucket_name), server=self.master)
                self.assertEqual(results_with_advise_index['status'], 'success')
                self.assertEqual(results_with_advise_index['metrics']['mutationCount'], 938)
            finally:
                index_name = index.split("INDEX")[1].split("ON")[0].strip()
                self.run_cbq_query("DROP INDEX `{0}`.{1}".format(self.bucket_name,index_name))

    # same query: query count should be > 1
    def test_same_query_array(self):
        try:
            results_simple = self.run_cbq_query(query="SELECT ADVISOR([ \
                \"UPDATE `{0}` SET city = 'San Francisco' WHERE lower(city) = 'sanfrancisco'\", \
                \"UPDATE `{0}` SET city = 'San Francisco' WHERE lower(city) = 'sanfrancisco'\" \
            ])".format(self.bucket_name), server=self.master)
            simple_indexes, statements = self.get_statements(results_simple)
            self.assertEqual(statements[0][0]['run_count'], 2)
        except Exception as e:
            self.log.error("Advisor statement failed: {0}".format(e))
            self.fail()

    # similar query: statement count should be > 1
    def test_similar_query_array(self):    
        try:
            results_simple = self.run_cbq_query(query="SELECT ADVISOR([ \
                \"UPDATE `{0}` SET city = 'San Francisco' WHERE lower(city) = 'sanfrancisco'\", \
                \"UPDATE `{0}` SET city = 'San Francisco' WHERE lower(city) = 'saintfrancois'\" \
            ])".format(self.bucket_name), server=self.master)
            simple_indexes, statements = self.get_statements(results_simple)
            self.assertEqual(len(statements[0]), 2)
        except Exception as e:
            self.log.error("Advisor statement failed: {0}".format(e))
            self.fail()

    def test_query_output_array(self):
        # Run some queries
        query_paris = "SELECT airportname FROM `{0}` WHERE type = 'airport' and lower(city) = 'paris' AND country = 'France'".format(self.bucket_name)
        query_lyon = "SELECT airportname FROM `{0}` WHERE type ='airport' and lower(city) = 'lyon' AND country = 'France'".format(self.bucket_name)
        query_grenoble = "SELECT airportname FROM `{0}` WHERE type = 'airport' and lower(city) = 'grenoble' AND country = 'France'".format(self.bucket_name)
        results = self.run_cbq_query(query=query_paris, server=self.master)
        results = self.run_cbq_query(query=query_paris, server=self.master)
        results = self.run_cbq_query(query=query_paris, server=self.master)
        results = self.run_cbq_query(query=query_lyon, server=self.master)
        results = self.run_cbq_query(query=query_lyon, server=self.master)
        results = self.run_cbq_query(query=query_grenoble, server=self.master)
        try:
            results = self.run_cbq_query(query="select ADVISOR((SELECT RAW statement FROM system:completed_requests order by requestTime DESC limit 6)) as `Advise`".format(self.bucket_name), server=self.master)
            advises = results['results'][0]['Advise']
            query_count = dict()
            for index in advises['recommended_indexes']:
                for query in index['statements']:
                    query_count[query['statement']] = query['run_count']
            self.assertEqual(query_count[query_paris], 3)
            self.assertEqual(query_count[query_lyon], 2)
            self.assertEqual(query_count[query_grenoble], 1)
        except Exception as e:
            self.log.error("Advisor statement failed: {0}".format(e))
            self.fail()

    def test_query_array_arg_large(self,num=10):
        query_paris = "SELECT airportname FROM `{0}` WHERE type = 'airport' and lower(city) = 'paris' AND country = 'France'".format(self.bucket_name)
        query_array = [query_paris] * num
        try:
            results = self.run_cbq_query(query="select ADVISOR({0}) as `Advise`".format(query_array), server=self.master)
            advises = results['results'][0]['Advise']
            self.assertEqual(advises['recommended_indexes'][0]['statements'][0]['run_count'], num)
            self.assertEqual(advises['recommended_indexes'][0]['statements'][0]['statement'], query_paris)
        except Exception as e:
            self.log.error("Advisor statement failed: {0}".format(e))
            self.fail()

    # get session recommendation for completed session
    def test_get_session_completed(self):
        try:
            results = self.run_cbq_query(query="SELECT ADVISOR({'action': 'start', 'duration': '10s', 'query_count': 2 })", server=self.master)
            session = results['results'][0]['$1']['session']
            results = self.run_cbq_query(query="SELECT airportname FROM `{0}` WHERE lower(city) = 'lyon' AND country = 'France'".format(self.bucket_name), server=self.master)
            results = self.run_cbq_query(query="SELECT airportname FROM `{0}` WHERE lower(city) = 'lyon' AND country = 'France'".format(self.bucket_name), server=self.master)
            # Wait for session to complete
            self.sleep(10)
            results = self.run_cbq_query(query="SELECT ADVISOR({{'action': 'get', 'session': '{0}'}})".format(session), server=self.master)
            self.assertTrue('recommended_indexes' in results['results'][0]['$1'][0][0], "There are no recommended index: {0}".format(results['results'][0]['$1'][0][0]))
        except Exception as e:
            self.log.error("Advisor session failed: {0}".format(e))
            self.fail()

    def test_get_session_stopped(self):
        try:
            results = self.run_cbq_query(query="SELECT ADVISOR({'action': 'start', 'duration': '1h', 'query_count': 2 })", server=self.master)
            session = results['results'][0]['$1']['session']
            results = self.run_cbq_query(query="SELECT airportname FROM `{0}` WHERE lower(city) = 'lyon' AND country = 'France'".format(self.bucket_name), server=self.master)
            results = self.run_cbq_query(query="SELECT airportname FROM `{0}` WHERE lower(city) = 'lyon' AND country = 'France'".format(self.bucket_name), server=self.master)
            self.sleep(3)

            results = self.run_cbq_query(query="SELECT ADVISOR({{'action': 'stop', 'session': '{0}'}})".format(session), server=self.master)
            results = self.run_cbq_query(query="SELECT ADVISOR({{'action': 'get', 'session': '{0}'}})".format(session), server=self.master)
            self.assertTrue('recommended_indexes' in results['results'][0]['$1'][0][0], "There are no recommended index: {0}".format(results['results'][0]['$1'][0][0]))
        except Exception as e:
            self.log.error("Advisor session failed: {0}".format(e))
            self.fail()

    def test_stop_session(self):
        try:
            results = self.run_cbq_query(query="SELECT ADVISOR({'action': 'start', 'duration': '1234567ms', 'query_count': 2 })", server=self.master)
            session = results['results'][0]['$1']['session']
            results = self.run_cbq_query(query="SELECT ADVISOR({{'action': 'stop', 'session': '{0}'}})".format(session), server=self.master)
            results = self.run_cbq_query(query="SELECT ADVISOR({'action':'list'}) as List", server=self.master)
            task = results['results'][0]['List'][0]['tasks_cache']
            self.log.info("Task cache is {0}".format(task))
            self.assertEqual(list(task.keys()), ['class', 'delay', 'id', 'name', 'node', 'results', 'state', 'subClass', 'submitTime'])
            self.assertEqual(task['state'], "cancelled")
            self.assertEqual(task['delay'], "20m34.567s")
        except Exception as e:
            self.log.error("Advisor session failed: {0}".format(e))
            self.fail()

    def test_abort_session(self):
        try:
            results = self.run_cbq_query(query="SELECT ADVISOR({'action': 'start', 'duration': '3600s', 'query_count': 200 })", server=self.master)
            session = results['results'][0]['$1']['session']
            # Check session is active
            results = self.run_cbq_query(query="SELECT ADVISOR({'action':'list', 'status': 'active'}) as List", server=self.master)
            task = results['results'][0]['List'][0]['tasks_cache']
            self.log.info("Task cache is {0}".format(task))
            self.assertEqual(task['state'], "scheduled")
            self.assertEqual(task['delay'], "1h0m0s")
            self.assertEqual(task['name'], session)
            # Abort session
            results = self.run_cbq_query(query="SELECT ADVISOR({{'action': 'abort', 'session': '{0}'}})".format(session), server=self.master)
            results = self.run_cbq_query(query="SELECT ADVISOR({'action':'list', 'status': 'all'}) as List", server=self.master)
            self.assertEqual(results['results'][0]['List'],[])
        except Exception as e:
            self.log.error("Advisor session failed: {0}".format(e))
            self.fail()

    def test_purge_session_completed(self):
        try:
            results = self.run_cbq_query(query="SELECT ADVISOR({'action': 'start', 'duration': '5000ms', 'query_count': 2 })", server=self.master)
            session = results['results'][0]['$1']['session']
            results = self.run_cbq_query(query="SELECT airportname FROM `{0}` WHERE lower(city) = 'lyon' AND country = 'France'".format(self.bucket_name), server=self.master)
            results = self.run_cbq_query(query="SELECT airportname FROM `{0}` WHERE lower(city) = 'lyon' AND country = 'France'".format(self.bucket_name), server=self.master)
            # Wait for session to complete
            self.sleep(5)
            results = self.run_cbq_query(query="SELECT ADVISOR({'action':'list'}) as List", server=self.master)
            task = results['results'][0]['List'][0]['tasks_cache']
            self.assertEqual(task['state'], "completed")
            # Purge session
            results = self.run_cbq_query(query="SELECT ADVISOR({{'action': 'purge', 'session': '{0}'}})".format(session), server=self.master)
            results = self.run_cbq_query(query="SELECT ADVISOR({'action':'list', 'status': 'all'}) as List", server=self.master)
            self.assertEqual(results['results'][0]['List'],[])
        except Exception as e:
            self.log.error("Advisor session failed: {0}".format(e))
            self.fail()

    def test_purge_session_stopped(self):
        try:
            results = self.run_cbq_query(query="SELECT ADVISOR({'action': 'start', 'duration': '5000s', 'query_count': 2 })", server=self.master)
            session = results['results'][0]['$1']['session']
            results = self.run_cbq_query(query="SELECT airportname FROM `{0}` WHERE lower(city) = 'lyon' AND country = 'France'".format(self.bucket_name), server=self.master)
            results = self.run_cbq_query(query="SELECT airportname FROM `{0}` WHERE lower(city) = 'lyon' AND country = 'France'".format(self.bucket_name), server=self.master)
            # Stop session
            results = self.run_cbq_query(query="SELECT ADVISOR({{'action': 'stop', 'session': '{0}'}})".format(session), server=self.master)
            results = self.run_cbq_query(query="SELECT ADVISOR({'action':'list'}) as List", server=self.master)
            task = results['results'][0]['List'][0]['tasks_cache']
            self.assertEqual(task['state'], "cancelled")
            # Purge session
            results = self.run_cbq_query(query="SELECT ADVISOR({{'action': 'purge', 'session': '{0}'}})".format(session), server=self.master)
            results = self.run_cbq_query(query="SELECT ADVISOR({'action':'list', 'status': 'all'}) as List", server=self.master)
            self.assertEqual(results['results'][0]['List'],[])
        except Exception as e:
            self.log.error("Advisor session failed: {0}".format(e))
            self.fail()

    def test_purge_session_active(self):
        try:
            results = self.run_cbq_query(query="SELECT ADVISOR({'action': 'start', 'duration': '3600s', 'query_count': 200 })", server=self.master)
            session = results['results'][0]['$1']['session']
            # Check session is active
            list_all = self.run_cbq_query(query="SELECT ADVISOR({'action':'list', 'status': 'active'}) as List", server=self.master)
            task = list_all['results'][0]['List'][0]['tasks_cache']
            self.log.info("Task cache is {0}".format(task))
            self.assertEqual(task['state'], "scheduled")
            self.assertEqual(task['delay'], "1h0m0s")
            self.assertEqual(task['name'], session)
            # Purge session
            purge = self.run_cbq_query(query="SELECT ADVISOR({{'action': 'purge', 'session': '{0}'}})".format(session), server=self.master)
            list_all = self.run_cbq_query(query="SELECT ADVISOR({'action':'list', 'status': 'all'}) as List", server=self.master)
            self.assertEqual(list_all['results'][0]['List'],[])
        except Exception as e:
            self.log.error("Advisor session failed: {0}".format(e))
            self.fail()

    def test_list_session(self):
        try:
            results = self.run_cbq_query(query="SELECT ADVISOR({'action': 'start', 'duration': '99h', 'query_count': 2 })", server=self.master)
            active_session = results['results'][0]['$1']['session']
            results = self.run_cbq_query(query="SELECT ADVISOR({'action': 'start', 'duration': '50ms', 'query_count': 2 })", server=self.master)
            completed_session = results['results'][0]['$1']['session']
            results = self.run_cbq_query(query="SELECT ADVISOR({'action': 'start', 'duration': '1600m', 'query_count': 2 })", server=self.master)
            stopped_session = results['results'][0]['$1']['session']
            results = self.run_cbq_query(query="SELECT airportname FROM `{0}` WHERE lower(city) = 'lyon' AND country = 'France'".format(self.bucket_name), server=self.master)
            results = self.run_cbq_query(query="SELECT airportname FROM `{0}` WHERE lower(city) = 'lyon' AND country = 'France'".format(self.bucket_name), server=self.master)
            # Stop session
            results = self.run_cbq_query(query="SELECT ADVISOR({{'action': 'stop', 'session': '{0}'}})".format(stopped_session), server=self.master)
            # List sessions
            results = self.run_cbq_query(query="SELECT ADVISOR({'action':'list'}) as List", server=self.master)
            all_sessions = dict()
            for task in results['results'][0]['List']:
                all_sessions[task['tasks_cache']['state']] = task['tasks_cache']['name']
            self.assertEqual(len(all_sessions), 3)
            self.assertEqual(all_sessions['scheduled'], active_session)
            self.assertEqual(all_sessions['cancelled'], stopped_session)
            self.assertEqual(all_sessions['completed'], completed_session)
        except Exception as e:
            self.log.error("Advisor session failed: {0}".format(e))
            self.fail()

    def test_list_session_active(self):
        try:
            results = self.run_cbq_query(query="SELECT ADVISOR({'action': 'start', 'duration': '99h', 'query_count': 2 })", server=self.master)
            active_session = results['results'][0]['$1']['session']
            results = self.run_cbq_query(query="SELECT ADVISOR({'action': 'start', 'duration': '50ms', 'query_count': 2 })", server=self.master)
            completed_session = results['results'][0]['$1']['session']
            results = self.run_cbq_query(query="SELECT ADVISOR({'action': 'start', 'duration': '1600m', 'query_count': 2 })", server=self.master)
            stopped_session = results['results'][0]['$1']['session']
            results = self.run_cbq_query(query="SELECT airportname FROM `{0}` WHERE lower(city) = 'lyon' AND country = 'France'".format(self.bucket_name), server=self.master)
            results = self.run_cbq_query(query="SELECT airportname FROM `{0}` WHERE lower(city) = 'lyon' AND country = 'France'".format(self.bucket_name), server=self.master)
            # Stop session
            results = self.run_cbq_query(query="SELECT ADVISOR({{'action': 'stop', 'session': '{0}'}})".format(stopped_session), server=self.master)
            # List ACTIVE sessions
            results = self.run_cbq_query(query="SELECT ADVISOR({'action':'list', 'status':'active'}) as List", server=self.master)
            all_sessions = dict()
            for task in results['results'][0]['List']:
                all_sessions[task['tasks_cache']['state']] = task['tasks_cache']['name']
            self.assertEqual(len(all_sessions), 1)
            self.assertEqual(all_sessions['scheduled'], active_session)
        except Exception as e:
            self.log.error("Advisor session failed: {0}".format(e))
            self.fail()    
            
    def test_list_session_completed(self):
        try:
            results = self.run_cbq_query(query="SELECT ADVISOR({'action': 'start', 'duration': '99h', 'query_count': 2 })", server=self.master)
            active_session = results['results'][0]['$1']['session']
            results = self.run_cbq_query(query="SELECT ADVISOR({'action': 'start', 'duration': '50ms', 'query_count': 2 })", server=self.master)
            completed_session = results['results'][0]['$1']['session']
            results = self.run_cbq_query(query="SELECT ADVISOR({'action': 'start', 'duration': '1600m', 'query_count': 2 })", server=self.master)
            stopped_session = results['results'][0]['$1']['session']
            results = self.run_cbq_query(query="SELECT airportname FROM `{0}` WHERE lower(city) = 'lyon' AND country = 'France'".format(self.bucket_name), server=self.master)
            results = self.run_cbq_query(query="SELECT airportname FROM `{0}` WHERE lower(city) = 'lyon' AND country = 'France'".format(self.bucket_name), server=self.master)
            # Stop session
            results = self.run_cbq_query(query="SELECT ADVISOR({{'action': 'stop', 'session': '{0}'}})".format(stopped_session), server=self.master)
            # List COMPLETED sessions
            results = self.run_cbq_query(query="SELECT ADVISOR({'action':'list', 'status':'completed'}) as List", server=self.master)
            all_sessions = dict()
            for task in results['results'][0]['List']:
                all_sessions[task['tasks_cache']['state']] = task['tasks_cache']['name']
            self.assertEqual(len(all_sessions), 1)
            self.assertEqual(all_sessions['completed'], completed_session)
        except Exception as e:
            self.log.error("Advisor session failed: {0}".format(e))
            self.fail()    
    
    def test_list_session_all(self):
        try:
            results = self.run_cbq_query(query="SELECT ADVISOR({'action': 'start', 'duration': '99h', 'query_count': 2 })", server=self.master)
            active_session = results['results'][0]['$1']['session']
            results = self.run_cbq_query(query="SELECT ADVISOR({'action': 'start', 'duration': '50ms', 'query_count': 2 })", server=self.master)
            completed_session = results['results'][0]['$1']['session']
            results = self.run_cbq_query(query="SELECT ADVISOR({'action': 'start', 'duration': '1600m', 'query_count': 2 })", server=self.master)
            stopped_session = results['results'][0]['$1']['session']
            results = self.run_cbq_query(query="SELECT airportname FROM `{0}` WHERE lower(city) = 'lyon' AND country = 'France'".format(self.bucket_name), server=self.master)
            results = self.run_cbq_query(query="SELECT airportname FROM `{0}` WHERE lower(city) = 'lyon' AND country = 'France'".format(self.bucket_name), server=self.master)
            # Stop session
            results = self.run_cbq_query(query="SELECT ADVISOR({{'action': 'stop', 'session': '{0}'}})".format(stopped_session), server=self.master)
            # List ALL sessions
            results = self.run_cbq_query(query="SELECT ADVISOR({'action':'list', 'status':'all'}) as List", server=self.master)
            all_sessions = dict()
            for task in results['results'][0]['List']:
                all_sessions[task['tasks_cache']['state']] = task['tasks_cache']['name']
            self.assertEqual(len(all_sessions), 3)
            self.assertEqual(all_sessions['scheduled'], active_session)
            self.assertEqual(all_sessions['cancelled'], stopped_session)
            self.assertEqual(all_sessions['completed'], completed_session)
        except Exception as e:
            self.log.error("Advisor session failed: {0}".format(e))
            self.fail()

    def test_start_session_duration_value(self):
        durations = ['3600000000000ns','3600000000us','3600000ms','3600s','60m', '1h']
        try:
            for duration in durations:
                start = self.run_cbq_query(query="SELECT ADVISOR({{'action': 'start', 'duration': '{0}'}})".format(duration), server=self.master)
                session = start['results'][0]['$1']['session']
                active = self.run_cbq_query(query="SELECT ADVISOR({'action':'list'}) as List", server=self.master)
                delay = active['results'][0]['List'][0]['tasks_cache']['delay']
                self.assertEqual(delay, '1h0m0s')
                abort = self.run_cbq_query(query="SELECT ADVISOR({{'action':'abort', 'session':'{0}'}}) as Abort".format(session), server=self.master)
        except Exception as e:
            self.log.error("Advisor session failed: {0}".format(e))
            self.fail()

    def test_session_duration_completed(self):
        durations = ['1800000000ns','1800000us','1800ms','1.8s','0.03m', '0.0005h']
        try:
            for duration in durations:
                start = self.run_cbq_query(query="SELECT ADVISOR({{'action': 'start', 'duration': '{0}'}})".format(duration), server=self.master)
                session = start['results'][0]['$1']['session']
                self.sleep(2)
                complete = self.run_cbq_query(query="SELECT ADVISOR({'action':'list','status':'completed'}) as List", server=self.master)
                name = complete['results'][0]['List'][0]['tasks_cache']['name']
                delay = complete['results'][0]['List'][0]['tasks_cache']['delay']
                state = complete['results'][0]['List'][0]['tasks_cache']['state']
                self.assertEqual(delay, '1.8s')
                self.assertEqual(name, session)
                self.assertEqual(state, "completed")
                purge = self.run_cbq_query(query="SELECT ADVISOR({{'action':'purge', 'session':'{0}'}}) as Purge".format(session), server=self.master)
        except Exception as e:
            self.log.error("Advisor session failed: {0}".format(e))
            self.fail()

    def test_session_response_below(self):
        responses = ['100000000ns','100000us','100ms','0.1s', '0.000027h']
        query1=f"SELECT airportname FROM `{self.bucket_name}` WHERE type = 'airport' AND lower(city) = 'lyon' AND country = 'France'"
        query2=f"SELECT airportname FROM `{self.bucket_name}` WHERE type = 'airport' AND lower(city) = 'grenoble' AND country = 'France'"
        query3=f"SELECT airportname FROM `{self.bucket_name}` WHERE type = 'airport' AND lower(city) = 'nice' AND country = 'France'"
        try:
            for response in responses:
                start = self.run_cbq_query(query="SELECT ADVISOR({{'action': 'start', 'duration': '60s', 'response': '{0}'}})".format(response), server=self.master)
                session = start['results'][0]['$1']['session']
                results = self.run_cbq_query(query=query1, server=self.master)
                results = self.run_cbq_query(query=query2, server=self.master)
                results = self.run_cbq_query(query=query3, server=self.master)
                stop = self.run_cbq_query(query="SELECT ADVISOR({{'action':'stop', 'session':'{0}'}}) as Stop".format(session), server=self.master)
                get = self.run_cbq_query(query="SELECT ADVISOR({{'action':'get', 'session':'{0}'}}) as Get".format(session), server=self.master)
                run_count = get['results'][0]['Get'][0][0]['recommended_indexes'][0]['statements'][0]['run_count']
                self.assertEqual(run_count, 1)
                purge = self.run_cbq_query(query="SELECT ADVISOR({{'action':'purge', 'session':'{0}'}}) as Purge".format(session), server=self.master)
        except Exception as e:
            self.log.error("Advisor session failed: {0}".format(e))
            self.fail()

    def test_session_response_above(self):
        responses = ['9000000000000ns','9000000000us','9000000ms','9000s', '0.25h']
        query1=f"SELECT airportname FROM `{self.bucket_name}` WHERE type = 'airport' AND lower(city) = 'lyon' AND country = 'France'"
        query2=f"SELECT airportname FROM `{self.bucket_name}` WHERE type = 'airport' AND lower(city) = 'grenoble' AND country = 'France'"
        query3=f"SELECT airportname FROM `{self.bucket_name}` WHERE type = 'airport' AND lower(city) = 'nice' AND country = 'France'"
        try:
            for response in responses:
                start = self.run_cbq_query(query="SELECT ADVISOR({{'action': 'start', 'duration': '60s', 'response': '{0}'}})".format(response), server=self.master)
                session = start['results'][0]['$1']['session']
                results = self.run_cbq_query(query=query1, server=self.master)
                results = self.run_cbq_query(query=query2, server=self.master)
                results = self.run_cbq_query(query=query3, server=self.master)
                stop = self.run_cbq_query(query="SELECT ADVISOR({{'action':'stop', 'session':'{0}'}}) as Stop".format(session), server=self.master)
                get = self.run_cbq_query(query="SELECT ADVISOR({{'action':'get', 'session':'{0}'}}) as Get".format(session), server=self.master)
                advise = get['results'][0]['Get'][0]
                self.assertEqual(advise, [[]])
                purge = self.run_cbq_query(query="SELECT ADVISOR({{'action':'purge', 'session':'{0}'}}) as Purge".format(session), server=self.master)
        except Exception as e:
            self.log.error("Advisor session failed: {0}".format(e))
            self.fail()

    def test_session_profile(self):
        self.users = [{"id": "johnDoe", "name": "Jonathan Downing", "password": "password1"}]
        self.create_users()
        grant = self.run_cbq_query(query="GRANT {0} to {1}".format("admin", self.users[0]['id']),server=self.master)

        query1=f'SELECT airportname FROM `{self.bucket_name}` WHERE type = "airport" AND lower(city) = "lyon" AND country = "France"'
        query2=f'SELECT airportname FROM `{self.bucket_name}` WHERE type = "airport" AND lower(city) = "grenoble" AND country = "France"'
        query3=f'SELECT airportname FROM `{self.bucket_name}` WHERE type = "airport" AND lower(city) = "nice" AND country = "France"'

        try:
            start = self.run_cbq_query(query="SELECT ADVISOR({{'action': 'start', 'duration': '180s', 'profile': '{0}'}})".format(self.users[0]['id']), server=self.master)
            session = start['results'][0]['$1']['session']
            # Run query as other user
            # results = self.curl_with_roles(query1)
            # results = self.curl_with_roles(query1)
            results = self.run_cbq_query(query=query1, username=self.users[0]['id'], password=self.users[0]['password'], server=self.master)
            results = self.run_cbq_query(query=query1, username=self.users[0]['id'], password=self.users[0]['password'], server=self.master)
            # run query as current user
            results = self.run_cbq_query(query=query2, server=self.master)
            
            stop = self.run_cbq_query(query="SELECT ADVISOR({{'action':'stop', 'session':'{0}'}}) as Stop".format(session), server=self.master)
            get = self.run_cbq_query(query="SELECT ADVISOR({{'action':'get', 'session':'{0}'}}) as Get".format(session), server=self.master)

            for index in get['results'][0]['Get'][0][0]['recommended_indexes']:
                for statement in index['statements']:
                    self.assertEqual(statement['statement'], query1)
        except Exception as e:
            self.log.error("Advisor session failed: {0}".format(e))
            self.fail()

    def test_session_query_txn(self):
        query1=f'SELECT airportname FROM `{self.bucket_name}` WHERE type = "airport" AND lower(city) = "lyon" AND country = "France"'
        close_txn = ['ROLLBACK WORK', 'COMMIT']
        try:
            for rollback_or_commit in close_txn:
                start = self.run_cbq_query(query="SELECT ADVISOR({'action': 'start', 'duration': '15m'})", server=self.master)
                session = start['results'][0]['$1']['session']
                # Run query in transaction
                results = self.run_cbq_query(query="BEGIN WORK", server=self.master)
                query_params = {'txid': results['results'][0]['txid']}
                results = self.run_cbq_query(query=query1, query_params=query_params, server=self.master)
                results = self.run_cbq_query(query=rollback_or_commit, query_params=query_params, server=self.master)
                # Stop and check session advise
                stop = self.run_cbq_query(query="SELECT ADVISOR({{'action':'stop', 'session':'{0}'}}) as Stop".format(session), server=self.master)
                get = self.run_cbq_query(query="SELECT ADVISOR({{'action':'get', 'session':'{0}'}}) as Get".format(session), server=self.master)
                for index in get['results'][0]['Get'][0][0]['recommended_indexes']:
                    for statement in index['statements']:
                        self.assertEqual(statement['statement'], query1)
        except Exception as e:
            self.log.error("Advisor session failed: {0}".format(e))
            self.fail()

    def test_negative_txn(self):
        results = self.run_cbq_query(query="BEGIN WORK", server=self.master)
        query_params = {'txid': results['results'][0]['txid']}
        error = "advisor function is not supported within the transaction"
        try:
            start = self.run_cbq_query(query="SELECT ADVISOR({'action': 'start', 'duration': '15m'})", query_params=query_params, server=self.master)
            self.fail("Start session did not fail. Error expected: {0}".format(error))
        except CBQError as ex:
            self.assertTrue(str(ex).find(error) > 0)
        else:
            self.fail("There were no errors. Error expected: {0}".format(error))

    def test_session_query_count(self):
        query_lyon=f'SELECT airportname FROM `{self.bucket_name}` WHERE type = "airport" AND lower(city) = "lyon" AND country = "France"'
        query_grenoble=f'SELECT airportname FROM `{self.bucket_name}` WHERE type = "airport" AND lower(city) = "grenoble" AND country = "France"'
        query_nice=f'SELECT airportname FROM `{self.bucket_name}` WHERE type = "airport" AND lower(city) = "nice" AND country = "France"'
        try:
            start = self.run_cbq_query(query="SELECT ADVISOR({'action': 'start', 'duration': '15m', 'query_count': 6})", server=self.master)
            session = start['results'][0]['$1']['session']
            # Run 9 queries 
            results = self.run_cbq_query(query=query_lyon, server=self.master)
            results = self.run_cbq_query(query=query_grenoble, server=self.master)
            results = self.run_cbq_query(query=query_nice, server=self.master)
            results = self.run_cbq_query(query=query_lyon, server=self.master)
            results = self.run_cbq_query(query=query_grenoble, server=self.master)
            results = self.run_cbq_query(query=query_lyon, server=self.master)
            results = self.run_cbq_query(query=query_nice, server=self.master)
            results = self.run_cbq_query(query=query_grenoble, server=self.master)
            results = self.run_cbq_query(query=query_nice, server=self.master)
            # Stop and check session advise. We should only see 6 queries count = 3*lyon + 2*grenoble + 1*nice
            stop = self.run_cbq_query(query="SELECT ADVISOR({{'action':'stop', 'session':'{0}'}}) as Stop".format(session), server=self.master)
            get = self.run_cbq_query(query="SELECT ADVISOR({{'action':'get', 'session':'{0}'}}) as Get".format(session), server=self.master)
            queries_count = dict()
            for index in get['results'][0]['Get'][0][0]['recommended_indexes']:
                for query in index['statements']:
                    queries_count[query['statement']] = query['run_count']
            self.assertEqual(queries_count[query_lyon], 3)
            self.assertEqual(queries_count[query_grenoble], 2)
            self.assertEqual(queries_count[query_nice], 1)
        except Exception as e:
            self.log.error("Advisor session failed: {0}".format(e))
            self.fail()

    def test_get_active_session(self):
        pass

    def test_negative_query_syntax_error(self):
        pass

    def test_negative_invalid_arg(self):
        pass

    def test_negative_missing_arg(self):
        pass

    def test_negative_array(self):
        pass

    def test_session_query_cancel(self):
        pass

    def test_session_query_timeout(self):
        pass

    def test_session_collection(self):
        pass

    def test_session_collection_context(self):
        pass

    def test_session_collection_join(self):
        pass

    def test_session_start_authorization(self):
        pass

    def test_session_list_authorization(self):
        pass






                    






















        





    




        












            





        


