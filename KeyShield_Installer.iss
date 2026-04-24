[Setup]
AppName=KeyShield
AppVersion=1.0
DefaultDirName={pf}\KeyShield
DefaultGroupName=KeyShield
OutputDir=installer
OutputBaseFilename=KeyShield_Installer
Compression=lzma
SolidCompression=yes

[Files]
; C++ executable (if built)
Source: "build\KeyShield.exe"; DestDir: "{app}"; Flags: ignoreversion; Check: FileExists(ExpandConstant('{src}\build\KeyShield.exe'))
Source: "build\Release\KeyShield.exe"; DestDir: "{app}"; DestName: "KeyShield.exe"; Flags: ignoreversion; Check: FileExists(ExpandConstant('{src}\build\Release\KeyShield.exe'))

; Python executables
Source: "dist\Dashboard.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\keylogger.exe"; DestDir: "{app}"; Flags: ignoreversion

; Launcher script
Source: "KeyShield_Launcher.bat"; DestDir: "{app}"; Flags: ignoreversion

; Documentation
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\KeyShield"; Filename: "{app}\KeyShield_Launcher.bat"; IconFilename: "{app}\KeyShield.exe"
Name: "{group}\KeyShield Dashboard"; Filename: "{app}\Dashboard.exe"
Name: "{group}\KeyShield Keylogger"; Filename: "{app}\keylogger.exe"
Name: "{group}\Uninstall KeyShield"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\KeyShield_Launcher.bat"; Description: "Launch KeyShield Application"; Flags: postinstall nowait

[Code]
function FileExists(const FileName: string): Boolean;
begin
  Result := FileExists(FileName);
end;