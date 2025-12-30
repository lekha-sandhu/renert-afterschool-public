from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
from wtforms import DateField
from wtforms import DateTimeField
from wtforms.widgets import DateInput, DateTimeLocalInput



class HTML5DateField(DateField):
    """
    Custom DateField that uses HTML5 date input widget.

    Typical Usage:
    In a FlaskAdmin ModelView, override the Date <input> to use native HTML5
    Instead of crappy Bootstrap4 implementation.
    Assume you have a SQLAlchemy database model class with a DATE column,
    FlaskAdmin (v2) in CREATE/EDIT mode will render it by default as
    Bootstrap4 Date field, which is next to un-useable.
    Using this class will render it as native HTML5 <input type="date">,
    which is much better (IMHO).


    class MyModel(db.Model):
        ...
        myfield = Column(Date)

    class MyAdminView(ModelView):
        form_overrides = {
            'myfield': HTML5DateField,   ### <-- Add this.
        }
    """
    widget = DateInput()



class DateTimeLocalInputWithSeconds(DateTimeLocalInput):
    """
    This WTForm widget inherits from DateTimeLocal , which results in
       <input type="datetime-local" ...>
    However, the default behaviour for "datetime-local" is to have "step=60"
    (meaning whole minutes). This prvents settings seconds in the UI, with the
    browser showing a warning such as:
       "Please enter a valid value. The two nearest valid values are... "

    This sub-class simply adds the "step=1" HTML attribute, so that the resulting
    HTML is:
       <input type="datetime-local" step="1" ...>
    And the user is able to set the seconds.
    """
    def __call__(self, field, **kwargs):
        kwargs.setdefault('step', 1)
        return super().__call__(field, **kwargs)


class HTML5DateTimeLocalTimezonedField(DateTimeField):
    """Custom DateTimeField with configurable timezone handling.

    Server-Side (python): Always stores data as timezone-aware datetime object.
    Client-Side (html): Displays/accepts date,time WITHOUT timezone (implicitly
                        assuming it's the client's timezone.

    ---

    Typical usage in FlaskAdmin, when having a db.Model with timezone field:

    You have:

        class MyModel(db.Model):
            ...
            myfield = Column(TIMESTAMP(timezone=True))


    Then add in your flask-admin:

        from XXX.form_date_fields import HTML5DateTimeLocalTimezonedField

        class MyAdminView(ModelView):
            form_overrides = {
                'myfield': HTML5DateTimeLocalTimezonedField
            }

    ----
    Background:
    HTML standard does not have an <input> with timezone-aware date/time .
    The <input type="datetime"> was decprecated exactly for this reason,
    and replaced with <input type="datetime-local"> , to explicity note
    that the date/time is local from the user's perspective.
    ---

    NOTE: This is lazy,incomplete implementation - when this python  object(=field) is created
    on the server side, the assumed client timezone is specified once and applies to
    all users. This is fine as long as all your users are in the same know timezone.

    Better solutions would be:
    1. Store each user's preferred timezone, and convert the UI's date-time-local value
       (which does not have timezone info) to the user's preference.
       BTW, PostgreSQL has nice features for this, as it supports timezone conversion
       based on a field in a table.
       This is lots of server-side/database work.
    2. Store an <input type="datetime-local" ...> with additional <input type=hidden> with timezone info.
       Have javascript code convert it from UTC (send from the server) to the client's native timezone.
       Then when the user submits the <form>, on the server-side,
       get the client's timezone from the hidden value and convert it to UTC.
       This is lots of delicate HTML/Javascript/WTForm work.
    """
    widget = DateTimeLocalInputWithSeconds()

    def __init__(self, label=None, validators=None, client_timezone='America/Edmonton', **kwargs):
        """Initialize field with client timezone configuration.

        Args:
            label: Field label
            validators: List of validators
            client_timezone: Client timezone string (e.g., 'America/Edmonton', 'UTC') or ZoneInfo object.
                           This is the timezone assumed on the client/browser side.
            **kwargs: Additional field arguments
        """
        super().__init__(label, validators, **kwargs)

        # Accept either string or ZoneInfo object
        if isinstance(client_timezone, str):
            self.client_timezone = ZoneInfo(client_timezone)
        elif isinstance(client_timezone, ZoneInfo):
            self.client_timezone = client_timezone
        else:
            raise ValueError(f"client_timezone must be a string or ZoneInfo object, got {client_timezone}/{type(client_timezone)}")

    def process_formdata(self, valuelist):
        """Process form data from HTML5 datetime-local input.

        Interprets the naive datetime from the browser as being in client_timezone.
        """
        self.data = None
        if not valuelist or not valuelist[0]:
            return
        datetime_str = valuelist[0]
        naive_dt = datetime.fromisoformat(datetime_str)
        self.data = naive_dt.replace(tzinfo=self.client_timezone)

    def _value(self):
        """Return formatted value for rendering in client timezone."""
        if self.data:
            if self.data.tzinfo is None:
                raise ValueError(f"Field {self.name} requires timezone-aware datetime")

            # Convert to client timezone for display
            local_dt = self.data.astimezone(self.client_timezone)
            return local_dt.strftime('%Y-%m-%dT%H:%M:%S')
        return ''





##
## TODO: use this in the future...
##
def created_timestamptz_formatter_func(requested_timezone='America/Edmonton', format_string="%Y-%m-%d  %I:%M:%S%P"):

    # Accept either string or ZoneInfo object
    if isinstance(requested_timezone, str):
        target_timezone = ZoneInfo(requested_timezone)
    elif isinstance(requested_timezone, ZoneInfo):
        target_timezone = requested_timezone
    else:
        raise ValueError(f"requested_timezone must be a string or ZoneInfo object, got {client_timezone}/{type(client_timezone)}")

    # To prevent later woes,
    # Check that the format string is valid now during construction.
    now = datetime.now(timezone.utc)
    tmp = now.strftime(format_string) #If this fails, check your "format_string"

    # Create a function using the requested parameters

    def localized_timezone_formatter(dt):
        if not dt:
            return None
        if not isinstance(dt, datetime):
            raise ValueError(f"'dt' parameter must be a datetime object with timezone")
        if not dt.tzinfo:
            raise ValueError(f"'dt' parameter must be a timezone-aware datetime")

        # Convert the timestamp to a timezone that is suitable for the USER display.
        # FIXME: currently lazy solution is always Mountain-Time...
        localized_dt = dt.astimezone(target_timezone)
        return localized_dt.strftime(format_string)

    # return the customized function
    return localized_timezone_formatter
