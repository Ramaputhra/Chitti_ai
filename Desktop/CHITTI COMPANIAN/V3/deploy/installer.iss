[Setup]
AppName=CHITTI V2
AppVersion=2.0
DefaultDirName={autopf}\CHITTI V2
DefaultGroupName=CHITTI V2
OutputDir=.\Output
OutputBaseFilename=chitti_v2_setup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64

[Files]
Source: "dist\chitti.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\CHITTI V2"; Filename: "{app}\chitti.exe"
Name: "{commondesktop}\CHITTI V2"; Filename: "{app}\chitti.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"
