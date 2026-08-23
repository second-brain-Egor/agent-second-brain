---
description: "Today, I'm going to show you guys nine of my favorite GrokBot hacks in just under 10 minutes. Now, using all of these hacks will help you get way..."
related:
  - "[[projects/_index]]"
---
Today, I'm going to show you guys nine
of my favorite GrokBot hacks in just
under 10 minutes. Now, using all of
these hacks will help you get way more
out of your GrokBots, and you don't have
to be technical at all to get any of
this set up and running. So, let's not
waste any time and just get straight
into the video. And real quick, I'm
assuming in this video that you've
already set up GrokBot, or you at least
know what it is. And if you aren't in
that position, then go ahead and watch
this one up here real quick, or I guess
it's on this side over here. That's
going to help you get up to speed,
understand what it is, and then come
back into this video so you can get the
most out of it. But, with that out of
the way, number one, we have using a
grill me skill. So, the whole value of
having a team of AI agents working for
you is that they know you, and they know
your business, and they know your goals.
So, the best way to get what's in your
head into an AI agent system like this
is to use a {slash} grill me skill. So,
this is something that you can get in my
free school community for completely
free. Go down to the description and
grab it in there. And what you can see
is that I have this skill right here,
which I use for Claude, I use for Codex,
but I can actually just drag this right
into here, into my GrokBot, and I can
say, "Hey, go ahead and read this skill.
Go ahead and make a new skill in here
that you can use. It's called the grill
me skill." And then basically, what I
want you to do is just use this on me to
learn more about my business and my
current goals. So, when I shoot that
off, it's basically going to have to do
a ton of things. It's going to read the
skill, it's going to create the skill
for us, and then it's going to start
interviewing us. Because basically, the
whole idea of this skill is that, as you
can see, "Relentlessly interview the
user about every aspect of the topic
until you reach shared understanding."
So, basically, I like to use grill me
when I have new plans for the quarter. I
like to use grill me before I build an
automation, or before I have a new
project, or before I have a new idea, so
my agents know exactly what I'm
thinking. So, this is going to create
that skill. As you can see, it just
saved it, so I can click into this, and
I can see that the skill is here, and I
can make any edits if I need to. And now
the agent will be able to automatically
use this skill whenever you say, "Hey,
grill me about X, Y, and Z." Oh, and by
the way, if you want to see where the
other skills live, you just click on
plugins, and then you go to yours. So,
they're basically considering these
little private plugins the skills. So,
that's where they are. And now, moving
on to tip number two, we have setting up
a chief of staff. So, right here, you
can see on the left, I've got a bunch of
different agents. You can see that I've
also got them grouped, like I've got
some content agents and some general
agents over here. Now, what you'll
notice is that I have Klaus pinned, and
Klaus is my chief, so he's my chief of
staff. And basically, my whole idea is
that I want to only talk to Klaus, and
Klaus has the ability to delegate work
to all of my different specialization
agents. Each one of these agents is
basically good at one job, and Klaus
knows which agent is good at what, and
then I don't have to worry about talking
to all of my different agents. I can
just talk to Klaus, and it does the
rest. As you can see here in my
description, I say, "This is Nate's
chief of staff. Klaus is the only bot
Nate talks to. Before doing any task,
check whether another Grok bot owns it
and delegate first. Only do the work
yourself if no specialist fits. Bring
the results back here." So, what you'll
notice if I start to scroll up in my
conversation with Klaus, we can see when
he's messaged other bots. So, right
here, he's been messaging Motion, and
you can see the conversation between
them. You can see here, he was messaging
Eyes because it needed some research.
You can see right below it, it messaged
Minor because it needed some research on
content and stuff like that. So,
basically, the whole idea is you have
your main agent, and you have a bunch of
different sub agents that your main
agent can delegate to. And basically,
the way you do it is you just make sure
that in each of your different sub
agents, you have a description for them
that's very clear. This bot creates
motion graphics and animations for
intros or transitions for YouTube
videos. So, these are almost like
skills. They're almost just like
specialized sub agents that you build.
For example, if I come down here to
Eyes, you can see this is my researcher.
You can see that Coffee is my morning
planner. You can see that Money deals
with Slack media. You can see that Views
helps me with content strategy. And by
the way, as you can see, Motion actually
made all of these motion graphics that
you saw earlier in the video, and it
saved them locally here for me in this
zip file. So, pretty cool. Which brings
us on to number three, which is
basically the idea that you might be
overwhelmed, you might not be able to
understand, like, oh, what deserves a
sub agent, what doesn't? Well, guess
what? Go through this Grill me, have
your main chief of staff understand what
your goals are, and then ask it to help
it build a team that it thinks will be
the most valuable. So, here you can see,
it says, "You already have research,
social mining, packaging, motion, blah,
blah, blah. So, I wouldn't add a general
helper or a thumbnail bot or a second
chief of staff. I would add tube, I
would add community, and I would add
voice. And as I was able to say, "Hey,
by the way, this month I'm working on
this or I'm really struggling with
this." It would help you build out more
and more sub-agents for you that it can
use to be better. And that brings us on
to number four, because as you start to
scale up your agents, you might have to
worry about memory and stuff, because
Grockbot automatically saves memory,
which is really cool. But there is a
difference between its individual memory
and shared memory across all of your
different agents. Because if you go to
plugins and you connect to things like
Gmail or calendar, all of your agents
can use those plugins. So, that's great.
But watch this. There's basically two
different types of files that are saved.
There's individual-level
agent memory, and then there's also like
shared agent memory across all
Grockbots. So, it's very important that
you're specifying to your Grockbots what
you need to be shared context and what
can just stay between you guys. So,
right here, here is the shared
knowledge. I'm the CEO of Uppercut AI.
I'm in Chicago. I've got this president
and CEO. Here's my channel. Here is blah
blah blah. Here's our funnel. Here is
Compozio. We use this for YouTube, Alexa
and LinkedIn, which is another hack.
Just give me a sec to get to that. And
then we have things that are Klaus-only,
like this, like this, like this. It's
really important to understand what does
the agent that you're talking to
actually know about you. And look at
this, quick little bonus hack for you
guys. You can actually start threads.
So, let's say this agent said something
right here that was really important and
you want to kind of like double tap on
that. Click on the three dots, start a
thread, and now you can have a separate
conversation with Klaus about one
specific thing, and then you can jump
back to the main session if you ever
need to. Okay, anyways, moving on to the
next one, number four. This is Compozio.
So, what I love about Grockbot is how
easy it is to set up. And when you go to
plugins, all you have to do is find the
plugin for what you're looking for. Now,
there are a lot of them, and I do
imagine over time they're going to be
adding more and more. But what if there
are some that you don't have? Like
YouTube, like Reddit, like LinkedIn,
like GoHighLevel. Well, that's where you
can create an account at something
called Compozio that has just like
hundreds and hundreds and hundreds in
here. And you can see that I was able to
connect to things like Perplexity and
YouTube and other things that I couldn't
do inside of Grokbot. And this is called
Compozio, and luckily, inside of
Grokbot, if I go here, Grokbot lets you
connect to Compozio. So, you can
basically just connect to almost
anything through this connection. And
that's why in my shared knowledge up
here, I wanted all my agents to know
that Compozio is how you get to YouTube,
Perplexity, and LinkedIn, as well as
other apps that we're probably going to
add later. So, I wanted to add that in
my shared knowledge. All right, moving
on to number six, we have the idea of
agent logging. You're probably going to
be using this on your phone and on your
desktop, and you're going to be shooting
off a lot of prompts and a lot of tasks.
So, what I did is I created a skill in
here. If I go to my plugins and I go to
mine right here called log Grokbot work
to ClickUp. Hey, go ahead and create a
quick project where I need you to
research the top five best voice AI
agent providers.
Now, what this does is basically, Klaus
is going to kick off a message probably
to a different agent, right? Probably
Eyes, because that's our researcher.
But, what's going to happen is it needs
to update the actual ClickUp. Because
what I have is this ClickUp space where
I can now see everything that my agents
have done and everything that they're
working on, and they also leave notes
for me. So, right here I can see notes,
it gives me a link, it tells me when it
started, it tells me the status, it
tells me the owner, and all of these
different items, I can see basically
like what is important and anything that
I need to know about them, progress
updates, and I can watch them over time.
And you can see right here, Klaus said,
"Okay, awesome. I logged this right here
in your ClickUp, so I should be able to
go in here, and if I see a new in
progress right here, research top five
voice providers, the owner is Eyes via
Klaus, and here is basically what we're
looking on. It's waiting on Eyes, blah
blah blah." All right, so moving on to
number seven, we have the ability to
teach our agents a task. So, when you're
building automations and stuff,
typically what you do is you use the
grill me skill or you explain the
process super clearly. But, if you're
doing something that might require like
some computer use or maybe it's a little
bit too difficult to explain because
it's kind of visual, you can open up the
computer of the actual agent that you're
working on. Now, they all have a shared
computer, but sometimes their desktops
look different, but ultimately, under
the hood, they all have the same shared
computer. But what you can do here is
teach a task. So, let's say I wanted to
teach Klaus how to, I don't know, go to
Google Images and search for like
Chicago Cubs, you know, food. And I
needed it to every single week give me a
rundown of the food that's
being sold at Wrigley Field. Or maybe, I
guess in this case, I would teach it how
to do something like a Capsica.
Basically, what's happening right now is
it's recording my screen. And then
whenever I stop the recording, it's
going to analyze what it did. It's going
to turn that into a skill, and then we
can reuse that in the future if we need
to. But anyways, I could go to Images,
and then I could basically just like
save a few of these to the desktop or
whatever. And then when I hit stop, it
basically understands what I did. So,
here you can see it says learn from
demonstration. It's going to analyze
that and turn that into a skill. All
right. And over on this right-hand
panel, we're going to move on to number
eight, which is to actually create
routines. Now, all of this stuff is
great, and you can do it on the go
because you can use the Grok Bot app on
your phone, which is great. But if you
want things to happen when you sleep, or
if you want them to happen on certain
triggers, you can create routines right
here. Routines are recurring tasks this
bot runs on a schedule. So, I can hit
create routine, and I can name it. I can
give it an instruction. You can also say
in this instruction, "Hey, you know, run
this skill, or talk to these agents and
do this." So, you can be very specific
here. And then, you can basically
trigger it on a schedule. So, every
hour, every day, a certain interval, or
on specific events. Right now, we only
have these six, but I'm sure they're
going to add more of these later. But on
Slack messages, on Git events, on Teams
messages. And that means that these
things can run even when your Grok Bot
app is turned off, or your phone's
turned off, or your computer's turned
off because this all runs in Grok's
cloud. And finally, we have the agent
computer, which is something that I
already showed you guys up here.
Obviously, we just took a look at this
Capsica, and we took a look at this
thing. But basically, what's really cool
is that you can save profiles. So, I
taught my
um
Klaus here how to do things in my school
account. And what happens is if I log in
right here to school,
you can see that I'm already signed in
in my account, which means if I wanted
to teach it a task, which I already did
by the way, it can go ahead and do it.
As you can see, if I go to my plugins
and I go to my like 7-day challenge
posts on school, it basically uses the
computer in my already signed in school
account, and it watched me go through
find posts and like them, and now I can
set that up on a routine to do that
every day or every week. But the point
being, you can have these credentials
saved in there, and you don't have to
like paste them in the chat, and you
don't have to be unsecure about it. You
can just go ahead and log in, and then
Grok Bot will be able to use that
profile. But anyways, I know this one
was quick, but I just wanted to show you
guys a few of the ways that I've been
using Grok Bot. If you haven't yet, or
if you're just getting started, that
might be able to help you get more out
of it. So, if you guys enjoyed the video
or you learned something new, please
give it a like, it helps me out a ton.
And as always, I appreciate you guys
making it to the end of the video, and
I'll see you on the next one.
Thanks, everyone.
