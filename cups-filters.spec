# we build CUPS also with relro
%global _hardened_build 1

Summary: OpenPrinting CUPS filters and backends
Name:    cups-filters
Version: 1.0.32
Release: 1%{?dist}

# For a breakdown of the licensing, see COPYING file
# GPLv2:   filters: commandto*, imagetoraster, pdftops, rasterto*,
#                   imagetopdf, pstopdf, texttopdf
#         backends: parallel, serial
# GPLv2+:  filters: textonly, texttops, imagetops
# GPLv3:   filters: bannertopdf
# GPLv3+:  filters: urftopdf
# LGPLv2+:   utils: cups-browsed
# MIT:     filters: pdftoijs, pdftoopvp, pdftopdf, pdftoraster
License: GPLv2 and GPLv2+ and GPLv3 and GPLv3+ and LGPLv2+ and MIT

Group:   System Environment/Base
Url:     http://www.linuxfoundation.org/collaborate/workgroups/openprinting/pdf_as_standard_print_job_format
Source0: http://www.openprinting.org/download/cups-filters/cups-filters-%{version}.tar.xz
Source1: cups-browsed.service

Requires: cups-filters-libs%{?_isa} = %{version}-%{release}

BuildRequires: cups-devel
# pdftopdf
BuildRequires: qpdf-devel
# pdftops
BuildRequires: poppler-utils
# pdftoijs, pdftoopvp, pdftoraster
BuildRequires: poppler-devel poppler-cpp-devel
BuildRequires: libjpeg-devel
BuildRequires: libpng-devel
BuildRequires: libtiff-devel
BuildRequires: zlib-devel
# libijs
BuildRequires: ghostscript-devel
BuildRequires: freetype-devel
BuildRequires: fontconfig-devel
BuildRequires: lcms2-devel
# cups-browsed
BuildRequires: avahi-devel avahi-glib-devel
BuildRequires: systemd

# Make sure we get postscriptdriver tags.
BuildRequires: python-cups

# autogen.sh
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: libtool

Requires: cups-filesystem
Requires: poppler-utils

# cups-browsed
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%package libs
Summary: OpenPrinting CUPS filters and backends - cupsfilters and fontembed libraries
Group:   System Environment/Libraries
# LGPLv2: libcupsfilters
# MIT:    libfontembed
License: LGPLv2 and MIT

%package devel
Summary: OpenPrinting CUPS filters and backends - development environment
Group:   Development/Libraries
License: LGPLv2 and MIT
Requires: cups-filters-libs%{?_isa} = %{version}-%{release}

%description
Contains backends, filters, and other software that was
once part of the core CUPS distribution but is no longer maintained by
Apple Inc. In addition it contains additional filters developed
independently of Apple, especially filters for the PDF-centric printing
workflow introduced by OpenPrinting.

%description libs
This package provides cupsfilters and fontembed libraries.

%description devel
This is the development package for OpenPrinting CUPS filters and backends.

%prep
%setup -q

%build
# work-around Rpath
./autogen.sh

# --with-pdftops=pdftops - use Poppler instead of Ghostscript (see README)
# --with-rcdir=no - don't install SysV init script
%configure --disable-static \
           --disable-silent-rules \
           --with-pdftops=pdftops \
           --with-browseremoteprotocols=DNSSD,CUPS \
           --with-rcdir=no

make %{?_smp_mflags}

%install
make install DESTDIR=%{buildroot}

# https://fedoraproject.org/wiki/Packaging_tricks#With_.25doc
mkdir __doc
mv  %{buildroot}%{_datadir}/doc/cups-filters/* __doc
rm -rf %{buildroot}%{_datadir}/doc/cups-filters

# Don't ship libtool la files.
rm -f %{buildroot}%{_libdir}/lib*.la

# Not sure what is this good for.
rm -f %{buildroot}%{_bindir}/ttfread

# systemd unit file
mkdir -p %{buildroot}%{_unitdir}
install -p -m 644 %{SOURCE1} %{buildroot}%{_unitdir}

%post
%systemd_post cups-browsed.service

# Initial installation
if [ $1 -eq 1 ] ; then
    IN=%{_sysconfdir}/cups/cupsd.conf
    OUT=%{_sysconfdir}/cups/cups-browsed.conf
    keyword=BrowsePoll

    # We can remove this after few releases, it's just for the introduction of cups-browsed.
    if [ -f "$OUT" ]; then
        echo -e "\nNOTE: This file is not part of CUPS. You need to start&enable cups-browsed service." >> "$OUT"
    fi

    # move BrowsePoll from cupsd.conf to cups-browsed.conf
    if [ -f "$IN" ] && grep -iq ^$keyword "$IN"; then
        if ! grep -iq ^$keyword "$OUT"; then
            (cat >> "$OUT" <<EOF

# Settings automatically moved from cupsd.conf by RPM package:
EOF
            ) || :
            (grep -i ^$keyword "$IN" >> "$OUT") || :
            #systemctl enable cups-browsed.service >/dev/null 2>&1 || :
        fi
        sed -i -e "s,^$keyword,#$keyword directive moved to cups-browsed.conf\n#$keyword,i" "$IN" || :
    fi
fi

%preun
%systemd_preun cups-browsed.service

%postun
%systemd_postun_with_restart cups-browsed.service 

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig


%files
%doc __doc/README __doc/AUTHORS __doc/NEWS
%config(noreplace) %{_sysconfdir}/cups/cups-browsed.conf
%config(noreplace) %{_sysconfdir}/fonts/conf.d/99pdftoopvp.conf
%attr(0755,root,root) %{_cups_serverbin}/filter/*
%attr(0755,root,root) %{_cups_serverbin}/backend/parallel
# Serial backend needs to run as root (bug #212577#c4).
%attr(0700,root,root) %{_cups_serverbin}/backend/serial
%{_datadir}/cups/banners
%{_datadir}/cups/charsets
%{_datadir}/cups/data/*
%{_datadir}/cups/drv/cupsfilters.drv
%{_datadir}/cups/mime/cupsfilters.types
%{_datadir}/cups/mime/cupsfilters.convs
%{_datadir}/ppd/cupsfilters
%{_sbindir}/cups-browsed
%{_unitdir}/cups-browsed.service

%files libs
%doc __doc/COPYING fontembed/README
%attr(0755,root,root) %{_libdir}/libcupsfilters.so.*
%attr(0755,root,root) %{_libdir}/libfontembed.so.*

%files devel
%{_includedir}/cupsfilters
%{_includedir}/fontembed
%{_libdir}/pkgconfig/libcupsfilters.pc
%{_libdir}/pkgconfig/libfontembed.pc
%{_libdir}/libcupsfilters.so
%{_libdir}/libfontembed.so

%changelog
* Thu Apr 04 2013 Fridolin Pokorny <fpokorny@redhat.com> - 1.0.32-1
- 1.0.32

* Fri Mar 29 2013 Jiri Popelka <jpopelka@redhat.com> - 1.0.31-3
- add note to cups-browsed.conf

* Thu Mar 28 2013 Jiri Popelka <jpopelka@redhat.com> - 1.0.31-2
- check cupsd.conf existence prior to grepping it (#928816)

* Fri Mar 22 2013 Jiri Popelka <jpopelka@redhat.com> - 1.0.31-1
- 1.0.31

* Tue Mar 19 2013 Jiri Popelka <jpopelka@redhat.com> - 1.0.30-4
- revert previous change

* Wed Mar 13 2013 Jiri Popelka <jpopelka@redhat.com> - 1.0.30-3
- don't ship banners for now (#919489)

* Tue Mar 12 2013 Jiri Popelka <jpopelka@redhat.com> - 1.0.30-2
- move BrowsePoll from cupsd.conf to cups-browsed.conf in %%post

* Fri Mar 08 2013 Jiri Popelka <jpopelka@redhat.com> - 1.0.30-1
- 1.0.30: CUPS browsing and broadcasting in cups-browsed

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.29-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sat Jan 19 2013 Rex Dieter <rdieter@fedoraproject.org> 1.0.29-3
- backport upstream buildfix for poppler-0.22.x

* Fri Jan 18 2013 Adam Tkac <atkac redhat com> - 1.0.29-2
- rebuild due to "jpeg8-ABI" feature drop

* Thu Jan 03 2013 Jiri Popelka <jpopelka@redhat.com> 1.0.29-1
- 1.0.29

* Wed Jan 02 2013 Jiri Popelka <jpopelka@redhat.com> 1.0.28-1
- 1.0.28: cups-browsed daemon and service

* Thu Nov 29 2012 Jiri Popelka <jpopelka@redhat.com> 1.0.25-1
- 1.0.25

* Fri Sep 07 2012 Jiri Popelka <jpopelka@redhat.com> 1.0.24-1
- 1.0.24

* Wed Aug 22 2012 Jiri Popelka <jpopelka@redhat.com> 1.0.23-1
- 1.0.23: old pdftopdf removed

* Tue Aug 21 2012 Jiri Popelka <jpopelka@redhat.com> 1.0.22-1
- 1.0.22: new pdftopdf (uses qpdf instead of poppler)

* Wed Aug 08 2012 Jiri Popelka <jpopelka@redhat.com> 1.0.20-4
- rebuild

* Thu Aug 02 2012 Jiri Popelka <jpopelka@redhat.com> 1.0.20-3
- commented multiple licensing breakdown (#832130)
- verbose build output

* Thu Aug 02 2012 Jiri Popelka <jpopelka@redhat.com> 1.0.20-2
- BuildRequires: poppler-cpp-devel (to build against poppler-0.20)

* Mon Jul 23 2012 Jiri Popelka <jpopelka@redhat.com> 1.0.20-1
- 1.0.20

* Tue Jul 17 2012 Jiri Popelka <jpopelka@redhat.com> 1.0.19-1
- 1.0.19

* Wed May 30 2012 Jiri Popelka <jpopelka@redhat.com> 1.0.18-1
- initial spec file
