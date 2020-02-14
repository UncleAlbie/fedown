Name:           fedown
Version:        0.1
Release:        1%{?dist}
Summary:        Print Fedora Pagure user access information

License:        GPL
URL:            https://github.com/UncleAlbie/%{name}
Source0:        https://github.com/UncleAlbie/%{name}/archive/v%{version}/v%{version}.tar.gz

Requires:       python3
BuildArch:      noarch

%description
Small script written in Python that prints Fedora user access information parsed from the Fedora Pagure API. Licensed under GPLv3.

%prep
%autosetup -n %{name}-%{version}


%build


%install
%{__install} -D -m 755 %{name}/%{name}.py %{buildroot}/%{_bindir}/%{name}


%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}


%changelog
* Fri Feb 14 2020 Patrik Novotný <panovotn@redhat.com> - 0.1-1
- Initial release
