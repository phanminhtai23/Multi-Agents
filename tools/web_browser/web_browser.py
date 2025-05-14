from playwright.sync_api import sync_playwright
import time
from typing import Optional, Dict, Any
from twocaptcha import TwoCaptcha


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
    # Ví dụ: Nếu trang có một input ẩn (id=”g-recaptcha-response”) thì gán giá trị token vào đó.
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
    
    def __init__(self, headless: bool = False):
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
    
    def __enter__(self):
        """Start the browser when entering the context."""
        self.playwright = sync_playwright().start()
        # Launch Chromium browser
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,  # Set to True to run without GUI
            slow_mo=50  # Slow down operations by 50ms
        )
        # Create a new browser context
        self.context = self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
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

if __name__ == "__main__":
    # Run the example
    example_usage() 