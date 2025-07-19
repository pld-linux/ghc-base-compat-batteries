#
# Conditional build:
%bcond_without	prof	# profiling library
#
%define		pkgname	base-compat-batteries
Summary:	base-compat with extra batteries
Summary(pl.UTF-8):	base-compat z dołączonymi bateriami
Name:		ghc-%{pkgname}
Version:	0.11.1
Release:	2
License:	MIT
Group:		Development/Languages
#Source0Download: http://hackage.haskell.org/package/base-compat-batteries
Source0:	http://hackage.haskell.org/package/%{pkgname}-%{version}/%{pkgname}-%{version}.tar.gz
# Source0-md5:	c1975c1d453094193426762a9c59f786
URL:		http://hackage.haskell.org/package/base-compat-batteries
# for ghc < 8.6 has more dependencies
BuildRequires:	ghc >= 8.6
BuildRequires:	ghc-base >= 4.3
BuildRequires:	ghc-base < 5
BuildRequires:	ghc-base-compat = 0.11.1
%if %{with prof}
BuildRequires:	ghc-prof >= 8.6
BuildRequires:	ghc-base-prof >= 4.3
BuildRequires:	ghc-base-compat-prof = 0.11.1
%endif
BuildRequires:	rpmbuild(macros) >= 1.608
%requires_eq	ghc
Requires(post,postun):	/usr/bin/ghc-pkg
Requires:	ghc-base >= 4.3
Requires:	ghc-base-compat = 0.11.1
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# debuginfo is not useful for ghc
%define		_enable_debug_packages	0

# don't compress haddock files
%define		_noautocompressdoc	*.haddock

%description
Provides functions available in later versions of base to a wider
range of compilers, without requiring you to use CPP pragmas in your
code.

This package provides the same API as the base-compat library, but
depends on compatibility packages (such as semigroups) to offer a
wider support window than base-compat, which has no dependencies.
Most of the modules in this library have the same names as in
base-compat to make it easier to switch between the two. There also
exist versions of each module with the suffix .Repl.Batteries, which
are distinct from anything in base-compat, to allow for easier use in
GHCi.

%description -l pl.UTF-8
Ta biblioteka dostarcza funkcje dostępne w nowszych wersjach
biblioteki bazowej dla szerszego zakresu kompilatorów bez konieczności
używania dyrektyw CCP w kodzie.

Ten pakiet udostępnia to samo API, co biblioteka base-compat, ale
zależy od pakietów zgodności (takich jak semigroups), aby zaoferować
szersze okno obsługiwanych wersji niż base-compat, która nie ma
zależności. Większość modułów w tej bibliotece ma te same nazwy, co w
base-compat, aby ułatwić przełączanie między nimi. Istnieją także
wersje każdego modułu z przyrostkiem .Repl.Batteries, które nie
pokrywają się z niczym w base-compat, aby umożliwić łatwiejsze użycie
w GHCi.

%package prof
Summary:	Profiling %{pkgname} library for GHC
Summary(pl.UTF-8):	Biblioteka profilująca %{pkgname} dla GHC
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	ghc-base-prof >= 4.3
Requires:	ghc-base-compat-prof = 0.11.1

%description prof
Profiling %{pkgname} library for GHC.  Should be installed when
GHC's profiling subsystem is needed.

%description prof -l pl.UTF-8
Biblioteka profilująca %{pkgname} dla GHC. Powinna być zainstalowana
kiedy potrzebujemy systemu profilującego z GHC.

%prep
%setup -q -n %{pkgname}-%{version}

%build
runhaskell Setup.lhs configure -v2 \
	%{?with_prof:--enable-library-profiling} \
	--prefix=%{_prefix} \
	--libdir=%{_libdir} \
	--libexecdir=%{_libexecdir} \
	--docdir=%{_docdir}/%{name}-%{version}

runhaskell Setup.lhs build

runhaskell Setup.lhs haddock --executables

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_libdir}/%{ghcdir}/package.conf.d

runhaskell Setup.lhs copy --destdir=$RPM_BUILD_ROOT

# work around automatic haddock docs installation
%{__rm} -rf %{name}-%{version}-doc
cp -a $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version} %{name}-%{version}-doc
%{__rm} -r $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}

find $RPM_BUILD_ROOT%{_libdir}/%{ghcdir}/%{pkgname}-%{version} -type d | %{__sed} "s|$RPM_BUILD_ROOT|%dir |" > %{name}.files
find $RPM_BUILD_ROOT%{_libdir}/%{ghcdir}/%{pkgname}-%{version} -name '*.hi' | %{__sed} "s|$RPM_BUILD_ROOT||" >> %{name}.files
find $RPM_BUILD_ROOT%{_libdir}/%{ghcdir}/%{pkgname}-%{version} -name '*.dyn_hi' | %{__sed} "s|$RPM_BUILD_ROOT||" >> %{name}.files
find $RPM_BUILD_ROOT%{_libdir}/%{ghcdir}/%{pkgname}-%{version} -name '*.p_hi' | %{__sed} "s|$RPM_BUILD_ROOT||" >> %{name}-prof.files

runhaskell Setup.lhs register \
	--gen-pkg-config=$RPM_BUILD_ROOT%{_libdir}/%{ghcdir}/package.conf.d/%{pkgname}.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
%ghc_pkg_recache

%postun
%ghc_pkg_recache

%files -f %{name}.files
%defattr(644,root,root,755)
%doc CHANGES.markdown README.markdown %{name}-%{version}-doc/*
%{_libdir}/%{ghcdir}/package.conf.d/%{pkgname}.conf
%attr(755,root,root) %{_libdir}/%{ghcdir}/%{pkgname}-%{version}/*.so
%{_libdir}/%{ghcdir}/%{pkgname}-%{version}/*.a
%exclude %{_libdir}/%{ghcdir}/%{pkgname}-%{version}/*_p.a

%if %{with prof}
%files prof -f %{name}-prof.files
%defattr(644,root,root,755)
%{_libdir}/%{ghcdir}/%{pkgname}-%{version}/*_p.a
%endif
