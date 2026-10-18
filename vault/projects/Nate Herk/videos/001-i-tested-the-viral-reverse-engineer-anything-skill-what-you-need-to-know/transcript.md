---
type: project
last_accessed: 2026-10-14
relevance: 0.98
tier: active
---
So this GitHub repo right here, reverse
engineer anything, has been absolutely
blowing up. Matthew Bourbon himself said
software is done. Now he's kind of
joking a little bit. This narrative has
been around for, you know, over a year
since vibe coding has really taken off.
But there is some truth to it because
the idea of reverse engineer Anything is
that you see a feature you like on some
sort of app or software that already
exists and then you can have your agents
using the frameworks inside of here,
understand how that functionality works
and then actually just go ahead and
recreate it. So today I wanted to
quickly talk about how this actually
works and why I don't think this is
anything really that new and because of
that how you can use this and also the
right mindset to be able to actually
build things way better. So I've been
playing around with this REA repo and
I've built games, I've built software,
I've built different tools and apps and
just tested out a bunch of things and it
is very impressive. But as I was going
through and testing it out and using it,
I realized that it's not anything new
and we have probably been doing this for
a long time. I definitely have been
doing this for a long time. The way that
I think about it is that AI is not
really that creative. It can't really
think outside the box. But if you give
it a very clear vision, it can execute
on that for you really well. And if we
take a look at some examples that I've
actually built a while before this
GitHub repo existed, you'll see what I
mean. On the left, we have my human
edited Instagram reels. I'm going to
mute this real quick so I can actually
play it. But you can see the vibe,
right? You've got B-roll, you've got
different font colors, you've got
shimmers, you've got different types of
animations. And what I did in order to
make a skill that now edits my Instagram
reels, is I had it go watch like 30 of
my best performing Instagram reels. And
now we get the style on the right, which
looks pretty much identical. The same
sorts of different colors and fonts and
vibe and animations and all of this kind
of stuff. And now this just lives inside
of a skill. And the point is what I had
to do here was I couldn't say, "Hey, I
want you to build me an Instagram
editing, you know, skill that has this
sort of vibe and does these sort of
transitions." No, what I did is I said,
"Hey, look at these videos. analyze all
of these frame by frame and understand
what's going on under the hood. And
that's essentially me decompiling my
human edited real style. Here's another
example with a motion edit. On the left
was one from Jordan Watkins, and you can
see that it's really, really well done.
And he said, "I'd love to see AI try and
recreate this." So, I was like, "Huh,
let's see what it can do." So, I
downloaded the video, gave it to Opus,
and said, "Hey, analyze this frame by
frame, understand what's going on and
how it works and why it works like this,
and then build me a skill around it and
show me that you can edit a video
similar to it." The one on the left is
still better with motion design and
sound design. It still is a little bit
better, but the thing is Opus could not
have thought of this. This is such a
creative design that I don't think
Claude or any AI could have created it,
but because I'm showing it, this is what
I want. Analyze it now build it for me.
It was able to do a much better job. And
when I've talked to you guys about how
to build the best skills, this is
exactly what I preach. I preach reverse
engineering the output. If you want to
build a Friday report, have it look at
five examples of good Friday reports
because now it knows exactly what you
want. I've talked a lot about how
communicating your intent has to be
specific. If you give an agent a generic
goal, it's going to give you a generic
result. So, this whole idea of reverse
engineering anything and having it
specifically look at an app that you
want to recreate and then copying the
features from it, that is way more
specific. Essentially, what you've done
is you've given the agent a very, very
specific PRD, but instead of you having
to type out the exact PRD with all the
specs, you're just saying, "Look at the
app. That's your PRD." I've done this
with landing pages, you know, taken
elements or animations or designs from
other landing pages. Here was an example
of one that I did with Glido. I've done
this with apps, right? Like you can see
right here, I've got this thing um right
here, which is basically the Loom clone
that I made from using this repo, right?
Like I had it look at Loom. I had it
understand how it can work with like the
different bubbles. You can see it does
the recording countdown. It might not
work because my face cam is recording
right right somewhere else. So, I'll
play a clip real quick. All right. All
right. So, I just wanted to test out how
this actually works to make sure that
this is like a decent software. So, I'm
going to see if I can pause this. And
now we can go ahead and keep on rolling.
I can move this thing around. I can also
make it smaller or larger while I'm
recording. That's very nice. And let's
go ahead and stop and see what happens.
But the thing that's important to
realize is that we didn't clone Loom.
This is a very different looking app. We
didn't clone like all of the exact UI
and the design elements. We cloned the
functionality. We understood how does
the little bubble work? How can you move
it around? How can you change the window
that you're recording, right? Like we
talked about this sort of stuff and we
had it analyze that sort of stuff. Loom
obviously records and stores your things
in the cloud in Loom's cloud, but this
one is just local. So, it's storing
these files in my own folder inside of
this app called Herk Recorder. I also
pointed this at Sand Castles and had it
inspect the functionality and understand
and research how it works and what it
does. And then it gave me basically my
own version of Sand Castles and I just
had to connect my API key. So it helps
me analyze Instagram content and analyze
my own content. And you can also see
this is true with something like our AIS
eval studio which lets us actually eval
our automations. We took a lot of
inspiration here from Langfuse and we
understood how they work, how they show
things, how they run the things. And now
we have our own version right here. And
it's not a carbon copy of course, but we
had it look at and grab some of the best
core features and how they work and why.
Real quick guys, I've got this
completely free website design skill
that I'm giving away. I use this for
every single website that I build,
including our AI automation society
site, which I think is pretty slick. And
I absolutely love this website. It's
called ScrollCraft, and it understands
things like scroll driven animations and
layering, but also it has things in
there like taste, typography, spacing,
depth. It's just a really good website
design skill in general, and it's
completely free. So, the link for this
will be down in the description. But
let's get back to the video. So, I guess
the point I'm trying to make there is
reverse engineering has been around for
a long, long time. But the reason why
this repo is blowing up is because this
repo gives your agents a very practical
and thought through framework for
decompiling and iterating in order to
actually create what you want to create.
And if you haven't been using your
agents in that way where you show them
the end goal and then help them sort of
work backwards to get there to build the
skills to give you a better output, then
you definitely should start thinking
about this not just when you're trying
to build apps or software, but when
you're just driving your day-to-day and
you're building skills. So, let me just
break down real quick, real simply what
actually this is and how it works. So,
reaver reverse engineer anything. It
helps your AI agent study something and
then help you build it. So, let's take a
look at like a recipe, a bakery example.
So, let's say the bakery has a cake that
you love. You order it every week and
you love it and you wanted to reverse
engineer the cake to get the recipe
because the recipe is locked away. It's
the the bakery's IP and they don't give
it away. So you buy a cake, the bakery
ships the end result to you and they use
the recipe to make that obviously. Now
you inside of your kitchen, you can
actually, you know, tear open the cake,
you can taste it, you can try to look at
it under microscope and you're
essentially trying to reverse engineer
the recipe from that cake. And this is
the process of decompiling, which means
you're actually tasting it. You're
inspecting it. You're trying to break it
down to figure out what are, you know,
the different code blocks and what is
the actual letters in here that make the
cake. And there's where you get sort of
like your own sort of trial and error
where you're building and you're
comparing and you're trying to iterate
on it until you hit the end result. So
what happens is if we take that example
of Loom, you can ask your agent, hey,
use reverse engineer anything and go
figure out how Loom's camera bubble work
so we can work that into our own, you
know, screen recording app. Your agent
would then inspect the files and inspect
the functionality of the app. It would
look through the evidence. It would
build its own version and then you
iterate until it basically matches up in
terms of functionality. And like I said,
it comes out so well because you're
pointing it at an end result. You're not
saying, "Hey, make me a cake." You're
saying, "Make me this very specific
example of cake that tastes like this
with this much density and it has, you
know, this type of frosting and this
many layers." It's just way more
specific of a request. So, this whole
doc that kind of walks through and
explains some of this, I will link in my
free school community for completely
free if you guys want to grab it, as
well as this doc, which just kind of
goes through like how to get the most
out of it. Because what I found after
building a bunch of stuff is it's so
hard to just say, hey, go reverse
engineer Loom. It's easier to pick out
features. So you use Loom for a little
bit and maybe it's like, okay, I want to
build this myself. What are the best
features of Loom that I like? Or, you
know, I want to rebuild my CRM. What are
the features of, you know, Salesforce or
whatever I use that I really, really
like? Okay, now we use our agent to go
pick out those specific features,
investigate them, decompile them, and
then bring them over to our own app. And
then what I did kind of for fun is I had
cloud code with the reverse engineer
anything framework reverse engineer the
reverse engineer anything repo to
basically help me figure out how it
works better so that I can use it better
and point my agents at it better and
instruct them better with it. So here is
what we have five main steps that I want
you guys to think about when you're
using this repo. Pick a feature route by
build summary first scene inferred
unknown and then rebuild and test. So we
already talked about this one a little
bit, right? not just pointing at the
whole app, but pointing at specific
behavior and functionality. Now, from
there, thinking about routing by build,
which means what the app is built with,
kind of picking the tools for that. So,
once you understand what sort of app or
software you're looking at and how it
actually exists, then you might be able
to change the way or alter the way that
the agent thinks about analyzing it to
use the right tools. And this isn't
something that I know off the top of my
head. I would just make sure I'm giving
the agent that context of you should be
thinking about this sort of stuff when
it comes to like the tech stack. Now
number three is about summary first. So
what happens is REA will basically
analyze the whole app and give you a bit
of a summary but the whole analysis for
Loom for example was over a gigabyte. So
basically the full analysis is turned
into a shorter summary for Claude to
actually fully read through. And it's
things like what it works, how this
thing does what it does and what it
couldn't yet figure out. And then what
happens is it kind of breaks that down
more granularly down to the modules and
to the traces. But you don't want to
have to rerun that entire summary, which
is something that you could easily get
caught in the loop of if you're not
being careful about how you instruct it
because this is already saved locally
within this project or somewhere in your
files. Now, this fourth one's really
important, which is once it starts to
dig through and understand what's going
on, Claude should be tagging these as
seen, inferred, or unknown. And these
are basically three different
categories. Meaning seen are things that
Claude actually found and were cited. So
for Loom 11 custom native add-ons, it
found it and it understands how they
work. Inferred is things that oh the
data and the code kind of points to this
being the way that it works, but this is
kind of more of a guess. We don't
actually know for a fact. And the reason
why this one's so important is because
if you accept some of these guesses and
assumptions that Claude might be
bringing back and then you build on top
of them as if they're fact, you can get
into some pretty messy situations. And
then of course we have things that are
completely unknown. Rea couldn't see it
inside of the native recorder or inside
of the the app that you're actually
using or looking at. And so it's these
types of things that you're able to do
with this reverse engineering anything
framework and repo that if you just
natively said, "Hey Claude, go look at
this app, research it, investigate it,
and then build it." That's where there's
a big difference on like how
professional and and I guess structured
this process feels when you use this
repo. And then of course, this is the
most important part of any build process
is the rebuilding and the testing. So
now you're taking all these findings
that you had grabbed and then you're
building on top of them. And you're not
just building, but you're also going
through and you're iterating and you're
actually testing these things out.
You're having it run these test cases.
You're having it actually process
things. So it's not just built, but it's
actually ran and tested and then
iterated on rather than just, you know,
shipping something once because it seems
like it's done. And the last things I
want to talk about here is that you
should never be copying exact code or
assets. There are definitely some legal
limits here when you are deeply
inspecting what's going on, but for the
most part, you also have to remember
that you're only looking at or cloud
code or whatever AI you're using is only
looking at things that actually exist
already and that you can grab. Meaning,
you know, you're not going to be telling
this thing to hack into like Loom's
server or to some app and software's
like private IP codebase. You probably
couldn't even get in there, but you
know, you're not going to tell your AI
to go hack into it. you're having it
analyze what it can already see in your
local files or if you have an API,
whatever it may be. It's just inspecting
how it already works and what already
lives there. And this whole process of
decompiling is something that people are
already doing because it's literally
there. It's public. It's it's in your
your hands. But humans obviously go
through it a lot slower than what an
agent would do. And also most of the
humans out there, I definitely couldn't
read through code and read through all
these traces and decompile it and then
build my own app based on that. The next
thing is that some apps require
different types of setup. you know,
based on, you know, we talked a little
bit earlier on where they actually live
and thinking about the tech stack and
thinking about how you need to set that
up. And then, of course, at the end of
the day, the results that you're going
to get from this thing are based on the
AI model that's actually writing the
code and inspecting the code. So, you
can't just assume that, oh, because you
gave, you know, your AI model this repo,
it's just going to build everything
magically. But what I do think is cool
about that is let's say you know you
have this software that you were
building with Opus 5.5 and maybe you
want to try with Sonnet 5.5 and it
wasn't possible earlier but now if
Sonnet 5.5 has all of this data that has
been done based on this investigation
maybe Sonnet 5.5 could build this for
you now and you could build this for a
lot cheaper than if you were running
Opus the whole time. So those are a
couple things that I wanted to talk
about. I will link all of this in my
free school community and I will drop
this repo in the description of this
video if you want to check it out. You
could also just Google search for it or
go on X and it will probably be the
first thing you see. So anyways, now
what I think is interesting about this
is a couple things. When I gave two
different coding agents the same prompt
except for one of them used the repo and
one of them didn't, the one that didn't
use the repo always finished first, but
the one that used the repo finished
slower but was much better results
because like I said, they were able to
use these frameworks inside of the REA
repo that understand how to break things
down a little bit better. It's it's this
whole REA investigation flow which is
what makes this so popular. I guess this
thing really is trending quick. It's got
192K stars. If I refresh, we're going to
go up to what 195 196K. And this was
probably 30 minutes ago that I last
refreshed this. Now, something else that
I think is really interesting is coding
agents are just going to get better at
this. Like I think that this whole idea
of reverse engineering now that this
framework has been blowing up on X like
I wouldn't be shocked if the next
version of Opus and Fable and Astra and
Soul and the other models have this
baked in a little bit better. But
anyways, really cool tool. It definitely
helps people that don't come from a
formal programming or software
engineering background build things that
feel a bit more professionally built.
And remember, the concept of reverse
engineering isn't anything new. You've
probably been doing it in your workflow
without even realizing it. we're able to
just basically give our agents a much
more specific PRD without having to go
through that painful process of building
a PRD because we already have a role
model that we're looking at of like this
is what we want now let's build it. So I
hope that that all made sense. I hope
that you can now sort of think about
reverse engineering in a different lens
which is it's not just about reverse
engineering software or apps. It's about
reverse engineering processes and skills
and things that are actually going on in
your day-to-day or in your business. go
out there, find someone who's done
something really well and proven that
they can do it well, and then understand
why that worked and how it it applies to
your context, to your personal
workflows. So, that was the video for
today. I hope you guys enjoyed, you
learned something new. I hope that all
made sense. If it did, please give it a
like. It helps me out a ton. And as
always, I appreciate you guys making it
to the end of the video, and I'll see
you on the next one. Thanks everyone.
