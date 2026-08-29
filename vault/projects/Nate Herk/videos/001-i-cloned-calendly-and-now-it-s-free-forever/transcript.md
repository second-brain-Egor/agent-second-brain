---
type: project
last_accessed: 2026-08-29
relevance: 0.98
tier: active
---
So, I just built a clone of Calendly,
and it's completely free for me to run.
Calendly has an estimated valuation of
$3 billion, and competitors like cal.com
have a valuation of around 150 million,
and have raised tens of millions of
dollars. But, in 1 week, I was able to
clone the core functionality of it with
just a few prompts, and now it's free
for me. So, in this video, I'm going to
show you guys what I built, give it away
for free, show you how you can get set
up for yourself, and talk about exactly
how much this cost me to actually build.
So, let's not waste any time, and just
get straight into today's video. All
right, so just going to jump right in.
This is called Snag Time. You can see
that we have to sign in. I've already
created an account, so I'm just going to
go ahead and log in. And now we are at
the home screen. You can see we have an
overview. We have my branding. This is
my workspace called Up at AI. I can see
my upcoming
bookings. I can see how many I've had
this month. I can see how many hours
I've booked, and my published links, so
how many different event types I have. I
can see all of my upcoming bookings
right here, and I could go in, find some
more details. I could also reschedule or
cancel. So, if you guys have used
Calendly or stuff like cal.com before,
it's very similar. You're getting the
same functionality. I can come down here
to my settings, and I can change my
workspace, my password, my profile
photo. I can invite other members, and
have different like permissions, whether
they're a member or an admin. And I can
set up my workspace image, colors,
descriptions, stuff like that. So, what
I thought I'd show you real quick is
what is an event type, and how does that
actually work? So, if I go to my event
types, you can see that I have a revenue
strategy session. I have this test, and
all of these were pretty much made
during testing. I've made a few of these
myself, like the paid scoping session.
Yes, I've connected Stripe, so you can
actually book in paid calls. And then
we've got this regular strategy call.
So, let me first just do a simple one
real quick. And by the way, all of these
say localhost, meaning right now I'm
running all of this locally. So, in
order to actually get this up and
running, so you can send, you know,
links to clients, and have them book in,
you'd have to put it to some sort of
public domain on, let's just say Vercel,
and then all of this is
fully working. So, when you get in here
to set this up, you're just going to
have to connect things like your Google
account, a back-end database, and your
Stripe account. If you guys want to get
this for free, all you have to do is go
to my free school community, which looks
like this. The link is in the
description. You'll go to classroom and
you'll go to all YouTube resources.
You'll be able to grab the whole setup
guide in there and get set up in one
day. So, anyways, let me go ahead and
copy this link, open up a new tab, paste
that in here and show you guys what that
actually looks like this booking flow.
You can see that I've set up for this to
be the description. I can obviously
change that. This is coming through as
our custom branding. And I'm going to be
able to go ahead and choose a date and
time. So, this is live to my real
calendar. I'll go over to the actual
calendar looking at Friday. You can see
that I can only book in from two to
about three and then from four to 4:30.
And this is the real calendar. So, you
can see all day tomorrow is blocked off
in the morning and then three to four is
blocked off. So, this is coming through
as accurate and then if I go to like
next week, there's nothing at all next
week besides these two calls
9:00 a.m. to 11:00 a.m. on Monday. And
if we come back into the booking link
and I go to Monday, you should see that
we don't have 9:00 a.m. up until 11:00
a.m. So, this is syncing live. If I was
to on Monday real quick put in some big
block from like 1:00 till 6:00,
we'll just call this busy. We go back
over here. Oops, wrong tab. We just give
this a quick refresh. And now if I go to
Monday, all those times are blocked off.
So, it's syncing live. Anyways, I'm
going to go to Friday and I'm just going
to book in for 4:15 and we're going to
move on to the next screen. This is
where we can obviously put in some
information. So, I'm just going to put
in Nate sample email address, which
actually is real. We're just going to
call this test and test. And then we can
go ahead and review the booking. This
page though, I could ask more questions
when I create an event type. So, I'll
show you guys that in a sec. But then,
I'm able to just go ahead and confirm
the booking and then this is the screen
that the user who is confirming or
setting up the booking sees. They get a
little notification. We can reschedule
or cancel it. And then if I go back to
my calendar and I go to Friday, we now
see that we have the strategy call with
that email address that
put that in right there. And then right
here I'm in the actual email that I just
signed up for that booking call with.
And you can see right here we got the
invite on our calendar and I'm just able
to go ahead and accept that. So, back in
the actual app, what does it look like
to make an event type or edit one? Well,
if you want to edit one, you just come
in here, you click edit, and then you're
able to change the color of it. You're
able to change the description, the
link, the name. You can change the
location. You can change how the
availability works. So, you can add a
buffer, you can do date range, so very
similar to Calendly, and then you can
also change what questions you're
asking. So, you get full customization
here on how many event types you need
and what they need to do, all that kind
of stuff. And if you're creating one,
it's basically the exact same thing.
Name, description, booking link, time,
all this kind of stuff. You have full
customization here. And then you also
get to, like I said, you can choose if
it's going to be free or paid. And if
it's paid, you set the price, and people
have to pay it. So, let me show you real
quick what that looks like to go through
a paid flow. So, I'm going to do this
again on Actually, let's go to Wednesday
of next week, so it's like completely
open. I'm going to grab a slot at 10:00
a.m. We're going to move forward. This
is going to be same person, so this
person is like really anxious to book in
some time and get something figured out.
And um also, one thing I wanted to call
out. So, like I just realized this was
one of the manual improvements that I
had to make. Also, this email's wrong.
Um
one of the manual improvements that I
remember making was even though the
agents clicked through all of this, they
didn't find any bugs after they kept
testing, but what I noticed was
you as a human, you come in here and you
think, okay, I'm on the review stage,
and I want to get back to the time. I
want to click up here, right? Cuz
there's this little progress bar. But,
the UI originally was not designed to
have these buttons be clickable. It was
only designed so you would have to
explicitly click on these arrows. And I
don't know about you guys, but I would
always immediately click on these rather
than going to click on this little arrow
that doesn't really crap capture my
attention. So, that's one of those
things where, you know, later I talk
about some of the other things that I
did in this project. Um but, I came back
and I did some redesigns on the user
experience because even though the
agents were really good at finding bugs,
they didn't always think about the
experience the same way that a human
does. Even though I prompted them to,
they missed something like this. And I
just wanted to call that out because
that is something I explicitly remember
thinking to myself like that's going to
be a much better user experience. So,
anyways, let's go ahead and pay for
this.
What happens is it takes us to a Stripe
booking link. So, it says confirming,
it's going to take us over to a
different link. Now, this is a sandbox
environment, so I'm putting in like this
fake card, but all you'd have to do is
switch out the API keys for a real
Stripe, and then boom, it works. So, let
me show you how that works real quick.
So, what Stripe has you do is you use
this number as a sandbox card, and then
you put in any combination here for
these two things. And this would just
simulate what it would actually look
like for the user to go through this
flow of putting in their card, paying.
And there you go. Now, you can see that
we just got that paid scoping session
notification with Nate at Wednesday,
September 2nd, 10:00 a.m. But yeah,
that's basically it. It's a super, super
simple interface. Now, I will say it's
missing some of the like automation
functionality that Calendly has, but
that could really easily be worked in
now that you have, you know, Codex or
Cloud Code that is fully aware of this
app existing and what you want to add to
it. And you can also build those
automations right in there if you
please. Of course, you can come in here
and do other things like change your
availability. If you want to work on
Saturdays and Sundays, you can change
your, you know, time of operation. You
can change your time zone. You can add
date override, or you can add time off.
And once again, now that this is yours,
all you have to say is, you know, "Oh,
can you just change
how this works? Or can you add this
functionality?" Because now, whenever
you feel a pain point due to snag time,
due to the way I built it, you just ask
Codex or Cloud Code to add more
functionality into this thing because
you own the software layer. All right.
So, now let's get into how I built this
and what it actually looked like as far
as like these stats. So, before I get
into these stats, let me talk about what
I did because I really only shot off
like five prompts. So, what I did at
first was I started off with a massive
slash goal prompt. And inside of this
prompt, I was basically like, "Hey, I
need you to Essentially, we're going to
clone Calendly here, and and I want to
be able to run it locally and for free.
What I need you to do is kind of work in
four phases. The first phase was
research, the second phase was planning,
the third phase was building, and then
the fourth phase was actually testing.
And then this kind of ran into this loop
where it would test and then build and
then, you know, test again and then keep
going. But, that's kind of what I said.
And I wanted it to research Calendly and
cal.com and research what people say
they don't like about it and what people
like about it. And basically,
take that research into the planning
phase where now we have the features and
functionality that we're looking for.
And then planning out how are we
actually feasibly going to be able to do
this with sub-agents and with a back-end
database and with, you know,
integrations. What does it actually look
like? And then once it was able to do
all that planning, it started building.
And it built and built and built and
then I had it go in this test loop where
after it built, I didn't want it to give
me a POC. I wanted it to put like 50
agents through it to have them go
through the admin experience, the
sign-up experience, the, you know,
creating an event type experience. They
they tested the thing for me so many
times before I even had to get in there.
So, they basically went in this loop
where they were building, finding bugs
while they were testing, and then fixing
the bugs, and then testing again,
finding more bugs, and fixing the bugs.
And this alone went on for days. And I
just think that whole like agentic,
autonomous testing loop is just so so
cool. So, anyways, after that what I did
was I got my hands dirty a little bit,
and I didn't love what came back. Cuz
initially what came back was an app that
looked really really vibe coded. So, my
next thing I wanted to do was I wanted
to rebrand. It came through and it was
originally called Tempo Cove. So, like
locally, if I go into my project real
quick, you can see right here that it's
still a project called Tempo Cove inside
of my Herc 2 because um,
that's what it wanted to name it at
first, which I didn't love. So, I did a
rebrand, so now it's called Snag Time. I
think that I kind of redesigned the UI a
little bit better as well.
So, we did a rebrand and sort of like a
redesign, and this was just me giving
some feedback. And then from there what
we did is we just did a bunch more
testing. So, one thing that happened
that it didn't catch was it was like
really, really laggy. I don't know why,
but it was so slow. So, we were doing
like performance enhancements. Um on the
actual booking link, it just like my
mouse was glitching, typing was slow, it
just wasn't very responsive. So, we
optimized that. I did a slash goal
prompt and I said, "Hey, I want you to
cut down all of this like
load time. I need you to make this like
10 milliseconds instead of like, you
know, 1 second or whatever it was." And
it did a lot of enhancement on the
actual laginess and responsiveness of
the site itself. I came back in. The
fourth thing that I did was I did more
um more designing. I mean, I I know it
still doesn't look great, but like the
UI Oh, oops, that's not how you spell
it. Not only was the UI a little bit
weird, but the experience was weird. So,
I kind of moved around some of the
buttons a little bit. I'm obviously not
a design expert and like I said, this
isn't like the most amazing thing ever
still, but trust me, it's better than
what I got. So, really the point I'm
trying to make here with showing you
what I had to do was that yes, the
initial slash goal prompt was awesome.
And yes, I was able to get so much done
with just a few prompts, but I don't
want to also discredit how hard it is to
build and scale a SaaS product. I think
there's a big difference between
building a product that you can use
internally for a small team and building
something that you want to truly scale
like tens of thousands of dollars per
month,
inference, databasing, there's going to
be so many bugs, there's going to be so
many feature requests. Even if I was to
just adopt this fully internally, which
I want to,
I'm going to find so many bugs and I'm
going to find so many things that I need
to take ownership over or someone on my
team needs to take ownership over. So,
it's not just as simple as a few prompts
and you now have something that can, you
know, stand the test of time. So, now
that that kind of, you know, I guess
kind of boring stuff is out of the way,
let's talk about this. So, first of all,
how long did this take me?
Well, this actually took 5 days and 5
hours of actual agents running and
coding, which I thought is pretty
interesting. In total, this took This
was like a 2-week thing because, you
know, I'd shoot off prompts and then I'd
work on other videos and sometimes it'd
be sitting there idle for a while, but
actual working was about 5 days. So, in
that 5 days though, it was an aggregate
of 334 total hours of different agents
running. Now, they were running in
parallel, doing things in parallel, but
334 hours of just straight Codex going
to town on my account. And throughout
this process, it only spun up 76 agents.
Now,
these were unique sub-agents and I think
that what happened here was it reused a
lot of agents. Like agents would come,
you know, they'd come, they'd grab a
task, they would then do something and
then they'd report back and then they'd
sit there and wait. I think that's what
happened. What I was kind of interested
in was, you know, as far as how many
times it actually delegated work to
sub-agents, this was way more in at
least
300, I'd say, because I did so many
testing loops and verification loops
where I had 50 agents at least going out
as a swarm to click around and try to
break the app. So, that was the
sub-agents. Let's talk about the cost.
Input tokens was 32 billion, 103
million,
178,000 736 input tokens. Output tokens,
47 million, which I actually thought
might
like I I was expecting that to be more,
but then when you look at the actual
cost in dollars, this was a $15,000
project. Now, I was on my Codex 200
bucks a month plan, so I didn't pay
$14,000, $15,000, thank goodness.
But it's interesting because
$14,000 is roughly what you get out of
maxing out a $200 per month Codex plan.
Whereas in Cloud Code, if you max out
that 200 bucks plan, it's about $8,000
in inference. You are getting about
$6,000 more inference out of Codex than
Cloud Code if you max out the plan and I
maxed out this plan for sure when I was
running this. I even dipped into the
usage credit territory, so
probably
150 bucks of this total cost was me
actually paying out of pocket, but the
rest was just my 200 bucks a month plan.
So, anyways, hopefully you guys find
those stats interesting, but like I
said, this would not be completely free
forever. If I wanted to truly use this.
It would be me having to probably shoot
off a few prompts every month, making a
few enhancements every month as new bugs
pop up. But for the most part, it's
probably better than paying a
subscription if you're willing to
dedicate some head space to actually
maintaining this thing on the back end.
But anyways, if you guys are interested
in kind of watching what this full
process looks like when it comes to
connecting some of the, you know,
credentials and integrations and things,
then definitely check out this video
right up here where I basically did like
a live build all day where I just built
a different SaaS product. So, check it
out right here. I'll see you guys over
there.
