import platform
import os
import ctypes
import plistlib


def get_file_version(file_path):
    """
    Get the version of a file or application, supporting both Windows and macOS.
    """
    system = platform.system()

    if system == "Windows":
        return get_version_windows(file_path)
    elif system == "Darwin":
        return get_version_macos(file_path)
    else:
        return "Unsupported operating system."


def get_version_windows(file_path):
    """
    Get the version of a file on Windows using ctypes.
    """

    class VS_FIXEDFILEINFO(ctypes.Structure):
        _fields_ = [
            ("dwSignature", ctypes.c_uint),
            ("dwStrucVersion", ctypes.c_uint),
            ("dwFileVersionMS", ctypes.c_uint),
            ("dwFileVersionLS", ctypes.c_uint),
            ("dwProductVersionMS", ctypes.c_uint),
            ("dwProductVersionLS", ctypes.c_uint),
            ("dwFileFlagsMask", ctypes.c_uint),
            ("dwFileFlags", ctypes.c_uint),
            ("dwFileOS", ctypes.c_uint),
            ("dwFileType", ctypes.c_uint),
            ("dwFileSubtype", ctypes.c_uint),
            ("dwFileDateMS", ctypes.c_uint),
            ("dwFileDateLS", ctypes.c_uint)
        ]

    try:
        kernel32 = ctypes.WinDLL('kernel32')

        # Get the size of the version information
        version_info_size = kernel32.GetFileVersionInfoSizeW(file_path, None)
        if version_info_size == 0:
            return "Error: Unable to get version info size."

        # Allocate buffer and get the version information
        version_info = ctypes.create_string_buffer(version_info_size)
        if not kernel32.GetFileVersionInfoW(file_path, 0, version_info_size, version_info):
            return "Error: Unable to get version info."

        # Query the version information
        lp_version_info = ctypes.c_void_p()
        ffi_size = ctypes.c_uint()
        if not kernel32.VerQueryValueW(version_info, r'\\', ctypes.byref(lp_version_info), ctypes.byref(ffi_size)):
            return "Error: Unable to query version info."

        ffi = ctypes.cast(lp_version_info, ctypes.POINTER(VS_FIXEDFILEINFO)).contents
        version = f"{(ffi.dwFileVersionMS >> 16) & 0xffff}.{(ffi.dwFileVersionMS) & 0xffff}." \
                  f"{(ffi.dwFileVersionLS >> 16) & 0xffff}.{(ffi.dwFileVersionLS) & 0xffff}"
        return version
    except Exception as e:
        return f"Error: {e}"


def get_version_macos(file_path):
    """
    Get the version of a macOS application by reading its Info.plist file.
    """
    try:
        plist_path = os.path.join(file_path, "Contents", "Info.plist")
        with open(plist_path, 'rb') as fp:
            plist = plistlib.load(fp)
            return plist.get('CFBundleShortVersionString', 'Unknown version')
    except FileNotFoundError:
        return "Error: Info.plist file not found."
    except plistlib.InvalidFileException:
        return "Error: Invalid Info.plist file."
    except Exception as e:
        return f"Error: {e}"




if __name__ == "__main__":
    # file_path = input("Enter the path to the file or application: ")
    version = get_file_version("/Applications/Google Chrome.app")
    print(f"Version: {version}")
