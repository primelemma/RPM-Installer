Name:           rpm-installer
Version:        0.4
Release:        1%{?dist}
Summary:        GUI to install local RPMs and manage packages
License:        MIT
URL:            https://github.com/yourusername/rpm-installer
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch

Requires:       python3
Requires:       python3-pyqt6
Requires:       polkit
Requires:       dnf
Requires:       rpm

%description
A lightweight Qt6-based tool to install local RPM packages on Fedora.
Version 0.4 includes a search feature to find, manage, and uninstall
existing system packages using a fuzzy search logic.

%prep
%setup -q

%install
mkdir -p %{buildroot}/%{_bindir}
mkdir -p %{buildroot}/%{_datadir}/applications
install -m 755 rpm-installer.py %{buildroot}/%{_bindir}/rpm-installer
install -m 644 rpm-installer.desktop %{buildroot}/%{_datadir}/applications/rpm-installer.desktop

%files
%{_bindir}/rpm-installer
%{_datadir}/applications/rpm-installer.desktop

%changelog
* Sat Nov 29 2025 Developer <dev@example.com> - 0.4-1
- Added Search bar for installed packages
- Added Fuzzy search (partial matching)
- Added Uninstall functionality

* Sat Nov 29 2025 Developer <dev@example.com> - 0.1-1
- Initial release
