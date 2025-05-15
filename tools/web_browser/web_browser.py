from playwright.sync_api import sync_playwright
import time
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from twocaptcha import TwoCaptcha
import pyautogui  # Thêm thư viện pyautogui


# (1) Khởi tạo dịch vụ 2captcha (thay YOUR_2CAPTCHA_API_KEY bằng key thật)
solver = TwoCaptcha("03bb89b8e93e115402f16c422a9c846d")

# (2) Hàm giải reCAPTCHA v2 (dùng cho trang có iframe reCAPTCHA)
def solve_recaptcha(page, site_key, url):
    # (a) Lấy token (g-recaptcha-response) từ dịch vụ 2captcha
    try:
        result = solver.recaptcha(sitekey=site_key, url=url)
        token = result["code"]
        print("Token reCAPTCHA nhận được:", token)
    except Exception as e:
        print("Lỗi khi gọi 2captcha:", e)
        return False

    # (b) Nhập token vào trang (giả sử trang có một input ẩn hoặc gọi hàm callback)
    # Ví dụ: Nếu trang có một input ẩn (id="g-recaptcha-response") thì gán giá trị token vào đó.
    # (Lưu ý: Trang thực tế có thể khác, bạn cần kiểm tra DOM hoặc tài liệu của trang.)
    try:
        page.evaluate("""(token) => {
            document.getElementById("g-recaptcha-response").innerHTML = token;
            // (Nếu trang có hàm callback, ví dụ: __grecaptcha_callback, thì gọi nó)
            if (typeof __grecaptcha_callback === "function") __grecaptcha_callback(token);
        }""", token)
        print("Đã nhập token reCAPTCHA vào trang.")
        return True
    except Exception as e:
        print("Lỗi khi nhập token reCAPTCHA:", e)
        return False

class WebBrowser:
    """A class to handle web browser automation using Playwright."""
    
    def __init__(self, headless: bool = True):
        """
        Initialize the WebBrowser.
        
        Args:
            headless (bool): Whether to run the browser in headless mode (no GUI)
        """
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
        # Setup logging
        logging.basicConfig(
            filename='web_browser.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def __enter__(self):
        """Start the browser when entering the context."""
        self.playwright = sync_playwright().start()
        # Launch Chromium browser with additional settings
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,  # Set to True to run without GUI
            slow_mo=100,  # Slow down operations by 100ms to see movements better
            args=[
                '--start-maximized',  # Start browser maximized
                '--disable-blink-features=AutomationControlled',  # Disable automation flag
                '--disable-features=IsolateOrigins,site-per-process'  # Disable site isolation
            ]
        )
        # Create a new browser context with larger viewport
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},  # Larger viewport
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        # Create a new page
        self.page = self.context.new_page()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources when exiting the context."""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def search_google(self, query: str, is_visible: bool = True) -> None:
        """
        Search Google and wait for user input before closing.
        
        Args:
            query (str): The search query to enter in Google
            is_visible (bool): If True, browser will be visible (non-headless). If False, browser will run in headless mode.
        """
        try:
            # Set headless mode based on is_visible parameter
            self.headless = not is_visible
            self.logger.info(f"Starting Google search for query: {query} in {'visible' if is_visible else 'headless'} mode")
            
            # Restart browser with new headless setting
            if self.browser:
                self.browser.close()
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                slow_mo=50
            )
            self.context = self.browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            self.page = self.context.new_page()
            
            # Navigate to Google
            self.navigate('https://www.google.com')
            self.logger.info("Navigated to Google")
            
            # Wait for search box and enter query
            self.wait_for_selector('textarea[name="q"]')
            self.type_text('textarea[name="q"]', query)
            self.logger.info(f"Entered search query: {query}")
            
            # Press Enter to search
            self.page.press('textarea[name="q"]', 'Enter')
            self.logger.info("Submitted search")
            
            # Handle CAPTCHA if it appears
            try:
                # Wait for CAPTCHA iframe with timeout
                captcha_frame = self.page.wait_for_selector("iframe[src*='recaptcha']", timeout=3000)
                if captcha_frame:
                    self.logger.info("CAPTCHA detected, attempting to solve...")
                    # Switch to CAPTCHA iframe
                    captcha_frame_content = captcha_frame.content_frame()
                    # Click the checkbox
                    captcha_checkbox = captcha_frame_content.wait_for_selector("#recaptcha-anchor")
                    captcha_checkbox.click()
                    self.logger.info("Clicked CAPTCHA checkbox")
                    # Wait a bit for CAPTCHA to process
                    self.page.wait_for_timeout(2000)
                    input("Press Enter when you finished solving CAPTCHA...")
            except Exception as e:
                self.logger.info("No CAPTCHA detected or error handling CAPTCHA: " + str(e))
            
            # Wait for search results with updated selector
            try:
                # Wait for either the main search results or the "no results" message
                self.page.wait_for_selector('div#search, div#result-stats, div#topstuff', timeout=5000)
                self.logger.info("Search results page loaded")
                
                # Click the first search result
                try:
                    # Try different selectors for search results
                    selectors = [
                        'div.g a[href^="http"]',  # Standard search result
                        'div[data-hveid] a[href^="http"]',  # Alternative result format
                        'a[href^="http"]:not([href*="google"])'  # Any non-Google link
                    ]
                    
                    first_result = None
                    for selector in selectors:
                        first_result = self.page.query_selector(selector)
                        if first_result:
                            break
                    
                    if first_result:
                        result_url = first_result.get_attribute('href')
                        self.logger.info(f"Clicking first result: {result_url}")
                        first_result.click()
                        # Wait for the new page to load
                        self.page.wait_for_load_state('networkidle')
                        self.logger.info("Navigated to first result page")
                    else:
                        self.logger.warning("No clickable search results found")
                except Exception as e:
                    self.logger.error(f"Error clicking first result: {str(e)}")
                    
            except Exception as e:
                self.logger.error(f"Error waiting for search results: {str(e)}")
                # Take screenshot of the current state for debugging
                self.take_screenshot('error_state.png')
                raise
            
            # Take screenshot of results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f'google_search_{timestamp}.png'
            self.take_screenshot(screenshot_path)
            self.logger.info(f"Saved screenshot to {screenshot_path}")
            
            

            # Only wait for user input if browser is visible
            if is_visible:
                input("Press Enter to close the browser...")
                self.logger.info("User closed the browser")

            
        except Exception as e:
            self.logger.error(f"Error during Google search: {str(e)}")
            raise

    def navigate(self, url: str) -> None:
        """
        Navigate to a URL.
        
        Args:
            url (str): The URL to navigate to
        """
        self.page.goto(url)
        # Wait for the page to be fully loaded
        self.page.wait_for_load_state('networkidle')
    
    def get_title(self) -> str:
        """Get the current page title."""
        return self.page.title()
    
    def get_content(self) -> str:
        """Get the current page content."""
        return self.page.content()
    
    def take_screenshot(self, path: str) -> None:
        """
        Take a screenshot of the current page.
        
        Args:
            path (str): Path where to save the screenshot
        """
        self.page.screenshot(path=path)
    
    def click(self, selector: str) -> None:
        """
        Click an element on the page.
        
        Args:
            selector (str): CSS selector of the element to click
        """
        self.page.click(selector)
    
    def type_text(self, selector: str, text: str) -> None:
        """
        Type text into an input field.
        
        Args:
            selector (str): CSS selector of the input field
            text (str): Text to type
        """
        self.page.fill(selector, text)
    
    def wait_for_selector(self, selector: str, timeout: int = 5000) -> None:
        """
        Wait for an element to appear on the page.
        
        Args:
            selector (str): CSS selector to wait for
            timeout (int): Maximum time to wait in milliseconds
        """
        self.page.wait_for_selector(selector, timeout=timeout)
    
    def get_text(self, selector: str) -> str:
        """
        Get text content of an element.
        
        Args:
            selector (str): CSS selector of the element
            
        Returns:
            str: Text content of the element
        """
        return self.page.text_content(selector)
    
    def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """
        Get an attribute value of an element.
        
        Args:
            selector (str): CSS selector of the element
            attribute (str): Name of the attribute
            
        Returns:
            Optional[str]: Value of the attribute or None if not found
        """
        element = self.page.query_selector(selector)
        if element:
            return element.get_attribute(attribute)
        return None

    def move_mouse(self, x: int, y: int) -> None:
        """
        Move mouse to specific coordinates on the screen using pyautogui.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
        """
        # Lấy vị trí cửa sổ trình duyệt
        browser_window = self.page.evaluate("""() => {
            return {
                x: window.screenX,
                y: window.screenY,
                width: window.outerWidth,
                height: window.outerHeight
            }
        }""")
        
        # Tính toán vị trí thực tế trên màn hình
        screen_x = browser_window['x'] + x
        screen_y = browser_window['y'] + y
        
        # Di chuyển chuột thật
        pyautogui.moveTo(screen_x, screen_y, duration=1)  # duration=1 để di chuyển trong 1 giây
        self.logger.info(f"Moved mouse to coordinates ({screen_x}, {screen_y})")
    
    def click_at_position(self, x: int, y: int) -> None:
        """
        Click at specific coordinates using pyautogui.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
        """
        # Lấy vị trí cửa sổ trình duyệt
        browser_window = self.page.evaluate("""() => {
            return {
                x: window.screenX,
                y: window.screenY,
                width: window.outerWidth,
                height: window.outerHeight
            }
        }""")
        
        # Tính toán vị trí thực tế trên màn hình
        screen_x = browser_window['x'] + x
        screen_y = browser_window['y'] + y
        
        # Click chuột thật
        pyautogui.click(screen_x, screen_y)
        self.logger.info(f"Clicked at coordinates ({screen_x}, {screen_y})")
    
    def drag_and_drop(self, start_x: int, start_y: int, end_x: int, end_y: int) -> None:
        """
        Perform drag and drop operation from one position to another.
        
        Args:
            start_x (int): Starting X coordinate
            start_y (int): Starting Y coordinate
            end_x (int): Ending X coordinate
            end_y (int): Ending Y coordinate
        """
        self.page.mouse.move(start_x, start_y)
        self.page.mouse.down()
        self.page.mouse.move(end_x, end_y)
        self.page.mouse.up()
        self.logger.info(f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})")
    
    def scroll_to_position(self, x: int, y: int) -> None:
        """
        Scroll the page to specific coordinates.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
        """
        self.page.mouse.wheel(x, y)
        self.logger.info(f"Scrolled to coordinates ({x}, {y})")
    
    def get_mouse_position(self) -> tuple:
        """
        Get current mouse position.
        
        Returns:
            tuple: (x, y) coordinates of current mouse position
        """
        # Note: This is a workaround as Playwright doesn't directly provide mouse position
        # You might need to use JavaScript to get the actual position
        position = self.page.evaluate("""() => {
            return {
                x: window.mouseX || 0,
                y: window.mouseY || 0
            }
        }""")
        return (position['x'], position['y'])

def example_usage():
    """Example of how to use the WebBrowser class."""
    # Example 1: Basic navigation and screenshot
    with WebBrowser(headless=False) as browser:
        # Navigate to a website
        browser.navigate('https://www.google.com')
        
        # Get the page title
        print(f"Page title: {browser.get_title()}")
        
        # Take a screenshot
        browser.take_screenshot('google_homepage.png')
        
        # Wait for search box to be visible and type into it
        browser.wait_for_selector('textarea[name="q"]')
        browser.type_text('textarea[name="q"]', 'Playwright Python')
        
        # Press Enter to search
        browser.page.press('textarea[name="q"]', 'Enter')
        
        try:
            # obtain the iFrame containing the CAPTCHA box
            captcha_frame = browser.page.wait_for_selector("iframe[src*='recaptcha']")
            if captcha_frame:
                # switch to the content of the CAPTCHA iframe
                captcha_frame_content = captcha_frame.content_frame()

                # extract site key for the CAPTCHA
                site_key = captcha_frame.get_attribute("src").split("k=")[-1].split("&")[0]

                # get the CAPTCHA checkbox element
                captcha_checkbox = captcha_frame_content.wait_for_selector("#recaptcha-anchor")

                # click the CAPTCHA checkbox
                captcha_checkbox.click()
                print("Đã click CAPTCHA checkbox")
        except Exception as e:
            print("Không phát hiện reCAPTCHA (hoặc lỗi khác):", e)

        

        # recaptcha_iframe = browser.page.query_selector("iframe[src*='recaptcha']")
        # if recaptcha_iframe:
        #     print("Phát hiện reCAPTCHA, đang giải...")
        #     # (b) Lấy site key (thường nằm trong thuộc tính data-sitekey của iframe hoặc trong src)
        #     # (Lưu ý: Trang thực tế có thể khác, bạn cần kiểm tra DOM hoặc tài liệu của trang.)
        #     site_key = recaptcha_iframe.get_attribute("data-sitekey") or "6Lc... (site key thật của trang)"
        #     if site_key:
        #         # (c) Gọi hàm giải CAPTCHA (giả sử trang có một input ẩn hoặc callback)
        #         if solve_recaptcha(browser.page, site_key, "https://www.google.com"):
        #             print("Đã giải CAPTCHA thành công, tiếp tục thao tác...")
        #         else:
        #             print("Không thể giải CAPTCHA, bạn có thể cần giải thủ công.")
        #             input("Giải xong CAPTCHA, nhấn Enter để tiếp tục...")
        #     else:
        #         print("Không tìm thấy site key của reCAPTCHA.")
        # else:
        #     print("Không phát hiện reCAPTCHA, tiếp tục thao tác...")


        input("Nếu có CAPTCHA, hãy giải xong rồi nhấn Enter để tiếp tục...")
        # Sau đó script sẽ tiếp tục các thao tác còn lại

        # Wait for results
        browser.wait_for_selector('#search')
        
        # Take another screenshot
        browser.take_screenshot('search_results.png')
        
        # Get search results
        # results = browser.get_text('#search')
        # print(f"Search results: {results[:200]}...")  # Print first 200 chars
        first_link = browser.page.query_selector_all("#b_results a")
        if first_link:
            # (a) Lấy href (URL) của link đầu tiên (nếu bạn chỉ muốn lấy URL)
            href = first_link.get_attribute("href")
            print("URL của trang đầu tiên:", href)
            # (b) Click vào link đầu tiên để truy cập trang đó
            first_link.click()
            # (c) Đợi trang đầu tiên tải xong (giả sử trang đó có một phần tử đặc trưng, ví dụ: <body>)
            browser.page.wait_for_load_state("networkidle")
            print("Đã truy cập trang đầu tiên, tiêu đề:", browser.get_title())
            # (d) (Tùy chọn) Chụp ảnh màn hình trang đầu tiên
            browser.take_screenshot("first_page.png")
        else:
            print("Không tìm thấy link đầu tiên trong kết quả tìm kiếm.")
    
    # Example 2: Form filling
    with WebBrowser(headless=False) as browser:
        browser.navigate('https://www.facebook.com/login.php/')
        
        # Fill in login form
        browser.type_text('#email', 'phanminhtai23@gmail.com')
        browser.type_text('#pass', 'Phanminhtai32@')
        
        # Click login button
        browser.click('button[type="submit"]')
        
        try:
            # obtain the iFrame containing the CAPTCHA box
            captcha_frame = browser.page.wait_for_selector("iframe[src*='recaptcha']")
            if captcha_frame:
                # switch to the content of the CAPTCHA iframe
                captcha_frame_content = captcha_frame.content_frame()

                # extract site key for the CAPTCHA
                site_key = captcha_frame.get_attribute("src").split("k=")[-1].split("&")[0]

                # get the CAPTCHA checkbox element
                captcha_checkbox = captcha_frame_content.wait_for_selector("#recaptcha-anchor")

                # click the CAPTCHA checkbox
                captcha_checkbox.click()
                print("Đã click CAPTCHA checkbox")
        except Exception as e:
            print("Không phát hiện reCAPTCHA (hoặc lỗi khác):", e)

        # Wait for login to complete
        browser.wait_for_selector('.dashboard')
        
        # Take screenshot of dashboard
        browser.take_screenshot('dashboard.png')

def example_mouse_control():
    """Example of how to use mouse control features."""
    with WebBrowser(headless=False) as browser:
        # Navigate to a page
        browser.navigate('https://www.google.com')
        
        # Move mouse to search box (approximate coordinates)
        browser.move_mouse(500, 300)
        
        # Click at that position
        browser.click_at_position(500, 300)
        
        # Type some text
        browser.type_text('textarea[name="q"]', 'test mouse control')
        
        # Drag and drop example (if there's a draggable element)
        browser.drag_and_drop(100, 100, 200, 200)
        
        # Scroll down
        browser.scroll_to_position(0, 500)
        
        # Get current mouse position
        x, y = browser.get_mouse_position()
        print(f"Current mouse position: ({x}, {y})")

if __name__ == "__main__":
    # Cài đặt pyautogui
    pyautogui.FAILSAFE = True  # Dừng chương trình nếu di chuyển chuột đến góc màn hình
    pyautogui.PAUSE = 0.5  # Thêm delay 0.5 giây giữa các thao tác
    
    # Test mouse control with real mouse movement
    with WebBrowser(headless=False) as browser:
        browser.navigate('https://www.google.com')
        time.sleep(2)  # Đợi trang load
        
        # Di chuyển chuột với pyautogui
        browser.move_mouse(500, 300)  # Di chuyển đến ô tìm kiếm
        time.sleep(1)
        browser.click_at_position(500, 300)  # Click vào ô tìm kiếm
        time.sleep(1)
        
        # Di chuyển đến các vị trí khác
        browser.move_mouse(1200, 800)
        time.sleep(1)
        browser.move_mouse(200, 500)
        time.sleep(1)
        
        # Click vào vị trí cuối
        browser.click_at_position(200, 500)
        time.sleep(2)
    