---
description: "Transcript — project"
type: project
last_accessed: 2026-08-24
relevance: 0.91
tier: active
---
Today I'm going to be building an AI SAS
product right in front of you guys
pretty much live. I'm going to be
basically starting at the complete
beginning. I don't even have an idea
yet. I'm going to go through ideation,
planning, building, testing,
authentication, payment processing,
connecting it to a real domain. I'm
going to do all of that in front of you
guys so that after this video you
basically know exactly how you can find
some sort of idea, turn it into a
product, and then actually go look at
getting some customers for your product.
So, I don't want to waste any time.
Let's just get straight into the video.
So there's six major P's that we're
going to be focusing on today when we're
building this sort of like SAS sprint.
So the first P is pain. I'm basically
going to pretend that I am in your shoes
right now. You might be starting from
completely zero, a little bit of AI
knowledge, but you don't have an idea or
a product. So that's what I want to kind
of simulate today. So pain, we obviously
want to build something that people will
actually use. Now in a perfect world,
the way that I would actually go about
this is I would go get feedback. I would
say, "Hey, here's my business idea. How
much would you pay for this? Would you
pay for this?" and I would get a bunch
of validation before I actually build or
I'd build like a little P proof of
concept to just say, "Hey, here's a
demo. When I build this out for real,
would you build this? Would you guys
find this value?" And then I would go
build it. So, basically sell before you
build. So, we're going to be using AI
here to help us find some pain points
and find the business idea. From there,
we're going to step into promise. It has
to be super clear and basically one
sentence on the landing page. What does
this tool do? How does this tool promise
that it's going to answer the pain that
we already found? From there, we're
going to be actually doing the product.
We're going to be planning it out. We're
going to be building it. We're going to
be testing it. And then, you know,
that's basically the actual core product
that we're building today. The fourth
one is the plumbing. So, we're going to
have to wire up things like the payment
processing, things like the
authentication, managing the database.
Obviously, when you have a product like
this, the goal is that you one day can
scale it to, you know, potentially
thousands and thousands of users. So,
you need to make sure the plumbing is
there to actually handle that. The fifth
one we have is the packaging. So, making
sure we have stuff like the brand
guidelines, consistent colors, you know,
it just feels like a professional
product that someone could actually like
maybe go to the website and just buy or
subscribe to. And then the last one is
proof. So, basically all throughout this
whole thing, we're going to be doing so
much verification because at the end of
the day, I don't know how to read
Python. I don't know how to code in
Python. I don't know what other
languages we might use, but AI can do it
really well. But it's on us to be the
project manager, to be the one that's
saying, "Hey, verify this until you're
like confident that it's done and prove
to me that you're confident." So, it's
all about how can we actually utilize
the more intelligent and more capable
coding agents that we're going to be
able to use, but we still remain in
control of the judgment. And you know,
at the end of the day, if the product
fails, it's on us. We can't blame AI, we
blame ourselves. So, I'm sure you guys
are curious about what tech stack we're
going to be using today. We're going to
be using three main ones to sort of
drive everything, but I'm sure there's
going to be, you know, other APIs or
other payment processors. There's going
to be a lot of things that go into this
build, but the three core that I want to
call to your attention are we're going
to be using codec. So, I have the chat
GBT desktop app that I'm going to be
using. I'm going to be using codec
through this. I'm also going to be using
Claude, so Claude code inside of the
Claude desktop app. So, you can download
that as well. And then finally, we're
going to be using Glido to actually talk
to everything. It's basically going to
be the voice layer so that I'm not going
to be bottlenecked by typing. I'm just
going to be able to talk as fast as I
can. and do this as fast as I can. So,
if you want to sort of follow along with
this video, then I would definitely
recommend you get all three of these
things so that you can basically move
quick and you can have different AI
models and different coding harnesses
get different perspectives on your
build, which I think is really helpful.
If you prefer codecs and you just want
to use codecs or if you prefer claw and
you just want to use claw, that's
totally fine. But I found it to be very
helpful to be able to have different
coding harnesses and models take a peek
at what I'm doing and help me sort of
like play devil's advocate, stress test
it, things like that. Okay. Now, how do
I think about the difference between,
you know, our friend Claude and our
friend Chadigati or Codex or whatever
you want to call him? So, I really like
to think of Claude as my kind of like
thought partner. It feels more creative.
Especially if I'm able to come down here
and switch this on to Fable, it feels
like it has more of that wise old owl
sort of perspective. Whereas, when I
jump over here to codeex, this thing
feels like a Rottweiler. It is basically
going to take the task. It's going to
take the command I give it and it's just
going to execute and it's going to keep
executing and keep verifying until it's
good until it's done. And so I think
it's really great to be able to use them
together in tandem. And with that being
said, I'm going to start off our build
here in the pain section trying to find
an idea. I'm going to be using um Cloud
for this. And by the way, if you guys
are curious on where I'm actually
building this, what I did is inside of
my Herk 2 project, which is my AIOS, if
you guys have been following me for a
while, I've got a folder called Other
Worlds. And I made a new world in here
called AI SAS Sprint that's completely
empty. And this is the folder that both
Codeex and Cloud Code will be working
out of so that they can see the same
stuff. So anyways, let's get started
here. I'm going to open up Glido and I'm
just going to start yapping. All right.
So what I'm trying to do today is build
an AI SAS product. I'm trying to show my
audience how much they can actually do
with AI. And the first most important
part of building a SAS product is we
have to have an actual painoint. We have
to answer a problem or solve a problem
that the market actually has. So a lot
of my audience might not have you know a
big YouTube channel or a big community
to leverage data from and we have that
ability. So basically the idea is I want
you to use our primary data which could
be things like YouTube comments um
people talking in our school community
what are the problems they're having but
then also I want you to go on more of
the publicly accessible data like
secondaries forums of Reddit, LinkedIn
X, Instagram. I want you to look through
this type of stuff and help me identify
a painoint that we can actually solve or
a few pain points that we can solve.
What we're looking to do here is we're
looking to build some sort of AI SAS
product that realistically can be built
in one day. Something that is very
visual and the promise is very clear. So
it's not like a super super technical um
like CRM sort of product that they would
have to get onboarded to and that they
would have to get familiar with over the
you know a week or two get trained up.
I'm looking for something that people
can sign up for and get value
immediately. Like within five to 10
minutes, they can use it, they can
understand it, and then they'll get
value. So, what I want you to do here is
I want you to act as the orchestrator. I
want you to spin up different sub aents,
and I want you to do research, scrape
different methods, and then at the end,
come back, consolidate everything, and
just give me clear signals of a couple
ideas, and then from there, I will
choose. Let me know if there's anything
specifically that you need for me as far
as like API keys or if you don't have
access to certain data because I've
already set you up with my Herk 2
project which you can go in there and
you can use you know you might have more
reach into some things but just let me
know if there's anything that you can't
reach that you would really like to. So
obviously guys because this is sort of
more of like a challenge style video I'm
going to assume that you have a little
bit of previous like cloud code or
codeex knowledge. If you don't then I'd
recommend checking out this video right
up here. It's going to walk through a
lot of the basics, how you set up
different like environment variables,
API keys, and it will make more sense
when you then hop into a video like
this. So, if you want to check out that
full free course, check it out and then
hop back over here because you can see
here my cloud code was able to have a
YouTube API, school, community access,
X, firecrawl, perplexity. So, it's
spinning up five different research
agents in parallel in order to start
doing all this. So throughout this
challenge, I'm going to be thinking
about how can we do multiple things at
once just because we're trying to move
through this fast. And you know, it's
already 9:00, so we've already, you
know, used basically 15 minutes. And I
have a feeling that the majority of the
time spent in this challenge is going to
be the AI processing and us just waiting
for things like these background agents
to run rather than me actually building
or prompting. So that's why we're going
to try to stack as much as possible. But
I do want to wait until we know the idea
because then once we know the idea, I
think we can start having a different
terminal start to build out some of the
packaging like you know the title or not
the title, the name, the logo, the
colors, maybe even start building the
landing page once we have an idea of
what the promise is. But right now we're
just kind of bottlenecked. We're waiting
on the whole ideation and research
phase. So I'll check in with you guys
once I figured out what the product is
going to be. It's okay though because
while we wait I can have some coffee and
I'm working on a little Hermes agent
right here. So, you know, I'll just keep
monitoring but I can still be productive
while that's going on.
Okay, guys. So, it's almost 10:00 now.
So, that took quite a while. But this is
arguably the most important part because
the idea, the pain is the entire
product. That's what everything is built
around. So, let's take a look at what
this scraped. It looked through about
16,000 YouTube comments. It looked
through about 8,000 comments and, you
know, within posts inside of my plus
community. It looked at about 4,000
tweets and it also looked at Reddit. It
was still running at this moment, but I
asked how many it did. And it looked
through about 20,000 comments on Reddit.
So, this is the whole idea of being able
to outsource the thinking and the data
collection, but not outsourcing the
understanding. And that's exactly what
we're doing here. Because in order for
me to read this many comments and scrape
as much as this just did, it would have
taken me far longer than about an hour.
But now we have to look at this data and
understand what it's telling us and what
we should build. And it basically gave
us these final three recommendations. So
a client proposal and handoff pack. So
essentially what this is is you are
putting in basically the build or the
proposal that you are sending over to
the client and then it will come back
with a bunch of stuff like a document, a
diagram, a bunch of other things. So
kind of like helping you run an AI
agency. Then we have a social visual
generator. So carousels, infographics,
you know, to be able to post things on
different social medias. and then an ad
creative resizer. So, honestly, it
recommended this first one. I think that
fits more with what my audience is
actually looking for. It's a product
that I could fit right into an existing
product. So, it just makes more sense
and I think that it's very practical.
Now, one thing about this is there's
truly no moat that I see because someone
could use this product, they could then
um basically use it for a month,
understand how it works, understand what
they like about it, and then build their
own claw skills and their own systems
around it. And that is something that
you just have to understand when you're
building something out, especially right
now, the product game is kind of scary
because of how fast different tools are
evolving and how different things are
becoming open source. So really what I
want to recommend here is I was able to
leverage my own primary data and see
what my already paying customers want
and what their pain points are. And
that's exactly what you should be doing.
And if you don't have an existing
product or audience, you should really
be looking at your own subject matter
expertise. If you know a lot about
construction companies, then you should
be doing this sort of research and and
scraping for pain points but within the
niche that you actually understand.
Because otherwise, if you send off sort
of a generic prompt like this, and
there's nothing specific to you and your
knowledge, then you're going to probably
get the same AI recommendations that
everyone else is doing if they're
sending off some sort of product or some
sort of prompt like, hey, you know, help
me find a good business idea. So, the
idea is really important. And I also
want to show you guys something else
that it surfaced right here. So,
initially, remember how I said like,
hey, you know, maybe like 5 to 25 bucks
a month. It said based on the data that
price is too low and now it has direct
quotes. Reddit surfaced 835 price
sentences with a consistent band. So
like just a tool that does one boring
thing really well can charge 50 bucks a
month and people are happy to pay that.
You need 100 to 200 people paying 25 to
50 bucks a month for something that
saves them time every single week. So
let's say we're going to go off and
build this client proposal handoff pack
sort of product. Let's start figuring
out now how do we actually move forward
with this? We have the pain. We need to
start building out the promise, the
product, the plumbing, and the
packaging. And all the while making sure
that we're verifying and proving that
this all works as we're building. So
before we get going, let's just make
sure that our files are all set up so
that we're able to stay organized and
not get too messy. This is the only
thing that currently exists in this
project is one folder called research
with five different markdown files of
YouTube, school, blah blah blah,
competitive landscape. And these are
pretty in-depth, right? Like if I click
into this competitive landscape markdown
file, you can see that this thing is,
like I said, very in-depth. It goes over
pricing. It goes over tools with
different, you know, like actual
metrics. All of these are different
sources that I could click in and look
at. So, there's a lot of data here. I
mean, this thing ran for like an hour
just doing research. So, we're going to
be able to use all of this stuff later
because it's already in our project. And
as I'm using codeex later or clawed
later, it can read through these things.
Okay. So, what I want to do now is just
get set up with like our cloud. Mmd and
our agents so that the rest of the
project understands what we're doing.
All right. Great. So, we're going to go
ahead and move forward with sort of that
um client handoff product where they're
able to create an account. They're able
to send in sort of like, hey, here's the
workflow I'm going to build. Here's the
business that I'm building this for.
Kind of the portal that they're able to
manage some of these client projects
from. And they'll get the deliverables
like a branded PDF. They'll get
visualizations. They'll get diagrams.
And they will get other things to think
about to send over to the client like um
credential handoff information and
client expectations, things like that.
So, now that we know this is the
direction we're going to take this
product in, let's go ahead and set up a
claw.md file and just duplicate that
over to another one called agents.mmd
because I'm going to be utilizing both
codeex and cloud code inside of this
project. So, just help us get set up
with the project. Um, the idea once
again is that we're building out this
product in one day. Yeah, just go ahead
and get set up so that we can keep on
sort of like planning and building and
getting everything set up. Okay, so
we're getting some of this foundational
stuff set up and then we're going to
move into a planning phase. But before
we do that, what I want to do is I want
to get started on the packaging before
we actually start building this thing
out, just because we can do these things
at the same time. They're not really
dependent on each other. So the
packaging, so I'm going to be using
codeex for this because it has GPT image
2, which I think is the best AI image
generation model out there right now.
And we're just going to get started on
ideulating on the name of this product,
as well as what it's going to look like,
the color scheme, the feel. Okay, so
inside of our project, you should see a
research folder. We just did a bunch of
research on what product we actually
want to build inside of this project.
And we're ending up going with a client
sort of handover sort of like a AI
agency client management product where
people will log in, they will be able to
upload information about the project
that they're working on with a client
and it will create them, you know, a
proposal, a PDF, maybe even like the
audit. It'll give them the deliverables
based on their natural language and it's
going to be professionally branded as
well as there'll be images and diagrams
and whatnot. So, that's the idea for
this product. Ask me any questions if
you have any about it so that we can go
ahead and design, you know, like the
name of it and um you can give me a
bunch of different logo variations and
color schemes so that we can have a sort
of like a design system ready to go for
this entire product. And remember, these
things are working in the exact same
folder. You can see here the agents MD
and the cloud.MD just got created by our
other claude. And we have the research
folder with the five markdown files. So
these two projects are working on the
exact same thing. These two coding
agents are working on the same stuff. We
just have to make sure that they're not
like overwriting each other, which right
now isn't an issue because they're
working on very different things. Okay.
So as you can see, the clawmd and the
agents MD has been set up. What I'm
going to do now is I'm going to use a
skill called session handoff, which is
basically just going to give us a
summary of what's been done, files that
are important so that I can clear the
session and paste it back in. And if you
guys want to access this skill
completely free, all you have to do is
go to my free school community. The link
for that's down in the description.
You'll go into my free school, you will
go to the classroom, and you will click
on all YouTube resources, and you can
download everything for free that I ever
give away for my YouTube videos. And so
now that it's giving me this full
handoff, as you can see like where it
started, what we talked about, key
files, all this kind of stuff. I can
basically just copy that message. I can
clear out this um session because you
can see we were at like half of our
context window. Paste it back in. And
now it's basically going to pick up
exactly where we were on a fresh
session. So I'm going to use this
particular session to help us sort of
with the planning of the whole product.
But before I actually start prompting
this to do the planning, let's jump back
over to Codeex because it has some
questions for us. I apologize for the
jumping around and I know it might feel
a little chaotic, but this is us trying
to move fast and this is pretty
realistic of the way that I typically
like to work. I am sort of juggling
different sessions and I'm moving
between them relatively quickly. I've
found out that I can do that in a way
where I'm not sort of like um decreasing
my quality because of the jumping around
and because of the context switching.
Sometimes obviously if you're in deep
flow you need to stay on one. But when
I'm setting up a lot of these
foundational things I like to jump
around. It just helps me feel like I'm
doing more with less time. And you know,
we're kind of up against the clock here.
Okay, so the strongest positioning it
says here is to turn messy project notes
and workflows into polished client ready
deliverables in minutes. I like that,
but I don't feel like that's strong
enough yet for our actual promise. And
in order to do that, we have to sort of
think about our avatar and the pain
point that they're feeling. But it is
starting to kind of create a vision for
um what this is going to look and feel
like. So it's asking me about some
questions here that I'm just going to go
ahead and turn on Glido and start
yapping about. So to question number
one, I would say the main moment here is
that after they have gone through like
discovery calls and sales calls and
they're ready to send over some
deliverables to to actually close the
sale, they need that to be branded. They
need to be professional and they need it
to be consistent. And I think that our
avatar that we're looking at here are
people that are just kind of getting
started in the AI agency game or they've
been running one and they have a few
clients and they're starting to get
overwhelmed trying to manage the
deliverables and the things that they
need to do. So, that's kind of the
avatar we're looking at. We're obviously
targeting AI agency owners and their
pain point is just feeling overwhelmed
and feeling like they don't have a
structure to what they deliver to their
clients. Now, for number two, I think
the naming style, it needs to feel
something. Yeah, I think literal is good
because we have one very specific
promise that we're trying to make and it
should align with the name so that it
feels very consistent. It's very clear
what this product does. How should the
brand feel? I think it should feel
like premium consultancy. Number four,
should it be visibly associated with
Nate Herk? It should be completely
independent of my my name, my brand. Is
an available.com required or are there
domains such asapp? That's a good
question. Um, don't worry about that
right now. We will figure out the actual
domain to host this on later. I just
want to prioritize a good name for the
actual product. And then are there any
colors, brands, logos, or visual styles
you strongly like or dislike? I would
like to stay away from the color red and
I want this to feel very modern and
clean, but I don't want any of this to
obviously feel AI vibe coded or feel
like AI slop. So, it should feel
professional. It should feel clean and
help us also create the like oneline
promise that's a little stronger than
the one that you gave us earlier. And
then from there, I want you to start
iterating on different um logos,
different concepts, different color
schemes, all that kind of stuff so that
we can lock in a final decision. Okay.
So, now that that's off and running, I'm
going to let this thing cook. I'm going
to hop back over to the Claude session,
and we're going to get going on the
planning. So, it's asking us some
questions here, and we're not going to
worry about that yet. I'm just going to
block off that, and I'm going to tell it
what I wanted to do here. So, here's my
thought process. There's a lot that's
going to go into the build, and we're
probably going to want to utilize
different sessions to be able to build
different things at the same time
without getting in each other's way. So,
that's what I want this session to help
me figure out. So, what I'm actually
going to do is I'm going to switch over
to Fable because now we're really going
to get into the whole planning and sort
of like looking down the line and trying
to see if we can look like look around
the corners, right? So, I'm on Fable
here and I'm going to have it help me
sort of plan out the structure. And what
I want to do is I want to have like a
plan document in our files. I want to
have something that all the agents can
look at and pick up and basically see
like a running task list of what's been
done and what needs to be done and
what's maybe in progress so that they
can see what everyone's working on. And
I think that having a plan doc like that
will just keep this project feeling more
organized. So let me start yapping into
Claude here. All right. So I actually
have a different codec session helping
right now figure out the name, the
oneline promise, the logo, the color
scheme, stuff like that. Your job in
this session, you're Fable 5. You're
super intelligent. You need to help me
figure out and plan out the actual
build. So what that means is your
deliverable right now is a plan
document, something that you can use
when you are delegating work to other
sub agents to actually build. You're not
the executor. You are just the manager.
You're the project manager here.
So like I said, figure out what this is
going to look like from a building
perspective. If you don't yet have a
clear vision of the actual product, then
ask me some questions and let's
brainstorm about that a little bit until
you feel confident that you know exactly
what the user experience and on the
technical side what needs to happen in
order to build this out.
So here's my vision. The PC version one
is we're going to turn basically a
discovery call transcript and a sales
call transcript, however many they want
to dump in. They will be able to dump
those in and that's going to kick off a
new project in their dashboard for
client A. Let's just call it for now.
The AI on the back end is going to
analyze those transcripts, analyze any
of the extra information that the user
has given us. And it's going to create
them a full deck on what was talked
about. And this is really important
because the goal of this deck is to
persuade the client to actually engage
in a partnership. So, it needs to at the
beginning highlight the pain, right?
like, hey, here is the pain that you're
feeling in your business. Here's where
you are constrained and here is the
solutions or here are the solutions that
we talked about in order to actually
resolve those constraints for you and
here are the expected outcomes that we
can receive. So, what's really important
when you're working with a client is
that you are showing them that their
investment in you, their investment in
this project is going to receive a 10x
on that. So, we need to show them, hey,
here's the pain and after the solution
is done, this is why you're going to
have a 10x on that investment. This is
basically
the justification for the price. And
then we need to show them the numbers
that are going to move because we're not
selling the the the journey. We're
selling the destination. So, hey, for
example, we talked about your pain of
feeling like um you don't have enough
business coming in. And what we realized
is that you actually need a better
system for follow-up and reactivation of
leads rather than getting more leads in.
So, we were able to reframe you there.
This is the solution. And now the metric
that we're looking for is you're
currently having about five no-shows per
week. This AI system is going to move
that no-show rate from five to two
within 30 days. And that's basically
like the metric that we're looking at
moving because that metric in the
business owner's mind has a very very
clear correlation to the bottom line to
the actual revenue of the business. So,
that's just an example of the way we
should be framing this. And then it's
going to get into sort of like the
technical details of what this looks
like, visualizing it, because business
owners and people that aren't technical
really like to look at things that are
visual. So, this deck will be very
professional, very visual, very outcome
driven. And then we also need to have
the ability for clients or sorry for the
users of this system to upload their own
case studies to upload their own
specialties so that every deck is
created in a personalized way because
we need these decks to feel personalized
from the actual agency owner themselves
with, hey, by the way, we did similar
builds for these clients and here were
their results. We did this, this, and
this. That's why we're confident we can
deliver this, this, and this. So, there
needs to be that aspect of
personalization as well. They need to be
able to add their own logo and their own
brand guidelines so that all of their
PDFs are coming out branded and
professional as well. And that's sort of
the general base idea that I have for
kind of like version one of this
product. So my idea with the to-do list
that you're building right now or sort
of this planning doc is that we're able
to see all of the different steps that
you imagine we need to build out so that
we can start to delegate work out to
different sessions. We can have
different agents working on different
work trees so they're not overwriting
each other's work and we can move as
much in parallel as possible to get this
done as soon as possible. Okay, so that
was a ton of information that I just
said in there, but like I said, the
majority of this build is actually just
me using judgment, me being the project
manager of agents. as you can see the
way that I've been talking to codeex and
cloud code and it's going to get even
more intense once we really start
building but it's a it's just basically
a lot of strategically prompting and
then working in verification so that you
aren't the one factecking every single
line but you are being able to basically
be given something from an agent that
says hey I'm confident that this works
and here's why here's what I tested all
right so hopping back into codeex let's
see how it's coming along over here with
the branding side so the collision check
eliminated several obvious names close
kit is already being used by nearly
identical AI proposal product. While
client ready is already being used for
an AI report service, the three cleanest
literal territories are client pack,
scope pack, and proposal ready. I'm
treating client pack as the leading
working name and we'll compare it
against the other two visually before
recommending a lock. The first three
studies confirming the name blah blah
blah. I'm doing two more. So, it's
starting to create some branding for us
as you can see. So, we have client pack.
Um, I actually really like this. It's
like there's a C and there's a P and
there's this color scheme which is
pretty professional. We have scope pack.
I don't quite like this one as much, but
it's really not too bad. We've got
proposal ready. I like this, but this
feels a little bit more AI. I don't know
exactly why. It just feels a little more
AI. It feels a little bit more playful
than kind of like premium. And then
we've got this client pack as well.
Okay. So, I mean, so far I really like
this one. I think that this feels
consulting grade. Um, let me close out
of here and see what it's telling us,
what it's yapping about over here. It's
okay. So, it's calling this a editorial
fold. Modern, approachable, and balanced
between SAS and consultancy. I really
like that one. These definitely feel
this feels like a I don't know, like a
financial wealth adviser or something.
But I think this one felt very SAS. This
one felt AI SAS, whereas this one just
felt trusted. So, I'm going to go with
this one. I really like this one. All
right. So, I want to go with a I like
the client pack editorial fold version.
Let's go ahead and lock that in. And now
we can also see the actual messaging.
Turn discovery calls into client ready
proposals. The oneline promise is turn
discovery calls into polished branded
deliverables that help close the client.
I like that. And the short brand line is
discovery in client ready out. Cool. So
before we lock in these three kind of
like pieces of messaging, let's see what
other AI agents think. So what I want
you to do now on the messaging, I like
those three, you know, the headline, the
oneline promise, and the short brand
line, but I want to make sure it's
extremely clear and it answers pain
points. So, what I want you to do is
spin up a few different agent personas,
business owners, agency owners, um,
small business owners, CEOs, and I want
you to have them read the messaging,
look at the logo and the name, and tell
us what they think about the branding
and if they trust it, if they think it's
strong enough, or if it feels very
generic. And once we have sort of like
this collection of other opinions, it'll
help me make a better decision. So, just
spin up those agents and tell me what
they think. You don't have to have them
debate. You don't have to have them give
you a deep analysis. just tell me what
their first impression of the brand is.
And this is something I do a lot and
it's really really helpful. Having teams
of agents, having different, you know,
sub agents or even debates, even war
rooms, having them discuss and argue
things and then give you the consensus.
It really helps you make decisions when
sometimes, you know, you have three
options that you like, but you just have
to get a little bit of persuasion in one
way or you have to hear, you know, the
holes in certain plans or the problems
with certain plans. That really helps me
out a lot when I am planning things or
when I'm building things out. Okay, so
it went through this kind of like sweep
of different personas from business
owner, agency owner, small business
owner, CEO, and it made a few tweaks. So
now the headline is turn discovery calls
into client ready proposal packs. Here's
the oneline promise, which is more
specific. Polished branded proposal,
scope, ROI breakdown, and project plan
without rebuilding every document from
scratch. So it hits on that pain point.
And then the short brand line is
discovery in client ready out. Now,
here's one thing I do want to call out.
Obviously, this in itself is not enough
to be a SAS product. I don't think that
it's enough of a pain point to really
sell, especially for high LTV because
people, like I said, will take it and
we'll do something else with it. But
what this is going to do is this is a
good V1 for us to build on top of once
we set up sort of like this hub. The
vision of this could be this is
basically the operating system that
people are going to be able to use
inside of all of their client
management. Maybe it's a portal now
where people can say, "Hey, log into
this portal, Mr. or Mrs. Client, and
this is where you can see our progress.
This is where you can see, you know,
submitting tickets, things like that."
this could really start to evolve based
on other feedback and other signals that
we're hearing from the audience or from
maybe our beta users. And so maybe this
is something that you get people on for
free to start. You start collecting
feedback and then you're able to charge
later because I know the hard part that
a lot of you guys are going to bring up
is like, okay, well the hardest part is
to get clients. And that is true. And
that's why it's very tough to start off,
you know, kind of like building a
business as a SAS product. And that's
why a lot of us are going through the
service-based route first because it's
easier to be sort of like hight touch.
it's easier to get some data on what
works, what doesn't, what are the
problems, and then sort of start to use
all that knowledge to build something
like a product. Okay, so two other
things I want to kick off now. We're
going to go back to Codeex, and what
we're going to do now is we're going to
spin up a one-page landing page. That's
basically a waiting list, and I'm going
to just let this thing go at it. So,
what I'm going to do is a /goal, which
means that I'm able to set a goal and
it's going to keep pursuing. And what
I'm going to do here is, hey, so now
that we know this information when it
comes to branding, we know the name, we
know the logo, the color scheme, I want
you to create a really simple,
professional onepage landing page. What
this means is I want you to create a
waiting list for people to be able to
sign up for access once this product is
ready. So we can start going around
getting feedback and validating if it's
something that people are actually
interested enough to get on the waiting
list for. So we should have obviously
the logo up top. We should have the
headline and the promise up top as well
so that they understand what they'd be
signing up for and then a little bit of
information down below as far as what
the product will actually do. So if you
have any specific questions about what
it's going to do and feel free to ask.
You can also investigate inside this
project. You can look at the planning
doc. You can let other conversations
that I've been having about it. But
basically just create us a super simple
onepage landing page that we can start
to either run ads to or you know hit to
our email list or drop in different
communities things like that. somewhere
where we can just send people once you
have actually finished building that.
Don't stop until you've validated it.
So, open it up, take screenshots, make
sure the waiting list works. Make sure
that when they sign up for um you know,
when they put their email in there, make
sure it actually captures somewhere.
Like, we need to capture that somewhere.
Whether that be a Google sheet or um it
sends me an email, whatever you want to
do, just make sure that it's actually
all completely functional before we
actually push that anywhere. Okay? So
that was me working in verification
because if I just told it without saying
that it would probably give me a landing
page that wouldn't work. It would just
be, you know, an HTML file. People could
put in an email and hit submit and then
nothing would happen. So hopefully
because I put in that verification loop,
it's able to consistently keep building,
testing, building and testing and then
give us back something that actually
works. And that's all part of sort of
like managing these agents better with
better prompts and things like that.
Okay, so now I'm going to go back over
to our cloud session where we had Fable
give us this plan. So I'm going to open
up this doc and we're going to take a
look at it real quick. We have our build
plan for the pre-sale deck generator. We
have some decisions that were locked. We
have the user experience. So they sign
up. They have a one-time setup. So they
can put in their logos. They can put in
their case studies that they had. They
can put in anything else. They can start
up new projects. So they'll put in the
client name, the client business. They
can dump transcripts. It'll get
analyzed. It'll have a review screen on
everything that's been sort of discussed
before it actually creates the PDF. It
generates the deck and then they have a
dashboard list with all of their past
projects and other things that they can
do, edit them, regenerate them,
whatever. So, here's the structure of
the deck. We have the cover, where you
are today, the real constraint, the
plan, what moves, the math, how it
works, why us, scope, investment, and
next steps. And then we have the actual
architecture of the app. So, it's going
to be a next.js app router. We're going
to have Superbase on the back end. We're
going to have a Stripe checkout. Okay,
perfect. It's going to have two AI calls
per project, which will be to analyze
things and to create the deck. So, this
is pretty in-depth, right? This is
basically the build plan. We have phase
zero, the foundation. We have phase one,
and then we have phase 2. And there's a
lot going on here, right? Like there's
basically A, B, C, D, E, F, G, H,
different work streams in here. And the
idea is maybe we can have these all
being built in parallel. We'll see how
that's possible or not, but we're
obviously going to be using Fable to
delegate all of that around because it
knows how to do this better than I do.
So, here's what we're going to do now.
I'm going to do a /gal prompt in cloud
code as well. This is not just codec
specific. It's also available in cloud
code. So, I'm going to be able to set
this condition here. Now, I'm going to
prompt this thing in a very very
particular way where I'm once again
telling Fable 5 that it is the project
manager. It should not be executing
anything because that would waste a lot
of our Fable credits. It should just be
delegating work around. And real quick,
guys, one thing I wanted to throw out
there before we really get into the
weeds of this video is that building and
scaling a SAS product successfully is
not easy. And I hope that because of
this video, you don't think that that's
the point I'm trying to make. You know,
I'm I'm seeing what's going on behind
the scenes with Glido and how complex it
is and how much the team is working on
the build and constantly iterating. It's
not easy, but what it is is 100 times
easier than what it used to be before
AI. And I think that a lot of us have so
many ideas that we want to build, but we
just never do it. So really, the point
of this video is I want you guys to see
in one day what I'm able to achieve just
by not being technical at all and just
by being curious and prompting and
managing agents and having them verify
things. The way that I'm doing this and
sort of the the mindset that I have when
I'm building all of this out today is
really what I want you guys to actually
take away from the video. So now that
I've got that out the way, let's just
get right back into it. Okay, so you are
the project manager of this entire
project. You need to see that it from
end to end all gets implemented right
and all gets built right because you at
the end of the day are responsible for
any of the mistakes here. So what I want
you to do is you're going to work off of
that build plan. You're going to work
through these phases by delegating work
to different sub aents using opus or
sonnet whatever you see fit for the
complexity of the task. So what I want
you to do is you can use dynamic
workflows, you can use just sub agents,
you can use agent teams, whatever you
see fit because you know how to do this
best. You know how to manage the project
best. Your job is to do this as fast as
possible. Meaning anything that can be
done in parallel, do them in parallel.
There's no need to wait and do this as
an assembly line. So figure out based on
your build plan what can be done
together and what has to you know what
has dependencies and just execute this
as fast as you can. Um if you need to
use different work trees, feel free. If
you want to just spin up a bunch of
different sub agents, feel free. But
what's really important is that you're
having the agents write progress back to
either the build plan or each agent
independently is creating a new folder
and is saying, "Hey, here's what I've
done. Here's what I'm still working on."
So that you can always check in on them
to see where they are to make sure that
they're not overwriting each other and
to make sure that you're constantly
verifying what they're doing and giving
them feedback. So your end deliverable
to me is basically a finished V1, a
finished P that we can get in there and
we can test and see if we're ready to
kind of like move on to the next phase
of this thing. A few things I imagine
potentially getting in your way would be
setting up like a superbase connection
because you might not have that API key.
Setting up the Stripe integration if
there's anything like that. Build out
the supporting infrastructure around it.
Build out the plumbing and then you can
basically flag me at the end when you
finished and say, "Hey, I need this API
key and I need this API key." But that's
the only thing I should have to do. You
should be able to then take the API keys
and set up everything else that has to
do with the front end and the back end.
You should be thinking about how people
pay and what it looks like when they get
onboarded, where their accounts get
made, how that happens in the back end,
and how we as admins are going to manage
the infrastructure in the back end of
our users and our databases and things
like that as well. This has to be idiot
proof on the customer journey side as
well as on the admin side. So that's
your goal. Go ahead and do whatever you
need to do to accomplish these tasks.
Okay, so that was obviously a very big
prompt, a huge slashgoal. So, this is
probably going to take a few hours, and
that doesn't surprise me. So, what I'm
going to do, though, is I'm able to use
this session on my phone. As you can
see, we have remote control, and we can
turn this on. As you can see, that just
got turned on, which means I can go into
my phone and I can actually manage this.
So, right here, I'm not sure if you can
see, but this is the prompt that I just
sent off, right? Um, I'm able to manage
this now from my phone, which means I'm
gonna be able to maybe go make a quick
bit of lunch, maybe go on a walk, maybe
go down to the gym, and I can just keep
checking in on this so that I'm not
wasting time because this is, like I
said, going to run for a little bit
because that's really what we're doing
now. We're kind of waiting. We have um
Claude over here working on the actual
build. We have Codeex over here working
on the packaging. And I guess the only
other things that we could do maybe is
we could go ahead and give them a
Superbase API key and a Stripe API key
or something so that they could start
building in the actual integrations. But
for now, I'm not going to mess with
them. I'm just going to go ahead and
wait and then we will come back when
these are done and we'll see what else
we need to do. But this is why this
stuff is so powerful. I mean, I was able
to send off one request and it's been
building things, viewing them,
iterating, viewing again, verifying,
iterating, using the sites integration
to see if it's working. It's, you know,
creating this type of stuff, and now
it's just going to keep going until it
has proven to me that it's all working,
which is just really, really cool. And
then on the other side, with what
Fable's doing right now, it basically
was able to work off that plan doc, and
now it knows exactly what to do, and
it's running a bunch of different agents
in parallel. As you can see, it's
spinning up tons of different workers to
do one very specific thing, which is
really, really cool because it's really
tough to have one agent do everything.
It gets confused. The context fills up.
You get the rot. You just get all of
this type of bloat. But if you're able
to have one main like fable manager that
delegates off tasks, spins up new
agents, and has them do one very
specific thing very well, the quality of
everything is just so much better. As
you can see, it's already finished all
these agents. right now. I can view the
transcript and I can see exactly what
they did and I can keep looking into
what they're doing in real time. And so
we're still, like I said, very much in
control, but we're not having to be the
middleman between everything. So don't
underestimate how powerful this stuff is
when you're able to kind of clearly have
a vision for something and then have
something like Fable or Codeex or
whatever it is help you sort of
orchestrate in the right way using a
bunch of different agents to help you
achieve that vision. And so really the
main point I'm trying to make in this
video is that there's a lot of things
that you might not know. Like maybe the
idea of, oh, how do I even integrate
Stripe into my own app? How do how do I
even do that? You don't have to know.
You have to outsource that thinking and
that research to something like Claude.
And then it will say, hey, in order to
do this, I need you to set up this
connection. I need you to give me this
key. And then I need you to enable that
in the actual UI. And then you can just
go ahead and do that. And it will take
care of the rest. I'm not trying to say,
"Hey, in this video I'm going to make a
million dollars with my AI app." I'm
showing you what it looks like to
actually build the thought process of
outsourcing the thinking but still
keeping yourself in the loop in the
right areas and hopefully motivating you
guys to realize that you can give AI a
lot more ambitious goals than you
actually thought that you could and you
can really just start to leverage this
even more to do even more yourself. I
mean, just take a look at all these
other agents we have. We have currently
nine that are running anywhere from
intaking and reviewing the UI, the data
layer, the API routes, viewing the PDFs,
um looking at the extraction spikes and
fixing them, even checking on Puppeteer
to make sure that it can go ahead and
click around on things. It's super super
cool. And because Fable isn't doing
this, because it's Opus or Sonnet doing
all this, our limit is going to last a
lot longer because we have a weekly
Fable limit, which we've only used 3%
of, even though we've done so much work
already with Fable.
All right, guys. So, take a look at
this. The client pack landing page is
done. So, we can go ahead and open it
up. And it looks like this. Honestly, I
think it looks really good. Like, you
can tell it was made by AI because it
has similar formatting. You know, the
big hero text, the kind of the the hero
image over here, but it's not bad at
all. And when you think about these
little images that it had to create, it
definitely has a nice kind of like
professional vibe. Even the depth in
this little logo here. I really like
this from a first pass. We could
obviously iterate more if we want to.
I'd say this little pulsing icon thing
is very AI, but this looks good. The
next question I had for it then was
like, okay, so how are the emails being
stored? Because obviously that's the
whole point of this is to collect emails
and it did all these verification
checks, right? It said that the emails
are being stored in the site's database.
So that's not something that we really
had the ability to access. So then I
came back and said, "Okay, so how do I
access these?" It says that you could
put it on a different password protected
weightless page. And I said, "Yeah, go
ahead and set that up." And so after it
did that, now we have a different admin
page that I can go ahead and sign into.
And when I sign in, I now get this
second page. I can sign out. This is,
you know, the email that I signed in
with. I could refresh this. I could
download this as a CSV, and I'm able to
see the most recent sign up, the total
signups, and I get all this data. So,
let's see if this actually works. I'll
go into here. I'll put in a fake email,
and then we'll go ahead and join the
wait list. See what happens. It says,
"You are on the list." We'll go back
into the admin. Let's see if we can give
this a refresh. There we go. We now have
a new entry signed in right here. And
now we have basically an email list
growing of people that are interested in
this product. So the next step now,
while Claude is still building out all
this stuff, obviously, like I said, this
is going to run for quite a bit. So
we're going to keep letting this thing
cook. What I want to do now on this side
is we want to actually be able to expose
this to an actual domain because right
now you guys can't see. Let me just copy
this. This is the domain that's being
hosted on right now.
Clientpack-weightlist.nateherk.t
tragic.
Which is cool because that is a URL that
anyone could access. But what we want to
do now is we want to be able to get this
to something that we actually own and it
looks a little more professional because
if you sent people to this URL, it just
doesn't have the right vibe, right?
That's clearly a chatbt website. So what
I want to do is push this onto a GitHub
repository so we can keep that codebase
and we're going to push that to
something called Verscell which lets us
basically host that URL. So,
okay, now that we have the site done, I
want you to create a new GitHub
repository for this. So, you should be
authenticated into my GitHub already. Go
ahead and create a new repository for
this. You can just call it the client
pack landing page. And then once you've
got that pushed, I'm going to connect
that to so we can actually deploy this
on our own site. Now, if you've never
used GitHub before, it's very, very
simple. Just type in github.com. It's
free to create an account and this will
actually let you sync your Versell
account with GitHub. So go to GitHub,
make an account and then you're going to
have to authenticate in to Codeex or
Cloud Code. Just basically say, "Hey,
here is my GitHub account. Um, help me
authenticate in and it will basically
pull up like an OOTH signin." You'll
sign in. It's super super easy. And then
it will have access to help you with
your repositories or basically just a
codebase. And then you're going to also
go to Verscell. And this is where you're
going to be able to manage other things
that you want to put onto a real live
URL. And this is where you can actually
buy your own custom URLs to put on an
app. So for example, right here I've got
nateherk.com.
And this will deploy by default on
natek-.vercell.app.
So it's doing the same thing that chatbt
does when it has like the chatbt.
But then you can also connect your own
custom domain which is super super easy.
So what you want to do that it referred
to earlier is you want to go see if your
domain is actually available. So you can
go in here to versel. You can go to
domains and you can either buy one from
here. So for example for client pack I
could say clientpack.com.
That's obviously unavailable. Um what if
I do like getclientpack.com? This one's
available for $11.25
as you can see. And we could buy this
straight here from Verscell. And then we
could just say okay cool. This is the
project that we have set up for client
pack. use this domain rather than using
a different one. Right? So that's how
you would do it if you wanted to buy
your own custom domain for your landing
page, for your website, for your app,
whatever it is. Okay, so that obviously
worked super quick here. It pushed this
to a GitHub account, to my GitHub
account, and it called it client pack
landing page. So I can click on this
link. This is what the GitHub looks
like. It has basically all of the files
and folders that we need in order to
host this site. And what this means is
we can have version control here. So if
later we update the color or we update
some of the copy, we could push that
back to GitHub. So now we have a working
version and we can go back and see
different versions if we changed
anything or anything that we added. And
that helps us be able to protect our
codebase. So now you're going to go back
into Versell. You're going to click on
add new project. And then all you have
to do is you're going to import the Git
repository. So right here it's going to
prompt you to connect your GitHub
account if you haven't done that. So go
ahead and connect the GitHub account.
And then you can literally just click on
this is the GitHub account or sorry the
GitHub repo. I can literally just click
on import. And then I can deploy this.
And all this is going to do is now it's
just going to take this landing page and
our admin site and it's going to put it
on our own URL that we can own like I
said. Okay. But there is an issue here
which sometimes happens with deployment.
So I'm kind of glad this happened. I can
show you what to do. So you can see it
says 404 not found. I'm going to go to
the dashboard. We're going to click on
the actual URL that it gave us and it
says 404 not found. So what I'm going to
do is I'm going to take a screenshot of
this because codeex will know how to
actually solve this. So I'm going to
copy this screenshot. I'm going to paste
it in here and say okay so I connected
my GitHub account. I connected the
GitHub repo that you just made client
pack landing page to Verscell and when I
tried to deploy it this is what
happened. I'm not sure if because it
tried to deploy this with Vite or
whatever happened but if you need more
info from Verscell let me know but this
is what we're currently seeing and you
need to fix this. And just like that,
you guys can see it's still working, but
it's already fixed the issue. I go back
into my versel, I refreshed it, and you
can see we now have this showing up as
the preview. And when I click into the
actual domain, we now have the actual
site that we were looking at ready to
go. So, for the most part, our packaging
has been done even though the product
isn't yet done. And I think it's really
important to realize that you can do the
whole like selling before you build idea
to actually validate that what you're
about to do, the time you're about to
put in to this product is going to pay
off. And then we even had codeex without
asking go ahead and verify that all of
that is working. So we are good on that
front. And Fable is still cooking up
over here. So I'm just going to keep
letting it do its thing. And because we
got the remote control on my phone, I'm
actually going to grab some lunch, run
down to the gym, and just keep checking
in. and then whenever it's done, I'll
come back and give you guys an update.
Okay, so I have not looked at this at
all yet. It says that it's done. It says
version one PC has been finished. And we
can go ahead and open it up. I'm
prompting it right now to open it up in
a different local host for me. So, it's
spinning that up right now. But here's
what got verified, not just built. So,
it said the full customer journey with
real model calls, meaning once a
customer comes in here and puts in
information, it will send off that
information to an AI model. Now, it
probably chose an enthropic one because
this is clawed, but that's part of
what's baked in here. And so,
essentially, that's what a user is
paying for when they subscribe to this
on, you know, a monthly subscription. We
could have maybe done like a pay as you
go billing, and you have a choice there
as far as the model, the business model
that you want to run. But what it chose
to do here was you have a subscription,
you probably get like 10 generations a
week or something like that based on how
much you're paying. And then we're
technically eating that API cost. Now,
as you start to scale that up, there's
going to be different types of problems
and other things to think through, but
that's the way that it's currently set
up. From there, it said the deck is
actually good. I screenshotted every
generated PDF and looked five layout
defects found and fixed, then reproven
on a fresh generation. A geometry fit
check script now guards all 10 slides.
So, one pack is going to cost about 16
to 20 cents. Every AI call logs, tokens,
and dollars to a specific event or to a
specific place in the admin panel, and
that is what got checked. Now,
obviously, this isn't a finished thing.
This is V1. We still have to set up a
few API keys. We have to get a couple
things sorted that are open items like
superbase forcell anthropic keys, things
like that. But we have something now
that we can sort of look at and give
some feedback on. So the demo is live.
We can go ahead and open up our local
host. So I'll click on this. And that
just opened up this page right here,
which is a local host. So no one else
could actually touch this. But this is
kind of the UI that we're looking at.
This is client pack. We have projects.
We have brand and case studies. So this
is where you as a user could come in
here and say here's my agency name,
here's my color, here's what we
specialize in, here's our logo, and then
we can also put in some case studies. So
I think the idea here is that every deck
is generated in your in your style. So
your logos, your colors, and your notes.
And then if there's a relevant case
study, you can put them in here so that
they can be automatically added into
your decks and into your, you know,
potential sales material. We also have
billing here. So right now we're on a
free plan. Zero out of one decks. The
free account covers one deck in total
and then we can go ahead and switch over
to a paid membership. So, it's a super
clean, super easy to use UI. Now, let's
take a look at here. We have two client
decks. One of them is a draft and one of
them is ready. Let's just go ahead and
click on the ready one real quick. So,
radiant skin med. If I open this up, it
basically opens it up in a little
project portal right here. We can see
the deck is ready. We can see the pain
points, the investment, the value per
month. We can view deck, edit, findings,
regenerate. And here are the transcripts
that we put in to this specific um
project. So, we put in a discovery call
on August 2nd and a follow-up call just
as a text on August 6. So, it looks like
when you add a transcript, you can do
text files, doc files, VTT, as many
files as you want. Or you can paste a
transcript in right there. So, that's
pretty cool. We also have project
details. So, I can open this up. We have
client name, what they do, anything else
we should know. Okay, perfect. Now,
let's go ahead and actually view this
deck. Okay, so it opens it up right
here, and we have 10 slides that we can
flip through here, or we could also
download this as a PDF. But here's what
we have. So, this is our agency name.
This is where our logo would appear. And
you'll notice that these colors are
basically being presented because this
is the color that we entered for our
agency. So, Radiant Skin Medspa, that's
the client. Fill the chairs you already
booked without raising ad spend. So,
prepared by us. Here's the date. And
we'll go ahead and go to the next slide.
So, it starts off with where you are
today. Five appointment slots a week go
empty. Blah blah blah. Inquiries you
already paid for, wait days for a reply.
And then Botox clients need a touch-up
at 12 weeks and nobody asks them. So,
what this did is it pulled specific
quotes where the client themselves told
us the pain. And this makes it a little
bit stronger cuz it's like, oh wow, I
did say that this is definitely
something that we have, you know, a pain
point in our business. And there's three
of them backed by real quotes from our
discovery call. So that already gives
them a sense of like, okay, I trust
these guys a little more. They're
clearly not just like putting me through
some AI generated like prompt. They're
pulling specific things that I said in
our call together. We keep going here
consistent with our branding, consistent
with our color screen. This is the real
constraint. They came in basically
saying, "Hey, we need more leads." But
what actually is true is you need 30
minutes after an inquiry and 12 weeks
after a visit. So this idea of the
reframe is positioning us as the
consultants, the long-term thought
partners who are really thinking about
the business and not just saying, "Okay,
oh, you want this? Here you go." We're
not just taking orders. We are actually
helping think about the business. So
here is the plan that we talked about.
We have three steps right there. We move
on to the actual metrics that we're
trying to move. So you can see five per
week goes down to two per week. The
first reply about two days goes to about
under five minutes. And then the
repeatable injectable bookings per month
is about four per month. And we want to
get that up to 10 per month. So we're
really showing them what it will look
like when you actually work with us.
Meridian Automation. Here we get into
the math. So this is basically what you
invest and this is what it returns in
year one. Obviously this has to be
backed by real data, real things that
they said, real numbers of what the
automation or what the solution is worth
to them is worth to their business and
value. But this once again is just going
through the framework of we have a
system as consultants. This is how we
work with businesses. This is how we
show value. This is how we show the ROI
and having this sort of consistent way
that you're presenting these decks is
going to help you come across more
professional. It's like you have your
own framework. Now, here we can see we
sort of dig into the actual processes.
So, here's the manual process and here's
what it will look like after launch as
well as a little bit of a visualization.
Now, this could be reworked a little
bit. I think this could be better. But
for a first step, this helps us be able
to really really visually explain, okay,
this is the trigger. This is a step that
happens. Here's maybe where a decision
happens. Here's where AI is involved.
Here's where your team is still
involved. So, it once again starts to
create a better picture in the client's
mind. We move on to why us. So, this is
where you can show specific examples
from your case studies and you can edit
the information. Here we have the actual
scope, what's included, what's not
included. And then we have the
investment and next steps. So, once
again, this is not like the formal
contract that they would be sending to
the client to get them to sign. This is
more so like, hey, we had three calls.
Here's what we learned. Here's what we
want it to look like when we work
together. are you guys in or not? So
that is what the PDF actually comes back
as. Now once again, I could go back to
this project. I could edit the findings
if I wanted. There's a lot of different
things here. We can change the severity.
We can move it up or down as a different
painoint. And we can really customize
this as much as we want. As you can see,
there's so much here that we can do
because obviously we want to make sure
that this is legit, right? So we have
all of these metrics we can play with
and then we can hit regenerate deck and
we get a new deck. I'm curious what this
one looks like in draft mode. So, I
think the only reason this is a draft is
because there's not yet a transcript in
there. And once we had a transcript in
there, we would go ahead and hit
generate deck or analyze deck and then
we would get something back. So, for a
first PC with the main functionality
here being taking transcripts and
turning it into decks that you can play
with and, you know, iterate on with your
own branding and case studies, I'm
pretty happy with this. Like, this is
V1. This is the first time I opened this
up. And now what we have to do is make
sure that everything is working because
there's probably some bugs in here that
we haven't yet found. But we also
haven't gone through like the onboarding
phase. So if I go ahead and click log
out in the bottom left, this doesn't
actually do anything. You know, maybe
it's cuz it's blocked, but I can't hit
sign out. Like yeah, nothing's happening
when I hit sign out. So I think the next
step that we have to go through is kind
of like stress testing this piece, but
then also getting that onboarding flow
set up. So I'm going to go back into
Claude and we're going to just chat a
little more. But one thing I want you
guys to pay attention to is all of that.
We could have done that all with Fable
5, right? And I'm not sure how much
better it would have been, but look at
this. We only used 1% of Fable since we
last checked in. So all of this
basically coding and decision-m Fable
was routing to different agents and we
weren't actually using Fable's real
compute to build out that code. So
that's really cool and it's a great
trick to use when you're sort of like
managing these agents. So, I'm going to
go ahead and once again do a session
handoff because we are kind of hitting
that context rot territory and I just
want to clear the context to throw off
another task while still keeping us like
on the right path. Okay, so I have this
handoff message. I'm going to clear this
chat, paste that back in, and I'm just
going to say here is what just happened.
Don't do anything yet until I tell you
what to do. So, I just wanted to read
that and get familiarized with what what
what's going on. Now, I'm also going to
open up Codeex and I'm going to open up
a new chat inside of our AI SAS Sprint
project and paste in that same session
handoff because what I want to do here
is I really like to use Codeex as my
verifier when it comes to an actual app
and opening it up and playing with it.
Codeex is much better with computer use.
And what I want it to do is I want it to
basically come in here, spin up a new
project, generate transcripts, paste in
different types of documents, paste in
different things. And I want Codeex to
try and break this app. I want it to
find bugs and find holes in it so that
we can go back and fix them. So that's
exactly what I'm going to do. So you can
see inside of Codeex, it says, "Okay,
cool. Here's the context. It's running
here." Blah, blah, blah. Okay, Codex,
here's what I want you to do. This is V1
of client pack. You can see it open in a
local host. What I want you to do is I
want you to use your computer use and I
want you to click every button. I want
you to play around with this. I want you
to try to break this. I want you to try
to find bugs. Your goal is to tell us
what needs to be fixed so that we can
fix this before any customers actually
come in here. I want you to try to
upload different formats. I want you to
try to generate transcripts or sorry,
generate decks. I want you to play with
different buttons and find where there
might be either like a visual bug or an
actual technical bug, a limitation in
the functionality of this app. And once
you've tested this um you know through a
bunch of different workflows and tried
to find edge cases and you either have
found a bunch or you found none, once
you feel confident that you've tried
enough stuff to confidently say that
this version is ready, then go ahead and
let me know what we need to change.
Okay, cool. So this is going to open up
the browser. It's going to start to play
around with it a little bit. And that's
great because it's not going to change
anything. So what that means is over
here back in claude I can have it start
building out some other stuff without
interfering with what Codex is doing. So
I'm going to come in here and say okay
cool. So right now I have codeex testing
everything the version you just gave me
in the local host. It's going to start
testing things generating new decks
playing around with different buttons
and seeing if there's any bugs. I will
come back to you with what codeex finds.
Now what I'm curious about from you is
once again you're Fable 5. You're the
orchestrator. You don't execute
anything. You're basically just um
you're basically just orchestrating a
team of sub agents, opus workers, sonnet
workers to help you build this out and
you are the project manager who's
responsible for everything. I'm now
curious about the onboarding flow. We
have to figure out what does it look
like from the beginning into the actual
dashboard when a client comes in and
they pay, you know, they subscribe and
then they onboard, they get logged in.
Where do we hold all that data in the
back end? And what does that journey
look like for the customer? Because it
has to has to be quick. It has to be
easy and seamless. Otherwise, we're
going to lose paying customers in that
onboarding process. So, that's what I
want to build out here. And I want to
make sure that I'm giving you everything
you need as far as like Superbase
integration, Stripe, whatever you need
here. Let's start building out that
whole onboarding and the payment
processing flow. Okay, cool. So, we have
these two other prompts coming back.
This one will probably take a little
bit, you know, of testing. And then this
one over here will probably be going
back and forth a little bit to answer
some questions and to set up some things
like superbase and whatnot. But real
quick in codeex, if I see over here the
browser, we can actually see it trying
things out. So right here you can see it
tried to enter an accent color like it
tried to type in red, but we obviously
need to use a hex color like 275 blah
blah blah. So now it put that in. And so
this mouse right here is codeex. This is
codeex using a browser. You can see it
clicking around. You can see it moving
around. And this is what's so cool is
it's just going to test a bunch of stuff
and then it will come back and say,
"Okay, I tested these a thousand
possibilities which would have taken you
like 12 hours to do." So, so using
codecs here as a computer use verifier
really really fun and also really really
helpful. Oh, I just realized that these
lights weren't turned on. There we go.
Now we got the the good vibe in here as
there's a bunch of clouds coming over
Lake Michigan. Hopefully it doesn't
start storming on us. And while it's
running through this, let me show you
something real quick, which is a slash
by the way, which means you can ask
Claude a question without interrupting
this main kind of like chain of thought.
So, what I'm curious about is the text
stack that it wants to use because I
remember it mentioned Superbase and
Stripe, but I just want to make sure
before I go off and like create a new
table or create a new account. So, while
you're thinking about this, I'm curious
the text stack that we're going to use
on the back end for authentication. I'm
not sure if you were planning on using
Superbase or Stripe or what all are the
things that you need, but if you could
let me know what we were planning so
that I can go real quick and spin up the
accounts and get the API keys ready and
stuff like that. So, as you can see,
it's a little side chat, right? It's
just it's super super cool feature when
you have a little one-off question like
this and you don't want to interrupt it.
And as you can see down here, the answer
we got is that Superbase is going to
handle the authentication. So, it's
basically going to store our users.
It'll be our customer database and then
Stripe is going to be just the payment.
So, it's never going to touch off Oth.
So, that's super clear. Now, we know
what accounts we'll have to go set up.
You can see that we're going to have to
get some API keys and things like that.
Superbase. And then from Stripe, we'll
have to get a secret key, probably a web
hook secret as well. It's already got
our anthropic API key. It's already got
this other stuff. So, cool. I'm going to
go ahead and close out of that chat. And
now you can see the main session has
some questions for us. So, what does a
new user get before paying? This decides
whether checkout comes before or after
the first deck. I would say yeah, free
deck, but it's watermarked. That's
perfect. Final price point config
currently says 39 bucks a month and 390
for the year. Research band is saying 29
to 49. Let's just go ahead and go with
the recommendation since it did go ahead
and do a bunch of research. So, I'll
click on the recommendation and now we
will see what comes next. So, the
journey that it wants is there's a
pricing page and you can sign up and
then you check out and then there's a
three-step onboarding which gets you
into your first deck. So, we're
basically going to follow this flow,
keep it super simple. We obviously have
to make sure that that works and also
that if they sign up for a subscription,
it's actually going to charge them
recurring and if they want to cancel it,
they're able to cancel it. So, while
this is all spinning, let's go ahead and
jump over to Superbase and to Stripe.
So, if you've never created a Superbase
account, it's super easy. It starts off
free as well. So, just go to
superbase.com and go ahead and sign in
or sign up for Superbase. So you can see
here with upai I am just on a free plan
here and I'm just going to go ahead and
start a new project and we are just
going to call this our um what's our
product called? Our client pack. Okay,
client pack. We have to set up a strong
database password. So just make sure
whatever you set this as you remember
it. We want to enable the data API
automatically expose new tables and just
all of that I'm keeping as default. And
we're going to go ahead and create this
new project. And then of course you're
going to go over to Stripe and you're
going to want to create an account over
here if you don't already have one set
up. And I know it might seem a little
intimidating. There's all this new
software. There's all these new things
to keep track of. Just don't worry.
Claude is going to tell you exactly what
it needs and how we get it. So let's
take a look at what it says. So we have
some decisions locked. We have two Opus
workers that are now building each in an
isolated work tree so that the codeex
testing stays untouched. So that's
amazing. It's building out the funnel
and the onboarding wizard and it's
building out sort of the watermark which
is going to actually go on those free um
those free decks. So now what's going to
happen is whenever we're ready we have
to paste values into thev.local
and that's going to be superbase stuff.
So create a free project at
superbase.com. Then go to project
settings, go to API, grab the project
URL, the A9 key, the service roll
secret, and we're going to have to
upload all of those to thev. And then
same thing for Stripe. And when it says
to put them in thev, as you guys know,
we'll go up here, we'll go to files, we
will click on our um Oh, I don't know
where it put the env. Okay, so I'm
actually not seeing av. So we're
probably going to have to make one. I'm
just going to tell it create us thev
file and then it will hopefully drop it
in there. But in the meantime, let's go
back over to Superbase and go to our
project settings to get these three
things. Okay, so here I am in Superbase.
I'll zoom in a little bit. I'm going to
go down here to project settings and we
have to go to I think API keys right
here. And now back in claude, I can see
we have ourv.local
and we have our Superbase instructions
here. So the next public Superbase URL
is our project URL. So I'm going to
delete this and we're just going to go
back into Superbase and grab our project
URL. Now, this is where it can get a
little confusing though because we have
API keys, we have service ro secrets.
I'm not seeing the project URL. There it
is. API URL. I believe this is correct.
So, I'm going to go ahead and copy this.
Go back into Claude and paste that in
there. And we'll obviously make sure and
ask Claude if all this is correct later.
Then, we need our Anon key, right? So,
back into Subabase. I'm going to go back
to project settings. We're going to go
to API keys. We can see if I click over
here, we have an anon public. So, I'll
click on that. I hope I'm saying that
right. Some of you guys are probably
face palming right now, but there is
that key. And then we need to get the
service roll secret, which is down here.
I'm going to click reveal. Copy that.
And then we're going to put that in
right there. Hit save. Now I'm going to
say, okay, cool. For superbase, I put in
those three things. Go ahead and see if
those are correct. And while you're
doing that, I will get the Stripe stuff.
So for Stripe, we need to get two keys.
So I'm going to go into Stripe, and I'm
going to go down here to developers. I
believe that's probably where it is. and
we will go to our
API keys down here. You can see we have
a secret key as well as a publishable
key. So I believe these are the two
things that it needs. I'm going to copy
each of these and put them into our file
here. So now the SUBA stuff is correct.
Go ahead and check if the Stripe keys
work as well. Okay, cool. So this is
something important I wanted to call
out. It wants us to do this in a sandbox
before we switch over, which I think is
very very smart. So in the Stripe
dashboard, you're going to go to a new
sandbox. So up here, you'll click on,
you know, switch to sandbox. You can
either create a new one or if you
already have one. And then when you go
to your API keys in the sandbox, you can
actually just play with this. And you
can see here, you are testing a sandbox.
No real transactions will be processed.
So I'm going to now put in the sandbox
keys into Claude. And then we'll have it
start to test out things and start
making subscriptions and things like
that. Okay. I switched those out with
our test keys. So we do all of our
testing here in a sandbox. And then as
soon as once everything's confirmed, we
have the full endend pipeline working,
we would just switch out the test key
with the real key and we'd be good to go
because there'd be all the backend sort
of like processes and scripts already
baked into the app itself. So hopefully
you guys are kind of realizing the
unlock here. It's that we don't really
have to know all of the plugins. We just
have to be able to ask the right
questions as if we were talking to a
developer who has built tons of
different SAS products and tools and
APIs even. And of course, we're able to
have it check its own work. As you can
see, soul over here in Codex is still
chugging away. It's been over 20
minutes, and it is still testing the
heck out of our app. Now, look how cool
this is. It told us that we needed to
put a Superbase table inside our project
because right now in Superbase, if I go
over here to our table editor, we have
no tables and we actually have to create
one. But what's really cool is read
this. It said, I just recopied the SQL
editor command to your clipboard. So
that basically means if I go into
Superbase and I go to the SQL editor and
I just paste, this is the actual query
that it wrote up that's going to create
the right table. So now I just hit run,
it's going to down here say success, no
rows returned. And now if I go to
tables, there we go. We have these. What
are these? Eight tables that it just
created. And I didn't have to do any of
that. And now it's going to have our
subscriptions, our transcripts, our
usage events, our decks, case studies.
It has all of these set up correctly.
And all of this information is now known
to claude so that it can actually write
up all the scripts on the back end. So
that worked amazing. We now have those
eight tables in our superbase. Let's
keep on building towards this full
process. Now there is one more thing
that it's really important about this
specific app that we're building. Yes,
we are testing functionally and
technically if everything's working. Are
the connections right? Are the buttons
right? Blah blah blah. But what about
the actual value of this specific app?
The value in this specific app is that
we're getting legitimately high quality
analysis. You know, when I come into the
deck, not just like, hey, does this look
good? Hey, is everything rendering
right? But is this stuff accurate? Like,
is this information real? And so part of
that is on us. The way that the AI on
the back end is actually analyzing the
transcripts and stuff, right? Like
that's part on us. And it goes back to
what I was saying about you can
outsource your thinking and the data
collection, but you can't outsource the
understanding. And so like if this is
just pulling generic information from,
you know, Opus 5 or whatever model on
the back end is powering it, that's not
going to be good enough. So what I would
do here is I would use something like a
grill me skill and I would say hey grill
me on everything that I know about
communicating to clients, you know,
positioning the value, the ROI, the
investment, the the actual realistic
results of these AI solutions. And then
I would say, okay, now that you just
interviewed me for like, you know, 20
minutes or whatever, take all of that
data and put it into the prompt of the
AI processing on the back end. Because
ultimately the IP here, the real moat,
the real important actual like moat here
is that the prompt that powers this on
the back end is what matters because
anyone could come in here and rebuild
this entire thing in one day. That can't
be the moat. The moat for me in this
business in this, you know, potential AI
SAS is that I have all of my knowledge,
all of my experience, all the landmines
that I've stepped on baked into the
prompt behind this regenerate button or
behind the analyze button. And as we
build out more little tools in here that
help agency owners run their agency
better, the moat is all of the data and
experiences that I put into it. Not
just, hey, can Stripe work with our app
and Superbase work with our app and does
it look pretty? Nobody's going to stick
around for that. they stick around for
the actual IP that they don't have
access to. The reason I wanted to call
that out here is because I'm not going
to sit here in this video and just brain
dump for hours and optimize this prompt
for hours. This was more about showing
you how much you can get done in one
day. And more importantly, how much
there's still left to do once you're
done. Every time you have a new customer
and you get the feedback, you're going
to have to fix things. Customers are
going to find bugs. Customers are going
to have feature requests. You're going
to want to iterate. So, I know the title
of this video kind of made it seem like
I'm building this SAS in one day, but
the truth is in the AI space, there's
like no such thing as a finished
product. My iOS, I change every day. All
of my skills I change every day. All of
my automations are changing constantly
based on new things that we learn. It's
never done when you think it's done.
Okay, speaking of done, codeex is done.
So, let's take a look and see what it
said. So, it basically came back with
this is not ready for customers yet. So
this is why I like to use a different AI
model to help me find things that
clearly Fable 5 and all these other
workers they missed. So there are two
main launch blockers. We have the review
and sign off are not enforced. So it
generated a real deck while an inferred
baseline was still unconfirmed. I also
confirmed that regenerate deck remains
enabled with zero pains, zero solutions,
negative interest, a negative
investment, empty required findings. So
we need to fix a couple things there.
Then we also have unknown ROI produces a
client-f facing 0x slide which obviously
cannot cannot happen. So these are sort
of like the two blockers. We also have
high priority bugs and medium priority
bugs. And then we have basically all
these other things that it confirmed are
working well. So now we have a decision
to make. Do we want to take this report
and give it back to Fable 5 to help us
build the stuff out or do we want to
just say okay codeex since you found all
this stuff you build it out. You make
all those fixes. And because so far
we've mainly been using Claude for the
building and also Claude's working on
building some other stuff. Let's just
try doing this in codeex. So I'm going
to come over here and I'm going to do a
/goal and I'm going to say okay cool. So
now you are in charge of managing all of
these things that you found. You're in
charge of fixing the blockers and fixing
the high priority bugs for now. Let's
just leave the medium priority bugs
alone. But what I want you to do is you
need to utilize a team of agents. I want
you to be the orchestrator. You're the
project manager. I want you to utilize
sub aents. I want you to utilize agent
teams. Whatever you need to do to
delegate the work around so that each
agent is specifically focused on one
very specific thing so that it can do
that job really well. I also want you to
be wary that no agents are overwriting
each other's work. I also want you to
know that right now in a different
session we have claude code building out
sort of like the onboarding flow and the
payment flow. So don't mess with any of
that. Only attack the actual blockers
and bugs that you found in our app.
Ultimately, you are responsible for
this. If it doesn't go well, I will
blame you. So, you have to verify what
the sub agents that you are
orchestrating. You have to verify that
what they're doing is correct. So, your
goal is to fix all the blockers and fix
the high priority bugs and verify that
they are truly fixed. You can use
computer use, whatever you need to do.
And then once you're confident that all
of that has been fixed and it's customer
ready, at least in your scope of work,
then report back to me. Okay, cool.
Cool. I'm going to shoot that off. It
just got really dark out of nowhere.
Let's see if I turn on that light if
that helps at all. O, that might be a
little too eh. It's not too bad. But
yeah, it's it just started raining. It
got super cloudy. So, I apologize the
lighting. Hopefully, we don't hear any
thunder and stuff or see some lightning.
But, let's just keep building this out.
Codex is now going to be working on all
those bugs it found. Claude is working
on the actual um connection with
Subabase, hopefully the connection with
Stripe, plugging everything up, setting
up all the plumbing, working on that
onboarding flow. This is coming along
really nicely and it is currently 1:40
1:39 um p.m. Keep in mind I also went
off I had lunch. I went down to the gym.
But I've just been constantly working on
this thing throughout the day and it's
been a lot of fun. Let's just do a quick
recap. We found the pain, right? We
found the pain because I was able to
analyze what was it like over 60,000
comments or threads from both me, my
community, my YouTube channel, but also
from just Reddit X general problems that
people in the space are having. We then
made a promise. We have one thing that
the current tool is doing really well
and hopefully it's going to do it better
than other tools out there. We have the
actual product that's being built. We
have all the plumbing going into it. So,
it's connecting to different AI models,
different APIs. We have it set up on
our, you know, Versell, everything like
that. We have the packaging figured out.
We have the logo, the name, we have the
actual um what's it called? The waiting
list application right here that people
can learn a little bit about it, get on
the wait list. And then we can see the
admin panel to see who's on the wait
list. As you can see right here,
obviously no one else signed up, but we
can see who has been signing up for our
app. And then we're kind of utilizing
proof throughout all of this. We're
having all of this do the verification.
We're having everybody check with
computer use, with um running API calls.
We're having all of this be proven and
double checked and triple checked before
we ever go try to send it off to people.
So, the six Ps are all coming along
really well, but obviously we're not
done yet. We've got a lot of stuff going
on. So, I will just kind of monitor this
and I will check in with you guys when
there's something else interesting
that's happening.
Okay, so here's where we're at now. When
we had Codeex go through and make all
the changes, it was able to fix
everything. Sorry if you guys hear
thunder or see lightning. It currently
is storming. And then it verified
everything. It ran 85 checks and said,
"Okay, cool. This stuff is now good to
go." And back in Claude, what happened
was I said, you know, hey, here are our
Superbase tables. And it basically
tested it out. Now, it did a test user.
It populated the table and it ran the
full customer journey as a smoke test.
We can see that it signed in. It did a
brand kit and case study. It created a
project. It analyzed it for 4 cents.
Generated the deck for 9 cents. Did a
watermark. Did a Stripe checkout web
hook. Watermark is delivered or sorry,
watermark was removed and all of that
happened with 13 cents for a full deck
for a new user. So, it found all this
stuff and now we're going to see what's
going on. It was building out some more
things. And then I basically said,
"Okay, cool. So, Codex is done and it
fixed all those things that it needed to
fix. Where are we at? And so, now I'm
basically looking at how I can test the
onboarding flow myself. So, I'm
basically going to open up this new
local host. And it open up on my other
monitor. Here it is right here. And this
is what the actual page looks like. So,
for AI agencies and automation builders,
turn every discovery call into a client
ready proposal. We obviously have some
information here. We didn't even design
this page if you guys remember. The only
thing that we had so far designed was
the weight list page, which was this
one. So, they have similar vibes because
they have, you know, the same sort of
design system. But what I did notice
here is that client pack did not use the
logo. The claw version didn't use the
logo of the actual client pack website.
So, we're going to have to fix that. But
that's a small thing. So, now if I go
ahead and say, let's just do start free.
So, I'm going to create an account real
quick. I'm going to go ahead and hit
sign up. Okay. So, it actually needs us
to have an eight character password. So,
I did 1, two, three, four, five. We'll
do 678 and 678. Let's see if that's
strong enough.
Okay, that's not a valid email. So, I
guess it has to be a real email. So,
that's cool. I didn't have it do any of
this verification, right? But it's
already baked in there. So, that's
pretty cool. Let me try this now with a
real email. Now, I put in an actual
Gmail that exists. I'm going to go ahead
and sign up. Let's see what happens.
Boom. Okay. So, so we have to go confirm
our account and then log in. So, I'm
going to go try to do that. So, this is
pretty cool. We get an email from
Superbase O. So, remember I didn't have
to set up any of this as well. So, I'm
going to go ahead and click confirm
email address. It takes us back to the
weight list page. We might want to fix
that. That's a little weird to go back
to the weight list page, but either way,
let's try to log in again now. All
right. So, now that we have logged in.
Cool. So, now we are in here. We can see
this is what the setup looks like. Three
things and you are running. We have a
brand kit. So, we can put in our name.
Let's just put in AI. Let's go ahead and
choose a different color. Let's make it
more of like a sort of a light blue like
this. Perfect. And let's go ahead and
upload a logo. Cool. So, we got that
filled out. Let's go ahead and save and
continue. Case study. I'm just going to
put in some really quick example one.
I'm actually just going to do these
placeholders. So, okay. So, this is
obviously where you'd spend some time
and you'd add some of your own case
studies, but we're going to click on add
and continue. And now our very first
client. So, let's go ahead and test this
out. I'm going to go back into Codex
real quick and say, so I'm currently
going through the onboarding flow just
to test it out for this app. Can you
give me um an example
client name, what they do, and call
transcript for me to paste in here just
to see how this actually works. Okay, so
we have this information in there. I'm
going to click on create project. And
now this is kind of the experience that
we're already pretty familiar with. We
have the transcript. We can analyze the
call. I'll go ahead and click that. And
we actually see sort of like a progress
bar of this currently being analyzed by
AI. Man, the lighting in this video has
just been
all over the place. Sorry about that.
Okay, so this is cool. Now that it's
analyzed the transcript, what it did is
it basically put in here all the pain
points and the constraints and all of
this information. And before it actually
wastes our tokens, wastes the user
subscription building out the deck
because that's a little bit more token
intensive. It wants you to review and
confirm all this stuff, which is really
important. So we would now read through
the pain points. We would say how severe
they were. We could see if the exact
quotes actually match up. And then we
could come in here and just make sure
that this information is correct based
on the call. And if you know, maybe they
really really prioritized a certain
element or they really stressed
something in the call, you could make
sure that the deck is going to hit on
that. So now you'll click on I checked
the pains, metrics, targets, and
investment. These are ready to show the
client. I'll go ahead and hit generate
deck. And once again, this will probably
take um this will probably take a few
minutes. The analyzing didn't take as
long. The transcript wasn't super long,
but this one will probably take a little
bit longer. And just for a quick time
check for you guys, it's currently
almost 3 p.m. If I go here, 2:52. So,
we're chugging along, making a lot of
good progress in, you know, just about 6
hours of of today's work. Awesome. So,
the deck is ready. We have three panes,
$12,000 investment, 11,932 value per
month. I'm not exactly sure what that's
coming from exactly. It feels like I
guess um they're paying $12,000 and each
month they're getting this much value
back. So, they basically are making
their money back in one month. But,
let's go ahead and click on view deck.
I'm not going to read all of this, but
you see we have our logo, we have our
color scheme. This is the color I put in
there. And we're going to just kind of
flip through real quick. It's all
matches the color scheme. Once again,
it's all very consistent. Every single
time we get 10 slides and we have this
repeatable flow. So, as you're kind of
presenting this to the client, you're
going to get really, really good at
being able to like communicate this very
well. We have our actual little um
visual diagram right here as well. We
have some proof. We have the scope. And
then we have our final sort of like call
to action. So now what you notice here
is this says free deck carries a client
pack watermark which is in the bottom
right. So right there you can see made
with client pack. If you want to remove
this, you can upgrade. So let's go ahead
and click upgrade. See what this looks
like. We used up our one free plan and
now we can get on a plan for 39 bucks a
month. So let's click on that. And this
is going to open up a checkout. Perfect.
This goes straight to a uh sandbox as
you can see a stripe sandbox. We have
$39 per month and then we're able to go
ahead and pay through here. So, because
we're in Sandbox, we basically paid with
a fake card. As you can see, there's
like a whole list on Stripe docs of fake
cards you use when you're in sandbox
mode. And then we actually are now on a
subscription. So, we have an active
plan. It renews September 9th. And let's
see, we have one out of 25 decks have
been created. If we wanted to actually
cancel, we would go to manage billing.
This would take us to a Stripe portal
right here where we could go ahead and,
you know, update our information. So,
this is all Stripe. Super easy. Stripe's
handling that. We know how to set that
up or sorry, people know how to cancel
subscriptions. It's super easy. Cool.
So, let's just real quick go back to our
actual project. Let's click on our deck
and make sure that now the watermark has
been removed. Cool. So, now the
watermark is removed because we are on a
paid plan. Awesome. So, all of that guys
was so so so easy to set up, but now
there's some other things to be thinking
about. Let's just say that this is kind
of V1 of our product of our app and V1
is done. There's a lot of other things
that we want to think about too still.
Real quick, I wanted to show you guys
what this actually looks like inside of
our database. So, this is Superbase. We
have decks. So, it's going to store the
data on all of the decks that have been
created. You can see um we have
information like the time that it was
created. We have information like the
actual content of the decks. We have our
case studies. So, when people are
putting them in, we're assigning that to
a user ID. So, that's kind of like the
unique key. Um I'm curious though, brand
profiles. Okay, cool. So, this is when
people sign up and create an account,
they now have a profile. And this is
where we can see stuff like their
colors, their logos, what they do, and
this is where we basically associate
these IDs with all of the other things.
So like this user ID is associated with
me. And so in the case studies, it's
there too. In the DEX, it's going to be
there, too. As you can see, that's kind
of sort of like the um the primary key
that relates all of these tables
together. So we can also see our
subscriptions. And that's really really
cool because once again, we didn't set
any of this up. It basically linked all
these tables together. Now, I'm also
curious in the Stripe side because we're
in our test sandbox. I'm wondering if we
come into our transactions here. This is
what we see. We see two subscriptions,
right? Um I can see 39 bucks succeeded
and we have a subscription creation.
Now, if I click into the subscription
creation, we should see that this
hopefully is going to auto renew because
in Stripe there is a difference between
a subscription and sort of like a
one-time
um product, right? So, here is one of
our products. We have client pack. This
is either $39 per month or $390 per
year. And it says that there are two
active subscriptions on this product.
So, that's how we know that this is
going to actually build them again in a
month, right? So, here are the two
active subscriptions. These are the ones
that we just signed up with. Awesome.
So, just think about that, guys. All we
had to do was come in here and give
Cloud Code or Codeex, both of them, API
keys for Stripe and API keys for
Superbase. And it set up everything. It
did all of that plumbing on the back end
so that we as humans just get to focus
on these things, right? The pain and the
promise, the experience of the product,
the packaging, and then the proof, which
is the boring stuff, the verification AI
can handle. The plumbing, the boring
stuff, the technical stuff, AI can
handle once again. And you guys saw me
do all of this. Every single prompt that
I shot off to these two coding agents so
far today, you've seen me, you've heard
me do it. And I'm 100% confident that
all of you guys could either replicate
the prompts that I sent off or you could
just also instruct the agents yourself
in the same way that I did it. But I
[snorts] did mention that there are some
other things to be thinking about,
right? I want to talk about some
security stuff. So I'm going to do this
in Codeex because I trust Codeex's
verification and security just a little
bit more. It feels a little bit more um
like it's able to just obey what I'm
saying and it stays on the path whereas
Claude can get a little bit creative
sometimes. So, what I'm going to do in
here is I'm just going to clear the
session. I'm going to go ahead and clear
the session. Okay, cool. So, what I'm
going to do is I'm going to paste in
this prompt, which I'm going to show you
guys. So, I'm not going to read this
entire thing out, but this is a prompt
that I like to use for security
reviewing, right? And you can see that
this is going to say to audit against
the OWSP
5.0. And that is actually a GitHub repo
that I'm going to show you guys right
here, which has a bunch of security
stuff because we've now set up
authentication. we've set up some
payment processing and we want to have
more confidence that someone couldn't
basically like hack the app and find the
other information from our clients like
find their credit card information, find
stuff like that. So, what I'm going to
do is copy the link to this GitHub repo
and I'm also going to basically just put
this in to this prompt so it understands
what's going on here. And then at the
front, I'm basically just going to add
So, we've basically just finished the V1
of our client pack app as you've been
helping me kind of work on. And you can
see because you're in the folder now
that we're ready getting ready to start
having customers come on and get
authenticated and create accounts and
start, you know, actually using the
product. We want to do some security
checks. So, here's what I want your help
with. And I will just kind of like
slowly scroll through this prompt so
that if you want to screenshot it and
copy it, you can feel free to as you see
right there. Okay. So, now I'm going to
shoot this off. And this is kind of the
next step that we're working on is just
trying to make sure that we're locking
things down a little bit as well. And
then while this is happening over here,
I'm going to go back over to Claude and
I'm going to tell it what's going on.
So, hey, by the way, I currently have um
Codeex helping us figure out some
security stuff. Just making sure that we
have everything locked up. People can't,
you know, throttle it and take advantage
of us, prompt, inject, steal things. Um,
I don't want to leak data, stuff like
that. So, it's going through that. I
went through and tested the whole flow.
I signed up for an account. I paid. I
did all that and it worked great. So,
good job. But now what I want to start
thinking about is we're starting to get
ready to put this out there into the
world and to actually invite people to
sign up and start testing it out and
giving us feedback. So what's your plan?
How do we actually think about pushing
this to GitHub? How do we think about
deploying this? How do we think about
managing users at scale when more people
start to come in? So let's say for now
the first milestone we want to hit is 50
paying users. How do we get there and
how do we support that? What does that
look like? Now, there is going to be a
big difference as we start to scale from
50 paying users to 500, then from 500 to
5,000. At each of those milestones,
there's going to be different things you
need to think about. And so, I'm not
going to dive into a lot of that
technical autoscaling and all this kind
of stuff right now. But let's first just
look at getting our first, you know, 50
paying users and making sure that we
have an actual action plan to get all of
this out there in the world in the right
way. So, let's take a look at what it
said. It said obviously hey good timing
on the security pass but phase one this
week we're going to do GitHub and
staging deploy. So the sprint repo is
already git with a clean history and
before anything leaves the machine we
have to run a scan over everything to
make sure nothing got committed have a
private repo out there in our GitHub
account and then Verscell will deploy
straight from GitHub on every push. So
that will be perfect. Phase two will be
the production cut over. So everything
that we've done up there is going to be
just test keys, uh, test sandbox,
stripe, all that. And once we're out
there, then we can go ahead and switch
everything. So we will get Stripe into
live mode. We will turn on the subbase
email confirmation and we will terms and
privacy pages. That's a good idea. We
will draft those out and make sure that
people are kind of accepting those as
well. And then we have um error
tracking. Basically the idea that
everything is being logged. All of the
actions are being logged. We have alerts
when there are errors because that's the
other thing about, you know, the whole
debate about like build versus buy. Yes,
there's a lot of things that you could
now build, but when you build, you kind
of have to realize that that's now a a
ball that you have to keep juggling
forever. Like in some form, you are
responsible or someone on your team is
responsible for that. So, same thing
when it comes like a SAS product. The
idea is, oh, you know, I can build
something once and sell it forever. Lots
of people buy it, blah, blah, blah. But
there's a lot of things that you have to
keep doing when it comes to maintenance.
So starting to think about how you set
up error tracking, notifications, um
things like that, right? Then phase
three is first 50 paying users. The info
answer is boring, which is good. 50
users is nothing for the stack, which is
great. Subbase pro 25 bucks a month for
backups. For CellPro, 20 bucks a month.
Worst case inference at full cap is
three bucks per user per month against
39 bucks that they're paying. So that's
good margins. But then it's starting to
think about the operating loop. So
inviting in batches, not all at once.
having a feedback channel, having
support, you know, customer support's
something that you have to deal with,
billing issues are going to come up,
people might get locked out. Um, what if
they forgot their password? How do we
help them automatically be able to reset
that? Like things like that are other
things that we need to bake in the
functionality of this app. It wants us
to watch three numbers weekly, signups,
first deck generated, so activation, and
then first deck into their paid
conversion, and then just kind of
watching the price and seeing how we
might need to affect it. So, from a
technical perspective, nothing here
surprises me. Nothing here is too out of
the ordinary, but I'm glad that we had
cloud code basically validate that
GitHub is kind of where the code base is
going to be stored. That's where we'll
have commits. That's where we'll have
pull requests and things like that. And
then Verscell is going to be where we
actually go ahead and deploy that on our
URL. And I already showed you guys
earlier how easy that is to create your
GitHub account, to create your Verscell
account, sync them together, and then
just say, "Hey, Codex, hey, Cloud Code,
push these changes to GitHub." And then
Versell picks it up automatically, and
it will just deploy super easily. You
can buy a URL on Verscell. You could buy
one on uh NameCheep, GoDaddy,
Squarespace, Wix, wherever you want. If
you already have an email domain or you
already have a domain you want to use,
you can easily switch that into Verscell
as well. You just have to point the DNS
records at it. Super simple. Claude can
obviously walk you through that step by
step. It's very, very easy. But really,
the last thing that I'm waiting for is
for Codeex to finish up here. It's
running a two tenant test and it's
testing things out. Look at this. It
found something that failed. So, it's
going to be really interesting to see
what sort of like conclusions Codex is
able to make here because this is being
treated as a readonly security review.
So, it's probably going to come back and
say, "Hey, I found major red flags. I'm
glad that you did this security check
before you push this off. Let me go
ahead and fix all these things." So, I
will just go ahead and check in with you
guys once this comes back. We're only at
step one out of six, so this might take
a little bit, but I'll check in with you
guys in a bit.
Okay, so in a weird way, this is exactly
what I wanted to see. Client pack is not
ready for customer onboarding yet. It
found four high severity release
blockers plus a critical configuration
condition that must be ruled out before
deployment. And let's just be honest,
these are probably not things that I
would have found myself if I wanted to
like inspect the codebase or whatever. I
would have needed a talented human
engineer to be able to look through
this. But because we can now give Codeex
some of this extra subject matter
expertise and as we know these models
are getting a lot better at cyber
security and things like that, I'm able
to do this in a way where I feel more
confident about it. So what I did is I
read through all this. We can see what's
blocked. We can see what's, you know,
what's been found that we need to fix.
And I'm basically just going to go have
this fix all of these things for me. Now
you can see it found like 10 things. It
marked like only four of them as the
high priority, but it still found a lot
of things. So it also tells us though
there are things that passed our review
which is at least good to know that it
didn't completely just like drop the
ball on this. And then there are some
things that we need to as a human we
still need to verify like switching the
production mode on. Right now it's you
know demo mode equals false. Um the
stripe keys, rotating the entropic key,
all these other things that we need to
do but for now let's go ahead and just
have it fix these things. So awesome.
I'm glad you found these vulnerabilities
so that before we push it into
production and have actual customers
start using it, we can fix these things.
So, what I want you to do is spin up a
team of agents. I want you to once again
play project manager. I want you to
orchestrate each agent to do one
specific task and you are the verifier.
You are there to make sure that they're
doing everything correctly and that
there are is nothing that's still going
to slip through the cracks. So, you
should basically not stop until you're
100% confident that all of these
vulnerabilities that you found have been
resolved. And just to make this even
stronger, I'm going to use this as
a/goal prompt because I want it to
continuously iterate and verify and
verify and and write tests and run tests
until it's confident that all of these
issues have been resolved. If there's
anything that's being blocked by me as a
human that you can't physically do
yourself, then feel free to leave that
till the end and then say when you give
me the final report, say, "Hey, by the
way, you still need to do these things."
But other than that, I want you to go
fix those vulnerabilities that you
found. Okay. So, while it's doing this,
we can still start pushing things to
GitHub and start that whole process of
switching things over because that's
really important is that like you're
going to be able to push things to
GitHub and they'll autodeploy and then
you're going to make changes. You're
going to work on changes for a week,
maybe a few days, and then you're going
to push to GitHub again. And that's a
flow of basically updating the app, you
know, rolling out updates, rolling out,
you know, different versions. That's
exactly how our apps that we have to
update constantly, that's how it works.
So, what I'm going to do is I'm going to
go back over to Claude and we're going
to start getting this set up in GitHub.
All right. So, I'm ready to start
pushing this into GitHub. Now, once we
deploy the code there and then I sync
that repo to Verscell, my understanding
is that we're going to have to give
Verscell the environment variables that
it needs like some of the API keys and
things like that. So help me understand
what we have to do there and go ahead
and create a private repo in my GitHub.
I should be authenticated in just call
it our client pack application. There
was also one other thing I noticed which
was in the whole onboarding sequence if
you are on the main page where you sign
up for an account we didn't have the
right client pack logo. So please go
find the logo. It should be somewhere in
our project and update that website
because that obviously needs to be using
our real logo. And so what's going to
happen is we're going to have this push
out as a different Verscell project. If
I go back to Verscell real quick, this
is going to be something different. So
in our homepage, we have different
projects for, you know, different repos.
And because we're building this out as a
different repo, we're going to be
creating a new project for it. Now, what
you could do is you could have
everything come off of one domain if you
want to. You know, you can have like the
main domain with a bunch of different
slash sort of like routes and you can
point to different places obviously, but
we're just going to be doing this as a
separate one. If you wanted to make it
all cohesive, you wanted to merge
everything into one, you certainly
could, but that's just the way that
we're going to be doing this today. Now,
if you're confused about what I said
about this whole like versel environment
variables thing, let me explain that
real quick. So, as we know in this
project, we have our files, right? So
basically what happens is all of these
files will get pushed to GitHub which
means I could you know work on my laptop
if I needed to. I could you know work
somewhere else someone else could be a
collaborator but what happens isv
files or anything that's listed inside
of the ignore don't get pushed to
GitHub. That's a security feature baked
in because you don't want um API keys to
be out there on the web exposed right.
So what's going to happen is it's going
to push everything to GitHub except for
the&amp;env API keys. So, Stripe, Superbase,
anthropic, other things like that. And
the problem with that is now how is
Verscell going to be able to actually
hit those providers? If Verscell doesn't
have those keys, it can't use Superbase,
Stripe, Anthropic, whatever else we
need. So, what we're going to have to do
inside of Versell is we're going to have
to set up some environment variables for
this specific project. So, just as an
example, let's pretend this was our main
production one. We would come over here
to environment variables, and this is
where we would add our API keys. So it's
basically just the whole idea that we're
adding environment variables places that
are secure and that won't transfer
through the public internet anywhere. So
the only way that people would get these
environment variables is if they were
able to sign into our forc cell account.
So that's what I meant. I'll show you
guys how to set that up in a bit. It's
super easy. You basically just enter the
key, you enter the value, and you can
just put in as many API keys as you
want. So the same way we add it to ourv
file when we're here in cloud code,
we're just going to do it in versell as
well. And if you've done things like
deployed automations to modal or
trigger.dev, it's a very similar thing.
It happens the same way like nitn it all
happens like that. Okay, so it says the
logo has been fixed. The GitHub is live.
Let me just open this up real quick. And
cool. We got our client pack
application. We have Oh, that was Codex.
Codex is still going ham on that
security stuff. Um, these are the
variables that we're going to have to
add inside of our cell. We're going to
have to do demo mode equals false. We're
going to have to do enthropic API key.
We will rotate it and then we will paste
a new one into the um versel. So it's
using probably like opus 5 or something
on the back end. Then we will do once
again our subbase stuff. We'll move that
into versel. We will do our subbase uh
service ro secret. Mark it as sensitive
in verscell. Okay, good to know. And
then stripe and admin emails. Cool. Two
values can't be set after the first
deploy because they depend on the URL
Versel assigns which are next public
site the deployed URL and the Stripe web
hook secret a new secret in the Stripe
sandbox dashboard in developers web
hooks add endpoint the CLI secret we've
been blah blah blah okay so the fastest
path is to connect the repo in Verscell
and tell me when the project exists if
you run Verscell login in a terminal I
can handle the environment variables the
two-step redeploy and the PDF smoke test
myself that's awesome so let's just go
ahead and do that. Yeah, totally. Let's
do the Verscell login so that you can
handle all of that. And also guys, just
to show you again, I could switch back
to Opus because we really don't need
Fable to be doing this, but all of this
work that we've done, we've only used 7%
of our Fable limit. You know, this whole
idea of having it just orchestrate and
brainstorm with you is not going to eat
so many Fable tokens or your entire
weekly 5 hour and context window limit.
If you're doing it like that, rather
than just saying, "Hey, Fable, go build
me an app. Go build me a website."
That's when it uses all of those tokens
and becomes very expensive very quick.
So cool. You can see right here it
opened up my authorization for for
Versell. And I'm just going to go ahead
and allow my cloud code to use our
Verscell CLI in order to set up the
project. Put in the environment
variables, mark it as sensitive, do all
the stuff that it needs to do. That just
makes our life so much easier. So that
is great. The moment it completes, I'll
take over. Link the repo as our shell
project under the root directory sent to
client pack. Load all the environment
variables. run the first deploy. Cool.
Now, one thing to do in parallel if you
have a minute is to rotate the entropic
key. So, what I'm going to do is I'm
going to actually just I'll copy this
URL. I will go into a browser, paste
that in. So, this is basically just the
dashboard where we're able to use
anthropic API keys and things like that.
So, I'm basically just going to rotate
the one that it gave us and then give
Claude a new one or I'll put it in the
environment variables of a new one that
it can actually use in production for
this app. So, you can see I'm just
making a new one in here called client
pack. I'm saying it expires never. I'm
going to add this. And then now that
I've copied that key, I can basically
remove this old one, which is the one
that it was using. I'm just going to go
ahead and disable that. And I can paste
the new one right here inside of the
env.local. Hit save. And now Claude can
actually push that into our versel
environment variable. I also just
changed that entropic key. I rotated it.
So you have the new one inside of the
env.local. And by the way, in codecs,
when you're seeing all these little
different icons, these are different sub
aents that are working. So, we have like
this green one finished up. This yellow
one is going, this red one is going. And
you can click in just like you can in
the cloud desktop app. And you can see
the prompt that was shot over and you
can see what they're doing. So, if you
were confused by what those were, that's
what it was. You can see this little
icon basically means that it's using the
browser, I believe. So, if I click into
here, you can see that it's running the
browser. If I go over here, oh, sorry,
right there. Client pack. It's once
again doing the same thing where it's
navigating around and making sure that
everything's good. So, it's really
interesting if you actually just like
watch codeex or claude as they're
building out and as they're doing
things. You'll learn a lot about how
they work under the hood just because
they'll visually sort of tell you
exactly what they're doing and you get a
lot of visibility. Cool. So, as you can
see, because we authenticated in it set
up this project for us. So, in versell
it created this one clientpack.cell.app.
We'll obviously connect a real domain to
that, but that's what it got for us at
the moment. You can see that this is the
only one that is not yet connected to a
git repository. So that's something that
we will of course set up in just a sec
here. But that's just showing you that
cloud code is now interacting with our
versel which makes things much easier
for us. And it's checking on some other
things now.
Okay, it's now 4:14. So what is that?
It's been over 7 hours now. Just barely
over 7 hours of when we started this
build. And we're in a good spot. So what
happened here is we have everything
pushed now to Verscell. If I go over
here, you can see that we have the
client pack. Um, it's not yet connected
to a GitHub repository, but we do have
this running. So, if I click on client
or sorry, clientpack.verell.app,
we have the actual sort of like the real
landing page. We have the real logo has
been updated. And we also, just to
remind you guys, this is separated from
our actual like waiting list page. So,
we initially had the waiting list. We
could have been shooting that off. And
now that we no longer need the waiting
list, we can now just kind of send
people here. So, from a design
perspective, there's a few things that
I'd probably want to change about this.
Claude made this one, whereas um Codex
made this one. And I honestly prefer the
codeex version. So, I'd probably want to
say like, hey, you know, this is our
currently waiting list. Let's make the
vibe of the actual landing page more
suited to this. And we'd redo that,
right? But this is what we have. And
then we have our whole thing where we go
through either logging into an account.
So, if I come here and I log in with the
one that we already have,
I I'm pretty sure this should have
stayed because we put this through the
same database on the back end.
Cool. We log into the actual account.
This is the example that we tried
earlier. But if I sign out now, I should
be able to actually sign up for an
account and go through the whole
authentication or sorry, yeah, go
through all of that one more time
because this is deployed, but it's not
yet connected to a GitHub repo. If I go
back to my projects, you can see we're
still not connected. And that's okay. It
just means that this wouldn't auto
update. We'd have to say, "Hey, Cloud
Code, go update this on Versell using
the CLI, blah blah blah." But what we
want to do is we want to connect it to
GitHub. And before we do that, we want
to make sure and check in on codeex over
here. So this ran for about 45 minutes.
And it fixed a ton of stuff. So we
rotated the key. We did all the things
that it said. Look at all these things
that it verified. 7 out of seven on the
application tenant attacks. We had
database migration checks. We had web
hook guard, strike mapping, logo
attacks, PDF attacks, all this kind of
stuff. So, I'm really glad that we took
the time to do this. And this is
probably something that we'd maybe want
to do every single week as more users
join, as we add things to the codebase.
So, this should all be synced together.
What I want to do now is we want to
start to actually connect this to GitHub
so that we can sync everything over. So,
Codeex just finished up a security
review. Um, I want you to basically make
sure that we have everything in one
place so that we can push the most
recent version of all of these changes
that we've made to GitHub and then I can
connect GitHub to Verscell for auto
deploys. And then we're going to go
ahead and set up like the custom domain
and everything like that. And we'll do a
full sweep through to make sure that
this is all working as expected. Just
like the exact same way that we did this
earlier with the actual landing page,
how it's connected to Verscell, we're
going to do as well with this one, which
is the actual application. You can see
there's been 55 commits. So, we have
been making tons of different versions
on here. This is what we've been working
on pretty much the whole day as far as
you know like the product actually goes
the product and the plumbing. And what
else I wanted to show you guys in here
in client pack if I go to the
environment variables here is
everything. This is where cloud code
wrote all of this to versel. It did all
of these that we would have manually had
to plug in one by one. So this is
awesome. It has all of these secrets.
The only thing we'll have to update is
when we do want to switch this to live
billing. So, our real Stripe, we would
obviously come into Stripe, we would
switch out of our sandbox, and we would
go back to a real environment, and then
we would grab those API keys. And it's
the exact same process as you guys saw
um where we come into here, we go to our
developer, we go to our API keys, and
then right here, I have my publishable
and my secret. You can see these are SK
test and PK test. But when you leave the
sandbox and you go to your actual real
environment, you'll have PK live and SK
live. So that's how you know that
they're actually real and they are no
longer in a sandbox. Super easy change.
And then you could tell cloud code, hey,
I just put these new ones in the EMV.
Can you go ahead and push those to
Versell and update the environment
variables and we should be all set. So
it's going to go over and make sure that
it understands what codeex did and make
sure that the codebase is completely
merged together in one master branch.
We're going to push that to GitHub and
then we'll get this deployed for real on
Verscell with auto updates and we will
connect a real domain. Okay. So now the
most updated version of what we're
working on is actually live because
we've connected it here as a GitHub
repo. As you can see if I go back home,
you can see that this is now connected
to our client pack application repo. Now
I did run into some issues. You can see
down here because what happens sometimes
is if you aren't authenticated in or
sorry like codeex or claude will try to
push changes to your GitHub repo and
then it gets blocked on the versel
deployment. So basically just tell
Codeex or Claude what's happening and
it'll be able to fix it. In this video
the Verscell deployments hasn't been
super smooth. Typically when I push
things to GitHub and then Verscell picks
it up. It's like super simple. Nothing
happens. But every once in a while you
will run into issues but once again
they're pretty easy to solve. So we now
have clientpack.verell.app.
We can go in. We can do everything. And
before we go through the final flow I
want to give this a real domain first. I
want to give this a domain that we
actually like fully own. So, I'm going
to do here is go over here down to the
domain section. I'm going to go ahead
and buy a domain. I'm just going to do
this right through Verscell to make it
super simple in this video. Once again,
you don't have to. If you have one on
Squarespace or GoDaddy or NameCheep, you
can bring that in with the DNS records.
It's very simple. Claude or Codex can
walk you through, but I'm going to do
what we were looking at earlier. Get
clientpack. We'll see if we can do just
We'll do getclientpack.com.
We'll go ahead and grab this. I have
bought that domain. As you can see, it's
going to go ahead and get that set up.
And now I can just add this to the
project. It should be super super
simple. Let's see if I can go ahead and
give this page a refresh.
What is going to happen with our domain?
Cool. Okay. So, I So, I think I'll click
add existing. Um, we should be able to
type in what is it? Getclientpack.com.
There it is. I want to connect this to
our production. And I'm just going to
click on add domain. And it's pretty
much just setting everything up right
now. So if you wanted to bring one in
that wasn't in Verscell, you would
basically just type it in and then it
would give you it said, "Hey, add this
to the A record, add this to the C name,
whatever it is." And you would just have
to set that up super easy. But because
you bought this in versel, it's going to
just be able to do that automatically
and it's getting that set up right now.
So now if you look at this, you can see
the domain that we have is
getclientpack.com
and that's what I can click into and go
through this flow. So let's do one final
test here. I'm going to log into our
account that we made earlier. Aha.
Interesting. So, when I try to log in,
it it booted me out. I'm going to try
that one more time and see if this is
working. Okay, so the login does not
seem to be working. I'm going to just go
back into into Codeex and we're going to
see what's going on here. This is why
it's so important to even though you're
just simply migrating something from um
one environment to the other, you have
to be careful about it because I think
it has to do with the authentication
that we set up. I think it has to do
with our our security thing because one
of the things that we had to do that I
didn't actually show you guys was we had
to create another table because when
Codex ran the security it said hey let's
add these other two tables in here to be
able to track things better and I was
like yeah it's a great idea. So maybe it
messed with something on the back end
with our subscriptions. I'm coming in
here and taking a look. We can see we
have one of these got cancelled. Um I
don't think any of this is what's
messing with the app not working. So
let's just go back into codeex. Cool. So
that looked like it worked on Verscell,
but now when I am trying to actually log
into the app, I'm logging in with my
nate88@gmail.com.
And when I click the login button, it
just sends me to a page that says that
it's not working. So can you help me
figure out why this isn't working and
what we need to do here so that we can
make sure that the app is working as it
should be. Now, this is really weird
because I just logged in. As you guys
saw, I just logged in and it worked, but
this is not the right domain. This is
myverell.app
domain. So, I'm not sure if it just was
taking some time to transfer over. Let's
try it one more time real quick. Or if
there's genuinely something wrong with
the real URL. Okay. Yeah, there's
something wrong with the real URL. So,
we have to figure out why that is.
That's probably some context that I
should add to this. So, I'm going to
tell it real quick. Okay. So, it's
interesting because on the um
clientpack.forcell.app,
it works fine. No issues. But what I did
is I connected a new domain. I connected
getclientpack.com
and when I connected that that's the URL
that's the domain that's actually having
these issues. So I'm not sure if that
helps you know with give you some more
context to help figure out what this is
but okay never mind. It looks like you
already figured that out. It says right
here I found a strong production only
clue. You failed login came from
clientpack.com, but the request stopped
inside the security middleware and never
reached the login action that matches
the app's cross-sight protection
rejecting the form when next public site
URL is configured for a different host
name, most likely clientpack.cell.app.
I'm confirming the response status and
the configured production host name
before changing anything. Okay, so that
makes a little bit more sense. Now,
let's see if it can handle this or if
we're going to have to like redeploy
this whole project. Hopefully that's not
the case, but let's see what it's able
to find. It looks like it's going to be
able to redeploy to this domain, so we
should be good, but obviously we'll have
to test that out. Okay, so it's saying
that this should work now. Um, it
confirmed that all of that exists.
Confirmed that it changed this variable.
Confirm that the Superbase security
tables are deployed. So, let's open this
up again. This is the correct domain.
And fingers crossed that this works this
time.
Okay, this is a good sign. It's loading
a little bit longer. Cool. There we go.
And we have once again our data is still
there. Remember, if we were to log in as
someone else, then this data wouldn't be
there. So, what I'm going to do now is
I'm going to sign out. I'm going to sign
up for a new account on the real domain.
And we're just going to run through this
flow again and and make sure that
everything's working, the database, the
payment, all of that. Okay, cool. So, I
just signed up and now it's asking us to
confirm our account once again. Here we
go. This is the Superbase O email. So,
I'm going to go ahead and click confirm
email address. This once again takes us
to the weight list. So, if it really is
annoying me, I could go ahead and change
this. But right now, that's not a big
deal. It would also be as easy as one
prompt to change where that hyperlink
goes to. And now we have once again
logged in with a new account. So, there
we go. We are going through the
onboarding, everything like that. What
I'm going to do now is I'm just going to
jump straight to the billing because we
already know what that onboarding looks
like. And we're going to sign up for 39
bucks a month. And we're going to see if
this still works. So, it takes us to the
Stripe page. This is obviously still the
sandbox. We just want to make sure that
this is all working on the new domain,
which it should be because we're in
Stripe. And that looks great. Boom. So,
as you can see, that all worked. We are
now on a monthly plan. We have 25 decks.
And we could go ahead and finish getting
onboarded. We could make our first
project. But the point being, if you're
logged in with a different account, it
will save your data. It will save your
password. And you can authenticate in to
your own account. And all the
subscription stuff is set up. If we go
back to our Subase table, you can see
that we just have a new entry come in.
If I refresh, there we go. You just saw
it pop in. And that is the one that we
just did. So we have all of this on the
back end set up. And our agents know how
to navigate it, change it, look through
it, all of that kind of stuff, which is
obviously great for us. And now, like I
said, it would just be a matter of
switching out of test mode. We would
click exit sandbox. We would go to our
developer keys once again, and then we
would just switch these in to Verscell,
and boom, we'd be all set to actually
start receiving real payments. Okay, so
it is 5:10, 5:10 p.m., which means that
we've been working on this pretty much
since like 9:00 a.m. So it's been about
8 hours. Now, think about the fact that
those eight hours were not just me
sitting down working the whole time. I
actually did a few other things today, a
few other projects I worked on. And I
also had lunch, went down to the gym,
went on a walk. I was able to keep
working on this all day because all you
guys saw me really do was think about
what I wanted and prompt it in a pretty
careful way. The majority of the actual
work that was done, I was kind of just
sitting here watching it and making sure
that nothing crazy was happening and I
was just giving it feedback and help
helping to steer it really. But once
again, I think the really important
thing to take away here is that you're
not going to be able to build a SAS in
one day and go scale that thing to a
million dollars. You're 100% able to
build a waiting list and to start
building ideas and to start building
demos and PC's and start shooting those
off to people, maybe even start figuring
out how you can start to acquire clients
for it, but you're not going to be able
to like build an app in one day with AI,
scale it to the moon, and make a million
dollars and never have to touch it
again. I think that that's just very
unrealistic. Now that I've been able to
sort of peak behind the curtains of what
it actually takes to build an AI first
SAS and when I've been building
different products and different
automations on the back end and I know
how much maintenance is truly required
as you scale the usage and users and
throughput and there's support and
there's all these other things to be
thinking about especially if you want to
actually build a brand and not just like
a quick cash grab. All right. So, now
that you guys have seen kind of like the
building side, what does it look like to
sort of try to come up with the idea,
plan it out, start to build it, start to
verify, start to integrate some stuff.
And obviously, that's just like one
iteration of the loop because you're
going to keep doing that. You're going
to keep looping, looping, improving
things, updating things. That's just the
nature of a product. Now, I want to talk
a little bit about what it looks like
and how you should be thinking about
getting customers, keeping them, how do
you actually make decisions for the
business, these types of things. So,
let's just start to dive in here. I want
you to think about as I'm going through
this deck,
what it looks like to get your first,
let's just call it 50 customers.
Because, as I kind of alluded to
earlier, there's different levels to
scale. Sometimes a certain amount of
customers is going to require different
things on the back end, technical
scaling infrastructure, but then there's
also going to be different things to
think about when it comes to scale. Um,
other types of hires you might need to
make, other types of automations you
might need to make, and it's going to
sort of grow as you grow. So, I think it
would be honestly a terrible thing for
the business if you built your product
and then the next day you had 10,000
customers sign up. It would probably
break. It would destroy the reputation.
you you would learn a lot of lessons too
late. So you think about it in the
phases. First milestone, let's just say
getting your first 10 customers, getting
your first 50 customers, right? Okay. So
more attention cannot rescue a confusing
offer. So what does that mean? Let's say
I right now have distribution, right?
Because I've got a YouTube channel. I've
got a community. because I have so much
attention coming into the content I put
out, that doesn't mean that I could
automatically just go sell a ton of some
sort of SAS tool because the offer has
to be extremely clear. Now, remember
earlier in this video when we started
building, the first thing we started
talking about was pain. And there's a
reason why I put this first because we
have to start with something that's
actually a problem. If you think about
what most people say when they had
invented something, they basically say,
I I saw this problem in my own life and
I had to solve it because there was
nothing else out there that I found that
solved this problem. So that is the
pain. From there, you obviously have to
be talking to one specific person. Same
thing even if you're service- based,
even if you have a YouTube channel,
whenever you have some sort of goal,
whatever your goal is, you're usually
trying to you need to target one
specific person. You have to narrow that
down because if you're trying to talk to
the entire world, the majority of the
world is not going to be interested at
all and they're not going to feel that
exact pain point. So, it's not going to
work. And then the promise is basically,
okay, you have this person and this
person experiences this pain. How does
my tool or my service or product, how
does my offer actually answer that
painoint, actually solve that painoint?
And once you get clear on those three
things, you actually have an offer that
you can go sell because you can
communicate it clearly. A lot of this
stuff is like you probably have a
painoint in your life that there is h
there are probably hundreds of tools out
there that solve it, but maybe you just
don't know of them because you're not
aware of them because no one's
communicated that to you clearly enough.
Right? So in our specific example with
client pack, the person was an agency
owner who was dealing with clients. The
pain is all of these sales calls coming
in, proposals being due, not having some
sort of consistent framework to generate
them, and not being able to communicate
the value and justify the ROI. And the
promise is just, hey, you're going to be
able to upload your transcripts. So, all
you have to do is you sit there in the
meeting, you talk to them, you do the
discovery, you find out the value of the
systems, you you you do what you're
supposed to do, right? You're the
consultant, and then you will get a
client ready deck in under an hour.
And I wanted to tell you guys real quick
about like why did I decide to join
Glido? Why did I decide to co-ound Glido
with the the team, with Giannis Moore,
with Jack Roberts, and with Dave Eelar
and Yors Eelar, who isn't on here. He
likes to sort of be a mysterious mystery
man in the back, but these guys are
grinders. So, part of it was, yeah, I
mean, good friends in the space. They're
all doing incredible things, and I
wanted the opportunity to work with
them. But more realistically,
the answer is that I felt this pain and
I knew that my audience also felt this
pain because I was using Whisper Flow.
There were certain things that I didn't
love about Whisper Flow. Sometimes it
felt slow, sometimes it had weird um
formatting. And every single YouTube
video that I made, people were asking,
"What's that tool? What's that tool? How
are you talking? How are you dictating?"
And I knew that there was clearly a pain
for me. And my audience as well was also
feeling a pain. And there was some sort
of need. there was some sort of, you
know, promise here of, oh, you can be
more productive because you can talk
into any app. And so that's why I was
like, hm, you know, maybe it would be
more cool for me rather than just having
an affiliate link to Whisper Flow to
actually be able to be part of
something, not even from like a, hey,
we're looking for a massive exit or,
hey, more money, just because I thought
it'd be really cool to actually be part
of something where I could share with
the community, hear feedback, share it
with the GL team, and and actually have
us iterate on something and and work
towards a vision together. And I thought
that that's been just super super cool.
But that's taught me a lot about how
different it is to be kind of like a
service-based business model compared to
a a product um a SAS product. One thing
that I want you guys to think about here
is as you're thinking about your person,
lots of other offers or products
probably have that same person, probably
have that same avatar. So one thing that
you can do is you can think about what
are the other tools out there, right?
What are my main competitors? And then
think about, you know, what are they
priced at? Where's the value? Go
download the tool, use it for a little
bit, see what you like, see what you
don't like. Go to Reddit, go to X, find
out what are people complaining about
about this tool. So basically, the worst
things about your competitor, you make
sure that you have better because in
order for people to also switch away
from a tool that they have because there
is like a switching cost associated with
switching tools, switching whatever,
they have to clearly see that jumping to
a different product is going to save
them something. Whether that be, oh,
it's 50% cheaper, or oh, they have this
one feature that my current provider
doesn't have. There has to be a clear
reason to switch. It's even harder, I
think, to switch to a new tool compared
to signing up for something if you don't
have a solution for it already.
Switching is tough. So, think about the
person. Think about the competitors.
Once you're ready to start getting this
in front of people, we talked about how
important it was to sell before you
build, right? That's why I showed you
guys building the landing page. That's
why I showed you guys building like that
waiting list. validate the idea before
you put a ton of time and effort into
it. If [snorts] you send that off to
hundreds of people and nobody is
interested enough to even just put their
email in a waiting list or even ask a
follow-up question, then that's probably
a signal that either your person is
completely wrong. That's one one
problem. Or if your person is dialed in
and you're shooting this offer off to
them and no one's signing up, that the
offer is not valuable enough. You know,
there's not you didn't highlight the
pain enough or you didn't highlight the
promise enough. And really a lot of what
I want to talk about today is just the
idea that you need data. And when you're
starting off, you have basically no
data. But data is what helps you
actually make decisions. So what you
need to do is you have to find the
people that are already looking. Um, for
example, let's take my client pack,
right? I know people are looking for
this because they're talking about it in
my community, in my YouTube comments,
probably on Reddit as well. I could go
to those communities and I could post,
hey, I'm building this. If you guys are
interested, sign up and see like, you
know, when I release this, if you want
to test it out, be beta users, I'd love
the feedback. And if I'm getting lots of
good support, then I know, okay, cool.
I'm going to definitely keep building
this for the next couple weeks, and
hopefully bring them something soon.
Then you want to move into like the
actual help, doing the results by hand.
When you're starting the business and
you're starting to try to get the
momentum going, you have to do a lot of
things that might not scale. You have to
get your hands dirty. You have to do
things that might be manual and you have
to just put in more time. That's just
what it takes to get something off the
ground. Um, I actually wanted to point
off to this other podcast real quick.
Starter story. Um, he did this episode
with with this guy who had gotten, I
think, two different SAS products to
like 3 million ARR in a couple years.
And he was talking about how he's how he
gets his first 100 users. Basically, the
playbook. And one of the things he
talked about here, um, let me find the
exact quote. He said like, "Do things
that don't scale." Right here. Do things
that don't scale. And I thought that was
really smart because he was in Reddit
threads. Him personally as the founder
was answering people's questions and he
was giving them free demos and this was
creating this cool loop of okay, I have
people in this Reddit community that are
interested in this and I'm publicly
sharing what my tool does and they're
getting to click the demo. They're
getting to see it and it's public,
right? Um, so I think that this is a
really good video to watch. Just type in
starter story, type in this title. Um,
it's like 14 minutes. There's a lot of
golden nuggets in there. So, definitely
check out that video. But it just goes
to show that point of like you have to
be strategic about where you're showing
up and finding where the people who are
looking for your product actually live.
Communities, YouTube channels, um
content creators, all of this type of
stuff. You have to be very clear on
these things in order to be clear on
these next things. And then you're
basically just going to need to use that
proof. So when you have maybe a couple
people that have used your product and
they have a testimonial or they have a
case study or they have like a result
that they got from your tool, that's one
of the things that no one else can
replicate. You have to think about what
can no one repeat from my what can no
one steal. They can steal the tech. They
can steal maybe even the prompts if they
play with it enough. There's a lot that
can be stolen or duplicated because of
AI. Now especially I saw a quote from
Sam Alman. He was doing an interview
with um Gary Tan and he was talking
about how when he started in the sort of
startup space, things that took him and
his team 3 months to build out, he's
able to do now in like I think he said
seven minutes. Maybe a bit of a
hyperbole, but he basically said, you
know, you're going to be able to do that
in a day and it used to take teams
months. So things can be replicated
easily. You have to think about what is
the moat. And that's why in this
specific video, this client pack thing,
I don't think this is something I would
go sell for 39 bucks a month, at least
not where it is now. I would probably
just sell it for free, um, five decks,
and then I would maybe try to scale that
up on some sort of subscription, but I
think that this alone is not valuable
enough. If this was like an open source
repo, I think people would love it, but
I don't think people would want to pay
for that because they would try to just
reverse engineer and steal it. I think
the only thing in my current client pack
that was truly a moat was my prompting
in it. And I if I would have put more
time into it, the prompting would have
been better. But that was really the
only IP I had. And it's not super super
defensible. But proof is defensible.
Proof is something that no one else can
replicate because it's your client and
it's your tool. So that's something else
you should really be thinking about once
you've collected proof and case studies.
How do you put that back into the
flywheel? How do you reinvest that?
Almost like the way that once you
achieve, you know, you're starting to
get going on scale, you're taking that
revenue and you're putting that money
back into the business rather than going
and buying watches or whatever. You're
taking the money, you're putting it back
into the business for ads. That's what
you want to do with the proof
testimonials, too. You're going to take
those, put it back into the business,
put it in the copy, put it in your uh
newsletter, put it on your website. You
have to reinvest that data. And then you
just have to kind of repeat that cycle.
Now, what I want you to think about is
how you can turn that playbook into one
week of action. What can that actually
look like? Find 30 people based on your
type of buyer, right? And you can start
doing some cold outreach here because
these are going to be super personal.
They're not going to be automated.
They're going to be you collecting data.
It's just about you having conversations
with people. What do you think of this
tool? Does it sound valuable? Blah blah
blah. How much would you pay for it? All
of these sorts of questions. I'm not
sure if you guys did this when you were
in college or whenever, but um I
remember I would go do like these
studies where people, you know, like
these big labs or whatever. They'd pay
you to just come in for an hour, try
their cereal, you know, uh try these
little experiments and they'd pay you
good money just to sit there and do
something. And I used to think like what
a steal. like I'm just doing but but the
reason is they're getting primary data
there. They're collecting data that no
one else has because they're actually
conducting experiments and they're
willing to pay for it because out of all
that data you can actually make a
databacked decision. Now I think there's
a lot of value in trusting your gut and
using your intuition for decisions. But
I think ultimately the best way to make
decisions is to rely on the data. And
when you're starting off you're going to
have to sort of like try things. You're
going to have to throw things at the
wall, see what sticks because you just
don't have the data. But as your
business expands, as your business
grows, you get more and more data. And
it would surely be a shame if you're not
using that data and leveraging it to
make decisions because that's another
thing that is a huge moat, the data.
Think about um Anthropic and and OpenAI.
They have so much data and that's truly
one of the things that's keeping them
going is because that data can be used
to train their models to make better
models. At the end of the day, it's
going to get to a point where I believe
most models are going to get pretty even
because Enthropic and Open AI and these
other companies have so much data.
They're going to be able to leverage
that in different ways. And that data is
insanely valuable. So use your data,
please. And then once you started to get
people to try it out and you've been
getting some results, ask them to show
you those results, right? Like you have
to actually be able to
see it and use it. Now, when it comes to
pricing, pricing is an interesting
question in all of the world, right?
When it comes to service based or when
it comes to a product. And I think this
is also a matter of calibrating. like
you're going to probably try some
pricing and it's not going to work.
You're going to bump it around and
that's just natural. But what I want you
to think about as well is how does the
user get a real result? When in the
cycle of someone trying your product or
using your product, do they have that
aha moment where it's like, damn, like
this thing is actually good. I could
picture myself using this. Because let's
say it would take them three to five
generations, right? So maybe it's like
an image model and you typically see
that people don't have that aha moment
till like their fifth image generation.
Then maybe you want to make that fifth
image generation, make it all free up
until then so that they actually realize
the value enough to be able to go start
paying for it, right? Especially, think
about this guys, a subscription is so
much harder to to sell. It's so much
harder to sell a subscription than a
one-time product. Let's say you're
selling a product for 50 bucks or you're
selling the exact same product for 10
bucks a month. It's probably going to be
harder to sell that for 10 bucks a
month. like just much harder just
because a subscription on a cold person
who's never done business with you
before. It's so hard to sell. That's why
these things like these sort of like
trip wires and funnels exist where you
first get someone to buy from you in the
beginning. So maybe you even have them
buy a $2 um PDF from you and then you
can try to sell them a subscription
later. Like subscriptions are just
harder to sell to a cold audience.
That's just the truth. So think about
some of these things. Maybe your product
isn't quite ready yet. Do you really
want to put a bunch of people through it
and have them pay for it and then
they're just going to be like, "Oh, this
isn't good. I'm never coming back.
Unsubscribe. Cancel. Brand is ruined."
That's where you put them in like a
beta. Maybe they get value in one
sitting. In 5 minutes, they can get
value. So like in our example with the
client pack, maybe we found that after
one generation, they have that aha
moment. Wow, I put in all my transcripts
and in 5 minutes I got this deck which
I'm ready to go present to my client.
Value in one sitting. Then okay, cool.
We give them one free deck. Anything
they want more than that, they have to
pay. And also, if they want the
watermark removed, they have to pay. And
I'm not saying that's right always, but
figure out where the value sits. If you
need to use it over and over for days,
then maybe give them a free trial,
right? So, for something like Glido, if
they've never done voicetoext, where do
they actually see the the real moment of
like, "Wow, this stuff really makes me
more productive." Is it in the first
transcription? Probably not. Is it maybe
in the first day of usage or the first
100,000 words? Where does that sit? and
how do we let them use it for free until
they sort of hit that aha moment and it
becomes sort of more like a sticky
thing. I almost think about the way that
OpenAI and Enthropic are right now
charging a subscription for Codeex Cloud
Code. Right now it's very cheap, right?
Um if you're on the 200 bucks a month
plan for for either of them, you're
getting about $8,000 to $14,000 of
inference. They're basically getting us
hooked to this for cheaper because then
once they raise the prices, if they
raise the prices, a lot of us are
probably still going to pay for it
because we've seen the value. We felt
the value. Whereas, if they would have
come out the gate with like, "Hey, by
the way, this is a $2,000 a month
subscription, there's probably a lot of
us that would never have even tried it
out and never have even realized the
value." So, think about that. Okay. Now,
let them see the result. Charge for the
next job. So in my example, right, real
transcript, they get the complete deck
with watermark and that's completely
free and then if they want more, that's
when they actually get on the paid plan.
Now your decisions improve as you learn
from the customers. It would surely be a
shame, like I said, if you didn't
leverage the data. So let's say you get
your first 10 customers and your mind is
just, okay, wow, scale, scale, scale,
more, more, more, and you throw 10 more
customers in, then 50 more customers in,
then 50 more customers in. Those
customers might have all a bad
experience, churn out, and never come
back. But maybe you get 10 and then you
hold it off, right? And then you see
what those 10 customers do. You see when
they leave, why did they leave? Reach
out to them. Have an automatic survey.
Was it for a competitor? Was it because
of the price? Was it because it didn't
give you what you needed. You guys have
all probably canceled a subscription.
And it's asked you why. And you send a
little feedback. That data is obviously
very important. You need to know the
reason why people are leaving. And it's
really interesting because maybe
sometimes
um people are leaving for a specific
reason that doesn't actually make sense
to you and it's like maybe that person
wasn't the right avatar in the first
place. So let's just take a quick
example, right? So for client pack,
let's say some people are leaving
because they say that um
the the deck isn't sort of like
generating the type of results they're
looking for. But then you actually dig
in and you find out that they don't even
run an AI agency. Maybe they run like
more of a they they run an ad agency. So
clearly this isn't going to work for
them. So you have to be thinking a
little bit about collecting the data,
analyzing it, and when you get more and
more, right, you it's a little harder to
filter through. But it's it's just a
question of like subjective data like
feedback and surveys should sometimes be
taken with a grain of salt and you have
to really look at the average and figure
out what's the story telling you rather
than just like trusting the data
blindly. I think that's where you get
into like objective data versus
qualitative objective maybe being more
something a little along the lines of
like okay how many days to to activation
meaning when they sign up when do they
get the first um deck generated like
when do they basically take the first
action because there's a huge drop off
to people that sign up and if they don't
activate right away or if they never
activate they're going to turn out
obviously so it's all part of that
experience so watch what they do get
feedback and collect what they're doing
get you know and put it right back into
the product if five out of [snorts] 10
people have complained that it's too
slow, see what you can do to speed it
up. Those types of things, and then
you're going to keep rolling out to more
customers. Just be careful. You don't
want to scale too fast. Obviously,
that's like a good problem to have if
you have so much demand where you have
to block it off and have a wait list.
It's a great problem to have, but you
don't want to just start blasting it to
12 different communities right away. You
want to be careful about it. So, people
will sign up, they will get their first
result, hopefully they'll want to use it
again, and that's when they'll pay for
it, and they have to keep being able to
use it. If they only get value for 30
days, then what's really the point?
they're going to turn out. You want to
see what you can do to increase the
lifetime value. Basically, when someone
becomes a customer, how much money do we
make out from them in total on average
lifetime? Now, if they stop or cancel,
you ask why. You group the reasons and
then you fix one problem at a time based
on what the data is telling you. Now,
how do you think about the pricing
without guessing? So, in our example, we
priced this at 39 bucks a month. And
this was kind of a guess. This was what
the agent told us based on the data. But
if I was really going to market with
this tool, I don't think I would do it
like this. I would probably launch this
for free, right? Like I think I would
probably have everyone just do it for
maybe five bucks or sorry, not five
bucks, maybe everyone gets five free
deck generations and I would get people
to, you know, use that, right? And then
I would talk to them about, you know,
how many decks on average do you
actually need to generate per week and
how much would you pay per month for
something like this? And I would ask
them questions like this and find out
where the value really lies and what the
result is worth. And it's not uncommon
to have like three plans, right? You
have like a free plan, a starter plan,
and a growth plan or something like
that. See which ones people are buying
and see which ones people are actually
what features they're actually using and
how you can play around with that model,
the premium model, right? And I think
that a lot of times when tools are
getting off the ground, they play with
their pricing a lot. We've seen bunch of
tools even now that have been up and
running for 10 plus years are constantly
changing their pricing. So, it's always
kind of adjusting to inflation, to the
market, to competitors, to the data.
There's a lot of things that are going
to go into the way that you actually go
ahead and price this. But when it comes
to pricing, you still have to ultimately
at the end of the day, you have to be
profitable. So, let's say someone pays
me 39 bucks for month one. That doesn't
mean I get 39 bucks for the business,
right? We have payment fees, we have the
API costs, we have other things, we
maybe we even have some staff that we
have to take care of, we have hosting
costs. So figure out what does it
actually cost for you to not only
deliver for one client but also to
acquire that client because if you're
spending money on ads, if you're
spending money paying creators to make
videos about your tool, that's something
that goes into your whole budget. And
you have to obviously be profitable to
achieve scale. And that's why I would
not recommend doing something like
running ads to your offer that you don't
yet know if the ads are going to work
because in order to run ads, you have to
be able to spend a decent amount of
money. If you're only spending like 500
bucks a month, thousand bucks a month,
Google or Meta or wherever you're
running the ads probably doesn't even
have enough to give you a broad enough
audience to see who is resonating and
which of your copy and creative is
working. And so if you're just kind of
throwing 500 to a,000 bucks down the
drain every month, that's a complete
waste of that money. Whereas I would
prefer, if I were you, I would take that
money and I would go pay smaller
creators that have a really warmed up
community and audience to show off the
tool. 250 bucks here, 500 bucks here. I
think that will be a much better use of
your investment. And then you can see as
you're making your own organic content,
which is something I 100% think you guys
should do for a tool. You're making your
own organic content. You're paying
creators to make content. You're seeing
which of these pieces of content are
outliers, and then just take that, put
that behind an actual ad, and run it,
right? Like, you're basically double
dipping there. You're creating your own
organic flywheel of content. You're
paying creators, and then whatever works
best, just put money behind it and push
it more. And I think that's really the
way to do it. I think that cold email
and cold ads are great to achieve true
scale once you've had an offer that is
proven and once you have the budget.
Otherwise, I think it's a waste of
money. I think it's the numbers game.
You know, volume negates luck. And
that's not where I would start. I would
start with my own organic content. I
would start with doing things that don't
scale. Posting in Reddit communities,
writing blogs, making my own organic
content, doing things that are a bit
more hands-on as the founder and a
little bit more sort of like grunt work
because you have to be in there and you
have to be getting as much data as you
can at the beginning. And like I said,
you're able to then reuse the results
into all of those things. Writing blogs,
um, comparing yourself to other tools.
Let's say for example, Glido, we have
competitors in Super Whisper, Whisper
Flow, Aqua Voice. We could make blogs
and we could publish articles and pieces
of content about, you know, the top five
alternatives to whisper flow and we
obviously include glido in there. We
could do glido versus aqua voice
comparisons and we can, you know, have
stuff in there. And this is going to be
ranking in search. This might even
appear in AI search results. And the
more you can get out there, the more you
can just show up where your audience is
looking and the more you can show up as
a brand on different social medias and
on the internet, the better because
you're going to start to be picked up a
little bit more. communities, obviously
putting in the results, putting in case
studies, referrals, obviously maybe you
have some sort of affiliate program once
you really want to get the flywheel
going. You can give people bonuses, you
can have them invite friends, and then
of course personal messages, just
actually reaching out to people in
certain communities, reaching out to
business owners, reaching out to your
network, that sort of stuff as well. So,
like I said, I think right now it's a
new world where creators and communities
is probably one of the biggest levers
you can pull. Super small creators are
getting brand deals all the time. large
creators are getting brand deals all the
time. Everyone who's out there building
in public and building an audience,
they're getting brand deals. So, take
advantage of that, right? I think um if
you remember, I made a video a while
back on an app called Cali. This guy
basically vibe coded this this fitness
AI app for like um nutrition tracking
calories and whatnot and he built it
obviously with Claude and then he
basically his whole scaling strategy to
start was just paying creators. He was
finding fitness creators. So, they
weren't even in the AI niche, right? but
he knew who his audience was and he knew
creators that had that audience and then
he paid them to show off his tool and
that worked really really well for him.
You find creators that have the right
community. You give them a free account
and you show them what the tool does.
You basically are able to then pay them
to make the content and you can have
like a performance bonus. You can have a
fixed rate and then you can give them
even like an affiliate code so that when
they also have people sign up, they're
more incentivized for that because
they're getting paid on the back end of
that as well. and they have the
guarantee of like, okay, this piece of
content, I'm still going to get 500
bucks no matter what. Like I said,
that's such a better use of your funds
than going straight away to putting 500
bucks behind a meta ad or something like
that. Trust me, working with creators is
going to be a huge unlock. And it's also
interesting because what we've seen is
like smaller creators actually have
sometimes better conversion numbers and
people and brands prefer to work with
smaller ones because the audience feels
like the creator is more human. The
community feels smaller. or the person
feels more sort of like attainable or
like reachable. I don't know exactly the
word I'm looking for, but small
audiences are very strong. There's a lot
of brand authority there. So, don't sort
of like overlook a creator because maybe
they only have like 5,000 Instagram
followers or something. Those 5,000
Instagram followers are probably super
bought in and super warmed up to that
specific creator. And then what you want
to be doing, of course, is basically
tracking everything you're doing. If you
pay these creators this much money and
they put out these pieces of content,
track them. What was the hook in that
content? what was um your budget for
them when you're putting out content,
tracking all of that. When you are
reaching out to people, tracking all of
that, the more stuff that you have
tracked, even if it's just like a super
super bogus Google sheet, that data,
trust me, you're going to want to look
back on that and you're going to want to
go to analyze that for your next
iterations when you have a next month's
budget that you have to spend on
creators and organic content and other
things like that, too. So, you're not
ready to run ads until you can answer
yes. Do you have the right person? Do
you have a clear promise? Do you know
exactly when they get their first real
outcome? When they receive the first
real value, when will they actually come
back? And can you track to know exactly
where they're coming from? And when you
have all these answers and when you've
sort of proven that offer, you can start
to run ads behind it. Of course, you
also need the budget as well. Now, I I
think I've alluded to this earlier, but
here's something that we've actually
specifically felt with Glido that I
think is really important to think
about. How often have you bought a tool
and then unsubscribed and then
resubscribed? Not very often. Like you
kind of have your first impression of
that tool and then you don't really
think about revisiting it. But what's
happening to that tool is they're
constantly iterating, right? They're
updating based on churn reasons. They're
updating based on feedback. They have a
huge road map of what's to come. And so
if you invite too many people at the
beginning and you get a ton of feedback
and tons of people saying, "Hey, I don't
like this tool for this reason." And
then they leave. Well, what if you go
fix that? And and if that functionality
would have been fixed in the first place
or would have been there in the first
place, they probably would have never
churned. And so now you just lost a
bunch of people who were kind of like
your perfect avatar and have proven that
they are willing to buy and now it's
hard to get them back. You know, you
can't just you can try to obviously
blast them and say, "Hey, here's what
you missed in this tool this week. We
updated this and this. You want to come
try it again?" But it's just so much
harder. So think about obviously, like I
said, for many reasons, not scaling too
fast. So, your simple 30-day plan, week
one, is just go have conversations, find
out what's going on, list 30 buyers,
have conversations, join communities,
see what people are talking about, do as
much of that gathering as you can and
asking people questions. Week two, pick
some people, get them on a free plan,
show them how the tool works, understand
what they like about the onboarding
flow, understand where they had an aha
moment, if they ever did. Just be very
hands-on with them. give them as much
value as you can and hopefully they're
going to give you back golden data,
golden feedback and then you're going to
learn. You're going to see what you're
hearing from them. You're going to see
what else needs to be fixed and you're
going to keep doing that. You're going
to keep fixing and then you're going to
repeat. You're going to keep doing this
very manual process until you get to a
point where you feel like you're ready
to sort of start like opening the doors
a little bit more. And then I think you
sort of unleash the content creator
strategy. You start pumping out organic
content. you start doing all of these
things, writing up the blogs, writing up
these SEO articles, doing these things
that help you just have a better
presence so that as your product is
getting better and better, you now have
um a good system in place and you can
stop doing some of those things that are
very hands-on for you that are very hard
to scale. And now you can start to more
focus on collecting feedback from the
users and driving the vision, figuring
out where do you want to go, but also
more importantly, think about where do
you not want to go? What bucket of tools
do you not want to be associated with?
And what bucket of tools do you want to
be associated with? And how do you
constantly see what the competitors are
doing, analyzing their feedback as well,
and making your tool do one thing really
well. I think that's a really important
thing to learn is that tools that are
more defensible and that are clearer and
have a better offer, they do one thing
better than everyone else. They don't
have to do five things. And I think a
lot of us think, oh, you know, I have
this hub. I have this AI tool. I can
build as much as I want. I'm going to
make this as useful as possible. All
that does is it creates overwhelm.
Especially when you're trying to get off
the ground, especially when you're
trying to scale, you need one super
super clear pain. One super clear pain.
I'm just going to go back to the slide
because it just helps paint the picture.
One super clear pain and one super clear
promise for one super specific type of
person. And if you try to add, oh, but
there's three pain points and I have two
different promises and I could picture
like five different types of people
using this. That's cool. That's okay.
And maybe one day you can scale there
when you have a huge you have 10,000
paying users and you can offer like a
team plan or you can offer like a scale
plan and you can have different upsells
and downsells throughout. But when
you're starting just start with one of
each and go as clear as possible. Just
do one thing better than anyone else and
you will see a lot of success when you
do that. All right. So I hope that this
was helpful. I'm going to put this deck
inside of my free school community just
like everything else that I do. As you
guys know, if you join the free school
community, which is in the link in the
description, you'll go to the classroom
and then you'll click on all YouTube
resources and you'll find everything in
there. So, if you want that deck, if you
want all the other skills and everything
else I've mentioned in this video or
other videos, just head to the free
school community. But that is going to
do it for this video. So, I really hope
that you guys enjoyed and I hope that
you learned something new. And if you
did, please give it a like. It helps me
out a ton. And as always, I appreciate
you guys making it to the end of the
video and I will see you all in the next
one. Thanks everyone.
