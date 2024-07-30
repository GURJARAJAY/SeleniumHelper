's a sample README file for your `SeleniumApi` class. This README provides an overview of the class, its methods, and usage instructions.
---

# SeleniumApi README

## Overview

The `SeleniumApi` class provides a wrapper around Selenium WebDriver for automating web browser interactions. It includes various methods for interacting with web elements, handling exceptions, and taking screenshots on failure. This class is designed to work with the Edge browser but can be extended to support other browsers.

## Prerequisites

Ensure you have the following installed:

- Python 3.x
- Selenium WebDriver
- `webdriver_manager` for managing browser drivers
- `packaging` for version comparisons

You can install the necessary Python packages using pip:

```bash
pip install selenium webdriver-manager packaging
```

## Usage

### Initialization

To use the `SeleniumApi` class, you first need to create an instance of it. Optionally, you can set a custom timeout value.

```python
from selenium_api import SeleniumApi

with SeleniumApi(timeout=10) as api:
    api.clear_text


```

### Methods

#### `launch_web_browser(url, options: Options = None)`

Launches the Edge browser and opens the specified URL.

- **`url`**: The URL to open in the browser.
- **`options`**: Optional `Options` object to configure the browser.

#### `wait_for_element(locator_type: str, locator_value: str, is_clickable=False, is_selectable=False, is_present=False, is_visible=False)`

Waits for an element to meet specific conditions (clickable, selectable, present, or visible).

- **`locator_type`**: Type of locator (e.g., `"id"`, `"xpath"`, `"class"`).
- **`locator_value`**: Value of the locator.
- **`is_clickable`**: Wait until the element is clickable.
- **`is_selectable`**: Wait until the element is selectable (for dropdowns).
- **`is_present`**: Wait until the element is present in the DOM.
- **`is_visible`**: Wait until the element is visible on the web page.

#### `click_element(locator_type: str, locator_value: str, use_js_click: bool = False)`

Clicks on an element using its locator.

- **`locator_type`**: Type of locator.
- **`locator_value`**: Value of the locator.
- **`use_js_click`**: If `True`, uses JavaScript to click the element.

#### `enter_text(locator_type: str, input_element: str, text: str)`

Enters text into an input field.

- **`locator_type`**: Type of locator.
- **`input_element`**: Locator value for the input field.
- **`text`**: Text to enter into the field.

#### `enter_text_without_element(text: str)`

Enters text without using a locator.

- **`text`**: Text to enter.

#### `is_element_visible(locator_type: str, locator_value: str, is_exists: bool = False)`

Checks if an element is visible or exists in the DOM.

- **`locator_type`**: Type of locator.
- **`locator_value`**: Value of the locator.
- **`is_exists`**: If `True`, checks if the element exists in the DOM.

#### `clear_text(locator_type: str, locator_value: str)`

Clears the text in an input field.

- **`locator_type`**: Type of locator.
- **`locator_value`**: Locator value for the input field.

#### `get_text_value(locator_type: str, locator_value: str)`

Gets the text value from a web element.

- **`locator_type`**: Type of locator.
- **`locator_value`**: Locator value for the element.

#### `select_checkbox(locator_type: str, checkbox_element: str)`

Selects a checkbox.

- **`locator_type`**: Type of locator.
- **`checkbox_element`**: Locator value for the checkbox.

#### `click_element_using_cursor(locator_type: str, locator_value: str)`

Moves the mouse cursor to an element and clicks it.

- **`locator_type`**: Type of locator.
- **`locator_value`**: Locator value for the element.

#### `find_element_in_shadow_root(tag_name: str, css_selector: str, root_element: str = None)`

Finds an element inside a shadow root.

- **`tag_name`**: Tag name of the root element.
- **`css_selector`**: CSS selector of the element inside the shadow root.
- **`root_element`**: Optional root element containing the shadow root.

#### `select_from_dropdown_by_visible_text(locator_type: str, locator_value: str, element_name: str)`

Selects an option from a dropdown by visible text.

- **`locator_type`**: Type of locator.
- **`locator_value`**: Locator value for the dropdown.
- **`element_name`**: Visible text of the option to select.

#### `move_slider_using_cursor(locator_type: str, locator_value: str, xrange: int, yrange: int)`

Moves a slider by a specified range.

- **`locator_type`**: Type of locator.
- **`locator_value`**: Locator value for the slider.
- **`xrange`**: Horizontal range to move.
- **`yrange`**: Vertical range to move.

#### `get_canvas_image(locator_type: str, locator_value: str)`

Fetches and decodes the image from a canvas element.

- **`locator_type`**: Type of locator.
- **`locator_value`**: Locator value for the canvas.

#### `wait_for_element_to_disappear(locator_type: str, locator_value: str)`

Waits until an element disappears.

- **`locator_type`**: Type of locator.
- **`locator_value`**: Locator value for the element.

#### `get_attribute(locator_type: str, locator_value: str, attribute: str)`

Gets the value of an attribute from a web element.

- **`locator_type`**: Type of locator.
- **`locator_value`**: Locator value for the element.
- **`attribute`**: Name of the attribute.

### Error Handling

The `SeleniumApi` class uses a decorator `handle_exception` to handle exceptions in methods. If an exception occurs, a screenshot is taken and saved in the `error_screenshot_directory`.

### Configuration

- **Error Screenshot Directory**: By default, screenshots are saved in `C:\\temp\\ErrorScreenShots`. You can change this directory using `set_error_screenshot_directory(directory)`.

### Example

Here’s a simple example of how to use the `SeleniumApi` class to open a web page and interact with it:

```python
from selenium_api import SeleniumApi

with SeleniumApi() as api:
    api.launch_web_browser("https://example.com")
    api.enter_text("id", "username", "testuser")
    api.enter_text("id", "password", "password123")
    api.click_element("id", "submit")
    print(api.get_text_value("id", "welcome-message"))
```

---

Feel free to customize the README based on any additional specifics or configurations relevant to your project.