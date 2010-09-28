%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

Name: sssd
Version: 1.3.0
#Never reset the Release, always increment it
#Otherwise we can have issues if library versions do not change
Release: 32%{?dist}
Group: Applications/System
Summary: System Security Services Daemon
License: GPLv3+
URL: http://fedorahosted.org/sssd/
Source0: https://fedorahosted.org/released/sssd/%{name}-%{version}.tar.gz
BuildRoot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

%global dhash_version 0.4.0
%global path_utils_version 0.2.0
%global collection_version 0.5.0
%global ini_config_version 0.6.0
%global refarray_version 0.1.0

### Patches ###
Patch0001: 0001-Treat-a-zero-length-password-as-a-failure.patch

### Dependencies ###

Requires: libldb >= 0.9.3
Requires: libtdb >= 1.1.3
Requires: sssd-client = %{version}-%{release}
Requires: libdhash >= %{dhash_version}
Requires: libcollection >= %{collection_version}
Requires: libini_config >= %{ini_config_version}
Requires: cyrus-sasl-gssapi
Requires: keyutils-libs
Requires(post): python
Requires(preun):  initscripts chkconfig
Requires(postun): /sbin/service

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
BuildRequires: check-devel
BuildRequires: doxygen
BuildRequires: libselinux-devel
BuildRequires: libsemanage-devel
BuildRequires: keyutils-libs-devel
BuildRequires: bind-utils
BuildRequires: libnl-devel

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

%package -n libdhash
Summary: Dynamic hash table
Group: Development/Libraries
Version: %{dhash_version}
License: LGPLv3+

%description -n libdhash
A hash table which will dynamically resize to achieve optimal storage & access
time properties

%package -n libdhash-devel
Summary: Development files for libdhash
Group: Development/Libraries
Version: %{dhash_version}
Requires: libdhash = %{dhash_version}-%{release}
License: LGPLv3+

%description -n libdhash-devel
A hash table which will dynamically resize to achieve optimal storage & access
time properties

%package -n libpath_utils
Summary: Filesystem Path Utilities
Group: Development/Libraries
Version: %{path_utils_version}
License: LGPLv3+

%description -n libpath_utils
Utility functions to manipulate filesystem pathnames

%package -n libpath_utils-devel
Summary: Development files for libpath_utils
Group: Development/Libraries
Version: %{path_utils_version}
Requires: libpath_utils = %{path_utils_version}-%{release}
License: LGPLv3+

%description -n libpath_utils-devel
Utility functions to manipulate filesystem pathnames

%package -n libcollection
Summary: Collection data-type for C
Group: Development/Libraries
Version: %{collection_version}
License: LGPLv3+

%description -n libcollection
A data-type to collect data in a heirarchical structure for easy iteration
and serialization

%package -n libcollection-devel
Summary: Development files for libcollection
Group: Development/Libraries
Version: %{collection_version}
Requires: libcollection = %{collection_version}-%{release}
License: LGPLv3+

%description -n libcollection-devel
A data-type to collect data in a heirarchical structure for easy iteration
and serialization

%package -n libini_config
Summary: INI file parser for C
Group: Development/Libraries
Version: %{ini_config_version}
Requires: libcollection >= %{collection_version}
License: LGPLv3+

%description -n libini_config
Library to process config files in INI format into a libcollection data
structure

%package -n libini_config-devel
Summary: Development files for libini_config
Group: Development/Libraries
Version: %{ini_config_version}
Requires: libini_config = %{ini_config_version}-%{release}
Requires: libcollection-devel
License: LGPLv3+

%description -n libini_config-devel
Library to process config files in INI format into a libcollection data
structure

%package -n libref_array
Summary: A refcounted array for C
Group: Development/Libraries
Version: %{refarray_version}
License: LGPLv3+

%description -n libref_array
A dynamically-growing, reference-counted array

%package -n libref_array-devel
Summary: Development files for libref_array
Group: Development/Libraries
Version: %{refarray_version}
Requires: libref_array = %{refarray_version}-%{release}
License: LGPLv3+

%description -n libref_array-devel
A dynamically-growing, reference-counted array

%prep
%setup -q
%patch0001 -p1

%build
%configure \
    --with-db-path=%{dbpath} \
    --with-pipe-path=%{pipepath} \
    --with-pubconf-path=%{pubconfpath} \
    --with-init-dir=%{_initrddir} \
    --enable-nsslibdir=/%{_lib} \
    --enable-pammoddir=/%{_lib}/security \
    --disable-static \
    --disable-rpath

make %{?_smp_mflags}

pushd common
make %{?_smp_mflags} docs
popd

%check
make %{?_smp_mflags} check

%install
rm -rf $RPM_BUILD_ROOT

make install DESTDIR=$RPM_BUILD_ROOT

# Remove the example files from the output directory
# We will copy them directly from the source directory
# for packaging
rm -f \
    $RPM_BUILD_ROOT/usr/share/doc/dhash/README \
    $RPM_BUILD_ROOT/usr/share/doc/dhash/examples/dhash_example.c \
    $RPM_BUILD_ROOT/usr/share/doc/dhash/examples/dhash_test.c

# Prepare language files
/usr/lib/rpm/find-lang.sh $RPM_BUILD_ROOT sss_daemon

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
    $RPM_BUILD_ROOT/%{_libdir}/libdhash.la \
    $RPM_BUILD_ROOT/%{_libdir}/libpath_utils.la \
    $RPM_BUILD_ROOT/%{_libdir}/libcollection.la \
    $RPM_BUILD_ROOT/%{_libdir}/libini_config.la \
    $RPM_BUILD_ROOT/%{_libdir}/libref_array.la \
    $RPM_BUILD_ROOT/%{_libdir}/ldb/memberof.la \
    $RPM_BUILD_ROOT/%{_libdir}/sssd/libsss_ldap.la \
    $RPM_BUILD_ROOT/%{_libdir}/sssd/libsss_proxy.la \
    $RPM_BUILD_ROOT/%{_libdir}/sssd/libsss_krb5.la \
    $RPM_BUILD_ROOT/%{_libdir}/sssd/libsss_ipa.la \
    $RPM_BUILD_ROOT/%{_libdir}/sssd/libsss_simple.la \
    $RPM_BUILD_ROOT/%{_libdir}/krb5/plugins/libkrb5/sssd_krb5_locator_plugin.la \
    $RPM_BUILD_ROOT/%{python_sitearch}/pysss.la

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
%{_sbindir}/sss_groupshow
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
%{_mandir}/man8/sss_groupadd.8*
%{_mandir}/man8/sss_groupdel.8*
%{_mandir}/man8/sss_groupmod.8*
%{_mandir}/man8/sss_groupshow.8*
%{_mandir}/man8/sss_useradd.8*
%{_mandir}/man8/sss_userdel.8*
%{_mandir}/man8/sss_usermod.8*
%{_mandir}/man8/sssd_krb5_locator_plugin.8*
%{python_sitearch}/pysss.so
%{python_sitelib}/*.py*


%files client
%defattr(-,root,root,-)
%doc src/sss_client/COPYING src/sss_client/COPYING.LESSER
/%{_lib}/libnss_sss.so.2
/%{_lib}/security/pam_sss.so
%{_libdir}/krb5/plugins/libkrb5/sssd_krb5_locator_plugin.so
%{_mandir}/man8/pam_sss.8*

%files -n libdhash
%defattr(-,root,root,-)
%doc common/dhash/COPYING
%doc common/dhash/COPYING.LESSER
%{_libdir}/libdhash.so.1
%{_libdir}/libdhash.so.1.0.0

%files -n libdhash-devel
%defattr(-,root,root,-)
%{_includedir}/dhash.h
%{_libdir}/libdhash.so
%{_libdir}/pkgconfig/dhash.pc
%doc common/dhash/README
%doc common/dhash/examples

%files -n libpath_utils
%defattr(-,root,root,-)
%doc common/path_utils/COPYING
%doc common/path_utils/COPYING.LESSER
%{_libdir}/libpath_utils.so.1
%{_libdir}/libpath_utils.so.1.0.0

%files -n libpath_utils-devel
%defattr(-,root,root,-)
%{_includedir}/path_utils.h
%{_libdir}/libpath_utils.so
%{_libdir}/pkgconfig/path_utils.pc
%doc common/path_utils/README
%doc common/path_utils/doc/html/

%files -n libcollection
%defattr(-,root,root,-)
%doc common/collection/COPYING
%doc common/collection/COPYING.LESSER
%{_libdir}/libcollection.so.2
%{_libdir}/libcollection.so.2.0.0

%files -n libcollection-devel
%defattr(-,root,root,-)
%{_includedir}/collection.h
%{_includedir}/collection_tools.h
%{_includedir}/collection_queue.h
%{_includedir}/collection_stack.h
%{_libdir}/libcollection.so
%{_libdir}/pkgconfig/collection.pc
%doc common/collection/doc/html/

%files -n libini_config
%defattr(-,root,root,-)
%doc common/ini/COPYING
%doc common/ini/COPYING.LESSER
%{_libdir}/libini_config.so.2
%{_libdir}/libini_config.so.2.0.0

%files -n libini_config-devel
%defattr(-,root,root,-)
%{_includedir}/ini_config.h
%{_libdir}/libini_config.so
%{_libdir}/pkgconfig/ini_config.pc
%doc common/ini/doc/html/

%files -n libref_array
%defattr(-,root,root,-)
%doc common/refarray/COPYING
%doc common/refarray/COPYING.LESSER
%{_libdir}/libref_array.so.1
%{_libdir}/libref_array.so.1.0.0

%files -n libref_array-devel
%defattr(-,root,root,-)
%{_includedir}/ref_array.h
%{_libdir}/libref_array.so
%{_libdir}/pkgconfig/ref_array.pc
%doc common/refarray/README
%doc common/refarray/doc/html/


%post
/sbin/ldconfig
/sbin/chkconfig --add %{servicename}
if [ $1 -ge 2 ] ; then
# a one-time upgrade from confdb v1 to v2, only if upgrading
    python %{_libexecdir}/%{servicename}/upgrade_config.py
fi

if [ $1 -ge 1 ] ; then
    /sbin/service %{servicename} condrestart 2>&1 > /dev/null
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

%post -n libdhash -p /sbin/ldconfig

%postun -n libdhash -p /sbin/ldconfig

%post -n libpath_utils -p /sbin/ldconfig
%postun -n libpath_utils -p /sbin/ldconfig

%post -n libcollection -p /sbin/ldconfig
%postun -n libcollection -p /sbin/ldconfig

%post -n libini_config -p /sbin/ldconfig
%postun -n libini_config -p /sbin/ldconfig

%post -n libref_array -p /sbin/ldconfig
%postun -n libref_array -p /sbin/ldconfig

%changelog
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
