%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import *; import sys; sys.stdout.write(get_python_lib(1))")}
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import *; import sys; sys.stdout.write(get_python_lib())")}

Name: sssd
Version: 1.0.5
Release: 2%{?dist}
Group: Applications/System
Summary: System Security Services Daemon
# The entire source code is GPLv3+ except replace/ which is LGPLv3+
License: GPLv3+
URL: http://fedorahosted.org/sssd
Source: https://fedorahosted.org/released/sssd/sssd-%{version}.tar.gz
BuildRoot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

### Patches ###

### Dependencies ###

Requires: libldb >= 0.9.3
Requires: libtdb >= 1.1.3
Requires: libtevent >= 0.9.8-7
Requires: sssd-client = %{version}-%{release}
Requires: cyrus-sasl-gssapi
Requires(post): python
Requires(preun):  initscripts chkconfig
Requires(postun): /sbin/service

%define servicename sssd
%define sssdstatedir %{_localstatedir}/lib/sss
%define dbpath %{sssdstatedir}/db
%define pipepath %{sssdstatedir}/pipes
%define pubconfpath %{sssdstatedir}/pubconf

### Build Dependencies ###

BuildRequires: autoconf
BuildRequires: automake
BuildRequires: libtool
BuildRequires: m4
%{?fedora:BuildRequires: popt-devel}
%if 0%{?rhel} <= 5
BuildRequires: popt
%endif
%if 0%{?rhel} >= 6
BuildRequires: popt-devel
%endif
BuildRequires: libtalloc-devel
BuildRequires: libtevent-devel >= 0.9.8-7
BuildRequires: libtdb-devel
BuildRequires: libldb-devel
BuildRequires: dbus-devel
BuildRequires: dbus-libs
BuildRequires: openldap-devel
BuildRequires: pam-devel
BuildRequires: nss-devel
BuildRequires: nspr-devel
BuildRequires: pcre-devel
BuildRequires: libxslt
BuildRequires: libxml2
BuildRequires: docbook-style-xsl
BuildRequires: krb5-devel
BuildRequires: c-ares-devel
BuildRequires: python-devel

%description
Provides a set of daemons to manage access to remote directories and
authentication mechanisms. It provides an NSS and PAM interface toward
the system and a pluggable backend system to connect to multiple different
account sources. It is also the basis to provide client auditing and policy
services for projects like FreeIPA.

%package client
Summary: SSSD Client libraries for NSS and PAM
Group: Applications/System
License: LGPLv3+

%description client
Provides the libraries needed by the PAM and NSS stacks to connect to the SSSD
service.

%prep
%setup -q

%build
NSS_LIBS=-lnss3 \
KRB5_LIBS=-lkrb5 \
%configure \
    --without-tests \
    --with-db-path=%{dbpath} \
    --with-pipe-path=%{pipepath} \
    --with-pubconf-path=%{pubconfpath} \
    --with-init-dir=%{_initrddir} \
    --enable-nsslibdir=/%{_lib}

make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT

make install DESTDIR=$RPM_BUILD_ROOT

# Prepare language files
/usr/lib/rpm/find-lang.sh $RPM_BUILD_ROOT sss_daemon
/usr/lib/rpm/find-lang.sh $RPM_BUILD_ROOT sss_client

# Copy default sssd.conf file
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/sssd
install -m600 server/examples/sssd.conf $RPM_BUILD_ROOT%{_sysconfdir}/sssd/sssd.conf
install -m400 server/config/etc/sssd.api.conf $RPM_BUILD_ROOT%{_sysconfdir}/sssd/sssd.api.conf
install -m400 server/config/etc/sssd.api.d/* $RPM_BUILD_ROOT%{_sysconfdir}/sssd/sssd.api.d/

# Remove .la files created by libtool
rm -f \
    $RPM_BUILD_ROOT/%{_lib}/libnss_sss.la \
    $RPM_BUILD_ROOT/%{_lib}/security/pam_sss.la \
    $RPM_BUILD_ROOT/%{_libdir}/ldb/memberof.la \
    $RPM_BUILD_ROOT/%{_libdir}/sssd/libsss_ldap.la \
    $RPM_BUILD_ROOT/%{_libdir}/sssd/libsss_proxy.la \
    $RPM_BUILD_ROOT/%{_libdir}/sssd/libsss_krb5.la \
    $RPM_BUILD_ROOT/%{_libdir}/sssd/libsss_ipa.la \
    $RPM_BUILD_ROOT/%{_libdir}/krb5/plugins/libkrb5/sssd_krb5_locator_plugin.la \
    $RPM_BUILD_ROOT/%{python_sitearch}/pysss.la

if test -e $RPM_BUILD_ROOT/%{_libdir}/krb5/plugins/libkrb5/sssd_krb5_locator_plugin.so
then
    # Apppend this file to the sss_daemon.lang
    # Older versions of rpmbuild can only handle one -f option
    echo %{_libdir}/krb5/plugins/libkrb5/sssd_krb5_locator_plugin.so >> sss_daemon.lang
fi
for file in `ls $RPM_BUILD_ROOT/%{python_sitelib}/*.egg-info 2> /dev/null`
do
    echo %{python_sitelib}/`basename $file` >> sss_daemon.lang
done

%clean
rm -rf $RPM_BUILD_ROOT

%files -f sss_daemon.lang
%defattr(-,root,root,-)
%doc COPYING
%{_initrddir}/%{name}
%{_sbindir}/sssd
%{_sbindir}/sss_useradd
%{_sbindir}/sss_userdel
%{_sbindir}/sss_usermod
%{_sbindir}/sss_groupadd
%{_sbindir}/sss_groupdel
%{_sbindir}/sss_groupmod
%{_libexecdir}/%{servicename}/
%{_libdir}/%{name}/
%{_libdir}/ldb/memberof.so
%dir %{sssdstatedir}
%attr(700,root,root) %dir %{dbpath}
%attr(755,root,root) %dir %{pipepath}
%attr(755,root,root) %dir %{pubconfpath}
%attr(700,root,root) %dir %{pipepath}/private
%attr(750,root,root) %dir %{_var}/log/%{name}
%attr(700,root,root) %dir %{_sysconfdir}/sssd
%config(noreplace) %{_sysconfdir}/sssd/sssd.conf
%config %{_sysconfdir}/sssd/sssd.api.conf
%attr(700,root,root) %dir %{_sysconfdir}/sssd/sssd.api.d
%config %{_sysconfdir}/sssd/sssd.api.d/
%{_mandir}/man5/sssd.conf.5*
%{_mandir}/man5/sssd-ipa.5*
%{_mandir}/man5/sssd-krb5.5*
%{_mandir}/man5/sssd-ldap.5*
%{_mandir}/man8/sssd.8*
%{_mandir}/man8/sss_groupadd.8*
%{_mandir}/man8/sss_groupdel.8*
%{_mandir}/man8/sss_groupmod.8*
%{_mandir}/man8/sss_useradd.8*
%{_mandir}/man8/sss_userdel.8*
%{_mandir}/man8/sss_usermod.8*
%{_mandir}/man8/sssd_krb5_locator_plugin.8*
%{python_sitearch}/pysss.so
%{python_sitelib}/*.py*


%files client -f sss_client.lang
%defattr(-,root,root,-)
%doc sss_client/COPYING sss_client/COPYING.LESSER
/%{_lib}/libnss_sss.so.2
/%{_lib}/security/pam_sss.so
%{_mandir}/man8/pam_sss.8*

%post
/sbin/ldconfig
/sbin/chkconfig --add %{servicename}
if [ $1 -ge 2 ] ; then
# a one-time upgrade from confdb v1 to v2, only if upgrading
    python %{_libexecdir}/%{servicename}/upgrade_config.py
fi

%preun
if [ $1 = 0 ]; then
    /sbin/service %{servicename} stop 2>&1 > /dev/null
    /sbin/chkconfig --del %{servicename}
fi

%postun
/sbin/ldconfig
if [ $1 -ge 1 ] ; then
    /sbin/service %{servicename} condrestart 2>&1 > /dev/null
fi

%post client -p /sbin/ldconfig

%postun client -p /sbin/ldconfig

%changelog
* Wed Feb 24 2010 Stephen Gallagehr <sgallagh@redhat.com> - 1.0.5-2
- Rebuild against new libtevent

* Fri Feb 19 2010 Stephen Gallagher <sgallagh@redhat.com> - 1.0.5-1
- Fix licenses in sources and on RPMs

* Mon Jan 25 2010 Stephen Gallagher <sgallagh@redhat.com> - 1.0.4-1
- Fix regression on 64-bit platforms

* Fri Jan 22 2010 Stephen Gallagher <sgallagh@redhat.com> - 1.0.3-1
- Fixes link error on platforms that do not do implicit linking
- Fixes double-free segfault in PAM
- Fixes double-free error in async resolver
- Fixes support for TCP-based DNS lookups in async resolver
- Fixes memory alignment issues on ARM processors
- Manpage fixes

* Thu Jan 14 2010 Stephen Gallagher <sgallagh@redhat.com> - 1.0.2-1
- Fixes a bug in the failover code that prevented the SSSD from detecting when it went back online
- Fixes a bug causing long (sometimes multiple-minute) waits for NSS requests
- Several segfault bugfixes

* Mon Jan 11 2010 Stephen Gallagher <sgallagh@redhat.com> - 1.0.1-1
- Fix CVE-2010-0014

* Mon Dec 21 2009 Stephen Gallagher <sgallagh@redhat.com> - 1.0.0-2
- Patch SSSDConfig API to address
- https://bugzilla.redhat.com/show_bug.cgi?id=549482

* Fri Dec 18 2009 Stephen Gallagher <sgallagh@redhat.com> - 1.0.0-1
- New upstream stable release 1.0.0

* Fri Dec 11 2009 Stephen Gallagher <sgallagh@redhat.com> - 0.99.1-1
- New upstream bugfix release 0.99.1

* Mon Nov 30 2009 Stephen Gallagher <sgallagh@redhat.com> - 0.99.0-1
- New upstream release 0.99.0

* Tue Oct 27 2009 Stephen Gallagher <sgallagh@redhat.com> - 0.7.1-1
- Fix segfault in sssd_pam when cache_credentials was enabled
- Update the sample configuration
- Fix upgrade issues caused by data provider service removal

* Mon Oct 26 2009 Stephen Gallagher <sgallagh@redhat.com> - 0.7.0-2
- Fix upgrade issues from old (pre-0.5.0) releases of SSSD

* Fri Oct 23 2009 Stephen Gallagher <sgallagh@redhat.com> - 0.7.0-1
- New upstream release 0.7.0

* Thu Oct 15 2009 Stephen Gallagher <sgallagh@redhat.com> - 0.6.1-2
- Fix missing file permissions for sssd-clients

* Tue Oct 13 2009 Stephen Gallagher <sgallagh@redhat.com> - 0.6.1-1
- Add SSSDConfig API
- Update polish translation for 0.6.0
- Fix long timeout on ldap operation
- Make dp requests more robust

* Tue Sep 29 2009 Stephen Gallagher <sgallagh@redhat.com> - 0.6.0-1
- Ensure that the configuration upgrade script always writes the config
  file with 0600 permissions
- Eliminate an infinite loop in group enumerations

* Mon Sep 28 2009 Sumit Bose <sbose@redhat.com> - 0.6.0-0
- New upstream release 0.6.0

* Mon Aug 24 2009 Simo Sorce <ssorce@redhat.com> - 0.5.0-0
- New upstream release 0.5.0

* Wed Jul 29 2009 Jakub Hrozek <jhrozek@redhat.com> - 0.4.1-4
- Fix for CVE-2009-2410 - Native SSSD users with no password set could log in
  without a password. (Patch by Stephen Gallagher)

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.4.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Jun 22 2009 Simo Sorce <ssorce@redhat.com> - 0.4.1-2
- Fix a couple of segfaults that may happen on reload

* Thu Jun 11 2009 Simo Sorce <ssorce@redhat.com> - 0.4.1-1
- add missing configure check that broke stopping the daemon
- also fix default config to add a missing required option

* Mon Jun  8 2009 Simo Sorce <ssorce@redhat.com> - 0.4.1-0
- latest upstream release.
- also add a patch that fixes debugging output (potential segfault)

* Mon Apr 20 2009 Simo Sorce <ssorce@redhat.com> - 0.3.2-2
- release out of the official 0.3.2 tarball

* Mon Apr 20 2009 Jakub Hrozek <jhrozek@redhat.com> - 0.3.2-1
- bugfix release 0.3.2
- includes previous release patches
- change permissions of the /etc/sssd/sssd.conf to 0600

* Tue Apr 14 2009 Simo Sorce <ssorce@redhat.com> - 0.3.1-2
- Add last minute bug fixes, found in testing the package

* Mon Apr 13 2009 Simo Sorce <ssorce@redhat.com> - 0.3.1-1
- Version 0.3.1
- includes previous release patches

* Mon Apr 13 2009 Simo Sorce <ssorce@redhat.com> - 0.3.0-2
- Try to fix build adding automake as an explicit BuildRequire
- Add also a couple of last minute patches from upstream

* Mon Apr 13 2009 Simo Sorce <ssorce@redhat.com> - 0.3.0-1
- Version 0.3.0
- Provides file based configuration and lots of improvements

* Tue Mar 10 2009 Simo Sorce <ssorce@redhat.com> - 0.2.1-1
- Version 0.2.1

* Tue Mar 10 2009 Simo Sorce <ssorce@redhat.com> - 0.2.0-1
- Version 0.2.0

* Sun Mar 08 2009 Jakub Hrozek <jhrozek@redhat.com> - 0.1.0-5.20090309git691c9b3
- package git snapshot

* Fri Mar 06 2009 Jakub Hrozek <jhrozek@redhat.com> - 0.1.0-4
- fixed items found during review
- added initscript

* Thu Mar 05 2009 Sumit Bose <sbose@redhat.com> - 0.1.0-3
- added sss_client

* Mon Feb 23 2009 Jakub Hrozek <jhrozek@redhat.com> - 0.1.0-2
- Small cleanup and fixes in the spec file

* Thu Feb 12 2009 Stephen Gallagher <sgallagh@redhat.com> - 0.1.0-1
- Initial release (based on version 0.1.0 upstream code)
