import datetime
import uuid
import mss
from mss import tools
import logging
import win32gui
import win32con
import win32process
import psutil
from src.config import SCREEN_DIR

logger = logging.getLogger(__name__)


def find_tradingview_windows():
    """Find all TradingView windows using win32gui"""
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                # Check if it's a browser window
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                try:
                    process = psutil.Process(pid)
                    process_name = process.name().lower()
                    
                    # List of possible TradingView title patterns
                    tradingview_patterns = [
                        'tradingview',
                        'trading view',
                        'xauusd',
                        'xau/usd',
                        'gold',
                        'forex',
                        'chart'
                    ]
                    
                    # Check if it's a browser process and title contains any trading-related keyword
                    if any(browser in process_name for browser in ['chrome', 'firefox', 'edge', 'brave', 'opera']):
                        if any(pattern in title.lower() for pattern in tradingview_patterns):
                            windows.append((hwnd, title))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                
                # Also check for standalone TradingView app
                if 'tradingview' in title.lower() and 'tradingview' in process_name:
                    windows.append((hwnd, title))
    
    windows = []
    win32gui.EnumWindows(callback, windows)
    return windows


def find_bot_ui_window():
    """Find the bot UI window"""
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title == "TradingView Mail-Bot":
                windows.append(hwnd)
    
    windows = []
    win32gui.EnumWindows(callback, windows)
    return windows[0] if windows else None


def minimize_bot_ui():
    """Minimize the bot UI window"""
    ui_hwnd = find_bot_ui_window()
    if ui_hwnd:
        try:
            win32gui.ShowWindow(ui_hwnd, win32con.SW_MINIMIZE)
            logger.info("Bot UI minimized")
            return ui_hwnd
        except Exception as e:
            logger.error(f"Failed to minimize UI: {e}")
    return None


def restore_window(hwnd):
    """Restore a minimized window"""
    if hwnd:
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        except Exception as e:
            logger.error(f"Failed to restore window: {e}")


def bring_window_to_front(hwnd):
    """Bring a window to the front"""
    try:
        # Restore window if minimized
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        
        # Bring to front
        win32gui.SetForegroundWindow(hwnd)
        return True
    except Exception as e:
        logger.error(f"Failed to bring window to front: {e}")
        return False


def grab_tradingview_window() -> str:
    """Capture only the TradingView window screenshot"""
    # First minimize the bot UI
    ui_hwnd = minimize_bot_ui()
    
    # Wait a bit for UI to minimize
    import time
    time.sleep(0.5)
    
    windows = find_tradingview_windows()
    
    if not windows:
        # Restore UI before throwing error
        restore_window(ui_hwnd)
        logger.error("TradingView window not found!")
        raise Exception("TradingView window not found. Make sure it's open.")
    
    # Use the first TradingView window found
    hwnd, title = windows[0]
    logger.info(f"Found TradingView window: {title}")
    
    # Bring window to front
    bring_window_to_front(hwnd)
    
    # Wait a bit for window to come to front
    time.sleep(0.5)
    
    # Get window dimensions
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top
    
    if width == 0 or height == 0:
        # Restore UI before throwing error
        restore_window(ui_hwnd)
        logger.error("TradingView window is minimized or invalid!")
        raise Exception("TradingView window is minimized or invalid.")
    
    # Take screenshot of the specific window area
    fname = SCREEN_DIR / f"{datetime.datetime.now():%Y%m%d_%H%M_%S}_{uuid.uuid4().hex}.png"
    
    with mss.mss() as sct:
        monitor = {
            "top": top,
            "left": left,
            "width": width,
            "height": height
        }
        
        img = sct.grab(monitor)
        tools.to_png(img.rgb, img.size, output=str(fname))
    
    # Restore the UI after screenshot
    restore_window(ui_hwnd)
    
    logger.info(f"Screenshot saved to: {fname}")
    return str(fname)