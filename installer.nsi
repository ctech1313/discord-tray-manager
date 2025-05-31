; Discord Tray Manager Installer
; NSIS Script for creating Windows installer

!define APPNAME "Discord Tray Manager"
!define COMPANYNAME "Discord Tray Manager"
!define DESCRIPTION "Keeps Discord icon visible in system tray"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0

!define HELPURL "https://github.com/your-repo/discord-tray-manager"
!define UPDATEURL "https://github.com/your-repo/discord-tray-manager"
!define ABOUTURL "https://github.com/your-repo/discord-tray-manager"

!define INSTALLSIZE 5000 ; Size in KB

RequestExecutionLevel admin

InstallDir "$PROGRAMFILES\${APPNAME}"

# rtf or txt file - remember if it is txt, it must be in the DOS text format (\r\n)
LicenseData "license.txt"
Name "${APPNAME}"
Icon "tray_icon.ico"
outFile "Discord_Tray_Manager_Setup.exe"

!include LogicLib.nsh

# Just three pages - license agreement, install location, and installation
page license
page directory
Page instfiles

!macro VerifyUserIsAdmin
UserInfo::GetAccountType
pop $0
${If} $0 != "admin" ;Require admin rights on NT4+
    messageBox mb_iconstop "Administrator rights required!"
    setErrorLevel 740 ;ERROR_ELEVATION_REQUIRED
    quit
${EndIf}
!macroend

function .onInit
	setShellVarContext all
	!insertmacro VerifyUserIsAdmin
	
	# Check for existing installation in multiple locations
	ReadRegStr $0 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString"
	${If} $0 == ""
		# Also check 32-bit registry on 64-bit systems
		ReadRegStr $0 HKLM "Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString"
	${EndIf}
	
	# Check if executable exists in Program Files
	${If} $0 == ""
		IfFileExists "$PROGRAMFILES\${APPNAME}\DiscordTrayManager.exe" 0 check_x86
		StrCpy $0 "$PROGRAMFILES\${APPNAME}\uninstall.exe"
		Goto found_existing
		
		check_x86:
		IfFileExists "$PROGRAMFILES32\${APPNAME}\DiscordTrayManager.exe" 0 no_existing
		StrCpy $0 "$PROGRAMFILES32\${APPNAME}\uninstall.exe"
		
		found_existing:
	${EndIf}
	
	${If} $0 != ""
		MessageBox MB_YESNO|MB_ICONQUESTION "An existing version of ${APPNAME} was found. The old version must be removed first. Continue?" IDYES uninstall_existing IDNO abort_install
		
		uninstall_existing:
		# Stop the running application first (multiple methods)
		nsExec::Exec "taskkill /f /im DiscordTrayManager.exe"
		nsExec::Exec "wmic process where name='DiscordTrayManager.exe' delete"
		Sleep 3000
		
		# Run the uninstaller
		ClearErrors
		${If} ${FileExists} "$0"
			DetailPrint "Running uninstaller: $0"
			ExecWait '"$0" /S' $1
			DetailPrint "Uninstaller exit code: $1"
		${Else}
			# Manual cleanup if uninstaller doesn't exist
			DetailPrint "Uninstaller not found, performing manual cleanup"
			RMDir /r "$PROGRAMFILES\${APPNAME}"
			RMDir /r "$PROGRAMFILES32\${APPNAME}"
			DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
			DeleteRegKey HKLM "Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
			DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "${APPNAME}"
		${EndIf}
		
		# Wait for cleanup to complete
		Sleep 3000
		
		# Verify cleanup
		${If} ${FileExists} "$INSTDIR\DiscordTrayManager.exe"
			MessageBox MB_OK "Some files from the previous installation could not be removed. They will be overwritten."
		${EndIf}
		Goto continue_install
		
		abort_install:
		Abort "Installation cancelled by user."
		
		continue_install:
	${EndIf}
	
	no_existing:
functionEnd

section "install"
	# Files for the install directory - to build the installer, these should be in the same directory as the install script (this file)
	setOutPath $INSTDIR
	
	# Files to install
	file "DiscordTrayManager.exe"
	file "config.json"
	file "README.md"
	
	# Uninstaller
	writeUninstaller "$INSTDIR\uninstall.exe"

	# Start Menu
	createDirectory "$SMPROGRAMS\${APPNAME}"
	createShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\DiscordTrayManager.exe" "" "$INSTDIR\DiscordTrayManager.exe"
	createShortCut "$SMPROGRAMS\${APPNAME}\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe"

	# Registry information for add/remove programs
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME} - ${DESCRIPTION}"
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "InstallLocation" "$\"$INSTDIR$\""
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$\"$INSTDIR\DiscordTrayManager.exe$\""
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${COMPANYNAME}"
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "HelpLink" "${HELPURL}"
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
	WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
	WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMinor" ${VERSIONMINOR}
	WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoModify" 1
	WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoRepair" 1
	WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "EstimatedSize" ${INSTALLSIZE}

	# Auto-start with Windows (run at startup)
	WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "${APPNAME}" "$INSTDIR\DiscordTrayManager.exe"

	# Start the application immediately after installation
	Exec "$INSTDIR\DiscordTrayManager.exe"

	# Success message
	MessageBox MB_OK "Discord Tray Manager has been installed successfully!$\r$\n$\r$\nThe application has been started and will start automatically with Windows.$\r$\nLook for the Discord Tray Manager icon in your system tray."
sectionEnd

# Uninstaller
function un.onInit
	SetShellVarContext all
	
	#Verify the uninstaller - last chance to back out
	MessageBox MB_OKCANCEL "Permanently remove ${APPNAME}?" IDOK next
		Abort
	next:
	!insertmacro VerifyUserIsAdmin
functionEnd

section "uninstall"
	# Stop the application if running (more aggressive)
	nsExec::Exec "taskkill /f /im DiscordTrayManager.exe"
	nsExec::Exec "wmic process where name='DiscordTrayManager.exe' delete"
	
	# Wait for processes to fully terminate
	Sleep 3000

	# Remove Start Menu launcher
	delete "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk"
	delete "$SMPROGRAMS\${APPNAME}\Uninstall.lnk"
	rmDir "$SMPROGRAMS\${APPNAME}"

	# Remove files (with retry for locked files)
	SetOverwrite on
	
	# Try to delete main executable
	ClearErrors
	delete "$INSTDIR\DiscordTrayManager.exe"
	IfErrors retry_exe
	Goto continue_uninstall
	
	retry_exe:
	Sleep 2000
	ClearErrors
	delete "$INSTDIR\DiscordTrayManager.exe"
	IfErrors exe_locked
	Goto continue_uninstall
	
	exe_locked:
	# If still locked, try to rename it for deletion on reboot
	Rename "$INSTDIR\DiscordTrayManager.exe" "$INSTDIR\DiscordTrayManager.exe.old"
	Delete /REBOOTOK "$INSTDIR\DiscordTrayManager.exe.old"
	
	continue_uninstall:
	# Remove other files
	delete "$INSTDIR\config.json"
	delete "$INSTDIR\README.md"
	delete "$INSTDIR\uninstall.exe"
	
	# Remove log files from AppData (optional - let user decide)
	MessageBox MB_YESNO|MB_ICONQUESTION "Do you want to remove log files and user data?" IDNO skip_userdata
	RMDir /r "$LOCALAPPDATA\Discord Tray Manager"
	skip_userdata:
	
	# Try to remove directory (might fail if files are locked)
	RMDir "$INSTDIR"
	
	# If directory still exists, schedule for deletion on reboot
	IfFileExists "$INSTDIR" 0 dir_removed
	RMDir /REBOOTOK "$INSTDIR"
	MessageBox MB_OK "Some files could not be removed and will be deleted on next reboot."
	Goto cleanup_registry
	
	dir_removed:
	MessageBox MB_OK "Discord Tray Manager has been successfully uninstalled."
	
	cleanup_registry:
	# Remove uninstaller information from the registry
	DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
	
	# Remove auto-start entry
	DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "${APPNAME}"
sectionEnd 