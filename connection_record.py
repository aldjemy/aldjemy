class _ConnectionRecord(object):

    """Internal object which maintains an individual DBAPI connection
    referenced by a :class:`_pool.Pool`.
    The :class:`._ConnectionRecord` object always exists for any particular
    DBAPI connection whether or not that DBAPI connection has been
    "checked out".  This is in contrast to the :class:`._ConnectionFairy`
    which is only a public facade to the DBAPI connection while it is checked
    out.
    A :class:`._ConnectionRecord` may exist for a span longer than that
    of a single DBAPI connection.  For example, if the
    :meth:`._ConnectionRecord.invalidate`
    method is called, the DBAPI connection associated with this
    :class:`._ConnectionRecord`
    will be discarded, but the :class:`._ConnectionRecord` may be used again,
    in which case a new DBAPI connection is produced when the
    :class:`_pool.Pool`
    next uses this record.
    The :class:`._ConnectionRecord` is delivered along with connection
    pool events, including :meth:`_events.PoolEvents.connect` and
    :meth:`_events.PoolEvents.checkout`, however :class:`._ConnectionRecord`
    still
    remains an internal object whose API and internals may change.
    .. seealso::
        :class:`._ConnectionFairy`
    """

    def __init__(self, pool: Pool, connect: bool = True):
        self.fresh = False
        self.fairy_ref = None
        self.starttime = 0
        self.dbapi_connection = None

        self.__pool = pool
        if connect:
            self.__connect()
        self.finalize_callback = deque()

    fresh = False

    fairy_ref = None

    starttime = None

    dbapi_connection = None
    """A reference to the actual DBAPI connection being tracked.
    May be ``None`` if this :class:`._ConnectionRecord` has been marked
    as invalidated; a new DBAPI connection may replace it if the owning
    pool calls upon this :class:`._ConnectionRecord` to reconnect.
    For adapted drivers, like the Asyncio implementations, this is a
    :class:`.AdaptedConnection` that adapts the driver connection
    to the DBAPI protocol.
    Use :attr:`._ConnectionRecord.driver_connection` to obtain the
    connection objected returned by the driver.
    .. versionadded:: 1.4.24
    """

    @property
    def driver_connection(self):
        """The connection object as returned by the driver after a connect.
        For normal sync drivers that support the DBAPI protocol, this object
        is the same as the one referenced by
        :attr:`._ConnectionRecord.dbapi_connection`.
        For adapted drivers, like the Asyncio ones, this is the actual object
        that was returned by the driver ``connect`` call.
        As :attr:`._ConnectionRecord.dbapi_connection` it may be ``None``
        if this :class:`._ConnectionRecord` has been marked as invalidated.
        .. versionadded:: 1.4.24
        """

        if self.dbapi_connection is None:
            return None
        else:
            return self.__pool._dialect.get_driver_connection(
                self.dbapi_connection
            )

    @property
    def connection(self):
        """An alias to :attr:`._ConnectionRecord.dbapi_connection`.
        This alias is deprecated, please use the new name.
        .. deprecated:: 1.4.24
        """
        return self.dbapi_connection

    @connection.setter
    def connection(self, value):
        self.dbapi_connection = value

    _soft_invalidate_time = 0

    @util.memoized_property
    def info(self):
        """The ``.info`` dictionary associated with the DBAPI connection.
        This dictionary is shared among the :attr:`._ConnectionFairy.info`
        and :attr:`_engine.Connection.info` accessors.
        .. note::
            The lifespan of this dictionary is linked to the
            DBAPI connection itself, meaning that it is **discarded** each time
            the DBAPI connection is closed and/or invalidated.   The
            :attr:`._ConnectionRecord.record_info` dictionary remains
            persistent throughout the lifespan of the
            :class:`._ConnectionRecord` container.
        """
        return {}

    @util.memoized_property
    def record_info(self):
        """An "info' dictionary associated with the connection record
        itself.
        Unlike the :attr:`._ConnectionRecord.info` dictionary, which is linked
        to the lifespan of the DBAPI connection, this dictionary is linked
        to the lifespan of the :class:`._ConnectionRecord` container itself
        and will remain persistent throughout the life of the
        :class:`._ConnectionRecord`.
        .. versionadded:: 1.1
        """
        return {}

    @classmethod
    def checkout(cls, pool):
        rec = pool._do_get()
        try:
            dbapi_connection = rec.get_connection()
        except BaseException as err:
            with util.safe_reraise():
                rec._checkin_failed(err, _fairy_was_created=False)

            # never called, this is for code linters
            raise

        echo = pool._should_log_debug()
        fairy = _ConnectionFairy(dbapi_connection, rec, echo)

        rec.fairy_ref = ref = weakref.ref(
            fairy,
            lambda ref: _finalize_fairy
            and _finalize_fairy(
                None, rec, pool, ref, echo, transaction_was_reset=False
            ),
        )
        _strong_ref_connection_records[ref] = rec
        if echo:
            pool.logger.debug(
                "Connection %r checked out from pool", dbapi_connection
            )
        return fairy

    def _checkin_failed(self, err, _fairy_was_created=True):
        self.invalidate(e=err)
        self.checkin(
            _fairy_was_created=_fairy_was_created,
        )

    def checkin(self, _fairy_was_created=True):
        if self.fairy_ref is None and _fairy_was_created:
            # _fairy_was_created is False for the initial get connection phase;
            # meaning there was no _ConnectionFairy and we must unconditionally
            # do a checkin.
            #
            # otherwise, if fairy_was_created==True, if fairy_ref is None here
            # that means we were checked in already, so this looks like
            # a double checkin.
            util.warn("Double checkin attempted on %s" % self)
            return
        self.fairy_ref = None
        connection = self.dbapi_connection
        pool = self.__pool
        while self.finalize_callback:
            finalizer = self.finalize_callback.pop()
            finalizer(connection)
        if pool.dispatch.checkin:
            pool.dispatch.checkin(connection, self)

        pool._return_conn(self)

    @property
    def in_use(self):
        return self.fairy_ref is not None

    @property
    def last_connect_time(self):
        return self.starttime

    def close(self):
        if self.dbapi_connection is not None:
            self.__close()

    def invalidate(self, e=None, soft=False):
        """Invalidate the DBAPI connection held by this
        :class:`._ConnectionRecord`.
        This method is called for all connection invalidations, including
        when the :meth:`._ConnectionFairy.invalidate` or
        :meth:`_engine.Connection.invalidate` methods are called,
        as well as when any
        so-called "automatic invalidation" condition occurs.
        :param e: an exception object indicating a reason for the
          invalidation.
        :param soft: if True, the connection isn't closed; instead, this
          connection will be recycled on next checkout.
         .. versionadded:: 1.0.3
        .. seealso::
            :ref:`pool_connection_invalidation`
        """
        # already invalidated
        if self.dbapi_connection is None:
            return
        if soft:
            self.__pool.dispatch.soft_invalidate(
                self.dbapi_connection, self, e
            )
        else:
            self.__pool.dispatch.invalidate(self.dbapi_connection, self, e)
        if e is not None:
            self.__pool.logger.info(
                "%sInvalidate connection %r (reason: %s:%s)",
                "Soft " if soft else "",
                self.dbapi_connection,
                e.__class__.__name__,
                e,
            )
        else:
            self.__pool.logger.info(
                "%sInvalidate connection %r",
                "Soft " if soft else "",
                self.dbapi_connection,
            )

        if soft:
            self._soft_invalidate_time = time.time()
        else:
            self.__close(terminate=True)
            self.dbapi_connection = None

    def get_connection(self):
        recycle = False

        # NOTE: the various comparisons here are assuming that measurable time
        # passes between these state changes.  however, time.time() is not
        # guaranteed to have sub-second precision.  comparisons of
        # "invalidation time" to "starttime" should perhaps use >= so that the
        # state change can take place assuming no measurable  time has passed,
        # however this does not guarantee correct behavior here as if time
        # continues to not pass, it will try to reconnect repeatedly until
        # these timestamps diverge, so in that sense using > is safer.  Per
        # https://stackoverflow.com/a/1938096/34549, Windows time.time() may be
        # within 16 milliseconds accuracy, so unit tests for connection
        # invalidation need a sleep of at least this long between initial start
        # time and invalidation for the logic below to work reliably.
        if self.dbapi_connection is None:
            self.info.clear()
            self.__connect()
        elif (
            self.__pool._recycle > -1
            and time.time() - self.starttime > self.__pool._recycle
        ):
            self.__pool.logger.info(
                "Connection %r exceeded timeout; recycling",
                self.dbapi_connection,
            )
            recycle = True
        elif self.__pool._invalidate_time > self.starttime:
            self.__pool.logger.info(
                "Connection %r invalidated due to pool invalidation; "
                + "recycling",
                self.dbapi_connection,
            )
            recycle = True
        elif self._soft_invalidate_time > self.starttime:
            self.__pool.logger.info(
                "Connection %r invalidated due to local soft invalidation; "
                + "recycling",
                self.dbapi_connection,
            )
            recycle = True

        if recycle:
            self.__close(terminate=True)
            self.info.clear()

            self.__connect()
        return self.dbapi_connection

    def _is_hard_or_soft_invalidated(self):
        return (
            self.dbapi_connection is None
            or self.__pool._invalidate_time > self.starttime
            or (self._soft_invalidate_time > self.starttime)
        )

    def __close(self, terminate=False):
        self.finalize_callback.clear()
        if self.__pool.dispatch.close:
            self.__pool.dispatch.close(self.dbapi_connection, self)
        self.__pool._close_connection(
            self.dbapi_connection, terminate=terminate
        )
        self.dbapi_connection = None

    def __connect(self) -> None:
        pool = self.__pool

        # ensure any existing connection is removed, so that if
        # creator fails, this attribute stays None
        self.dbapi_connection = None
        try:
            self.starttime = time.time()
            self.dbapi_connection = connection = pool._invoke_creator(self)
            pool.logger.debug("Created new connection %r", connection)
            self.fresh = True
        except BaseException as e:
            with util.safe_reraise():
                pool.logger.debug("Error on connect(): %s", e)
        else:
            # in SQLAlchemy 1.4 the first_connect event is not used by
            # the engine, so this will usually not be set
            if pool.dispatch.first_connect:
                pool.dispatch.first_connect.for_modify(
                    pool.dispatch
                ).exec_once_unless_exception(self.dbapi_connection, self)

            # init of the dialect now takes place within the connect
            # event, so ensure a mutex is used on the first run
            pool.dispatch.connect.for_modify(pool.dispatch)._exec_w_sync_on_first_run(
                self.dbapi_connection, self
            )
