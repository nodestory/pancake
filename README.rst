pancake
=======
.. image:: https://codeship.com/projects/b9987b60-8e77-0132-3248-6a5ca7220068/status
    :target: https://codeship.com/projects/60954)

Installation
------------
The following service dependencies need to be installed:
 * MongoDB
 * Redis-Server

To install python dependencies for development::

    make config-develop

To run tests::

    make test

To run the server::

    python pancacke/app.py

This runs the server at http://localhost:8080. Part of the API docs can be
found at http://localhost:8080/docs. Note only the following endpoints have
correct documentation there right now:
 * `/contact`
 * `/media`
 * `/event`
 * `/subscription`
 * `/acknowledgement`

The rest are erroneous due to bugs in the `Eve-Doc` library which generated
them..

Admin interface is available at http://localhost:8080/admin , no auth required.

Additional documentation can be built by running::

    make docs


How does it work
----------------
Pancake receives events and decides whether to send notifications to users.
`Contact` represents a user while `Media` represents a way to notify the user,
like SMS and Email. `Event` can be anything interesting in the system.

By default, no notification is sent. To receive notifications, users need to
create subscriptions to express their interest. A notification may be sent only
when a matching subscription is found for an event.

A subscription matches an event if:
 * subscription.user_id == event.user_id
 * subscription.event == event.name
 * subscription.level <= event.level
 * subscription.start_time <= event.time < subscription.end_time

A notification is sent via the `media` of the matching subscription.
The media does not necessarily belong to the user of the event, i.e., John can
subscribe to Paul's events with his Email. Subscription permission is out of
the scope of Pancake and shall be managed by other systems.

In addition, a subscription can be muted by an `acknowledgement`. An
acknowledgement is almost the same as a subscription, only that
it mutes instead of invoking a notification. Think of subscriptions as
notification white-lists and acknowledgements as black-lists.

If both matching subscriptions and acknowledgements are found for an event, the
acknowledgements takes precedence, i.e., notifications are muted.

Finally, each user has a global configuration, limiting how many notifications
in total can be sent to him during some period of time. If this limit is
reached, no notification is sent until the limit resets at the next period.

Notification Templates
----------------------
Pancake uses notification service to actually send the notifications.
The content of the notifications is rendered with templates. Each contact
has a `template` attribute, which is used to determine which templates to use
when rendering different notifications.

Currently Email and SMS notifications are supported.

For Email notifications, the following templates are used:
* `%{contact.template}s.subject` renders the subject of the email
* `%{contact.template}s.html` renders the html content of the email
* `%{contact.template}s.txt` renders the txt content of the email

For SMS notifications, the template `%{contact.template}s.sms` is used to
render the content of the SMS.

All those templates but be defined in the notification service beforehand,
otherwise notifications cannot be sent successfully. The template attribute
can be set to any string.
For example, the organization of the user or his name. It depends
on how much you want to personalize the content of the notifications.
Of course, the more personalized, the more templates you need to create.


Cookbook
--------
 * Only send notifications according to a pre-defined schedule, i.e., 8 AM. to
   8 PM. on weekdays and no notifications during weekend, for the whole Feb.

   Create subscriptions for all weekdays in Feb. Note that the start time and
   end time of a subscription/acknowledgement are the exact time of a date.
   They don't repeat in any way.

 * Send notifications in periods that no subscriptions are defined by previous
   schedule.

   Create subscriptions in these periods..

 * Mute notifications in periods that subscriptions are defined by previous
   schedule.

   Create acknowledgements in these periods..
