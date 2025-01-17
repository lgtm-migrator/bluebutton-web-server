import os
import time
from django.test import TestCase

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys

from .selenium_cases import (
    Action,
    TESTCASE_BANNER_FMT,
    LNK_TXT_GET_TOKEN_V1,
    LNK_TXT_GET_TOKEN_PKCE_V1,
    LNK_TXT_GET_TOKEN_V2,
    LNK_TXT_GET_TOKEN_PKCE_V2,
    LNK_TXT_RESTART_TESTCLIENT,
    API_V2,
    API_V1,
    SEQ_LOGIN_MSLSX,
    SEQ_LOGIN_SLSX,
    PROD_URL,
)

USER_ACCOUNT_TESTS_LOGGING_FILE = "./docker-compose/tmp/bb2_account_tests.log"


class SeleniumGenericTests(TestCase):
    '''
    A super selenium tests to be extended by
    other selenium tests covering functional areas
    '''
    wait_completed = False

    def setUp(self):
        super(SeleniumGenericTests, self).setUp()
        # a bit waiting for selenium services ready for sure
        if not SeleniumGenericTests.wait_completed:
            time.sleep(20)
            SeleniumGenericTests.wait_completed = True
            print("set wait_completed={}".format(SeleniumGenericTests.wait_completed))
        else:
            print("wait_completed={}".format(SeleniumGenericTests.wait_completed))

        self.use_mslsx = os.environ['USE_MSLSX']
        self.use_debug = os.environ['USE_DEBUG']
        self.login_seq = SEQ_LOGIN_MSLSX if self.use_mslsx == 'true' else SEQ_LOGIN_SLSX
        print("use_mslsx={}, use_debug={}".format(self.use_mslsx, self.use_debug))

        opt = webdriver.ChromeOptions()
        opt.add_argument("--disable-dev-shm-usage")
        opt.add_argument("--disable-web-security")
        opt.add_argument("--allow-running-insecure-content")
        opt.add_argument("--no-sandbox")
        opt.add_argument("--disable-setuid-sandbox")
        opt.add_argument("--disable-webgl")
        opt.add_argument("--disable-popup-blocking")
        opt.add_argument("--enable-javascript")
        opt.add_argument('--allow-insecure-localhost')
        opt.add_argument('--window-size=1920,1080')
        opt.add_argument("--whitelisted-ips=''")

        if self.use_debug == 'true':
            self.driver = webdriver.Remote(
                command_executor='http://chrome:4444/wd/hub',
                desired_capabilities=DesiredCapabilities.CHROME, options=opt)
        else:
            opt.add_argument('--headless')
            self.driver = webdriver.Chrome(options=opt)

        self.actions = {
            Action.LOAD_PAGE: self._load_page,
            Action.FIND_CLICK: self._find_and_click,
            Action.FIND: self._find_and_return,
            Action.FIND_SEND_KEY: self._find_and_sendkey,
            Action.CHECK: self._check_page_title,
            Action.CHECK_PKCE_CHALLENGE: self._check_pkce_challenge,
            Action.CONTAIN_TEXT: self._check_page_content,
            Action.GET_SAMPLE_TOKEN_START: self._click_get_sample_token,
            Action.GET_SAMPLE_TOKEN_PKCE_START: self._click_get_sample_token_pkce,
            Action.BACK: self._back,
            Action.LOGIN: self._login,
            Action.SLEEP: self._sleep,
            Action.VALIDATE_EVENTS: self._validate_events,
        }

    def tearDown(self):
        self.driver.quit()
        super(SeleniumGenericTests, self).tearDown()

    def _validate_events(self, subj_line, key_line_prefix, **kwargs):
        with open(USER_ACCOUNT_TESTS_LOGGING_FILE, 'r') as f:
            log_records = f.readlines()
            email_subj_cnt = 0
            key_cnt = 0
            ak = None
            while log_records:
                r = log_records.pop(0)
                if r.startswith(subj_line):
                    # print("SUBJ: {}".format(r))
                    email_subj_cnt += 1
                elif key_line_prefix is not None and r.startswith(key_line_prefix):
                    # print("KEY: {}".format(r))
                    ak = r.split(key_line_prefix)[1]
                    key_cnt += 1
                else:
                    pass
                    # print("NOT COUNTED: {}".format(r))
            # assert one and only one expected email (subj line) found
            # if key_line_prefix is not None - need to extract activation key
            self.assertEqual(email_subj_cnt, 1)
            if key_line_prefix is not None:
                self.assertEqual(key_cnt, 1)
                self.assertIsNotNone(ak)
            return ak

    def _find_and_click(self, timeout_sec, by, by_expr, **kwargs):
        elem = WebDriverWait(self.driver, timeout_sec).until(EC.visibility_of_element_located((by, by_expr)))
        self.assertIsNotNone(elem)
        elem.click()
        return elem

    def _testclient_home(self, **kwargs):
        return self._find_and_click(30, By.LINK_TEXT, LNK_TXT_RESTART_TESTCLIENT, **kwargs)

    def _find_and_sendkey(self, timeout_sec, by, by_expr, txt, **kwargs):
        elem = WebDriverWait(self.driver, timeout_sec).until(EC.visibility_of_element_located((by, by_expr)))
        self.assertIsNotNone(elem)
        elem.send_keys(txt)
        return elem

    def _click_get_sample_token(self, **kwargs):
        return self._find_and_click(30, By.LINK_TEXT,
                                    LNK_TXT_GET_TOKEN_V2 if kwargs.get("api_ver", API_V1) == API_V2 else LNK_TXT_GET_TOKEN_V1)

    def _click_get_sample_token_pkce(self, **kwargs):
        return self._find_and_click(30, By.LINK_TEXT,
                                    LNK_TXT_GET_TOKEN_PKCE_V2 if kwargs.get("api_ver", API_V1) == API_V2
                                    else LNK_TXT_GET_TOKEN_PKCE_V1)

    def _find_and_return(self, timeout_sec, by, by_expr, **kwargs):
        elem = WebDriverWait(self.driver, timeout_sec).until(EC.visibility_of_element_located((by, by_expr)))
        self.assertIsNotNone(elem)
        return elem

    def _load_page(self, url, **kwargs):
        if url == PROD_URL or url == PROD_URL + "/":
            print("Skip loading page: {}".format(url))
        else:
            self.driver.get(url)

    def _check_page_title(self, timeout_sec, by, by_expr, fmt, resource_type, **kwargs):
        elem = self._find_and_return(timeout_sec, by, by_expr, **kwargs)
        if not (elem.text == fmt.format(resource_type, kwargs.get("api_ver"))):
            print("PAGE:{}".format(self.driver.page_source))
        self.assertEqual(elem.text, fmt.format(resource_type, kwargs.get("api_ver")))

    def _check_pkce_challenge(self, timeout_sec, by, by_expr, pkce, **kwargs):
        elem = self._find_and_return(timeout_sec, by, by_expr, **kwargs)
        if pkce:
            self.assertTrue(("code_challenge" in elem.text and "code_challenge_method" in elem.text))
        else:
            self.assertFalse(("code_challenge" in elem.text or "code_challenge_method" in elem.text))

    def _check_page_content(self, timeout_sec, by, by_expr, content_txt, **kwargs):
        elem = self._find_and_return(timeout_sec, by, by_expr, **kwargs)
        self.assertIn(content_txt, elem.text)

    def _back(self, **kwargs):
        self.driver.back()

    def _sleep(self, sec, **kwargs):
        time.sleep(sec)

    def _login(self, step, **kwargs):
        if self.use_mslsx == 'false':
            # dismiss Medicare.gov popup if present
            webdriver.ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
        self._play(self.login_seq, step, **kwargs)

    def _print_testcase_banner(self, test_name, api_ver, step_0, id_service, start=True):
        print()
        print("******************************************************************")
        print(TESTCASE_BANNER_FMT.format("START" if start else "END", test_name, api_ver, step_0,
                                         "MSLSX" if id_service == 'true' else "SLSX"))
        print("******************************************************************")
        print()

    def _play(self, lst, step, **kwargs):
        for s in lst:
            seq = s.get("sequence")
            # expects sequence of actions or action
            if seq is not None:
                self._play(seq, step, **kwargs)
            else:
                # single action
                action = s.get('action', None)
                step[0] = step[0] + 1
                # Click 'Deny' on DEMO info grant form:
                if action is not None:
                    print("{}:{}:".format(step[0], s.get("display", "Not available")))
                    if action == Action.LOGIN:
                        self.actions[action](*s.get("params", []), step, **kwargs)
                    else:
                        self.actions[action](*s.get("params", []), **kwargs)
                else:
                    raise ValueError("Invalid test case, expect dict with action...")
