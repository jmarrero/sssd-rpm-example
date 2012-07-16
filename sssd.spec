%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

# we don't want to provide private python extension libs
%define __provides_exclude_from %{python_sitearch}/.*\.so$

%if (0%{?fedora} > 15)
%define _hardened_build 1
%endif

# Determine the location of the LDB modules directory
%global ldb_modulesdir %(pkg-config --variable=modulesdir ldb)
%global ldb_version 1.1.8

Name: sssd
Version: 1.9.0
Release: 11%{?dist}.beta4
Group: Applications/System
Summary: System Security Services Daemon
License: GPLv3+
URL: http://fedorahosted.org/sssd/
Source0: https://fedorahosted.org/released/sssd/%{name}-%{version}beta4.tar.gz
BuildRoot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

### Patches ###

Patch0001: 0001-AD-Add-missing-DP-option-terminator.patch

### Dependencies ###

Conflicts: selinux-policy < 3.10.0-46
Requires: libldb%{?_isa} = %{ldb_version}
Requires: libtdb%{?_isa} >= 1.1.3
Requires: sssd-client%{?_isa} = %{version}-%{release}
Requires: cyrus-sasl-gssapi%{?_isa}
Requires: libipa_hbac%{?_isa} = %{version}-%{release}
Requires: libsss_idmap%{?_isa} = %{version}-%{release}
Requires: krb5-libs%{?_isa} >= 1.10
Requires(post): systemd-units initscripts chkconfig /sbin/ldconfig
Requires(preun): systemd-units initscripts chkconfig
Requires(postun): systemd-units initscripts chkconfig /sbin/ldconfig

%global servicename sssd
%global sssdstatedir %{_localstatedir}/lib/sss
%global dbpath %{sssdstatedir}/db
%global pipepath %{sssdstatedir}/pipes
%global pubconfpath %{sssdstatedir}/pubconf
%global mcachepath %{sssdstatedir}/mc

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
BuildRequires: libldb-devel = %{ldb_version}
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
BuildRequires: krb5-devel >= 1.10
BuildRequires: c-ares-devel
BuildRequires: python-devel
BuildRequires: check-devel
BuildRequires: doxygen
BuildRequires: libselinux-devel
BuildRequires: libsemanage-devel
BuildRequires: bind-utils
BuildRequires: keyutils-libs-devel
BuildRequires: libnl-devel
BuildRequires: gettext-devel
BuildRequires: pkgconfig
BuildRequires: glib2-devel
BuildRequires: findutils
BuildRequires: samba4-devel >= samba4-4.0.0-59beta2

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

%package -n libsss_idmap
Summary: FreeIPA Idmap library
Group: Development/Libraries
License: LGPLv3+

%description -n libsss_idmap
Utility library to SIDs to Unix uids and gids

%package -n libsss_idmap-devel
Summary: FreeIPA Idmap library
Group: Development/Libraries
License: LGPLv3+
Requires: libsss_idmap = %{version}-%{release}

%description -n libsss_idmap-devel
Utility library to SIDs to Unix uids and gids

%package -n libipa_hbac
Summary: FreeIPA HBAC Evaluator library
Group: Development/Libraries
License: LGPLv3+

%description -n libipa_hbac
Utility library to validate FreeIPA HBAC rules for authorization requests

%package -n libipa_hbac-devel
Summary: FreeIPA HBAC Evaluator library
Group: Development/Libraries
License: LGPLv3+
Requires: libipa_hbac = %{version}-%{release}

%description -n libipa_hbac-devel
Utility library to validate FreeIPA HBAC rules for authorization requests

%package -n libipa_hbac-python
Summary: Python bindings for the FreeIPA HBAC Evaluator library
Group: Development/Libraries
License: LGPLv3+
Requires: libipa_hbac = %{version}-%{release}

%description -n libipa_hbac-python
The libipa_hbac-python contains the bindings so that libipa_hbac can be
used by Python applications.

%package -n libsss_sudo
Summary: A library to allow communication between SUDO and SSSD
Group: Development/Libraries
License: LGPLv3+

%description -n libsss_sudo
A utility library to allow communication between SUDO and SSSD

%package -n libsss_sudo-devel
Summary: A library to allow communication between SUDO and SSSD
Group: Development/Libraries
License: LGPLv3+
Requires: libsss_sudo = %{version}-%{release}

%description -n libsss_sudo-devel
A utility library to allow communication between SUDO and SSSD

%prep
# Update timestamps on the files touched by a patch, to avoid non-equal
# .pyc/.pyo files across the multilib peers within a build, where "Level"
# is the patch prefix option (e.g. -p1)
# Taken from specfile for python-simplejson
UpdateTimestamps() {
  Level=$1
  PatchFile=$2

  # Locate the affected files:
  for f in $(diffstat $Level -l $PatchFile); do
    # Set the files to have the same timestamp as that of the patch:
    touch -r $PatchFile $f
  done
}

%setup -q -n %{name}-1.8.94

for p in %patches ; do
    %__patch -p1 -i $p
    UpdateTimestamps -p1 $p
done

%build
autoreconf -ivf
%configure \
    --with-db-path=%{dbpath} \
    --with-pipe-path=%{pipepath} \
    --with-pubconf-path=%{pubconfpath} \
    --with-mcache-path=%{mcachepath} \
    --with-init-dir=%{_initrddir} \
    --with-krb5-rcache-dir=%{_localstatedir}/cache/krb5rcache \
    --with-default-ccache-dir=/run/user/%U \
    --with-default-ccname-template=DIR:%d/ccdir \
    --enable-nsslibdir=/%{_lib} \
    --enable-pammoddir=/%{_lib}/security \
    --disable-static \
    --disable-rpath \
    --with-test-dir=/dev/shm \
    --enable-all-experimental-features

make %{?_smp_mflags} all docs

%check
# 'patch' doesn't create the new tests with the executable flag
chmod +x src/tests/pyhbac-test.py

export CK_TIMEOUT_MULTIPLIER=10
make %{?_smp_mflags} check
unset CK_TIMEOUT_MULTIPLIER

%install
rm -rf $RPM_BUILD_ROOT

make install DESTDIR=$RPM_BUILD_ROOT

# Prepare language files
/usr/lib/rpm/find-lang.sh $RPM_BUILD_ROOT sssd

# Prepare empty config file
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/sssd
touch $RPM_BUILD_ROOT/%{_sysconfdir}/sssd/sssd.conf

# Copy default logrotate file
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/logrotate.d
install -m644 src/examples/logrotate $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/sssd

# Make sure SSSD is able to run on read-only root
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/rwtab.d
install -m644 src/examples/rwtab $RPM_BUILD_ROOT%{_sysconfdir}/rwtab.d/sssd

# Replace sysv init script with systemd unit file
rm -f $RPM_BUILD_ROOT/%{_initrddir}/%{name}
mkdir -p $RPM_BUILD_ROOT/%{_unitdir}/
cp src/sysv/systemd/sssd.service $RPM_BUILD_ROOT/%{_unitdir}/

# Remove .la files created by libtool
find $RPM_BUILD_ROOT -name "*.la" -exec rm -f {} \;

# Suppress developer-only documentation
rm -Rf ${RPM_BUILD_ROOT}/%{_docdir}/%{name}

# Older versions of rpmbuild can only handle one -f option
# So we need to append to the sssd.lang file
for file in `ls $RPM_BUILD_ROOT/%{python_sitelib}/*.egg-info 2> /dev/null`
do
    echo %{python_sitelib}/`basename $file` >> sssd.lang
done

touch sssd_tools.lang
for man in `find $RPM_BUILD_ROOT/%{_mandir}/??/man?/ -type f | sed -e "s#$RPM_BUILD_ROOT/%{_mandir}/##"`
do
    lang=`echo $man | cut -c 1-2`
    case `basename $man` in
        sss_*)
            echo \%lang\(${lang}\) \%{_mandir}/${man}\* >> sssd_tools.lang
            ;;
        pam_sss*)
            echo \%lang\(${lang}\) \%{_mandir}/${man}\* >> sssd_client.lang
            ;;
        sssd_krb5_locator_plugin*)
            echo \%lang\(${lang}\) \%{_mandir}/${man}\* >> sssd_client.lang
            ;;
        *)
            echo \%lang\(${lang}\) \%{_mandir}/${man}\* >> sssd.lang
            ;;
    esac
done

# Print these to the rpmbuild log
echo "sssd.lang:"
cat sssd.lang

echo "sssd_client.lang:"
cat sssd_client.lang

echo "sssd_tools.lang:"
cat sssd_tools.lang


%clean
rm -rf $RPM_BUILD_ROOT

%files -f sssd.lang
%defattr(-,root,root,-)
%doc COPYING
%doc src/examples/sssd-example.conf
%{_unitdir}/sssd.service
%{_sbindir}/sssd

%dir %{_libexecdir}/%{servicename}
%{_libexecdir}/%{servicename}/krb5_child
%{_libexecdir}/%{servicename}/ldap_child
%{_libexecdir}/%{servicename}/proxy_child
%{_libexecdir}/%{servicename}/sssd_be
%{_libexecdir}/%{servicename}/sssd_nss
%{_libexecdir}/%{servicename}/sssd_pam
%{_libexecdir}/%{servicename}/sssd_autofs
%{_libexecdir}/%{servicename}/sssd_ssh
%{_libexecdir}/%{servicename}/sssd_sudo
%{_libexecdir}/%{servicename}/sssd_pac

%dir %{_libdir}/%{name}
%{_libdir}/%{name}/libsss_ipa.so
%{_libdir}/%{name}/libsss_krb5.so
%{_libdir}/%{name}/libsss_ldap.so
%{_libdir}/%{name}/libsss_proxy.so
%{_libdir}/%{name}/libsss_simple.so
%{_libdir}/%{name}/libsss_ad.so

%{ldb_modulesdir}/memberof.so
%{_bindir}/sss_ssh_authorizedkeys
%{_bindir}/sss_ssh_knownhostsproxy

%dir %{sssdstatedir}
%dir %{_localstatedir}/cache/krb5rcache
%attr(700,root,root) %dir %{dbpath}
%attr(755,root,root) %dir %{pipepath}
%attr(755,root,root) %dir %{pubconfpath}
%attr(755,root,root) %dir %{mcachepath}
%attr(700,root,root) %dir %{pipepath}/private
%attr(750,root,root) %dir %{_var}/log/%{name}
%attr(700,root,root) %dir %{_sysconfdir}/sssd
%ghost %attr(0600,root,root) %config(noreplace) %{_sysconfdir}/sssd/sssd.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/sssd
%config(noreplace) %{_sysconfdir}/rwtab.d/sssd
%dir %{_datadir}/sssd
%{_datadir}/sssd/sssd.api.conf
%{_datadir}/sssd/sssd.api.d
%{_mandir}/man1/sss_ssh_authorizedkeys.1*
%{_mandir}/man1/sss_ssh_knownhostsproxy.1*
%{_mandir}/man5/sssd.conf.5*
%{_mandir}/man5/sssd-ipa.5*
%{_mandir}/man5/sssd-krb5.5*
%{_mandir}/man5/sssd-ldap.5*
%{_mandir}/man5/sssd-simple.5*
%{_mandir}/man5/sssd-ad.5*
%{_mandir}/man8/sssd.8*
%{python_sitearch}/pysss.so
%dir %{python_sitelib}/SSSDConfig
%{python_sitelib}/SSSDConfig/*.py*

%files client -f sssd_client.lang
%defattr(-,root,root,-)
%doc src/sss_client/COPYING src/sss_client/COPYING.LESSER
/%{_lib}/libnss_sss.so.2
/%{_lib}/security/pam_sss.so
%{_libdir}/krb5/plugins/libkrb5/sssd_krb5_locator_plugin.so
%{_libdir}/krb5/plugins/authdata/sssd_pac_plugin.so
%{_mandir}/man8/pam_sss.8*
%{_mandir}/man8/sssd_krb5_locator_plugin.8*

%files tools -f sssd_tools.lang
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
%{_sbindir}/sss_cache
%{_sbindir}/sss_debuglevel
%{_mandir}/man8/sss_groupadd.8*
%{_mandir}/man8/sss_groupdel.8*
%{_mandir}/man8/sss_groupmod.8*
%{_mandir}/man8/sss_groupshow.8*
%{_mandir}/man8/sss_useradd.8*
%{_mandir}/man8/sss_userdel.8*
%{_mandir}/man8/sss_usermod.8*
%{_mandir}/man8/sss_obfuscate.8*
%{_mandir}/man8/sss_cache.8*
%{_mandir}/man8/sss_debuglevel.8*

%files -n libsss_idmap
%defattr(-,root,root,-)
%doc src/sss_client/COPYING src/sss_client/COPYING.LESSER
%{_libdir}/libsss_idmap.so.*

%files -n libsss_idmap-devel
%defattr(-,root,root,-)
%doc idmap_doc/html
%{_includedir}/sss_idmap.h
%{_libdir}/libsss_idmap.so
%{_libdir}/pkgconfig/sss_idmap.pc

%files -n libipa_hbac
%defattr(-,root,root,-)
%doc src/sss_client/COPYING src/sss_client/COPYING.LESSER
%{_libdir}/libipa_hbac.so.*

%files -n libipa_hbac-devel
%defattr(-,root,root,-)
%doc hbac_doc/html
%{_includedir}/ipa_hbac.h
%{_libdir}/libipa_hbac.so
%{_libdir}/pkgconfig/ipa_hbac.pc

%files -n libipa_hbac-python
%defattr(-,root,root,-)
%{python_sitearch}/pyhbac.so

%package -n libsss_autofs
Summary: A library to allow communication between Autofs and SSSD
Group: Development/Libraries
License: LGPLv3+

%description -n libsss_autofs
A utility library to allow communication between Autofs and SSSD

%files -n libsss_sudo
%defattr(-,root,root,-)
%doc src/sss_client/COPYING src/sss_client/COPYING.LESSER
%{_libdir}/libsss_sudo.so.*

%files -n libsss_sudo-devel
%doc libsss_sudo_doc/html
%{_includedir}/sss_sudo.h
%{_libdir}/libsss_sudo.so
%{_libdir}/pkgconfig/libsss_sudo.pc

%files -n libsss_autofs
%defattr(-,root,root,-)
%doc src/sss_client/COPYING src/sss_client/COPYING.LESSER
%{_libdir}/sssd/modules/libsss_autofs.so*

%post
/sbin/ldconfig

if [ $1 -ge 1 ] ; then
    # Initial installation
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi

%preun
if [ $1 = 0 ]; then
     # Package removal, not upgrade
    /bin/systemctl --no-reload disable sssd.service > /dev/null 2>&1 || :
    /bin/systemctl stop sssd.service > /dev/null 2>&1 || :
fi

%triggerun -- sssd < %{version}-%{release}
if /sbin/chkconfig --level 3 sssd ; then
        /bin/systemctl --no-reload enable sssd.service >/dev/null 2>&1 || :
fi

if /sbin/chkconfig --level 5 sssd ; then
        /bin/systemctl --no-reload enable sssd.service >/dev/null 2>&1 || :
fi

/sbin/chkconfig --del sssd >/dev/null 2>&1 || :



%postun
/sbin/ldconfig
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # On upgrade, reload init system configuration if we changed unit files
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
    /bin/systemctl try-restart sssd.service >/dev/null 2>&1 || :
fi

%post client -p /sbin/ldconfig

%postun client -p /sbin/ldconfig

%post -n libipa_hbac -p /sbin/ldconfig

%postun -n libipa_hbac -p /sbin/ldconfig

%changelog
* Fri Jul 16 2012 Stephen Gallagher <sgallagh@redhat.com> - 1.9.0-11.beta4
- Fix broken ARM build
- Add missing DP_OPTION_TERMINATOR in AD provider options

* Wed Jul 11 2012 Jakub Hrozek <jhrozek@redhat.com> - 1.9.0-10.beta4
- Own several directories create during make install (#839782)

* Wed Jul 11 2012 Jakub Hrozek <jhrozek@redhat.com> - 1.9.0-9.beta4
- New upstream release 1.9.0 beta 4
- https://fedorahosted.org/sssd/wiki/Releases/Notes-1.9.0beta4
- Add a new AD provider to improve integration with Active Directory 2008 R2
  or later servers
- SUDO integration was completely rewritten. The new implementation works
  with multiple domains and uses an improved refresh mechanism to download
  only the necessary rules
- The IPA authentication provider now supports subdomains
- Fixed regression for setups that were setting default_tkt_enctypes
  manually by reverting a previous workaround.

* Mon Jun 25 2012 Stephen Gallagher <sgallagh@redhat.com> - 1.9.0-8.beta3
- New upstream release 1.9.0 beta 3
- https://fedorahosted.org/sssd/wiki/Releases/Notes-1.9.0beta3
- Add a new PAC responder for dealing with cross-realm Kerberos trusts
- Terminate idle connections to the NSS and PAM responders

* Wed Jun 20 2012 Stephen Gallagher <sgallagh@redhat.com> - 1.9.0-7.beta2
- Switch unicode library from libunistring to Glib
- Drop unnecessary explicit Requires on keyutils
- Guarantee that versioned Requires include the correct architecture

* Mon Jun 18 2012 Stephen Gallagher <sgallagh@redhat.com> - 1.9.0-6.beta2
- Fix accidental disabling of the DIR cache support

* Fri Jun 15 2012 Stephen Gallagher <sgallagh@redhat.com> - 1.9.0-5.beta2
- New upstream release 1.9.0 beta 2
- https://fedorahosted.org/sssd/wiki/Releases/Notes-1.9.0beta2
- Add support for the Kerberos DIR cache for storing multiple TGTs
  automatically
- Major performance enhancement when storing large groups in the cache
- Major performance enhancement when performing initgroups() against Active
  Directory
- SSSDConfig data file default locations can now be set during configure for
  easier packaging

* Tue May 29 2012 Stephen Gallagher <sgallagh@redhat.com> - 1.9.0-4.beta1
- Fix regression in endianness patch

* Tue May 29 2012 Stephen Gallagher <sgallagh@redhat.com> - 1.9.0-3.beta1
- Rebuild SSSD against ding-libs 0.3.0beta1
- Fix endianness bug in service map protocol

* Thu May 24 2012 Stephen Gallagher <sgallagh@redhat.com> - 1.9.0-2.beta1
- Fix several regressions since 1.5.x
- Ensure that the RPM creates the /var/lib/sss/mc directory
- Add support for Netscape password warning expiration control
- Rebuild against libldb 1.1.6

* Fri May 11 2012 Stephen Gallagher <sgallagh@redhat.com> - 1.9.0-1.beta1
- New upstream release 1.9.0 beta 1
- https://fedorahosted.org/sssd/wiki/Releases/Notes-1.9.0beta1
- Add native support for autofs to the IPA provider
- Support for ID-mapping when connecting to Active Directory
- Support for handling very large (> 1500 users) groups in Active Directory
- Support for sub-domains (will be used for dealing with trust relationships)
- Add a new fast in-memory cache to speed up lookups of cached data on
  repeated requests

* Thu May 03 2012 Stephen Gallagher <sgallagh@redhat.com> - 1.8.3-11
- New upstream release 1.8.3
- https://fedorahosted.org/sssd/wiki/Releases/Notes-1.8.3
- Numerous manpage and translation updates
- LDAP: Handle situations where the RootDSE isn't available anonymously
- LDAP: Fix regression for users using non-standard LDAP attributes for user
  information

* Mon Apr 09 2012 Stephen Gallagher <sgallagh@redhat.com> - 1.8.2-10
- New upstream release 1.8.2
- https://fedorahosted.org/sssd/wiki/Releases/Notes-1.8.2
- Several fixes to case-insensitive domain functions
- Fix for GSSAPI binds when the keytab contains unrelated principals
- Fixed several segfaults
- Workarounds added for LDAP servers with unreadable RootDSE
- SSH knownhostproxy will no longer enter an infinite loop preventing login
- The provided SYSV init script now starts SSSD earlier at startup and stops
  it later during shutdown
- Assorted minor fixes for issues discovered by static analysis tools

* Mon Mar 26 2012 Stephen Gallagher <sgallagh@redhat.com> - 1.8.1-9
- Don't duplicate libsss_autofs.so in two packages
- Set explicit package contents instead of globbing

* Wed Mar 21 2012 Stephen Gallagher <sgallagh@redhat.com> - 1.8.1-8
- Fix uninitialized value bug causing crashes throughout the code
- Resolves: rhbz#804783 - [abrt] Segfault during LDAP 'services' lookup

* Mon Mar 12 2012 Stephen Gallagher <sgallagh@redhat.com> - 1.8.1-7
- New upstream release 1.8.1
- Resolve issue where we could enter an infinite loop trying to connect to an
  auth server
- Fix serious issue with complex (3+ levels) nested groups
- Fix netgroup support for case-insensitivity and aliases
- Fix serious issue with lookup bundling resulting in requests never
  completing
- IPA provider will now check the value of nsAccountLock during pam_acct_mgmt
  in addition to pam_authenticate
- Fix several regressions in the proxy provider
- Resolves: rhbz#743133 - Performance regression with Kerberos authentication
                          against AD
- Resolves: rhbz#799031 - --debug option for sss_debuglevel doesn't work

* Tue Feb 28 2012 Stephen Gallagher <sgallagh@redhat.com> - 1.8.0-6
- New upstream release 1.8.0
- Support for the service map in NSS
- Support for setting default SELinux user context from FreeIPA
- Support for retrieving SSH user and host keys from LDAP (Experimental)
- Support for caching autofs LDAP requests (Experimental)
- Support for caching SUDO rules (Experimental)
- Include the IPA AutoFS provider
- Fixed several memory-corruption bugs
- Fixed a regression in group enumeration since 1.7.0
- Fixed a regression in the proxy provider
- Resolves: rhbz#741981 - Separate Cache Timeouts for SSSD
- Resolves: rhbz#797968 - sssd_be: The requested tar get is not configured is
                          logged at each login
- Resolves: rhbz#754114 - [abrt] sssd-1.6.3-1.fc16: ping_check: Process
                          /usr/sbin/sssd was killed by signal 11 (SIGSEGV)
- Resolves: rhbz#743133 - Performance regression with Kerberos authentication
                          against AD
- Resolves: rhbz#773706 - SSSD fails during autodetection of search bases for
                          new LDAP features
- Resolves: rhbz#786957 - sssd and kerberos should change the default location for create the Credential Cashes to /run/usr/USERNAME/krb5cc

* Wed Feb 22 2012 Stephen Gallagher <sgallagh@redhat.com> - 1.8.0-5.beta3
- Change default kerberos credential cache location to /run/user/<username>

* Wed Feb 15 2012 Stephen Gallagher <sgallagh@redhat.com> - 1.8.0-4.beta3
- New upstream release 1.8.0 beta 3
- https://fedorahosted.org/sssd/wiki/Releases/Notes-1.8.0beta3
- Fixed a regression in group enumeration since 1.7.0
- Fixed several memory-corruption bugs
- Finalized the ABI for the autofs support
- Fixed a regression in the proxy provider

* Fri Feb 10 2012 Petr Pisar <ppisar@redhat.com> - 1.8.0-3.beta2
- Rebuild against PCRE 8.30

* Mon Feb 06 2012 Stephen Gallagher <sgallagh@redhat.com> - 1.8.0-1.beta2
- New upstream release
- https://fedorahosted.org/sssd/wiki/Releases/Notes-1.8.0beta2
- Fix two minor manpage bugs
- Include the IPA AutoFS provider

* Mon Feb 06 2012 Stephen Gallagher <sgallagh@redhat.com> - 1.8.0-1.beta1
- New upstream release
- https://fedorahosted.org/sssd/wiki/Releases/Notes-1.8.0beta1
- Support for the service map in NSS
- Support for setting default SELinux user context from FreeIPA
- Support for retrieving SSH user and host keys from LDAP (Experimental)
- Support for caching autofs LDAP requests (Experimental)
- Support for caching SUDO rules (Experimental)

* Wed Feb 01 2012 Stephen Gallagher <sgallagh@redhat.com> - 1.7.0-5
- Resolves: rhbz#773706 - SSSD fails during autodetection of search bases for
                          new LDAP features - fix netgroups and sudo as well

* Wed Feb 01 2012 Stephen Gallagher <sgallagh@redhat.com> - 1.7.0-4
- Fixes a serious memory hierarchy bug causing unpredictable behavior in the
  LDAP provider.

* Wed Feb 01 2012 Stephen Gallagher <sgallagh@redhat.com> - 1.7.0-3
- Resolves: rhbz#773706 - SSSD fails during autodetection of search bases for
                          new LDAP features

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Thu Dec 22 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.7.0-1
- New upstream release 1.7.0
- https://fedorahosted.org/sssd/wiki/Releases/Notes-1.7.0
- Support for case-insensitive domains
- Support for multiple search bases in the LDAP provider
- Support for the native FreeIPA netgroup implementation
- Reliability improvements to the process monitor
- New DEBUG facility with more consistent log levels
- New tool to change debug log levels without restarting SSSD
- SSSD will now disconnect from LDAP server when idle
- FreeIPA HBAC rules can choose to ignore srchost options for significant
  performance gains
- Assorted performance improvements in the LDAP provider

* Mon Dec 19 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.6.4-1
- New upstream release 1.6.4
- Rolls up previous patches applied to the 1.6.3 tarball
- Fixes a rare issue causing crashes in the failover logic
- Fixes an issue where SSSD would return the wrong PAM error code for users
  that it does not recognize.

* Wed Dec 07 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.6.3-5
- Rebuild against libldb 1.1.4

* Tue Nov 29 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.6.3-4
- Resolves: rhbz#753639 - sssd_nss crashes when passed invalid UTF-8 for the
                          username in getpwnam()
- Resolves: rhbz#758425 - LDAP failover not working if server refuses
                          connections

* Thu Nov 24 2011 Jakub Hrozek <jhrozek@redhat.com> - 1.6.3-3
- Rebuild for libldb 1.1.3

* Thu Nov 10 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.6.3-2
- Resolves: rhbz#752495 - Crash when apply settings

* Fri Nov 04 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.6.3-1
- New upstream release 1.6.3
- https://fedorahosted.org/sssd/wiki/Releases/Notes-1.6.3
- Fixes a major cache performance issue introduced in 1.6.2
- Fixes a potential infinite-loop with certain LDAP layouts

* Wed Oct 26 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.2-5
- Rebuilt for glibc bug#747377

* Sun Oct 23 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.6.2-4
- Change selinux policy requirement to Conflicts: with the old version,
  rather than Requires: the supported version.

* Fri Oct 21 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.6.2-3
- Add explicit requirement on selinux-policy version to address new SBUS
  symlinks.

* Wed Oct 19 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.6.2-2
- Remove %%files reference to sss_debuglevel copied from wrong upstreeam
  spec file.

* Tue Oct 18 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.6.2-1
- Improved handling of users and groups with multi-valued name attributes
  (aliases)
- Performance enhancements
    Initgroups on RFC2307bis/FreeIPA
    HBAC rule processing
- Improved process-hang detection and restarting
- Enabled the midpoint cache refresh by default (fewer cache misses on
  commonly-used entries)
- Cleaned up the example configuration
- New tool to change debug level on the fly

* Mon Aug 29 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.6.1-1
- New upstream release 1.6.1
- https://fedorahosted.org/sssd/wiki/Releases/Notes-1.6.1
- Fixes a serious issue with LDAP connections when the communication is
  dropped (e.g. VPN disconnection, waking from sleep)
- SSSD is now less strict when dealing with users/groups with multiple names
  when a definitive primary name cannot be determined
- The LDAP provider will no longer attempt to canonicalize by default when
  using SASL. An option to re-enable this has been provided.
- Fixes for non-standard LDAP attribute names (e.g. those used by Active
  Directory)
- Three HBAC regressions have been fixed.
- Fix for an infinite loop in the deref code

* Wed Aug 03 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.6.0-2
- Build with _hardened_build macro

* Wed Aug 03 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.6.0-1
- New upstream release 1.6.0
- https://fedorahosted.org/sssd/wiki/Releases/Notes-1.6.0
- Add host access control support for LDAP (similar to pam_host_attr)
- Finer-grained control on principals used with Kerberos (such as for FAST or
- validation)
- Added a new tool sss_cache to allow selective expiring of cached entries
- Added support for LDAP DEREF and ASQ controls
- Added access control features for Novell Directory Server
- FreeIPA dynamic DNS update now checks first to see if an update is needed
- Complete rewrite of the HBAC library
- New libraries: libipa_hbac and libipa_hbac-python

* Tue Jul 05 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.5.11-2
- New upstream release 1.5.11
- https://fedorahosted.org/sssd/wiki/Releases/Notes-1.5.11
- Fix a serious regression that prevented SSSD from working with ldaps:// URIs
- IPA Provider: Fix a bug with dynamic DNS that resulted in the wrong IPv6
- address being saved to the AAAA record

* Fri Jul 01 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.5.10-1
- New upstream release 1.5.10
- https://fedorahosted.org/sssd/wiki/Releases/Notes-1.5.10
- Fixed a regression introduced in 1.5.9 that could result in blocking calls
- to LDAP

* Thu Jun 30 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.5.9-1
- New upstream release 1.5.9
- https://fedorahosted.org/sssd/wiki/Releases/Notes-1.5.9
- Support for overriding home directory, shell and primary GID locally
- Properly honor TTL values from SRV record lookups
- Support non-POSIX groups in nested group chains (for RFC2307bis LDAP
- servers)
- Properly escape IPv6 addresses in the failover code
- Do not crash if inotify fails (e.g. resource exhaustion)
- Don't add multiple TGT renewal callbacks (too many log messages)

* Fri May 27 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.5.8-1
- New upstream release 1.5.8
- https://fedorahosted.org/sssd/wiki/Releases/Notes-1.5.8
- Support for the LDAP paging control
- Support for multiple DNS servers for name resolution
- Fixes for several group membership bugs
- Fixes for rare crash bugs

* Mon May 23 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.5.7-3
- Resolves: rhbz#706740 - Orphaned links on rc0.d-rc6.d
- Make sure to properly convert to systemd if upgrading from newer
- updates for Fedora 14

* Mon May 02 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.5.7-2
- Fix segfault in TGT renewal

* Fri Apr 29 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.5.7-1
- Resolves: rhbz#700891 - CVE-2011-1758 sssd: automatic TGT renewal overwrites
-                         cached password with predicatable filename

* Wed Apr 20 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.5.6.1-1
- Re-add manpage translations

* Wed Apr 20 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.5.6-1
- New upstream release 1.5.6
- https://fedorahosted.org/sssd/wiki/Releases/Notes-1.5.6
- Fixed a serious memory leak in the memberOf plugin
- Fixed a regression with the negative cache that caused it to be essentially
- nonfunctional
- Fixed an issue where the user's full name would sometimes be removed from
- the cache
- Fixed an issue with password changes in the kerberos provider not working
- with kpasswd

* Wed Apr 20 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.5.5-5
- Resolves: rhbz#697057 - kpasswd fails when using sssd and
-                         kadmin server != kdc server
- Upgrades from SysV should now maintain enabled/disabled status

* Mon Apr 18 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.5.5-4
- Fix %%postun

* Thu Apr 14 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.5.5-3
- Fix systemd conversion. Upgrades from SysV to systemd weren't properly
- enabling the systemd service.
- Fix a serious memory leak in the memberOf plugin
- Fix an issue where the user's full name would sometimes be removed
- from the cache

* Tue Apr 12 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.5.5-2
- Install systemd unit file instead of sysv init script

* Tue Apr 12 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.5.5-1
- New upstream release 1.5.5
- https://fedorahosted.org/sssd/wiki/Releases/Notes-1.5.5
- Fixes for several crash bugs
- LDAP group lookups will no longer abort if there is a zero-length member
- attribute
- Add automatic fallback to 'cn' if the 'gecos' attribute does not exist

* Thu Mar 24 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.5.4-1
- New upstream release 1.5.4
- https://fedorahosted.org/sssd/wiki/Releases/Notes-1.5.4
- Fixes for Active Directory when not all users and groups have POSIX attributes
- Fixes for handling users and groups that have name aliases (aliases are ignored)
- Fix group memberships after initgroups in the IPA provider

* Thu Mar 17 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.5.3-2
- Resolves: rhbz#683267 - sssd 1.5.1-9 breaks AD authentication

* Fri Mar 11 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.5.3-1
- New upstream release 1.5.3
- Support for libldb >= 1.0.0

* Thu Mar 10 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.5.2-1
- New upstream release 1.5.2
- https://fedorahosted.org/sssd/wiki/Releases/Notes-1.5.2
- Fixes for support of FreeIPA v2
- Fixes for failover if DNS entries change
- Improved sss_obfuscate tool with better interactive mode
- Fix several crash bugs
- Don't attempt to use START_TLS over SSL. Some LDAP servers can't handle this
- Delete users from the local cache if initgroups calls return 'no such user'
- (previously only worked for getpwnam/getpwuid)
- Use new Transifex.net translations
- Better support for automatic TGT renewal (now survives restart)
- Netgroup fixes

* Sun Feb 27 2011 Simo Sorce <ssorce@redhat.com> - 1.5.1-9
- Rebuild sssd against libldb 1.0.2 so the memberof module loads again.
- Related: rhbz#677425

* Mon Feb 21 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.5.1-8
- Resolves: rhbz#677768 - name service caches names, so id command shows
-                         recently deleted users

* Fri Feb 11 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.5.1-7
- Ensure that SSSD builds against libldb-1.0.0 on F15 and later
- Remove .la for memberOf

* Fri Feb 11 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.5.1-6
- Fix memberOf install path

* Fri Feb 11 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.5.1-5
- Add support for libldb 1.0.0

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Feb 01 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.5.1-3
- Fix nested group member filter sanitization for RFC2307bis
- Put translated tool manpages into the sssd-tools subpackage

* Thu Jan 27 2011 Stephen Gallagher <sgallagh@redhat.com> - 1.5.1-2
- Restore Requires: cyrus-sasl-gssapi as it is not auto-detected during
- rpmbuild

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
