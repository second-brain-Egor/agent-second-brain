So here you can see that I've got this
Grockbot set up to wake up about every
30 minutes and place trades for me in
the stock market or sell them or
something like that. Except for this
routine isn't firing every 30 minutes.
It's actually firing when a web hook
fires. Which means that this Grockbot
wakes up whenever it receives an email
and it's got its own email account. So
what I'm actually doing here is I have
GBD6 Astra doing the research and then
sending over an email to this Grockbot
called trader and actually saying hey
place this trade or hey sell this. You
can also see that I get these
notifications twice a day, once in the
morning and once at night, which is my
Grockbot called Nat, which is this one
right here, who is cleaning up my actual
inbox. So, this runs every day at 6:45
a.m. and 6:45 p.m. And you can see that
this has been running for me for a while
now. It basically just keeps my inbox
completely clean. It marks things as red
and it organizes every single email into
either newsletters, outreach, primary,
or urgent. So, by the end of this video,
you will be able to have both of these
things set up so that you can manage
your own inbox and you can also give
your Grockbots their own email to
manage. So, let's get straight into it.
Okay, so first of all, let's just start
with the super super easy one, which is
the inbox manager. You can see I've
named this one Nat. And this one took
almost no time to set up. As you can
see, not very long conversation at all.
I created a new bot. So, you'd come in
here and click create new bot. And then
what you're going to do is just
basically tell this bot what to do. So,
this was my prompt. I said, "Hey, you
are my email management agent. Your name
is Natie. I need you to help me keep my
inbox clean." So what I'm thinking is I
want these different labels. I want
primary, I want notifications, I want
outreach, and I want urgent. So I was
basically just telling it these are kind
of the four categories and here are
typically what fits into each category.
So notifications are like from my bank
or from services that I'm signed up for.
You know, having all those notifications
in one spot. Outreach is when people are
reaching out to me if they want to
sponsor a video or if they want to just
like pitch an idea or something. That's
outreach. And primary and urgent are the
ones that I mainly care to actually look
at. these two. I said, "Hey, just go
ahead and mark those as red right away."
So, I just want to know if it's
communication that I'm actively having
with people or if it's some sort of
urgent bill or invoice or something like
that. So, the first step here is to
really just get clear on your routing
rules. What do you want to happen when
an email hits the inbox? How do you want
it to be classified? And you can see
here what it did is it said, "Okay,
actually, I want to add newsletters as
well because you do get quite a few
newsletters." So, I said, "Yep, let's do
that." It locked it in. And then all you
have to do from there is just add your
actual account. So whether that's Gmail
or Outlook or whatever it is, go to the
marketplace and then just search for it.
If it's Gmail, you can add one here. And
you can also add multiple accounts. So
if you have different inboxes you want
to manage, you can add all of them. Just
make sure you're giving them a label. So
I should probably label this one Nate
Maine. And then if I wanted to add other
inboxes, I could add those as well and
set up different agents to manage the
different inboxes. And the cool part is,
of course, you can have every one of
these wakeups message you. So, I said,
"What I want you to do is do this twice
a day and then send me a ClickUp DM so
that I can actually just get a quick
notification on my phone that, hey, you
know, this email came through. Here's
urgent ones. Here's what you should
probably respond to, blah blah blah."
And that's super simple. It created the
routine and now I can just see exactly
what it's supposed to do. It labels
them. It doesn't draft anything for me.
It literally just labels and marks as
red and stuff like that. And now I can
see every time it runs and I get a
ClickUp message in my ClickUp. And I
also told it to add a label to the
bottom of the ClickUp message that says
sent by Nat. So yeah, this one's super
super simple. It's so easy to set up.
Literally will take you 5 to 10 minutes.
So go get this set up and then let me
show you how we actually give a Crockpot
their own email to wake up to. All
right, guys. Real quick, huge thanks to
Clay for sponsoring this part of the
video. Now, one of the most common
questions I get is where to actually
find leads for cold outreach and how to
learn enough about these people to send
them something that they'll actually
open. Because a raw list of names
doesn't tell you things like if they
have decision-making authority and how
to reach them or what they even care
about. So, Clay is a data enrichment and
orchestration platform. And it gives you
access to over 250 data providers and AI
research tools all in one spot. So,
instead of asking your agent to dig up
whatever it can find online, you can
research a whole list at once and pull
the right person to contact, their work
email, and the size of their company.
And if one provider comes back empty,
Clay just moves down the list to the
next one until it gets you a result. And
what's really cool is the logic you
build stays attached to your data. So,
the same steps can be run again and
again on every new lead that you add.
And you can see each step that it took,
like which provider every value came
from and what it cost you. You can build
all of this from cloud code with the
Clay CLI, which is what I'm doing right
here. So try Clay using the link in the
description and you'll get 2,000 free
credits. Now, let's get back to the
video. So the way we do this is we use a
service called Agent Mail and it's
completely free to start if you want to
just create an account here and log in
and then I'll show you what to do next.
So you can see here right away the
dashboard shows us basically like some
email deliverability stats. So, this is
how many our Grockbot has sent and
received right here. Now, what you're
going to do is you're going to go to
inboxes, and you can see this is the
email that this Grockbot is connected
to. His name is Bull the Trading Bot
from when I did the trading challenge
previously. But on this free plan, you
can see that it says I have two
remaining emails, which means I can make
one more right now to show you guys. So,
what I'm going to do is click on create
inbox. This username right here is just
going to be YouTube and it's going to go
to an agentmail.to
default domain. You could connect this
to something custom if you'd like to,
but right now I'm just going to leave it
as the default. And then I'm just going
to go ahead and create this inbox. Okay,
I had to change the name to YouTube test
because it said that YouTube was taken.
So now we have this. Now what's going to
happen here is we can actually see the
inbox. So I can see all the emails and I
could respond to them in here. So if I
actually want to go back to my other
inbox, you can see that I can see all
the messages that are coming from my
other email account that's sending
messages to Crockbot. Now you're going
to go back into Crockbot. You're going
to go to the marketplace and you're
going to connect agent mail, which is a
native connector in here, which is
awesome. You'll click on agent mail and
you'll go ahead and add an account. I
obviously have one here, so I'm just
going to call this one bull. But then if
you don't have one, you will go ahead
and add an account. I'm just going to
call this the test. And then you're
going to authorize. And when you
authorize, this will basically just pull
in the ability for you to log in. So I'm
going to click allow. And then it
completely connects to your agent mail.
Okay. So now we have connected to test.
We are going to go ahead and create a
new agent. So, I'm going to create a new
bot. I'm just going to say,
"Hey, you are Stephanie. You are my
assistant. Just hold tight and I'll tell
you what you need to do." So, random
prompt, threw that off. And what we're
going to do now is we need to set up a
routine. So, we need to actually tell
it, "Okay, you wake up when you receive
emails." So, I'm going to say, "All
right, Stephanie, your job is to respond
to emails, and you're kind of like
Nate's assistant. So, I'm going to give
you an email address, and that's how
you're going to respond. It's going to
be connected through agent mail, and
you're going to use the agent mail um
credential that I just connected. Now,
what I want you to do is create a
routine. And this routine is going to be
a web hook. And then I'm going to
connect that web hook to agent mail so
that when you
um receive an email, that's when you
should basically wake up. And if you've
never actually heard of a web hook
before, just ask Glido, what is a super
simple explanation of a web hook? and it
will tell you right here. A web hook is
a way for one app to automatically send
a small message to another app whenever
a specific event happens like a new
comment posted or in our case a new
email hit the inbox. Cool. So now this
routine is live. I can go ahead and
click on it and you can see that we have
this button down here that says when a
web hook fires and actually I just
refreshed and I had a new update to
install for Grockbot. And now you can
see when you click on the routine it
looks a little bit different. So if your
screen looked different from what I was
showing earlier that's why it's just an
update to Grockbot. Now, what we need to
do is we need to be able to actually see
the web hook address and the key that we
need for this web hook because we have
to give Grockbot and agent mail
permission to talk through the web hook.
It's it's more than just that
authorization we did earlier. Now, in
the previous update or the previous
version, you used to be able to click on
this and it would show you that
information, but I'm not seeing it now.
All right, so now it is the next day. I
had to wait for the desktop app to come
up with an update because I knew that
was a bug. And now that I've updated the
desktop app, which by the way, if you
need to, it'll be right down here.
there'll be like a little cloud or you
click into here and it'll say update.
And now that I've updated this, this
works as expected. This is no longer
buggy. And we can see that we have our
web hook address and we have our actual
key. So I'm going to show you exactly
what we do with this. But basically, we
have to give this to agent mail so that
agent mail is allowed to send basically
a notification to Stephanie, this inbox
agent right here, when there is a new
inbox or a new email. So I'm going to go
back over to agent mail. Here we are.
These are the two inboxes. And then what
we're going to do is we're going to go
to the web hooks on the left. So you're
going to click on web hooks. You can see
that I've already got one set up right
here. And this is for my trader and
Grockbot. You can see this endpoint
sends emails to trader and Grockbot. So
what we're going to do here is we're
going to click on add endpoint. We're
going to put in the URL. So that's where
you go back into Grock. You're going to
grab this URL right here and copy it.
And then you're going to paste that
right into there. The description. So
this is a test web hook for Stephanie
inside of Grockbot. So that is what we
got there. And then for the subscribing
to events, this basically means like
what events are going to actually
trigger this web hook, trigger a message
being sent to this endpoint. So what we
need to do here is you can look through
the event catalog, but um that will take
you a different page. So I'm not going
to look at the catalog. You can scroll
through here. Basically, all that we
want to do is we just want to check the
messages once. So this is just going to
allow us to you know when a message is
received actually wake up Stephanie.
Now, if you wanted to go through this
and, you know, click info and and get
more specific, you could. But I'm just
going to select messages. And then we
are going to go ahead and hit this
button, which this UI is a little bit
buggy. We should be able to hit save.
And now what we need to do is we need to
add the key. So the way that we add the
key is we go to advanced and then right
here, custom headers. So if you go back
into Grockbot, what you can see is that
the header is authorization colon bearer
space and then your key. So what you
want to do is you're just going to copy
the word authorization. Actually, you
know what? Just type it because you
don't want to um copy the wrong thing.
So, capital A authorization.
And then for the value, you're going to
do capital B bearer just like this.
You're going to hit space one time. And
then you're going to go in, copy this
key, go back into agent mail, paste that
in. So, it should be bearer, space, and
then your key. And then this interface
is a little buggy, but I'm going to go
ahead and hit save. And then it should
look like that. And now, this is
basically all you need to do. This
should be set up. So, what we have to do
now is we have to actually test this
endpoint. Real quick, guys, as I'm
editing this video, I just wanted to say
that the actual API key that you're
getting there that you copied from
Grockbot into agent mail, you probably
want to keep that private. And also, you
probably want to keep the URL, the
endpoint private because if anyone has
those two things, they can basically
trigger that web hook. So, they could
find a way into your Grockbot and have
it do things that you probably don't
want it to do. So, treat it like you
treat any API key or password. Keep it
private. Obviously, the ones that I
showed you guys in this demo, I've
deleted by now, so don't even try it.
But just wanted to say that. But let's
get back to the video. Now, here's
something that I'm sure you guys are
wondering because I was wondering it,
too, is that now we have two inboxes and
we also have two web hooks, but we
didn't ever choose, you know, like which
inbox do we want to correlate to which
web hook. Meaning, both Trader and
Stephanie are going to be getting emails
from both of those inboxes, and we don't
really want that. Now, what you can do
inside of Grockbot is you can just tell
it, "Hey, by the way, Stephanie, you
should only be responding to emails that
are coming in to this inbox." You know,
you can set up the routine and it will
filter everything out immediately and
that will work, but it's just not super
clean. So, I'll show you guys real quick
how you can set that up if you want to.
And for some reason, agent mail, if
you're listening to this, make this
easier. I don't It should just really be
a simple UI dropown. Hey, which inbox do
you want this to correlate to? It lets
us do it, but we have to do it in code,
which is pretty weird. So, we have to
set an inbox ID. So, what I did here is
I just went to Codeex. I told it the
situation. I said, "Hey, I've got this
inbox, this inbox. I want it to
correlate to this one only." And it gave
me this JavaScript, which I'm basically
able to just copy this. I also pulled up
my um HML console right in here. And it
said I can just paste that into there
and then hit save. And so now this
endpoint should only actually be
triggered by emails that come into that
new YouTube test inbox right here.
YouTube testmail.to. And by the way, the
way I got there was inside of my web
hook, I went to advanced. So right where
we put the API key, and then I just
clicked on edit transformation and
that's where we got that um code that we
could edit there. So what we're going to
do now is we are going to actually test
that out. This is the moment of truth.
We're going to send an email to that
account. Test. This is just gonna say,
"Hey, could you please just let me know
if you get this and tell me your
favorite joke?" And then real quick,
could you go ahead and format this as an
email? It's to Stephanie and it's from
Nate.
Okay. Boom. Now, we'll go ahead and send
that off to agent mail. Now, what we're
looking for in inside of Grockbot is
we're looking for Stephanie to get that
email and we'll see her start spinning
and start working. And we'll see this
thing spinning as well. So, there we go.
Right on Q. We see this spinning. We see
Stephanie working and that means that
two things worked. The actual web hook
from agent mail to Grockbot worked and
the filter which only allows this inbox
YouTube test to actually trigger
Stephanie because you'll see here if I
go over to Trader, nothing's happening.
Trader did not react to that email at
all, but Stephanie did as you can see.
So, she should be coming back and
telling us a joke. Real quick, guys,
just wanted to say we have this
completely free kit for you all for
building your own AIOS. It's a template
that will help 10x your productivity.
It's got a bunch of skills in there, a
bunch of resources in there, and it will
basically help you transform your
system. Whether that's for Cloud Code or
Codeex or Hermes Agent or whatever agent
harness you're using, whatever tool
you're using, this kit will help you
out. But like I said, this is yours
completely free. The link for this will
be down in the description. But let's
get back to the video. Now, because I
never answered Stephanie's question
earlier up here, it went ahead and just
proactively updated the routine to only
touch emails from here. But it said,
"Got your test email. Replied in thread
confirming receipt with a short joke.
Web hook path is working. So we can
treat that address as inbox going
forward. Now if I go back into agent
mail real quick and we go to the inbox,
you can see that we have this test
message and then our Grockbot responded
and say, "Hi Nate, got it. Your message
landed in the inbox. Favorite joke is
why don't scientists trust Adams?"
Because they make up everything. Classic
AI joke. But you can see that you can
actually look at the inbox here and you
can talk from here. But that is how we
know that Grockbot actually was able to
respond after it got this message. So
this is pretty cool. Well, the
possibilities are truly endless once you
start to scale up different bots and
give them their own inboxes. And you
know, obviously Grockbots inside here
can talk to each other. So, they don't
need inboxes to talk with each other.
But if you want them to talk to other
agents, like your codecs can send emails
or something like that to your Grockbot
or different automations, it's going to
be pretty cool. So, I can't wait to see
what you guys are able to build. But
that is going to do it for today. If you
guys want to watch more Grockbot
content, then check out this video right
up here where I go over every single
core concept that you need to know about
Crockbot. So, I'll see you guys over
there. And thanks for making it the end.
