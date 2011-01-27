%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

Name: sssd
Version: 1.5.1
Release: 1%{?dist}
Group: Applications/System
Summary: System Security Services Daemon
License: GPLv3+
URL: http://fedorahosted.org/sssd/
Source0: https://fedorahosted.org/released/sssd/%{name}-%{version}.tar.gz
BuildRoot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

### Patches ###

### Dependencies ###

Requires: libldb >= 0.9.3
Requires: libtdb >= 1.1.3
Requires: sssd-client = %{version}-%{release}
Requires: krb5-libs >= 1.9
Requires(post): initscripts chkconfig /sbin/ldconfig
Requires(preun):  initscripts chkconfig
Requires(postun): initscripts chkconfig /sbin/ldconfig

%global servicename sssd
%global sssdstatedir %{_localstatedir}/lib/sss
%global dbpath %{sssdstatedir}/db
%global pipepath %{sssdstatedir}/pipes
%global pubconfpath %{sssdstatedir}/pubconf

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
BuildRequires: libtevent-devel
BuildRequires: libtdb-devel
BuildRequires: libldb-devel
BuildRequires: libdhash-devel >= 0.4.2
BuildRequires: libcollection-devel
BuildRequires: libini_config-devel
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
BuildRequires: krb5-devel >= 1.9
BuildRequires: c-ares-devel
BuildRequires: python-devel
BuildRequires: check-devel
BuildRequires: doxygen
BuildRequires: libselinux-devel
BuildRequires: libsemanage-devel
BuildRequires: bind-utils
BuildRequires: keyutils-libs-devel
BuildRequires: libnl-devel
BuildRequires: nscd

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

%package tools
Summary: Userspace tools for use with the SSSD
Group: Applications/System
License: GPLv3+
Requires: sssd = %{version}-%{release}

%description tools
Provides userspace tools for manipulating users, groups, and nested groups in
SSSD when using id_provider = local in /etc/sssd/sssd.conf.

Also provides a userspace tool for generating an obfuscated LDAP password for
use with ldap_default_authtok_type = obfuscated_password.

%prep
%setup -q

%build
%configure \
    --with-db-path=%{dbpath} \
    --with-pipe-path=%{pipepath} \
    --with-pubconf-path=%{pubconfpath} \
    --with-init-dir=%{_initrddir} \
    --enable-nsslibdir=/%{_lib} \
    --enable-pammoddir=/%{_lib}/security \
    --disable-static \
    --disable-rpath \
    --with-test-dir=/dev/shm

make %{?_smp_mflags}

%check
export CK_TIMEOUT_MULTIPLIER=10
make %{?_smp_mflags} check
unset CK_TIMEOUT_MULTIPLIER

%install
rm -rf $RPM_BUILD_ROOT

make install DESTDIR=$RPM_BUILD_ROOT

# Prepare language files
/usr/lib/rpm/find-lang.sh $RPM_BUILD_ROOT sssd

# Copy default sssd.conf file
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/sssd
install -m600 src/examples/sssd.conf $RPM_BUILD_ROOT%{_sysconfdir}/sssd/sssd.conf
install -m400 src/config/etc/sssd.api.conf $RPM_BUILD_ROOT%{_sysconfdir}/sssd/sssd.api.conf
install -m400 src/config/etc/sssd.api.d/* $RPM_BUILD_ROOT%{_sysconfdir}/sssd/sssd.api.d/

# Copy default logrotate file
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/logrotate.d
install -m644 src/examples/logrotate $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/sssd

# Make sure SSSD is able to run on read-only root
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/rwtab.d
install -m644 src/examples/rwtab $RPM_BUILD_ROOT%{_sysconfdir}/rwtab.d/sssd

# Remove .la files created by libtool
rm -f \
    $RPM_BUILD_ROOT/%{_lib}/libnss_sss.la \
    $RPM_BUILD_ROOT/%{_lib}/security/pam_sss.la \
    $RPM_BUILD_ROOT/%{_libdir}/ldb/memberof.la \
    $RPM_BUILD_ROOT/%{_libdir}/sssd/libsss_ldap.la \
    $RPM_BUILD_ROOT/%{_libdir}/sssd/libsss_proxy.la \
    $RPM_BUILD_ROOT/%{_libdir}/sssd/libsss_krb5.la \
    $RPM_BUILD_ROOT/%{_libdir}/sssd/libsss_ipa.la \
    $RPM_BUILD_ROOT/%{_libdir}/sssd/libsss_simple.la \
    $RPM_BUILD_ROOT/%{_libdir}/krb5/plugins/libkrb5/sssd_krb5_locator_plugin.la \
    $RPM_BUILD_ROOT/%{python_sitearch}/pysss.la

# Older versions of rpmbuild can only handle one -f option
# So we need to append to the sssd.lang file
for file in `ls $RPM_BUILD_ROOT/%{python_sitelib}/*.egg-info 2> /dev/null`
do
    echo %{python_sitelib}/`basename $file` >> sssd.lang
done

%clean
rm -rf $RPM_BUILD_ROOT

%files -f sssd.lang
%defattr(-,root,root,-)
%doc COPYING
%{_initrddir}/%{name}
%{_sbindir}/sssd
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
%config(noreplace) %{_sysconfdir}/logrotate.d/sssd
%config(noreplace) %{_sysconfdir}/rwtab.d/sssd
%config %{_sysconfdir}/sssd/sssd.api.conf
%attr(700,root,root) %dir %{_sysconfdir}/sssd/sssd.api.d
%config %{_sysconfdir}/sssd/sssd.api.d/
%{_mandir}/man5/sssd.conf.5*
%{_mandir}/man5/sssd-ipa.5*
%{_mandir}/man5/sssd-krb5.5*
%{_mandir}/man5/sssd-ldap.5*
%{_mandir}/man5/sssd-simple.5*
%{_mandir}/man8/sssd.8*
%{python_sitearch}/pysss.so
%{python_sitelib}/*.py*

%lang(cs)       %{_mandir}/cs/man[58]/*
%lang(uk)       %{_mandir}/uk/man[58]/*

%files client
%defattr(-,root,root,-)
%doc src/sss_client/COPYING src/sss_client/COPYING.LESSER
/%{_lib}/libnss_sss.so.2
/%{_lib}/security/pam_sss.so
%{_libdir}/krb5/plugins/libkrb5/sssd_krb5_locator_plugin.so
%{_mandir}/man8/pam_sss.8*
%{_mandir}/man8/sssd_krb5_locator_plugin.8*

%files tools
%defattr(-,root,root,-)
%doc COPYING
%{_sbindir}/sss_useradd
%{_sbindir}/sss_userdel
%{_sbindir}/sss_usermod
%{_sbindir}/sss_groupadd
%{_sbindir}/sss_groupdel
%{_sbindir}/sss_groupmod
%{_sbindir}/sss_groupshow
%{_sbindir}/sss_obfuscate
%{_mandir}/man8/sss_groupadd.8*
%{_mandir}/man8/sss_groupdel.8*
%{_mandir}/man8/sss_groupmod.8*
%{_mandir}/man8/sss_groupshow.8*
%{_mandir}/man8/sss_useradd.8*
%{_mandir}/man8/sss_userdel.8*
%{_mandir}/man8/sss_usermod.8*
%{_mandir}/man8/sss_obfuscate.8*

%post
/sbin/ldconfig
/sbin/chkconfig --add %{servicename}

if [ $1 -ge 1 ] ; then
    /sbin/service %{servicename} condrestart 2>&1 > /dev/null
fi

%preun
if [ $1 = 0 ]; then
    /sbin/service %{servicename} stop 2>&1 > /dev/null
    /sbin/chkconfig --del %{servicename}
fi

%postun -p /sbin/ldconfig

%post client -p /sbin/ldconfig

%postun client -p /sbin/ldconfig

%changelog
* Thu Jan 27 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.5.1-1
- New upstream release 1.5.1
- Addresses CVE-2010-4341 - DoS in sssd PAM responder can prevent logins
- Vast performance improvements when enumerate = true
- All PAM actions will now perform a forced initgroups lookup instead of just
- a user information lookup
-   This guarantees that all group information is available to other
-   providers, such as the simple provider.
- For backwards-compatibility, DNS lookups will also fall back to trying the
- SSSD domain name as a DNS discovery domain.
- Support for more password expiration policies in LDAP
-    389 Directory Server
-    FreeIPA
-    ActiveDirectory
- Support for ldap_tls_{cert,key,cipher_suite} config options
-Assorted bugfixes

* Tue Jan 11 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.5.0-2
- CVE-2010-4341 - DoS in sssd PAM responder can prevent logins

* Wed Dec 22 2010 Stephen Gallagher <sgallagh@redhat.com> - 1.5.0-1
- New upstream release 1.5.0
- Fixed issues with LDAP search filters that needed to be escaped
- Add Kerberos FAST support on platforms that support it
- Reduced verbosity of PAM_TEXT_INFO messages for cached credentials
- Added a Kerberos access provider to honor .k5login
- Addressed several thread-safety issues in the sss_client code
- Improved support for delayed online Kerberos auth
- Significantly reduced time between connecting to the network/VPN and
- acquiring a TGT
- Added feature for automatic Kerberos ticket renewal
- Provides the kerberos ticket for long-lived processes or cron jobs
- even when the user logs out
- Added several new features to the LDAP access provider
- Support for 'shadow' access control
- Support for authorizedService access control
- Ability to mix-and-match LDAP access control features
- Added an option for a separate password-change LDAP server for those
- platforms where LDAP referrals are not supported
- Added support for manpage translations


* Thu Nov 18 2010 Stephen Gallagher <sgallagh@redhat.com> - 1.4.1-3
- Solve a shutdown race-condition that sometimes left processes running
- Resolves: rhbz#606887 - SSSD stops on upgrade

* Tue Nov 16 2010 Stephen Gallagher <sgallagh@redhat.com> - 1.4.1-2
- Log startup errors to the syslog
- Allow cache cleanup to be disabled in sssd.conf

* Mon Nov 01 2010 Stephen Gallagher <sgallagh@redhat.com> - 1.4.1-1
- New upstream release 1.4.1
- Add support for netgroups to the proxy provider
- Fixes a minor bug with UIDs/GIDs >= 2^31
- Fixes a segfault in the kerberos provider
- Fixes a segfault in the NSS responder if a data provider crashes
- Correctly use sdap_netgroup_search_base

* Mon Oct 18 2010 Stephen Gallagher <sgallagh@redhat.com> - 1.4.0-2
- Fix incorrect tarball URL

* Mon Oct 18 2010 Stephen Gallagher <sgallagh@redhat.com> - 1.4.0-1
- New upstream release 1.4.0
- Added support for netgroups to the LDAP provider
- Performance improvements made to group processing of RFC2307 LDAP servers
- Fixed nested group issues with RFC2307bis LDAP servers without a memberOf plugin
- Build-system improvements to support Gentoo
- Split out several libraries into the ding-libs tarball
- Manpage reviewed and updated

* Mon Oct 04 2010 Stephen Gallagher <sgallagh@redhat.com> - 1.3.0-35
- Fix pre and post script requirements

* Mon Oct 04 2010 Stephen Gallagher <sgallagh@redhat.com> - 1.3.0-34
- Resolves: rhbz#606887 - sssd stops on upgrade

* Fri Oct 01 2010 Stephen Gallagher <sgallagh@redhat.com> - 1.3.0-33
- Resolves: rhbz#626205 - Unable to unlock screen

* Tue Sep 28 2010 Stephen Gallagher <sgallagh@redhat.com> - 1.3.0-32
- Resolves: rhbz#637955 - libini_config-devel needs libcollection-devel but
-                         doesn't require it

* Thu Sep 16 2010 Stephen Gallagher <sgallagh@redhat.com> - 1.3.0-31
- Resolves: rhbz#632615 - the krb5 locator plugin isn't packaged for multilib

* Tue Aug 24 2010 Stephen Gallagher <sgallagh@redhat.com> - 1.3.0-30
- Resolves: CVE-2010-2940 - sssd allows null password entry to authenticate
-                           against LDAP

* Thu Jul 22 2010 David Malcolm <dmalcolm@redhat.com> - 1.2.91-21
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Fri Jul 09 2010 Stephen Gallagher <sgallagh@redhat.com> - 1.2.91-20
- New upstream version 1.2.91 (1.3.0rc1)
- Improved LDAP failover
- Synchronous sysdb API (provides performance enhancements)
- Better online reconnection detection

* Mon Jun 21 2010 Stephen Gallagher <sgallagh@redhat.com> - 1.2.1-15
- New stable upstream version 1.2.1
- Resolves: rhbz#595529 - spec file should eschew %%define in favor of
-                         %%global
- Resolves: rhbz#593644 - Empty list of simple_allow_users causes sssd service
-                         to fail while restart.
- Resolves: rhbz#599026 - Makefile typo causes SSSD not to use the kernel
-                         keyring
- Resolves: rhbz#599724 - sssd is broken on Rawhide

* Mon May 24 2010 Stephen Gallagher <sgallagh@redhat.com> - 1.2.0-12
- New stable upstream version 1.2.0
- Support ServiceGroups for FreeIPA v2 HBAC rules
- Fix long-standing issue with auth_provider = proxy
- Better logging for TLS issues in LDAP

* Tue May 18 2010 Stephen Gallagher <sgallagh@redhat.com> - 1.1.92-11
- New LDAP access provider allows for filtering user access by LDAP attribute
- Reduced default timeout for detecting offline status with LDAP
- GSSAPI ticket lifetime made configurable
- Better offline->online transition support in Kerberos

* Fri May 07 2010 Stephen Gallagher <sgallagh@redhat.com> - 1.1.91-10
- Release new upstream version 1.1.91
- Enhancements when using SSSD with FreeIPA v2
- Support for deferred kinit
- Support for DNS SRV records for failover

* Fri Apr 02 2010 Simo Sorce <ssorce@redhat.com> - 1.1.1-3
- Bump up release number to avoid library sub-packages version issues with
  previous releases.

* Thu Apr 01 2010 Stephen Gallagher <sgallagh@redhat.com> - 1.1.1-1
- New upstream release 1.1.1
- Fixed the IPA provider (which was segfaulting at start)
- Fixed a bug in the SSSDConfig API causing some options to revert to
- their defaults
- This impacted the Authconfig UI
- Ensure that SASL binds to LDAP auto-retry when interrupted by a signal

* Tue Mar 22 2010 Stephen Gallagher <sgallagh@redhat.com> - 1.1.0-2
- Release SSSD 1.1.0 final
- Fix two potential segfaults
- Fix memory leak in monitor
- Better error message for unusable confdb

* Wed Mar 17 2010 Stephen Gallagher <sgallagh@redhat.com> - 1.1.0-1.pre20100317git0ea7f19
- Release candidate for SSSD 1.1
- Add simple access provider
- Create subpackages for libcollection, libini_config, libdhash and librefarray
- Support IPv6
- Support LDAP referrals
- Fix cache issues
- Better feedback from PAM when offline

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
