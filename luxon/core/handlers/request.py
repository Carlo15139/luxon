# -*- coding: utf-8 -*-
# Copyright (c) 2018 Christiaan Frans Rademan.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holders nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.
from luxon import g
from luxon.core.auth import Auth
from luxon.exceptions import AccessDeniedError
from luxon.utils.unique import request_id
from luxon import policy as policy_engine
from luxon.structs.container import Container


class RequestBase(object):
    """Request Base class representing a request.
    """

    __slots__ = (
        '_cached_id',
        '_cached_auth',
        '_cached_policy',
        '_context',
    )

    def __init__(self):
        self._cached_id = None
        self._cached_auth = None
        self._cached_policy = None
        self._context = Container()

    def __repr__(self):
        return '<%s: %s %r>' % (self.__class__.__name__, self.method,
                                self.route)

    def __str__(self):
        return '<%s: %s %r>' % (self.__class__.__name__, self.method,
                                self.route)

    @property
    def id(self):
        if self._cached_id is None:
            self._cached_id = request_id()
        return self._cached_id

    @property
    def context(self):
        return self._context

    @property
    def credentials(self):
        """Credentials"""
        if self._cached_auth is None:
            expire = g.app.config.getint('tokens', 'expire', fallback=3600)
            self._cached_auth = Auth(expire=expire)
            if self.user_token:
                try:
                    self.credentials.token = self.user_token
                    self.log['USER-ID'] = self._cached_auth.user_id
                except AccessDeniedError as e:
                    self.user_token = None
                    self.session.clear()
                    raise

        return self._cached_auth

    @property
    def user_token(self):
        return None

    @property
    def context_domain(self):
        return None

    @property
    def context_tenant_id(self):
        return None

    @property
    def policy(self):
        if self._cached_policy is None:
            self._cached_policy = policy_engine(req=self, g=g)

        return self._cached_policy
