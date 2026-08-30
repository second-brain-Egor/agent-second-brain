---
description: "Transcript — project"
type: project
last_accessed: 2026-08-24
relevance: 0.91
tier: active
---
So, I've been using Deep Sea Carness for
the past week now, and I found a lot of
things that I really like about it, and
a lot of things that I also don't really
like about it. So, today I'm just going
to give you guys my honest thoughts,
break down what I've been using it for,
how it feels, and I'm also going to be
specifically talking about it in
comparison with Cloud Code since I know
that's on a lot of you guys' minds. So,
let's not waste any time and just get
straight into this video. Okay, I'm
going to try to do this in about 60
seconds. If you've never heard of Deep
Seek Harness, what is it? So, Deepseek
has different models, right? We had a
big Deepseek moment last year, Deepseek
R1, and then we have like DeepSeek V4
Flash and Pro right now. Decent models,
pretty cheap, but we have a harness now
from Deepseek, which is open source, and
it's free. So, as we know, we have
something like Codeex, which is the
harness, and the AI models that you can
use inside Codeex natively are GBT 5.6
Soul, GBT 5.6 Luna, things like that. We
have Cloud Code, which is a different
harness, and the AI models we natively
use inside of Cloud Code are Cloud Opus,
Cloud Fable, things like that. And now
we have a Deep Seek harness which has
other AI models inside. I mean by
natively we have the Deepseek models,
but you can also add any of the other
models. You can add Opus in there. You
can add GBT in there. You can add Kimmy.
You can add Meta if you're crazy enough
to do it. You can add basically whatever
you want in there. Now, yes, you can
also do that with these harnesses as
well, but they're not exactly like made
for it or promoted as much. But also
things like OpenClaw, that's an agent
harness. Also something like Hermes
Agent, that's an agent harness. So it's
not groundbreaking new tech. It's just a
new harness. But what's really cool
about this one is because the harness is
open source, we can like fully customize
it. So with a closed source harness like
Cloud Code, it has its basic kind of
like prompting rules and it has its tool
calls and it has its loops and it has
its agentic harness that we can't touch.
We can basically look at it like a car
that we can sit in, we can drive it, we
can change out the model of the engine,
but we can't move things around. Whereas
with our deep sea harness, the open
source harness, we can switch out the
seats. We can switch out the steering
wheel. We can switch things out. We can
change the way the agent actually
behaves under the hood, which is pretty
cool. And that's why a lot of people are
freaking out because if you go back to
the site, it literally says everything
is a plugin. And so by that, they don't
mean just like skills and like MCP
servers. They mean every capability is a
plug-in. Tools, skills, sessions,
sandboxes, storage, loops, the UI. This
is all a plug-in environment. And so I
will just be honest about that real
quick. In this video, I'm not going to
be talking about plugins that I
installed from other people or plugins
that I've built because I wanted to see
out of the box what this thing felt
like. And I will say about plugins, be
careful because if people are giving out
all these open source plugins, you don't
know what might be in there. So, be
smart. Have Cloud Code or have Codex
review the plugins before you ever
install anything like that off the
internet. Okay, so here are some of the
things that I want to talk about today
when it comes to our DeepC Carnis. So,
the first thing is let me just open up
the UI and just show you what it looks
like real quick. So, it looks like a
chatbot, right? It looks like kind of
like the Chag app or whatever you might
be familiar with. It's not going to be
anything new or super confusing. You can
have products on the left. You can
manage your different sessions, things
like that. Pretty normal stuff. And if
you want to test this out, literally
what I did is I gave the GitHub link to
Codeex and I said, "Hey, help me set
this up." It opens this up in a local
host. So, this is completely local right
now. And then you're pretty much all
good. All you have to do from there is
you're going to go to your settings.
You're going to go to models and you're
going to put in some sort of key. I put
in an open router key which is why now I
can choose between all of these
different models that are available to
me on open router. Unfortunately you
can't by default use like a cloud
subscription or a codec subscription. I
have seen some plugins where people say
that it works. I haven't myself tested
it but if you are interested in that
then definitely look into that. But
default you're going to be charged here
by token you know API billing. Anyways
that's what it looks like. We'll look at
some other stuff in this UI in a bit but
let me just go back over here to this
screen. Okay, so let's talk about output
quality. This entirely depends on the
model and the effort, of course. I mean,
you have a harness, so that can do so
much, but at the end of the day, the
model is what's going to drive a lot of
the actual quality that you're getting.
If you put Fable 5 in here and then you
put in like a super small local model,
they're going to be a big difference in
the output, right? So, just get that out
of the way real quick. What's cool is
how quickly and easily you can switch
out different models and different
modes. Because actually, if you go here,
you can see that before I start a
prompt, I can be in standard mode, PTC
mode, minimal mode, or creator mode. So,
let me dive into these real quick.
Standard mode is what you're going to be
on most of the time. Full coding agent
with file editing, shell, file, web
search, blah blah blah. That's standard
mode. Now, PTC mode is really cool. It
almost makes me think of sort of like in
cloud code with that dynamic workflows.
It's not exactly that, but it feels more
like, okay, I've got this big task. I
have a lot of stuff that I want to run
in parallel. I've got multi-chain. Let
me just ch throw this on PTC mode
instead of standard mode. And I've
gotten some pretty cool outputs
comparing standard mode to PTC mode when
I did it like that. Now, I want to talk
about minimal mode because this is a two
tool coding agent with persistent bash
and whatever that means. But minimal
mode is really solid because it gets rid
of some of the context and it just kind
of executes faster. And for things that
you don't need to look through tons of
things or do so many different actions,
minimal mode is solid. It's fast. It
feels cheap. It feels efficient. But let
me show you one thing about standard
versus minimal. If I shoot off high, who
am I in standard mode, it immediately
has a context injection. It reads my
agents MD and my cloudmd and my cloudmd
local. Then it reads the deepseek system
prompt and then it looks in the skill
catalog. So that's basically what
happens right away. We get that
fullergentic loop and it understands
things about me. And we've talked a lot
about being tool agnostic and model
agnostic, right? And harness agnostic.
this thing immediately. I plugged it
into my AIOS and I didn't have to change
anything. It already feels like it's
right in my AIOS. Now, watch this. If I
start a new chat in here and I go to
minimal mode, hi, who am I? Watch what
happens. It doesn't do that context
injection right away. So, this is almost
more like you're getting one-off chats
and you're trying to do quick tasks.
You're not getting that whole like I'm
in Cloud Code or I'm in Codeex and I'm
in my AOS. So, keep that in mind. But
what that does mean is I didn't have to
change like anything in order to use my
Cloud skills and my Claude context and
all of that kind of stuff. So that is
pretty cool. Okay, let's go to cost. So
the harness is completely free. You
could run this harness 24/7 with a free
model and you would never get charged.
But for inference, that's not free.
Deepseek models are cheap. They're
pretty solid. Deepseek V4 flash is
really good. Deepseek V4 Pro is also
really good. Um, obviously Flash is
cheaper, but both of those models can't
see anything. So, I had Deepseek V4
Flash is what I was testing this this
harness on for the first couple days and
it was really good. But when I was doing
things like this, for example, I made
this website with Deepseek V4 Flash in
the Deepseek harness and it's really
solid, right? It took these assets. It
had my brand guidelines. It has the
scroll thing. It has like this standard
feel matches the brand guidelines. But
look at this. This is where something
that Codeex or Cloud Code would have
never let happen because of the
verification checks and because of the
ability to screenshot, look, reason,
iterate. There's a lot of things when it
comes to a UI and design perspective
that the Deepseek models will not be
very good at because it can't
screenshot, it can't look. Now, that
doesn't mean that Deepseek harness
couldn't be good at design. It just
means that the the models that you're
putting inside there, you have to be
aware of what are their strengths and
weaknesses. And so similarly when we get
to tokens, this can be really really
cheap tokens. So like let's say you're
using a um local model or you're using
one of open routers free models, really
cheap tokens, but guess what? If it's
not an efficient harness or if the model
is so bad that it's not running
efficiently, then ultimately that's not
really that cheap. So token, you know,
you look at your 1 million input, 1
million output, those numbers can be
deceiving sometimes because it's also
about efficiency and cost to completion
rather than just cost for tokens, right?
Okay, reliability. It feels very
promising, but it certainly feels like a
preview. You can see that it literally
says, you know, this is a developer
preview, and that's what it feels like.
There are some bugs. There are sometimes
it just stopped working for me. There
was literally one time where it locked
my mouse. Like my mouse could only move
in a square that was about this big, and
I was like, "Uh, CEX, can you help me
out?" I don't know if I just got hacked
or something, but it was able to fix it.
There are some bugs. There are some bugs
with like the the compression. Sometimes
it just feels like it completely forgot
what I was talking about. I do like the
direction. It feels like it has a lot of
promise, but like I said, there are some
things right now that just feel a little
bit buggy when you're getting into like
long sessions or you're trying to work
on some sort of big project. So, just
like I said, long sessions, you get some
compaction bugs and sometimes you get
some context regressions. You could also
argue that's a little bit user error and
yeah, I was trying to see like where it
would break and I was trying to see what
would happen and like context rot
territory, but it did overall the UI
still in some places felt a little bit
buggy. Customization though, this is
where this thing absolutely crushes.
It's not even close to codeex or claw
code. Like it's way in a different
league, of course, because you can do
whatever you want in here. If I go back
over here, I realized that when I was
talking about these harnesses, I stopped
talking about these modes. But look at
this mode. This mode is called creator
mode. This is literally when you want to
create custom agent presets, you want to
build plugins, you want to change the
UI. This is how you do it. So, you would
turn to creator mode and you'd say,
"Hey, can you like build me this for my
harness?" And look at this. This is
another bug, right? I'm clicking on
creator mode and it's just instantly
switching back. So, little bit of a bug.
I would have to restart the harness and
it probably be fine. But also, if I go
to my settings, you can see here that
when you go to your plugins, you can
change these things right away, right?
Like our shell, you can change these
settings. You can change the agent loop,
you can change the web search provider,
or you can put in the DC provider. And
then you can have this list of plugins
where it has all of these things that
you can turn on, turn off, you can
customize these. You can also, like I
said, there's a bunch of GitHub repos
out there where people have been
building custom Deep Sea Carniss or DSH
plugins, but like I said, I didn't want
to focus on that in today's video
because I wanted to just see how this
thing felt on its own. But the
customization is unmatched. Here's the
thing though, for me personally, the
majority of the time that I'm using
Claude Code and Codeex, it's for video
editing, it's for research, it's for
knowledge work, it's for document
creation, I have never felt a gap in
Claude Code or Codex where I'm like, I
really wish the harness did this, this,
and this. I really wish I could
customize the harness in this way. Now,
if you're a hardcore developer, if
you're building products, you probably
have had those moments. And if you
actually have a pain in your typical
dayto-day, week to week, where you're
like, man, I want to customize my
harness, then this is going to be for
you for sure. Me personally, I have some
use cases in mind where I'm going to use
this. Maybe I'm getting close to my
limits. Maybe I have a bunch of
knowledge work I need to get done or a
bunch of research and I can, hey, come
into Deepseek. I can put on a really
cheap model in here and then just go
ahead and shoot that off in Deep Seek
and boom, it's going to be good. But I
don't have that need to build my own
harness. At least not right now. I think
though, seeing how this is waking people
up and seeing like the energy around
this idea of wow, like we might soon be
able to all have our own custom
harnesses that are really, you know,
custom made for us. It's very cool,
especially because when you want to if
you run into some issue or, you know,
something's going wrong, just say, "Hey,
switch to creator mode. Let's build a
fix for this. Let's fix what just
happened by building a custom plugin to
this harness. And I think that's really
cool and I think that's where we're
headed. So finally, the question I
wanted to sort of end off on here and
I'll still run through some more
examples is that does this replace
Claude? And I would say no. No. I mean,
if you want to do deep deep stuff, I
still think that the Claude code harness
is going to have your back. I also think
because if you want to use like Opus,
then you're going to get way better bang
for your buck on the subscription inside
of Cloud Code than if you used Opus
inside of this DeepC harness, which I
did a lot of testing with that. I'm
going to get into that in just a few
minutes here. Um, and similarly with
Codeex, I just think that right now for
what I'm doing, this does not replace
cloud code to me at all. This is not a
free cloud code. This is just a free
harness and you can switch out different
cheap models if you want, which by the
way, you can use any model you want
inside Cloud Code and Codeex 2. You just
have to configure that. I've made videos
about that if you want to check it out.
I'll tag one right up here. It'll
probably be right up here on putting
your own model or a different model into
Cloud Code. So, if you're seeing that
like Deep Sea Carness is a free cloud
code, it's not. It's a completely
different harness. So, let me show you
some examples of that. The first thing
that I've noticed about Deep Sea Carness
is it's super super fast. Like this
thing will find things in my AIOS
quicker than Claude. So, for example, I
would say, "Hey, can you remember that
project we were working on last week
where we talked about this, this, and
this. I don't remember what it was
called, but can you go find it and pull
it up?" And I did that same prompt at
the exact same time to both systems
multiple times. DeepSeek blew Cloud Code
out of the water. Like, I'm talking 1
minute in Deep Seek and five plus
minutes in Cloud Code. Let me actually
just show you guys a real quick example
of that. Okay, so shooting off the exact
same prompt at the same time to these
different harnesses. I've got a huge
wiki in here. This is my AI operating
system. It has to look through so much
stuff and it's going to be my guess is
it's going to find it quicker over here.
Actually, sorry. The screen's a little
bit off. Um I I think that it's going to
find it quicker in DeSseek because every
time I've done this, it has found it
quicker in Deep Seek. What is going on
over here? Okay, I'm sorry. Hope that
that isn't annoying. But yeah, let me
just show you when this is done. Look at
this. So already over here in Deepseek
about 50 seconds, it found the
transcript. It searched through
everything and it gave me the two
sentence summary and cloud code over
here is still searching. These are both
using the same model. So the harness
here just works so much more
efficiently. And even when I'm, you
know, pushing out sub agents, hey, can
you guys spin up a bunch of sub agents,
do research? I've done a ton of tests of
literally sidebyside prompts, exact same
thing. And Deepseek just gets the answer
for me so much quicker. It's so
consistently quicker. And while this is
still going, let me show you the
trajectory thing in Deepseek. So if I
click into directory, it actually shows
us a super granular like intermediate
steps and it's all in one spot and this
continues to go out through the whole
session and you can also download the
session log. So what's really cool about
this is think about how when you do
something like this and you want to go
back and say hey turn that into a skill
for me or hey turn this into a plugin or
did you see what happened in this
session? Can we build a plugin to fix x
y and z that just happened so that next
time your harness agentic loop runs this
doesn't happen. This is pretty cool. And
I also like the direction that they're
taking this visual sort of like
trajectory
in because every time you shoot off a
prompt, it'll show this is the user
prompt. Here's all the context that came
in. Here's all the things that happened.
I really like this. Okay, so Claude Code
is still searching for that transcript.
I'm just going to put him away right
now. We don't really need to watch that
happen. It's kind of sad. Let me talk
about some other things that I've done.
So, I shot off a prompt to both of them
and I asked them to look through my
YouTube data to find the analytics that
have been recently pulled and build me a
little Excel sheet that breaks it down.
I think this is a really good example
that I typically like to see if agents
can do because it uses some skills. It
uses some um like API calls and it uses
some like reasoning and structuring
scripts to build a deliverable. So, this
is the first one. This is the one that
was created for me by Deep Seek Caress
with Opus 5. So, same model under the
hood and this one came back in about 3
minutes whereas the other one from Cloud
Code took I think it was 17 minutes. So,
big difference like big big difference
there. Let's talk about quality though.
So, Deep Sea came back with the
performance data on the trailing three
months. It's got videos. So, what I
really like here is it also colorcoded
these columns on views and engagement
rate which was pretty cool. We have top
and bottom and it created this top 10 by
views chart. Now, it's kind of tough to
see because like it doesn't actually
label anything. It literally just shows
graphics, but it does correlate to these
top 10 over here, which is cool. And we
also have the bottom 10. We go into
monthly trend. We can see once again, it
created a little chart for us. What I'm
noticing about this is it's pretty
simple, but it delivers me the
information in an effective way because
it's easy to interpret. It's not too
wordy. It's not word vomit. We have tag
analysis as well with another
color-coded section. And then we have
notes and sources. Now, let's take a
look at the one that Claude Code made
for us. So, this is the exact same data.
Um, obviously, this one took longer, but
this one's a lot wordier. Arguably, this
has better analytics. The drill down's a
little bit better. It's a bit more
specific. It gives us this last 90 days.
The metrics are coming in just as good,
if not better. We don't have any color
coding. It gives us more tabs. It gives
us more data. Honestly, it even did all
videos, which is like all 467 videos. It
did top 50. It did monthly trend. So
this as far as quality was a better
output. I will say though like this is a
bit word vomit. But I will say I also
gave them both a very vague prompt. I
literally just said create me an Excel
sheet showing me the data. If I would
have instructed them, hey this is what I
want to see. These are my pain points
and this is what I'm concerned about.
Then they probably would have both
tailored something a little bit more
specific. But I wanted to see what they
did with a vague prompt. Here's another
one. I asked them to use my storm
research skill to build a report about
um the effects of sugar on the body. And
so we got these two outputs. This one is
from Claude Code and this one is from um
Deep Sea Carness. Now, they look the
exact same because it's a skill. They
use the skill. They were supposed to
structure it like this. So, they both
followed the skill well, which is good.
But when we actually like read, I'm not
going to read all this out to you guys
or make you read all this. But when I
read these and I looked at the sources
and I looked at how they did it, here's
what I found. Claude Code did this in
about 5,000 words, whereas Deep Sea
Caress did this in about 4,400. So,
Claude Code had a little bit more
wordage in here. We also see that cloud
code had 26 sources and then we had deep
sea harness with 14 at least 14 that
were considered loadbearing. I think in
total it actually found 22 I believe.
Now when it comes to the actual like
breadth cloud code was way more
in-depth. It was way more scientific and
deepseek was way more about like hey
let's make this relatable. Let's make
this practical. I'm not saying that one
is better than the other based on what I
prompted. I just think that that's
really interesting how much that harness
affects the underlying same exact model.
Cloud code also kind of typically came
across as more conservative with its
findings and with its facts. While
sometimes deepse harness was like too
confident. It like it told me something
that I was like h I actually don't know
if I agree with that. So overall, which
one of these do I trust more? I trust
the Claude Code one more. Like I'd
probably be more willing to give the
Claude code deliverable to a client or
to my team compared to the Deep Sea
Caress one. But also keep in mind that
the skills that I've built that I'm
having DeepC use were built for Claude
code. And you you all should hopefully
understand that when you upgrade your
model or you switch harnesses, the
skills are interpreted a little bit
different every time. Which means if I
was to build a skill specifically for
Deep Seek Harness, it would probably do
a really really good job and it would
also be a lot faster. So, the point I'm
trying to make here is I think it's good
that you guys are like listening to my
advice and you're listening to maybe
other people on X or YouTube, but
ultimately you need to get in here, get
your hands dirty with Deep Sea Carness,
put in the models that you want to try
and just test these things out for how
they work for you specifically. So,
anyways, hope you guys found this one
insightful, and if you did, please give
it a like. It helps me out a ton. And as
always, I appreciate you guys making it
to the end of the video, and I will see
you on the next one. Thanks guys.
