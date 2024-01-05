# -*- coding: utf-8 -*-
""" Classes to manage HTTP requests and responses. """

import urllib.request as urllib_request

class WebServiceRedirectException(Exception):
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
        super(WebServiceRedirectException, self).__init__(value)


class NoRedirectionHandler(urllib_request.HTTPRedirectHandler):
    """ Handler that does not direct """
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        """ Copied and modified from the standard library. """
        raise WebServiceRedirectException(
            "Requests with credentials (username, password) are not being "
            "redirected by default to improve security. To force redirects "
            "and if you trust the data center, set `force_redirect` to True "
            "when initializing the Client.")

class CustomRedirectHandler(urllib_request.HTTPRedirectHandler):
    """
    Custom redirection handler to also do it for POST requests which the
    standard library does not do by default.
    """
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        """ Copied and modified from the standard library. """
        # Force the same behaviour for GET, HEAD, and POST.
        m = req.get_method()
        if (not (code in (301, 302, 303, 307) and
                 m in ("GET", "HEAD", "POST"))):
            raise urllib_request.HTTPError(
                req.full_url, code, msg, headers, fp)

        # be conciliant with URIs containing a space
        newurl = newurl.replace(' ', '%20')
        content_headers = ("content-length", "content-type")
        newheaders = dict((k, v) for k, v in req.headers.items()
                          if k.lower() not in content_headers)

        # Also redirect the data of the request which the 
        # standard library interestingly enough does not do.
        return urllib_request.Request(
            newurl, headers=newheaders,
            data=req.data,
            origin_req_host=req.origin_req_host,
            unverifiable=True)
