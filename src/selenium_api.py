import base64
import functools
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Union

import selenium
from packaging import version
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from utils.common_method import get_file_version
from utils.logger import get_logger
from utils.wait import Utilities

Log = get_logger()


class SeleniumApi:
    def __init__(self, timeout: int = 10) -> None:
        self.driver = None
        self.error_screenshot_directory: Union[str, Path] = "C:\\temp\\ErrorScreenShots"
        self.timeout = timeout

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_driver()

    def handle_exception(func): # noqa: N805
        """This decorator simply calls the wrapped function inside a try suite."""

        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return_result = func(self, *args, **kwargs)
                return return_result
            except Exception as e:
                self.save_screenshot_on_fail()
                Log.warning(f"Exception in Method {func.__name__} - {args} - {kwargs}")
                raise e

        return wrapper

    def set_error_screenshot_directory(self, directory):
        if directory:
            self.error_screenshot_directory = directory
        if not os.path.exists(self.error_screenshot_directory):
            os.makedirs(self.error_screenshot_directory)
            Log.info(f"Created {self.error_screenshot_directory} directory")

    def save_screenshot_on_fail(self):
        """The method is used to save the screenshot of failed step using seleniumHelper"""
        if sys.exc_info()[0]:
            fail_url = self.driver.current_url
            Log.info(f"URL of the failed step: {fail_url}")
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            file_path = self.error_screenshot_directory + "\\%s.png" % now
            self.driver.get_screenshot_as_file(file_path)
            Log.info(f"Screenshot of failed step is saved at {file_path}")
            return file_path

    def close_driver(self):
        """This method is used to quits the driver and closes every associated window"""
        self.driver.quit()

    def launch_web_browser(self, url, options: Options = None):
        """This method will call the Edge driver and
        open requested web url on Edge browser w.r.t seleniumHelper version

        :param url: Web url to open on the browser (ex:- https://example.com/)
        :param options: it is used to pass optional arguments required for edge browser
        :type url: str
        """
        if options is None:
            options = Options()
        current_version = version.parse(selenium.__version__)
        Log.info(f"Current Selenium Version: {current_version}")
        min_version = version.parse("4.6.0")
        if current_version <= min_version:
            self.driver = webdriver.Edge(
                service=EdgeService(EdgeChromiumDriverManager().install()),
                options=options,
            )
        else:
            self.driver = webdriver.Edge(options=options)
        self.driver.get(url)
        self.driver.maximize_window()
        Log.info(f"{url} launched successfully.")

    def wait_for_element(
        self,
        locator_type: str,
        locator_value: str,
        is_clickable=False,
        is_selectable=False,
        is_present=False,
        is_visible=False,
    ):
        """
        Wait until an element is clickable based on locator type and value.

        Args:
            locator_type (str): The type of locator (e.g., "id", "xpath", "class").
            locator_value (str): The value of the locator.
            is_clickable (bool): To check an element is visible & clickable.
            is_selectable (bool): To check an element is present & selectable
            is_present (bool): To check that an element is present on the DOM of a page.
            is_visible (bool): To check that an element is visible on the web page.

        Returns:
            WebElement: The WebElement object to interact with.


        """
        # Get the By constant dynamically based on the locator type
        by_locator = getattr(By, locator_type)
        Log.info(f" Locator type is: {by_locator}")

        if is_clickable:
            return WebDriverWait(self.driver, self.timeout).until(
                expected_conditions.element_to_be_clickable((by_locator, locator_value))
            )
        if is_selectable:
            return Select(
                WebDriverWait(self.driver, self.timeout).until(
                    expected_conditions.element_to_be_clickable(
                        (by_locator, locator_value)
                    )
                )
            )
        if is_present:
            return WebDriverWait(self.driver, self.timeout).until(
                expected_conditions.presence_of_element_located(
                    (by_locator, locator_value)
                )
            )
        if is_visible:
            return WebDriverWait(self.driver, self.timeout).until(
                expected_conditions.visibility_of_element_located(
                    (by_locator, locator_value)
                )
            )

    @handle_exception
    def click_element(
        self, locator_type: str, locator_value: str, use_js_click: bool = False
    ):
        """This method is used to perform click action on the element visible to UI
        :param locator_type: The type of locator (e.g., "id", "xpath", "class").
        :type locator_type: str
        :param locator_value: to find the web element to be clicked using locator
        :type locator_value: str
        :param use_js_click: Used to call the underlying JS method which gets called on
        element click, useful when other DIVs are blocking on top of the element
        :type use_js_click: bool
        """
        element = self.wait_for_element(
            is_clickable=True, locator_type=locator_type, locator_value=locator_value
        )
        if use_js_click:
            self.driver.execute_script("arguments[0].click();", element)
        else:
            element.click()
        Log.info(f"Clicked on {locator_value}")

    @handle_exception
    def enter_text(self, locator_type: str, input_element: str, text: str):
        """This method will find the web elements using xpath and will
        type/fill in the required field with string or characters when called
        :param locator_type: The type of locator (e.g., "id", "xpath", "class").
        :type locator_type: str
        :param input_element: to find the web element to be filled with string input
        :type input_element: str
        :param text: to send characters/string what is to be typed
        :type text: str
        """
        element = self.wait_for_element(
            is_clickable=True,
            locator_type=locator_type,
            locator_value=input_element,
        )
        element.clear() # Clear any existing text
        element.send_keys(text)
        element.is_selected()
        Log.info(f"'{text}' entered successfully.")

    @handle_exception
    def enter_text_without_element(self, text: str):
        """This method is used enter text, keys,
        string or characters without using locator
        :param text: text to enter keys/characters/string
        :type text: str
        """
        actions = ActionChains(self.driver)
        for character in text:
            actions.send_keys(character)
            actions.perform()
            Utilities.wait(
                1, "Wait for next char to enter"
            ) # Delay is given to enter one character at a time
            # to avoid the overlapping issue
        Log.info(f"Entered text is: {text}")

    @handle_exception
    def is_element_visible(
        self, locator_type: str, locator_value: str, is_exists: bool = False
    ):
        """
        This method is used to check if an element is present
        in DOM & visible on the web page
        :param locator_type: The type of locator (e.g., "id", "xpath", "class").
        :type locator_type: str
        :param locator_value: to find the web element to be exists/visible using locator
        :type locator_value: str
        :param is_exists: This is used check if an element exists in the DOM.
        Not necessarily mean to be is visible on Web UI.
        :type is_exists: bool
        """
        if is_exists:
            self.wait_for_element(
                is_present=True, locator_type=locator_type, locator_value=locator_value
            )
            Log.info(f"{locator_value} Element is present in the DOM")
        else:
            self.wait_for_element(
                is_visible=True, locator_type=locator_type, locator_value=locator_value
            )
            Log.info(f"{locator_value} Element is visible in the web UI")

    @handle_exception
    def clear_text(self, locator_type: str, locator_value: str):
        """
        This method is used to clear the text in the specified input field
        :param locator_type: The type of locator (e.g., "id", "xpath", "class").
        :type locator_type: str
        :param locator_value: locator of the input field
        from where to clear the text in it
        :type locator_value: str
        """
        input_element = self.wait_for_element(
            is_clickable=True, locator_type=locator_type, locator_value=locator_value
        )
        input_element.clear()
        Log.info(f"Cleared the text in the '{locator_value}' successfully")

    @handle_exception
    def get_text_value(self, locator_type: str, locator_value: str):
        """This method is used to get the text from specified web element
        :param locator_type: The type of locator (e.g., "id", "xpath", "class").
        :type locator_type: str
        :param locator_value: to find the web element get the text using its xpath
        :type locator_value: str
        """
        element = self.wait_for_element(
            is_visible=True, locator_type=locator_type, locator_value=locator_value
        )
        element_text = element.text
        Log.info(f"Element text is '{element_text}'")
        return element_text

    @handle_exception
    def select_checkbox(self, locator_type: str, checkbox_element: str):
        """This method will select the specified web element of a checkbox
        :param locator_type: The type of locator (e.g., "id", "xpath", "class").
        :type locator_type: str
        :param checkbox_element: xpath of the checkbox
         from where the web element is to be selected
        :type checkbox_element: str
        """
        check_box = self.wait_for_element(
            is_clickable=True, locator_type=locator_type, locator_value=checkbox_element
        )
        if not check_box.is_selected():
            self.driver.execute_script("arguments[0].click();", check_box)
        else:
            Log.info(f"{checkbox_element} is already selected")

    @handle_exception
    def click_element_using_cursor(self, locator_type: str, locator_value: str):
        """
        This Method will move mouse cursor to a specified web element and click on it

        :param locator_type: The type of locator (e.g., "id", "xpath", "class").
        :type locator_type: str
        :param locator_value: to find the web element get the text using its xpath
        :type locator_value: str
        """
        element = self.wait_for_element(
            is_visible=True, locator_type=locator_type, locator_value=locator_value
        )
        actions = ActionChains(self.driver)
        actions.move_to_element(element)
        actions.click()
        actions.perform()
        Log.info(f"Mouse moved to element: {locator_value} and clicked on it")

    def find_element_in_shadow_root(
        self, tag_name: str, css_selector: str, root_element: str = None
    ):
        """Finds an element inside a shadow root.

        :param tag_name: Tag name of the root element containing the shadow root.
        :param css_selector: CSS selector of the element inside the shadow root.
        :param root_element : Root element containing the shadow root.
        Defaults to None, which will search within the entire document.
        :Returns WebElement: The found element inside the shadow root.
        """
        if root_element is None:
            root_element = self.driver.find_element(By.TAG_NAME, tag_name)

        shadow_root = self.driver.execute_script(
            "return arguments[0].shadowRoot", root_element
        )
        return WebDriverWait(shadow_root, 10).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, css_selector)
            )
        )

    @handle_exception
    def select_from_dropdown_by_visible_text(
        self,
        locator_type: str,
        locator_value: str,
        element_name: str,
    ):
        """This method is used to select an element from a dropdown list by visible text
        :param locator_type: The type of locator (e.g., "id", "xpath", "class").
        :type locator_type: str
        :param locator_value: to find the web element get the text using its xpath
        :type locator_value: str
        :param element_name: The visible text of the element to be selected.
        :type element_name: str
        """
        element = self.wait_for_element(
            is_clickable=True, locator_type=locator_type, locator_value=locator_value
        )
        element.click()
        select = Select(element)
        select.select_by_visible_text(element_name)
        Log.info(f"The element {element_name} is selected from the {locator_value}")

    @handle_exception
    def move_slider_using_cursor(
        self, locator_type: str, locator_value: str, xrange: int, yrange: int
    ):
        """This method is used to move the slider from xrange to yrange
        :param locator_type: The type of locator (e.g., "id", "xpath", "class").
        :type locator_type: str
        :param locator_value: to find the web element get the text using its xpath
        :type locator_value: str
        :param xrange: the xrange of the slider
        :type locator_value: int
        :param yrange: The yrange of the slider
        :type element_name: int
        """
        element = self.wait_for_element(
            is_clickable=True, locator_type=locator_type, locator_value=locator_value
        )
        move = ActionChains(self.driver)
        move.click_and_hold(element).move_by_offset(xrange, yrange).release().perform()
        Log.info(
            f"The element in the {locator_value} is moved from {xrange} to {yrange}"
        )

    @handle_exception
    def get_canvas_image(self, locator_type: str, locator_value: str):
        """This method is used to fetch and decode the canvas image
        :param locator_type: The type of locator (e.g., "id", "xpath", "class").
        :type locator_type: str
        :param locator_value: to find the web element get the text using its xpath
        :type locator_value: str
        """
        element = self.wait_for_element(
            is_clickable=True, locator_type=locator_type, locator_value=locator_value
        )
        canvas_base64 = self.driver.execute_script(
            "return arguments[0].toDataURL('image/png').substring(21);", element
        )
        canvas_capture = base64.b64decode(canvas_base64)
        Log.info("Canvas Image has been decoded successfully.")
        return canvas_capture

    @handle_exception
    def wait_for_element_to_disappear(self, locator_type: str, locator_value: str):
        """
        Wait until an element disappears based on locator type and value.

        Args:
            locator_type (str): The type of locator (e.g., "id", "xpath", "class").
            locator_value (str): The value of the locator.
        """
        by_locator = getattr(By, locator_type)
        Log.info(f" Locator type is: {by_locator}")

        return WebDriverWait(self.driver, self.timeout).until(
            expected_conditions.invisibility_of_element_located(
                (by_locator, locator_value)
            )
        )

    @handle_exception
    def get_attribute(self, locator_type: str, locator_value: str, attribute: str):
        """This method is used to get the attribute from a specified web element
        :param locator_type: The type of locator (e.g., "id", "xpath", "class").
        :type locator_type: str
        :param locator_value: The value of the locator to find the web element.
        :type locator_value: str
        :param attribute: attribute of element.
        :type locator_value: str
        :return: The text value of the attribute otherwise None.
        :rtype: str or None
        """
        element = self.wait_for_element(
            is_visible=True, locator_type=locator_type, locator_value=locator_value
        )
        attribute_value = element.get_attribute(attribute)
        Log.info(f"{attribute} for element {locator_value} is {attribute_value}")

        return attribute_value
