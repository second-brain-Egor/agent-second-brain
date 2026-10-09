---
type: project
last_accessed: 2026-10-06
relevance: 0.97
tier: active
---
So, this isn't the Claude that you know.
I just turned one of the biggest minds
in AI into a Claude agent. Andrej
Karpathy is one of Anthropic's lead
engineers, a co-founder of OpenAI, and
the person that everyone says explains
AI better than anyone alive. And today,
I'm going to show you the exact four
steps to turn his thoughts into your own
Claude agent. So, let's get into it.
Okay, so real quick, who is this guy? He
was a founding member of OpenAI back in
2015. Then he ran AI at Tesla for about
five years, leading the computer vision
team behind autopilot. Then he left to
do education full-time and started
Eureka Labs. And as of May of this year,
he's at Anthropic on the pre-training
team, which is the team that trains
Claude models before they're released to
the public. And on the side, he has put
out so many different YouTube videos and
courses on building with AI. So, what
we're building today is not a voice
clone of Andrej Karpathy. It's not an
impression of him. It's an agent that
condenses the way the best AI teacher,
Andrej Karpathy, explains things, and it
teaches you the same way. So, it follows
seven rules that all come from his own
writing and his blogs and his lectures,
stuff like build the smallest version
first, predict what's going to happen
before you run it, show the broken
version, and never hand over code that
you haven't run yourself. So, this is
more than just a clone of a person. It's
more about cloning the way that his
brain thinks. So, now I bet you guys are
wondering, why would you actually build
this? Let's think about what happens
when you ask Claude to explain something
that you don't understand. It might
overexplain. It might make stuff up
along the way. And you actually just end
up feeling like you learned nothing and
feeling more overwhelmed. And if you're
building something for a client, that's
how you end up shipping code that you
can't fix or explain when it breaks. And
Andrej Karpathy has run into this exact
same thing. Back in August of last year,
he actually posted publicly that he
tried to get Claude code to teach him
alongside the code that it was writing,
and in his words, it didn't work at all
because it really just wants to write
code a lot more than it wants to explain
anything along the way. So, building
this agent here is going to fix AI's
worst habit, which is sounding right
instead of being right. And the bigger
reason is honestly this, the quality of
what you build with AI comes down to the
expertise that's in the system, and
you're not going to be an expert on
everything. You know, I'm not a machine
learning researcher. I'm not a machine
learning expert, but I can certainly go
have agents pull in everything that a
real expert has said, compile it into
something that Claude can actually use,
and then I can just talk to it until I
understand it. And then, once I
understand a little bit better, I have
all that knowledge already in my
project, and I can wire that knowledge
into my own skills and my own agents and
my own workflows, which is exactly what
we're doing today with Karpathy. And
what's really cool is, once you've done
this with Karpathy, you can do this with
pretty much anyone. You can do this with
your favorite, you know, sales teacher,
or an author you really like, or a coach
that you're already paying for. And it's
basically just the same four steps, in
the same way that [music] we build this
sort of like second brain. Now, real
quick, before we get into the build,
I've got this completely free AI OS kit
for you guys to help you build and scale
your operating systems. If you combine
this sort of setup with things like
Karpathy's brain, it's just going to be
a huge unlock, and that's how I'm able
to move so fast. So, link for that will
be down in the description, but let's
get into the build. Okay, so I'm going
to do this inside of Claude Code, and
there are going to be six prompts to run
here, and I'll show all of them on
screen, so you can just kind of take a
screenshot and paste them into your own
Claude Code. So, first, Claude needs
everything that's inside of Andre
Karpathy's head. Things like his blogs,
his lecture transcripts, his GitHub
repos, his posts on X, all of that is
going to be just basically free and
public. But, Claude Code might not be
able to just grab all of that for free,
because it might be behind some sort of
like paywall or software wall. So, what
I did for YouTube is I had it pull
captions with two free Python packages,
YouTube Transcript API and yt-dlp. And
then, for X, I'm using a API called
twitterapi.io, which is a paid API, but
I've pulled basically every post that
he's made since 2023, and it was about a
dollar. It's not a very expensive API at
all. So, here is the prompt for the
crawl. It basically says where to get
everything, which tool to use for each
source, and I told it to run one agent
per source, so they all go at once and
parallel, so it doesn't take forever. I
told it to write down what it got, so
that you can actually check it. And this
took me about 45 minutes to an hour for
all of these agents to run and grab
everything. And what we end up with is
one raw folder with one subfolder per
source, and over 700,000 words, straight
from Andre Karpathy himself. Now, you
could just stop here and point Claude at
that folder, but all of these, you know,
messy words, it doesn't really fit into
Claude's head in the right way where it
actually can filter through it in a good
fashion, right? Like it's going to be
too messy. It's like finding a needle in
a haystack. So, what we're going to do
is what Karpathy told everyone to do
back in April. He posted about how he
has an LLM compile his raw sources into
a wiki. The raw files don't get touched,
but the LLM basically reads through all
of them and then links them together
with pages, keeps an index, keeps a log,
and now you're able to actually query
against it in a way that makes more
sense because there's like
relationships. And you put that whole
idea in a gist, and that's what I'm
going to paste into the coding agent.
The link to the gist is in the
description of this video. So, what
we're doing is kind of funny. We're
storing Karpathy's brain inside of
Karpathy's own LLM wiki memory system.
And if you guys have been following me
for a while, you know that I've made
quite a few videos on this topic, and
I've got a bunch of different LLM wikis
set up in my own AI OS. All right, so
here's prompt two to set up the wiki.
You're going to paste in the gist, and
then you're going to tell Claude to use
it on the raw folder, which is just
everything that Claude previously just
extracted for you. And what comes out is
a wiki inside of Obsidian. Now, Obsidian
is just kind of the visual layer on top
of it, which is what I'm showing you
guys here. And you don't need Obsidian
to get this to work, but if you want to
look at it visually, Obsidian works. You
can see down here we have the sources,
we have one page per thing he wrote or
said, we have topics on what he knows,
we have principles, we have the rules,
we have methods, we have how he
explains, we have how he debugs, we have
basically, just like I said, the way his
brain works. And whenever you see one of
these purple links, that is the wiki
connecting one page to another or one
method to another. Every rule links back
to the source that it came from or
sources that it came from. Every source
links to the rules that it supports. So,
instead of just having a dump of notes
like we had earlier, we now have like
this interconnected web or sort of like
relationship map. And every time that
something new goes in, you ingest a new
blog or a new idea, the LLM will once
again ingest it and link it to a bunch
of other concepts. Now, this next step
is what makes it think like him instead
of just knowing what he said in the
past. So, here's the prompt for setting
up the rules. It basically pulls his
rules out of the the and every rule has
to connect with an exact quote from him
and where it came from. Because we don't
want Claude to just make things up. So,
what we got here were seven rules.
Number one is build it or you don't
understand it. Number two is first order
term first. Basically, find the one
piece that matters, show it working, and
then add just one thing at a time. And
pretty much his whole course is built in
that way. Number three is to predict,
then run, then compare. He'll say the
number he expects before he runs the
cell because, in his words, most of the
time it will train, but silently work a
bit worse. Number four is to show the
wrong version first. He leaves his own
bugs in the recording on purpose. Number
five is prove it, don't claim it. Number
six is say what you assumed. His number
one complaint about Claude code is that
the models make wrong assumptions on
your behalf and then just run along them
without checking. And number seven is
that simpler wins. And what's cool is
you can check any of these. You can
click the quote and it will open up the
page that it came from with the
timestamp or with the exact source. And
if there is no source, the agent has to
say explicitly that it's inferring based
on things that Karpathy has said. Now,
these rules need to live somewhere where
the agent can actually read them. So,
here is prompt four. And it has Claude
turn them into two files for us. That
first file is a sub-agent. And in case
you don't know what that is, it's a
separate Claude with its own
instructions and its own memory and
context window, so that if you want to
hand off a task to a sub-agent, it
doesn't drag your whole conversation
along with it. And you can see here
inside of this sub-agent file, we can
see the seven rules. We can also see how
it talks. And we can see the loop that
it runs on every single task. So, this
is basically like a little mini Karpathy
agent. Now, the second one is a skill.
So, you can see here that when I type
{slash} Karpathy-teach and then whatever
I'm stuck on, it goes into the agent
with the rules, and then it grades the
answer against a checklist, one line per
rule, and then it will actually show me
everything. So, those are the two things
we have, a Karpathy agent and a Karpathy
skill. Okay. Now, here's another thing
that's really important when we're
setting this up. We want the agent to
make sure that it's running its code
before it answers you. And that's why
building this inside of Claude code
works so well because it can already
write and run code. And it's a step that
we have to make sure that the agent
can't skip based on Karpathy's own
rules. So, here's prompt five. It's
basically adding a run gate. It adds a
hook, which is a little script that runs
right when the agent tries to finish its
turn. So, if it wrote code and it never
ran it, the hook will basically block
the answer and it will send it back with
one message saying, "Hey, you have to
run this before you say it works." So,
we're kind of just baking in like a
verification loop. And you know,
obviously you don't have to code or
write this hook yourself. You just ask
for it with this prompt. So, now it will
run, it will test, and it will fix, and
then only after all that will you
actually see the final thing. And then
the last step, of course, is just to
test it. So, a few different prompts
that we used it. I asked it here to
build something real and teach me how it
works, which was a byte pair tokenizer,
which is the thing that turns text into
numbers before a large language model
ever sees it. And watch what it does
here. The first thing, it writes down
what done means before it touches any
code. And then it builds the smallest
version that works on a tiny input and
before it runs it, it tells me what it
expects to see. Then it runs it and
shows me the real output. And then, it
shows me a version that breaks and why,
and then it fixes it. And then at the
bottom it lists basically everything it
ran, what came out, what it changed, and
which rule it was following for each of
those moves. So, instead of getting just
a block of code back and then the agent
saying, "Hey, this works." I basically
got walked through it one piece at a
time and now I can understand a lot
better what just happened. Now, another
thing you can test is its review. So,
before something goes to a client, I can
ask it one question, which is, "Would
the client accept this and what would he
want to delete?" Or, you know, questions
like that. And here's a script that
Claude wrote for me that I can use as an
example. This script pulls YouTube
comments and it ran fine when Claude
tested it. The agent reads it, predicts
it'll crash on an emoji under a normal
Windows terminal, it runs it that way,
and then it crashes before writing any
files. So, saying that it works was only
true in one specific setting or
terminal. So, here you can see that
Claude was able to go through and cut a
bunch of stuff that wasn't earning its
place. It was able to give me an
analysis on how we actually fix this and
clean it up and review it before we can
actually like ship it. And then it
proves the trimmed version catches the
same questions by running both of them
side by side and actually showing me.
And then the other thing I wanted to
bring up is that this thing will just
keep learning. Back in July, Karpathy
posted about how he rambles at the model
by voice for 10 minutes and then he lets
the model clean up all that text. So, I
can run {slash} Karpathy {dash} ingest
with any sort of link. It will then
check the raw folder, it'll write a
source page for the [music] post, and
then it will update every page that post
touches. It added a new behavior here to
rule six. So, now the agent knows to ask
me a couple of questions when my request
is thin instead of just guessing. And a
rule that was sitting on the bench with
one source behind it got its second
source and became a real rule. And then,
because it understands how this wiki
works, it'll update the index, it'll
update the hot page, it'll update the
log. So, the brain just got better from
me adding one link. And I never had to
touch the wiki by hand or manually set
up these relationships or links. And
that, of course, was his rule two. Okay,
so zooming out, we had four steps. We
gave Claude everything inside of
someone's head, Karpathy's head, and we
compiled it into a wiki. We turned that
into his rules with a quote for each
one. We make it run before it talks, and
we make it test on things that are real.
And the line that I'd want to leave you
guys with today is one of my favorite
quotes, and it's something that he
himself has said this year, which is
that you can outsource your thinking,
but you cannot outsource your
understanding. You are not going to be
the expert at everything, and that's
fine. But, you can certainly pull in the
expert and build on top of him or her.
Anyways, that is going to do it for this
one. So, if you guys enjoyed the video
or you learned something new, please
give it a like. It definitely helps me
out a ton. And as always, I appreciate
you guys making it to the end of the
video, and I'll see you on the next one.
Thanks, everyone.
