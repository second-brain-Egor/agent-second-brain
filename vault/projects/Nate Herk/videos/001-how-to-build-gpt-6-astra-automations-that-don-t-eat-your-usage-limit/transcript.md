---
type: project
description: "Codex lets you build automations right inside of it using scheduled tasks. However, because these scheduled tasks basically just send messages right..."
related: 
last_accessed: 2026-09-20
relevance: 0.97
tier: active
---
Codex lets you build automations right
inside of it using scheduled tasks.
However, because these scheduled tasks
basically just send messages right into
an actual chat thread. What that means
is this eats at your actual weekly usage
limit. So, it doesn't really make sense
to build a bunch of your personal and
company automations inside of codeex. A
lot of the most useful automations can
run somewhere completely independently
of codeex, but we can use codeex to help
us build them. So, that's exactly what
I'm going to show you guys today. Even
if you have no technical background at
all, by the end of this video, you'll
see how to build scheduled automations
or ones that are triggered on some sort
of event that live outside of Codeex so
they don't eat away at your
subscription. So, I don't want to waste
any time today. Let's just get straight
into this one. So, like I said, when you
have an automation running inside of
Codeex all the time, it's eating away at
your subscription limit. So, what I'm
going to show you guys today is how we
actually build our automations with
Codeex and then instead of actually
hosting them there, we're going to host
them in something called trigger.dev.
Because when we actually build the
automation, what happens is we can
actually just turn that into code. So
instead of having, you know, our
scheduled task run a skill on a certain
cadence, it basically just turns that
skill into code that can actually be
executed and then that code is just
given from codeex to GitHub. And then
GitHub basically says, "Okay,
trigger.dev, you're supposed to run this
code, you know, every hour or you're
supposed to run this code whenever
someone submits that form submission."
So if that sounds overwhelming or scary
at all, don't worry about it. It's going
to be super simple. Just think of it as
the idea that you're giving your skills
to something else to run it so that it
doesn't eat your codeex subscription. So
that way instead of your usage limit
looking like this, it will look more
like this one down here, which is green
and a lot more full. So what you'll need
for this video is a codeex subscription,
you'll need a trigger. And a GitHub
account. That's what we're going to be
using. Okay. So there are three
different types of automations that I'm
going to show you guys today. And I'm
also going to explain the difference. So
it's going to be a scheduled automation.
We're going to have a web hook
automation. And then we're going to have
a codeex SDK automation. So, let's start
with just number one. This is a
scheduled automation, which basically
just means we are going to have
trigger.dev execute our code that we
write on a schedule every 30 minutes, 6
a.m. on Mondays, however we want to set
up that schedule, very similar to the
way that the scheduled tasks inside of
codeex actually work. So, the first step
of planning out the automation is the
planning. It means we just want to kind
of brainstorm with um Astra in this case
to help us make sure that it fully
understands what we want built and to
make sure that we're not, you know,
missing anything. We're not we're
thinking through all the different
scenarios. And yes, this example is
going to be very simple, but it's just
to show you how this actually works. So,
I want to build an automation and I'm
going to put this on trigger.dev to
actually be hosted there, but you need
to help me plan this out and then
actually build it. So, the first step is
just the planning. I want this to be a
morning routine automation. And so this
is going to go off, let's say 6:00 a.m.,
and it's going to look at my calendar
for the day, and it's going to just give
me a brief. So it will have to check my
Google calendar, and it will just look
at the events I have. And then if
there's any additional research or
anything like that that it could do to
be more helpful, it can just sort of
help me prep for the day. Is there
anything else important that I'm not
thinking of? And do you understand how
this will actually be built out? And
what's cool is it will actually be able
to use some of the context that's
already in your projects if you are
working inside of a project. Because you
can see the first thing it said is I'm
going to check your existing morning
routine workflow so that I can actually
understand a little bit better how you
want this built. So trigger.dev hosts
something called TypeScript which is
just basically a coding language. If you
used something like modal then you would
be writing it in Python. So don't worry
about this word. It just is basically
the language of the code that we're
writing but don't worry about it. So
it's explaining now how is this going to
work. So the morning trigger would go
off at 6 a.m. America Chicago time. And
then we would look at Google calendar
and we would read today's events. We
would read their descriptions and their
times and their attendees and locations.
And then it would decide whether the
events need prep. So if it's with
someone new, we have this stuff that
could be helpful. If it's a podcast, we
could have this stuff. So it's going to
do a little bit of AI reasoning here.
And then it's going to use AI once again
to write the short brief. And then after
that, it will send it to me, but I
didn't actually tell it where. So it
said, "Where do you want this to be
sent?" Um, what's the timing? What's the
calendar scope? It's asking me some
questions here. So all of these are good
thoughts. I want this to actually be
sent to me in ClickUp. I want this to be
sent to me as a DM to Nate Herk, so to
myself and ClickUp. And you will use the
Upit AI account to actually send this.
As far as timing, we want this to be 6
a.m. And let's just have it be on
weekdays. It doesn't really matter to me
how long it takes. If it if I get it at
6:05 or 6:10, that's fine. The calendar
scope, we're going to use my main work
calendar. And research boundaries, let's
just do public web research for now.
later. We could always work in other
things like meeting notes and ClickUp
and Google Drive and things like that.
As far as the research, there's really
no reason why you should be spending
more than, you know, 25 cents for
research at this point, but we can
increase that later. Right now, let's
just assume that the calendar's locked
at 6:00 a.m. So, don't worry about
checking in later. So, now that I've
given it some more information, I will
go ahead and send that off as well. Now,
what I wanted you guys to notice here is
figuring out if the automation is one of
these two things, which are it's either
a deterministic automation or it's a
non-deterministic
automation. And so, what this means is
basically is it a predictable process or
is it unpredictable? And usually the
unpredictable automations when you get
into this territory over here, this is
when we really need to go for, you know,
a full agentic harness, a full codeex
routine because these are very
nondeterministic. They're unpredictable.
And in this specific example, this was
pretty simple. We basically have, you
know, a 6 a.m. trigger. So we have 6
a.m. it goes off. Then what happens next
is we will read calendar. And so that is
the next step. And so far there's not
even any AI involved. Where we start to
get AI is in this next step. when we
sort of do like the decision- making on
do we need research and you know what
would we do so this is research and this
would be an AI step so I would fill in
this with green just to indicate that
this is in fact AI the other thing that
we would need AI for is drafting the
message because you can't really draft a
message um with code unless you were
just using explicit placeholders and
it's not as flexible and then the final
step is to send that message to ClickUp
so what I wanted you guys to see here is
this is a very deterministic automation
because it goes 1 two three four five
oops five and it happens in that order
every single time. So that is a
deterministic flow. What's not
deterministic in here are these specific
AI steps. So step number three and step
number four are nondeterministic because
the research is going to be different
every time based on the input that goes
in and then the draft message is going
to be nondeterministic because it's
different every time based on the
research that goes in. So these are
important things to think about because
the more deterministic your automation
gets, the more of a waste it would be to
use codeex to host that. There's no
reason to use the full Astra agentic
loop inside of codeex if your automation
looks like this. 90% of business use
cases or personal productivity use cases
are more like this. They're more of the
deterministic automations that help you
out and really save time. So anyways,
just wanted to call that out. Hopefully
you're learning some new stuff in this
video. All right guys, real quick break
for a message from today's sponsor,
Hyper Agent. Now, I know that a lot of
you guys are running AI agencies and a
very tedious part is teaching the same
thing over and over again to every new
client's agents because every client
wants it done a certain way. So, Hyper
Agent handles that with skills and
memories because you can teach an agent
a skill once like your due diligence
framework or your press release
framework or format or you know some API
that you always end up wiring in and it
will just keep it in its memory and then
it will build up memories as it works on
things like the client's preferences,
their data sources and how they want
things formatted. And then you can watch
the whole fleet from a command center
that runs eval rubrics and it can do AB
tests so that you can see which agents
are actually getting better and what
each client costs you to actually run.
They can also sit in your Slack channels
and they can jump in when something
needs doing instead of just waiting
around for you to ask. So if that sounds
like something that could be useful for
your agency, then check out Hyper Agent
through the link in the description and
you'll get some free credits to start.
So thanks again to Hyper Agent for
sponsoring this part of the video. But
now let's get back to it. So anyways,
Codex comes back and says, "Okay, cool.
That gives us a clear plan. Here's
exactly what we will do. Here's the
budget. Here's the research. Here's all
the stuff that's how it's going to work.
And now, let's actually go ahead and
start building it. It also calls out
this hosting detail, which is that
Trigger Dev's current free plan
scheduling window can delay a 6 a.m.
start by up to an hour. So, if we really
need this right at 6 a.m., you might
have to upgrade your Trigger.dev plan.
But, as far as getting started, you can
start on the free plan. All right. So,
sounds like you have a good idea of how
this works. What do you need from me?
Are there any different API keys that I
need to get, or do you already have
access to all of these keys? So that's
really the next step to be thinking
about because if you have been building
inside of codeex and you're using a
bunch of these plugins, so you've
connected to all of your accounts inside
of these codeex plugins, those will not
transfer over to trigger.dev, which is
why I really like to use plugins not
very much. I like to use thev file and I
like to put all my API keys in there so
that if I ever need to move them over to
cloud code or if I need to move them
over to trigger.dev, I already have them
in one spot and I can just copy and
paste them. And I will show you guys how
that works later. But yeah, now that
we've done sort of the hard part, the
heavy lifting of actually planning out
what we want, the implementation is the
easy part because now we let Codeex
actually go ahead and build this out for
us because as you can see, it says,
okay, it has access to Google Calendar,
ClickUp, OpenAI, Perplexity, and we will
obviously set up trigger.dev, but
basically everything we need to move
this over once Codex has built it is
already here. If you don't yet have your
API keys for Google Calendar or ClickUp,
you would just say, "Hey, can you help
me set that up with Google Calendar with
ClickUp?" and it will tell you exactly
where to go and what to click on and
what to get. So getting API keys and
getting that set up is not really
technical. It's not really a technical
lift anymore. It used to be a little
more intimidating in the old days, but
now it's so easy. So if you don't have
API keys, just ask Codex to help you
find where those are and just go grab
them. But now we're ready to start
building. So I'm just going to tell it,
yep, go ahead and start building. And
I'll check in with you guys when we're
ready to move this over to trigger.dev.
But the one thing I'll say is before we
move it into trigger.dev, we want to
have Codex do as much verification on it
as possible. So, if it's able to test it
out and basically fix it before we move
it over, then that's good. You know,
we've talked a lot about giving agents a
way to verify their own work and telling
them to verify their own work so that
you're not getting their first attempt.
So, go ahead and build this out for me.
Make sure you feel confident in how it
works and you've validated that it will
work before you actually tell me we're
going to move it into trigger.dev and
then once you're done, we will move
everything over and host it. Now, you
can see what it's doing is it's building
it out and it's testing it. You can see
it's using test-driven development. It
is sending DMs. It is looking at how
much all this costs and it's basically
optimizing for what I actually said. It
even made sure that the DM was the
correct conversation. And the reason why
this whole deterministic or
nondeterministic thing is important to
understand is because yes, you could
easily do this as a routine inside of
codeex, but I actually did this before
where I had a routine that was very
simple like this and after about a
month, it started to just go rogue. It's
just randomly started to send to
different DM channels and it started to
send to like the team channel and stuff
like that. And the reason for that is
because it was an agent on the back end.
the agent was just interpreting the
message different every time and it just
acted differently. But what we're
actually building here is we're building
a script so it doesn't have the option
to act differently. We're literally
saying, "Hey, this is what runs and it's
goes the same way every time." So in
this code, we're basically like hard-
coding the direct channel with the
channel ID and the message ID and
everything that gets sent rather than
giving the agent the full connection to
ClickUp and saying, "Hey, just send it
to Nate." Anyways, this has just
finished up. So you can see, whoops,
that it was built and validated locally.
And we should have a test brief in
ClickUp. So let me check that real
quick. Awesome. So you can see right
here that I do have this DM where I see
my Tuesday morning briefing. I have my
day right here. Every single one of
these things has a link to my calendar
as well. If I click on this, for
example, it pulls up the actual event in
my calendar. And then it also comes back
with, hey, here's some useful prep. And
here are some things to notice. So we
know that the ClickUp connection works.
We know that the AI is working on the
background. And we know that the Google
calendar connection is working as well.
And it says that everything has been
built and validated. And this costed
about 1.33 cents. So us giving it the
gate of, you know, maxing each run at 25
cents seems pretty realistic. Anyways,
now we have to deploy to trigger.dev and
validate one run there before we turn on
the schedule. And the cool thing about
this is yes, you're going to be able to
follow this tutorial so you know exactly
how to connect to trigger.dev, but if
you didn't, so how exactly do I get this
automation from the code that you built
into trigger.dev? And while it's doing
this, let's go ahead and make sure we
have a trigger. account. So, head over
to trigger.dev. Go ahead and create an
account. Like I said, you can get
started for free. Now that I'm in here,
you can see I'm on a free plan in this
account and I just created a new project
up here called YouTube. And this is what
it will look like in order for you to
sort of like get everything set up.
There's nothing yet in here. So, this is
how it gets really cool because we're
able to basically just connect codeex to
trigger.dev and it can basically talk to
trigger.dev in order to do all of this.
Now, you can also have it connect to
GitHub, which is something that I do
recommend because that way GitHub
connects to trigger.dev and the three of
them talk together. And the reason why
we like to use GitHub is because then
you can have like different version
control and you can have other people
more easily contribute to the automation
if you need someone else to change it or
something like that. And Codex can
connect to trigger.dev and GitHub via
the command line tool. So, that's what I
would probably say next is let's get
connected to GitHub and trigger.dev dev
via the command line and then we can
just push our code to GitHub and then
trigger.dev will sync with that code.
And what this will do is it will use the
CLI and it will prompt you to just
authenticate in. So it will do one of
those things where it opens up the
browser, you sign in with GitHub, you
sign in with trigger.dev, and then you
come back into Codex and it says boom,
got it, I'm connected. So here is the
trigger.dev authorization. I just have
to go ahead and authorize right here.
And then it says return to your terminal
to continue. So Codex should have gotten
that now. And you can see that because
my codeex is already authenticated to
GitHub, I didn't have to do that. But it
would be the same exact flow if you
haven't done that yet. So now I want you
to create a new private repo for this
automation in my GitHub account. And I'm
just going to shoot off this message to
steer codeex in the right direction now
that we know we're connected to these
two tools. And you can see that it says
the API keys, the calendar snapshots,
and anything sensitive are excluded from
Git. Even though we're creating it as a
private repo, it gets completely
excluded. And that's the whole point of
thev. So, what we'll have to do in
trigger.dev is we will have to manually
move those over. And look at this.
Because Codeex's browser use is so good,
it also pulled up my trigger. account in
this browser. So, if there's anything
that you're confused about navigating
the trigger interface, you can have it
help you out by just clicking around
right in there. But, it says that we did
create this GitHub repo for the morning
brief. So, basically, this repo, just
think of it like a Google Drive. It
holds the actual code and the rules for
how this automation runs. And
trigger.dev will grab this and actually
host it. So, it's super simple. But also
if you make different versions you will
update it here. So you could roll back
to previous versions if you want and
that way if a team member later wants to
take over this automation all of the
details are here and they can contribute
to this project. Okay. So take a look at
this. It actually created its own
project in my trigger. So it said in
morning brief and settings and git is
the GitHub repo connected. So basically
what that's saying is okay it got into
my trigger.dev. You guys saw me create a
new project called YouTube but it
decided okay I'm going to create my own
project. So it made one called morning
brief. And now what we need to do is we
need to see if this trigger.dev project
is connected to our actual GitHub
codebase called morning brief so that
they can sync and talk to each other. So
that's what it's asking me to verify. It
said to go to the settings in here, but
you can see that it says GitHub isn't
connected. So it's actually not syncing
to anything at all. So what I need to do
maybe is install the GitHub app. But
let's see. I'm just going to say I don't
see any deployments. I don't see any
integrations. When I go into
trigger.dev, it tells me that GitHub
isn't yet connected. So that's what I
see. But this is really cool, guys. You
can see how proactive this thing is. It
actually just went ahead and started
doing all of the connections rather than
telling me what to do, which is pretty
cool. But every once in a while, it hits
a snag and it will just tell you, hey,
can you check this? Can you check this?
But hopefully with this context, it's
going to be able to help out with that
now. And now you can see it's going to
open it up to actually do it itself. So
you can see the mouse right here moving.
This isn't me. This is codeex using its
browser use to check on all this for us.
Okay. So you can see that this says
connected and verified and morning
delivery remains disabled until the full
hosted delivery test passes. So that's
good. And it actually moved it back
under the personal account where the
GitHub connection already exists and
ClickUp still uses UPAI. Now let's go in
there real quick so I can show you guys
something. If I go back into the other
project and it actually did it in a
different org. So if I go back to my
personal org, this is where we should
see the morning brief. There we go. So I
was just looking at the completely wrong
one. And if I go to tasks, this is where
we can actually see the interface of our
weekday runs. And what's cool is it did
two different tasks. It did the
scheduled one. So this one you can see
is the one that goes off at 6 a.m.
Monday through Friday. And then what
actually happens when this runs is it
calls this other I guess runner. So it
calls this and this is the one that has
the actual process in it. So it does it
in two parts. And that's pretty cool
because as you create these longer, more
complex workflows, they call individual
tasks and pieces that codeex will build
out for you and it just helps with some
visibility. So anyways, what we can do
here is if I go into the schedule and I
hit test schedule, this basically starts
running this. So I'll hit run test and
now this runs in production. And then
what you can see is that it actually
calls this other little task. And now
this thing is running. It's showing us
how long this is taking. It's going to
show us all these little different
details so that if this errors, we could
copy all this data, give it to Codex and
say, "Hey, this is what happened. Help
me fix this." So, you can see that this
already finished and we can look through
the payload. We can look at the status
which came through as disabled. And
you'll notice that I didn't get a new
DM. So, we have to figure out why this
didn't seem to work. My first thought
would be, okay, well, do we have all of
our API keys and all of our secrets in
here? And if I go down to deployments,
this is where I can click on environment
variables. And you can see that we have
a bunch of stuff in here that got added
today. Today's September 15th. So Codeex
actually took our ENV and via the CLI
put everything in here, which is
awesome. So we should have our ClickUp
ids. We have our workspace ID, client
ID, all of this stuff should be working
in here. So what I would do is I would
say, okay, so I just ran a test run
inside of trigger.dev, but I didn't get
a ClickUp message. I didn't get
anything. Can you just check and see
what happened there? So you guys
remember how it came through and said
status equals disabled. It's because it
had morning brief enabled as false. So
if I go back into our trigger.dev and I
go to our environment variables, you can
see right here, morning brief, it says
false. So we would basically have to
come in here, edit this, and we would
have to change this to true. Hit save.
And now if we go back, let's see if this
fixes the issue. So I'm going to go into
the morning brief weekdays and hit test
and go ahead and run that. And there we
go. This looks a little bit different
now because you can see it called on our
different runner. We can see what's
actually going on. And we can see this
thing actually in real time sort of like
playing out. We got a little bit of a
green message here. We get output equals
delivered. Let's open up my ClickUp.
See, was this a new run? Okay. Well,
unfortunately, this still doesn't look
like it was a new run. So, once again,
we have to go figure out why this didn't
work yet. Because if you guys remember,
it worked when Codex was testing it
locally, but it didn't work yet in
production. So, okay, that run seemed to
work. It showed that we actually got the
output, but I didn't get any DM in
ClickUp. So, take a look at that run and
help me figure out how do we fix this.
Okay, that's really interesting. What
happened was the run found today's
earlier test message. So, it skipped
sending a duplicate because it would
have been essentially the exact same
message. So, it seems like that run
didn't actually fail. It was more so
done by design. You can see the existing
message was sent at 12:01 and we just
tried to run a new one at 12:33, so it
didn't get sent. That's why it's always
important that when you're having AI
build you automations and build you
code, you don't have to know what every
single line is doing. But you do have to
test the stuff out to figure out how it
works and why it does what it does. I
mean, look how powerful this is. It's
basically able to deploy everything,
debug everything, move around in the
interface, and then just test it all for
me. And we're just using our natural
language, and we're using our intent to
drive all of this. This is so much
quicker than the way I used to have to
build automations. it worked in this
variable that shows that if it was
already delivered and it got triggered
twice for some reason to not send a
duplicate message. So duplicate
prevention remains intact. I think it
did a really good job there. But I do
want to prove to you guys that this
works. So I'm telling it to override
that just so we can see that it works as
expected. And then we'll move on to the
next automation. There we go. We can now
see that we got the hosted proof test
for the morning brief. And now we can
feel better about turning this thing on
inside of trigger.dev and knowing that
it will actually have all the
connections set up because we've seen it
in here. We've tested it. We know that
all of the environment variables are
also moved over. So, we are all good to
go. All right. So, we took care of the
scheduled type of automation. Let's look
at one that is triggered by something.
So, typically this is triggered by a web
hook. So, we're going to go back into
Codex and we're just going to start
having it do two things for us. It needs
to build sort of like a very simple
front end that will actually be our
trigger for this specific example. And
then we'll build the back end, too. So,
I'm actually going to try to do this in
one fell swoop. I'm going to do a
slashgoal. And here we go. So now I want
to build a web hook triggered automation
inside of trigger.dev. So this is kind
of a two-parter. The first part is we
need to use or sorry I need you to help
me build just a very simple local host
that is sort of like a form submission
that you might see on a website.
Collects information like the name, the
email and um team size and what they're
looking for. So, a simple landing page,
a simple form that we can fill out, and
then when the user hits submit on that,
that's what I want to trigger the actual
automation on the back end that we're
going to build and put in trigger.dev.
So, basically what I want is for um that
automation to just send me a ClickUp DM.
So, same DM as before, and I want this
one to just say, "Hey, you got a new
form submission. It's for this person.
Here's what they asked for, and here is
how I recommend you reach out to them."
So, sort of like just creating a draft.
So, I'm going to shoot that off and it
might have some questions for us. But
this is a very simple use case just to
show you how it works with a web hook.
But this is still a very much a
deterministic automation. Even though it
is AI, it is still deterministic. So,
let me show you real quick what this one
looks like. This one is a web hook
trigger. So, this is just going to be a
form submission. That is basically what
kicks this thing off over here. From the
form submission, what happens is it's
going to actually read the form and it's
basically just going to have to do one
thing, which is create the actual um
message that will go to us in ClickUp.
and then it will basically send it to us
in ClickUp. So, it takes a very similar
shape as to what we've already seen,
except for instead of going off on a
schedule at 6 a.m., it goes off based on
the actual action which is triggered by
us. And then once again, the only time
we actually see AI inside of this
process is just here. Now, you could
actually do this with no AI. If you
wanted the form submission to just shoot
you a message in ClickUp, you could do
it with placeholders and you could do
that. you'd save yourself some money and
some time because there'd be no AI
message or sorry, there'd be no AI step
and that would be 100% deterministic
every single time. Now, obviously, there
are some edge cases you might want to
think of. You know, how do you build the
form so that they can't, you know, spam
it a thousand times in a second? How do
you build the form so that if you're
expecting an email field, you're
actually going to get only email fields?
There's a lot of other edge cases to
think through. But what's cool about
that is after you build this, you could
say, "Okay, cool. Now, spin up 50
different sub aents and have all of them
test this thing, try to break it, and
then let me know what you find." and you
can really stress test and QA your own
automations before you actually have any
sort of human or customer find these
bugs or anything like that. So that's
pretty cool. It's going to spin up a
local page. It's going to use the
existing trigger.dev deployment on the
back end. And now because we've already
set up the connection with like GitHub
and trigger.dev. All of the automations
we want to build in the future are going
to be much much easier. So I'm basically
just going to check in with you guys
when this one is done and show you how
that works. Okay, so it says that this
is done. You can see that we have this
form here to fill out. It says that it
has built and verified this end to end.
So submitting it now will start the
hosted trigger. Task. It will generate
the outreach recommendation and it will
send everything to ClickUp. So let's go
ahead and real quick check in
trigger.dev. We do have this new one
right here. I'm going to refresh just in
case. And you can see that we have this
new one called form submission. It has
already been triggered a few times. It
looks like actually let me just zoom out
so that we can see this better. It has
been triggered five times. So this was
Codeex testing it. And now let us go
ahead and test it ourselves. So, I'm
going to go back into Codex. I'm going
to fill out this form. So, we're just
going to say Alex Morgan, Alex
company.com.
Team size, we will just put 200 plus. We
are spending so much time on, you know,
making hamburgers and it's just becoming
a real bottleneck. So, I'm looking to
see if we can automate that. And let's
go ahead and shoot that off. What do we
get on this front end? Your request is
in. Let's go back to trigger.dev. Let's
see if we get some sort of run. I'll go
back to the tasks. We should see it
looks like there's a new one executing
right now. If I click into this run, we
should see that all of this is actually
going on. So that proves that this web
hook has been set up correctly. Now, in
the old days, we would have had to set
up the URL and kind of sync them
together and like build out the payload.
But we don't have to do that at all and
it this is the payload basically like
the information that comes through and
now we have the output. Let me check and
see if we got this in ClickUp. Sweet.
Okay, so we actually got a lot of these.
These are all of the demo examples that
it tried, you know, the new form
submissions. But this is the one that we
just submitted. You can see right here,
Alex Morgan. Here's the email. Here's
the team size. Now, this took no AI.
This is what I meant when I said that
this could be just placeholders. So, if
you wanted just to just get this
notification, no AI needed. But here's
where we needed AI, the recommended
outreach and the email draft. And this
is what had to be obviously generated
with artificial intelligence. So, that's
kind of the trade-off there. But, super
simple, super easy. That took me no time
to build. And I barely had to do
anything as far as like wiring things up
by hand. So, that is a web hook
automation. That doesn't obviously have
to be just a form submission. That can
be a new record in the CRM. That can be
a new email entered the inbox. There's
so many different event-based triggers
that you can have for a web hook style
automation. By the way, guys, I've got
this completely free SOP for you about
getting your first a automation client.
It's going to go over the exact steps
that has been proven for hundreds of our
AIS Plus members to get their first paid
gigs. It goes over the one sentence
service pitch that can get you started
today. Why your first client should cost
you money. The five-minute video that
answers, can this person actually
deliver before you've actually received
any money, what to do when you have zero
case studies. There's so many good
things in here that are going to help
you out. Even if you already do have
clients, I would recommend grabbing this
because, like I said, it's yours
completely free. So, if you want to grab
this, there's a link for it down in the
description. Let's get back to the
video. All right. And for this last use
case, now that we've done the web hook
as well, this one's a little bit
special, and this is when you kind of
want that full agentic loop that you're
used to getting inside of codeex, but
now you're getting it programmatically,
and that is through the codeex SDK. So,
a really good opportunity to see if you
want to actually use the Codex SDK is
when you need to bring something that
might be an already existing routine
into something like trigger.dev. Now the
thing about this is most of the time if
you're running an automation in a
scheduled task inside of codecs, I would
recommend you keep these as a codec
scheduled task because then it actually
eats away at your subscription. But if
you need to do this at scale and you
can't use your subscription
programmatically, then you probably want
to build the automation with the Codex
SDK and then host it on something like
trigger.dev. So if that ever does become
the case, you kind of get the full
agentic loop. So here is what that might
look like. We saw these first two
examples. Now, what I'm going to do here
is this is going to be a scheduled task.
So, we're just going to call this
actually let's just call this every 30
minutes. And I actually do this for real
inside of a a scheduled task inside of
my codeex where 30 minutes it wakes up.
And we basically just have this full
agent. And what it does is it basically
it looks at my I'm just going to call
this an agent because it does a lot of
things. It looks at my alpaca account
and actually let me just like go down
here and make some tools. Just pretend
that these are tools. So, it has to like
check alpaca, which is where I have like
some trading going on and my agent here
helps me trade. It will also, you know,
like do research. It can also just like
look at like past logs and stuff like
that. So, it's leaving logs for itself
every time so that the next time the
agent wakes up, it's not completely
stateless and just like doesn't know
what to do. So the reason why this is
the SDK rather than just being more of
like one of these deterministic AI
automations is because we don't know how
many times it might need to look at the
logs and read things or look at the
research or check back in in alpaca if
it's doing research for 10 minutes and
it's like wait let me just check the
current holdings one more time because
things may have shifted this it it has
the ability to basically just go back
and forth you know it can go like this
and then this and then this and then
this and then this and then this and
then this and it's basically an agent
and it has that luxury and then what
happens is It essentially just sends an
email with a recommendation. So, I'll
just call this email. And it sends that
to Grockbot. And then Grockbot actually
places the trade because OpenAI models
and cloud models don't actually let you
trade anymore. They just won't do it. I
think it's because all this security
stuff is going on, but Grock still lets
you trade. So, my Grockbot is the one
placing the trades and Astra is doing
all of this heavy lifting research. Now,
yes, you could do this exact same sort
of thing in a deterministic flow, but
that would just look different. It would
basically be a predetermined amount of
research. So, for example, it could hit
like a research step or maybe it hits,
you know, two research steps. So, I'm
just going to like sort of demonstrate
this like this where maybe it does two
different like research sources. So,
maybe this one is firecrawl and this
one's perplexity or something. And then
it basically will send it to an agent to
um look at the research and can create
the draft, create the email and then
send it off. But what if it looks
through this and it's like, "Wait, I
want to do some more research." Because
now the AI agent has analyzed it and
it's like, "Wait, let me do some more."
We would have to work in somehow the
ability for the agent to loop back and
do more research. And that's essentially
why we would just use something like
this where we're now using the SDK to
give us that sort of autonomy. So, let's
go ahead and build that out real quick.
Now, this would be a very similar
process where I would like you to say,
"Hey, I want you to interview me about
this process. I want to get very clear
on what this does." Especially the more
autonomous your systems get, there's
more room for error. There's more room
for, you know, you're increasing the
risk, you're increasing the cost, you're
increasing complexity, you're increasing
the maintenance, you're increasing a lot
of things. So build the simplest
solution possible and only move up the
sort of AI systems pyramid as I call it
when you truly need that functionality.
So I would go through this whole process
of interviewing to get what I want. But
we have this luxury here of all of this
is already set up because we have these
routines going. You can see that I have
this um thread called challenge thread
where I'm doing this actual trading and
you can see that every like 30 minutes
or so it's basically just starting this
routine and it's doing the whole agentic
loop. We see that one is actually
running like right now and this is the
this is codeex. This is codeex working
and we're basically just trying to move
this over to trigger.dev. Now I'm not
really wanting to I obviously want to
keep that using my subscription but for
the sake of the demo. So what I need you
to do now is I want you to build me a
codeex SDK automation and we're going to
host this inside of trigger.dev. dev.
Now, what I want to do is I basically
want to transition the Astra trading
challenge, that thread. I want to move
that routine over to trigger.dev. So, we
basically wake up like every 30 minutes
during trading hours, one check before,
one check after, and we do this research
loop. We check Alpaca. We check the
logs. So, familiarize yourself with that
actual process. And then just turn this
into a Codex SDK automation for me and
host it in trigger.dev. Let me know if
there's anything else that you need to
build this. So once again, the hardest
part is already done here. And now we're
just going to get that built out. So
I'll check in with you guys when this is
all done. Okay, so this run took about
15 minutes, a little over 15 minutes.
And we can see now that this is ready
for our review. It did 44 passes or 44
tests and it paused the old desktop
routine, which I'm going to say, you
know, I don't want it to pause that.
This was just a demo. So anyways, um it
was being pretty proactive there,
though. But anyways, what it did is it
made a new project. So it created a full
new one rather than what we were doing
earlier. And I'm actually just going to
open this up full screen in my desktop
over here. Give this a quick refresh.
You can see what it did is it basically
made a few different like tasks or
runners or whatever you want to call
them. And they kind of call on each
other. So you can see here there's the
check. This ran 18 times. Um then we
have an install plan. We have a
pre-flight and we have a proof. So I'm
not exactly sure the right order to run
this in, but this is what it did. And if
I go to the runs, we can see exactly
what happened. So it basically runs, you
know, these failed, these completed.
We've got these checks. So what we're
going to want to do is we're going to
want to figure out what does each one of
these do? So I'm going to go ask um
Codex that real quick. So I can see that
you actually created four different
tasks. We've got a check, an install
plan, a pre-flight, and a proof. Can you
just explain to me what these are and
how they work together and how these use
the codeex SDK to give us sort of that
full agentic loop that we're looking for
here? Okay, so Astro check is the actual
recurring worker. that is the one that
should fire on the schedule. The other
three help it do things. So the
pre-flight checks the codeex runtime,
alpaca connection, SIP market data,
policy files, and the checkpoint
storage. And it can optionally make a
small model test call. So this really
only needs to run during setup or
troubleshooting. We have proof, which
runs the full research and reporting
workflow, including the the test label,
email, and clickup delivery. It prevents
actionable trade tickets during the
test, and this will run before enabling
the routine. currently disabled after
verification, the install plan during
setup, and then the check at each
scheduled check. So, it's actually
interesting. It made all of those to
help it build and to check. But now, I'm
not sure because each check now follows
this process where we have it loads up
the context. It asks codeex what needs
investigation. It finds the evidence. It
has Codex evaluate all that. And this is
with the SDK, of course, it validates
and delivers, and then it saves the
handoff. So the agentic part is Astra
choosing what to research using web
tools, doing deeper evidence, and
adjusting its conclusions based on the
result, which is pretty interesting.
This is the only one that will actually
run now that this is all built. So I'm
going to go back into here and we're
going to go to Astra check and we're
going to hit test and just test this
thing out right here. Now look at this.
It just called this attempt right here.
And we open this up, we can see
everything that's actually going on. Now
this is pretty cool. The reason why this
did nothing is it actually sent this
payload over which was like the time and
the date and then the output was hey
this is early because this was set up by
Astra in a way where it's supposed to
check in during market hours and right
now the market has already closed. So
the next scheduled run isn't until
tomorrow morning before the market
opens. So that's why it basically fired
and it was like oh you know this
actually isn't right. I'm not supposed
to run yet so I'm outputting the word
early. But I do know that this works
because if I go into my ClickUp thread
where I'm actually getting these
notifications every day from the actual
routine, you can see that these started
to come in. You can see we have the test
migration here, 341, 347. We have
another test migration for Nate's
review. It's doing the research. It's
giving us assessments. It's linking
things. It's looking at our account.
It's pulling in all the sources. It did
another one at 352 for the market close.
So, this is currently working. And what
it's actually doing is it is messaging
Grockbot. This is my trading Grockbot
that actually places these, you know,
trades based on getting an email. So,
everything transferred over to the point
where it's getting these test migration
reports as you can see because what's
going on is trigger.dev automation with
the Codex SDK like it said, it's
checking, it's doing research, it's
looking at the evidence, and then it's
making recommendation and it's sending
it to ClickUp, but also as an email to
my Grockbot. So, you can see we now have
already set that up in trigger.dev dev
to basically mimic a codeex routine with
Astra on the back end with a full codeex
agentic loop, but we could now trigger
this programmatically and we could do it
by web hooks and on different schedules.
And like I said, you only would really
do this when you need it to truly be
programmatic and at scale because
otherwise you want to throw it on your
subscription because paying for Astra
via API credits is obviously more
expensive than paying for Astra via
subscription. But that is how these
three types of automations differ. And
now I can come back in here and I can
cross out Codex SDK. But anyways guys,
that is going to do it for this one. So
I hope that you enjoyed and you learned
something new. And if you did, please
give it a like. It helps me out a ton.
If you guys want to check out any more
Codeex content from me, then go ahead
and check out this playlist right here.
All of that's about Codex and Astra and
more stuff like that. So hope to see you
guys over there. Thanks for making it to
the end. Take care.
