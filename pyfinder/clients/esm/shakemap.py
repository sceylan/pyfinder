#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import urllib.parse
import urllib.request as urllib_request
import datetime
import xmltodict
from http.client import HTTPException, IncompleteRead
from .base import ClientBase


class ShakemapEventData:
    def __init__(self, xml_content):
        self.xml_content = xml_content
        self.station_list = []
        self._parse()

    def get_creation_date(self):
        return datetime.datetime.fromtimestamp(
            int(self.xml_content['stationlist']['@created']))

    def get_stations(self):
        return self.station_list

    def _parse(self):
        self.station_list = []
        for _sta in self.xml_content['stationlist']['station']:
            # Station ID is constructed using network and station code to
            # search for the station in station list
            _id = "{}.{}".format(_sta['@netid'], _sta['@code'])

            # Each station is a dictionary of attributes, and contains
            # another list for the components
            station = {'id': _id, 'name': _sta['@name'], 'code': _sta['@code'],
                       'netid': _sta['@netid'], 'source': _sta['@source'],
                       'insttype': _sta['@insttype'], 'components': [],
                       'lat': float(_sta['@lat']),
                       'lon': float(_sta['@lon'])}

            # Each component is again a dictionary
            for _comp in _sta['comp']:
                component = {'name': _comp['@name'],
                             'depth': float(_comp['@depth']),
                             'acc': float(_comp['acc']['@value']),
                             'accflag': int(_comp['acc']['@flag']),
                             'vel': float(_comp['vel']['@value']),
                             'velflag': int(_comp['vel']['@flag']),
                             'psa03': float(_comp['psa03']['@value']),
                             'psa03flag': int(_comp['psa03']['@flag']),
                             'psa10': float(_comp['psa10']['@value']),
                             'psa10flag': int(_comp['psa10']['@flag']),
                             'psa30': float(_comp['psa30']['@value']),
                             'psa30flag': int(_comp['psa30']['@flag'])}

                station['components'].append(component)

            self.station_list.append(station)

    def __str__(self):
        _str = "ESM query station list: \n"
        for station in self.get_stations():
            _str += "{}.{} \n".format(station['netid'], station['code'])
            for component in station['components']:
                _str += "\t{}\n".format(component['name'])
        return _str


class CustomRedirectHandler(urllib_request.HTTPRedirectHandler):
    """
    Custom redirection handler to also do it for POST requests which the
    standard library does not do by default.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        """
        Copied and modified from the standard library.
        """
        # Force the same behaviour for GET, HEAD, and POST.
        m = req.get_method()
        if (not (code in (301, 302, 303, 307) and
                 m in ("GET", "HEAD", "POST"))):
            raise urllib_request.HTTPError(req.full_url, code, msg, headers,
                                           fp)

        # be conciliant with URIs containing a space
        newurl = newurl.replace(' ', '%20')
        content_headers = ("content-length", "content-type")
        newheaders = dict((k, v) for k, v in req.headers.items()
                          if k.lower() not in content_headers)

        # Also redirect the data of the request which the standard library
        # interestingly enough does not do.
        return urllib_request.Request(
            newurl, headers=newheaders,
            data=req.data,
            origin_req_host=req.origin_req_host,
            unverifiable=True)


class FDSNException(Exception):
    status_code = None

    def __init__(self, value, server_info=None):
        if server_info is not None:
            if self.status_code is None:
                value = "\n".join([value, "Detailed response of server:", "",
                                   server_info])
            else:
                value = "\n".join([value,
                                   "HTTP Status code: {}"
                                   .format(self.status_code),
                                   "Detailed response of server:",
                                   "",
                                   server_info])
        super(FDSNException, self).__init__(value)

class FDSNRedirectException(FDSNException):
    pass

class NoRedirectionHandler(urllib_request.HTTPRedirectHandler):
    """
    Handler that does not direct!
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        """
        Copied and modified from the standard library.
        """
        raise FDSNRedirectException(
            "Requests with credentials (username, password) are not being "
            "redirected by default to improve security. To force redirects "
            "and if you trust the data center, set `force_redirect` to True "
            "when initializing the Client.")


class Shakemap(ClientBase):
    """ Class for ESM shakemap web services """
    def __init__(self):
        super(Shakemap, self).__init__(agency='ESM', web_service='shakemap')

        # ESM endpoint for web services
        self.url_base = 'https://esm-db.eu/esmws/shakemap/1/query?'

    def get_supported_ws_options(self):
        """ The list of options available at the ESM shakemap web service. """
        return ['eventid', 'catalog', 'format', 'flag', 'encoding']

    def build_url(self, **options):
        """ Return the final URL with web service combined. """
        return self.url_base + urllib.parse.urlencode(options, encoding='utf-8')

    def parse(self, file_like_obj):
        xml_content = xmltodict.parse(file_like_obj, encoding='utf-8')
        return ShakemapEventData(xml_content=xml_content)

    def parse_from_file(self, file_path):
        with open(file_path, 'r') as xmlfile:
            return self.parse(xmlfile.read())

    def query(self, **options):
        self.validate_options(**options)
        url = self.build_url(**options)

        # S. Ceylan: The code below is from obspy
        # Only add the authentication handler if required.
        handlers = []
        user = None
        password = None
        if user is not None and password is not None:
            # Create an OpenerDirector for HTTP Digest Authentication
            password_mgr = urllib_request.HTTPPasswordMgrWithDefaultRealm()
            password_mgr.add_password(None, self.base_url, user, password)
            handlers.append(urllib_request.HTTPDigestAuthHandler(password_mgr))

        if (user is None and password is None) or self._force_redirect is True:
            # Redirect if no credentials are given or the force_redirect
            # flag is True.
            handlers.append(CustomRedirectHandler())
        else:
            handlers.append(NoRedirectionHandler())
        opener = urllib_request.build_opener(*handlers)

        code, url_response = self.download_url(url=url, opener=opener)
        if code != 400:
            return self.parse(file_like_obj=url_response)


    @staticmethod
    def download_url(url, opener, timeout=10, headers={}, debug=False,
                     return_string=True, data=None, use_gzip=True):
        """
        Returns a pair of tuples.

        The first one is the returned HTTP code and the second the data as
        string.

        Will return a tuple of Nones if the service could not be found.
        All encountered exceptions will get raised unless `debug=True` is
        specified.

        Performs a http GET if data=None, otherwise a http POST.
        """
        if debug is True:
            print("Downloading %s %s requesting gzip compression" % (
                url, "with" if use_gzip else "without"))
            if data:
                print("Sending along the following payload:")
                print("-" * 70)
                print(data.decode())
                print("-" * 70)
        try:
            request = urllib_request.Request(url=url, headers=headers)
            # Request gzip encoding if desired.
            if use_gzip:
                request.add_header("Accept-encoding", "gzip")
            url_obj = opener.open(request, timeout=timeout, data=data)
        # Catch HTTP errors.
        except urllib_request.HTTPError as e:
            if debug is True:
                msg = "HTTP error %i, reason %s, while downloading '%s': %s" % \
                      (e.code, str(e.reason), url, e.read())
                print(msg)
            else:
                # Without this line we will get unclosed sockets
                e.read()
            return e.code, e
        except Exception as e:
            if debug is True:
                print("Error while downloading: %s" % url)
            return None, e

        code = url_obj.getcode()

        if return_string is False:
            data = io.BytesIO(url_obj.read())
        else:
            data = url_obj.read()

        if debug is True:
            print("Downloaded %s with HTTP code: %i" % (url, code))

        return code, data

