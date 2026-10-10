---
type: project
last_accessed: 2026-10-09
relevance: 0.98
tier: active
---
So, Grockbot just dropped two major
upgrades, and today I'm going to talk
about what those are, why they matter,
and what you should do about it. And
then I'm also going to tell you guys my
number one favorite Grockbot hack that
you guys can all get set up in about 5
minutes, and it will truly change the
way you work. So, let's not waste any
time and just get straight into this
one. Okay, so yesterday Elon Musk came
out and said that Grockbot is going to
be using the best back-end model for any
given task, including Cloudov 5.5 and
other things like Midjourney, which is a
image model, and Sunno, which is a like
AI music model. And then he said also
other leading APIs. So basically
Grockbot will understand the task and it
will route to whatever model is most
likely to give you the best outcome. Now
from here someone basically said hey
that's super cool. I have some questions
about how this works. Obviously I had a
lot of questions too like can we see it?
Can we control it? Blah blah blah. How
does this affect our weekly usage? And
what we now know is that this will be
running on Opus 5.5. I assume by
default, although we don't unfortunately
really have any visibility into what
model it's using at the moment or what
effort level or anything like that. Elon
Musk then came back and said, "Okay, so
it will use whatever will achieve the
best outcome for users. Simple questions
will route to small fast models while
questions with complex answers will
route to large models." So ideally, this
is going to be optimizing and getting
you to essentially getting your usage or
your weekly limit to last longer. And he
said, "However, most bot requests are
pretty simple and will be handled by a
lightning fast version of Grock 4.8 when
that drops. The idea is to give users
the best possible combination of speed
and intelligence. Now, I think this is a
really cool idea. I wish that we had a
little bit more ability to control and
to manipulate that because then it's
basically like Grockbot is the harness
that we could control with any model and
ideally any subscription, which would be
really cool. And that's a little bit of
foreshadowing to the hack I'm going to
show you guys in the end. But of course,
some people aren't super happy about
this. People have been asking if they
could opt out. They don't want it to be
going to Enthropic. They purposely got
on Grockbot because they wanted to use
Groc models. So whether you fit on the
side where you really like this or you
really don't, that did happen and
unfortunately we don't have a lot of
visibility into it. But I think that
honestly I think it's a step in the
right direction. I think this is pretty
cool. And then later that day we also
saw this which is Grockbot can now
search, read and monitor X which is
awesome because you know obviously X
Elon Musk Grockbot but normally you had
to actually pay for that. So what I
would recommend that you do right now
about this is you go into your Grockbot.
You can see I have one called X that
helps me monitor X and find posts and
and gives me good like updates and
stuff. And I asked it if it saw the
update. I wanted to switch that over
from our paid API, which was the X API,
the developer API, which still wasn't
too expensive, but you were still paying
every time it pulled in a tweet. And now
this is builtin X search, and it's
completely free. It is native
functionality of Grockbot. So, I then
asked it to switch over all my routines.
And I wanted to make sure that all of my
other Grock bots because a lot of these
Grock bots touch X and search through X
when they're collecting data, doing
research, helping me plan things,
whatever it is. And I wanted all of them
to be aware of that. So, this bot X
messaged all these other bots, minor,
pod, eyes, AIS, news, motion, all these
other bots that might need to use X and
that do use X and now they all have
awareness of this. And then I was just
curious about how much it actually did
cost us the old way. And like I said,
it's not too expensive. We maybe were at
104 at one point and now we're about 89
and we were spending about five bucks a
week with all the X searching that we
were doing. So like I said, not a huge
deal, but you might as well take
advantage of this and switch over to the
native use. So then I went over to minor
who I hadn't talked to yet today and it
did get messaged by X earlier and I said
go on X and see what people are saying
about Cloud Motion and then tell me how
much that cost you. So it found these
five tweets about Cloud Motion and then
it actually said okay this cost me zero.
I use the built-in X access. I didn't
touch your paid X API credits, but you
do have a free daily allowance of a,000
reads. So, today you have 995 left and
that resets every night around 7:00 p.m.
Central, which would make sense because
I shot this off right after 7:00 p.m.
Central. And earlier today and
yesterday, I've been doing a bunch of X
searching with this new thing. So, that
makes sense. But sometimes you have to
take this with a grain of salt because
sometimes Grockbot doesn't always know
exactly how it works. Also, this might
be running on Opus 5.5 as we speak. So,
grain of salt, but this seems like it
makes sense. Real quick, guys, I've got
this completely free kit that I want to
give to you all on helping you build
your own AIOS. Whether you need to build
it or whether you need to scale it up,
this is the full kit. It's based on my
actual framework I call the Herk Loop.
Context, connections, capabilities, and
cadence. This thing comes with six
skills. It helps you set up a brain. It
helps you set up your priorities and
your business and it interviews you. It
is exactly how I built my own actual AI
operating system and it's how I'm able
to move so fast. So, if you guys want
this, the link for this is down in the
description. But anyways, let's get back
to the video. Now, before I talk about
this last hack, there is one thing that
I think is really interesting to think
about, which is the actual model
routing. So, let's say this is using
Opus 5.5 and at some point it'll be
maybe by default using Grock 4.8. What I
think is really interesting and what I'm
going to make sure I'm doing is I'm
going to make sure I'm breaking up my
skills because think about that. If you
have a skill that does like seven things
and it's just one mega skill, that might
be fine. Like that might be fun right
now because it's like, oh, run my, you
know, YouTube video creation skill and
it does everything. It does the
ideation, the research, the pulling in
the comments, the, you know, the
animation, the packaging, it does all
that in one skill. And maybe that works
best when you have one agent that can
just do it. But when you really think
about how this is going to be routing on
the back end, you want to make sure that
you're truly getting the best experience
of balancing intelligence and quality
and uh cost. Because if you have a skill
and let's say it's seven pieces and four
of those pieces could be easily Grock
4.8, faster, cheaper, but three of them
you might need opus 5.5 for things that
are more reasoning or more design, more
taste. Then you want to break those up
into different skills. That's at least
the first thing I thought about was
like, oh well, I don't think that the
model is going to be rerouting or switch
routing midtask. Like it's probably
going to understand load the full
context and then it's going to choose
the best model because then you'd have
other things like the the cache expiring
and you have like this whole handoff. So
it's probably going to be working where
it's like it's just one model selection
per prompt. I guess. And then we've also
got the idea of, okay, what if minor,
for example, shoots off off my prompt,
shoots off prompts to Becky, Dan,
Klouse, X, Nat, and Grockbot. And now
we've got six other types of model
selections to be made. I really hope
that they start to bring us more
visibility. I think it would be great if
we could actually see what model they
were using, what effort level they were
using, and if we could control that, or
if we could build skills and say, "Hey,
for this skill, please run Opus or for
this skill, please run Grock." Because
that is a big deal. a skill won't
perform the same way for different
models and that's just the truth. So, we
want to make sure that we are getting
more visibility. I really hope the
Grockbot team will bring us that
visibility and bring us that
customization. But anyways, those are
things to be thinking about. Those were
two huge upgrades that we got this week,
which I am very happy about, at least
the direction they're going in. But now,
let me talk about one of my favorite
hacks with Grockbot that's changed the
way that I work. This isn't actually
using your claw subscription. This is
still using the Grockbot subscription.
Whether you get that through Cursor or
SpaceX or what, Super Grock, whatever it
is. It's kind of confusing, but you can
have all your Grock bots use your claw
code subscription or your codec
subscription, which is awesome because
every single one of your bots has their
own computer. As you guys know, they
they share one big computer. They share
a file system, but they own but they all
kind of have like their own monitors
like their like what's on their screen
is different, but they share the same
file system if you open up your file
manager. So anyways, because they have
this, they have a terminal, which means
in the terminal, they can install cloud
code and codecs and other CLIs and they
can just run them. And all you have to
do is authenticate in the same way you
authenticate in when you're on your own
machine. So literally just go to one of
your agents. As you can see right here,
this agent Klouse is opened up inside of
Cloud Code in my repo on Opus 5.5 and
it's using my team plan. So it's using
my actual subscription. So now because
this cloud computer is always on, you
essentially have cloud code always on in
your pocket and you can just use um one
of your agents to play with it or you
could create a new agent that's
literally just called cloud code and you
can create a new agent that's literally
just called codeex and now in your
pocket you have these subscriptions and
it's really cool because literally all I
did here you can see is I said I want
you to on the desktop use my cloud code
subscription. Just go to the terminal,
open that up, it installs it. It then
prompts me to sign in. So this is where
you take over, you sign in, you click
authorize and then you're good to go.
And then you just want to have it copy
in your repo. So clone in your AIOS
repo, clone in your projects, and then
you're pretty much all set up because
you've got your cloud. B, you've got
your skills, you've got your agentmd,
you've got anything that you need in
there. And then the final piece to be
aware of is you want to transfer over
your file because obviously you want all
those skills and all of the real value
in your AIOS to be transferred over. And
so that's why I don't like relying on
like cloud desktop app plugins or codeex
desktop app plugins. I like relying on
API keys so that if I switch over to
something like this, I can just do one
simple migration of one file and now
Grockbot can do everything that I can do
on my own desktop. So, this has been
super great. You know, we've we've seen
Dots, we've seen um Muse, and they could
pretty much do the same thing. They have
computers as well, but I have just been
liking Grockbot so much more than those
two tools. And I do truly use this thing
every day for just really quick and easy
and simple automations that I've got set
up in here. As you can see, quite a few
Grock bots working for me. So anyways,
get this stuff set up. Hopefully this
was helpful. Hopefully you enjoyed the
video or you learned something new. And
if you did, please give it a like. It
helps me out a ton. And as always, I
appreciate you guys making it to the end
of the video. And I will see you all on
the next one. Thanks everyone.
